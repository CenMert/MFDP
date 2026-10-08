"""
DayPanel - Focus ekranında timer'ın altında duran, açılıp kapanan günlük özet.

Kapalıyken tek satır: "▸ Bugün · 4s 15dk   ◀ ▶"
Açıkken tag → blok listesi: "A   10:02 – 11:05   55dk". Bir bloğa tıklanınca
block_clicked sinyali yayılır.
"""

import datetime
from typing import Optional

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QScrollArea, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QFontMetrics

from mfdp_app.core.daily_report import (DaySummary, WorkBlock, build_day_summary,
                                        logical_day, format_day_label, format_duration)


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


class BlockRow(QFrame):
    """Tıklanabilir blok satırı."""

    clicked = Signal()

    def __init__(self, block: WorkBlock, parent=None):
        super().__init__(parent)
        self.setObjectName("DayBlockRow")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"{block.task_name}\nAyrıntılar için tıkla")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 3, 6, 3)
        layout.setSpacing(10)

        name = ElidedLabel(block.task_name)
        layout.addWidget(name, 1)

        time_range = QLabel(f"{block.start:%H:%M} – {block.end:%H:%M}")
        time_range.setObjectName("DayBlockTime")
        layout.addWidget(time_range)

        duration = QLabel(format_duration(block.active_seconds))
        duration.setObjectName("DayBlockDuration")
        duration.setMinimumWidth(58)
        duration.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(duration)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class _BodyScroll(QScrollArea):
    """İstenen yüksekliği (maximumHeight) sizeHint olarak bildiren kaydırma alanı."""

    def sizeHint(self):
        hint = super().sizeHint()
        hint.setHeight(self.maximumHeight())
        return hint


class DayPanel(QFrame):
    """Timer altındaki açılır günlük özet paneli."""

    block_clicked = Signal(object, str)  # WorkBlock, tag rengi
    expanded_changed = Signal(bool)

    MAX_VISIBLE_BLOCKS = 3  # Bundan fazla blok varsa liste kaydırılır

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DayPanel")
        # Pencere büyüyünce içerikten fazla uzamasın, gerektiğinde daralabilsin
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._expanded = False
        self._day: Optional[datetime.date] = None  # None = bugünü takip et
        self._summary: Optional[DaySummary] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 2, 6, 4)
        root.setSpacing(0)

        # Başlık satırı
        header = QHBoxLayout()
        header.setSpacing(0)
        self.btn_header = QPushButton()
        self.btn_header.setObjectName("DayPanelHeader")
        self.btn_header.setCursor(Qt.PointingHandCursor)
        self.btn_header.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.btn_header.clicked.connect(self.toggle_expanded)
        header.addWidget(self.btn_header, 1)

        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        for btn, delta, tip in ((self.btn_prev, -1, "Önceki gün"), (self.btn_next, 1, "Sonraki gün")):
            btn.setObjectName("DayNavButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tip)
            btn.clicked.connect(lambda checked=False, d=delta: self.shift_day(d))
            header.addWidget(btn)
        root.addLayout(header)

        # Gövde (kaydırılabilir liste)
        self.scroll = _BodyScroll()
        self.scroll.setObjectName("DayPanelScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.body = QWidget()
        self.body.setObjectName("DayPanelBody")
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 2, 0, 2)
        self.body_layout.setSpacing(1)
        self.scroll.setWidget(self.body)
        self.scroll.setVisible(False)
        root.addWidget(self.scroll)

        self.refresh()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def current_day(self) -> datetime.date:
        return self._day or logical_day(datetime.datetime.now())

    def shift_day(self, delta: int):
        today = logical_day(datetime.datetime.now())
        new_day = min(self.current_day() + datetime.timedelta(days=delta), today)
        self._day = None if new_day == today else new_day
        if not self._expanded:
            self.toggle_expanded()
        else:
            self.refresh()

    def toggle_expanded(self):
        self._expanded = not self._expanded
        self.scroll.setVisible(self._expanded)
        self.refresh()
        self.expanded_changed.emit(self._expanded)

    def refresh(self, *_):
        """Veriyi yeniden oku ve paneli çiz (session_saved_signal'a bağlanabilir)."""
        day = self.current_day()
        today = logical_day(datetime.datetime.now())
        self._summary = build_day_summary(day)

        arrow = "▾" if self._expanded else "▸"
        total = format_duration(self._summary.total_active) if self._summary.groups else "kayıt yok"
        self.btn_header.setText(f"{arrow}  {format_day_label(day, today)}  ·  {total}")
        self.btn_next.setEnabled(day < today)

        if self._expanded:
            self._rebuild_body()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _clear_body(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _rebuild_body(self):
        self._clear_body()

        if not self._summary.groups:
            empty = QLabel("Bu gün kayıt yok")
            empty.setObjectName("DayEmptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.body_layout.addWidget(empty)
        else:
            for group in self._summary.groups:
                self.body_layout.addWidget(self._tag_header(group.tag, group.color, group.total_active))
                for block in group.blocks:
                    row = BlockRow(block)
                    row.clicked.connect(lambda b=block, c=group.color: self.block_clicked.emit(b, c))
                    self.body_layout.addWidget(row)
        self.body_layout.addStretch()

        # İçerik kadar uza, ama en fazla MAX_VISIBLE_BLOCKS blok satırı kadar; fazlası kaydırılır.
        # Yeni eklenen satırlar henüz gösterilmediği için layout.sizeHint() 0 döner;
        # yükseklik satırlardan tek tek toplanır.
        rows = [self.body_layout.itemAt(i).widget() for i in range(self.body_layout.count())]
        rows = [w for w in rows if w]
        margins = self.body_layout.contentsMargins()
        height = margins.top() + margins.bottom()
        blocks_seen = 0
        for i, w in enumerate(rows):
            if blocks_seen >= self.MAX_VISIBLE_BLOCKS:
                break
            height += w.sizeHint().height() + (self.body_layout.spacing() if i else 0)
            if isinstance(w, BlockRow):
                blocks_seen += 1

        # Dar alanda bir satıra kadar küçülebilir, geniş alanda bu yüksekliği aşmaz
        first_row = rows[0].sizeHint().height() if rows else 0
        self.scroll.setMinimumHeight(min(height, first_row + margins.top() + margins.bottom()))
        self.scroll.setMaximumHeight(height)

    def _tag_header(self, tag: str, color: str, total_seconds: int) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 6, 6, 1)
        layout.setSpacing(6)

        stripe = QFrame()
        stripe.setFixedSize(4, 14)
        stripe.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        layout.addWidget(stripe)

        name = QLabel(tag.upper())
        name.setObjectName("DayTagLabel")
        name.setStyleSheet(f"color: {color};")
        layout.addWidget(name)
        layout.addStretch()

        total = QLabel(format_duration(total_seconds))
        total.setObjectName("DayTagLabel")
        layout.addWidget(total)
        return row
