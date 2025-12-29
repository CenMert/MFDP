# mfdp_app/core/notifier.py (İçeriği bununla güncelle)

import os
import datetime
from PySide6.QtCore import QUrl, QTimer, QObject
from PySide6.QtMultimedia import QSoundEffect

class Notifier(QObject):
    def __init__(self):
        super().__init__()
        
        self.base_path = os.path.join(os.getcwd(), 'mfdp_app', 'resources', 'sounds')
        
        self.alarm_sound = self._load_sound('alarm.wav') 
        self.chime_sound = self._load_sound('chime.wav')

        self.last_triggered_minute = -1
        
        # YENİ: Varsayılan olarak açık
        self.chime_enabled = True 

        self.chime_timer = QTimer()
        self.chime_timer.timeout.connect(self._check_hourly_chime)
        self.chime_timer.start(1000)

    def _load_sound(self, filename):
        full_path = os.path.join(self.base_path, filename)
        effect = QSoundEffect()
        if os.path.exists(full_path):
            effect.setSource(QUrl.fromLocalFile(full_path))
            effect.setVolume(1.0)
        return effect

    def set_chime_enabled(self, enabled):
        """Arayüzden gelen On/Off komutunu işler."""
        self.chime_enabled = enabled
        status = "AÇIK" if enabled else "KAPALI"
        print(f"Ayaklı Saat özelliği: {status}")

    def play_alarm(self):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🔔 ALARM ÇALIYOR!")
        if self.alarm_sound.source().isValid():
            self.alarm_sound.play()
        else:
            print('\a') 

    def play_chime(self):
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🕰️ GONG!")
        if self.chime_sound.source().isValid():
            self.chime_sound.play()
        else:
            print('\a')

    def _check_hourly_chime(self):
        # YENİ: Eğer özellik kapalıysa hiçbir şey yapma
        if not self.chime_enabled:
            return

        now = datetime.datetime.now()
        current_minute = now.minute

        if current_minute == 0 or current_minute == 30:
            if current_minute != self.last_triggered_minute:
                self.play_chime()
                self.last_triggered_minute = current_minute
        else:
            self.last_triggered_minute = current_minute