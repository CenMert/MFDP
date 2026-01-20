"""
Atomic Event Repository - manages low-level event sourcing for sessions.
Stores raw events for fine-grained analysis and auditing.
"""

import datetime
import json
from typing import List, Dict, Optional, Tuple

from mfdp_app.db.base_repository import BaseRepository


class AtomicEventRepository(BaseRepository):
    """Handle all atomic event operations (event sourcing)."""
    
    @staticmethod
    def insert_events(events_data: List[Dict]) -> bool:
        """
        Batch insert atomic events into database.
        Used by AtomicAnalyzer to persist raw events for later analysis.
        
        Args:
            events_data: List of event dictionaries with format:
                {
                    'event_type': 'interruption_detected',
                    'session_id': 123,
                    'elapsed_seconds': 180,
                    'timestamp': '2025-01-18T10:30:45.123456',
                    'metadata': {...}
                }
        
        Returns:
            True if successful, False otherwise
        """
        if not events_data:
            return True
        
        operations = []
        
        for event in events_data:
            # Convert metadata dict to JSON string
            metadata_json = json.dumps(event.get('metadata', {})) if event.get('metadata') else None
            
            operations.append((
                """
                INSERT INTO atomic_events
                (session_id, event_type, timestamp, elapsed_seconds, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    event['session_id'],
                    event['event_type'],
                    event['timestamp'],
                    event['elapsed_seconds'],
                    metadata_json
                )
            ))
        
        success = BaseRepository.execute_transaction(
            operations,
            f"Inserted {len(events_data)} atomic events"
        )
        
        return success
    
    @staticmethod
    def get_events(session_id: int) -> List[Dict]:
        """
        Get all atomic events for a session in chronological order.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of event dictionaries
        """
        rows = BaseRepository.execute_query(
            """
            SELECT id, session_id, event_type, elapsed_seconds, timestamp, metadata, created_at
            FROM atomic_events
            WHERE session_id = ?
            ORDER BY elapsed_seconds ASC, id ASC
            """,
            (session_id,),
            fetch_all=True
        )
        
        events = []
        if rows:
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                events.append({
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'event_type': row['event_type'],
                    'elapsed_seconds': row['elapsed_seconds'],
                    'timestamp': row['timestamp'],
                    'metadata': metadata,
                    'created_at': row['created_at']
                })
        
        return events
    
    @staticmethod
    def get_events_by_range(
        start_date: datetime.datetime,
        end_date: datetime.datetime
    ) -> List[Dict]:
        """
        Get all atomic events within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
        
        Returns:
            List of event dictionaries
        """
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        rows = BaseRepository.execute_query(
            """
            SELECT id, session_id, event_type, elapsed_seconds, timestamp, metadata, created_at
            FROM atomic_events
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC, id ASC
            """,
            (start_str, end_str),
            fetch_all=True
        )
        
        events = []
        if rows:
            for row in rows:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                
                events.append({
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'event_type': row['event_type'],
                    'elapsed_seconds': row['elapsed_seconds'],
                    'timestamp': row['timestamp'],
                    'metadata': metadata,
                    'created_at': row['created_at']
                })
        
        return events
    
    @staticmethod
    def get_interruption_events(session_id: int) -> List[Dict]:
        """
        Get interruption detection events for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of interruption event dictionaries
        """
        all_events = AtomicEventRepository.get_events(session_id)
        return [e for e in all_events if e['event_type'] == 'interruption_detected']
    
    @staticmethod
    def get_focus_shift_events(session_id: int) -> List[Dict]:
        """
        Get focus shift detection events for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of focus shift event dictionaries
        """
        all_events = AtomicEventRepository.get_events(session_id)
        return [e for e in all_events if e['event_type'] == 'focus_shift_detected']
    
    @staticmethod
    def get_distraction_events(session_id: int) -> List[Dict]:
        """
        Get distraction identification events for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of distraction event dictionaries
        """
        all_events = AtomicEventRepository.get_events(session_id)
        return [e for e in all_events if e['event_type'] == 'distraction_identified']
    
    @staticmethod
    def get_event_statistics(session_id: int) -> Dict:
        """
        Get aggregated event statistics for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Statistics dictionary with event type counts
        """
        events = AtomicEventRepository.get_events(session_id)
        
        stats = {
            'total_events': len(events),
            'interruptions': 0,
            'focus_shifts': 0,
            'distractions': 0,
            'environment_changes': 0,
            'breaks': 0,
            'event_types': {}
        }
        
        for event in events:
            event_type = event['event_type']
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
            
            if event_type == 'interruption_detected':
                stats['interruptions'] += 1
            elif event_type == 'focus_shift_detected':
                stats['focus_shifts'] += 1
            elif event_type == 'distraction_identified':
                stats['distractions'] += 1
            elif event_type == 'environment_changed':
                stats['environment_changes'] += 1
            elif event_type in ('break_started', 'break_ended'):
                stats['breaks'] += 1
        
        return stats
    
    @staticmethod
    def get_heatmap(
        days: int = 14,
        event_types: Optional[List[str]] = None
    ) -> Tuple[List[str], List[List[int]]]:
        """
        Get atomic events heatmap (day x hour matrix).
        
        Args:
            days: Number of days back from today (inclusive)
            event_types: Optional filter for specific event types
        
        Returns:
            Tuple of (day_labels, matrix) where matrix[day][hour] = event_count
        """
        # Build date range
        day_dates = [
            datetime.date.today() - datetime.timedelta(days=i)
            for i in range(days-1, -1, -1)
        ]
        day_map = {d.strftime('%Y-%m-%d'): idx for idx, d in enumerate(day_dates)}
        matrix = [[0 for _ in range(24)] for _ in range(days)]
        
        # Build query with optional event type filter
        params = [f'-{days-1} days']
        event_filter = ""
        if event_types:
            placeholders = ",".join(["?"] * len(event_types))
            event_filter = f"AND event_type IN ({placeholders})"
            params.extend(event_types)
        
        query = f"""
            SELECT strftime('%Y-%m-%d', timestamp) AS day,
                   CAST(strftime('%H', timestamp) AS INTEGER) AS hour,
                   COUNT(*) AS cnt
            FROM atomic_events
            WHERE timestamp >= date('now', ?, 'localtime')
            {event_filter}
            GROUP BY day, hour
            ORDER BY day ASC, hour ASC
        """
        
        rows = BaseRepository.execute_query(query, tuple(params), fetch_all=True)
        
        if rows:
            for row in rows:
                day_key = row['day']
                hour = row['hour']
                if day_key in day_map and 0 <= hour <= 23:
                    matrix[day_map[day_key]][hour] = row['cnt']
        
        day_labels = [d.strftime('%d %b') for d in day_dates]
        return day_labels, matrix
    
    @staticmethod
    def delete_events_for_session(session_id: int) -> bool:
        """
        Delete all atomic events for a session (cascade delete).
        
        Args:
            session_id: Session ID
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM atomic_events WHERE session_id = ?",
            (session_id,),
            commit=True
        ) is not None
    
    @staticmethod
    def delete_events_by_range(
        start_date: datetime.datetime,
        end_date: datetime.datetime
    ) -> bool:
        """
        Delete all atomic events within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
        
        Returns:
            True if successful, False otherwise
        """
        return BaseRepository.execute_query(
            "DELETE FROM atomic_events WHERE timestamp >= ? AND timestamp <= ?",
            (start_date.isoformat(), end_date.isoformat()),
            commit=True
        ) is not None
