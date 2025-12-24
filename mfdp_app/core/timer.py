import datetime
from PySide6.QtCore import QTimer, QObject, Signal
from mfdp_app.db_manager import log_session_v2, load_settings 

class PomodoroTimer(QObject):
    timeout_signal = Signal(str)
    finished_signal = Signal(str)
    state_changed_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        
        # Ayarlar (Default)
        self.durations = {"Focus": 25, "Short Break": 5, "Long Break": 15}
        self.reload_settings() 
        
        self.current_state = "Focus"
        self.is_running = False
        
        # V2 Verileri
        self.session_start_time = None 
        self.planned_minutes = 0 
        self.paused_duration = 0  # Duraklatma süresi (saniye)
        self.pause_start_time = None  # Duraklatma başlangıç zamanı
        
        self._set_time_based_on_state()

    def start_stop(self):
        if self.is_running:
            # DURAKLAT
            self.timer.stop()
            self.is_running = False
            self.pause_start_time = datetime.datetime.now()
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
        self.planned_minutes = self.durations.get(mode, 25)  # YENİ MODUN SÜRESİNİ AYARLA
        self._set_time_based_on_state()
        self.state_changed_signal.emit(mode)
        self._emit_time()
        
    def reload_settings(self):
        settings = load_settings()
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
        
        log_session_v2(
            start_time=self.session_start_time,
            end_time=end_time,
            duration_sec=int(actual_duration),
            planned_min=self.planned_minutes,
            mode=self.current_state,
            completed=completed
        )
        
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