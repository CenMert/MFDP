from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QSpinBox,
                               QPushButton, QHBoxLayout, QFormLayout, QSlider)
from PySide6.QtCore import Qt
from mfdp_app.db.settings_repository import SettingsRepository

class SettingsDialog(QDialog):
    def __init__(self, parent=None, notifier=None):
        super().__init__(parent)
        self.notifier = notifier
        self.setWindowTitle("Ayarlar")
        self.setFixedWidth(340)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Form Düzeni
        form_layout = QFormLayout()

        # 1. Focus Süresi
        self.spin_focus = QSpinBox()
        self.spin_focus.setRange(1, 120)
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

        # Ses Seviyesi
        self.layout.addSpacing(8)
        volume_label = QLabel("Ses Seviyesi")
        volume_label.setStyleSheet("font-weight: bold; color: #cdd6f4;")
        self.layout.addWidget(volume_label)

        volume_row = QHBoxLayout()
        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setTickInterval(10)
        self.slider_volume.setCursor(Qt.PointingHandCursor)

        self.lbl_volume_pct = QLabel("100%")
        self.lbl_volume_pct.setFixedWidth(38)
        self.lbl_volume_pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_volume_pct.setStyleSheet("color: #cdd6f4;")

        volume_row.addWidget(self.slider_volume)
        volume_row.addWidget(self.lbl_volume_pct)
        self.layout.addLayout(volume_row)

        self.slider_volume.valueChanged.connect(self._on_volume_changed)

        # Kaydet Butonu
        self.layout.addSpacing(8)
        self.btn_save = QPushButton("Kaydet ve Kapat")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.save_values)
        self.btn_save.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 8px;")
        self.layout.addWidget(self.btn_save)

        # Mevcut değerleri yükle
        self.load_current_values()

        # Cancel için orijinal sesi hatırla
        self._original_volume = self.slider_volume.value()

    def _on_volume_changed(self, value: int):
        self.lbl_volume_pct.setText(f"{value}%")
        if self.notifier:
            self.notifier.set_volume(value / 100.0)

    def load_current_values(self):
        settings = SettingsRepository.load_settings()
        self.spin_focus.setValue(int(settings.get('focus_duration', 25)))
        self.spin_short.setValue(int(settings.get('short_break_duration', 5)))
        self.spin_long.setValue(int(settings.get('long_break_duration', 15)))
        volume = int(settings.get('sound_volume', 100))
        self.slider_volume.setValue(volume)
        self.lbl_volume_pct.setText(f"{volume}%")

    def save_values(self):
        SettingsRepository.save_setting('focus_duration', self.spin_focus.value())
        SettingsRepository.save_setting('short_break_duration', self.spin_short.value())
        SettingsRepository.save_setting('long_break_duration', self.spin_long.value())
        SettingsRepository.save_setting('sound_volume', self.slider_volume.value())
        self.accept()

    def reject(self):
        # Revert live preview if user cancels
        if self.notifier:
            self.notifier.set_volume(self._original_volume / 100.0)
        super().reject()