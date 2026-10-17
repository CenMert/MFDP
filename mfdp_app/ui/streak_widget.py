"""
StreakGrid - GitHub tarzı katkı ızgarası (sütun = hafta, satır = gün).
Hücre rengi o günün çalışma dakikasına göre 0-4 seviye; üzerine gelince ipucu.

Izgara kendi genişliğine uyar: hücre boyutu 6-14 px arasında hesaplanır; 18 hafta bu aralığa
sığmayacak kadar darsa yalnızca son N hafta çizilir. Böylece dar yan panelde taşmaz.
"""

import datetime
from typing import Optional, Tuple

from PySide6.QtWidgets import QWidget, QToolTip, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QFont

from mfdp_app.core.streak import StreakData
from mfdp_app.core.daily_report import format_duration

LEVEL_COLORS = ["#35302a", "#4f5240", "#646850", "#797d62", "#9b9b7a"]
_TR_MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
_TR_DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


class StreakGrid(QWidget):
    GAP = 3
    LEFT = 26      # gün etiketleri
    TOP = 16       # ay etiketleri
    MIN_CELL = 6
    MAX_CELL = 14
    PREFERRED_CELL = 12
    MIN_WEEKS = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: Optional[StreakData] = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_data(self, data: StreakData):
        self._data = data
        self.updateGeometry()
        self.update()

    # ---- boyutlar -------------------------------------------------------
    def _total_weeks(self) -> int:
        if not self._data:
            return 0
        return (self._data.today - self._data.start).days // 7 + 1

    def _fit(self, width: int) -> Tuple[int, int]:
        """(hücre px, çizilecek hafta sayısı) — verilen genişliğe sığacak en iyi düzen."""
        total = max(self._total_weeks(), 1)
        avail = max(width - self.LEFT, 1)
        cell = avail // total - self.GAP
        if cell >= self.MIN_CELL:
            return min(cell, self.MAX_CELL), total
        weeks = max(self.MIN_WEEKS, avail // (self.MIN_CELL + self.GAP))
        return self.MIN_CELL, min(weeks, total)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        cell, _ = self._fit(width)
        return self.TOP + 7 * (cell + self.GAP)

    def sizeHint(self):
        width = self.LEFT + self._total_weeks() * (self.PREFERRED_CELL + self.GAP)
        return QSize(width, self.heightForWidth(width))

    def minimumSizeHint(self):
        width = self.LEFT + self.MIN_WEEKS * (self.MIN_CELL + self.GAP)
        return QSize(width, self.heightForWidth(width))

    # ---- çizim ----------------------------------------------------------
    def _geometry(self):
        cell, weeks = self._fit(self.width())
        first_week = self._total_weeks() - weeks     # bu haftadan öncekiler çizilmez
        return cell, weeks, first_week

    def _cell_rect(self, day: datetime.date, cell: int, first_week: int) -> Optional[QRect]:
        offset = (day - self._data.start).days
        week = offset // 7 - first_week
        if week < 0:
            return None
        step = cell + self.GAP
        return QRect(self.LEFT + week * step, self.TOP + (offset % 7) * step, cell, cell)

    def paintEvent(self, event):
        if not self._data:
            return
        cell, weeks, first_week = self._geometry()
        step = cell + self.GAP
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        font = QFont(self.font())
        font.setPointSize(7)
        p.setFont(font)

        p.setPen(QColor("#8f8273"))
        for row in (0, 2, 4):
            p.drawText(QRect(0, self.TOP + row * step - 1, self.LEFT - 4, cell + 2),
                       Qt.AlignRight | Qt.AlignVCenter, _TR_DAYS[row])

        last_month = None
        for day in self._data.days():
            rect = self._cell_rect(day, cell, first_week)
            if rect is None:
                continue
            if day.weekday() == 0 and day.month != last_month:
                p.drawText(QRect(rect.x(), 0, 40, self.TOP - 2), Qt.AlignLeft | Qt.AlignBottom,
                           _TR_MONTHS[day.month - 1])
                last_month = day.month

        p.setPen(Qt.NoPen)
        for day in self._data.days():
            rect = self._cell_rect(day, cell, first_week)
            if rect is None:
                continue
            p.setBrush(QColor(LEVEL_COLORS[self._data.levels.get(day, 0)]))
            p.drawRoundedRect(rect, 2, 2)
        today_rect = self._cell_rect(self._data.today, cell, first_week)
        if today_rect is not None:
            p.setBrush(Qt.NoBrush)
            p.setPen(QColor("#ffcb69"))
            p.drawRoundedRect(today_rect.adjusted(-1, -1, 1, 1), 3, 3)

    def mouseMoveEvent(self, event):
        if not self._data:
            return
        cell, _, first_week = self._geometry()
        pos = event.position().toPoint()
        for day in self._data.days():
            rect = self._cell_rect(day, cell, first_week)
            if rect is not None and rect.adjusted(-1, -1, 1, 1).contains(pos):
                mins = self._data.minutes.get(day, 0)
                text = format_duration(mins * 60) if mins else "çalışma yok"
                label = f"{day.day} {_TR_MONTHS[day.month - 1]} {_TR_DAYS[day.weekday()]} · {text}"
                QToolTip.showText(event.globalPosition().toPoint(), label, self)
                return
        QToolTip.hideText()
