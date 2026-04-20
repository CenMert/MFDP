import sys
import os
import traceback
import faulthandler
import threading
from mfdp_app.ui.styles import MODERN_DARK_THEME
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import qInstallMessageHandler
from mfdp_app.ui.main_window import MainWindow
from mfdp_app.db.database_initializer import DatabaseInitializer
from mfdp_app.db.base_repository import BaseRepository

def message_handler(msg_type, context, message):
    """Suppress only FFmpeg/VDPAU spam, print everything else."""
    msg_lower = message.lower()
    if any(k in msg_lower for k in ['ffmpeg', 'vdpau', 'libvdpau']):
        return
    print(f"[Qt] {message}", file=sys.stderr, flush=True)

def dump_after_timeout(seconds=10):
    def _dump():
        print(f"[DEBUG] watchdog: dumping traceback after {seconds}s", flush=True)
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
    t = threading.Timer(seconds, _dump)
    t.daemon = True
    t.start()

def main():
    faulthandler.enable()
    dump_after_timeout(10)

    os.environ.setdefault("QT_LOGGING_RULES", "qt.multimedia.*=false")
    qInstallMessageHandler(message_handler)

    print("[DEBUG] starting app", flush=True)
    BaseRepository.initialize_pool(pool_size=5)
    DatabaseInitializer.setup_database()
    print("[DEBUG] db ready", flush=True)

    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_DARK_THEME)

    print("[DEBUG] creating MainWindow", flush=True)
    window = MainWindow()
    print("[DEBUG] showing MainWindow", flush=True)
    window.show()

    rc = app.exec()
    print(f"[DEBUG] app.exec() returned {rc}", flush=True)
    sys.exit(rc)

if __name__ == "__main__":
    main()