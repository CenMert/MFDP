from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSettings, QPoint, QTimer
from PySide6.QtGui import QGuiApplication


class MiniWindow(QWidget):
    """Köşeye sabitlenebilen minimal pencere: yalnızca görev rengi + süre."""

    restore_requested = Signal()
    toggle_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setToolTip("Tek tık: duraklat/devam • Çift tık: kapat • Sürükle: taşı")
        self.setCursor(Qt.SizeAllCursor)
        self._drag_offset = None
        self._moved = False
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self.toggle_requested.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        self.dot = QLabel()
        self.dot.setFixedSize(14, 14)
        layout.addWidget(self.dot)

        self.lbl_time = QLabel("00:00")
        self.lbl_time.setStyleSheet(
            "color: #f1dca7; font-size: 26px; font-weight: bold; background: transparent;")
        layout.addWidget(self.lbl_time)

        self.setStyleSheet(
            "MiniWindow { background-color: #24201b; border: 1px solid #4a4238; border-radius: 10px; }")
        self.set_color(None)

    def set_time(self, text):
        self.lbl_time.setText(text)

    def set_color(self, color):
        """Görev rengi; None ise nötr gri."""
        c = color or "#5e5448"
        self.dot.setStyleSheet(f"background-color: {c}; border-radius: 7px;")

    def showEvent(self, event):
        super().showEvent(event)
        self.adjustSize()
        pos = QSettings("MFDP", "MFDP").value("mini_window/pos")
        if isinstance(pos, QPoint) and self._on_screen(pos):
            self.move(pos)
        else:
            geo = QGuiApplication.primaryScreen().availableGeometry()
            self.move(geo.right() - self.width() - 16, geo.bottom() - self.height() - 16)

    def _on_screen(self, pos):
        return any(s.availableGeometry().contains(pos) for s in QGuiApplication.screens())

    def set_paused(self, paused):
        """Duraklatılmışsa süreyi soluk göster."""
        color = "#7a6e60" if paused else "#f1dca7"
        self.lbl_time.setStyleSheet(
            f"color: {color}; font-size: 26px; font-weight: bold; background: transparent;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._moved = False

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self._moved = True
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        if self._drag_offset is None:
            return
        self._drag_offset = None
        if self._moved:
            QSettings("MFDP", "MFDP").setValue("mini_window/pos", self.pos())
        else:
            # Çift tıklamayla karışmaması için tek tıkı biraz beklet
            self._click_timer.start(QGuiApplication.styleHints().mouseDoubleClickInterval())

    def mouseDoubleClickEvent(self, event):
        self._click_timer.stop()
        self.restore_requested.emit()
