"""
TrackingDialog - Hangi dersler için tekrar hatırlatması isteniyor?

Hatırlatma opt-in'dir: işaretlenmeyen derslerde (ör. plansız, boşluk buldukça yapılan bitirme
çalışması) hiçbir etiket, sınav bağı ya da kuyruk girdisi hatırlatma üretmez.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, Signal

from mfdp_app.db.review_repository import ReviewRepository
from mfdp_app.db.task_repository import TaskRepository


class TrackingDialog(QDialog):
    tracking_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tekrar Takibi")
        self.resize(440, 420)
        self.setStyleSheet(
            "QDialog { background-color: #1e1e2e; }"
            "QListWidget { background-color: #181825; border: 1px solid #45475a; border-radius: 4px; }"
            "QListWidget::item { padding: 5px; }"
            "QListWidget::indicator { width: 16px; height: 16px; border: 1px solid #6c7086;"
            " border-radius: 3px; background-color: #181825; }"
            "QListWidget::indicator:checked { background-color: #a6e3a1; border-color: #a6e3a1; }")

        root = QVBoxLayout(self)
        intro = QLabel("Hangi dersler için <b>tekrar hatırlatması</b> istiyorsun? İşaretlediklerin için "
                       "derste işlenenler ve çalıştığın konular 1-3-7-14 gün aralıklarla, sınav varsa sınava "
                       "göre sana hatırlatılır. İşaretlemediğin işler (plansız projeler, keyfine çalıştıkların) "
                       "hiçbir hatırlatma üretmez.")
        intro.setWordWrap(True)
        root.addWidget(intro)

        self.list = QListWidget()
        tracked = ReviewRepository.get_tracked_course_ids()
        for task in TaskRepository.get_root_tasks():
            item = QListWidgetItem(f"{task.name}   ·   {task.tag}" if task.tag else task.name)
            item.setData(Qt.UserRole, task.id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if task.id in tracked else Qt.Unchecked)
            self.list.addItem(item)
        self.list.itemChanged.connect(self._on_changed)
        root.addWidget(self.list, 1)

        row = QHBoxLayout()
        row.addStretch()
        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        row.addWidget(btn_close)
        root.addLayout(row)

    def _on_changed(self, item):
        ReviewRepository.set_course_tracked(item.data(Qt.UserRole), item.checkState() == Qt.Checked)
        self.tracking_changed.emit()
