from itertools import count

from PySide6.QtCore import QObject, Signal, Slot, SLOT
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

NOTIF_SERVICE = "org.freedesktop.Notifications"
NOTIF_PATH = "/org/freedesktop/Notifications"
NOTIF_IFACE = "org.freedesktop.Notifications"


class DNDManager(QObject):
    """
    Sistem genelinde 'Rahatsız Etme' (KDE Plasma / freedesktop Notifications).

    Ekstra izin gerekmez: Inhibit çağrısı kullanıcı oturum bus'ında yapılır.

    Neden ayrı bir D-Bus bağlantısı?
    - Plasma, inhibit'i çağıranın bus bağlantısına bağlar; bağlantı kapanınca
      inhibit'i kendisi kaldırır. (Eski 'busctl' yöntemi bu yüzden anında düşüyordu.)
    - PySide6 uint32 gönderemediği için UnInhibit(cookie) çağrılamıyor.
    Bu yüzden her DND oturumu için özel bir bağlantı açıyoruz; kapatmak için
    bağlantıyı koparmak yeterli. Uygulama çökerse de DND otomatik kalkar.
    """

    # Bizim DND durumumuz değişince (True = açık)
    dnd_changed_signal = Signal(bool)
    # Sistemdeki toplam DND durumu değişince (KDE panelinden yapılanlar dahil)
    system_dnd_changed_signal = Signal(bool)

    _conn_ids = count(1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._conn_name = None  # Aktif inhibit bağlantısının adı
        self.cookie = None

        bus = QDBusConnection.sessionBus()
        self._iface = QDBusInterface(NOTIF_SERVICE, NOTIF_PATH, NOTIF_IFACE, bus)
        self.is_available = bus.isConnected() and self._iface.isValid()

        if self.is_available:
            bus.connect(NOTIF_SERVICE, NOTIF_PATH, "org.freedesktop.DBus.Properties",
                        "PropertiesChanged", self, SLOT("_on_properties_changed(QDBusMessage)"))
        else:
            print("DND: Bildirim servisi bulunamadı, DND devre dışı.")

    @property
    def is_active(self) -> bool:
        return self._conn_name is not None

    @property
    def system_inhibited(self) -> bool:
        """Sistemde (herhangi bir kaynaktan) DND açık mı?"""
        if not self.is_available:
            return False
        return bool(self._iface.property("Inhibited"))

    def enable_dnd(self, reason: str = "Focus Mode"):
        """Bildirimleri sustur."""
        if not self.is_available or self.is_active:
            return

        name = f"mfdp_dnd_{next(self._conn_ids)}"
        conn = QDBusConnection.connectToBus(QDBusConnection.BusType.SessionBus, name)
        reply = QDBusInterface(NOTIF_SERVICE, NOTIF_PATH, NOTIF_IFACE, conn).call(
            "Inhibit", "MFDP", reason, {})

        if reply.type() != QDBusMessage.MessageType.ReplyMessage:
            print(f"DND Açma Hatası: {reply.errorMessage()}")
            QDBusConnection.disconnectFromBus(name)
            return

        self._conn_name = name
        self.cookie = reply.arguments()[0]
        print(f"DND Aktif. (Token: {self.cookie})")
        self.dnd_changed_signal.emit(True)

    def disable_dnd(self):
        """Bildirimleri serbest bırak."""
        if not self.is_active:
            return

        # Bağlantı kopunca Plasma inhibit'i kaldırır
        QDBusConnection.disconnectFromBus(self._conn_name)
        self._conn_name = None
        self.cookie = None
        print("DND Pasif. Bildirimler açık.")
        self.dnd_changed_signal.emit(False)

    def toggle_dnd(self) -> bool:
        """Manuel tuş için. Yeni durumu döndürür."""
        if self.is_active:
            self.disable_dnd()
        else:
            self.enable_dnd("Manual")
        return self.is_active

    @Slot(QDBusMessage)
    def _on_properties_changed(self, msg):
        args = msg.arguments()
        if len(args) < 2 or args[0] != NOTIF_IFACE:
            return
        changed = args[1]
        # PySide bazen a{sv}'yi dict'e çeviremiyor; o zaman direkt sor
        if isinstance(changed, dict):
            if "Inhibited" not in changed:
                return
            value = bool(changed["Inhibited"])
        else:
            value = self.system_inhibited
        self.system_dnd_changed_signal.emit(value)

        # Kullanıcı DND'yi KDE panelinden kapattıysa bizim inhibit'imiz de gitti
        if not value and self.is_active:
            self.disable_dnd()
