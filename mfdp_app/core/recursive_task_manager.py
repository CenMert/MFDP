"""
Recursive Task Manager - Composite Pattern ile hiyerarşik görev yönetimi
"""
from PySide6.QtCore import QObject, Signal
from typing import Optional, List
from mfdp_app.models.data_models import Task
from mfdp_app.db_manager import (
    insert_task, update_task, get_task_by_id,
    get_root_tasks, get_child_tasks, get_all_subtasks_recursive
)


class RecursiveTaskManager(QObject):
    """
    Composite Design Pattern kullanarak hiyerarşik görev yönetimi.
    Recursive completion mantığı:
    - Aşağı Doğru: Ana görev tamamlandığında tüm alt görevler tamamlanır
    - Yukarı Doğru: Tüm alt görevler tamamlandığında ana görev otomatik tamamlanır
    """
    
    task_updated_signal = Signal(int)  # task_id
    task_completed_signal = Signal(int)  # task_id
    task_uncompleted_signal = Signal(int)  # task_id
    
    def __init__(self):
        super().__init__()
    
    def create_task(self, title: str, parent_id: Optional[int] = None, 
                   planned_duration: Optional[int] = None, tag: str = "General") -> Optional[int]:
        """Yeni görev oluştur."""
        task_id = insert_task(
            name=title,
            tag=tag,
            planned_duration_minutes=planned_duration,
            parent_id=parent_id,
            is_completed=False
        )
        if task_id:
            self.task_updated_signal.emit(task_id)
        return task_id
    
    def update_task(self, task_id: int, title: Optional[str] = None,
                   planned_duration: Optional[int] = None, tag: Optional[str] = None) -> bool:
        """Görev bilgilerini güncelle."""
        success = update_task(
            task_id,
            name=title,
            planned_duration_minutes=planned_duration,
            tag=tag
        )
        if success:
            self.task_updated_signal.emit(task_id)
        return success
    
    def set_task_completed(self, task_id: int, completed: bool) -> bool:
        """
        Görevi tamamlandı/tamamlanmadı olarak işaretle.
        Recursive completion mantığını uygular.
        """
        task = get_task_by_id(task_id)
        if not task:
            return False
        
        # Eğer durum değişmediyse işlem yapma
        if task.is_completed == completed:
            return True
        
        # Güncellenen task ID'lerini takip et (signal'leri batch olarak emit etmek için)
        updated_task_ids = set()
        
        # Aşağı Doğru: Eğer ana görev tamamlanıyorsa, tüm alt görevleri de tamamla
        if completed:
            self._complete_subtasks_recursive(task_id, updated_task_ids)
        
        # Görevin kendisini güncelle
        success = update_task(task_id, is_completed=completed)
        
        if success:
            updated_task_ids.add(task_id)
            
            # Yukarı Doğru: Ana görevi kontrol et (hem tamamlanma hem tamamlanmama durumunda)
            self._check_and_update_parent(task_id, updated_task_ids)
            
            # Tüm güncellemeleri batch olarak signal'lerle bildir
            for tid in updated_task_ids:
                updated_task = get_task_by_id(tid)
                if updated_task:
                    if updated_task.is_completed:
                        self.task_completed_signal.emit(tid)
                    else:
                        self.task_uncompleted_signal.emit(tid)
                    self.task_updated_signal.emit(tid)
        
        return success
    
    def _complete_subtasks_recursive(self, parent_id: int, updated_task_ids: set):
        """Bir görevin tüm alt görevlerini recursive olarak tamamla."""
        children = get_child_tasks(parent_id)
        for child in children:
            # Alt görevi tamamla
            update_task(child.id, is_completed=True)
            updated_task_ids.add(child.id)
            # Alt görevin alt görevlerini de tamamla (recursive)
            self._complete_subtasks_recursive(child.id, updated_task_ids)
    
    def _check_and_update_parent(self, task_id: int, updated_task_ids: set):
        """
        Bir görev değiştiğinde, ana görevin durumunu kontrol et.
        - Eğer tüm kardeşler tamamlanmışsa ana görevi tamamla
        - Eğer herhangi bir kardeş tamamlanmamışsa ana görevi tamamlanmamış yap
        Signal'leri batch olarak emit etmek için updated_task_ids set'ine ekler.
        """
        task = get_task_by_id(task_id)
        if not task or not task.parent_id:
            return
        
        parent_id = task.parent_id
        
        # Circular reference kontrolü
        if parent_id in updated_task_ids:
            return
        
        siblings = get_child_tasks(parent_id)
        
        if not siblings:
            return
        
        # Tüm kardeşler tamamlandı mı kontrol et
        all_completed = all(sibling.is_completed for sibling in siblings)
        
        parent = get_task_by_id(parent_id)
        if not parent:
            return
        
        if all_completed:
            # Tüm kardeşler tamamlandıysa ana görevi tamamla
            if not parent.is_completed:
                update_task(parent_id, is_completed=True)
                updated_task_ids.add(parent_id)
                # Ana görevin ana görevini de kontrol et (recursive)
                self._check_and_update_parent(parent_id, updated_task_ids)
        else:
            # Herhangi bir kardeş tamamlanmamışsa ana görevi tamamlanmamış yap
            if parent.is_completed:
                update_task(parent_id, is_completed=False)
                updated_task_ids.add(parent_id)
                # Ana görevin ana görevini de kontrol et (recursive)
                self._check_and_update_parent(parent_id, updated_task_ids)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """ID'ye göre görev getir."""
        return get_task_by_id(task_id)
    
    def get_root_tasks(self) -> List[Task]:
        """Tüm root (ana) görevleri getir."""
        return get_root_tasks()
    
    def get_child_tasks(self, parent_id: int) -> List[Task]:
        """Bir görevin doğrudan alt görevlerini getir."""
        return get_child_tasks(parent_id)
    
    def get_all_tasks_hierarchical(self) -> List[Task]:
        """
        Tüm görevleri hiyerarşik yapıda getir.
        Root görevler ve tüm alt görevleri içerir.
        """
        all_tasks = []
        root_tasks = self.get_root_tasks()
        
        def add_task_and_children(task: Task):
            all_tasks.append(task)
            children = self.get_child_tasks(task.id)
            for child in children:
                add_task_and_children(child)
        
        for root_task in root_tasks:
            add_task_and_children(root_task)
        
        return all_tasks
    
    def delete_task(self, task_id: int) -> bool:
        """Görevi sil (soft delete - is_active=False)."""
        success = update_task(task_id, is_active=False)
        if success:
            self.task_updated_signal.emit(task_id)
        return success

