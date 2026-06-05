import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from PySide6.QtCore import QTimer, QObject, Signal
from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.settings_repository import SettingsRepository
from mfdp_app.core.atomic_analyzer import AtomicAnalyzer, InterruptionSeverity


"""
FocusSession vs PmdrCountdownTimer Farkı:

FocusSession:
- Sadece DATA tutar (data class)
- Bir oturumun (session) tüm bilgilerini içerir
- İş mantığı YOK, sadece state tutar
- tick(), pause(), resume() gibi metodlar sadece sayıcıları günceller
- DB'ye yazmaz, sadece veri hazırlar (to_db_dict())

PmdrCountdownTimer:
- İŞ MANTIĞI yönetir (timer logic)
- Qt QTimer'ı yönetir, UI ile iletişim kurar
- FocusSession'ı kullanır ama timer işlevselliğini sağlar
- start_stop(), reset(), set_mode() gibi metodlar timer'ı kontrol eder
- DB'ye yazar, signal'lar gönderir
- FocusSession'ı oluşturur, yönetir ve kaydeder

Özet: FocusSession = Veri, PmdrCountdownTimer = Mantık
"""


@dataclass
class FocusSession:
    """Focus oturumunu temsil eden class - Runtime state tutar (sadece veri)"""
    
    # Temel bilgiler
    start_time: datetime.datetime
    mode: str  # "Focus", "Short Break", "Long Break"
    planned_minutes: int
    
    # Süre takibi (sadece sayıcılar)
    active_seconds: int = 0      # Aktif çalışma süresi (duraklatmalar hariç)
    total_seconds: int = 0       # Toplam geçen süre (duraklatmalar dahil)
    pause_seconds: int = 0        # Toplam duraklatma süresi
    
    # Duraklatma detayları
    pause_count: int = 0
    pause_durations: List[float] = field(default_factory=list)
    is_paused: bool = False
    pause_start_time: Optional[datetime.datetime] = None
    
    # Kesinti takibi
    interruption_count: int = 0
    interruption_times: List[datetime.datetime] = field(default_factory=list)
    interruption_seconds: List[int] = field(default_factory=list)
    interruption_types: List[str] = field(default_factory=list)
    
    # Durum
    is_completed: bool = False
    current_task_id: Optional[int] = None
    current_task_name: Optional[str] = None
    category: Optional[str] = None
    
    def tick(self, is_running: bool):
        """Her saniye çağrılır - sadece sayıcıları artırır"""
        self.total_seconds += 1
        if is_running and not self.is_paused:
            self.active_seconds += 1
        elif self.is_paused:
            self.pause_seconds += 1
    
    def pause(self):
        """Duraklatma başlat"""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = datetime.datetime.now()
    
    def resume(self):
        """Duraklatma bitir"""
        if self.is_paused and self.pause_start_time:
            pause_duration = (datetime.datetime.now() - self.pause_start_time).total_seconds()
            self.pause_durations.append(pause_duration)
            self.pause_count += 1
            self.is_paused = False
            self.pause_start_time = None
    
    def mark_interruption(self, interruption_type: str = "pause"):
        """Kesinti işaretle (reset, mod değişimi vb.)"""
        self.interruption_count += 1
        self.interruption_times.append(datetime.datetime.now())
        self.interruption_seconds.append(self.active_seconds)
        self.interruption_types.append(interruption_type)
        print(f" Interruption marked: {interruption_type} @ {self.active_seconds // 60}dk {self.active_seconds % 60}s")
    
    def to_db_dict(self, end_time: datetime.datetime, task_name: Optional[str], category: Optional[str]):
        """DB'ye kaydetmek için dict'e çevir"""
        return {
            'start_time': self.start_time,
            'end_time': end_time,
            'duration_seconds': self.active_seconds,
            'planned_duration_minutes': self.planned_minutes,
            'mode': self.mode,
            'completed': self.is_completed,
            'task_name': task_name,
            'category': category,
            'interruption_count': self.interruption_count
        }
    
    def get_interruptions_for_db(self):
        """Interruption'ları DB formatına çevir"""
        return [
            {
                'seconds_into_session': sec,
                'interruption_time': time,
                'interruption_type': itype
            }
            for sec, time, itype in zip(
                self.interruption_seconds,
                self.interruption_times,
                self.interruption_types
            )
        ]


class PmdrCountdownTimer(QObject):
    """
    Yeni timer implementasyonu - Session class ile lazy DB write yaklaşımı
    Mevcut PomodoroTimer API'si ile uyumlu
    """
    
    timeout_signal = Signal(str)
    finished_signal = Signal(str)
    state_changed_signal = Signal(str)
    task_changed_signal = Signal(int)  # task_id, -1 if None
    
    def __init__(self, task_manager=None, atomic_analyzer: Optional[AtomicAnalyzer] = None):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)

        # State
        self.current_state = "Focus"
        self.is_running = False

        # Ayarlar
        self.durations = {"Focus": 25, "Short Break": 5, "Long Break": 15}
        self.reload_settings()

        # Session yönetimi
        self.current_session: Optional[FocusSession] = None

        # Timer countdown
        self.current_time = 0

        # Task desteği
        self.task_manager = task_manager
        self.current_task_id = None

        self.atomic_analyzer = atomic_analyzer
        self._milestones_fired: set = set()

        self._set_time_based_on_state()

    def start_stop(self):
        """Başlat/Duraklat"""
        if self.is_running:
            # DURAKLAT
            self.timer.stop()
            self.is_running = False
            if self.current_session:
                self.current_session.mark_interruption()
                self.current_session.pause()
            if self.atomic_analyzer:
                self.atomic_analyzer.record_interruption(
                    reason="user_pause",
                    severity=InterruptionSeverity.LOW
                )
        else:
            # DEVAM ET veya BAŞLAT
            if self.current_session:
                # Devam et
                self.current_session.resume()
                if self.atomic_analyzer:
                    self.atomic_analyzer.resume_session()
            else:
                # Yeni session başlat
                self._start_new_session()

            self.timer.start(1000)
            self.is_running = True

        return self.is_running
    
    def reset(self):
        """
        Sıfırla - Mevcut session'ı kaydet (eğer çalışma süresi varsa)
        Reset = Kesinti olarak kaydet ama o zamana kadarki süreyi de kaydet
        """
        if self.current_session and self.current_session.active_seconds > 0:
            if not self.current_session.is_paused:
                self.current_session.mark_interruption("reset")
            if self.atomic_analyzer:
                self.atomic_analyzer.abandon_session(reason="reset")
            self._save_current_session(completed=0)

        self.timer.stop()
        self.is_running = False
        self.current_session = None
        self._milestones_fired.clear()
        self._set_time_based_on_state()
        self._emit_time()

    def set_mode(self, mode):
        """Mod değiştir - Mevcut session'ı kaydet"""
        if self.is_running and self.current_session:
            self.current_session.mark_interruption("mode_change")
            if self.atomic_analyzer:
                self.atomic_analyzer.abandon_session(reason="mode_change")
            self._save_current_session(completed=0)

        self.timer.stop()
        self.is_running = False
        self.current_state = mode
        self.current_session = None
        self._milestones_fired.clear()
        self._set_time_based_on_state()
        self.state_changed_signal.emit(mode)
        self._emit_time()
    
    def reload_settings(self):
        """Ayarları yeniden yükle"""
        settings = SettingsRepository.load_settings()
        if 'focus_duration' in settings:
            self.durations["Focus"] = int(settings['focus_duration'])
        if 'short_break_duration' in settings:
            self.durations["Short Break"] = int(settings['short_break_duration'])
        if 'long_break_duration' in settings:
            self.durations["Long Break"] = int(settings['long_break_duration'])
        
        # Eğer timer çalışmıyorsa, mevcut modun süresini güncelle
        if not self.is_running:
            self._set_time_based_on_state()
            self._emit_time()
    
    def set_task(self, task_id):
        """Timer'a task ata"""
        # Eğer aynı task_id zaten ayarlıysa, signal emit etme (sonsuz döngüyü önle)
        if self.current_task_id == task_id:
            return
        
        self.current_task_id = task_id
        if self.current_session:
            self.current_session.current_task_id = task_id
            # Task bilgilerini güncelle
            if self.task_manager:
                task_name, category = self.task_manager.get_task_name_and_tag()
                self.current_session.current_task_name = task_name
                self.current_session.category = category
        self.task_changed_signal.emit(task_id if task_id else -1)
    
    def _start_new_session(self):
        """Yeni session başlat"""
        self.current_session = FocusSession(
            start_time=datetime.datetime.now(),
            mode=self.current_state,
            planned_minutes=self.durations.get(self.current_state, 25),
            current_task_id=self.current_task_id
        )

        if self.task_manager and self.current_task_id:
            task_name, category = self.task_manager.get_task_name_and_tag()
            self.current_session.current_task_name = task_name
            self.current_session.category = category

        self._milestones_fired.clear()

        if self.atomic_analyzer:
            planned_secs = self.durations.get(self.current_state, 25) * 60
            self.atomic_analyzer.start_session(
                planned_duration=planned_secs,
                session_type=self.current_state
            )

    def _set_time_based_on_state(self):
        """Mevcut moda göre timer süresini ayarla"""
        minutes = self.durations.get(self.current_state, 25)
        self.current_time = minutes * 60
    
    def _update_timer(self):
        """Her saniye çağrılır"""
        self.current_time -= 1

        if self.current_session:
            self.current_session.tick(self.is_running)

        # Milestone kontrolü (sadece Focus modunda)
        if self.atomic_analyzer and self.current_session and self.current_state == "Focus":
            planned_secs = self.durations.get("Focus", 25) * 60
            if planned_secs > 0:
                elapsed = self.current_session.active_seconds
                pct = elapsed / planned_secs
                for threshold, label in ((0.25, "quarter"), (0.5, "halfway"), (0.75, "three_quarters")):
                    if pct >= threshold and threshold not in self._milestones_fired:
                        self._milestones_fired.add(threshold)
                        self.atomic_analyzer.record_milestone(
                            milestone_type=label,
                            percentage=int(threshold * 100)
                        )

        self._emit_time()

        if self.current_time <= 0:
            self.timer.stop()
            self.is_running = False

            if self.current_session:
                self.current_session.is_completed = True
                if self.atomic_analyzer:
                    self.atomic_analyzer.complete_session(
                        actual_duration=self.current_session.active_seconds,
                        completed_by="timer"
                    )
                self._save_current_session(completed=1)

            self.finished_signal.emit(self.current_state)
    
    def _save_current_session(self, completed):
        """Mevcut session'ı DB'ye kaydet"""
        if not self.current_session:
            print("UYARI: Session yok, kayıt yapılmıyor")
            return

        end_time = datetime.datetime.now()
        task_name = self.current_session.current_task_name
        category = self.current_session.category
        session_dict = self.current_session.to_db_dict(end_time, task_name, category)

        session_id = SessionRepository.log_session(
            start_time=session_dict['start_time'],
            end_time=session_dict['end_time'],
            duration_seconds=session_dict['duration_seconds'],
            planned_duration_minutes=session_dict['planned_duration_minutes'],
            mode=session_dict['mode'],
            completed=completed,
            task_name=session_dict['task_name'],
            category=session_dict['category'],
            interruption_count=session_dict['interruption_count']
        )

        if self.atomic_analyzer:
            self.atomic_analyzer.flush_events(session_id=session_id)

        self.current_session = None

    def _emit_time(self):
        """Zamanı UI'ya gönder"""
        if self.current_time < 0:
            self.current_time = 0
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.timeout_signal.emit(time_str)

    def save_on_exit(self):
        """Uygulama kapanırken aktif session'ı kaydet"""
        if self.current_session and self.current_session.active_seconds > 0:
            self.current_session.mark_interruption("app_exit")
            if self.atomic_analyzer:
                self.atomic_analyzer.abandon_session(reason="app_exit")
            self._save_current_session(completed=0)


class CountUpTimer(QObject):
    """
    Count-up timer (stopwatch) - Süreyi yukarı doğru sayar
    Mola modları yok, sadece başlat/duraklat, sıfırla ve tamamla
    """
    
    timeout_signal = Signal(str)  # "MM:SS" formatında
    finished_signal = Signal(str)  # "Free Timer" - tamamlandığında
    state_changed_signal = Signal(str)  # Durum değişikliği için (opsiyonel)
    task_changed_signal = Signal(int)  # task_id, -1 if None
    
    def __init__(self, task_manager=None, atomic_analyzer: Optional[AtomicAnalyzer] = None):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)

        self.is_running = False
        self.current_session: Optional[FocusSession] = None
        self.current_time = 0
        self.task_manager = task_manager
        self.current_task_id = None
        self.atomic_analyzer = atomic_analyzer

    def start_stop(self):
        """Başlat/Duraklat"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            if self.current_session:
                self.current_session.mark_interruption()
                self.current_session.pause()
            if self.atomic_analyzer:
                self.atomic_analyzer.record_interruption(
                    reason="user_pause",
                    severity=InterruptionSeverity.LOW
                )
        else:
            if self.current_session:
                self.current_session.resume()
                if self.atomic_analyzer:
                    self.atomic_analyzer.resume_session()
            else:
                self._start_new_session()

            self.timer.start(1000)
            self.is_running = True

        return self.is_running
    
    def reset(self):
        """Sıfırla - Mevcut session'ı kaydet (eğer çalışma süresi varsa)"""
        if self.current_session and self.current_session.active_seconds > 0:
            if not self.current_session.is_paused:
                self.current_session.mark_interruption("reset")
            if self.atomic_analyzer:
                self.atomic_analyzer.abandon_session(reason="reset")
            self._save_current_session(completed=0)

        self.timer.stop()
        self.is_running = False
        self.current_session = None
        self.current_time = 0
        self._emit_time()

    def complete(self):
        """Tamamla - Timer'ı durdur ve session'ı tamamlanmış olarak kaydet"""
        self.timer.stop()
        self.is_running = False

        if self.current_session:
            self.current_session.is_completed = True
            if self.atomic_analyzer:
                self.atomic_analyzer.complete_session(
                    actual_duration=self.current_time,
                    completed_by="user"
                )
            self._save_current_session(completed=1)

        self.current_time = 0
        self._emit_time()
        self.finished_signal.emit("Free Timer")
    
    def set_task(self, task_id):
        """Timer'a task ata"""
        # Eğer aynı task_id zaten ayarlıysa, signal emit etme (sonsuz döngüyü önle)
        if self.current_task_id == task_id:
            return
        
        self.current_task_id = task_id
        if self.current_session:
            self.current_session.current_task_id = task_id
            # Task bilgilerini güncelle
            if self.task_manager:
                task_name, category = self.task_manager.get_task_name_and_tag()
                self.current_session.current_task_name = task_name
                self.current_session.category = category
        self.task_changed_signal.emit(task_id if task_id else -1)
    
    def _start_new_session(self):
        """Yeni session başlat"""
        self.current_session = FocusSession(
            start_time=datetime.datetime.now(),
            mode="Free Timer",
            planned_minutes=0,
            current_task_id=self.current_task_id
        )

        if self.task_manager and self.current_task_id:
            task_name, category = self.task_manager.get_task_name_and_tag()
            self.current_session.current_task_name = task_name
            self.current_session.category = category

        if self.atomic_analyzer:
            self.atomic_analyzer.start_session(
                planned_duration=0,
                session_type="Free Timer"
            )

    def _update_timer(self):
        """Her saniye çağrılır"""
        self.current_time += 1

        if self.current_session:
            self.current_session.tick(self.is_running)

        self._emit_time()
    
    def _save_current_session(self, completed):
        """Mevcut session'ı DB'ye kaydet"""
        if not self.current_session:
            print("UYARI: Session yok, kayıt yapılmıyor")
            return

        end_time = datetime.datetime.now()
        task_name = self.current_session.current_task_name
        category = self.current_session.category
        session_dict = self.current_session.to_db_dict(end_time, task_name, category)

        session_id = SessionRepository.log_session(
            start_time=session_dict['start_time'],
            end_time=session_dict['end_time'],
            duration_seconds=session_dict['duration_seconds'],
            planned_duration_minutes=None,
            mode="Free Timer",
            completed=completed,
            task_name=session_dict['task_name'],
            category=session_dict['category'],
            interruption_count=session_dict['interruption_count']
        )

        if self.atomic_analyzer:
            self.atomic_analyzer.flush_events(session_id=session_id)

        self.current_session = None

    def _emit_time(self):
        """Zamanı UI'ya gönder"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.timeout_signal.emit(time_str)

    def save_on_exit(self):
        """Uygulama kapanırken aktif session'ı kaydet"""
        if self.current_session and self.current_session.active_seconds > 0:
            self.current_session.mark_interruption("app_exit")
            if self.atomic_analyzer:
                self.atomic_analyzer.abandon_session(reason="app_exit")
            self._save_current_session(completed=0)


# Eski PomodoroTimer - Geriye uyumluluk için korunuyor
class PomodoroTimer(QObject):
    timeout_signal = Signal(str)
    finished_signal = Signal(str)
    state_changed_signal = Signal(str)
    task_changed_signal = Signal(int)  # task_id, -1 if None

    def __init__(self, task_manager=None):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        
        # ÖNEMLİ: reload_settings() içinde is_running kullanıldığı için önce tanımlanmalı
        self.current_state = "Focus"
        self.is_running = False
        
        # Ayarlar (Default)
        self.durations = {"Focus": 25, "Short Break": 5, "Long Break": 15}
        self.reload_settings()
        
        # V2 Verileri
        self.session_start_time = None 
        self.planned_minutes = 0 
        self.paused_duration = 0  # Duraklatma süresi (saniye)
        self.pause_start_time = None  # Duraklatma başlangıç zamanı
        self.interruption_count = 0  # Kesinti sayısı
        
        # Task desteği
        self.task_manager = task_manager
        self.current_task_id = None
        
        self._set_time_based_on_state()

    def start_stop(self):
        if self.is_running:
            # DURAKLAT
            self.timer.stop()
            self.is_running = False
            self.pause_start_time = datetime.datetime.now()
            self.interruption_count += 1  # Kesinti say
        else:
            # DEVAM ET veya BAŞLAT
            if self.pause_start_time:
                # Duraklatma süresini hesapla ve ekle
                if self.session_start_time:  # Mantıksal kontrol
                    pause_duration = (datetime.datetime.now() - self.pause_start_time).total_seconds()
                    self.paused_duration += pause_duration
                self.pause_start_time = None
            
            if self.session_start_time is None:
                # İlk başlatma
                self.session_start_time = datetime.datetime.now()
                self.planned_minutes = self.durations.get(self.current_state, 25)
                self.paused_duration = 0  # Yeni oturum, duraklatma yok
            
            self.timer.start(1000)
            self.is_running = True
        return self.is_running

    def reset(self):
        self.timer.stop()
        self.is_running = False
        self.session_start_time = None
        self.paused_duration = 0
        self.pause_start_time = None
        self.interruption_count += 1  # Kesinti say
        self._set_time_based_on_state()
        self._emit_time()

    def set_mode(self, mode):
        # Eğer timer çalışıyorsa ve bir oturum varsa, önce mevcut oturumu kaydet
        if self.is_running and self.session_start_time:
            self._save_current_session(completed=0)  # Kesinti olarak işaretle
        
        self.timer.stop()
        self.is_running = False
        self.current_state = mode
        self.session_start_time = None
        self.paused_duration = 0  # Yeni mod, duraklatma sıfırla
        self.pause_start_time = None
        self.interruption_count += 1  # Kesinti say
        self.planned_minutes = self.durations.get(mode, 25)  # YENİ MODUN SÜRESİNİ AYARLA
        self._set_time_based_on_state()
        self.state_changed_signal.emit(mode)
        self._emit_time()
        
    def reload_settings(self):
        settings = SettingsRepository.load_settings()
        if 'focus_duration' in settings:
            self.durations["Focus"] = int(settings['focus_duration'])
        if 'short_break_duration' in settings:
            self.durations["Short Break"] = int(settings['short_break_duration'])
        if 'long_break_duration' in settings:
            self.durations["Long Break"] = int(settings['long_break_duration'])
        
        # Eğer timer çalışmıyorsa, mevcut modun süresini güncelle
        if not self.is_running:
            self._set_time_based_on_state()
            self._emit_time()

    def _set_time_based_on_state(self):
        minutes = self.durations.get(self.current_state, 25)
        self.current_time = minutes * 60

    def _update_timer(self):
        self.current_time -= 1
        self._emit_time()

        if self.current_time <= 0:
            self.timer.stop()
            self.is_running = False
            self._save_current_session(completed=1)
            self.finished_signal.emit(self.current_state)
    
    def set_task(self, task_id):
        """Timer'a task ata."""
        # Eğer aynı task_id zaten ayarlıysa, signal emit etme (sonsuz döngüyü önle)
        if self.current_task_id == task_id:
            return
        
        self.current_task_id = task_id
        self.task_changed_signal.emit(task_id if task_id else -1)
    
    def _save_current_session(self, completed):
        """Mevcut oturumu veritabanına kaydet (yardımcı metod)"""
        if not self.session_start_time:
            # Hata durumu - kayıt yapma
            print("UYARI: session_start_time yok, kayıt yapılmıyor")
            return
        
        end_time = datetime.datetime.now()
        total_duration = (end_time - self.session_start_time).total_seconds()
        actual_duration = total_duration - self.paused_duration  # Duraklatma süresini çıkar
        
        # Negatif süre kontrolü (hata durumunda 0 yap)
        if actual_duration < 0:
            print(f"UYARI: Negatif süre tespit edildi ({actual_duration:.2f} sn), 0 olarak kaydediliyor")
            actual_duration = 0
        
        # Task bilgilerini al
        task_name = None
        category = None
        if self.task_manager and self.current_task_id:
            task_name, category = self.task_manager.get_task_name_and_tag()
        
        SessionRepository.log_session(
            start_time=self.session_start_time,
            end_time=end_time,
            duration_seconds=int(actual_duration),
            planned_duration_minutes=self.planned_minutes,
            mode=self.current_state,
            completed=completed,
            task_name=task_name,
            category=category,
            interruption_count=self.interruption_count
        )
        
        # Session sonrası temizlik
        self.session_start_time = None
        self.paused_duration = 0
        self.pause_start_time = None
        self.interruption_count = 0  # Kesinti sayısını sıfırla
        
        # Temizle
        self.session_start_time = None
        self.paused_duration = 0
        self.pause_start_time = None

    def _emit_time(self):
        if self.current_time < 0: self.current_time = 0
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        self.timeout_signal.emit(time_str)
