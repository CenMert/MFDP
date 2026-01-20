import sys
import os
from mfdp_app.ui.styles import MODERN_DARK_THEME
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qInstallMessageHandler
from mfdp_app.ui.main_window import MainWindow
# Database initialization
from mfdp_app.db.database_initializer import DatabaseInitializer
from mfdp_app.db.base_repository import BaseRepository

def message_handler(msg_type, context, message):
    """FFmpeg ve VDPAU uyarılarını bastırır"""
    msg_lower = message.lower()
    if any(keyword in msg_lower for keyword in ['ffmpeg', 'vdpau', 'libvdpau']):
        return  # Bu mesajları görmezden gel

def main():
    # Qt Multimedia uyarılarını bastır
    os.environ.setdefault('QT_LOGGING_RULES', 'qt.multimedia.*=false')
    qInstallMessageHandler(message_handler)
    
    # 1. Initialize database with connection pooling
    BaseRepository.initialize_pool(pool_size=5)
    DatabaseInitializer.setup_database()
    
    # 2. Start application
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_DARK_THEME)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()