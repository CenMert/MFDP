"""
FlowLayout - öğeleri soldan sağa dizen, sığmayanı alt satıra saran yerleşim.

Pencere daraldıkça butonların üst üste binmesi yerine satırlara dağılmasını sağlar.
`hasHeightForWidth` doğru olduğu için bir QVBoxLayout içinde yüksekliği genişliğe göre büyür.
Minimum boyut yalnızca en geniş öğedir (hepsinin toplamı değil), bu yüzden dar pencereyi zorlamaz.
"""

from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtWidgets import QLayout


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin: int = 0, hspacing: int = 6, vspacing: int = 6):
        super().__init__(parent)
        self._items = []
        self._hspacing = hspacing
        self._vspacing = vspacing
        self.setContentsMargins(margin, margin, margin, margin)

    # --- QLayout arayüzü -------------------------------------------------
    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            if not item.isEmpty():
                size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    # --- Yerleşim ---------------------------------------------------------
    def _do_layout(self, rect, test_only):
        m = self.contentsMargins()
        area = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y, line_height = area.x(), area.y(), 0
        for item in self._items:
            if item.isEmpty():
                continue
            hint = item.sizeHint()
            width = min(hint.width(), max(area.width(), 1))   # tek başına satırdan geniş olamaz
            if x + width > area.right() + 1 and line_height > 0:
                x = area.x()
                y += line_height + self._vspacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), QSize(width, hint.height())))
            x += width + self._hspacing
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y() + m.bottom()
