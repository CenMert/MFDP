"""
Task Repository - manages tasks with hierarchical support.
"""

import datetime
from typing import List, Optional

from mfdp_app.db.base_repository import BaseRepository


class TaskRepository(BaseRepository):
    """Handle all task-related database operations including hierarchy."""
    
    @staticmethod
    def insert_task(
        name: str,
        tag: str,
        planned_duration_minutes: Optional[int] = None,
        color: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_completed: bool = False
    ) -> Optional[int]:
        """
        Create a new task.
        
        Args:
            name: Task name (must be unique)
            tag: Task category/tag
            planned_duration_minutes: Planned duration
            color: Task color
            parent_id: Parent task ID (for subtasks)
            is_completed: Whether task is completed
        
        Returns:
            Task ID if successful, None otherwise
        """
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            task_id = BaseRepository.get_lastrowid(
                """
                INSERT INTO tasks (name, tag, planned_duration_minutes, created_at, color, parent_id, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, tag, planned_duration_minutes, created_at, color, parent_id, is_completed)
            )
            
            if task_id:
                # Create tag if it doesn't exist
                tag_exists = BaseRepository.execute_query(
                    "SELECT name FROM tags WHERE name = ?",
                    (tag,),
                    fetch_one=True
                )
                
                if not tag_exists:
                    BaseRepository.execute_query(
                        "INSERT INTO tags (name, color, created_at) VALUES (?, ?, ?)",
                        (tag, color, created_at),
                        commit=True
                    )
                
                return task_id
        except Exception as e:
            print(f"Task creation error: {e}")
        
        return None
    
    @staticmethod
    def update_task(
        task_id: int,
        name: Optional[str] = None,
        tag: Optional[str] = None,
        planned_duration_minutes: Optional[int] = None,
        color: Optional[str] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[int] = None,
        is_completed: Optional[bool] = None
    ) -> bool:
        """
        Update task fields (selective update).
        
        Args:
            task_id: Task ID to update
            name: New task name
            tag: New task tag
            planned_duration_minutes: New planned duration
            color: New task color
            is_active: Active status
            parent_id: New parent task ID
            is_completed: Completion status
        
        Returns:
            True if successful, False otherwise
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if tag is not None:
            updates.append("tag = ?")
            params.append(tag)
        if planned_duration_minutes is not None:
            updates.append("planned_duration_minutes = ?")
            params.append(planned_duration_minutes)
        if color is not None:
            updates.append("color = ?")
            params.append(color)
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(is_active)
        if parent_id is not None:
            updates.append("parent_id = ?")
            params.append(parent_id)
        if is_completed is not None:
            updates.append("is_completed = ?")
            params.append(is_completed)
        
        if not updates:
            return False
        
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        
        return BaseRepository.execute_query(query, tuple(params), commit=True) is not None
    
    @staticmethod
    def get_task_by_id(task_id: int) -> Optional['Task']:
        """
        Get a single task by ID.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task object or None
        """
        from mfdp_app.models.data_models import Task
        
        row = BaseRepository.execute_query(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
            fetch_one=True
        )
        
        if row:
            return Task(
                id=row['id'],
                name=row['name'],
                tag=row['tag'],
                planned_duration_minutes=row['planned_duration_minutes'],
                created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                is_active=bool(row['is_active']),
                color=row['color'],
                parent_id=row['parent_id'] if row['parent_id'] else None,
                is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
            )
        
        return None
    
    @staticmethod
    def get_all_tasks(include_inactive: bool = False) -> List['Task']:
        """
        Get all tasks.
        
        Args:
            include_inactive: Include inactive tasks
        
        Returns:
            List of Task objects
        """
        from mfdp_app.models.data_models import Task
        
        if include_inactive:
            query = "SELECT * FROM tasks ORDER BY created_at DESC"
            params = ()
        else:
            query = "SELECT * FROM tasks WHERE is_active = 1 ORDER BY created_at DESC"
            params = ()
        
        rows = BaseRepository.execute_query(query, params, fetch_all=True)
        
        tasks = []
        if rows:
            for row in rows:
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        
        return tasks
    
    @staticmethod
    def get_tasks_by_tag(tag: str) -> List['Task']:
        """
        Get all active tasks with specific tag.
        
        Args:
            tag: Tag name
        
        Returns:
            List of Task objects
        """
        from mfdp_app.models.data_models import Task
        
        rows = BaseRepository.execute_query(
            "SELECT * FROM tasks WHERE tag = ? AND is_active = 1 ORDER BY created_at DESC",
            (tag,),
            fetch_all=True
        )
        
        tasks = []
        if rows:
            for row in rows:
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        
        return tasks
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Soft delete a task (set is_active=False).
        
        Args:
            task_id: Task ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        return TaskRepository.update_task(task_id, is_active=False)
    
    @staticmethod
    def get_task_time_summary(task_id: int, days: Optional[int] = None) -> float:
        """
        Get total session time for a task in minutes.
        
        Args:
            task_id: Task ID
            days: Optional filter for last N days
        
        Returns:
            Total minutes
        """
        task = TaskRepository.get_task_by_id(task_id)
        if not task:
            return 0.0
        
        if days:
            query = """
                SELECT SUM(duration_seconds) / 60.0 as total_minutes
                FROM sessions_v2
                WHERE task_name = ?
                AND (mode = 'Focus' OR mode = 'Free Timer')
                AND start_time >= date('now', ?, 'localtime')
            """
            params = (task.name, f'-{days} days')
        else:
            query = """
                SELECT SUM(duration_seconds) / 60.0 as total_minutes
                FROM sessions_v2
                WHERE task_name = ?
                AND (mode = 'Focus' OR mode = 'Free Timer')
            """
            params = (task.name,)
        
        row = BaseRepository.execute_query(query, params, fetch_one=True)
        
        return float(row['total_minutes']) if row and row['total_minutes'] else 0.0
    
    # --- RECURSIVE TASK METHODS ---
    
    @staticmethod
    def get_child_tasks(parent_id: int) -> List['Task']:
        """
        Get direct children of a task.
        
        Args:
            parent_id: Parent task ID
        
        Returns:
            List of Task objects
        """
        from mfdp_app.models.data_models import Task
        
        rows = BaseRepository.execute_query(
            "SELECT * FROM tasks WHERE parent_id = ? AND is_active = 1 ORDER BY created_at ASC",
            (parent_id,),
            fetch_all=True
        )
        
        tasks = []
        if rows:
            for row in rows:
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        
        return tasks
    
    @staticmethod
    def get_root_tasks() -> List['Task']:
        """
        Get all root-level tasks (parent_id IS NULL).
        
        Returns:
            List of Task objects
        """
        from mfdp_app.models.data_models import Task
        
        rows = BaseRepository.execute_query(
            "SELECT * FROM tasks WHERE parent_id IS NULL AND is_active = 1 ORDER BY created_at ASC",
            fetch_all=True
        )
        
        tasks = []
        if rows:
            for row in rows:
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        
        return tasks
    
    @staticmethod
    def get_all_subtasks_recursive(task_id: int) -> List['Task']:
        """
        Get all descendants of a task recursively.
        
        Args:
            task_id: Task ID
        
        Returns:
            List of all Task objects in the subtree
        """
        all_subtasks = []
        direct_children = TaskRepository.get_child_tasks(task_id)
        all_subtasks.extend(direct_children)
        
        for child in direct_children:
            all_subtasks.extend(TaskRepository.get_all_subtasks_recursive(child.id))
        
        return all_subtasks
