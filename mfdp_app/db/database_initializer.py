"""
Database schema initialization and migrations.
Handles creating tables, indices, and schema upgrades.
"""

import sqlite3
from typing import Optional

from mfdp_app.db.base_repository import BaseRepository


class DatabaseInitializer:
    """Initialize and manage database schema."""
    
    @staticmethod
    def setup_database() -> bool:
        """
        Create all tables and indices. Idempotent - safe to call multiple times.
        Applies migrations for existing databases.
        
        Returns:
            True if successful, False otherwise
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Settings Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """)
            
            # 2. Sessions V2 Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                planned_duration_minutes INTEGER,
                mode TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                task_name TEXT,
                category TEXT,
                interruption_count INTEGER DEFAULT 0
            );
            """)
            
            # Migration: oturum sonu geri bildirimi (odak puanı 1-5, oturum türü)
            for column in ("focus_rating INTEGER", "session_kind TEXT"):
                try:
                    cursor.execute(f"ALTER TABLE sessions_v2 ADD COLUMN {column}")
                except sqlite3.OperationalError:
                    pass

            # Sessions indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions_v2 (start_time);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_completed ON sessions_v2 (completed);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_task_name ON sessions_v2 (task_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_category ON sessions_v2 (category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_mode ON sessions_v2 (mode);")
            
            # 3. Tasks Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                tag TEXT NOT NULL,
                planned_duration_minutes INTEGER,
                created_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                color TEXT,
                parent_id INTEGER,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """)
            
            # Migration: Add parent_id and is_completed columns if they don't exist
            try:
                cursor.execute("ALTER TABLE tasks ADD COLUMN parent_id INTEGER")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE tasks ADD COLUMN is_completed BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            
            # Tasks indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks (parent_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_tag ON tasks (tag);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_is_active ON tasks (is_active);")
            
            # 4. Tags Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                name TEXT PRIMARY KEY,
                color TEXT,
                created_at TEXT NOT NULL
            );
            """)
            
            # 5. Atomic Events Table (Event Sourcing)
            cursor.execute("""
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
            """)
            
            # Atomic events indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_session_id ON atomic_events (session_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_event_type ON atomic_events (event_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_timestamp ON atomic_events (timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_elapsed_seconds ON atomic_events (elapsed_seconds);")
            
            # 6. Calendar tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                kind TEXT NOT NULL DEFAULT 'diger',
                note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_ranges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                color TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            # Migration: sınav -> ders (ana görev) bağlantısı
            try:
                cursor.execute("ALTER TABLE calendar_events ADD COLUMN task_id INTEGER")
            except sqlite3.OperationalError:
                pass
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events (date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_ranges_start ON calendar_ranges (start_date, end_date);")

            # 7. Eğer-ise planları (implementation intentions)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS if_then_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weekdays TEXT NOT NULL,
                time TEXT,
                cue TEXT,
                task_id INTEGER,
                action TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                outcome TEXT NOT NULL,
                session_id INTEGER,
                logged_at TEXT NOT NULL
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_log_plan_day ON plan_log (plan_id, day);")

            # 8. Aralıklı tekrar (1-3-7-14): konu başına durum ve tekrar geçmişi
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_state (
                task_id INTEGER PRIMARY KEY,
                step INTEGER NOT NULL DEFAULT 0,
                next_due TEXT NOT NULL,
                last_review TEXT NOT NULL,
                lapses INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                session_id INTEGER,
                recall INTEGER NOT NULL,
                day TEXT NOT NULL,
                reviewed_at TEXT NOT NULL,
                prev_step INTEGER NOT NULL,
                prev_next_due TEXT NOT NULL,
                prev_last_review TEXT NOT NULL,
                prev_lapses INTEGER NOT NULL
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_log_session ON review_log (session_id);")
            # Migration: konunun ilk karşılaşma günü (derste işlendiği gün) ve kaynağı
            for column in ("learned_on TEXT", "source TEXT"):
                try:
                    cursor.execute(f"ALTER TABLE review_state ADD COLUMN {column}")
                except sqlite3.OperationalError:
                    pass

            conn.commit()
            print("✅ Database V2 schema initialized successfully.")
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            BaseRepository.return_connection(conn)
    
    @staticmethod
    def verify_schema() -> bool:
        """
        Verify that all required tables exist.
        
        Returns:
            True if all tables exist, False otherwise
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            required_tables = ['settings', 'sessions_v2', 'tasks', 'tags', 'atomic_events', 'calendar_events', 'calendar_ranges', 'if_then_plans', 'plan_log', 'review_state', 'review_log']
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(required_tables) - existing_tables
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                return False
            
            print("✅ All required tables exist.")
            return True
            
        except sqlite3.Error as e:
            print(f"Schema verification error: {e}")
            return False
        finally:
            BaseRepository.return_connection(conn)
    
    @staticmethod
    def reset_database() -> bool:
        """
        Drop all tables (for development/testing only).
        WARNING: This will delete all data!
        
        Returns:
            True if successful, False otherwise
        """
        conn = BaseRepository.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            tables = ['review_log', 'review_state', 'plan_log', 'if_then_plans', 'calendar_events', 'calendar_ranges', 'atomic_events', 'tasks', 'tags', 'sessions_v2', 'settings']
            
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            conn.commit()
            print("⚠️  Database reset - all tables dropped.")
            return True
            
        except sqlite3.Error as e:
            print(f"Database reset error: {e}")
            return False
        finally:
            BaseRepository.return_connection(conn)
