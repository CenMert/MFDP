"""
Session Repository - manages focus/timer sessions and analytics.
"""

import datetime
from typing import List, Dict, Tuple, Optional

from mfdp_app.db.base_repository import BaseRepository


class SessionRepository(BaseRepository):
    """Handle all session-related database operations and analytics."""
    
    @staticmethod
    def log_session(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        duration_seconds: int,
        planned_duration_minutes: Optional[int],
        mode: str,
        completed: bool,
        task_name: Optional[str] = None,
        category: Optional[str] = None,
        interruption_count: int = 0
    ) -> Optional[int]:
        """
        Log a focus/timer session.
        
        Args:
            start_time: Session start time
            end_time: Session end time
            duration_seconds: Actual duration in seconds
            planned_duration_minutes: Planned duration in minutes
            mode: Session mode ('Focus' or 'Free Timer')
            completed: Whether session was completed
            task_name: Associated task name
            category: Session category/tag
            interruption_count: Number of interruptions
        
        Returns:
            Session ID if successful, None otherwise
        """
        session_id = BaseRepository.get_lastrowid(
            """
            INSERT INTO sessions_v2 (
                start_time, end_time, duration_seconds,
                planned_duration_minutes, mode, completed,
                task_name, category, interruption_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                duration_seconds,
                planned_duration_minutes,
                mode,
                completed,
                task_name,
                category,
                interruption_count
            )
        )
        
        if session_id:
            print(f"💾 Session logged: {mode} ({duration_seconds}s, {interruption_count} interruptions)")
        
        return session_id
    
    @staticmethod
    def get_session(session_id: int) -> Optional[Dict]:
        """
        Get a single session by ID.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data dictionary or None
        """
        row = BaseRepository.execute_query(
            "SELECT * FROM sessions_v2 WHERE id = ?",
            (session_id,),
            fetch_one=True
        )
        
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def get_all_sessions(limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """
        Get all sessions with optional pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
        
        Returns:
            List of session dictionaries
        """
        query = "SELECT * FROM sessions_v2 ORDER BY start_time DESC"
        params = ()
        
        if limit:
            query += " LIMIT ? OFFSET ?"
            params = (limit, offset)
        
        rows = BaseRepository.execute_query(query, params, fetch_all=True)
        
        if rows:
            return [dict(row) for row in rows]
        return []
    
    @staticmethod
    def get_daily_trend(days: int = 7) -> List[Tuple[str, int]]:
        """
        Get daily productivity trend for last N days (Focus and Free Timer modes only).
        
        Args:
            days: Number of days to retrieve
        
        Returns:
            List of (date_label, minutes) tuples
        """
        rows = BaseRepository.execute_query(
            """
            SELECT strftime('%Y-%m-%d', start_time) as day,
                   SUM(duration_seconds) / 60 as minutes
            FROM sessions_v2
            WHERE (mode = 'Focus' OR mode = 'Free Timer')
            AND start_time >= date('now', ?, 'localtime')
            GROUP BY day
            ORDER BY day ASC
            """,
            (f'-{days-1} days',),
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
    def get_hourly_productivity() -> List[int]:
        """
        Get hourly productivity aggregation (Focus and Free Timer modes only).
        
        Returns:
            List of 24 integers representing minutes per hour (0-23)
        """
        hours_data = [0] * 24
        
        rows = BaseRepository.execute_query(
            """
            SELECT strftime('%H', start_time) as hour,
                   SUM(duration_seconds) / 60 as minutes
            FROM sessions_v2
            WHERE mode = 'Focus' OR mode = 'Free Timer'
            GROUP BY hour
            """,
            fetch_all=True
        )
        
        if rows:
            for row in rows:
                hour_idx = int(row['hour'])
                hours_data[hour_idx] = int(row['minutes'])
        
        return hours_data
    
    @staticmethod
    def get_completion_rate() -> Dict[str, int]:
        """
        Get session completion statistics (Focus and Free Timer modes only).
        
        Returns:
            Dictionary with 'completed' and 'interrupted' counts
        """
        stats = {'completed': 0, 'interrupted': 0}
        
        rows = BaseRepository.execute_query(
            """
            SELECT completed, COUNT(*) as count
            FROM sessions_v2
            WHERE mode = 'Focus' OR mode = 'Free Timer'
            GROUP BY completed
            """,
            fetch_all=True
        )
        
        if rows:
            for row in rows:
                if row['completed'] == 1:
                    stats['completed'] = row['count']
                else:
                    stats['interrupted'] = row['count']
        
        return stats
    
    @staticmethod
    def get_focus_quality_stats() -> Dict[str, int]:
        """
        Get focus quality statistics based on interruption counts.
        Groups sessions into Deep Work, Moderate, and Distracted categories.
        
        Returns:
            Dictionary with focus quality counts
        """
        stats = {
            'Deep Work (0 Kesinti)': 0,
            'Moderate (1-2 Kesinti)': 0,
            'Distracted (3+ Kesinti)': 0
        }
        
        rows = BaseRepository.execute_query(
            """
            SELECT interruption_count, COUNT(*) as count
            FROM sessions_v2
            WHERE mode = 'Focus' OR mode = 'Free Timer'
            GROUP BY interruption_count
            """,
            fetch_all=True
        )
        
        if rows:
            for row in rows:
                count = row['interruption_count']
                qty = row['count']
                
                if count == 0:
                    stats['Deep Work (0 Kesinti)'] += qty
                elif count <= 2:
                    stats['Moderate (1-2 Kesinti)'] += qty
                else:
                    stats['Distracted (3+ Kesinti)'] += qty
        
        return stats
    
    @staticmethod
    def get_sessions_by_task(task_name: str) -> List[Dict]:
        """
        Get all sessions associated with a specific task.
        
        Args:
            task_name: Name of the task
        
        Returns:
            List of session dictionaries
        """
        rows = BaseRepository.execute_query(
            "SELECT * FROM sessions_v2 WHERE task_name = ? ORDER BY start_time DESC",
            (task_name,),
            fetch_all=True
        )
        
        if rows:
            return [dict(row) for row in rows]
        return []
    
    @staticmethod
    def get_sessions_by_category(category: str, days: Optional[int] = None) -> List[Dict]:
        """
        Get sessions by category (tag).
        
        Args:
            category: Category/tag name
            days: Optional filter for last N days
        
        Returns:
            List of session dictionaries
        """
        if days:
            query = """
                SELECT * FROM sessions_v2
                WHERE category = ?
                AND start_time >= date('now', ?, 'localtime')
                ORDER BY start_time DESC
            """
            params = (category, f'-{days} days')
        else:
            query = "SELECT * FROM sessions_v2 WHERE category = ? ORDER BY start_time DESC"
            params = (category,)
        
        rows = BaseRepository.execute_query(query, params, fetch_all=True)
        
        if rows:
            return [dict(row) for row in rows]
        return []
    
    @staticmethod
    def delete_session(session_id: int) -> bool:
        """
        Delete a session. Associated atomic events will cascade delete.
        
        Args:
            session_id: Session ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM sessions_v2 WHERE id = ?",
            (session_id,),
            commit=True
        ) is not None
