"""
LectureDialog - Derste işlenen konuları kaydet.

Ders + tarih seç, her satıra bir konu yaz. Her konu dersin altında bir alt görev olur ve
ders günü "ilk karşılaşma" sayılır: tekrar takvimi (1-3-7-14-30) o günden başlar, sol panelde
"derste işlendi · N gün önce" diye hatırlatılır. Hiç çalışmadan da kaydedilebilir.
"""

import datetime

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
                               QDateEdit, QPlainTextEdit, QFormLayout, QMessageBox, QTextBrowser)
from PySide6.QtCore import Qt, QDate, Signal

from mfdp_app.core import review_scheduler
from mfdp_app.core.daily_report import logical_day
from mfdp_app.db.task_repository import TaskRepository

_TR_DAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


class LectureDialog(QDialog):
    topics_added = Signal()

    def __init__(self, parent=None, course_id=None):
        super().__init__(parent)
        self.setWindowTitle("Derste İşlenenler")
        self.resize(520, 560)
        self.setStyleSheet(
            "QDialog { background-color: #1e1e2e; }"
            "QPlainTextEdit, QTextBrowser, QComboBox, QDateEdit { background-color: #181825;"
            " border: 1px solid #45475a; border-radius: 4px; padding: 3px; }")

        root = QVBoxLayout(self)
        intro = QLabel("Bugün derste ne işlendi? Her satıra bir konu yaz; her biri tekrar takvimine "
                       "<b>ders günü</b> ilk karşılaşma olarak girer ve sonra sana hatırlatılır.")
        intro.setWordWrap(True)
        root.addWidget(intro)

        form = QFormLayout()
        self.course_combo = QComboBox()
        for task in TaskRepository.get_root_tasks():
            self.course_combo.addItem(task.name, task.id)
        if course_id is not None:
            idx = self.course_combo.findData(course_id)
            if idx >= 0:
                self.course_combo.setCurrentIndex(idx)
        form.addRow("Ders:", self.course_combo)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        today = logical_day(datetime.datetime.now())
        self.date_edit.setDate(QDate(today.year, today.month, today.day))
        self.date_edit.setMaximumDate(QDate(today.year, today.month, today.day))
        form.addRow("Ders günü:", self.date_edit)
        root.addLayout(form)

        self.topics_edit = QPlainTextEdit()
        self.topics_edit.setPlaceholderText(
            "Dipol antenler\nIşıma örüntüsü ve yönlülük\nFriis iletim denklemi")
        root.addWidget(self.topics_edit, 1)

        row = QHBoxLayout()
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #a6e3a1;")
        row.addWidget(self.lbl_status, 1)
        btn_add = QPushButton("Kaydet")
        btn_add.setObjectName("StartButton")
        btn_add.clicked.connect(self._save)
        row.addWidget(btn_add)
        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        row.addWidget(btn_close)
        root.addLayout(row)

        recent_title = QLabel("Son 14 günde işlenenler")
        recent_title.setStyleSheet("font-weight: bold; margin-top: 6px;")
        root.addWidget(recent_title)
        self.recent = QTextBrowser()
        self.recent.setMaximumHeight(170)
        root.addWidget(self.recent)
        self._reload_recent()

    def _day(self) -> datetime.date:
        return self.date_edit.date().toPython()

    def _save(self):
        course_id = self.course_combo.currentData()
        titles = self.topics_edit.toPlainText().splitlines()
        if not course_id:
            QMessageBox.warning(self, "Eksik", "Önce Tasklar'dan bir ders (ana görev) oluştur.")
            return
        if not any(t.strip() for t in titles):
            QMessageBox.warning(self, "Eksik", "En az bir konu yaz.")
            return
        created, skipped = review_scheduler.add_lecture_topics(course_id, self._day(), titles)
        self.topics_edit.clear()
        msg = f"{len(created)} konu kaydedildi."
        if skipped:
            msg += f" Kaydedilemeyen: {', '.join(skipped)}"
        self.lbl_status.setText(msg)
        self._reload_recent()
        self.topics_added.emit()

    def _reload_recent(self):
        rows = review_scheduler.recent_lecture_topics(14)
        if not rows:
            self.recent.setHtml("<span style='color:#7f849c'>Henüz kayıt yok.</span>")
            return
        html, last = [], None
        for r in rows:
            day = datetime.date.fromisoformat(r['learned_on'])
            if day != last:
                html.append(f"<p style='margin:6px 0 2px; color:#f9e2af'><b>{day.day:02d}.{day.month:02d} "
                            f"{_TR_DAYS[day.weekday()]}</b></p>")
                last = day
            prefix = f"{r['course_name']} · "
            topic = r['name'][len(prefix):] if r['name'].startswith(prefix) else r['name']
            html.append(f"<div>• <span style='color:#7f849c'>{r['course_name']}</span> — {topic}</div>")
        self.recent.setHtml("".join(html))
