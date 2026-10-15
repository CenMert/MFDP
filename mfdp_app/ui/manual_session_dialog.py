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
                               QSpinBox, QCheckBox, QWidget, QMessageBox)
from PySide6.QtCore import Qt, QDate, QTime

from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.task_repository import TaskRepository

SLIDER_STEP_MIN = 5
SLIDER_MAX_MIN = 12 * 60


class ManualSessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oturum Ekle")
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; }
            QLabel { color: #cdd6f4; }
            QComboBox, QDateEdit, QTimeEdit, QSpinBox {
                background-color: #313244; color: #cdd6f4; border: 1px solid #45475a;
                border-radius: 4px; padding: 4px;
            }
            QPushButton { background-color: #45475a; color: #cdd6f4; border: none;
                          border-radius: 6px; padding: 7px 14px; }
            QPushButton:hover { background-color: #585b70; }
            QPushButton#primary { background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; }
            QPushButton#primary:hover { background-color: #94d990; }
            QSlider::groove:horizontal { height: 6px; background: #45475a; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #89b4fa; border-radius: 3px; }
            QSlider::handle:horizontal { background: #cdd6f4; width: 16px; margin: -5px 0; border-radius: 8px; }
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

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        form.addRow("Tarih:", self.date_edit)

        now = QTime.currentTime()
        self.start_edit = QTimeEdit(now.addSecs(-3600))
        self.end_edit = QTimeEdit(now)
        for e in (self.start_edit, self.end_edit):
            e.setDisplayFormat("HH:mm")
        form.addRow("Başlangıç:", self.start_edit)
        form.addRow("Bitiş:", self.end_edit)

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
        self.summary_label.setStyleSheet("color: #a6adc8;")
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

        self._set_mode(False)
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
        s, e = self.start_edit.time(), self.end_edit.time()
        return (e.hour() * 60 + e.minute()) - (s.hour() * 60 + s.minute())

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
        value = round(value / SLIDER_STEP_MIN) * SLIDER_STEP_MIN
        start = self.start_edit.time()
        start_min = start.hour() * 60 + start.minute()
        # Keep the session within the chosen day: cap by moving start earlier if needed.
        if start_min + value > 24 * 60 - 1:
            start_min = 24 * 60 - 1 - value
            self._syncing = True
            self.start_edit.setTime(QTime(start_min // 60, start_min % 60))
            self._syncing = False
        end_min = start_min + value
        self._syncing = True
        self.end_edit.setTime(QTime(end_min // 60, end_min % 60))
        self._syncing = False
        self._refresh_labels()

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

        d = self.date_edit.date().toPython()
        s = self.start_edit.time().toPython().replace(second=0, microsecond=0)
        e = self.end_edit.time().toPython().replace(second=0, microsecond=0)
        start_dt = datetime.datetime.combine(d, s)
        end_dt = datetime.datetime.combine(d, e)
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
