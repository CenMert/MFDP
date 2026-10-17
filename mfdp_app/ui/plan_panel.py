"""
PlanPanel - Ana pencerenin sağında açılıp kapanan "bu oturumda ne yapacağım?" paneli.

Üstte hiyerarşik görev ağacı (eski Hiyerarşik Görevler penceresinin yerine), altta oturum planı:
çalışılacak görev + tahmini süre (başlatmak için zorunlu) + isteğe bağlı ilk adım notu.
"""

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                               QTreeWidget, QTreeWidgetItem, QSpinBox, QComboBox, QCheckBox,
                               QMenu, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QPixmap, QIcon, QKeySequence, QShortcut

from mfdp_app.core.recursive_task_manager import RecursiveTaskManager
from mfdp_app.db.tag_repository import TagRepository
from mfdp_app.db.task_repository import TaskRepository

ESTIMATE_CHIPS = (15, 25, 45, 60, 90)
TAG_COLORS = ['#e8ac65', '#9b9b7a', '#ffcb69', '#d08c60',
              '#997b66', '#d9ae94', '#797d62', '#b58463']
DEFAULT_TAG = "General"
INVALID_STYLE = "border: 1px solid #d08c60;"


class PlanPanel(QFrame):
    task_chosen = Signal(int)  # ağaçtan görev seçildi (id)

    WIDTH = 340

    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("SidePanel")
        self.setFixedWidth(self.WIDTH)
        self.task_manager = task_manager  # aktif görev bunda tutulur
        self.tasks = RecursiveTaskManager()
        self._building = False
        self._locked = False
        self._active_id = None
        self._loading = False  # programatik doldurma kaydedilmemiş değişiklik sayılmaz
        self._dirty = False

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self.refresh)
        self.tasks.task_updated_signal.connect(lambda _id: self._refresh_timer.start(100))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        title = QLabel("Ne üzerinde çalışacaksın?")
        title.setObjectName("SideTitle")
        root.addWidget(title)

        # --- Görev ağacı ---
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Görev", "Tahmin"])
        self.tree.setColumnWidth(0, 210)
        self.tree.setRootIsDecorated(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.setStyleSheet("""
            QTreeWidget { background-color: #24201b; border: 1px solid #35302a;
                          border-radius: 5px; color: #f1dca7; font-size: 12px; }
            QTreeWidget::item { padding: 3px; }
            QTreeWidget::item:selected { background-color: #4a4238; }
            QTreeWidget::item:hover { background-color: #35302a; }
            QHeaderView::section { background-color: #1c1915; color: #8f8273; border: none; padding: 3px; }
        """)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.customContextMenuRequested.connect(self._show_menu)
        self.tree.setMinimumHeight(180)
        root.addWidget(self.tree, 1)

        self.chk_done = QCheckBox("Bitenleri göster")
        self.chk_done.setObjectName("ChimeCheckbox")
        self.chk_done.toggled.connect(lambda _on: self.refresh())
        root.addWidget(self.chk_done)

        # --- Yeni görev ekleme ---
        add_row = QHBoxLayout()
        add_row.setSpacing(4)
        self.input_new = QLineEdit()
        self.input_new.setPlaceholderText("Yeni görev…")
        self.input_new.returnPressed.connect(self._add_default)
        add_row.addWidget(self.input_new, 1)
        self.combo_tag = QComboBox()
        self.combo_tag.setEditable(True)
        self.combo_tag.setFixedWidth(90)
        self.combo_tag.setToolTip("Ana görevin etiketi (alt görev üstünün etiketini alır)")
        add_row.addWidget(self.combo_tag)
        root.addLayout(add_row)

        add_btns = QHBoxLayout()
        add_btns.setSpacing(4)
        self.btn_add_sub = QPushButton("+ Alt görev")
        self.btn_add_sub.setCursor(Qt.PointingHandCursor)
        self.btn_add_sub.setToolTip("Seçili görevin altına ekle (Enter)")
        self.btn_add_sub.clicked.connect(self._add_sub)
        add_btns.addWidget(self.btn_add_sub)
        self.btn_add_root = QPushButton("+ Ana görev")
        self.btn_add_root.setCursor(Qt.PointingHandCursor)
        self.btn_add_root.clicked.connect(self._add_root)
        add_btns.addWidget(self.btn_add_root)
        root.addLayout(add_btns)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("SideLine")
        root.addWidget(line)

        # --- Oturum planı ---
        plan_title = QLabel("Bu oturumun planı")
        plan_title.setObjectName("SideTitle")
        root.addWidget(plan_title)

        self.lbl_task = QLabel("Görev: seçilmedi")
        self.lbl_task.setObjectName("SidePlanRow")
        self.lbl_task.setWordWrap(True)
        root.addWidget(self.lbl_task)

        est_row = QHBoxLayout()
        est_row.setSpacing(4)
        self.spin_est = QSpinBox()
        self.spin_est.setRange(0, 600)
        self.spin_est.setSuffix(" dk")
        self.spin_est.setSpecialValueText("Tahmin?")
        self.spin_est.setFixedWidth(90)
        self.spin_est.valueChanged.connect(lambda _v: self._clear_invalid(self.spin_est))
        self.spin_est.valueChanged.connect(lambda _v: self._mark_dirty())
        est_row.addWidget(self.spin_est)
        self.chips = []
        for minutes in ESTIMATE_CHIPS:
            chip = QPushButton(str(minutes))
            chip.setObjectName("FeedbackChip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda _c=False, m=minutes: self.spin_est.setValue(m))
            self.chips.append(chip)
            est_row.addWidget(chip)
        est_row.addStretch()
        root.addLayout(est_row)

        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("İlk adım: bu oturum sonunda ne bitmiş olacak?")
        self.input_note.textEdited.connect(lambda _t: self._mark_dirty())
        root.addWidget(self.input_note)

        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setToolTip("Seçili görevin tahminini ve notunu kaydet (Ctrl+S)")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(lambda _checked=False: self.save_plan())
        root.addWidget(self.btn_save)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_plan)

        self.lbl_msg = QLabel("")
        self.lbl_msg.setObjectName("SideMuted")
        self.lbl_msg.setWordWrap(True)
        root.addWidget(self.lbl_msg)

        self.refresh()

    # ------------------------------------------------------------------
    # Dışarıya açılan API
    # ------------------------------------------------------------------
    def estimate_minutes(self) -> int:
        return self.spin_est.value()

    def plan_note(self) -> str:
        return self.input_note.text().strip()

    def validate(self, need_estimate=True) -> bool:
        """Başlamadan önce görev (ve tahmin) seçilmiş mi; değilse eksik alanı vurgula."""
        if self._active_id is None:
            self._flag(self.tree, "Önce neye çalışacağını seç ya da yeni görev yaz.")
            self.input_new.setFocus()
            return False
        if need_estimate and self.spin_est.value() <= 0:
            self._flag(self.spin_est, "Ne kadar süreceğini tahmin et (dk).")
            self.spin_est.setFocus()
            return False
        self.lbl_msg.setText("")
        return True

    def save_plan(self, task_id=None):
        """Tahmin ve notu göreve kalıcı yaz (task_id verilmezse aktif görev)."""
        if not isinstance(task_id, int):
            task_id = self._active_id
        if task_id is None:
            self.lbl_msg.setText("Kaydetmek için önce bir görev seç.")
            return
        if self.spin_est.value() > 0:
            self.tasks.update_task(task_id, planned_duration=self.spin_est.value())
        TaskRepository.set_notes(task_id, self.plan_note())
        self._set_dirty(False)
        self.lbl_msg.setText("Kaydedildi.")
        QTimer.singleShot(2000, lambda: self.lbl_msg.text() == "Kaydedildi." and self.lbl_msg.setText(""))

    def remember_estimate(self):
        """Oturum başlarken tahmin + notu göreve yaz; sonraki oturumda ön dolum olur."""
        if self._active_id is not None:
            self.save_plan(self._active_id)

    def _mark_dirty(self):
        if not self._loading:
            self._set_dirty(True)

    def _set_dirty(self, dirty):
        self._dirty = dirty
        self.btn_save.setEnabled(dirty and self._active_id is not None)
        self.btn_save.setText("Kaydet •" if dirty else "Kaydet")

    def set_locked(self, running: bool):
        """Oturum sürerken plan değiştirilemez; bitince yeni oturum için sıfırlanır."""
        was_locked = self._locked
        self._locked = running
        for w in (self.spin_est, *self.chips):  # oturum içi not alınabilsin: not açık kalır
            w.setEnabled(not running)
        if was_locked and not running:
            self._loading = True
            self.spin_est.setValue(0)
            self._loading = False
            self._prefill_estimate()

    def sync_active(self, task_id):
        """Aktif görev başka yerden değiştiyse (plan 'Başla', tekrar satırı…) ağaçta göster."""
        new_id = task_id if task_id and task_id > 0 else None
        if new_id != self._active_id:
            if self._dirty and self._active_id is not None:
                self.save_plan(self._active_id)  # görev değişirken kaydedilmemiş düzenleme kaybolmasın
            self._active_id = new_id
            self._load_task_fields()
        self._select_active()
        task = TaskRepository.get_task_by_id(self._active_id) if self._active_id else None
        self.lbl_task.setText(f"Görev: {self._path(task)}" if task else "Görev: seçilmedi")
        if task:
            self._clear_invalid(self.tree)
            if not self._locked:
                self._prefill_estimate()

    # ------------------------------------------------------------------
    # Ağaç
    # ------------------------------------------------------------------
    def refresh(self):
        show_done = self.chk_done.isChecked()
        self._building = True
        self.tree.blockSignals(True)
        try:
            colors = {t['name']: t['color'] for t in TagRepository.get_all_tags() if t['color']}
            self.tree.clear()
            for task in self.tasks.get_root_tasks():
                if task.is_completed and not show_done:
                    continue
                item = self._make_item(task, colors)
                self.tree.addTopLevelItem(item)
                self._add_children(item, task.id, colors, show_done)
            self._reload_tags()
        finally:
            self.tree.blockSignals(False)
            self._building = False
        self._select_active()

    def _make_item(self, task, colors):
        item = QTreeWidgetItem()
        item.setText(0, task.name)
        item.setCheckState(0, Qt.Checked if task.is_completed else Qt.Unchecked)
        item.setText(1, f"{task.planned_duration_minutes} dk" if task.planned_duration_minutes else "")
        item.setData(0, Qt.UserRole, task.id)
        color = task.color or colors.get(task.tag)
        if color:
            pix = QPixmap(8, 8)
            pix.fill(QColor(color))
            item.setIcon(0, QIcon(pix))
        if task.is_completed:
            for col in (0, 1):
                item.setForeground(col, QColor("#7a6e60"))
        return item

    def _add_children(self, parent_item, parent_id, colors, show_done):
        children = [c for c in self.tasks.get_child_tasks(parent_id) if show_done or not c.is_completed]
        for child in children:
            child_item = self._make_item(child, colors)
            parent_item.addChild(child_item)
            self._add_children(child_item, child.id, colors, show_done)
        if children:
            parent_item.setExpanded(True)

    def _select_active(self):
        self.tree.blockSignals(True)
        self.tree.clearSelection()
        if self._active_id is not None:
            item = self._find_item(self._active_id)
            if item:
                item.setSelected(True)
                self.tree.scrollToItem(item)
        self.tree.blockSignals(False)

    def _find_item(self, task_id):
        stack = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if item.data(0, Qt.UserRole) == task_id:
                return item
            stack.extend(item.child(i) for i in range(item.childCount()))
        return None

    def _selected_id(self):
        items = self.tree.selectedItems()
        return items[0].data(0, Qt.UserRole) if items else None

    def _on_item_clicked(self, item, _col):
        if self._locked:
            return  # oturum sürerken görev değişmez
        task_id = item.data(0, Qt.UserRole)
        if task_id:
            self.task_chosen.emit(task_id)

    def _on_item_changed(self, item, col):
        if self._building or col != 0:
            return
        task_id = item.data(0, Qt.UserRole)
        if task_id:
            self.tasks.set_task_completed(task_id, item.checkState(0) == Qt.Checked)

    def _load_task_fields(self):
        """Seçilen görevin kayıtlı not ve tahminini alanlara yükle."""
        self._loading = True
        self.input_note.setText(TaskRepository.get_notes(self._active_id) if self._active_id else "")
        if not self._locked:
            self.spin_est.setValue(0)
        self._loading = False
        self._set_dirty(False)

    def _prefill_estimate(self):
        if self._active_id is None or self.spin_est.value() > 0:
            return
        task = TaskRepository.get_task_by_id(self._active_id)
        if task and task.planned_duration_minutes:
            self._loading = True
            self.spin_est.setValue(task.planned_duration_minutes)
            self._loading = False

    def _path(self, task):
        parts, seen = [task.name], {task.id}
        while task.parent_id and task.parent_id not in seen:
            seen.add(task.parent_id)
            task = TaskRepository.get_task_by_id(task.parent_id)
            if not task:
                break
            parts.insert(0, task.name)
        return " › ".join(parts)

    # ------------------------------------------------------------------
    # Ekleme / düzenleme / silme
    # ------------------------------------------------------------------
    def _reload_tags(self):
        current = self.combo_tag.currentText()
        self.combo_tag.clear()
        names = [t['name'] for t in TagRepository.get_all_tags()] or [DEFAULT_TAG]
        self.combo_tag.addItems(names)
        if current:
            self.combo_tag.setEditText(current)

    def _add_default(self):
        (self._add_sub if self._selected_id() else self._add_root)()

    def _add_root(self):
        self._create(None)

    def _add_sub(self):
        parent_id = self._selected_id()
        if parent_id is None:
            self.lbl_msg.setText("Alt görev için önce bir görev seç.")
            return
        self._create(parent_id)

    def _create(self, parent_id):
        name = self.input_new.text().strip()
        if not name:
            self._flag(self.input_new, "Görev adı boş olamaz.")
            return
        if parent_id:
            parent = TaskRepository.get_task_by_id(parent_id)
            tag = parent.tag if parent else DEFAULT_TAG
        else:
            tag = self.combo_tag.currentText().strip() or DEFAULT_TAG
        task_id = self.tasks.create_task(name, parent_id=parent_id, tag=tag, color=self._tag_color(tag))
        if not task_id:
            QMessageBox.warning(self, "Hata", "Görev oluşturulamadı (aynı adlı görev olabilir).")
            return
        self.input_new.clear()
        self._clear_invalid(self.input_new)
        self.refresh()
        if not self._locked:
            self.task_chosen.emit(task_id)  # yeni eklenen görev hemen seçili olur

    def _tag_color(self, tag):
        """Etiketin rengi; yeni etikete paletten sıradaki renk atanır."""
        tags = TagRepository.get_all_tags()
        for t in tags:
            if t['name'] == tag and t['color']:
                return t['color']
        color = TAG_COLORS[len(tags) % len(TAG_COLORS)]
        TagRepository.assign_color_to_tag(tag, color)
        return color

    def _show_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        task_id = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        act_sub = menu.addAction("Alt görev ekle")
        act_rename = menu.addAction("Yeniden adlandır")
        act_est = menu.addAction("Süre tahmini…")
        act_tag = menu.addAction("Etiketi değiştir…")
        menu.addSeparator()
        act_del = menu.addAction("Sil")
        chosen = menu.exec(self.tree.viewport().mapToGlobal(pos))
        if chosen is act_sub:
            if not self._locked:
                self.task_chosen.emit(task_id)
            self.input_new.setFocus()
        elif chosen is act_rename:
            name, ok = QInputDialog.getText(self, "Yeniden adlandır", "Yeni ad:", text=item.text(0))
            if ok and name.strip():
                self.tasks.update_task(task_id, title=name.strip())
        elif chosen is act_est:
            task = TaskRepository.get_task_by_id(task_id)
            value, ok = QInputDialog.getInt(self, "Süre tahmini", "Dakika:",
                                            task.planned_duration_minutes or 25, 1, 600)
            if ok:
                self.tasks.update_task(task_id, planned_duration=value)
        elif chosen is act_tag:
            self._change_tag(task_id)
        elif chosen is act_del:
            self._delete(task_id, item.text(0))

    def _change_tag(self, task_id):
        """Görevin etiketini (ve rengini) değiştir; alt görevler isteğe bağlı birlikte gider."""
        task = TaskRepository.get_task_by_id(task_id)
        names = [t['name'] for t in TagRepository.get_all_tags()] or [DEFAULT_TAG]
        tag, ok = QInputDialog.getItem(self, "Etiketi değiştir", "Etiket (yeni yazabilirsin):",
                                       names, names.index(task.tag) if task.tag in names else 0, True)
        tag = tag.strip()
        if not ok or not tag or tag == task.tag:
            return
        targets = [task_id]
        subs = TaskRepository.get_all_subtasks_recursive(task_id)
        if subs:
            reply = QMessageBox.question(
                self, "Alt görevler", f"{len(subs)} alt görevin etiketi de '{tag}' olsun mu?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                targets += [sub.id for sub in subs]
        color = self._tag_color(tag)
        for tid in targets:
            self.tasks.update_task(tid, tag=tag)
            TaskRepository.update_task(tid, color=color)
        self.refresh()
        if self._active_id in targets:
            self.task_manager.active_task_changed_signal.emit(self._active_id)  # başlık etiketi tazelensin

    def _delete(self, task_id, name):
        reply = QMessageBox.question(
            self, "Onay", f"'{name}' silinsin mi?\nAlt görevleri de silinir.",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        doomed = [sub.id for sub in TaskRepository.get_all_subtasks_recursive(task_id)] + [task_id]
        for tid in doomed:
            self.tasks.delete_task(tid)
        if self._active_id in doomed:
            self.task_manager.set_active_task(None)
        self.refresh()

    # ------------------------------------------------------------------
    # Doğrulama vurgusu
    # ------------------------------------------------------------------
    def _flag(self, widget, message):
        widget.setStyleSheet(widget.styleSheet() + INVALID_STYLE if widget is not self.tree
                             else widget.styleSheet().replace("border: 1px solid #35302a;", INVALID_STYLE))
        self.lbl_msg.setText(message)
        self.lbl_msg.setStyleSheet("font-size: 11px; color: #d08c60;")
        QTimer.singleShot(2500, lambda: self._clear_invalid(widget))

    def _clear_invalid(self, widget):
        if widget is self.tree:
            widget.setStyleSheet(widget.styleSheet().replace(INVALID_STYLE, "border: 1px solid #35302a;"))
        else:
            widget.setStyleSheet(widget.styleSheet().replace(INVALID_STYLE, ""))
        if not self.lbl_msg.text().startswith("Alt görev için"):
            self.lbl_msg.setText("")
        self.lbl_msg.setStyleSheet("")
