"""
Database Manager - Unified facade for all database operations.
This module provides backward compatibility by exposing all repository methods
through a single interface. Internally, it delegates to specialized repositories.

Architecture:
- BaseRepository: Connection pooling and common query operations
- DatabaseInitializer: Schema management
- SettingsRepository: Key-value settings
- SessionRepository: Focus/timer sessions and analytics
- TaskRepository: Task CRUD and hierarchies
- TagRepository: Category/tag management
- AtomicEventRepository: Event sourcing
"""

from mfdp_app.db.base_repository import initialize_database, BaseRepository
from mfdp_app.db.database_initializer import DatabaseInitializer
from mfdp_app.db.settings_repository import SettingsRepository
from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.task_repository import TaskRepository
from mfdp_app.db.tag_repository import TagRepository
from mfdp_app.db.atomic_event_repository import AtomicEventRepository

# --- INITIALIZATION ---

DB_NAME = 'focus_tracker.db'


def setup_database():
    """Initialize database schema. Call this at application startup."""
    BaseRepository.initialize_pool(pool_size=5)
    return DatabaseInitializer.setup_database()


def verify_schema():
    """Verify that all required tables exist."""
    return DatabaseInitializer.verify_schema()


# --- SETTINGS (Forwarded to SettingsRepository) ---

def load_settings():
    """Load all application settings."""
    return SettingsRepository.load_settings()


def get_setting(key, default=None):
    """Get a single setting by key."""
    return SettingsRepository.get_setting(key, default)


def save_setting(key, value):
    """Save or update a setting."""
    return SettingsRepository.save_setting(key, value)


def delete_setting(key):
    """Delete a setting by key."""
    return SettingsRepository.delete_setting(key)


# --- SESSIONS (Forwarded to SessionRepository) ---

def log_session_v2(start_time, end_time, duration_sec, planned_min, mode, completed, task_name=None, category=None, interruption_count=0):
    """Log a focus/timer session."""
    return SessionRepository.log_session(
        start_time, end_time, duration_sec, planned_min,
        mode, completed, task_name, category, interruption_count
    )


def get_session(session_id):
    """Get a single session by ID."""
    return SessionRepository.get_session(session_id)


def get_all_sessions(limit=None, offset=0):
    """Get all sessions with optional pagination."""
    return SessionRepository.get_all_sessions(limit, offset)


def get_daily_trend_v2(days=7):
    """Get daily productivity trend."""
    return SessionRepository.get_daily_trend(days)


def get_hourly_productivity_v2():
    """Get hourly productivity aggregation."""
    return SessionRepository.get_hourly_productivity()


def get_completion_rate_v2():
    """Get session completion statistics."""
    return SessionRepository.get_completion_rate()


def get_focus_quality_stats():
    """Get focus quality statistics by interruption count."""
    return SessionRepository.get_focus_quality_stats()


def get_sessions_by_task(task_name):
    """Get all sessions for a specific task."""
    return SessionRepository.get_sessions_by_task(task_name)


def get_sessions_by_category(category, days=None):
    """Get sessions by category/tag."""
    return SessionRepository.get_sessions_by_category(category, days)


def delete_session(session_id):
    """Delete a session."""
    return SessionRepository.delete_session(session_id)


# --- TASKS (Forwarded to TaskRepository) ---

def insert_task(name, tag, planned_duration_minutes=None, color=None, parent_id=None, is_completed=False):
    """Create a new task."""
    return TaskRepository.insert_task(name, tag, planned_duration_minutes, color, parent_id, is_completed)


def update_task(task_id, name=None, tag=None, planned_duration_minutes=None, color=None, is_active=None, parent_id=None, is_completed=None):
    """Update task fields."""
    return TaskRepository.update_task(task_id, name, tag, planned_duration_minutes, color, is_active, parent_id, is_completed)


def get_task_by_id(task_id):
    """Get a single task by ID."""
    return TaskRepository.get_task_by_id(task_id)


def get_all_tasks(include_inactive=False):
    """Get all tasks."""
    return TaskRepository.get_all_tasks(include_inactive)


def get_tasks_by_tag(tag):
    """Get all active tasks with specific tag."""
    return TaskRepository.get_tasks_by_tag(tag)


def delete_task(task_id):
    """Soft delete a task."""
    return TaskRepository.delete_task(task_id)


def get_task_time_summary(task_id, days=None):
    """Get total session time for a task."""
    return TaskRepository.get_task_time_summary(task_id, days)


# --- RECURSIVE TASKS (Forwarded to TaskRepository) ---

def get_child_tasks(parent_id):
    """Get direct children of a task."""
    return TaskRepository.get_child_tasks(parent_id)


def get_root_tasks():
    """Get all root-level tasks."""
    return TaskRepository.get_root_tasks()


def get_all_subtasks_recursive(task_id):
    """Get all descendants of a task recursively."""
    return TaskRepository.get_all_subtasks_recursive(task_id)


# --- TAGS (Forwarded to TagRepository) ---

def get_all_tags():
    """Get all distinct tags."""
    return TagRepository.get_all_tags()


def get_tag(tag_name):
    """Get a specific tag by name."""
    return TagRepository.get_tag(tag_name)


def create_tag(name, color=None):
    """Create a new tag."""
    return TagRepository.create_tag(name, color)


def assign_color_to_tag(tag, color):
    """Assign or update color for a tag."""
    return TagRepository.assign_color_to_tag(tag, color)


def get_tag_time_summary(tag, days=None):
    """Get total session time for a tag."""
    return TagRepository.get_tag_time_summary(tag, days)


def get_daily_trend_by_tag(tag, days=7):
    """Get daily productivity trend for a tag."""
    return TagRepository.get_daily_trend_by_tag(tag, days)


def delete_tag(tag_name):
    """Delete a tag."""
    return TagRepository.delete_tag(tag_name)


def get_tags_with_task_counts():
    """Get all tags with associated task counts."""
    return TagRepository.get_tags_with_task_counts()


# --- ATOMIC EVENTS (Forwarded to AtomicEventRepository) ---

def insert_atomic_events(events_data):
    """Batch insert atomic events."""
    return AtomicEventRepository.insert_events(events_data)


def get_atomic_events(session_id):
    """Get all atomic events for a session."""
    return AtomicEventRepository.get_events(session_id)


def get_atomic_events_by_range(start_date, end_date):
    """Get atomic events within a date range."""
    return AtomicEventRepository.get_events_by_range(start_date, end_date)


def get_interruption_events(session_id):
    """Get interruption detection events for a session."""
    return AtomicEventRepository.get_interruption_events(session_id)


def get_focus_shift_events(session_id):
    """Get focus shift detection events for a session."""
    return AtomicEventRepository.get_focus_shift_events(session_id)


def get_distraction_events(session_id):
    """Get distraction identification events for a session."""
    return AtomicEventRepository.get_distraction_events(session_id)


def get_event_statistics_for_session(session_id):
    """Get aggregated event statistics for a session."""
    return AtomicEventRepository.get_event_statistics(session_id)


def delete_atomic_events_for_session(session_id):
    """Delete all atomic events for a session."""
    return AtomicEventRepository.delete_events_for_session(session_id)


def get_atomic_event_heatmap(days=14, event_types=None):
    """Get atomic events heatmap."""
    return AtomicEventRepository.get_heatmap(days, event_types)
