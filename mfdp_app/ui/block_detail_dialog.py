"""
BlockDetailDialog - Gün panelindeki bir bloğun ayrıntılı raporu.

Net çalışma, verim (net / ayrılan süre), duraklama ve ara sayıları,
zaman çizelgesi şeridi ve bölünme analizi gösterir.
"""

from typing import List

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QWidget, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath

from mfdp_app.core.daily_report import (BlockReport, Segment, format_duration,
                                        format_duration_precise, format_day_label, logical_day)


_SEGMENT_COLORS = {
    "pause": QColor("#7f849c"),
    "gap": QColor("#45475a"),
}


class TimelineBar(QWidget):
    """Bloğun zaman şeridi: çalışma tag renginde, duraklama ve aralar gri."""

    def __init__(self, report: BlockReport, parent=None):
        super().__init__(parent)
        self.report = report
        self.setFixedHeight(22)
        self.setMinimumWidth(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())

        clip = QPainterPath()
        clip.addRoundedRect(rect, 6, 6)
        painter.setClipPath(clip)
        painter.fillRect(rect, QColor("#181825"))

        start = self.report.block.start
        total = max(1.0, (self.report.block.end - start).total_seconds())
        work = QColor(self.report.color)
        unknown = QColor(self.report.color)
        unknown.setAlpha(110)

        for seg in self.report.timeline:
            x0 = rect.width() * (seg.start - start).total_seconds() / total
            x1 = rect.width() * (seg.end - start).total_seconds() / total
            if seg.kind == "work":
                color = work
            elif seg.kind == "unknown":
                color = unknown
            else:
                color = _SEGMENT_COLORS[seg.kind]
            painter.fillRect(QRectF(x0, 0, max(1.0, x1 - x0), rect.height()), color)


class BlockDetailDialog(QDialog):
    def __init__(self, report: BlockReport, parent=None):
        super().__init__(parent)
        self.report = report
        block = report.block

        self.setWindowTitle(f"{block.task_name} - Ayrıntı")
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("QDialog { background-color: #1e1e2e; }")
        self.resize(540, 660)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        # Başlık
        tag_label = QLabel(block.tag.upper())
        tag_label.setStyleSheet(f"color: {report.color}; font-size: 12px; font-weight: bold;")
        root.addWidget(tag_label)

        title = QLabel(block.task_name)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        root.addWidget(title)

        day_text = format_day_label(logical_day(block.start))
        subtitle = QLabel(
            f"{day_text}  ·  {block.start:%H:%M} – {block.end:%H:%M}  ·  "
            f"{len(block.sessions)} oturum"
        )
        subtitle.setStyleSheet("color: #7f849c; font-size: 12px;")
        root.addWidget(subtitle)

        # Stat kartları
        cards = QHBoxLayout()
        cards.setSpacing(8)
        cards.addWidget(self._card("Net çalışma", format_duration(report.active_seconds),
                                   f"ayrılan {format_duration(report.wall_seconds)}", "#a6e3a1"))
        cards.addWidget(self._card("Verim", f"%{round(report.efficiency * 100)}",
                                   "net / ayrılan süre", self._efficiency_color(report.efficiency)))
        approx = "≈" if report.estimated_pause_count else ""
        cards.addWidget(self._card("Duraklama", f"{approx}{report.pause_count}",
                                   f"toplam {approx}{format_duration(report.pause_seconds)}", "#f9e2af"))
        cards.addWidget(self._card("Ara", str(len(report.gaps)),
                                   f"toplam {format_duration(report.gap_seconds)}", "#89b4fa"))
        root.addLayout(cards)

        # Zaman şeridi
        root.addWidget(self._section_title("Zaman çizelgesi"))
        root.addWidget(TimelineBar(report))
        axis = QHBoxLayout()
        for text, align in ((f"{block.start:%H:%M}", Qt.AlignLeft), (self._legend_text(), Qt.AlignCenter),
                            (f"{block.end:%H:%M}", Qt.AlignRight)):
            lbl = QLabel(text)
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet("color: #7f849c; font-size: 11px;")
            lbl.setAlignment(align)
            axis.addWidget(lbl, 1 if align == Qt.AlignCenter else 0)
        root.addLayout(axis)

        # Bölünme analizi
        root.addWidget(self._section_title("Bölünme analizi"))
        root.addLayout(self._analysis_grid())

        # Kesinti listesi
        root.addWidget(self._section_title("Duraklamalar ve aralar"))
        root.addWidget(self._interruption_list(), 1)

        if report.has_legacy:
            note = QLabel("⚠ Bazı oturumlar eski kayıt: duraklama sayısı ve süresi tahmini, "
                          "zaman çizelgesinde o kısım soluk gösteriliyor.")
            note.setWordWrap(True)
            note.setStyleSheet("color: #fab387; font-size: 11px;")
            root.addWidget(note)

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------

    @staticmethod
    def _efficiency_color(ratio: float) -> str:
        if ratio >= 0.85:
            return "#a6e3a1"
        if ratio >= 0.6:
            return "#f9e2af"
        return "#f38ba8"

    @staticmethod
    def _card(title: str, value: str, sub: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #313244; border-radius: 8px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        for text, style in ((title, "color: #a6adc8; font-size: 11px;"),
                            (value, f"color: {color}; font-size: 20px; font-weight: bold;"),
                            (sub, "color: #7f849c; font-size: 10px;")):
            lbl = QLabel(text)
            lbl.setStyleSheet(style + " background: transparent;")
            layout.addWidget(lbl)
        return card

    @staticmethod
    def _section_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #bac2de; font-size: 13px; font-weight: bold; margin-top: 4px;")
        return lbl

    def _legend_text(self) -> str:
        def dot(color: str, label: str) -> str:
            return f"<span style='color:{color};'>■</span> {label}"
        return "&nbsp;&nbsp;".join([dot(self.report.color, "çalışma"), dot("#7f849c", "duraklama"),
                                    dot("#45475a", "ara")])

    def _analysis_grid(self) -> QGridLayout:
        r = self.report
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)

        if r.longest_focus_seconds:
            longest = format_duration(r.longest_focus_seconds)
            average = format_duration(r.average_focus_seconds)
        else:
            longest = average = "—"

        phases = r.phase_counts
        if sum(phases.values()):
            phase_text = "  ·  ".join(f"{k} {v}" for k, v in phases.items())
        else:
            phase_text = "bölünme yok" if not r.has_legacy else "—"

        sessions_text = f"{r.completed_sessions} tamamlandı"
        if r.abandoned_sessions:
            reasons = ", ".join(f"{k} {v}" for k, v in r.abandon_reasons.items())
            sessions_text += f", {r.abandoned_sessions} yarıda ({reasons})"

        rows = [
            ("En uzun kesintisiz odak", longest),
            ("Ortalama odak dilimi", average),
            ("Bölünmelerin yeri (blok 1/3'leri)", phase_text),
            ("Oturumlar", sessions_text),
        ]
        if r.plan_ratio is not None:
            rows.append(("Pomodoro planına uyum", f"%{round(r.plan_ratio * 100)}  "
                                                 f"(plan {format_duration(r.planned_seconds)})"))

        for i, (key, value) in enumerate(rows):
            k = QLabel(key)
            k.setStyleSheet("color: #a6adc8; font-size: 12px;")
            v = QLabel(value)
            v.setWordWrap(True)
            v.setStyleSheet("font-size: 12px; font-weight: bold;")
            grid.addWidget(k, i, 0)
            grid.addWidget(v, i, 1)
        grid.setColumnStretch(1, 1)
        return grid

    def _interruption_list(self) -> QWidget:
        r = self.report
        items: List[tuple] = []
        for p in r.pauses:
            minute = f"{p.active_before_seconds // 60 + 1}. dk  ·  " if p.active_before_seconds is not None else ""
            items.append((p.start, "#f9e2af", "Duraklama",
                          f"{p.start:%H:%M}  ·  {minute}{format_duration_precise(p.seconds)}"))
        for g in r.gaps:
            items.append((g.start, "#89b4fa", "Ara",
                          f"{g.start:%H:%M} – {g.end:%H:%M}  ·  {format_duration_precise(g.seconds)}"))
        items.sort(key=lambda x: x[0])

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if not items:
            text = "Kayıtlı duraklama ayrıntısı yok" if r.estimated_pause_count else "Hiç bölünmeden çalıştın 🎯"
            empty = QLabel(text)
            empty.setStyleSheet("color: #7f849c; font-size: 12px;")
            layout.addWidget(empty)
        for _, color, kind, text in items:
            row = QHBoxLayout()
            badge = QLabel(kind)
            badge.setFixedWidth(78)
            badge.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            row.addWidget(badge)
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 12px;")
            row.addWidget(lbl, 1)
            layout.addLayout(row)
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        scroll.setMinimumHeight(min(len(items), 5) * 22 + 10)
        scroll.setWidget(container)
        return scroll
