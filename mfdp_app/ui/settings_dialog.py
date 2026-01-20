from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QSpinBox, 
                               QPushButton, QHBoxLayout, QFormLayout)
from PySide6.QtCore import Qt
from mfdp_app.db.settings_repository import SettingsRepository

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setFixedWidth(300)
        # Ana pencerenin stilini miras alsın diye parent verdik ama 
        # bazen dialoglara özel stil gerekebilir. Şimdilik sade kalsın.
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Form Düzeni
        form_layout = QFormLayout()
        
        # 1. Focus Süresi
        self.spin_focus = QSpinBox()
        self.spin_focus.setRange(1, 120) # 1 dk ile 120 dk arası
        self.spin_focus.setSuffix(" dk")
        form_layout.addRow("Focus Süresi:", self.spin_focus)

        # 2. Kısa Mola
        self.spin_short = QSpinBox()
        self.spin_short.setRange(1, 60)
        self.spin_short.setSuffix(" dk")
        form_layout.addRow("Kısa Mola:", self.spin_short)

        # 3. Uzun Mola
        self.spin_long = QSpinBox()
        self.spin_long.setRange(1, 90)
        self.spin_long.setSuffix(" dk")
        form_layout.addRow("Uzun Mola:", self.spin_long)

        self.layout.addLayout(form_layout)

        # Kaydet Butonu
        self.btn_save = QPushButton("Kaydet ve Kapat")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.save_values)
        self.btn_save.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 8px;")
        
        self.layout.addWidget(self.btn_save)

        # Mevcut değerleri yükle
        self.load_current_values()

    def load_current_values(self):
        settings = SettingsRepository.load_settings()
        # Veritabanında yoksa varsayılanları (25, 5, 15) kullan
        self.spin_focus.setValue(int(settings.get('focus_duration', 25)))
        self.spin_short.setValue(int(settings.get('short_break_duration', 5)))
        self.spin_long.setValue(int(settings.get('long_break_duration', 15)))

    def save_values(self):
        # Değerleri Veritabanına Yaz
        SettingsRepository.save_setting('focus_duration', self.spin_focus.value())
        SettingsRepository.save_setting('short_break_duration', self.spin_short.value())
        SettingsRepository.save_setting('long_break_duration', self.spin_long.value())
        
        self.accept() # Pencereyi kapat ve 'kabul edildi' sinyali ver