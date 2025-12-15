from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QHBoxLayout, QCheckBox)
from PySide6.QtCore import Qt
from mfdp_app.core.notifier import Notifier
from mfdp_app.core.timer import PomodoroTimer
from mfdp_app.ui.settings_dialog import SettingsDialog
from mfdp_app.ui.stats_window import StatsWindow # YENİ IMPORT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.notifier = Notifier()
        self.setWindowTitle("MFDP - Focus")
        self.resize(450, 420)
        
        self.timer_logic = PomodoroTimer()
        self.timer_logic.timeout_signal.connect(self.update_timer_label)
        self.timer_logic.state_changed_signal.connect(self.update_status_label)
        self.timer_logic.finished_signal.connect(self.on_timer_finished)
        self.timer_logic.finished_signal.connect(self.notifier.play_alarm)

        self.init_ui()
        self.timer_logic.reset()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        self.lbl_status = QLabel("Focus")
        self.lbl_status.setObjectName("StatusLabel")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_status)

        self.lbl_timer = QLabel("25:00")
        self.lbl_timer.setObjectName("TimerLabel")
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_timer)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Başlat")
        self.btn_start.setObjectName("StartButton")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_start.setMinimumHeight(60)
        btn_layout.addWidget(self.btn_start)

        self.btn_reset = QPushButton("Sıfırla")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.timer_logic.reset)
        self.btn_reset.setMinimumHeight(60)
        btn_layout.addWidget(self.btn_reset)
        main_layout.addLayout(btn_layout)

        mode_layout = QHBoxLayout()
        modes = [("Focus", "Focus"), ("Kısa Mola", "Short Break"), ("Uzun Mola", "Long Break")]
        for btn_text, mode_key in modes:
            btn = QPushButton(btn_text)
            btn.setObjectName("ModeButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, m=mode_key: self.timer_logic.set_mode(m))
            mode_layout.addWidget(btn)
        main_layout.addLayout(mode_layout)

        # ALT KONTROLLER
        settings_layout = QHBoxLayout()
        
        self.chk_chime = QCheckBox("Gong Sesi")
        self.chk_chime.setObjectName("ChimeCheckbox")
        self.chk_chime.setChecked(True)
        self.chk_chime.setCursor(Qt.PointingHandCursor)
        self.chk_chime.toggled.connect(self.notifier.set_chime_enabled)
        settings_layout.addWidget(self.chk_chime)
        
        settings_layout.addStretch()

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

    def toggle_timer(self):
        is_running = self.timer_logic.start_stop()
        if is_running:
            self.btn_start.setText("Duraklat")
        else:
            self.btn_start.setText("Devam Et")
            
    def update_timer_label(self, time_str):
        self.lbl_timer.setText(time_str)

    def update_status_label(self, mode):
        self.lbl_status.setText(mode)
        self.btn_start.setText("Başlat")

    def on_timer_finished(self, finished_mode):
        self.lbl_status.setText(f"{finished_mode} Bitti!")
        self.btn_start.setText("Başlat")
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec(): 
            self.timer_logic.reload_settings()
            if not self.timer_logic.is_running:
                self.timer_logic.reset()

    def open_stats(self):
        stats_dialog = StatsWindow(self)
        stats_dialog.exec()