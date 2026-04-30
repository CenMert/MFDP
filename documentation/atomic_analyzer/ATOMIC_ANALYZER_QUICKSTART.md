# AtomicAnalyzer Quick Start Guide

Get up and running with AtomicAnalyzer in 5 minutes.

---

## What is AtomicAnalyzer?

AtomicAnalyzer captures **discrete events** that happen during focus sessions (interruptions, focus shifts, milestones) instead of just storing session summaries.

### Why? Three key benefits:

1. **Pattern Detection**: Identify when interruptions typically happen ("always interrupted at 5-min mark")
2. **Focus Capacity Analysis**: Understand your actual focus limits ("can't sustain 45-min sessions")
3. **Environmental Impact**: See what helps focus ("DND improves focus by 23%")

---

## Basic Usage

### 1. Initialize AtomicAnalyzer

```python
from mfdp_app.core.atomic_analyzer import AtomicAnalyzer

# In your main_window.py or initialization code
analyzer = AtomicAnalyzer(db_manager)
```

### 2. Record Session Lifecycle

```python
# When session starts
analyzer.start_session(
    session_id=123,              # from sessions_v2 table
    planned_duration=1800,       # 30 minutes in seconds
    session_type="pomodoro"      # or "flowtime", "custom"
)

# When user resumes after pause
analyzer.resume_session(app_context="VS Code")

# When session completes
analyzer.complete_session(
    actual_duration=1750,        # How long it actually ran
    completed_by="timer"         # or "user"
)

# When session is abandoned
analyzer.abandon_session(reason="user_quit")
```

### 3. Record Interruptions

```python
from mfdp_app.core.atomic_analyzer import InterruptionSeverity

# User got distracted
analyzer.record_interruption(
    reason="slack_notification",
    severity=InterruptionSeverity.MEDIUM,
    recovery_app="Slack"
)

# User manually paused
analyzer.record_interruption(
    reason="user_pause",
    severity=InterruptionSeverity.LOW
)

# Unexpected interruption
analyzer.record_interruption(
    reason="phone_call",
    severity=InterruptionSeverity.HIGH
)
```

### 4. Record Focus Shifts

```python
# When user switches apps/windows
analyzer.record_focus_shift(
    from_app="VS Code",
    to_app="Chrome",
    context="checking email"
)
```

### 5. Record Distractions

```python
# When a distraction is identified
analyzer.record_distraction(
    distraction_type="notification",
    source="Slack",
    severity="medium"
)
```

### 6. Record Milestones

```python
# Automatically tracked at 25%, 50%, 75%, 100%
# You can also manually record:
analyzer.record_milestone(
    percentage=50,
    notes="halfway there!"
)
```

### 7. Record Breaks

```python
# When break starts
analyzer.record_break_started(break_type="5min")

# When break ends
analyzer.record_break_ended()
```

### 8. Save to Database

```python
# Manually flush events (AtomicAnalyzer automatically flushes every 50 events)
analyzer.flush_events()
```

---

## Available Event Types

| Event | When to Use |
|-------|-----------|
| `SESSION_STARTED` | Session timer begins |
| `SESSION_RESUMED` | User resumes after pause |
| `SESSION_PAUSED` | User pauses timer |
| `SESSION_COMPLETED` | Session successfully finishes |
| `SESSION_ABANDONED` | User quits early |
| `INTERRUPTION_DETECTED` | User distracted/paused |
| `FOCUS_SHIFT_DETECTED` | App/window changed |
| `DISTRACTION_IDENTIFIED` | Notification/alert detected |
| `MILESTONE_REACHED` | 25%, 50%, 75%, 100% of session |
| `BREAK_STARTED` | Break period begins |
| `BREAK_ENDED` | Break period ends |
| `DND_TOGGLED` | Do Not Disturb toggled |
| `ENVIRONMENT_CHANGED` | Noise level, lighting, etc. |

---

## Severity Levels

```python
from mfdp_app.core.atomic_analyzer import InterruptionSeverity

InterruptionSeverity.LOW       # User paused, can resume easily
InterruptionSeverity.MEDIUM    # Context-switching required
InterruptionSeverity.HIGH      # Major distraction, full context loss
```

---

## Integration Points

### PomodoroTimer Integration

```python
class PomodoroTimer(QObject):
    def __init__(self, db_manager, analyzer=None):
        self.analyzer = analyzer
        self.session_id = None
    
    def start_session(self, duration):
        # Create session in DB
        self.session_id = self.db_manager.log_session_v2(...)
        
        # Notify analyzer
        if self.analyzer:
            self.analyzer.start_session(self.session_id, duration)
    
    def pause_session(self):
        if self.analyzer:
            self.analyzer.record_interruption(
                reason="user_pause",
                severity=InterruptionSeverity.LOW
            )
    
    def finish_session(self):
        if self.analyzer:
            self.analyzer.complete_session(self.elapsed_seconds)
            self.analyzer.flush_events()
```

### SystemMonitor Integration

```python
class SystemMonitor:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
    
    def detect_app_switch(self, from_app, to_app):
        if self.analyzer:
            self.analyzer.record_focus_shift(from_app, to_app)
```

### DNDManager Integration

```python
class DNDManager:
    def __init__(self, analyzer=None):
        self.analyzer = analyzer
    
    def toggle_dnd(self, enabled):
        if self.analyzer:
            self.analyzer.record_dnd_toggled(enabled)
```

---

## Querying Events

### Get All Events for a Session

```python
events = db_manager.get_atomic_events(session_id=123)
for event in events:
    print(f"{event['event_type']} at {event['elapsed_seconds']}s")
```

### Get Only Interruptions

```python
interruptions = db_manager.get_interruption_events(session_id=123)
```

### Get Focus Shifts

```python
shifts = db_manager.get_focus_shift_events(session_id=123)
```

### Get Events by Date Range

```python
from datetime import datetime, timedelta

start = datetime.now() - timedelta(days=7)
end = datetime.now()

events = db_manager.get_atomic_events_by_range(start, end)
```

### Get Event Statistics

```python
stats = db_manager.get_event_statistics_for_session(session_id=123)
# Returns: event_type counts by type
```

---

## Data Structure

Each event has:

```python
@dataclass
class AtomicEvent:
    event_type: EventType          # Type of event
    session_id: int                # Which session
    elapsed_seconds: int           # When in session (e.g., 300 = 5 min mark)
    timestamp: datetime            # Exact timestamp
    metadata: Dict[str, Any]       # Event-specific details
```

**Key insight**: `elapsed_seconds` is what matters for pattern analysis. Two interruptions at the 5-minute mark in different sessions are directly comparable.

---

## Performance Tuning

### Auto-Flush Threshold

By default, AtomicAnalyzer auto-flushes every **50 events** to balance memory and database write frequency.

```python
# To change (in atomic_analyzer.py):
AtomicAnalyzer.AUTO_FLUSH_THRESHOLD = 100
```

### Manual Flush

```python
# Explicitly save all buffered events to database
analyzer.flush_events()
```

**Best practice**: Call `flush_events()` when session completes to ensure no data loss.

---

## Example: Complete Session Flow

```python
# Initialize
analyzer = AtomicAnalyzer(db_manager)

# Start session
session_id = db_manager.log_session_v2(...)
analyzer.start_session(
    session_id=session_id,
    planned_duration=1800,
    session_type="pomodoro"
)

# 5 minutes in, user gets interrupted
analyzer.record_interruption(
    reason="slack_notification",
    severity=InterruptionSeverity.MEDIUM
)

# At 25% mark
analyzer.record_milestone(percentage=25)

# Focus shift detected
analyzer.record_focus_shift(
    from_app="VS Code",
    to_app="Slack",
    context="checking message"
)

# 27 minutes later, session completes
analyzer.complete_session(actual_duration=1620)

# Ensure all events saved
analyzer.flush_events()
```

---

## Database Schema

Events are stored in the `atomic_events` table:

```sql
CREATE TABLE atomic_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    elapsed_seconds INTEGER NOT NULL,
    metadata TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions_v2(id)
);
```

Indexes for fast queries:
- `idx_atomic_events_session_id` - Get events for a session
- `idx_atomic_events_event_type` - Get events by type
- `idx_atomic_events_timestamp` - Get events by date
- `idx_atomic_events_elapsed_seconds` - Get events at specific time in session

---

## Common Patterns

### Find Your Focus Limit

```python
# Sessions with interruptions at same elapsed time
events = db_manager.get_interruption_events(session_id)
first_interruption_times = [e['elapsed_seconds'] for e in events]
# Analyze: Do you always get interrupted around 15-20 minutes?
```

### Measure DND Effectiveness

```python
# Compare sessions with DND on vs off
dnd_sessions = db_manager.get_events_by_dnd_status(enabled=True)
no_dnd_sessions = db_manager.get_events_by_dnd_status(enabled=False)

# Count interruptions in each group
# If DND sessions have fewer interruptions, DND works!
```

### Identify Most Disruptive Apps

```python
# Find which apps cause most focus shifts
shifts = db_manager.get_focus_shift_events(session_id)
app_switch_count = {}
for shift in shifts:
    to_app = shift['metadata']['to_app']
    app_switch_count[to_app] = app_switch_count.get(to_app, 0) + 1

# Slack probably wins 😅
```

---

## Troubleshooting

### Events Not Saving?
- Call `analyzer.flush_events()` explicitly
- Check database connection is working
- Verify `session_id` is valid

### Missing Events?
- Make sure you're calling recorder methods (e.g., `record_interruption`)
- Verify `analyzer` is initialized before session starts
- Check event buffer size (should auto-flush at 50 events)

### Wrong `elapsed_seconds`?
- `elapsed_seconds` is calculated from `session_start_time`
- Must call `start_session()` first
- Make sure system clock is accurate

---

## Next Steps

1. **Initialize AtomicAnalyzer** in `main_window.py`
2. **Pass to components** (timer, monitor, dnd_manager)
3. **Call record methods** at appropriate times
4. **Query events** for analysis and patterns
5. **Build insights** from the data!

See [ATOMIC_ANALYZER_INTEGRATION.md](ATOMIC_ANALYZER_INTEGRATION.md) for detailed integration instructions.
