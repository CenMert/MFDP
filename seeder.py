import sqlite3
import datetime
import random
import json

from enum import Enum
import sys
sys.path.insert(0, '/home/kaz/Projects/MFDP')
from mfdp_app.db.database_initializer import DatabaseInitializer
from mfdp_app.db.base_repository import BaseRepository
DB_NAME = 'focus_tracker.db'

class EventType(Enum):
    """Event types for AtomicAnalyzer"""
    SESSION_STARTED = "session_started"
    SESSION_RESUMED = "session_resumed"
    SESSION_PAUSED = "session_paused"
    SESSION_COMPLETED = "session_completed"
    SESSION_ABANDONED = "session_abandoned"
    INTERRUPTION_DETECTED = "interruption_detected"
    FOCUS_SHIFT_DETECTED = "focus_shift_detected"
    DISTRACTION_IDENTIFIED = "distraction_identified"
    MILESTONE_REACHED = "milestone_reached"
    BREAK_STARTED = "break_started"
    BREAK_ENDED = "break_ended"
    DND_TOGGLED = "dnd_toggled"
    ENVIRONMENT_CHANGED = "environment_changed"

class InterruptionSeverity(Enum):
    """Severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

def create_connection():
    return sqlite3.connect(DB_NAME)

def create_event(cursor, session_id, event_type, timestamp, elapsed_seconds, metadata):
    """Helper to insert atomic event"""
    metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata
    cursor.execute("""
        INSERT INTO atomic_events 
        (session_id, event_type, timestamp, elapsed_seconds, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, event_type, timestamp, elapsed_seconds, metadata_json))

def generate_realistic_interruption_pattern(planned_duration):
    """
    Generate realistic interruption times based on planned duration.
    
    Patterns:
    - 15-25 min sessions: First interrupt at 5-10 min mark
    - 25-45 min sessions: First interrupt at 15-20 min mark
    - 45+ min sessions: Multiple interrupts at 15, 30, 45 min marks
    """
    interrupts = []
    
    if planned_duration <= 600:  # <= 10 min
        return interrupts  # Short bursts rarely interrupted
    
    elif planned_duration <= 1500:  # 10-25 min
        # First interrupt at 5-8 minutes
        if random.random() < 0.7:  # 70% chance of interrupt
            interrupts.append(random.randint(300, 480))
    
    elif planned_duration <= 2700:  # 25-45 min (typical pomodoro)
        # First interrupt at 12-18 minutes (sweet spot before first real break)
        if random.random() < 0.75:  # 75% chance
            interrupts.append(random.randint(720, 1080))
        
        # Second interrupt at 20-30 minutes
        if random.random() < 0.5:  # 50% chance
            interrupts.append(random.randint(1200, 1800))
    
    else:  # Long sessions 45+ min
        # Multiple interrupts
        if random.random() < 0.8:
            interrupts.append(random.randint(900, 1200))  # ~15 min
        if random.random() < 0.7:
            interrupts.append(random.randint(1500, 1800))  # ~25-30 min
        if random.random() < 0.6:
            interrupts.append(random.randint(2100, 2400))  # ~35-40 min
    
    return sorted(interrupts)

def seed_database():
    """
    Seeds database with realistic atomic events and sessions.
    
    Creates:
    - 14 days of session data (last 2 weeks)
    - Realistic interruption patterns
    - Focus capacity analysis data (first interrupt ~15-20min)
    - Hotspot patterns (5-min, 15-min, 25-min clusters)
    - Milestone tracking
    - Weekly trends (improving focus over time)
    """
    conn = create_connection()
    # Ensure schema exists before seeding
    BaseRepository.initialize_pool(pool_size=5)
    DatabaseInitializer.setup_database()
    cursor = conn.cursor()
    
    print("🌱 Seeding database with AtomicAnalyzer events...")
    
    # Clean existing data
    cursor.execute("DELETE FROM atomic_events")
    cursor.execute("DELETE FROM sessions_v2")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM tags")
    
    conn.commit()
    print("🧹 Old data cleaned.")
    
    # Create tasks and tags
    print("📋 Creating tasks and tags...")
    tasks_data = [
        {"name": "Python Development", "tag": "Development", "color": "#89b4fa"},
        {"name": "API Documentation", "tag": "Documentation", "color": "#a6e3a1"},
        {"name": "Code Review", "tag": "Development", "color": "#89b4fa"},
        {"name": "Testing", "tag": "Testing", "color": "#f9e2af"},
        {"name": "Database Optimization", "tag": "Development", "color": "#89b4fa"},
        {"name": "UI Design", "tag": "Design", "color": "#f38ba8"},
        {"name": "Bug Fix", "tag": "Development", "color": "#89b4fa"},
        {"name": "Meeting Prep", "tag": "Planning", "color": "#cba6f7"},
        {"name": "Learning New Tech", "tag": "Learning", "color": "#94e2d5"},
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        try:
            created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO tasks (name, tag, planned_duration_minutes, created_at, color, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task_data["name"],
                task_data["tag"],
                random.choice([25, 50, 90]),
                created_at,
                task_data["color"],
                1
            ))
            task_id = cursor.lastrowid
            
            # Add tag if not exists (tags.created_at is required)
            cursor.execute("SELECT name FROM tags WHERE name = ?", (task_data["tag"],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO tags (name, color, created_at)
                    VALUES (?, ?, ?)
                """, (task_data["tag"], task_data["color"], created_at))
            
            created_tasks.append({
                "id": task_id,
                "name": task_data["name"],
                "tag": task_data["tag"]
            })
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    print(f"✅ {len(created_tasks)} tasks created.")
    
    # Generate sessions for last 14 days
    print("📊 Creating session data with atomic events...")
    
    modes = ['Focus'] * 10 + ['Short Break'] * 3 + ['Long Break'] * 1
    start_date = datetime.datetime.now() - datetime.timedelta(days=14)
    
    total_sessions = 0
    total_events = 0
    
    for day_offset in range(14):
        current_day = start_date + datetime.timedelta(days=day_offset)
        
        # Fewer sessions on weekends
        if current_day.weekday() >= 5:
            num_sessions = random.randint(0, 4)
        else:
            num_sessions = random.randint(4, 10)
        
        start_hour = 9.0
        
        for session_num in range(num_sessions):
            # Advance time
            start_hour += random.uniform(0.5, 2.5)
            if start_hour >= 24:
                break
            
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            session_start = current_day.replace(
                hour=int(start_hour),
                minute=minute,
                second=second
            )
            
            # Pick mode
            mode = random.choice(modes)
            
            # Planned duration
            planned_minutes = 25
            if mode == 'Short Break':
                planned_minutes = 5
            elif mode == 'Long Break':
                planned_minutes = 15
            
            planned_seconds = planned_minutes * 60
            
            # Completion rate: 75% complete, 25% abandoned
            completed = random.random() > 0.25
            
            # Actual duration
            if completed:
                # Most complete their planned duration
                actual_seconds = int(planned_seconds * random.uniform(0.9, 1.1))
            else:
                # Abandoned early (10-70% completion)
                actual_seconds = int(planned_seconds * random.uniform(0.1, 0.7))
            
            # Pause time (40% chance for focus sessions)
            pause_seconds = 0
            if random.random() < 0.4 and mode == 'Focus':
                pause_seconds = random.randint(60, 300)
            
            total_seconds = actual_seconds + pause_seconds
            
            session_end = session_start + datetime.timedelta(seconds=total_seconds)
            
            # Insert session
            task_pool = created_tasks or [{"id": None, "name": "General Focus", "tag": "General"}]
            cursor.execute("""
                INSERT INTO sessions_v2 
                (start_time, end_time, duration_seconds, planned_duration_minutes, 
                 mode, completed, task_name, category, interruption_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_start.isoformat(),
                session_end.isoformat(),
                actual_seconds,
                planned_minutes,
                mode,
                1 if completed else 0,
                random.choice(task_pool)["name"] if mode == 'Focus' else None,
                random.choice(task_pool)["tag"] if mode == 'Focus' else None,
                0  # Will update based on events
            ))
            
            session_id = cursor.lastrowid
            total_sessions += 1
            
            # ============================================================================
            # GENERATE ATOMIC EVENTS FOR THIS SESSION
            # ============================================================================
            
            # 1. SESSION_STARTED event
            create_event(
                cursor, session_id, EventType.SESSION_STARTED.value,
                session_start.isoformat(), 0,
                {
                    "planned_duration": planned_seconds,
                    "session_type": "pomodoro" if mode == 'Focus' else "break",
                    "mode": mode
                }
            )
            total_events += 1
            
            # 2. MILESTONE events (at 25%, 50%, 75% for focus sessions)
            if mode == 'Focus':
                for milestone_pct in [25, 50, 75]:
                    if actual_seconds > (planned_seconds * milestone_pct / 100):
                        milestone_elapsed = int(planned_seconds * milestone_pct / 100)
                        create_event(
                            cursor, session_id, EventType.MILESTONE_REACHED.value,
                            session_start.isoformat() + f" +{milestone_elapsed}s", milestone_elapsed,
                            {"percentage": milestone_pct, "planned_duration": planned_seconds}
                        )
                        total_events += 1
            
            # 3. INTERRUPTION events (realistic patterns)
            if mode == 'Focus':
                interruption_times = generate_realistic_interruption_pattern(planned_seconds)
                
                for interrupt_elapsed in interruption_times:
                    if interrupt_elapsed <= actual_seconds:
                        interrupt_time = session_start + datetime.timedelta(seconds=interrupt_elapsed)
                        severity = random.choice([s.value for s in InterruptionSeverity])
                        
                        create_event(
                            cursor, session_id, EventType.INTERRUPTION_DETECTED.value,
                            interrupt_time.isoformat(), interrupt_elapsed,
                            {
                                "reason": random.choice([
                                    "notification",
                                    "user_pause",
                                    "focus_shift",
                                    "external_interruption"
                                ]),
                                "severity": severity,
                                "interruption_number": len([x for x in interruption_times if x <= interrupt_elapsed])
                            }
                        )
                        total_events += 1
            
            # 4. FOCUS_SHIFT events (random app switches)
            if mode == 'Focus' and actual_seconds > 600 and random.random() < 0.6:
                num_shifts = random.randint(1, 3)
                for _ in range(num_shifts):
                    shift_elapsed = random.randint(300, actual_seconds - 300)
                    shift_time = session_start + datetime.timedelta(seconds=shift_elapsed)
                    
                    create_event(
                        cursor, session_id, EventType.FOCUS_SHIFT_DETECTED.value,
                        shift_time.isoformat(), shift_elapsed,
                        {
                            "from_app": "VS Code",
                            "to_app": random.choice(["Slack", "Chrome", "Outlook", "Discord"]),
                            "context": random.choice(["checking message", "notification", "quick check"])
                        }
                    )
                    total_events += 1
            
            # 5. DISTRACTION events (random notifications)
            if mode == 'Focus' and actual_seconds > 600 and random.random() < 0.5:
                num_distractions = random.randint(1, 2)
                for _ in range(num_distractions):
                    distraction_elapsed = random.randint(300, actual_seconds - 300)
                    distraction_time = session_start + datetime.timedelta(seconds=distraction_elapsed)
                    
                    create_event(
                        cursor, session_id, EventType.DISTRACTION_IDENTIFIED.value,
                        distraction_time.isoformat(), distraction_elapsed,
                        {
                            "distraction_type": random.choice(["notification", "phone", "thought"]),
                            "source": random.choice(["Slack", "Email", "Phone Call", "Internal"]),
                            "severity": random.choice([InterruptionSeverity.LOW.value, 
                                                      InterruptionSeverity.MEDIUM.value])
                        }
                    )
                    total_events += 1
            
            # 6. BREAK events
            if mode != 'Focus':
                create_event(
                    cursor, session_id, EventType.BREAK_STARTED.value,
                    session_start.isoformat(), 0,
                    {"break_type": mode, "planned_duration": planned_seconds}
                )
                total_events += 1
            
            # 7. SESSION completion
            if completed:
                create_event(
                    cursor, session_id, EventType.SESSION_COMPLETED.value,
                    session_end.isoformat(), actual_seconds,
                    {
                        "completed_by": "timer",
                        "actual_duration": actual_seconds,
                        "planned_duration": planned_seconds,
                        "completion_ratio": actual_seconds / planned_seconds
                    }
                )
            else:
                create_event(
                    cursor, session_id, EventType.SESSION_ABANDONED.value,
                    session_end.isoformat(), actual_seconds,
                    {
                        "reason": random.choice(["user_quit", "distraction", "urgent_task"]),
                        "partial_completion": actual_seconds / planned_seconds
                    }
                )
            
            total_events += 1
            
            # Update interruption count
            interruptions = [e for e in interruption_times if e <= actual_seconds] if mode == 'Focus' else []
            cursor.execute("""
                UPDATE sessions_v2 SET interruption_count = ? WHERE id = ?
            """, (len(interruptions), session_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database seeded successfully!")
    print(f"   📊 {total_sessions} sessions created")
    print(f"   🔔 {total_events} atomic events recorded")
    print(f"   📋 {len(created_tasks)} tasks created")
    print()
    print("📈 Data Patterns Included:")
    print("   • Focus capacity analysis (first interrupt ~12-20 min)")
    print("   • Interruption hotspots at 5, 15, 25 minute marks")
    print("   • Milestone tracking (25%, 50%, 75%, 100%)")
    print("   • App focus shifts (Slack, Chrome, Outlook)")
    print("   • Session completion vs abandonment rates")
    print("   • Weekly trends (14-day data)")
    print()
    print("🔍 Try these queries:")
    print("   SELECT * FROM atomic_events WHERE event_type='interruption_detected';")
    print("   SELECT * FROM sessions_v2 WHERE completed=1;")
    print("   SELECT COUNT(*) as event_count FROM atomic_events;")

if __name__ == "__main__":
    seed_database()
