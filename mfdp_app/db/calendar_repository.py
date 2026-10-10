"""
Calendar Repository - events (exams, homework, meetings) and date ranges.
Dates are stored as ISO strings (YYYY-MM-DD), so string comparison is date order.
"""

from typing import List, Dict, Optional

from mfdp_app.db.base_repository import BaseRepository


class CalendarRepository(BaseRepository):
    """Handle all calendar-related database operations."""

    @staticmethod
    def get_events_between(start_date: str, end_date: str) -> List[Dict]:
        rows = BaseRepository.execute_query(
            "SELECT id, title, date, time, kind, note FROM calendar_events "
            "WHERE date BETWEEN ? AND ? ORDER BY date, COALESCE(time, ''), id",
            (start_date, end_date),
            fetch_all=True
        )
        return [dict(r) for r in rows] if rows else []

    @staticmethod
    def add_event(title: str, date: str, kind: str = "diger",
                  time: Optional[str] = None, note: Optional[str] = None) -> Optional[int]:
        return BaseRepository.execute_query(
            "INSERT INTO calendar_events (title, date, time, kind, note) VALUES (?, ?, ?, ?, ?)",
            (title, date, time, kind, note),
            commit=True
        )

    @staticmethod
    def delete_event(event_id: int) -> bool:
        return BaseRepository.execute_query(
            "DELETE FROM calendar_events WHERE id = ?", (event_id,), commit=True
        ) is not None

    @staticmethod
    def get_ranges_overlapping(start_date: str, end_date: str) -> List[Dict]:
        rows = BaseRepository.execute_query(
            "SELECT id, label, start_date, end_date, color FROM calendar_ranges "
            "WHERE start_date <= ? AND end_date >= ? ORDER BY start_date, id",
            (end_date, start_date),
            fetch_all=True
        )
        return [dict(r) for r in rows] if rows else []

    @staticmethod
    def add_range(label: str, start_date: str, end_date: str,
                  color: Optional[str] = None) -> Optional[int]:
        return BaseRepository.execute_query(
            "INSERT INTO calendar_ranges (label, start_date, end_date, color) VALUES (?, ?, ?, ?)",
            (label, start_date, end_date, color),
            commit=True
        )

    @staticmethod
    def delete_range(range_id: int) -> bool:
        return BaseRepository.execute_query(
            "DELETE FROM calendar_ranges WHERE id = ?", (range_id,), commit=True
        ) is not None
