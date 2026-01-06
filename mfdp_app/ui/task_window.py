from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QFormLayout,
    QSpinBox, QCheckBox, QColorDialog, QMessageBox, QWidget,
    QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from mfdp_app.core.task_manager import TaskManager
from mfdp_app.models.data_models import Task

class TaskWindow(QDialog):
    task_selected_signal = Signal(int)  # task_id
    
    def __init__(self, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.editing_task_id = None
        
        self.setWindowTitle("Task Yönetimi - MFDP")
        self.resize(700, 600)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")
        
        # Non-modal yap - arka plandaki pencereyi kullanılabilir tut
        self.setModal(False)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("Task Yönetimi")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #a6e3a1; padding: 10px;")
        main_layout.addWidget(title)
        
        # Ana içerik: Sol tarafta liste, sağ tarafta form
        content_layout = QHBoxLayout()
        
        # Sol: Task Listesi
        list_group = QGroupBox("Tasklar")
        list_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #45475a; border-radius: 5px; margin-top: 30px; padding-top: 30px; }")
        list_layout = QVBoxLayout()
        
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabel("Tasklar (Tag'a göre gruplanmış)")
        self.task_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 5px;
                color: #cdd6f4;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #45475a;
            }
        """)
        self.task_tree.itemClicked.connect(self.on_task_selected)
        list_layout.addWidget(self.task_tree)
        
        # Aktif task butonu
        self.btn_set_active = QPushButton("Aktif Task Olarak Ayarla")
        self.btn_set_active.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; font-weight: bold;")
        self.btn_set_active.clicked.connect(self.set_active_task)
        list_layout.addWidget(self.btn_set_active)
        
        list_group.setLayout(list_layout)
        content_layout.addWidget(list_group, stretch=2)
        
        # Sağ: Task Formu
        form_group = QGroupBox("Task Oluştur/Düzenle")
        form_group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #45475a; border-radius: 5px; margin-top: 30px; padding-top: 30px; }")
        form_layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Task adı")
        self.input_name.setStyleSheet("background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px;")
        form.addRow("Task Adı:", self.input_name)
        
        self.input_tag = QLineEdit()
        self.input_tag.setPlaceholderText("Tag adı (örn: Ders, İş)")
        self.input_tag.setStyleSheet("background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px;")
        form.addRow("Tag:", self.input_tag)
        
        # Süre seçimi
        duration_layout = QHBoxLayout()
        self.chk_has_duration = QCheckBox("Belirli süre ata")
        self.chk_has_duration.setStyleSheet("color: #bac2de;")
        self.chk_has_duration.toggled.connect(self.on_duration_toggled)
        duration_layout.addWidget(self.chk_has_duration)
        
        self.input_duration = QSpinBox()
        self.input_duration.setMinimum(1)
        self.input_duration.setMaximum(999)
        self.input_duration.setValue(25)
        self.input_duration.setSuffix(" dakika")
        self.input_duration.setEnabled(False)
        self.input_duration.setStyleSheet("background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px;")
        duration_layout.addWidget(self.input_duration)
        form.addRow("Süre:", duration_layout)
        
        # Tag renk seçici
        color_layout = QHBoxLayout()
        self.btn_color = QPushButton("Renk Seç")
        self.btn_color.setStyleSheet("background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 5px;")
        self.btn_color.clicked.connect(self.select_tag_color)
        self.color_preview = QLabel("")
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("border: 1px solid #45475a; border-radius: 3px;")
        self.selected_color = None
        color_layout.addWidget(self.btn_color)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        form.addRow("Tag Rengi:", color_layout)
        
        form_layout.addLayout(form)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Kaydet")
        self.btn_save.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_task)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_delete = QPushButton("Sil")
        self.btn_delete.setStyleSheet("background-color: #f38ba8; color: #1e1e2e; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_task)
        btn_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.setStyleSheet("background-color: #45475a; color: #cdd6f4;")
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
        self.btn_close.setStyleSheet("background-color: #45475a; color: #cdd6f4;")
        self.btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(bottom_layout)
        
        # TaskManager signal'larını dinle
        self.task_manager.task_created_signal.connect(self.refresh_task_list)
        self.task_manager.task_updated_signal.connect(self.refresh_task_list)
        self.task_manager.active_task_changed_signal.connect(self.on_active_task_changed)
        
        # İlk yükleme
        self.refresh_task_list()
        self.on_active_task_changed(self.task_manager.get_active_task_id() or -1)
    
    def on_duration_toggled(self, checked):
        """Süre checkbox'ı değiştiğinde."""
        self.input_duration.setEnabled(checked)
    
    def select_tag_color(self):
        """Tag rengi seç."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #45475a; border-radius: 3px;")
    
    def refresh_task_list(self):
        """Task listesini yenile."""
        self.task_tree.clear()
        
        # Tüm taskları al
        tasks = self.task_manager.get_all_tasks()
        
        # Tag'lara göre grupla
        tasks_by_tag = {}
        for task in tasks:
            if task.tag not in tasks_by_tag:
                tasks_by_tag[task.tag] = []
            tasks_by_tag[task.tag].append(task)
        
        # Tree widget'a ekle
        for tag, tag_tasks in tasks_by_tag.items():
            # Tag için renk al
            tag_info = next((t for t in self.task_manager.get_all_tags() if t['name'] == tag), None)
            tag_color = tag_info['color'] if tag_info and tag_info.get('color') else '#89b4fa'
            
            # Tag item'ı
            tag_item = QTreeWidgetItem(self.task_tree)
            tag_item.setText(0, f"🏷️ {tag}")
            tag_item.setData(0, Qt.UserRole, None)  # Tag item'ı, task değil
            tag_item.setExpanded(True)
            tag_item.setForeground(0, QColor(tag_color))
            
            # Task'ları ekle
            for task in tag_tasks:
                task_item = QTreeWidgetItem(tag_item)
                duration_text = f" ({task.planned_duration_minutes} dk)" if task.planned_duration_minutes else " (Süresiz)"
                task_item.setText(0, f"✓ {task.name}{duration_text}")
                task_item.setData(0, Qt.UserRole, task.id)
                
                # Aktif task'ı vurgula
                if self.task_manager.get_active_task_id() == task.id:
                    task_item.setForeground(0, QColor("#a6e3a1"))
                    task_item.setText(0, f"▶ {task.name}{duration_text}")
    
    def on_task_selected(self, item, column):
        """Task seçildiğinde formu doldur."""
        task_id = item.data(0, Qt.UserRole)
        if task_id is None:
            return  # Tag item'ı seçilmiş
        
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            return
        
        self.editing_task_id = task_id
        self.input_name.setText(task.name)
        self.input_tag.setText(task.tag)
        
        if task.planned_duration_minutes:
            self.chk_has_duration.setChecked(True)
            self.input_duration.setValue(task.planned_duration_minutes)
        else:
            self.chk_has_duration.setChecked(False)
        
        # Renk
        tag_info = next((t for t in self.task_manager.get_all_tags() if t['name'] == task.tag), None)
        if tag_info and tag_info.get('color'):
            self.selected_color = tag_info['color']
            self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #45475a; border-radius: 3px;")
        else:
            self.selected_color = None
            self.color_preview.setStyleSheet("border: 1px solid #45475a; border-radius: 3px;")
    
    def save_task(self):
        """Task kaydet."""
        name = self.input_name.text().strip()
        tag = self.input_tag.text().strip()
        
        if not name or not tag:
            QMessageBox.warning(self, "Uyarı", "Task adı ve tag boş olamaz!")
            return
        
        planned_duration = None
        if self.chk_has_duration.isChecked():
            planned_duration = self.input_duration.value()
        
        if self.editing_task_id:
            # Güncelle
            success = self.task_manager.update_task(
                self.editing_task_id,
                name=name,
                tag=tag,
                planned_duration_minutes=planned_duration
            )
            if success and self.selected_color:
                self.task_manager.assign_color_to_tag(tag, self.selected_color)
        else:
            # Yeni oluştur
            task_id = self.task_manager.create_task(name, tag, planned_duration, self.selected_color)
            if task_id:
                if self.selected_color:
                    self.task_manager.assign_color_to_tag(tag, self.selected_color)
        
        self.clear_form()
        self.refresh_task_list()
    
    def delete_task(self):
        """Task sil."""
        if not self.editing_task_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir task seçin!")
            return
        
        reply = QMessageBox.question(
            self, "Onay", "Bu task'ı silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.task_manager.delete_task(self.editing_task_id)
            self.clear_form()
            self.refresh_task_list()
    
    def set_active_task(self):
        """Seçili task'ı aktif yap."""
        selected_items = self.task_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Önce bir task seçin!")
            return
        
        item = selected_items[0]
        task_id = item.data(0, Qt.UserRole)
        if task_id is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir task seçin, tag değil!")
            return
        
        self.task_manager.set_active_task(task_id)
        self.task_selected_signal.emit(task_id)
        self.refresh_task_list()
    
    def on_active_task_changed(self, task_id):
        """Aktif task değiştiğinde."""
        if task_id == -1:
            self.btn_set_active.setText("Aktif Task Olarak Ayarla")
        else:
            task = self.task_manager.get_task_by_id(task_id)
            if task:
                self.btn_set_active.setText(f"Aktif: {task.name}")
        self.refresh_task_list()
    
    def clear_form(self):
        """Formu temizle."""
        self.editing_task_id = None
        self.input_name.clear()
        self.input_tag.clear()
        self.chk_has_duration.setChecked(False)
        self.input_duration.setValue(25)
        self.selected_color = None
        self.color_preview.setStyleSheet("border: 1px solid #45475a; border-radius: 3px;")
        self.task_tree.clearSelection()

