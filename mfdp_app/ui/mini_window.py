from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSettings, QPoint
from PySide6.QtGui import QGuiApplication


class MiniWindow(QWidget):
    """Köşeye sabitlenebilen minimal pencere: yalnızca görev rengi + süre."""

    restore_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setToolTip("Sürükle: taşı • Çift tıkla: ana pencere")
        self.setCursor(Qt.SizeAllCursor)
        self._drag_offset = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        self.dot = QLabel()
        self.dot.setFixedSize(14, 14)
        layout.addWidget(self.dot)

        self.lbl_time = QLabel("00:00")
        self.lbl_time.setStyleSheet(
            "color: #cdd6f4; font-size: 26px; font-weight: bold; background: transparent;")
        layout.addWidget(self.lbl_time)

        self.setStyleSheet(
            "MiniWindow { background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 10px; }")
        self.set_color(None)

    def set_time(self, text):
        self.lbl_time.setText(text)

    def set_color(self, color):
        """Görev rengi; None ise nötr gri."""
        c = color or "#585b70"
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        if self._drag_offset is not None:
            self._drag_offset = None
            QSettings("MFDP", "MFDP").setValue("mini_window/pos", self.pos())

    def mouseDoubleClickEvent(self, event):
        self.restore_requested.emit()
