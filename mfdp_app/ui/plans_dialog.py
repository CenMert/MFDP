"""
PlansDialog - eğer-ise planlarını ekle / sil.

"EĞER <gün(ler)> <saat> (<durum>) İSE <görev>: <eylem>"
Saat seçiliyse plan o saatte sorulur; yalnızca durum yazılırsa (ör. "kahvaltıdan sonra")
yan panelde hatırlatılır.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QCheckBox, QTimeEdit, QLineEdit, QComboBox, QListWidget,
                               QListWidgetItem, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt, QTime, Signal

from mfdp_app.db.plan_repository import PlanRepository
from mfdp_app.db.task_repository import TaskRepository
from mfdp_app.ui.side_panel import plan_sentence, _TR_DAYS


class PlansDialog(QDialog):
    plans_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eğer–İse Planları")
        self.resize(560, 520)
        self.setStyleSheet(
            "QDialog { background-color: #1e1e2e; }"
            "QListWidget, QLineEdit, QComboBox, QTimeEdit { background-color: #181825;"
            " border: 1px solid #45475a; border-radius: 4px; padding: 3px; }"
            "QListWidget::item:selected { background-color: #313244; color: #f9e2af; }")

        root = QVBoxLayout(self)
        intro = QLabel("Ne zaman ve nerede başlayacağını önceden kararlaştır: "
                       "<i>“Eğer Salı 10:00 olursa, Sinyaller'den 1 oturum soru çözerim.”</i>")
        intro.setWordWrap(True)
        root.addWidget(intro)

        self.list = QListWidget()
        root.addWidget(self.list, 1)
        btn_delete = QPushButton("Seçili planı sil")
        btn_delete.clicked.connect(self._delete_selected)
        root.addWidget(btn_delete, 0, Qt.AlignRight)

        form = QFormLayout()
        days_row = QHBoxLayout()
        self.day_checks = []
        for i, name in enumerate(_TR_DAYS):
            cb = QCheckBox(name)
            cb.setChecked(i < 5)
            self.day_checks.append(cb)
            days_row.addWidget(cb)
        form.addRow("EĞER gün:", days_row)

        time_row = QHBoxLayout()
        self.chk_time = QCheckBox("saat")
        self.chk_time.setChecked(True)
        self.time_edit = QTimeEdit(QTime(10, 0))
        self.time_edit.setDisplayFormat("HH:mm")
        self.chk_time.toggled.connect(self.time_edit.setEnabled)
        time_row.addWidget(self.chk_time)
        time_row.addWidget(self.time_edit)
        time_row.addStretch()
        form.addRow("", time_row)

        self.cue_edit = QLineEdit()
        self.cue_edit.setPlaceholderText("isteğe bağlı durum: kahvaltıdan sonra, kütüphaneye girince…")
        form.addRow("ve/veya durum:", self.cue_edit)

        self.task_combo = QComboBox()
        self.task_combo.addItem("— görev yok —", None)
        for task in TaskRepository.get_all_tasks():
            label = f"{task.tag} · {task.name}" if task.tag else task.name
            self.task_combo.addItem(label, task.id)
        form.addRow("İSE görev:", self.task_combo)

        self.action_edit = QLineEdit()
        self.action_edit.setPlaceholderText("ne yapacağım: 1 oturum soru çöz, 3. bölümü kendimi test ederek tekrar et…")
        form.addRow("eylem:", self.action_edit)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_add = QPushButton("Plan ekle")
        btn_add.setObjectName("StartButton")
        btn_add.clicked.connect(self._add)
        btn_row.addWidget(btn_add)
        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

        self._reload()

    def _reload(self):
        self.list.clear()
        for plan in PlanRepository.get_active_plans():
            item = QListWidgetItem(plan_sentence(plan))
            item.setData(Qt.UserRole, plan['id'])
            self.list.addItem(item)

    def _add(self):
        days = [i for i, cb in enumerate(self.day_checks) if cb.isChecked()]
        time = self.time_edit.time().toString("HH:mm") if self.chk_time.isChecked() else None
        cue = self.cue_edit.text().strip() or None
        action = self.action_edit.text().strip() or None
        task_id = self.task_combo.currentData()
        if not days:
            QMessageBox.warning(self, "Eksik", "En az bir gün seç.")
            return
        if not time and not cue:
            QMessageBox.warning(self, "Eksik", "Bir saat ya da bir durum (ipucu) gir: planın 'eğer' kısmı bu.")
            return
        if not task_id and not action:
            QMessageBox.warning(self, "Eksik", "Bir görev ya da eylem gir: planın 'ise' kısmı bu.")
            return
        PlanRepository.add_plan(days, time, cue, task_id, action)
        self.cue_edit.clear()
        self.action_edit.clear()
        self._reload()
        self.plans_changed.emit()

    def _delete_selected(self):
        item = self.list.currentItem()
        if not item:
            return
        PlanRepository.delete_plan(item.data(Qt.UserRole))
        self._reload()
        self.plans_changed.emit()
