"""
Manual session entry - record work done away from the app.

Two modes in one dialog:
  * Simple:   task + date + start/end time.
  * Detailed: adds a duration slider (synced with start/end), completion
              flag and interruption count. Toggle back and forth freely.
"""

import datetime

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                               QComboBox, QDateEdit, QTimeEdit, QPushButton, QSlider,
                               QSpinBox, QCheckBox, QWidget, QMessageBox, QToolButton,
                               QFrame, QGridLayout)
from PySide6.QtCore import Qt, QDate, QTime

from mfdp_app.core.daily_report import DAY_START_HOUR, logical_day
from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.task_repository import TaskRepository

SLIDER_STEP_MIN = 5
SLIDER_MAX_MIN = 12 * 60
DAY_MIN = 24 * 60
DAY_START_MIN = DAY_START_HOUR * 60


def _offset(t: QTime, is_end: bool = False) -> int:
    """Minutes since the logical day start (DAY_START_HOUR). End at day start == end of day."""
    off = (t.hour() * 60 + t.minute() - DAY_START_MIN) % DAY_MIN
    return DAY_MIN if (is_end and off == 0) else off


def _time_from_offset(off: int) -> QTime:
    m = (DAY_START_MIN + off) % DAY_MIN
    return QTime(m // 60, m % 60)


class TimePickerPopup(QFrame):
    """Click-to-pick popup: hour grid (0-23) then minute grid (5-min steps)."""

    _BTN = ("QPushButton { background-color: #35302a; padding: 5px 0; min-width: 30px; }"
            "QPushButton:hover { background-color: #5e5448; }"
            "QPushButton:checked { background-color: #e8ac65; color: #24201b; font-weight: bold; }")

    def __init__(self, time_edit: QTimeEdit, parent=None):
        super().__init__(parent, Qt.Popup)
        self.time_edit = time_edit
        self.setStyleSheet("QFrame { background-color: #24201b; border: 1px solid #4a4238; }"
                           "QLabel { border: none; color: #b8a99a; }")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Saat"))
        self.hour_btns = self._grid(lay, range(24), 6, lambda v: f"{v:02d}", self._pick_hour)
        lay.addWidget(QLabel("Dakika"))
        self.min_btns = self._grid(lay, range(0, 60, 5), 6, lambda v: f"{v:02d}", self._pick_minute)

    def _grid(self, lay, values, cols, fmt, slot):
        grid = QGridLayout()
        grid.setSpacing(3)
        btns = {}
        for i, v in enumerate(values):
            b = QPushButton(fmt(v))
            b.setCheckable(True)
            b.setStyleSheet(self._BTN)
            b.clicked.connect(lambda _=False, v=v: slot(v))
            grid.addWidget(b, i // cols, i % cols)
            btns[v] = b
        lay.addLayout(grid)
        return btns

    def popup_at(self, widget):
        t = self.time_edit.time()
        for h, b in self.hour_btns.items():
            b.setChecked(h == t.hour())
        for m, b in self.min_btns.items():
            b.setChecked(m == t.minute())
        self.move(widget.mapToGlobal(widget.rect().bottomLeft()))
        self.show()

    def _pick_hour(self, h):
        t = self.time_edit.time()
        self.time_edit.setTime(QTime(h, t.minute()))
        for k, b in self.hour_btns.items():
            b.setChecked(k == h)

    def _pick_minute(self, m):
        t = self.time_edit.time()
        self.time_edit.setTime(QTime(t.hour(), m))
        self.close()


class ManualSessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oturum Ekle")
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog { background-color: #24201b; color: #f1dca7; }
            QLabel { color: #f1dca7; }
            QComboBox, QDateEdit, QTimeEdit, QSpinBox {
                background-color: #35302a; color: #f1dca7; border: 1px solid #4a4238;
                border-radius: 4px; padding: 4px;
            }
            QPushButton { background-color: #4a4238; color: #f1dca7; border: none;
                          border-radius: 6px; padding: 7px 14px; }
            QPushButton:hover { background-color: #5e5448; }
            QPushButton#primary { background-color: #9b9b7a; color: #24201b; font-weight: bold; }
            QPushButton#primary:hover { background-color: #baa587; }
            QSlider::groove:horizontal { height: 6px; background: #4a4238; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #e8ac65; border-radius: 3px; }
            QSlider::handle:horizontal { background: #f1dca7; width: 16px; margin: -5px 0; border-radius: 8px; }
        """)

        self._detailed = False
        self._syncing = False
        self._tasks = TaskRepository.get_all_tasks()

        root = QVBoxLayout(self)
        form = QFormLayout()
        root.addLayout(form)

        self.task_combo = QComboBox()
        self.task_combo.addItem("(Görevsiz)", None)
        for t in self._tasks:
            self.task_combo.addItem(f"{t.name}  [{t.tag}]" if t.tag else t.name, t)
        form.addRow("Görev:", self.task_combo)

        today = QDate.fromString(logical_day(datetime.datetime.now()).isoformat(), Qt.ISODate)
        self.date_edit = QDateEdit(today)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(today)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        form.addRow("Tarih:", self.date_edit)

        now = QTime.currentTime()
        self.start_edit = QTimeEdit(now.addSecs(-3600))
        self.end_edit = QTimeEdit(now)
        for e in (self.start_edit, self.end_edit):
            e.setDisplayFormat("HH:mm")
        form.addRow("Başlangıç:", self._time_row(self.start_edit))
        form.addRow("Bitiş:", self._time_row(self.end_edit))

        quick = QHBoxLayout()
        quick.setSpacing(4)
        for label, mins in (("30dk", 30), ("1s", 60), ("1.5s", 90), ("2s", 120), ("3s", 180)):
            b = QPushButton(label)
            b.setToolTip(f"Bitişi başlangıçtan {label} sonrasına ayarla")
            b.clicked.connect(lambda _=False, m=mins: self._apply_duration(m))
            quick.addWidget(b)
        now_btn = QPushButton("Şimdi")
        now_btn.setToolTip("Bitişi şu an yap")
        now_btn.clicked.connect(lambda: self.end_edit.setTime(QTime.currentTime()))
        quick.addWidget(now_btn)
        form.addRow("Hızlı:", quick)

        # --- Detailed-only section ---
        self.detail_box = QWidget()
        dform = QFormLayout(self.detail_box)
        dform.setContentsMargins(0, 0, 0, 0)

        slider_row = QHBoxLayout()
        self.dur_slider = QSlider(Qt.Horizontal)
        self.dur_slider.setRange(SLIDER_STEP_MIN, SLIDER_MAX_MIN)
        self.dur_slider.setSingleStep(SLIDER_STEP_MIN)
        self.dur_slider.setPageStep(15)
        self.dur_label = QLabel()
        self.dur_label.setMinimumWidth(70)
        self.dur_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        slider_row.addWidget(self.dur_slider, 1)
        slider_row.addWidget(self.dur_label)
        dform.addRow("Süre:", slider_row)

        self.completed_check = QCheckBox("Tamamlandı")
        self.completed_check.setChecked(True)
        dform.addRow("", self.completed_check)

        self.interrupt_spin = QSpinBox()
        self.interrupt_spin.setRange(0, 99)
        dform.addRow("Kesinti sayısı:", self.interrupt_spin)

        root.addWidget(self.detail_box)

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #b8a99a;")
        root.addWidget(self.summary_label)

        buttons = QHBoxLayout()
        self.toggle_btn = QPushButton()
        self.toggle_btn.clicked.connect(self._toggle_mode)
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        self.save_btn = QPushButton("Ekle")
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self._save)
        buttons.addWidget(self.toggle_btn)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(self.save_btn)
        root.addLayout(buttons)

        self.start_edit.timeChanged.connect(self._on_times_changed)
        self.end_edit.timeChanged.connect(self._on_times_changed)
        self.date_edit.dateChanged.connect(self._on_times_changed)
        self.dur_slider.valueChanged.connect(self._on_slider_changed)

        if self._duration_minutes() <= 0:  # e.g. just after the 03:00 day boundary
            self.start_edit.setTime(_time_from_offset(0))
        self._set_mode(False)
        self._on_times_changed()

    def _time_row(self, edit: QTimeEdit) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        btn = QToolButton()
        btn.setText("🕒")
        btn.setToolTip("Saati tıklayarak seç")
        btn.setStyleSheet("QToolButton { background-color: #35302a; border: 1px solid #4a4238;"
                          " border-radius: 4px; padding: 3px 6px; }"
                          "QToolButton:hover { background-color: #4a4238; }")
        popup = TimePickerPopup(edit, self)
        btn.clicked.connect(lambda: popup.popup_at(btn))
        h.addWidget(edit, 1)
        h.addWidget(btn)
        return row

    def _apply_duration(self, mins: int):
        self._set_end_from_duration(mins)

    def _set_end_from_duration(self, mins: int):
        """end = start + mins within the logical day; pull start back if it would overflow."""
        start_off = _offset(self.start_edit.time())
        if start_off + mins > DAY_MIN:
            start_off = DAY_MIN - mins
            self._syncing = True
            self.start_edit.setTime(_time_from_offset(start_off))
            self._syncing = False
        self._syncing = True
        self.end_edit.setTime(_time_from_offset(start_off + mins))
        self._syncing = False
        self._on_times_changed()

    # ------------------------------------------------------------------
    # Mode handling
    # ------------------------------------------------------------------
    def _toggle_mode(self):
        self._set_mode(not self._detailed)

    def _set_mode(self, detailed: bool):
        self._detailed = detailed
        self.detail_box.setVisible(detailed)
        self.toggle_btn.setText("‹ Basit" if detailed else "Ayrıntılı ›")
        self.adjustSize()

    # ------------------------------------------------------------------
    # Time <-> slider sync
    # ------------------------------------------------------------------
    def _duration_minutes(self) -> int:
        return _offset(self.end_edit.time(), is_end=True) - _offset(self.start_edit.time())

    def _on_times_changed(self, *_):
        if self._syncing:
            return
        mins = self._duration_minutes()
        self._syncing = True
        self.dur_slider.setValue(max(SLIDER_STEP_MIN, min(SLIDER_MAX_MIN, mins)))
        self._syncing = False
        self._refresh_labels()

    def _on_slider_changed(self, value):
        if self._syncing:
            return
        self._set_end_from_duration(round(value / SLIDER_STEP_MIN) * SLIDER_STEP_MIN)

    def _refresh_labels(self):
        mins = self._duration_minutes()
        h, m = divmod(max(mins, 0), 60)
        text = f"{h}s {m}dk" if h else f"{m}dk"
        self.dur_label.setText(text)
        self.summary_label.setText(
            f"Süre: {text}" if mins > 0 else "⚠ Bitiş, başlangıçtan sonra olmalı"
        )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    def _save(self):
        mins = self._duration_minutes()
        if mins <= 0:
            QMessageBox.warning(self, "Geçersiz aralık", "Bitiş zamanı başlangıçtan sonra olmalı.")
            return

        day_start = datetime.datetime.combine(
            self.date_edit.date().toPython(), datetime.time(hour=DAY_START_HOUR))
        start_dt = day_start + datetime.timedelta(minutes=_offset(self.start_edit.time()))
        end_dt = start_dt + datetime.timedelta(minutes=mins)
        if end_dt > datetime.datetime.now():
            QMessageBox.warning(self, "Geçersiz aralık", "Bitiş zamanı gelecekte olamaz.")
            return

        task = self.task_combo.currentData()
        # 'Free Timer' mode so stats queries (Focus / Free Timer only) include it.
        session_id = SessionRepository.log_session(
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=mins * 60,
            planned_duration_minutes=None,
            mode="Free Timer",
            completed=self.completed_check.isChecked() if self._detailed else True,
            task_name=task.name if task else None,
            category=task.tag if task else None,
            interruption_count=self.interrupt_spin.value() if self._detailed else 0,
        )
        if not session_id:
            QMessageBox.critical(self, "Hata", "Oturum kaydedilemedi.")
            return
        self.accept()
