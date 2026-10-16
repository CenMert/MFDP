"""
StreakGrid - GitHub tarzı katkı ızgarası (sütun = hafta, satır = gün).
Hücre rengi o günün çalışma dakikasına göre 0-4 seviye; üzerine gelince ipucu.
"""

import datetime
from typing import Optional

from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QFont

from mfdp_app.core.streak import StreakData
from mfdp_app.core.daily_report import format_duration

LEVEL_COLORS = ["#35302a", "#4f5240", "#646850", "#797d62", "#9b9b7a"]
_TR_MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
_TR_DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


class StreakGrid(QWidget):
    CELL = 12
    GAP = 3
    LEFT = 26   # gün etiketleri
    TOP = 16    # ay etiketleri

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: Optional[StreakData] = None
        self.setMouseTracking(True)

    def set_data(self, data: StreakData):
        self._data = data
        self.updateGeometry()
        self.update()

    def _weeks(self) -> int:
        if not self._data:
            return 0
        return (self._data.today - self._data.start).days // 7 + 1

    def sizeHint(self):
        step = self.CELL + self.GAP
        return QSize(self.LEFT + self._weeks() * step, self.TOP + 7 * step)

    def minimumSizeHint(self):
        return self.sizeHint()

    def _cell_rect(self, day: datetime.date) -> QRect:
        offset = (day - self._data.start).days
        step = self.CELL + self.GAP
        return QRect(self.LEFT + (offset // 7) * step, self.TOP + (offset % 7) * step, self.CELL, self.CELL)

    def paintEvent(self, event):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        font = QFont(self.font())
        font.setPointSize(7)
        p.setFont(font)

        p.setPen(QColor("#8f8273"))
        step = self.CELL + self.GAP
        for row in (0, 2, 4):
            p.drawText(QRect(0, self.TOP + row * step - 1, self.LEFT - 4, self.CELL + 2),
                       Qt.AlignRight | Qt.AlignVCenter, _TR_DAYS[row])

        last_month = None
        for day in self._data.days():
            if day.weekday() == 0 and day.month != last_month:
                x = self._cell_rect(day).x()
                p.drawText(QRect(x, 0, 40, self.TOP - 2), Qt.AlignLeft | Qt.AlignBottom,
                           _TR_MONTHS[day.month - 1])
                last_month = day.month

        p.setPen(Qt.NoPen)
        for day in self._data.days():
            p.setBrush(QColor(LEVEL_COLORS[self._data.levels.get(day, 0)]))
            p.drawRoundedRect(self._cell_rect(day), 2, 2)
        today_rect = self._cell_rect(self._data.today).adjusted(-1, -1, 1, 1)
        p.setBrush(Qt.NoBrush)
        p.setPen(QColor("#ffcb69"))
        p.drawRoundedRect(today_rect, 3, 3)

    def mouseMoveEvent(self, event):
        if not self._data:
            return
        pos = event.position().toPoint()
        for day in self._data.days():
            if self._cell_rect(day).adjusted(-1, -1, 1, 1).contains(pos):
                mins = self._data.minutes.get(day, 0)
                text = format_duration(mins * 60) if mins else "çalışma yok"
                label = f"{day.day} {_TR_MONTHS[day.month - 1]} {_TR_DAYS[day.weekday()]} · {text}"
                QToolTip.showText(event.globalPosition().toPoint(), label, self)
                return
        QToolTip.hideText()
