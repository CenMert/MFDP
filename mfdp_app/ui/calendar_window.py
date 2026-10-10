import calendar
import datetime

from PySide6.QtCore import Qt, Signal, QRect, QDate, QTime
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                               QWidget, QLineEdit, QComboBox, QDateEdit, QTimeEdit,
                               QCheckBox, QGroupBox, QMessageBox)

from mfdp_app.db.calendar_repository import CalendarRepository

# Catppuccin Mocha
BASE, SURFACE, OVERLAY, TEXT, SUBTEXT = "#1e1e2e", "#313244", "#45475a", "#cdd6f4", "#a6adc8"

EVENT_KINDS = {
    "sinav": ("Sınav", "#f38ba8"),
    "odev": ("Ödev", "#f9e2af"),
    "toplanti": ("Toplantı", "#89b4fa"),
    "diger": ("Diğer", "#cba6f7"),
}
RANGE_COLORS = {
    "Yeşil": "#a6e3a1",
    "Turuncu": "#fab387",
    "Turkuaz": "#94e2d5",
    "Pembe": "#f5c2e7",
    "Mavi": "#89b4fa",
}
WEEKDAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
          "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

HEADER_H = 24
DAY_NUM_H = 18
LANE_H = 15
MAX_LANES = 3
COL_GAP = 2   # yan yana günler arası
ROW_GAP = 5   # hafta satırları arası
EVENT_H = 14


def _iso(d):
    return d.isoformat()


def _parse(s):
    return datetime.date.fromisoformat(s)


class MonthGrid(QWidget):
    """Draws one month: events as colored lines, ranges as labelled strips."""
    day_clicked = Signal(object)  # datetime.date

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 420)
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.events = {}   # iso date -> [event dict]
        self.ranges = []   # [(range dict, lane)]
        self._grid_start = None
        self._rows = 5

    def set_data(self, year, month, events, ranges):
        self.year, self.month = year, month
        first = datetime.date(year, month, 1)
        offset = first.weekday()
        days = calendar.monthrange(year, month)[1]
        self._rows = -(-(offset + days) // 7)
        self._grid_start = first - datetime.timedelta(days=offset)

        self.events = {}
        for ev in events:
            self.events.setdefault(ev["date"], []).append(ev)

        # Lane assignment: first lane whose last range ended before this one starts
        lane_ends = []
        self.ranges = []
        for r in sorted(ranges, key=lambda r: (r["start_date"], r["id"])):
            for i, end in enumerate(lane_ends):
                if end < r["start_date"]:
                    lane_ends[i] = r["end_date"]
                    lane = i
                    break
            else:
                lane_ends.append(r["end_date"])
                lane = len(lane_ends) - 1
            self.ranges.append((r, lane))
        self.update()

    def _lane_count(self):
        return min(MAX_LANES, max((l for _, l in self.ranges), default=-1) + 1)

    def _cell_size(self):
        cw = (self.width() - 6 * COL_GAP) / 7
        ch = (self.height() - HEADER_H - (self._rows - 1) * ROW_GAP) / self._rows
        return cw, ch

    def _cell_rect(self, index):
        cw, ch = self._cell_size()
        row, col = divmod(index, 7)
        return QRect(round(col * (cw + COL_GAP)), round(HEADER_H + row * (ch + ROW_GAP)),
                     round(cw), round(ch))

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton or self._grid_start is None:
            return
        pos = e.position().toPoint()
        for i in range(self._rows * 7):
            if self._cell_rect(i).contains(pos):
                self.day_clicked.emit(self._grid_start + datetime.timedelta(days=i))
                return

    def paintEvent(self, _):
        if self._grid_start is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(BASE))
        small = QFont(self.font())
        small.setPointSize(max(7, self.font().pointSize() - 2))
        today = datetime.date.today()
        lanes = self._lane_count()

        # Weekday header
        p.setPen(QColor(SUBTEXT))
        for c, name in enumerate(WEEKDAYS):
            p.drawText(QRect(self._cell_rect(c).left(), 0, self._cell_rect(c).width(), HEADER_H),
                       Qt.AlignCenter, name)

        # Cells, day numbers, events
        for i in range(self._rows * 7):
            d = self._grid_start + datetime.timedelta(days=i)
            rect = self._cell_rect(i)
            in_month = d.month == self.month
            p.setPen(QPen(QColor(OVERLAY), 1))
            p.setBrush(QColor(SURFACE) if in_month else QColor(BASE))
            p.drawRect(rect.adjusted(0, 0, -1, -1))

            p.setFont(self.font())
            if d == today:
                p.setPen(Qt.NoPen)
                p.setBrush(QColor("#a6e3a1"))
                p.drawEllipse(rect.left() + 4, rect.top() + 2, 16, 16)
                p.setPen(QColor(BASE))
            else:
                p.setPen(QColor(TEXT if in_month else OVERLAY))
            p.drawText(QRect(rect.left() + 4, rect.top() + 2, 16, 16), Qt.AlignCenter, str(d.day))

            p.setFont(small)
            evs = self.events.get(_iso(d), [])
            y = rect.top() + DAY_NUM_H + lanes * LANE_H + 2
            fit = max(0, (rect.bottom() - y) // EVENT_H)
            shown = evs if len(evs) <= fit else evs[:max(0, fit - 1)]
            for ev in shown:
                color = QColor(EVENT_KINDS.get(ev["kind"], EVENT_KINDS["diger"])[1])
                p.setPen(Qt.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(rect.left() + 4, y + 3, 6, 6, 3, 3)
                p.setPen(QColor(TEXT if in_month else SUBTEXT))
                text = p.fontMetrics().elidedText(ev["title"], Qt.ElideRight, rect.width() - 16)
                p.drawText(QRect(rect.left() + 13, y, rect.width() - 15, EVENT_H),
                           Qt.AlignVCenter | Qt.AlignLeft, text)
                y += EVENT_H
            if len(shown) < len(evs):
                p.setPen(QColor(SUBTEXT))
                p.drawText(QRect(rect.left() + 4, y, rect.width() - 8, EVENT_H),
                           Qt.AlignVCenter | Qt.AlignLeft, f"+{len(evs) - len(shown)} daha")

        # Range strips, one segment per week row
        for r, lane in self.ranges:
            if lane >= MAX_LANES:
                continue
            rs, re_ = _parse(r["start_date"]), _parse(r["end_date"])
            color = QColor(r["color"] or "#a6e3a1")
            for row in range(self._rows):
                row_start = self._grid_start + datetime.timedelta(days=row * 7)
                row_end = row_start + datetime.timedelta(days=6)
                if re_ < row_start or rs > row_end:
                    continue
                c0 = (max(rs, row_start) - row_start).days
                c1 = (min(re_, row_end) - row_start).days
                left = self._cell_rect(row * 7 + c0)
                right = self._cell_rect(row * 7 + c1)
                seg = QRect(left.left() + 2, left.top() + DAY_NUM_H + lane * LANE_H,
                            right.right() - left.left() - 3, LANE_H - 2)
                p.setPen(Qt.NoPen)
                p.setBrush(color)
                p.drawRoundedRect(seg, 3, 3)
                if c0 == 0 or rs >= row_start:  # label where the strip begins in this row
                    p.setFont(small)
                    p.setPen(QColor(BASE))
                    p.drawText(seg.adjusted(4, 0, -2, 0), Qt.AlignVCenter | Qt.AlignLeft,
                               p.fontMetrics().elidedText(r["label"], Qt.ElideRight, seg.width() - 6))
        p.end()


class DayDialog(QDialog):
    """List, add and delete events/ranges for one day."""

    def __init__(self, day, parent=None):
        super().__init__(parent)
        self.day = day
        self.setWindowTitle(f"{day.day} {MONTHS[day.month - 1]} {day.year}")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumWidth(380)
        self.changed = False
        self.layout_ = QVBoxLayout(self)

        self.list_box = QVBoxLayout()
        self.layout_.addLayout(self.list_box)
        self._build_add_event()
        self._build_add_range()
        self._refresh_list()

    def _clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear(item.layout())

    def _refresh_list(self):
        self._clear(self.list_box)
        iso = _iso(self.day)
        events = CalendarRepository.get_events_between(iso, iso)
        ranges = CalendarRepository.get_ranges_overlapping(iso, iso)
        if not events and not ranges:
            self.list_box.addWidget(QLabel("Bu gün için kayıt yok."))
        for ev in events:
            kind_name, color = EVENT_KINDS.get(ev["kind"], EVENT_KINDS["diger"])
            time = f"{ev['time']} " if ev["time"] else ""
            self._row(f"<span style='color:{color}'>●</span> {time}{ev['title']} <i>({kind_name})</i>",
                      lambda _=False, i=ev["id"]: self._delete(CalendarRepository.delete_event, i))
        for r in ranges:
            self._row(f"<span style='color:{r['color']}'>▬</span> {r['label']} "
                      f"<i>({r['start_date']} → {r['end_date']})</i>",
                      lambda _=False, i=r["id"]: self._delete(CalendarRepository.delete_range, i))

    def _row(self, html, on_delete):
        row = QHBoxLayout()
        label = QLabel(html)
        label.setWordWrap(True)
        btn = QPushButton("Sil")
        btn.setFixedWidth(50)
        btn.clicked.connect(on_delete)
        row.addWidget(label, 1)
        row.addWidget(btn)
        self.list_box.addLayout(row)

    def _delete(self, fn, item_id):
        fn(item_id)
        self.changed = True
        self._refresh_list()

    def _build_add_event(self):
        box = QGroupBox("Olay ekle")
        lay = QVBoxLayout(box)
        self.ev_title = QLineEdit()
        self.ev_title.setPlaceholderText("Başlık (örn. Fizik kısa sınav)")
        self.ev_kind = QComboBox()
        for key, (name, _) in EVENT_KINDS.items():
            self.ev_kind.addItem(name, key)
        self.ev_use_time = QCheckBox("Saat")
        self.ev_time = QTimeEdit(QTime(9, 0))
        self.ev_time.setEnabled(False)
        self.ev_use_time.toggled.connect(self.ev_time.setEnabled)
        add = QPushButton("Ekle")
        add.clicked.connect(self._add_event)
        row = QHBoxLayout()
        for w in (self.ev_kind, self.ev_use_time, self.ev_time, add):
            row.addWidget(w)
        lay.addWidget(self.ev_title)
        lay.addLayout(row)
        self.layout_.addWidget(box)

    def _build_add_range(self):
        box = QGroupBox("Tarih aralığı işaretle")
        lay = QVBoxLayout(box)
        self.rg_label = QLineEdit()
        self.rg_label.setPlaceholderText("Etiket (örn. Sınav haftası)")
        qd = QDate(self.day.year, self.day.month, self.day.day)
        self.rg_start, self.rg_end = QDateEdit(qd), QDateEdit(qd)
        for w in (self.rg_start, self.rg_end):
            w.setCalendarPopup(True)
        self.rg_color = QComboBox()
        for name, hex_ in RANGE_COLORS.items():
            self.rg_color.addItem(name, hex_)
        add = QPushButton("Ekle")
        add.clicked.connect(self._add_range)
        row = QHBoxLayout()
        for w in (self.rg_start, QLabel("→"), self.rg_end, self.rg_color, add):
            row.addWidget(w)
        lay.addWidget(self.rg_label)
        lay.addLayout(row)
        self.layout_.addWidget(box)

    def _add_event(self):
        title = self.ev_title.text().strip()
        if not title:
            return
        time = self.ev_time.time().toString("HH:mm") if self.ev_use_time.isChecked() else None
        CalendarRepository.add_event(title, _iso(self.day), self.ev_kind.currentData(), time)
        self.ev_title.clear()
        self.changed = True
        self._refresh_list()

    def _add_range(self):
        label = self.rg_label.text().strip()
        start, end = self.rg_start.date().toPython(), self.rg_end.date().toPython()
        if not label:
            return
        if end < start:
            QMessageBox.warning(self, "Geçersiz aralık", "Bitiş tarihi başlangıçtan önce olamaz.")
            return
        CalendarRepository.add_range(label, _iso(start), _iso(end), self.rg_color.currentData())
        self.rg_label.clear()
        self.changed = True
        self._refresh_list()


class CalendarWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Takvim - MFDP")
        self.resize(800, 600)
        self.setModal(False)
        # Free the grid and its data when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        today = datetime.date.today()
        self.year, self.month = today.year, today.month

        layout = QVBoxLayout(self)
        nav = QHBoxLayout()
        self.btn_prev, self.btn_next = QPushButton("◀"), QPushButton("▶")
        self.btn_today = QPushButton("Bugün")
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        f = self.title.font()
        f.setPointSize(f.pointSize() + 4)
        f.setBold(True)
        self.title.setFont(f)
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.title, 1)
        nav.addWidget(self.btn_today)
        nav.addWidget(self.btn_next)
        layout.addLayout(nav)

        self.grid = MonthGrid()
        layout.addWidget(self.grid, 1)

        legend = QHBoxLayout()
        for name, color in EVENT_KINDS.values():
            legend.addWidget(QLabel(f"<span style='color:{color}'>●</span> {name}"))
        legend.addStretch()
        layout.addLayout(legend)

        self.btn_prev.clicked.connect(lambda: self._shift(-1))
        self.btn_next.clicked.connect(lambda: self._shift(1))
        self.btn_today.clicked.connect(self._go_today)
        self.grid.day_clicked.connect(self._open_day)
        self._reload()

    def _shift(self, delta):
        m = self.month - 1 + delta
        self.year += m // 12
        self.month = m % 12 + 1
        self._reload()

    def _go_today(self):
        t = datetime.date.today()
        self.year, self.month = t.year, t.month
        self._reload()

    def _reload(self):
        self.title.setText(f"{MONTHS[self.month - 1]} {self.year}")
        first = datetime.date(self.year, self.month, 1)
        grid_start = first - datetime.timedelta(days=first.weekday())
        grid_end = grid_start + datetime.timedelta(days=41)
        self.grid.set_data(
            self.year, self.month,
            CalendarRepository.get_events_between(_iso(grid_start), _iso(grid_end)),
            CalendarRepository.get_ranges_overlapping(_iso(grid_start), _iso(grid_end)),
        )

    def _open_day(self, day):
        dlg = DayDialog(day, self)
        dlg.finished.connect(lambda _: self._reload())
        dlg.open()
