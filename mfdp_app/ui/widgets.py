"""
Ortak küçük widget'lar: sığmayan metni '…' ile kısaltan etiket ve buton.

Pencere çok daraldığında metin kırpılıp taşmak yerine kısaltılır; tam metin tooltip'te kalır.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QFontMetrics
from PySide6.QtWidgets import (QLabel, QPushButton, QSizePolicy, QStyle, QStyleOptionButton,
                               QStylePainter)


class ElidedLabel(QLabel):
    """Sığmadığında sonu '…' ile kırpılan etiket (genişliği ebeveyne göre daralır)."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(24)

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(self.rect(), Qt.AlignVCenter | Qt.AlignLeft, elided)


class ElidedButton(QPushButton):
    """
    Metni sığmayınca '…' ile kısalan buton. Doğal genişliği tam metne göre kalır (sizeHint),
    ama yerleşim onu istediği kadar daraltabilir; kısaltılmış metin yalnızca çizimde uygulanır.
    """

    MIN_WIDTH = 24

    def __init__(self, text: str = "", parent=None, shrinkable: bool = True):
        """shrinkable=False: doğal genişliğini korur (ör. kısa etiket chip'i); yalnızca komşusu kısalır."""
        super().__init__(text, parent)
        if shrinkable:
            self.setMinimumWidth(self.MIN_WIDTH)
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        else:
            # Açık minimum genişlik verilirse Fixed politikasını ezip düğmeyi küçültür; verme
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def setText(self, text):
        super().setText(text)
        self.setToolTip(text if text else "")

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        # Stil içeriği (padding) kadar pay bırakıp metni kısalt
        content = self.style().subElementRect(QStyle.SE_PushButtonContents, option, self)
        option.text = QFontMetrics(self.font()).elidedText(
            self.text(), Qt.ElideRight, max(0, content.width()))
        painter.drawControl(QStyle.CE_PushButton, option)
