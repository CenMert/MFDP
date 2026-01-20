"""
Tag Repository - manages task categories/tags.
"""

import datetime
from typing import List, Dict, Optional, Tuple

from mfdp_app.db.base_repository import BaseRepository


class TagRepository(BaseRepository):
    """Handle all tag-related database operations."""
    
    @staticmethod
    def get_all_tags() -> List[Dict[str, Optional[str]]]:
        """
        Get all distinct tags.
        
        Returns:
            List of dicts with 'name' and 'color' keys
        """
        rows = BaseRepository.execute_query(
            "SELECT DISTINCT name, color FROM tags ORDER BY name",
            fetch_all=True
        )
        
        tags = []
        if rows:
            for row in rows:
                tags.append({
                    'name': row['name'],
                    'color': row['color']
                })
        
        return tags
    
    @staticmethod
    def get_tag(tag_name: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Get a specific tag by name.
        
        Args:
            tag_name: Tag name
        
        Returns:
            Tag dictionary or None
        """
        row = BaseRepository.execute_query(
            "SELECT * FROM tags WHERE name = ?",
            (tag_name,),
            fetch_one=True
        )
        
        if row:
            return {
                'name': row['name'],
                'color': row['color'],
                'created_at': row['created_at']
            }
        return None
    
    @staticmethod
    def create_tag(name: str, color: Optional[str] = None) -> bool:
        """
        Create a new tag.
        
        Args:
            name: Tag name
            color: Tag color (optional)
        
        Returns:
            True if successful, False otherwise
        """
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return BaseRepository.execute_query(
            "INSERT OR IGNORE INTO tags (name, color, created_at) VALUES (?, ?, ?)",
            (name, color, created_at),
            commit=True
        ) is not None
    
    @staticmethod
    def assign_color_to_tag(tag: str, color: str) -> bool:
        """
        Assign or update color for a tag and sync to tasks.
        
        Args:
            tag: Tag name
            color: Color value
        
        Returns:
            True if successful, False otherwise
        """
        operations = [
            # Update or insert tag color
            ("INSERT OR REPLACE INTO tags (name, color, created_at) VALUES (?, ?, ?)",
             (tag, color, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
            # Sync color to tasks with this tag
            ("UPDATE tasks SET color = ? WHERE tag = ?",
             (color, tag))
        ]
        
        return BaseRepository.execute_transaction(operations, f"Color assigned to tag '{tag}'")
    
    @staticmethod
    def get_tag_time_summary(tag: str, days: Optional[int] = None) -> float:
        """
        Get total session time for a tag in minutes (Focus and Free Timer modes only).
        
        Args:
            tag: Tag name
            days: Optional filter for last N days
        
        Returns:
            Total minutes
        """
        if days:
            query = """
                SELECT SUM(duration_seconds) / 60.0 as total_minutes
                FROM sessions_v2
                WHERE category = ?
                AND (mode = 'Focus' OR mode = 'Free Timer')
                AND start_time >= date('now', ?, 'localtime')
            """
            params = (tag, f'-{days} days')
        else:
            query = """
                SELECT SUM(duration_seconds) / 60.0 as total_minutes
                FROM sessions_v2
                WHERE category = ?
                AND (mode = 'Focus' OR mode = 'Free Timer')
            """
            params = (tag,)
        
        row = BaseRepository.execute_query(query, params, fetch_one=True)
        
        return float(row['total_minutes']) if row and row['total_minutes'] else 0.0
    
    @staticmethod
    def get_daily_trend_by_tag(tag: str, days: int = 7) -> List[Tuple[str, int]]:
        """
        Get daily productivity trend for a tag (Focus and Free Timer modes only).
        
        Args:
            tag: Tag name
            days: Number of days to retrieve
        
        Returns:
            List of (date_label, minutes) tuples
        """
        rows = BaseRepository.execute_query(
            """
            SELECT strftime('%Y-%m-%d', start_time) as day,
                   SUM(duration_seconds) / 60 as minutes
            FROM sessions_v2
            WHERE category = ?
            AND (mode = 'Focus' OR mode = 'Free Timer')
            AND start_time >= date('now', ?, 'localtime')
            GROUP BY day
            ORDER BY day ASC
            """,
            (tag, f'-{days-1} days'),
            fetch_all=True
        )
        
        data = []
        if rows:
            db_data = {row['day']: row['minutes'] for row in rows}
            
            for i in range(days - 1, -1, -1):
                date_calc = datetime.date.today() - datetime.timedelta(days=i)
                date_str = date_calc.strftime('%Y-%m-%d')
                minutes = db_data.get(date_str, 0)
                display_date = date_calc.strftime('%d %b')
                data.append((display_date, minutes))
        
        return data
    
    @staticmethod
    def delete_tag(tag_name: str) -> bool:
        """
        Delete a tag. Note: tasks using this tag will keep it, but orphaned.
        
        Args:
            tag_name: Tag name to delete
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM tags WHERE name = ?",
            (tag_name,),
            commit=True
        ) is not None
    
    @staticmethod
    def get_tags_with_task_counts() -> List[Dict]:
        """
        Get all tags with count of associated tasks.
        
        Returns:
            List of dicts with 'name', 'color', and 'task_count'
        """
        rows = BaseRepository.execute_query(
            """
            SELECT DISTINCT t.name, t.color, COUNT(tk.id) as task_count
            FROM tags t
            LEFT JOIN tasks tk ON t.name = tk.tag AND tk.is_active = 1
            GROUP BY t.name
            ORDER BY t.name
            """,
            fetch_all=True
        )
        
        tags = []
        if rows:
            for row in rows:
                tags.append({
                    'name': row['name'],
                    'color': row['color'],
                    'task_count': row['task_count']
                })
        
        return tags
