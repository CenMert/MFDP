# AtomicAnalyzer Integration Guide

This document explains how to integrate `AtomicAnalyzer` with your existing MFDP codebase.

## Database Setup ✅

The database schema has been updated with:

```sql
-- atomic_events table created in db_manager.py
CREATE TABLE IF NOT EXISTS atomic_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    elapsed_seconds INTEGER NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions_v2(id) ON DELETE CASCADE
);

-- Indexes for fast queries
CREATE INDEX idx_atomic_events_session_id
CREATE INDEX idx_atomic_events_event_type
CREATE INDEX idx_atomic_events_timestamp
CREATE INDEX idx_atomic_events_elapsed_seconds
```

## New Database Functions

Added to `db_manager.py`:

- `insert_atomic_events(events_data)` - Batch insert events
- `get_atomic_events(session_id)` - Retrieve all events for a session
- `get_atomic_events_by_range(start_date, end_date)` - Get events by time period
- `get_interruption_events(session_id)` - Filter interruption events
- `get_focus_shift_events(session_id)` - Filter focus shift events
- `get_distraction_events(session_id)` - Filter distraction events
- `delete_atomic_events_for_session(session_id)` - Clean up events
- `get_event_statistics_for_session(session_id)` - Get event counts by type

## Integration Points

### 1. **main_window.py** - Initialize AtomicAnalyzer

```python
from mfdp_app.core.atomic_analyzer import AtomicAnalyzer

class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing code ...
        self.db_manager = DatabaseManager()
        
        # Initialize AtomicAnalyzer
        self.analyzer = AtomicAnalyzer(self.db_manager)
        
        # Pass to timer and other components
        self.timer = PomodoroTimer(self.db_manager, analyzer=self.analyzer)
        self.system_monitor = SystemMonitor(analyzer=self.analyzer)
        self.dnd_manager = DNDManager(analyzer=self.analyzer)
```

### 2. **timer.py** - Record Session Events

```python
from mfdp_app.core.atomic_analyzer import InterruptionSeverity

class PomodoroTimer(QObject):
    def __init__(self, db_manager, analyzer=None):
        self.db_manager = db_manager
        self.analyzer = analyzer
        self.session_id = None
    
    def start(self):
        # Create session in database
        self.session_id = self.db_manager.log_session_v2(...)
        
        # Notify analyzer
        if self.analyzer:
            self.analyzer.start_session(
                session_id=self.session_id,
                planned_duration=self.duration,
                session_type="pomodoro"
            )
    
    def pause(self):
        if self.analyzer:
            self.analyzer.record_interruption(
                reason="user_pause",
                severity=InterruptionSeverity.LOW
            )
    
    def resume(self):
        if self.analyzer:
            self.analyzer.resume_session()
    
    def finish(self):
        if self.analyzer:
            self.analyzer.complete_session(
                actual_duration=self.elapsed_time,
                completed_by="timer"
            )
        
        # Flush events to database
        if self.analyzer:
            self.analyzer.flush_events()
```

### 3. **system_monitor.py** - Record Focus Shifts

```python
class SystemMonitor(QObject):
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.last_app = None
        self.last_app_start_time = None
    
    def on_window_changed(self, new_app):
        if self.analyzer and self.analyzer.current_session_id:
            focus_duration = self._calculate_duration(self.last_app_start_time)
            
            self.analyzer.record_focus_shift(
                from_app=self.last_app,
                to_app=new_app,
                focus_duration=focus_duration
            )
        
        self.last_app = new_app
        self.last_app_start_time = datetime.now()
    
    def on_distraction_detected(self, distraction_type, app_name=None):
        if self.analyzer and self.analyzer.current_session_id:
            self.analyzer.record_distraction(
                distraction_type=distraction_type,
                app_name=app_name,
                severity=InterruptionSeverity.MEDIUM
            )
```

### 4. **dnd_manager.py** - Record Environment Changes

```python
class DNDManager(QObject):
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
        self.is_enabled = False
    
    def toggle_dnd(self, enabled):
        self.is_enabled = enabled
        
        if self.analyzer and self.analyzer.current_session_id:
            self.analyzer.record_dnd_toggle(enabled)
    
    def notify_environment_change(self, factor_type, value):
        if self.analyzer and self.analyzer.current_session_id:
            self.analyzer.record_environment_change(factor_type, value)
```

## Usage Example

```python
from mfdp_app.core.atomic_analyzer import AtomicAnalyzer, InterruptionSeverity

# Initialize
analyzer = AtomicAnalyzer(db_manager)

# Start a session
analyzer.start_session(
    session_id=123,
    planned_duration=1800,  # 30 minutes
    session_type="pomodoro"
)

# During session - record events
analyzer.record_interruption(
    reason="slack_notification",
    severity=InterruptionSeverity.MEDIUM
)

analyzer.record_focus_shift(
    from_app="VSCode",
    to_app="Chrome",
    focus_duration=300
)

# End of session
analyzer.complete_session(
    actual_duration=1200,  # Actually 20 minutes
    completed_by="user"
)

# Flush to database
analyzer.flush_events()

# Retrieve and analyze
events = analyzer.get_session_events(123)
interruptions = analyzer.get_interruption_pattern(123)
print(f"Interruptions: {interruptions['total_interruptions']}")
print(f"First interruption at: {interruptions['first_interruption_at']}s")
```

## Event Types

The `EventType` enum includes:

- **SESSION_STARTED** - Session begins
- **SESSION_RESUMED** - Paused session resumed
- **SESSION_PAUSED** - User paused
- **SESSION_COMPLETED** - Session finished successfully
- **SESSION_ABANDONED** - Session quit early
- **INTERRUPTION_DETECTED** - User interrupted (with severity)
- **FOCUS_SHIFT_DETECTED** - App/window switched
- **DISTRACTION_IDENTIFIED** - Specific distraction noted
- **DND_TOGGLED** - Do-Not-Disturb toggled
- **ENVIRONMENT_CHANGED** - Environmental factor changed
- **MILESTONE_REACHED** - 25%, 50%, 75%, 100% completion
- **BREAK_STARTED** / **BREAK_ENDED** - Break periods

## Data Flow

```
User Action
    ↓
Timer/SystemMonitor Component
    ↓
analyzer.record_* method
    ↓
Event buffered in memory (AUTO_FLUSH_THRESHOLD = 50)
    ↓
analyzer.flush_events() or auto-flush triggered
    ↓
insert_atomic_events() in db_manager.py
    ↓
atomic_events TABLE in SQLite
    ↓
get_atomic_events() for analysis
    ↓
Visualization/Reporting
```

## Next Steps

1. **Phase 2**: Create `session_analysis` table for derived metrics
2. **Phase 3**: Build analysis window with charts
3. **Phase 4**: ML models for personalized recommendations

## Notes

- Events are **immutable** - stored as-is, never modified
- **Metadata is flexible** - JSON format allows any additional data
- **Batch operations** - Events are flushed in batches for performance
- **No data loss** - All raw events preserved for future analysis
- **Indexing** - Queries optimized with proper database indexes
