"""
Recursive Task Window - Hiyerarşik görev yönetimi için UI
QTreeWidget ile checkbox'lar ve hierarchical görünüm
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QFormLayout,
    QSpinBox, QMessageBox, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QKeyEvent
from mfdp_app.core.recursive_task_manager import RecursiveTaskManager
from mfdp_app.models.data_models import Task
from mfdp_app.db.tag_repository import TagRepository


class RecursiveTaskWindow(QDialog):
    """Özyinelemeli görev yönetimi penceresi."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_manager = RecursiveTaskManager()
        self.editing_task_id = None
        self._updating_tree = False  # Tree güncelleme flag'i
        
        # Debounce timer - birden fazla signal geldiğinde tek bir refresh yapmak için
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh_tree)
        
        self.setWindowTitle("Özyinelemeli Görev Yönetimi - MFDP")
        self.resize(900, 700)
        self.setStyleSheet("background-color: #24201b; color: #f1dca7;")
        
        # Non-modal yap - arka plandaki pencereyi kullanılabilir tut
        self.setModal(False)
        
        self.init_ui()
        
        # Default button'u kaldır - Enter tuşunun pencereyi kapatmasını önle
        self.btn_close.setDefault(False)
        self.btn_close.setAutoDefault(False)
        
        # TaskManager signal'larını dinle
        self.task_manager.task_updated_signal.connect(self.schedule_refresh)
        self.task_manager.task_completed_signal.connect(self.on_task_completed)
        self.task_manager.task_uncompleted_signal.connect(self.on_task_uncompleted)
        
        # İlk yükleme
        self.refresh_task_tree()
    
    def init_ui(self):
        """UI bileşenlerini oluştur."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("Özyinelemeli Görev Yönetimi")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #9b9b7a; padding: 10px;")
        main_layout.addWidget(title)
        
        # Ana içerik: Sol tarafta tree, sağ tarafta form
        content_layout = QHBoxLayout()
        
        # Sol: Task Tree
        tree_group = QGroupBox("Görevler (Hiyerarşik)")
        tree_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #4a4238; border-radius: 5px; margin-top: 30px; padding-top: 30px; }")
        tree_layout = QVBoxLayout()
        
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["Görev", "Süre"])
        self.task_tree.setColumnWidth(0, 400)
        self.task_tree.setColumnWidth(1, 100)
        self.task_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #35302a;
                border: 1px solid #4a4238;
                border-radius: 5px;
                color: #f1dca7;
            }
            QTreeWidget::item {
                padding: 5px;
                height: 25px;
            }
            QTreeWidget::item:selected {
                background-color: #4a4238;
            }
            QTreeWidget::item:hover {
                background-color: #5e5448;
            }
        """)
        self.task_tree.itemChanged.connect(self.on_checkbox_changed)
        self.task_tree.itemClicked.connect(self.on_task_selected)
        self.task_tree.itemDoubleClicked.connect(self.on_task_double_clicked)
        tree_layout.addWidget(self.task_tree)
        
        # Alt görev ekleme butonu
        btn_add_subtask = QPushButton("Seçili Görevin Alt Görevi Olarak Ekle")
        btn_add_subtask.setStyleSheet("background-color: #e8ac65; color: #24201b; font-weight: bold; padding: 8px;")
        btn_add_subtask.setCursor(Qt.PointingHandCursor)
        btn_add_subtask.clicked.connect(self.add_as_subtask)
        tree_layout.addWidget(btn_add_subtask)
        
        tree_group.setLayout(tree_layout)
        content_layout.addWidget(tree_group, stretch=2)
        
        # Sağ: Task Formu
        form_group = QGroupBox("Görev Oluştur/Düzenle")
        form_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #4a4238; border-radius: 5px; margin-top: 30px; padding-top: 30px; }")
        form_layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Görev başlığı")
        self.input_title.setStyleSheet("background-color: #35302a; border: 1px solid #4a4238; border-radius: 5px; padding: 5px;")
        # Enter tuşuna basıldığında kaydet
        self.input_title.returnPressed.connect(self.save_task)
        form.addRow("Başlık:", self.input_title)
        
        # Parent seçimi
        self.combo_parent = QComboBox()
        self.combo_parent.addItem("(Ana Görev)", None)
        self.combo_parent.setStyleSheet("background-color: #35302a; border: 1px solid #4a4238; border-radius: 5px; padding: 5px;")
        form.addRow("Ana Görev:", self.combo_parent)
        
        # Süre seçimi
        self.input_duration = QSpinBox()
        self.input_duration.setMinimum(0)
        self.input_duration.setMaximum(999)
        self.input_duration.setValue(0)
        self.input_duration.setSuffix(" dakika")
        self.input_duration.setSpecialValueText("Süresiz")
        self.input_duration.setStyleSheet("background-color: #35302a; border: 1px solid #4a4238; border-radius: 5px; padding: 5px;")
        form.addRow("Planlanan Süre:", self.input_duration)
        
        # Tag seçimi
        self.combo_tag = QComboBox()
        self.combo_tag.setEditable(True)
        self.combo_tag.setStyleSheet("background-color: #35302a; border: 1px solid #4a4238; border-radius: 5px; padding: 5px;")
        form.addRow("Tag:", self.combo_tag)
        
        form_layout.addLayout(form)
        
        # Bilgi etiketi
        info_label = QLabel("💡 İpucu: Tree'de bir göreve çift tıklayarak veya 'Alt Görev Ekle' butonuna basarak alt görev ekleyebilirsiniz.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #d2c2a8; font-size: 11px; padding: 5px; background-color: #35302a; border-radius: 5px;")
        form_layout.addWidget(info_label)
        
        # Butonlar
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setStyleSheet("background-color: #9b9b7a; color: #24201b; font-weight: bold; padding: 8px;")
        self.btn_save.clicked.connect(self.save_task)
        # Enter tuşu için default button yapma - sadece görsel olarak vurgula
        self.btn_save.setAutoDefault(False)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_delete = QPushButton("Sil")
        self.btn_delete.setStyleSheet("background-color: #d08c60; color: #24201b; font-weight: bold; padding: 8px;")
        self.btn_delete.clicked.connect(self.delete_task)
        btn_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.setStyleSheet("background-color: #4a4238; color: #f1dca7; padding: 8px;")
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)
        
        form_layout.addLayout(btn_layout)
        form_group.setLayout(form_layout)
        content_layout.addWidget(form_group, stretch=1)
        
        main_layout.addLayout(content_layout)
        
        # Alt butonlar
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.btn_close = QPushButton("Kapat")
        self.btn_close.setStyleSheet("background-color: #4a4238; color: #f1dca7; padding: 8px 20px;")
        self.btn_close.clicked.connect(self.accept)
        # Default button olarak ayarlama - Enter tuşunun pencereyi kapatmasını önle
        self.btn_close.setDefault(False)
        self.btn_close.setAutoDefault(False)
        bottom_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(bottom_layout)
    
    def schedule_refresh(self):
        """Refresh'i schedule et (debounce için)."""
        # Timer'ı yeniden başlat - eğer zaten çalışıyorsa iptal et ve tekrar başlat
        self._refresh_timer.stop()
        self._refresh_timer.start(100)  # 100ms debounce
    
    def _do_refresh_tree(self):
        """Gerçek refresh işlemini yap."""
        self.refresh_task_tree()
    
    def refresh_task_tree(self):
        """Görev ağacını yenile."""
        # Signal döngüsünü önlemek için flag kontrolü
        if self._updating_tree:
            return
        
        self._updating_tree = True
        
        # Signal'leri geçici olarak bloke et
        self.task_tree.blockSignals(True)
        
        try:
            self.task_tree.clear()
            
            # Root görevleri al
            root_tasks = self.task_manager.get_root_tasks()
            
            # Tree widget'a ekle
            for root_task in root_tasks:
                root_item = self._create_tree_item(root_task)
                self.task_tree.addTopLevelItem(root_item)
                self._add_children_to_tree(root_item, root_task.id)
            
            # Parent combo box'ı güncelle
            self._refresh_parent_combo()
            
            # Tag combo box'ı güncelle
            self._refresh_tag_combo()
        finally:
            # Signal'leri tekrar aktif et
            self.task_tree.blockSignals(False)
            self._updating_tree = False
    
    def _create_tree_item(self, task: Task) -> QTreeWidgetItem:
        """Bir görev için tree item oluştur."""
        item = QTreeWidgetItem()
        
        # Checkbox ile görev başlığı
        item.setText(0, task.name)
        item.setCheckState(0, Qt.Checked if task.is_completed else Qt.Unchecked)
        
        # Süre bilgisi
        duration_text = f"{task.planned_duration_minutes} dk" if task.planned_duration_minutes else "Süresiz"
        item.setText(1, duration_text)
        
        # Task ID'yi sakla
        item.setData(0, Qt.UserRole, task.id)
        
        # Tamamlanmış görevler için stil
        if task.is_completed:
            item.setForeground(0, QColor("#7a6e60"))
            item.setForeground(1, QColor("#7a6e60"))
        
        return item
    
    def _add_children_to_tree(self, parent_item: QTreeWidgetItem, parent_id: int):
        """Bir görevin alt görevlerini tree'ye ekle."""
        children = self.task_manager.get_child_tasks(parent_id)
        for child_task in children:
            child_item = self._create_tree_item(child_task)
            parent_item.addChild(child_item)
            # Recursive olarak alt görevlerin alt görevlerini de ekle
            self._add_children_to_tree(child_item, child_task.id)
        
        # Alt görevler varsa expand et
        if children:
            parent_item.setExpanded(True)
    
    def _refresh_parent_combo(self):
        """Parent combo box'ı güncelle."""
        self.combo_parent.clear()
        self.combo_parent.addItem("(Ana Görev)", None)
        
        # Tüm görevleri al ve combo'ya ekle
        all_tasks = self.task_manager.get_all_tasks_hierarchical()
        for task in all_tasks:
            # Düzenlenen görevi hariç tut (kendisini parent yapamaz)
            if self.editing_task_id and task.id == self.editing_task_id:
                continue
            
            # Hiyerarşik isim oluştur
            display_name = self._get_task_display_name(task)
            # Girinti ekle (hierarchy için)
            indent = "  " * self._get_task_depth(task)
            self.combo_parent.addItem(f"{indent}{display_name}", task.id)
    
    def _get_task_depth(self, task: Task) -> int:
        """Bir görevin derinliğini hesapla (root = 0)."""
        depth = 0
        current_task = task
        visited_ids = {task.id}
        
        while current_task.parent_id:
            if current_task.parent_id in visited_ids:
                break
            visited_ids.add(current_task.parent_id)
            parent = self.task_manager.get_task(current_task.parent_id)
            if not parent:
                break
            depth += 1
            current_task = parent
        
        return depth
    
    def _get_task_display_name(self, task: Task) -> str:
        """Görev için hiyerarşik görünen isim oluştur."""
        # Parent chain'i topla
        path_parts = [task.name]
        current_task = task
        visited_ids = {task.id}  # Circular reference kontrolü
        
        while current_task.parent_id:
            if current_task.parent_id in visited_ids:
                break  # Circular reference tespit edildi
            visited_ids.add(current_task.parent_id)
            
            parent = self.task_manager.get_task(current_task.parent_id)
            if not parent:
                break
            path_parts.insert(0, parent.name)
            current_task = parent
        
        return " > ".join(path_parts)
    
    def _refresh_tag_combo(self):
        """Tag combo box'ı güncelle."""
        self.combo_tag.clear()
        tags = TagRepository.get_all_tags()
        for tag in tags:
            self.combo_tag.addItem(tag['name'])
        if not tags:
            self.combo_tag.addItem("General")
    
    def on_checkbox_changed(self, item: QTreeWidgetItem, column: int):
        """Checkbox değiştiğinde çağrılır."""
        # Tree güncelleniyorsa işlem yapma
        if self._updating_tree:
            return
        
        if column != 0:
            return
        
        task_id = item.data(0, Qt.UserRole)
        if not task_id:
            return
        
        is_checked = item.checkState(0) == Qt.Checked
        
        # Recursive completion mantığını tetikle
        # Signal'ler otomatik olarak refresh_task_tree'yi çağıracak
        self.task_manager.set_task_completed(task_id, is_checked)
    
    def on_task_selected(self, item: QTreeWidgetItem, column: int):
        """Görev seçildiğinde formu doldur."""
        task_id = item.data(0, Qt.UserRole)
        if not task_id:
            return
        
        task = self.task_manager.get_task(task_id)
        if not task:
            return
        
        self.editing_task_id = task_id
        self.input_title.setText(task.name)
        
        # Parent seçimi
        if task.parent_id:
            index = self.combo_parent.findData(task.parent_id)
            if index >= 0:
                self.combo_parent.setCurrentIndex(index)
        else:
            self.combo_parent.setCurrentIndex(0)
        
        # Süre
        self.input_duration.setValue(task.planned_duration_minutes or 0)
        
        # Tag
        index = self.combo_tag.findText(task.tag)
        if index >= 0:
            self.combo_tag.setCurrentIndex(index)
        else:
            self.combo_tag.setEditText(task.tag)
    
    def on_task_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Görev çift tıklandığında - alt görev olarak ekleme moduna geç."""
        task_id = item.data(0, Qt.UserRole)
        if not task_id:
            return
        
        # Formu temizle ve seçili görevi parent olarak ayarla
        self.clear_form()
        index = self.combo_parent.findData(task_id)
        if index >= 0:
            self.combo_parent.setCurrentIndex(index)
        
        # Başlık alanına odaklan
        self.input_title.setFocus()
        
        # Kullanıcıya bilgi ver
        task = self.task_manager.get_task(task_id)
        if task:
            self.input_title.setPlaceholderText(f"'{task.name}' görevinin alt görevi olarak ekle...")
    
    def save_task(self):
        """Görev kaydet."""
        title = self.input_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Uyarı", "Görev başlığı boş olamaz!")
            self.input_title.setFocus()
            return
        
        parent_id = self.combo_parent.currentData()
        planned_duration = self.input_duration.value() if self.input_duration.value() > 0 else None
        tag = self.combo_tag.currentText().strip() or "General"
        
        if self.editing_task_id:
            # Güncelle
            success = self.task_manager.update_task(
                self.editing_task_id,
                title=title,
                planned_duration=planned_duration,
                tag=tag
            )
            if not success:
                QMessageBox.warning(self, "Hata", "Görev güncellenemedi!")
                return
        else:
            # Yeni oluştur
            task_id = self.task_manager.create_task(
                title=title,
                parent_id=parent_id,
                planned_duration=planned_duration,
                tag=tag
            )
            if not task_id:
                QMessageBox.warning(self, "Hata", "Görev oluşturulamadı!")
                return
        
        # Formu temizle ve default haline getir
        self.clear_form()
        # Tree refresh signal'ler tarafından otomatik yapılacak
    
    def delete_task(self):
        """Görev sil."""
        if not self.editing_task_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir görev seçin!")
            return
        
        reply = QMessageBox.question(
            self, "Onay", "Bu görevi silmek istediğinize emin misiniz?\nAlt görevler de silinecektir.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.task_manager.delete_task(self.editing_task_id)
            self.clear_form()
            self.refresh_task_tree()
    
    def on_task_completed(self, task_id: int):
        """Görev tamamlandığında çağrılır."""
        pass  # Tree zaten refresh_task_tree ile güncelleniyor
    
    def on_task_uncompleted(self, task_id: int):
        """Görev tamamlanmadığında çağrılır."""
        pass  # Tree zaten refresh_task_tree ile güncelleniyor
    
    def add_as_subtask(self):
        """Seçili görevin alt görevi olarak ekleme moduna geç."""
        selected_items = self.task_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Bilgi", "Lütfen önce bir görev seçin!")
            return
        
        item = selected_items[0]
        task_id = item.data(0, Qt.UserRole)
        if not task_id:
            QMessageBox.information(self, "Bilgi", "Lütfen geçerli bir görev seçin!")
            return
        
        # Formu temizle ve seçili görevi parent olarak ayarla
        self.clear_form()
        index = self.combo_parent.findData(task_id)
        if index >= 0:
            self.combo_parent.setCurrentIndex(index)
        
        # Başlık alanına odaklan
        self.input_title.setFocus()
        
        # Kullanıcıya bilgi ver
        task = self.task_manager.get_task(task_id)
        if task:
            self.input_title.setPlaceholderText(f"'{task.name}' görevinin alt görevi olarak ekle...")
    
    def keyPressEvent(self, event: QKeyEvent):
        """Enter tuşunu yakala ve kaydetme yap, pencereyi kapatma."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Eğer bir input alanı focus'ta ise kaydet
            if self.input_title.hasFocus() or self.combo_tag.hasFocus():
                self.save_task()
                event.accept()
                return
        # Diğer tuşları normal şekilde işle
        super().keyPressEvent(event)
    
    def clear_form(self):
        """Formu temizle."""
        self.editing_task_id = None
        self.input_title.clear()
        self.input_title.setPlaceholderText("Görev başlığı")
        self.combo_parent.setCurrentIndex(0)
        self.input_duration.setValue(0)
        self.combo_tag.setCurrentIndex(0)
        self.task_tree.clearSelection()
        # Focus'u başlık alanına geri ver
        self.input_title.setFocus()

