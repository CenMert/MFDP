from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QHBoxLayout, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from mfdp_app.core.notifier import Notifier
from mfdp_app.core.timer import PmdrCountdownTimer, CountUpTimer
from mfdp_app.core.dnd_manager import DNDManager
from mfdp_app.core.task_manager import TaskManager
from mfdp_app.ui.settings_dialog import SettingsDialog
from mfdp_app.ui.stats_window import StatsWindow
from mfdp_app.ui.task_window import TaskWindow
from mfdp_app.ui.recursive_task_window import RecursiveTaskWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.notifier = Notifier()
        self.dnd_manager = DNDManager()
        self.task_manager = TaskManager()
        self.setWindowTitle("MFDP - Focus")
        self.resize(450, 420)
        
        # Dialog instance'larını sakla (non-modal için)
        self.recursive_task_window = None
        self.task_window = None
        self.stats_window = None
        
        # Timer modu ve instance'ları
        self.timer_mode = "countdown"  # "countdown" veya "countup"
        self.timer_logic_countdown = PmdrCountdownTimer(self.task_manager)
        self.timer_logic_countup = CountUpTimer(self.task_manager)
        
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
        self.timer_logic_countdown.reset()

        # Timer durumlarını dinleyerek DND'yi yönetmeliyiz (sadece countdown için)
        self.timer_logic_countdown.state_changed_signal.connect(self.check_dnd_status)
        self.timer_logic_countdown.finished_signal.connect(lambda: self.dnd_manager.disable_dnd())
        
        # TaskManager signal'larını dinle
        self.task_manager.active_task_changed_signal.connect(self.on_task_changed)
        
        # Başlangıçta aktif task'ı göster
        active_task_id = self.task_manager.get_active_task_id()
        if active_task_id:
            self.on_task_changed(active_task_id)
        else:
            self.on_task_changed(-1)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # Üst kısım: Toggle butonu (sağ üstte)
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        # Toggle butonu
        self.btn_toggle_mode = QPushButton("Count Down")
        self.btn_toggle_mode.setFixedSize(120, 30)
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

        self.btn_reset_countup = QPushButton("Sıfırla")
        self.btn_reset_countup.setCursor(Qt.PointingHandCursor)
        self.btn_reset_countup.clicked.connect(self.reset_timer_countup)
        self.btn_reset_countup.setMinimumHeight(60)
        self.btn_reset_countup.setVisible(False)
        btn_layout_countup.addWidget(self.btn_reset_countup)
        
        self.btn_complete_countup = QPushButton("Tamamla")
        self.btn_complete_countup.setCursor(Qt.PointingHandCursor)
        self.btn_complete_countup.clicked.connect(self.complete_timer_countup)
        self.btn_complete_countup.setMinimumHeight(60)
        self.btn_complete_countup.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold;")
        self.btn_complete_countup.setVisible(False)
        btn_layout_countup.addWidget(self.btn_complete_countup)
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

        # YENİ: DND Checkbox
        self.chk_dnd = QCheckBox("Rahatsız Etme")
        self.chk_dnd.setObjectName("DNDCheckbox")
        self.chk_dnd.setChecked(False) # Varsayılan kapalı olsun, kullanıcı seçsin
        self.chk_dnd.setCursor(Qt.PointingHandCursor)
        # Eğer kullanıcı kutucuğu manuel kapatırsa, aktif DND'yi de iptal et
        self.chk_dnd.toggled.connect(self.manual_dnd_toggle)

        settings_layout.addWidget(self.chk_dnd)

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
                self.timer_logic_countup.start_stop()
        
        # Mod değiştir
        if self.timer_mode == "countdown":
            self.timer_mode = "countup"
            self.btn_toggle_mode.setText("Count Up")
            
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
            self.btn_reset_countup.setVisible(True)
            self.btn_complete_countup.setVisible(True)
            
            # Aktif timer'ı değiştir
            self.timer_logic = self.timer_logic_countup
        else:
            self.timer_mode = "countdown"
            self.btn_toggle_mode.setText("Count Down")
            
            # Countup UI'ını gizle
            self.lbl_status_countup.setVisible(False)
            self.lbl_timer_countup.setVisible(False)
            self.btn_start_countup.setVisible(False)
            self.btn_reset_countup.setVisible(False)
            self.btn_complete_countup.setVisible(False)
            
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
        """Başlat/Duraklat butonu mantığına DND kontrolü ekle (countdown için)."""
        is_running = self.timer_logic_countdown.start_stop()

        if is_running:
            self.btn_start.setText("Duraklat")
            self.check_dnd_status() # Timer başladı, DND gerekirse aç
        else:
            self.btn_start.setText("Devam Et")
            self.dnd_manager.disable_dnd() # Duraklatılınca bildirimler gelsin
    
    def toggle_timer_countup(self):
        """Count-up timer için başlat/duraklat."""
        is_running = self.timer_logic_countup.start_stop()
        
        if is_running:
            self.btn_start_countup.setText("Duraklat")
        else:
            self.btn_start_countup.setText("Devam Et")
    
    def reset_timer_countup(self):
        """Count-up timer'ı sıfırla."""
        self.timer_logic_countup.reset()
        self.btn_start_countup.setText("Başlat")
        self.lbl_timer_countup.setText("00:00")
    
    def complete_timer_countup(self):
        """Count-up timer'ı tamamla."""
        self.timer_logic_countup.complete()
        self.btn_start_countup.setText("Başlat")
        self.lbl_timer_countup.setText("00:00")
    
    def update_timer_label_countup(self, time_str):
        """Count-up timer label'ını güncelle."""
        self.lbl_timer_countup.setText(time_str)
    
    def on_timer_finished_countup(self, finished_mode):
        """Count-up timer tamamlandığında."""
        self.lbl_status_countup.setText("Tamamlandı!")
        self.btn_start_countup.setText("Başlat")
            
    def update_timer_label(self, time_str):
        self.lbl_timer.setText(time_str)

    def update_status_label(self, mode):
        self.lbl_status.setText(mode)
        self.btn_start.setText("Başlat")

    def on_timer_finished(self, finished_mode):
        self.lbl_status.setText(f"{finished_mode} Bitti!")
        self.btn_start.setText("Başlat")
    
    def on_task_changed(self, task_id):
        """Aktif task değiştiğinde."""
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
        if self.task_window is None or not self.task_window.isVisible():
            self.task_window = TaskWindow(self.task_manager, self)
            self.task_window.task_selected_signal.connect(self.on_task_selected_from_dialog)
            self.task_window.setModal(False)  # Non-modal yap
            self.task_window.show()
        else:
            # Zaten açıksa öne getir
            self.task_window.raise_()
            self.task_window.activateWindow()
    
    def on_task_selected_from_dialog(self, task_id):
        """Dialog'dan task seçildiğinde."""
        self.task_manager.set_active_task(task_id)
        self.timer_logic.set_task(task_id)
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec(): 
            self.timer_logic.reload_settings()
            if not self.timer_logic.is_running:
                self.timer_logic.reset()

    def open_stats(self):
        """İstatistik penceresini aç."""
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsWindow(self)
            self.stats_window.setModal(False)  # Non-modal yap
            self.stats_window.show()
        else:
            # Zaten açıksa öne getir
            self.stats_window.raise_()
            self.stats_window.activateWindow()
    
    def open_recursive_tasks(self):
        """Özyinelemeli görev yönetim penceresini aç."""
        if self.recursive_task_window is None or not self.recursive_task_window.isVisible():
            self.recursive_task_window = RecursiveTaskWindow(self)
            # setModal(False) zaten __init__ içinde yapılıyor
            self.recursive_task_window.show()
        else:
            # Zaten açıksa öne getir
            self.recursive_task_window.raise_()
            self.recursive_task_window.activateWindow()

    def manual_dnd_toggle(self, checked):
        """Kullanıcı kutucuğa tıkladığında ne olsun?"""
        if not checked:
            # Kutucuk tiki kaldırıldıysa zorla kapat
            self.dnd_manager.disable_dnd()
        # Kutucuk işaretlendiyse hemen açmıyoruz, Timer başlayınca açılacak.

    def check_dnd_status(self, mode=None):
        """Şu anki duruma göre DND açılmalı mı?"""
        # Eğer mode parametresi gelmediyse mevcut modu al
        if not mode:
            mode = self.timer_logic.current_state

        # Kurallar:
        # 1. Checkbox işaretli olmalı.
        # 2. Timer çalışıyor olmalı (is_running).
        # 3. Mod "Focus" olmalı (Molada rahatsız edilmek isteyebiliriz).

        if self.chk_dnd.isChecked() and self.timer_logic.is_running and mode == "Focus":
            self.dnd_manager.enable_dnd()
        else:
            self.dnd_manager.disable_dnd()

    def reset_timer(self):
        """Countdown timer'ı sıfırla."""
        self.timer_logic_countdown.reset()
        self.dnd_manager.disable_dnd()
    
    def closeEvent(self, event: QCloseEvent):
        """Uygulama kapanırken aktif timer'ları kaydet."""
        self.timer_logic_countdown.save_on_exit()
        self.timer_logic_countup.save_on_exit()
        event.accept()