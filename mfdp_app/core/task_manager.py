from PySide6.QtCore import QObject, Signal
from typing import Optional, List, Tuple
from mfdp_app.models.data_models import Task
from mfdp_app.db_manager import (
    insert_task, update_task, delete_task, get_task_by_id,
    get_all_tasks, get_tasks_by_tag, get_all_tags,
    assign_color_to_tag, get_tag_time_summary, get_task_time_summary
)

class TaskManager(QObject):
    """Task ve tag yönetimi için core sınıf."""
    
    task_created_signal = Signal(int)  # task_id
    task_updated_signal = Signal(int)  # task_id
    active_task_changed_signal = Signal(int)  # task_id, None ise -1
    
    def __init__(self):
        super().__init__()
        self._active_task_id: Optional[int] = None
        self._default_colors = [
            '#89b4fa', '#a6e3a1', '#f9e2af', '#f38ba8',
            '#cba6f7', '#fab387', '#94e2d5', '#f5c2e7'
        ]
        self._color_index = 0
    
    def create_task(self, name: str, tag: str, planned_duration_minutes: Optional[int] = None, color: Optional[str] = None) -> Optional[int]:
        """Yeni task oluştur."""
        # Eğer renk verilmemişse, tag için otomatik renk ata
        if color is None:
            existing_tags = get_all_tags()
            tag_colors = {t['name']: t['color'] for t in existing_tags if t['color']}
            if tag in tag_colors:
                color = tag_colors[tag]
            else:
                # Yeni tag için otomatik renk ata
                color = self._get_next_color()
                assign_color_to_tag(tag, color)
        
        task_id = insert_task(name, tag, planned_duration_minutes, color)
        if task_id:
            self.task_created_signal.emit(task_id)
        return task_id
    
    def update_task(self, task_id: int, name: Optional[str] = None, tag: Optional[str] = None,
                   planned_duration_minutes: Optional[int] = None, color: Optional[str] = None) -> bool:
        """Task güncelle."""
        success = update_task(task_id, name, tag, planned_duration_minutes, color)
        if success:
            self.task_updated_signal.emit(task_id)
        return success
    
    def delete_task(self, task_id: int) -> bool:
        """Task'ı sil (soft delete)."""
        success = delete_task(task_id)
        if success:
            # Eğer aktif task silindiyse, aktif task'ı temizle
            if self._active_task_id == task_id:
                self.set_active_task(None)
        return success
    
    def get_all_tasks(self, include_inactive: bool = False) -> List[Task]:
        """Tüm taskları getir."""
        return get_all_tasks(include_inactive)
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Tag'a göre taskları getir."""
        return get_tasks_by_tag(tag)
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """ID'ye göre task getir."""
        return get_task_by_id(task_id)
    
    def set_active_task(self, task_id: Optional[int]):
        """Aktif task ayarla."""
        # Eğer aynı task_id zaten ayarlıysa, signal emit etme (sonsuz döngüyü önle)
        if self._active_task_id == task_id:
            return
        
        if task_id is not None:
            task = get_task_by_id(task_id)
            if not task or not task.is_active:
                return
        
        self._active_task_id = task_id
        self.active_task_changed_signal.emit(task_id if task_id else -1)
    
    def get_active_task(self) -> Optional[Task]:
        """Aktif task'ı getir."""
        if self._active_task_id is None:
            return None
        return get_task_by_id(self._active_task_id)
    
    def get_active_task_id(self) -> Optional[int]:
        """Aktif task ID'sini getir."""
        return self._active_task_id
    
    def get_all_tags(self) -> List[dict]:
        """Tüm tagları getir."""
        return get_all_tags()
    
    def assign_color_to_tag(self, tag: str, color: str) -> bool:
        """Tag'a renk ata."""
        return assign_color_to_tag(tag, color)
    
    def get_tag_time_summary(self, tag: str, days: Optional[int] = None) -> float:
        """Tag için toplam süre (dakika)."""
        return get_tag_time_summary(tag, days)
    
    def get_task_time_summary(self, task_id: int, days: Optional[int] = None) -> float:
        """Task için toplam süre (dakika)."""
        return get_task_time_summary(task_id, days)
    
    def get_task_name_and_tag(self) -> Tuple[Optional[str], Optional[str]]:
        """Aktif task'ın adını ve tag'ini döndür."""
        task = self.get_active_task()
        if task:
            return (task.name, task.tag)
        return (None, None)
    
    def _get_next_color(self) -> str:
        """Sıradaki renk paletinden renk al."""
        color = self._default_colors[self._color_index % len(self._default_colors)]
        self._color_index += 1
        return color

