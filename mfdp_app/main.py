import sys
import os
from mfdp_app.ui.styles import MODERN_DARK_THEME
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qInstallMessageHandler
from mfdp_app.ui.main_window import MainWindow
# Veritabanı başlatmayı şimdilik yorum satırı yapabiliriz veya aktif tutabiliriz
from mfdp_app.db_manager import create_connection, setup_database

def message_handler(msg_type, context, message):
    """FFmpeg ve VDPAU uyarılarını bastırır"""
    msg_lower = message.lower()
    if any(keyword in msg_lower for keyword in ['ffmpeg', 'vdpau', 'libvdpau']):
        return  # Bu mesajları görmezden gel

def main():
    # Qt Multimedia uyarılarını bastır
    os.environ.setdefault('QT_LOGGING_RULES', 'qt.multimedia.*=false')
    qInstallMessageHandler(message_handler)
    # 1. Veritabanını hazırla
    conn = create_connection()
    if conn:
        setup_database(conn)
        conn.close()

    # 2. Uygulamayı başlat
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_DARK_THEME) # <--- Stili burada yüklüyoruz
    
    # İleride buraya stil dosyası (QSS) yükleyeceğiz
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()