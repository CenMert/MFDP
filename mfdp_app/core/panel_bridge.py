import json
import os
import time
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot, ClassInfo

try:
    from PySide6.QtDBus import QDBusConnection
except ImportError:  # QtDBus yoksa köprü sadece dosya yazar
    QDBusConnection = None

DBUS_SERVICE = "org.mfdp.Timer"
DBUS_PATH = "/Timer"


@ClassInfo({"D-Bus Interface": "org.mfdp.Timer"})
class PanelBridge(QObject):
    """KDE panel widget'ı ile köprü.

    - Durumu `$XDG_RUNTIME_DIR/mfdp/state.json` dosyasına her saniye yazar.
    - `org.mfdp.Timer.Toggle()` D-Bus çağrısını `toggle_requested` sinyaline çevirir.
    """

    toggle_requested = Signal()

    def __init__(self, snapshot: Callable[[], dict], parent=None):
        super().__init__(parent)
        self._snapshot = snapshot
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/mfdp-{os.getuid()}"
        self._dir = os.path.join(runtime_dir, "mfdp")
        self._path = os.path.join(self._dir, "state.json")
        self._registered = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.publish)
        self._timer.start(1000)

        self._register_dbus()
        self.publish()

    def _register_dbus(self):
        if QDBusConnection is None:
            return
        bus = QDBusConnection.sessionBus()
        if not bus.isConnected():
            return
        if bus.registerService(DBUS_SERVICE) and bus.registerObject(
                DBUS_PATH, self, QDBusConnection.ExportAllSlots):
            self._registered = True

    @Slot()
    def Toggle(self):
        self.toggle_requested.emit()

    def publish(self):
        data = dict(self._snapshot())
        data["ts"] = time.time()
        try:
            os.makedirs(self._dir, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, self._path)
        except OSError:
            pass

    def shutdown(self):
        self._timer.stop()
        try:
            os.remove(self._path)
        except OSError:
            pass
        if self._registered:
            bus = QDBusConnection.sessionBus()
            bus.unregisterObject(DBUS_PATH)
            bus.unregisterService(DBUS_SERVICE)
            self._registered = False
