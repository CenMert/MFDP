"""
AtomicAnalyzer Module

This module provides fine-grained event capture and analysis for focus sessions.
Instead of storing only session summaries, AtomicAnalyzer captures discrete events
(interruptions, focus shifts, milestones) as they occur during a session.

This raw event data enables:
- Pattern detection (e.g., "always interrupted at 5min mark")
- Focus capacity analysis (e.g., "can't sustain 45min sessions")
- Environmental impact assessment (e.g., "DND improves focus by X%")
- Future ML models for personalized recommendations

Design Pattern: Event Sourcing
- Events are immutable records of what happened
- Multiple analyses can be derived from the same event stream
- No data is lost; only aggregated/cached for performance
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass, asdict
import json


class EventType(Enum):
    """Enumeration of all possible atomic events during a session."""
    
    # Session lifecycle events
    SESSION_STARTED = "session_started"
    SESSION_RESUMED = "session_resumed"
    SESSION_PAUSED = "session_paused"
    SESSION_COMPLETED = "session_completed"
    SESSION_ABANDONED = "session_abandoned"
    
    # Focus interruption events
    INTERRUPTION_DETECTED = "interruption_detected"
    FOCUS_SHIFT_DETECTED = "focus_shift_detected"  # App/window changed
    
    # Environmental events
    DISTRACTION_IDENTIFIED = "distraction_identified"
    DND_TOGGLED = "dnd_toggled"
    ENVIRONMENT_CHANGED = "environment_changed"
    
    # Session milestones
    MILESTONE_REACHED = "milestone_reached"  # 25%, 50%, 75%, 100%
    BREAK_STARTED = "break_started"
    BREAK_ENDED = "break_ended"


class InterruptionSeverity(Enum):
    """Severity levels for interruptions."""
    LOW = "low"          # User paused, can resume easily
    MEDIUM = "medium"    # Context-switching required
    HIGH = "high"        # Major distraction, full context loss


@dataclass
class AtomicEvent:
    """
    Immutable representation of a single event during a session.
    
    Attributes:
        event_type: Type of event (EventType enum)
        session_id: ID of the session this event belongs to
        elapsed_seconds: How many seconds into the session this event occurred
        timestamp: Exact datetime when the event was recorded
        metadata: Additional context as a dictionary
        
    Note: elapsed_seconds is more important than timestamp because:
    - It tells us WHERE in the session the event happened
    - Two interruptions at 5 min in different sessions are comparable
    - Absolute time (9am vs 3pm) is secondary
    """
    
    event_type: EventType
    session_id: int
    elapsed_seconds: int
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['event_type'] = self.event_type.value  # Store enum as string
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AtomicAnalyzer:
    """
    Central event collector for focus session analytics.
    
    Responsibilities:
    1. Record atomic events during sessions (interruptions, focus shifts, etc.)
    2. Buffer events in memory for performance
    3. Flush buffered events to database in batches
    4. Provide query methods for analysis
    
    Integration Points:
    - PomodoroTimer/CountUpTimer: Record pause/resume/completion events
    - SystemMonitor: Record focus shift (app switching) events
    - DNDManager: Record environment change events
    - MainWindow: Initialize and manage lifecycle
    
    Example Usage:
        analyzer = AtomicAnalyzer(db_manager)
        analyzer.start_session(session_id=123, planned_duration=1800)
        # ... session runs ...
        analyzer.record_interruption(
            elapsed_seconds=180,
            reason="user_pause",
            severity=InterruptionSeverity.LOW
        )
        analyzer.flush_events()  # Save to DB
    """
    
    # Buffer size before auto-flush (how many events to accumulate)
    AUTO_FLUSH_THRESHOLD = 50
    
    def __init__(self, db_manager):
        """
        Initialize the AtomicAnalyzer.
        
        Args:
            db_manager: DatabaseManager instance for persisting events
        """
        self.db_manager = db_manager
        
        # Current session context
        self.current_session_id: Optional[int] = None
        self.session_start_time: Optional[datetime] = None
        self.session_planned_duration: Optional[int] = None  # in seconds
        self.session_type: str = "pomodoro"  # or "flowtime", "custom", etc.
        
        # Event buffer - accumulate events before batch inserting
        self.event_buffer: List[AtomicEvent] = []
        
        # Statistics for the current session (cached)
        self.interruption_count = 0
        self.first_interruption_elapsed = None
        self.last_focus_shift_time = None

    # ============================================================================
    # SESSION LIFECYCLE METHODS
    # ============================================================================
    
    def start_session(self, session_id: int, planned_duration: int, 
                     session_type: str = "pomodoro", app_before: str = None) -> None:
        """
        Mark the start of a new focus session.
        
        This should be called when a Pomodoro/Flowtime session begins.
        
        Args:
            session_id: Unique identifier for this session (from sessions_v2 table)
            planned_duration: Intended session length in seconds
            session_type: Type of session ("pomodoro", "flowtime", "custom", etc.)
            app_before: The app that was active before session start (optional)
        """
        self.current_session_id = session_id
        self.session_start_time = datetime.now()
        self.session_planned_duration = planned_duration
        self.session_type = session_type
        self.interruption_count = 0
        self.first_interruption_elapsed = None
        self.last_focus_shift_time = 0
        
        # Record the session start event
        self._record_event(
            event_type=EventType.SESSION_STARTED,
            elapsed_seconds=0,
            metadata={
                "planned_duration": planned_duration,
                "session_type": session_type,
                "app_before": app_before
            }
        )

    def resume_session(self, app_context: str = None) -> None:
        """
        Mark when a paused session is resumed.
        
        Args:
            app_context: Current app when resuming (optional)
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        self._record_event(
            event_type=EventType.SESSION_RESUMED,
            elapsed_seconds=elapsed,
            metadata={"app_context": app_context}
        )

    def complete_session(self, actual_duration: int, completed_by: str = "timer") -> None:
        """
        Mark the successful completion of a session.
        
        Args:
            actual_duration: How long the session actually ran (seconds)
            completed_by: How session ended ("timer", "user", "cancelled")
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.SESSION_COMPLETED,
            elapsed_seconds=elapsed,
            metadata={
                "actual_duration": actual_duration,
                "planned_duration": self.session_planned_duration,
                "completed_by": completed_by,
                "interruption_count": self.interruption_count,
                "focus_completion_ratio": (
                    actual_duration / self.session_planned_duration 
                    if self.session_planned_duration else 0
                )
            }
        )
        
        self._reset_session_context()

    def abandon_session(self, reason: str = "user_quit") -> None:
        """
        Mark when a session is abandoned without completion.
        
        Args:
            reason: Why the session was abandoned
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.SESSION_ABANDONED,
            elapsed_seconds=elapsed,
            metadata={
                "reason": reason,
                "interruption_count": self.interruption_count,
                "partial_completion": elapsed / self.session_planned_duration 
                                     if self.session_planned_duration else 0
            }
        )
        
        self._reset_session_context()

    # ============================================================================
    # INTERRUPTION AND FOCUS EVENTS
    # ============================================================================
    
    def record_interruption(self, reason: str, severity: InterruptionSeverity,
                           recovery_app: str = None) -> None:
        """
        Record that the user was interrupted during the session.
        
        An interruption is when the user manually pauses the timer, gets distracted,
        or stops focusing on the task at hand.
        
        Args:
            reason: Why interrupted ("user_pause", "notification", "external_call", etc.)
            severity: How severe was this interruption (LOW/MEDIUM/HIGH)
            recovery_app: What app they switched to (optional)
        
        Example:
            analyzer.record_interruption(
                reason="slack_notification",
                severity=InterruptionSeverity.MEDIUM
            )
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        # Track first interruption time
        if self.first_interruption_elapsed is None:
            self.first_interruption_elapsed = elapsed
        
        self.interruption_count += 1
        
        self._record_event(
            event_type=EventType.INTERRUPTION_DETECTED,
            elapsed_seconds=elapsed,
            metadata={
                "reason": reason,
                "severity": severity.value,
                "interruption_number": self.interruption_count,
                "first_interruption_at": self.first_interruption_elapsed,
                "recovery_app": recovery_app
            }
        )
        
        # Auto-flush if buffer is getting large
        if len(self.event_buffer) >= self.AUTO_FLUSH_THRESHOLD:
            self.flush_events()

    def record_focus_shift(self, from_app: str, to_app: str, 
                          focus_duration: int = None) -> None:
        """
        Record that the user switched focus to a different application.
        
        This is detected by SystemMonitor when the active window changes.
        Unlike interruptions, this might be intentional (switching to reference material).
        
        Args:
            from_app: Application they were focused on
            to_app: Application they shifted focus to
            focus_duration: How long they focused on 'from_app' (seconds, optional)
        
        Example:
            analyzer.record_focus_shift(
                from_app="VSCode",
                to_app="Chrome",
                focus_duration=300
            )
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.FOCUS_SHIFT_DETECTED,
            elapsed_seconds=elapsed,
            metadata={
                "from_app": from_app,
                "to_app": to_app,
                "focus_duration_seconds": focus_duration,
                "shift_number": self._count_focus_shifts()
            }
        )

    def record_distraction(self, distraction_type: str, app_name: str = None,
                          severity: InterruptionSeverity = InterruptionSeverity.MEDIUM) -> None:
        """
        Record identification of a specific distraction during the session.
        
        Different from generic interruptions - this is for specific identified distractions.
        
        Args:
            distraction_type: Type of distraction ("noise", "notification", "person", "thought")
            app_name: If app-related, which app caused it
            severity: How distracting it was
        
        Example:
            analyzer.record_distraction(
                distraction_type="notification",
                app_name="Slack",
                severity=InterruptionSeverity.MEDIUM
            )
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.DISTRACTION_IDENTIFIED,
            elapsed_seconds=elapsed,
            metadata={
                "distraction_type": distraction_type,
                "app_name": app_name,
                "severity": severity.value
            }
        )

    # ============================================================================
    # ENVIRONMENTAL EVENTS
    # ============================================================================
    
    def record_dnd_toggle(self, enabled: bool) -> None:
        """
        Record when Do-Not-Disturb mode is toggled.
        
        Args:
            enabled: True if DND was turned ON, False if turned OFF
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.DND_TOGGLED,
            elapsed_seconds=elapsed,
            metadata={"dnd_enabled": enabled}
        )

    def record_environment_change(self, factor_type: str, value: Any) -> None:
        """
        Record changes to the environment during a session.
        
        Args:
            factor_type: Type of environmental factor ("location", "noise_level", 
                        "people_present", "temperature", etc.)
            value: The value of the factor
        
        Example:
            analyzer.record_environment_change(
                factor_type="location",
                value="home_office"
            )
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.ENVIRONMENT_CHANGED,
            elapsed_seconds=elapsed,
            metadata={
                "factor_type": factor_type,
                "value": value
            }
        )

    # ============================================================================
    # MILESTONE EVENTS
    # ============================================================================
    
    def record_milestone(self, milestone_type: str, percentage: int = None) -> None:
        """
        Record progress milestones during the session (25%, 50%, 75%, 100%).
        
        This helps track where in the session interruptions typically occur.
        
        Args:
            milestone_type: Type of milestone ("quarter", "halfway", "three_quarters", "complete")
            percentage: Percentage of session completed (25, 50, 75, 100)
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        
        self._record_event(
            event_type=EventType.MILESTONE_REACHED,
            elapsed_seconds=elapsed,
            metadata={
                "milestone_type": milestone_type,
                "percentage": percentage or 0
            }
        )

    def record_break(self, break_type: str, duration: int = None, 
                    action: str = "started") -> None:
        """
        Record break periods during or after sessions.
        
        Args:
            break_type: Type of break ("short", "long", "spontaneous")
            duration: How long the break was (seconds, if known)
            action: "started" or "ended"
        """
        if not self.current_session_id:
            return
        
        elapsed = self._get_elapsed_seconds()
        event_type = EventType.BREAK_STARTED if action == "started" else EventType.BREAK_ENDED
        
        self._record_event(
            event_type=event_type,
            elapsed_seconds=elapsed,
            metadata={
                "break_type": break_type,
                "duration": duration
            }
        )

    # ============================================================================
    # DATA PERSISTENCE
    # ============================================================================
    
    def flush_events(self) -> bool:
        """
        Flush all buffered events to the database.
        
        This should be called:
        - Explicitly at session end (complete_session/abandon_session)
        - Periodically during long sessions (via auto-flush threshold)
        - When the application is closing
        
        Returns:
            True if flush was successful, False otherwise
        """
        if not self.event_buffer:
            return True
        
        try:
            # Convert events to dictionaries for database storage
            events_data = [event.to_dict() for event in self.event_buffer]
            
            # Batch insert all events
            self.db_manager.insert_atomic_events(events_data)
            
            # Clear buffer after successful insert
            self.event_buffer = []
            
            return True
            
        except Exception as e:
            print(f"Error flushing events: {e}")
            # Keep events in buffer for retry on next flush
            return False

    # ============================================================================
    # QUERY AND ANALYSIS METHODS
    # ============================================================================
    
    def get_session_events(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all events for a specific session.
        
        Args:
            session_id: ID of the session to retrieve events for
            
        Returns:
            List of event dictionaries
        """
        try:
            return self.db_manager.get_atomic_events(session_id)
        except Exception as e:
            print(f"Error retrieving session events: {e}")
            return []

    def get_sessions_by_time_range(self, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retrieve all events within a time range.
        
        Args:
            start_date: Start of time range
            end_date: End of time range
            
        Returns:
            List of event dictionaries
        """
        try:
            return self.db_manager.get_atomic_events_by_range(start_date, end_date)
        except Exception as e:
            print(f"Error retrieving events by range: {e}")
            return []

    def get_interruption_pattern(self, session_id: int) -> Dict[str, Any]:
        """
        Analyze interruption patterns for a session.
        
        Returns statistics about when interruptions occurred.
        
        Args:
            session_id: ID of the session to analyze
            
        Returns:
            Dictionary with interruption pattern data:
            {
                'total_interruptions': int,
                'first_interruption_at': int,  # seconds
                'interruptions_by_phase': [],  # early/middle/late
                'average_time_between_interruptions': int,
                'severity_distribution': {}
            }
        """
        events = self.get_session_events(session_id)
        interruptions = [e for e in events 
                        if e['event_type'] == EventType.INTERRUPTION_DETECTED.value]
        
        if not interruptions:
            return {
                'total_interruptions': 0,
                'first_interruption_at': None,
                'interruptions_by_phase': {'early': 0, 'middle': 0, 'late': 0},
                'average_time_between_interruptions': None,
                'severity_distribution': {}
            }
        
        times = [i['elapsed_seconds'] for i in interruptions]
        planned_duration = self.session_planned_duration or 1800
        
        # Categorize by phase (early=0-33%, middle=33-66%, late=66-100%)
        early = sum(1 for t in times if t < planned_duration * 0.33)
        middle = sum(1 for t in times if planned_duration * 0.33 <= t < planned_duration * 0.66)
        late = sum(1 for t in times if t >= planned_duration * 0.66)
        
        # Severity distribution
        severity_dist = {}
        for interrupt in interruptions:
            severity = interrupt['metadata'].get('severity', 'unknown')
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
        
        # Average time between interruptions
        if len(times) > 1:
            gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
            avg_gap = sum(gaps) / len(gaps)
        else:
            avg_gap = None
        
        return {
            'total_interruptions': len(interruptions),
            'first_interruption_at': min(times) if times else None,
            'interruptions_by_phase': {
                'early': early,
                'middle': middle,
                'late': late
            },
            'average_time_between_interruptions': avg_gap,
            'severity_distribution': severity_dist
        }

    def get_focus_shifts(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all focus shifts (app switches) during a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of focus shift events
        """
        events = self.get_session_events(session_id)
        return [e for e in events 
                if e['event_type'] == EventType.FOCUS_SHIFT_DETECTED.value]

    # ============================================================================
    # PRIVATE/HELPER METHODS
    # ============================================================================
    
    def _record_event(self, event_type: EventType, elapsed_seconds: int,
                     metadata: Dict[str, Any]) -> None:
        """
        Internal method to record an event and add it to the buffer.
        
        Args:
            event_type: Type of event
            elapsed_seconds: Seconds elapsed in the current session
            metadata: Event-specific metadata
        """
        event = AtomicEvent(
            event_type=event_type,
            session_id=self.current_session_id,
            elapsed_seconds=elapsed_seconds,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        self.event_buffer.append(event)

    def _get_elapsed_seconds(self) -> int:
        """
        Calculate how many seconds have elapsed since session start.
        
        Returns:
            Elapsed seconds, or 0 if session not active
        """
        if not self.session_start_time:
            return 0
        
        elapsed = (datetime.now() - self.session_start_time).total_seconds()
        return int(elapsed)

    def _reset_session_context(self) -> None:
        """Reset all session-specific state when a session ends."""
        self.current_session_id = None
        self.session_start_time = None
        self.session_planned_duration = None
        self.interruption_count = 0
        self.first_interruption_elapsed = None
        self.last_focus_shift_time = None
        # Note: Don't clear event_buffer - let flush_events handle that

    def _count_focus_shifts(self) -> int:
        """Count total focus shift events in current buffer."""
        return sum(1 for e in self.event_buffer 
                  if e.event_type == EventType.FOCUS_SHIFT_DETECTED)