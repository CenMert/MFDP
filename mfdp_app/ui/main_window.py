import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QHBoxLayout, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from mfdp_app.core.notifier import Notifier
from mfdp_app.core.timer import PmdrCountdownTimer, CountUpTimer
from mfdp_app.core.dnd_manager import DNDManager
from mfdp_app.core.task_manager import TaskManager
from mfdp_app.core.atomic_analyzer import AtomicAnalyzer
from mfdp_app.core.panel_bridge import PanelBridge
from mfdp_app.ui.settings_dialog import SettingsDialog
from mfdp_app.ui.stats_window import StatsWindow
from mfdp_app.ui.calendar_window import CalendarWindow
from mfdp_app.ui.task_window import TaskWindow
from mfdp_app.ui.recursive_task_window import RecursiveTaskWindow
from mfdp_app.ui.day_panel import DayPanel
from mfdp_app.ui.mini_window import MiniWindow
from mfdp_app.ui.block_detail_dialog import BlockDetailDialog
from mfdp_app.core.daily_report import build_block_report, logical_day, WORK_MODES
from mfdp_app.core.plan_scheduler import PlanScheduler
from mfdp_app.core import review_scheduler
from mfdp_app.db.plan_repository import PlanRepository
from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.ui.side_panel import SidePanel, plan_sentence
from mfdp_app.ui.plans_dialog import PlansDialog
from mfdp_app.ui.lecture_dialog import LectureDialog
from mfdp_app.ui.tracking_dialog import TrackingDialog
from mfdp_app.ui.feedback_strip import FeedbackStrip

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.notifier = Notifier()
        self.dnd_manager = DNDManager(self)
        self.task_manager = TaskManager()
        self.atomic_analyzer = AtomicAnalyzer()
        self.setWindowTitle("MFDP - Focus")
        self.resize(450, 420)

        # Dialog instance'larını sakla (non-modal için)
        self.recursive_task_window = None
        self.task_window = None
        self.stats_window = None
        self.calendar_window = None
        self.mini_window = None

        # Timer modu ve instance'ları
        self.timer_mode = "countdown"  # "countdown" veya "countup"
        self.timer_logic_countdown = PmdrCountdownTimer(self.task_manager, self.atomic_analyzer)
        self.timer_logic_countup = CountUpTimer(self.task_manager, self.atomic_analyzer)
        
        # Aktif timer (başlangıçta countdown)
        self.timer_logic = self.timer_logic_countdown
        
        # Countdown timer signal'leri
        self.timer_logic_countdown.timeout_signal.connect(self.update_timer_label)
        self.timer_logic_countdown.state_changed_signal.connect(self.update_status_label)
        self.timer_logic_countdown.finished_signal.connect(self.on_timer_finished)
        self.timer_logic_countdown.finished_signal.connect(self.notifier.play_alarm)
        self.timer_logic_countdown.task_changed_signal.connect(self.on_task_changed)
        
        # Countup timer signal'leri
        self.timer_logic_countup.timeout_signal.connect(self.update_timer_label_countup)
        self.timer_logic_countup.finished_signal.connect(self.on_timer_finished_countup)
        self.timer_logic_countup.finished_signal.connect(self.notifier.play_alarm)
        self.timer_logic_countup.task_changed_signal.connect(self.on_task_changed)

        self.init_ui()

        # Oturum DB'ye yazılınca gün panelini tazele
        self.timer_logic_countdown.session_saved_signal.connect(self.day_panel.refresh)
        self.timer_logic_countup.session_saved_signal.connect(self.day_panel.refresh)
        self.timer_logic_countdown.session_saved_signal.connect(self.on_session_saved)
        self.timer_logic_countup.session_saved_signal.connect(self.on_session_saved)
        self._last_session_id = None
        self._pending_plan_log = None  # "Başla" denen planın log id'si; ilk kaydedilen oturuma bağlanır

        # Eğer-ise planları: saati gelince sor
        self.plan_scheduler = PlanScheduler(self)
        self.plan_scheduler.plan_due.connect(self.on_plan_due)
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_side_panel)

        self.timer_logic_countdown.reset()

        # Count-up birincil mod: açılışta ona geç
        self.toggle_timer_mode()
        QShortcut(QKeySequence("I"), self, lambda: self.mark_interruption_countup("internal"))
        QShortcut(QKeySequence("E"), self, lambda: self.mark_interruption_countup("external"))

        # DND sadece tuş / Ctrl+D ile yönetilir
        self.dnd_manager.dnd_changed_signal.connect(self.on_dnd_changed)
        QShortcut(QKeySequence("Ctrl+D"), self, self.toggle_dnd_manual)
        
        # TaskManager signal'larını dinle
        self.task_manager.active_task_changed_signal.connect(self.on_task_changed)
        
        # Başlangıçta aktif task'ı göster
        active_task_id = self.task_manager.get_active_task_id()
        if active_task_id:
            self.on_task_changed(active_task_id)
        else:
            self.on_task_changed(-1)

        # KDE panel widget köprüsü (durum dosyası + D-Bus Toggle)
        self.panel_bridge = PanelBridge(self._panel_snapshot, self)
        self.panel_bridge.toggle_requested.connect(self.mini_toggle)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        outer_layout = QHBoxLayout(central_widget)
        outer_layout.setContentsMargins(12, 12, 0, 12)
        outer_layout.setSpacing(0)

        # Sol yan panel: süreklilik ızgarası + eğer-ise planları (başlangıçta kapalı)
        self.side_panel = SidePanel()
        self.side_panel.setVisible(False)
        self.side_panel.edit_plans_requested.connect(self.open_plans)
        self.side_panel.review_start_requested.connect(self.start_task_session)
        self.side_panel.lecture_requested.connect(self.open_lecture_dialog)
        self.side_panel.tracking_requested.connect(self.open_tracking_dialog)
        outer_layout.addWidget(self.side_panel)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(28, 28, 40, 28)
        main_layout.setSpacing(20)
        outer_layout.addWidget(content, 1)

        # Üst kısım: yan panel tuşu (solda), mod tuşu (sağda)
        top_layout = QHBoxLayout()
        self.btn_side = QPushButton("▤  Süreklilik")
        self.btn_side.setObjectName("SideToggle")
        self.btn_side.setCheckable(True)
        self.btn_side.setCursor(Qt.PointingHandCursor)
        self.btn_side.setToolTip("Seri ızgarası ve eğer-ise planları (Ctrl+B)")
        self.btn_side.clicked.connect(self.toggle_side_panel)
        top_layout.addWidget(self.btn_side)
        top_layout.addStretch()
        
        # Toggle butonu
        self.btn_toggle_mode = QPushButton("Count Down")
        self.btn_toggle_mode.setFixedSize(250, 40)
        self.btn_toggle_mode.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_mode.clicked.connect(self.toggle_timer_mode)
        self.btn_toggle_mode.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        top_layout.addWidget(self.btn_toggle_mode)
        main_layout.addLayout(top_layout)

        # Status label (countdown için)
        self.lbl_status = QLabel("Focus")
        self.lbl_status.setObjectName("StatusLabel")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_status)
        
        # Status label (countup için - başlangıçta gizli)
        self.lbl_status_countup = QLabel("Free Timer")
        self.lbl_status_countup.setObjectName("StatusLabel")
        self.lbl_status_countup.setAlignment(Qt.AlignCenter)
        self.lbl_status_countup.setVisible(False)
        main_layout.addWidget(self.lbl_status_countup)
        
        # Aktif task gösterimi - iki buton (tag ve task name)
        task_layout = QHBoxLayout()
        task_layout.setAlignment(Qt.AlignCenter)
        task_layout.setSpacing(5)
        
        self.btn_tag = QPushButton("")
        self.btn_tag.setEnabled(False)  # Tıklanamaz
        self.btn_tag.setStyleSheet("""
            font-size: 12px; 
            font-weight: bold; 
            color: #cdd6f4; 
            background-color: #313244; 
            border: 1px solid #45475a; 
            border-radius: 5px; 
            padding: 5px 10px;
        """)
        
        self.btn_task_name = QPushButton("")
        self.btn_task_name.setEnabled(False)  # Tıklanamaz
        self.btn_task_name.setStyleSheet("""
            font-size: 14px; 
            color: #bac2de; 
            background-color: #313244; 
            border: 1px solid #45475a; 
            border-radius: 5px; 
            padding: 5px 15px;
        """)
        
        # Başlangıçta görünmez
        self.btn_tag.setVisible(False)
        self.btn_task_name.setVisible(False)
        
        task_layout.addWidget(self.btn_tag)
        task_layout.addWidget(self.btn_task_name)
        main_layout.addLayout(task_layout)

        # Timer label (countdown için)
        self.lbl_timer = QLabel("25:00")
        self.lbl_timer.setObjectName("TimerLabel")
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_timer)
        
        # Timer label (countup için - başlangıçta gizli)
        self.lbl_timer_countup = QLabel("00:00")
        self.lbl_timer_countup.setObjectName("TimerLabel")
        self.lbl_timer_countup.setAlignment(Qt.AlignCenter)
        self.lbl_timer_countup.setVisible(False)
        main_layout.addWidget(self.lbl_timer_countup)

        # Gün paneli (açılır özet, her iki modda da görünür)
        # Oturum sonu geri bildirimi (odak puanı + oturum türü)
        self.feedback_strip = FeedbackStrip()
        self.feedback_strip.rating_selected.connect(lambda v: self._save_feedback(focus_rating=v))
        self.feedback_strip.kind_selected.connect(lambda k: self._save_feedback(session_kind=k))
        self.feedback_strip.recall_selected.connect(self._on_recall)
        main_layout.addWidget(self.feedback_strip)

        self.day_panel = DayPanel()
        self.day_panel.block_clicked.connect(self.open_block_detail)
        self.day_panel.expanded_changed.connect(self.on_day_panel_toggled)
        main_layout.addWidget(self.day_panel)

        # Butonlar (countdown için)
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Başlat")
        self.btn_start.setObjectName("StartButton")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_start.setMinimumHeight(60)
        btn_layout.addWidget(self.btn_start)

        self.btn_reset = QPushButton("Sıfırla")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_timer)
        self.btn_reset.setMinimumHeight(60)
        btn_layout.addWidget(self.btn_reset)
        main_layout.addLayout(btn_layout)
        
        # Butonlar (countup için - başlangıçta gizli)
        btn_layout_countup = QHBoxLayout()
        self.btn_start_countup = QPushButton("Başlat")
        self.btn_start_countup.setObjectName("StartButton")
        self.btn_start_countup.setCursor(Qt.PointingHandCursor)
        self.btn_start_countup.clicked.connect(self.toggle_timer_countup)
        self.btn_start_countup.setMinimumHeight(60)
        self.btn_start_countup.setVisible(False)
        btn_layout_countup.addWidget(self.btn_start_countup)

        # Duraklatma yok: kesintiler oturumu durdurmadan işaretlenir
        self.btn_internal_countup = QPushButton("İç kesinti")
        self.btn_internal_countup.setCursor(Qt.PointingHandCursor)
        self.btn_internal_countup.setToolTip("Aklım dağıldı / kendim böldüm (I)")
        self.btn_internal_countup.clicked.connect(lambda: self.mark_interruption_countup("internal"))
        self.btn_internal_countup.setMinimumHeight(60)
        self.btn_internal_countup.setVisible(False)
        btn_layout_countup.addWidget(self.btn_internal_countup)

        self.btn_external_countup = QPushButton("Dış kesinti")
        self.btn_external_countup.setCursor(Qt.PointingHandCursor)
        self.btn_external_countup.setToolTip("Biri / bir şey böldü (E)")
        self.btn_external_countup.clicked.connect(lambda: self.mark_interruption_countup("external"))
        self.btn_external_countup.setMinimumHeight(60)
        self.btn_external_countup.setVisible(False)
        btn_layout_countup.addWidget(self.btn_external_countup)
        main_layout.addLayout(btn_layout_countup)

        # Mola butonları (sadece countdown için)
        self.mode_layout = QHBoxLayout()
        self.mode_buttons = []
        modes = [("Focus", "Focus"), ("Kısa Mola", "Short Break"), ("Uzun Mola", "Long Break")]
        for btn_text, mode_key in modes:
            btn = QPushButton(btn_text)
            btn.setObjectName("ModeButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=mode_key: self.timer_logic_countdown.set_mode(m))
            self.mode_buttons.append(btn)
            self.mode_layout.addWidget(btn)
        main_layout.addLayout(self.mode_layout)

        # ALT KONTROLLER
        settings_layout = QHBoxLayout() 
        
        self.chk_chime = QCheckBox("Gong Sesi")
        self.chk_chime.setObjectName("ChimeCheckbox")
        self.chk_chime.setChecked(True)
        self.chk_chime.setCursor(Qt.PointingHandCursor)
        self.chk_chime.toggled.connect(self.notifier.set_chime_enabled)
        settings_layout.addWidget(self.chk_chime)
        
        settings_layout.addStretch()

        # DND tuşu: sistem genelinde Rahatsız Etme aç/kapat (Ctrl+D)
        self.btn_dnd = QPushButton("🔕")
        self.btn_dnd.setObjectName("DNDButton")
        self.btn_dnd.setCheckable(True)
        self.btn_dnd.setCursor(Qt.PointingHandCursor)
        self.btn_dnd.setFixedWidth(40)
        self.btn_dnd.setToolTip("Rahatsız Etme'yi şimdi aç/kapat (Ctrl+D)")
        self.btn_dnd.setStyleSheet("QPushButton#DNDButton:checked { background-color: #f38ba8; color: #1e1e2e; }")
        self.btn_dnd.setEnabled(self.dnd_manager.is_available)
        self.btn_dnd.clicked.connect(self.toggle_dnd_manual)
        settings_layout.addWidget(self.btn_dnd)

        # Task Butonu
        self.btn_tasks = QPushButton("Tasklar")
        self.btn_tasks.setCursor(Qt.PointingHandCursor)
        self.btn_tasks.clicked.connect(self.open_tasks)
        self.btn_tasks.setFixedWidth(100)
        self.btn_tasks.setStyleSheet("background-color: #cba6f7; color: #1e1e2e; font-weight: bold; border: none;")
        settings_layout.addWidget(self.btn_tasks)

        settings_layout.addSpacing(10)

        # Recursive Task Butonu
        self.btn_recursive_tasks = QPushButton("Hiyerarşik Görevler")
        self.btn_recursive_tasks.setCursor(Qt.PointingHandCursor)
        self.btn_recursive_tasks.clicked.connect(self.open_recursive_tasks)
        self.btn_recursive_tasks.setFixedWidth(180)
        self.btn_recursive_tasks.setStyleSheet("background-color: #f9e2af; color: #1e1e2e; font-weight: bold; border: none;")
        settings_layout.addWidget(self.btn_recursive_tasks)

        settings_layout.addSpacing(10)

        # İstatistik Butonu
        self.btn_stats = QPushButton("İstatistik")
        self.btn_stats.setCursor(Qt.PointingHandCursor)
        self.btn_stats.clicked.connect(self.open_stats)
        self.btn_stats.setFixedWidth(100)
        self.btn_stats.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; font-weight: bold; border: none;")
        settings_layout.addWidget(self.btn_stats)

        settings_layout.addSpacing(10)

        # Takvim Butonu
        self.btn_calendar = QPushButton("Takvim")
        self.btn_calendar.setCursor(Qt.PointingHandCursor)
        self.btn_calendar.clicked.connect(self.open_calendar)
        self.btn_calendar.setFixedWidth(100)
        self.btn_calendar.setStyleSheet("background-color: #94e2d5; color: #1e1e2e; font-weight: bold; border: none;")
        settings_layout.addWidget(self.btn_calendar)

        settings_layout.addSpacing(10)

        # Mini Mod Butonu
        self.btn_mini = QPushButton("Mini")
        self.btn_mini.setCursor(Qt.PointingHandCursor)
        self.btn_mini.clicked.connect(self.open_mini)
        self.btn_mini.setFixedWidth(100)
        settings_layout.addWidget(self.btn_mini)

        settings_layout.addSpacing(10)

        self.btn_settings = QPushButton("Ayarlar")
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_settings.setFixedWidth(100)
        settings_layout.addWidget(self.btn_settings)
        
        main_layout.addLayout(settings_layout)

    def toggle_timer_mode(self):
        """Count-down ve count-up arasında geçiş yap."""
        # Aktif timer'ı durdur
        if self.timer_mode == "countdown":
            if self.timer_logic_countdown.is_running:
                self.timer_logic_countdown.start_stop()
        else:
            if self.timer_logic_countup.is_running:
                self.finish_timer_countup()
        
        # Mod değiştir
        if self.timer_mode == "countdown":
            self.timer_mode = "countup"
            self.btn_toggle_mode.setText("Count Up - Free Timer")
            
            # Countdown UI'ını gizle
            self.lbl_status.setVisible(False)
            self.lbl_timer.setVisible(False)
            self.btn_start.setVisible(False)
            self.btn_reset.setVisible(False)
            # Mola butonlarını gizle
            for btn in self.mode_buttons:
                btn.setVisible(False)
            
            # Countup UI'ını göster
            self.lbl_status_countup.setVisible(True)
            self.lbl_timer_countup.setVisible(True)
            self.btn_start_countup.setVisible(True)
            self.btn_internal_countup.setVisible(True)
            self.btn_external_countup.setVisible(True)
            self._sync_countup_buttons()
            
            # Aktif timer'ı değiştir
            self.timer_logic = self.timer_logic_countup
        else:
            self.timer_mode = "countdown"
            self.btn_toggle_mode.setText("Count Down - Pomodoro")
            
            # Countup UI'ını gizle
            self.lbl_status_countup.setVisible(False)
            self.lbl_timer_countup.setVisible(False)
            self.btn_start_countup.setVisible(False)
            self.btn_internal_countup.setVisible(False)
            self.btn_external_countup.setVisible(False)
            
            # Countdown UI'ını göster
            self.lbl_status.setVisible(True)
            self.lbl_timer.setVisible(True)
            self.btn_start.setVisible(True)
            self.btn_reset.setVisible(True)
            # Mola butonlarını göster
            for btn in self.mode_buttons:
                btn.setVisible(True)
            
            # Aktif timer'ı değiştir
            self.timer_logic = self.timer_logic_countdown
            self.timer_logic_countdown.reset()
    
    def toggle_timer(self):
        """Countdown timer için başlat/duraklat."""
        is_running = self.timer_logic_countdown.start_stop()

        if is_running:
            self.feedback_strip.hide()
            self.notifier.play_start_counter_sound()
            self.btn_start.setText("Duraklat")
        else:
            self.notifier.play_pause_counter_sound()
            self.btn_start.setText("Devam Et")
    
    def toggle_timer_countup(self):
        """Count-up: durmuşsa başlat, çalışıyorsa bitir (duraklatma yok)."""
        if self.timer_logic_countup.is_running:
            self.finish_timer_countup()
        else:
            self.timer_logic_countup.start()
            self.feedback_strip.hide()
            self.notifier.play_start_counter_sound()
            self.lbl_status_countup.setText("Odakta")
            self._sync_countup_buttons()

    def finish_timer_countup(self):
        """Count-up oturumunu bitir ve kaydet. Devam etmek yeni oturumdur."""
        saved = self.timer_logic_countup.finish()
        self.lbl_status_countup.setText(
            "Kaydedildi — mola zamanı" if saved else "1 dk altı, kaydedilmedi")
        self.lbl_timer_countup.setText("00:00")
        self._sync_countup_buttons()

    def mark_interruption_countup(self, kind):
        """İç/dış kesinti: oturum akmaya devam eder."""
        if self.timer_mode != "countup":
            return
        count = self.timer_logic_countup.mark_interruption(kind)
        if count:
            label = "İç" if kind == "internal" else "Dış"
            self.lbl_status_countup.setText(f"{label} kesinti işaretlendi · toplam {count}")

    def _sync_countup_buttons(self):
        running = self.timer_logic_countup.is_running
        self.btn_start_countup.setText("Bitir" if running else "Başlat")
        self.btn_internal_countup.setEnabled(running)
        self.btn_external_countup.setEnabled(running)
        if self.mini_window is not None:
            self.mini_window.set_paused(not running)

    def update_timer_label_countup(self, time_str):
        """Count-up timer label'ını güncelle."""
        self._mini_set_time(time_str)
        self.lbl_timer_countup.setText(time_str)
    
    def on_timer_finished_countup(self, finished_mode):
        """Count-up oturumu bittiğinde (durum yazısını finish_timer_countup belirler)."""
        self._sync_countup_buttons()
            
    def update_timer_label(self, time_str):
        self._mini_set_time(time_str)
        self.lbl_timer.setText(time_str)

    def update_status_label(self, mode):
        self.lbl_status.setText(mode)
        self.btn_start.setText("Başlat")

    def on_timer_finished(self, finished_mode):
        self.lbl_status.setText(f"{finished_mode} Bitti!")
        self.btn_start.setText("Başlat")
    
    def on_task_changed(self, task_id):
        """Aktif task değiştiğinde."""
        self._mini_sync_color(task_id)
        if task_id == -1 or task_id is None:
            self.btn_tag.setText("")
            self.btn_task_name.setText("")
            self.btn_tag.setVisible(False)
            self.btn_task_name.setVisible(False)
        else:
            task = self.task_manager.get_task_by_id(task_id)
            if task:
                # Tag butonu - kalın harflerle
                self.btn_tag.setText(task.tag.upper())
                self.btn_task_name.setText(task.name)
                self.btn_tag.setVisible(True)
                self.btn_task_name.setVisible(True)
                
                # Tag rengini al ve butona uygula
                tag_info = next((t for t in self.task_manager.get_all_tags() if t['name'] == task.tag), None)
                if tag_info and tag_info.get('color'):
                    tag_color = tag_info['color']
                    self.btn_tag.setStyleSheet(f"""
                        font-size: 12px; 
                        font-weight: bold; 
                        color: #1e1e2e; 
                        background-color: {tag_color}; 
                        border: 1px solid {tag_color}; 
                        border-radius: 5px; 
                        padding: 0px 10px;
                    """)
                else:
                    # Varsayılan stil
                    self.btn_tag.setStyleSheet("""
                        font-size: 12px; 
                        font-weight: bold; 
                        color: #cdd6f4; 
                        background-color: #313244; 
                        border: 1px solid #45475a; 
                        border-radius: 5px; 
                        padding: 0px 10px;
                    """)
                
                # Her iki timer'a da task ata (set_task içinde zaten kontrol var, ama ek güvenlik için)
                # Timer'ların mevcut task_id'si farklıysa güncelle
                if self.timer_logic_countdown.current_task_id != task_id:
                    self.timer_logic_countdown.set_task(task_id)
                if self.timer_logic_countup.current_task_id != task_id:
                    self.timer_logic_countup.set_task(task_id)
    
    def open_tasks(self):
        """Task yönetim penceresini aç."""
        if not self._window_alive(self.task_window) or not self.task_window.isVisible():
            if self._window_alive(self.task_window):
                self.task_window.deleteLater()
            self.task_window = TaskWindow(self.task_manager, self)
            self.task_window.setAttribute(Qt.WA_DeleteOnClose)
            self.task_window.task_selected_signal.connect(self.on_task_selected_from_dialog)
            self.task_window.setModal(False)
            self.task_window.show()
        else:
            self.task_window.raise_()
            self.task_window.activateWindow()
    
    def on_task_selected_from_dialog(self, task_id):
        """Dialog'dan task seçildiğinde."""
        self.task_manager.set_active_task(task_id)
        self.timer_logic.set_task(task_id)
    
    def open_settings(self):
        dialog = SettingsDialog(self, notifier=self.notifier)
        if dialog.exec():
            self.timer_logic.reload_settings()
            if not self.timer_logic.is_running:
                self.timer_logic.reset()

    def _window_alive(self, win):
        """Qt C++ nesnesi silinmişse False döner."""
        if win is None:
            return False
        try:
            win.isVisible()
            return True
        except RuntimeError:
            return False

    def open_stats(self):
        """İstatistik penceresini aç."""
        if not self._window_alive(self.stats_window) or not self.stats_window.isVisible():
            if self._window_alive(self.stats_window):
                self.stats_window.deleteLater()
            self.stats_window = StatsWindow(self)
            self.stats_window.show()
        else:
            self.stats_window.raise_()
            self.stats_window.activateWindow()

    def open_calendar(self):
        """Takvim penceresini aç."""
        if not self._window_alive(self.calendar_window) or not self.calendar_window.isVisible():
            if self._window_alive(self.calendar_window):
                self.calendar_window.deleteLater()
            self.calendar_window = CalendarWindow(self)
            self.calendar_window.show()
        else:
            self.calendar_window.raise_()
            self.calendar_window.activateWindow()

    def _mini_set_time(self, time_str):
        if self.mini_window is not None:
            self.mini_window.set_time(time_str)

    def _task_color(self, task_id):
        """Görevin etiket rengi; görev yoksa None."""
        if task_id in (None, -1):
            return None
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            return None
        tag_info = next((t for t in self.task_manager.get_all_tags() if t['name'] == task.tag), None)
        return tag_info.get('color') if tag_info else None

    def _mini_sync_color(self, task_id):
        if self.mini_window is None:
            return
        self.mini_window.set_color(self._task_color(task_id))

    def _panel_snapshot(self):
        """KDE panel widget'ının okuyacağı durum."""
        return {
            "running": self.timer_logic.is_running,
            "mode": self.timer_mode,
            "seconds": self.timer_logic.current_time,
            "color": self._task_color(self.timer_logic.current_task_id),
        }

    def open_mini(self):
        """Mini pencereyi göster (ana pencere açık kalır)."""
        if self.mini_window is None:
            self.mini_window = MiniWindow()
            self.mini_window.restore_requested.connect(self.close_mini)
            self.mini_window.toggle_requested.connect(self.mini_toggle)
        lbl = self.lbl_timer if self.timer_mode == "countdown" else self.lbl_timer_countup
        self.mini_window.set_time(lbl.text())
        self.mini_window.set_paused(not self.timer_logic.is_running)
        self._mini_sync_color(self.timer_logic.current_task_id)
        self.mini_window.show()

    def mini_toggle(self):
        """Mini pencere / panel tek tık: countdown'da duraklat/devam, count-up'ta başlat/bitir."""
        if self.timer_mode == "countdown":
            self.toggle_timer()
        else:
            self.toggle_timer_countup()
        if self.mini_window is not None:
            self.mini_window.set_paused(not self.timer_logic.is_running)
        self.panel_bridge.publish()

    def close_mini(self):
        self.mini_window.hide()

    def open_recursive_tasks(self):
        """Özyinelemeli görev yönetim penceresini aç."""
        if not self._window_alive(self.recursive_task_window) or not self.recursive_task_window.isVisible():
            if self._window_alive(self.recursive_task_window):
                self.recursive_task_window.deleteLater()
            self.recursive_task_window = RecursiveTaskWindow(self)
            self.recursive_task_window.setAttribute(Qt.WA_DeleteOnClose)
            self.recursive_task_window.show()
        else:
            self.recursive_task_window.raise_()
            self.recursive_task_window.activateWindow()

    def open_block_detail(self, block, color):
        """Gün panelinden seçilen bloğun ayrıntılı raporunu aç."""
        dialog = BlockDetailDialog(build_block_report(block, color), self)
        dialog.show()

    def on_day_panel_toggled(self, expanded):
        """Panel açılınca pencere uzasın, kapanınca eski boyuna dönsün."""
        QTimer.singleShot(0, lambda: self.resize(self.width(), self.sizeHint().height()))

    def toggle_dnd_manual(self):
        """DND tuşu / Ctrl+D: aç-kapat."""
        self.dnd_manager.toggle_dnd()
        # Servis yoksa / hata olduysa tuş gerçek durumu göstersin
        self.btn_dnd.setChecked(self.dnd_manager.is_active)

    def on_dnd_changed(self, enabled):
        """DND gerçekten açıldı/kapandı: tuşu senkronla, olayı kaydet."""
        self.btn_dnd.setChecked(enabled)
        self.atomic_analyzer.record_dnd_toggle(enabled)

    # ------------------------------------------------------------------
    # Yan panel, eğer-ise planları, oturum sonu geri bildirimi
    # ------------------------------------------------------------------
    def toggle_side_panel(self):
        show = not self.side_panel.isVisible()
        if show:
            self.side_panel.refresh()
        self.side_panel.setVisible(show)
        self.btn_side.setChecked(show)
        delta = SidePanel.WIDTH if show else -SidePanel.WIDTH
        QTimer.singleShot(0, lambda: self.resize(max(self.minimumSizeHint().width(), self.width() + delta),
                                                 self.height()))

    def open_lecture_dialog(self):
        """Derste işlenenleri gir: aktif görevin (varsa) dersi varsayılan olarak seçilir."""
        course_id = None
        active = self.task_manager.get_active_task()
        if active:
            course_id = active.parent_id or active.id
        dialog = LectureDialog(self, course_id)
        dialog.topics_added.connect(self.side_panel.refresh)
        dialog.exec()
        self.side_panel.refresh()

    def open_tracking_dialog(self):
        dialog = TrackingDialog(self)
        dialog.tracking_changed.connect(self.side_panel.refresh)
        dialog.exec()
        self.side_panel.refresh()

    def open_plans(self):
        dialog = PlansDialog(self)
        dialog.plans_changed.connect(self.side_panel.refresh)
        dialog.exec()
        self.side_panel.refresh()

    def on_session_saved(self, session_id):
        self._last_session_id = session_id
        if self._pending_plan_log:
            PlanRepository.attach_session(self._pending_plan_log, session_id)
            self._pending_plan_log = None
        session = SessionRepository.get_session(session_id)
        if session and session['mode'] in WORK_MODES:
            self.feedback_strip.open_for_session()
            self.feedback_strip.recall_allowed = review_scheduler.is_task_tracked(session['task_name'])
            QTimer.singleShot(0, lambda: self.resize(self.width(), self.sizeHint().height()))
        if self.side_panel.isVisible():
            self.side_panel.refresh()

    def _save_feedback(self, focus_rating=None, session_kind=None):
        if self._last_session_id:
            SessionRepository.set_session_feedback(self._last_session_id, focus_rating, session_kind)
            if session_kind:
                # Okuma / soru / üretim konuyu tekrar takvimine alır
                session = SessionRepository.get_session(self._last_session_id)
                review_scheduler.on_session_kind(session and session['task_name'], session_kind)
                self._refresh_side_panel_if_open()

    def _on_recall(self, recall):
        """'Tekrar' oturumundan sonra 1-4 hatırlama puanı: konunun takvimini ilerlet / başa sar."""
        if not self._last_session_id:
            return
        session = SessionRepository.get_session(self._last_session_id)
        review_scheduler.apply_recall(session and session['task_name'], self._last_session_id, recall)
        self._refresh_side_panel_if_open()

    def _refresh_side_panel_if_open(self):
        if self.side_panel.isVisible():
            self.side_panel.refresh()

    def start_task_session(self, task_id):
        """Görevi seç, count-up'a geç ve oturumu başlat (plan 'Başla' ve tekrar satırı için ortak)."""
        if task_id:
            self.task_manager.set_active_task(task_id)
        if self.timer_mode != "countup":
            self.toggle_timer_mode()
        if not self.timer_logic_countup.is_running:
            self.toggle_timer_countup()

    def on_plan_due(self, plan):
        """Planın saati geldi: başla / ertele / atla."""
        box = QMessageBox(self)
        box.setWindowTitle("Plan zamanı")
        box.setIcon(QMessageBox.Information)
        box.setText(plan_sentence(plan))
        box.setInformativeText("Önceden verdiğin karar. Şimdi başlıyor musun?")
        btn_start = box.addButton("Başla", QMessageBox.AcceptRole)
        btn_snooze = box.addButton("10 dk ertele", QMessageBox.ActionRole)
        box.addButton("Bugün atla", QMessageBox.RejectRole)
        box.setStyleSheet("QMessageBox { background-color: #1e1e2e; }")
        box.setAttribute(Qt.WA_DeleteOnClose)
        box.setModal(False)

        def handle(button):
            day = logical_day(datetime.datetime.now())
            if button is btn_start:
                self._pending_plan_log = PlanRepository.log_outcome(plan['id'], day, 'started')
                self.start_task_session(plan.get('task_id'))
            elif button is btn_snooze:
                PlanRepository.log_outcome(plan['id'], day, 'snoozed')
                self.plan_scheduler.snooze(plan['id'], 10)
            else:
                PlanRepository.log_outcome(plan['id'], day, 'skipped')
            if self.side_panel.isVisible():
                self.side_panel.refresh()

        box.buttonClicked.connect(handle)
        self.notifier.play_start_counter_sound()
        self.raise_()
        self.activateWindow()
        box.show()

    def reset_timer(self):
        """Countdown timer'ı sıfırla."""
        self.timer_logic_countdown.reset()
    
    def closeEvent(self, event: QCloseEvent):
        """Uygulama kapanırken aktif timer'ları kaydet."""
        self.panel_bridge.shutdown()
        if self.mini_window is not None:
            self.mini_window.close()
        self.timer_logic_countdown.save_on_exit()
        self.timer_logic_countup.save_on_exit()
        self.dnd_manager.disable_dnd()
        event.accept()