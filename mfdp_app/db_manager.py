import sqlite3
import datetime

DB_NAME = 'focus_tracker.db'

def create_connection():
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return None

def setup_database(conn):
    if conn is None: return
    cursor = conn.cursor()

    # 1. Ayarlar Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # 2. SESSIONS V2 (Prompt'a uygun yeni yapı)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT NOT NULL,       -- ISO8601
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

    # İndeksler (Hızlı sorgu için)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions_v2 (start_time);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_completed ON sessions_v2 (completed);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_task_name ON sessions_v2 (task_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_category ON sessions_v2 (category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_mode ON sessions_v2 (mode);")

    # 3. TASKS Tablosu
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
    
    # Mevcut tabloya parent_id ve is_completed sütunlarını ekle (migration)
    # SQLite'da FOREIGN KEY constraint ALTER TABLE ile eklenemez, sadece sütun eklenir
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN parent_id INTEGER")
    except sqlite3.OperationalError:
        pass  # Sütun zaten varsa hata verme
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN is_completed BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Sütun zaten varsa hata verme
    
    # parent_id için indeks
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks (parent_id);")

    # 4. TAGS Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tags (
        name TEXT PRIMARY KEY,
        color TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Task ve Tag indeksleri
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_tag ON tasks (tag);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_is_active ON tasks (is_active);")

    # 5. ATOMIC EVENTS Tablosu (Event Sourcing - Ham veri toplama)
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
    
    # Atomic events indeksleri (hızlı sorgulamalar için)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_session_id ON atomic_events (session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_event_type ON atomic_events (event_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_timestamp ON atomic_events (timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_atomic_events_elapsed_seconds ON atomic_events (elapsed_seconds);")

    conn.commit()
    print("Veritabanı V2 Şeması Hazır.")

# --- KAYIT FONKSİYONU ---
def log_session_v2(start_time, end_time, duration_sec, planned_min, mode, completed, task_name=None, category=None, interruption_count=0):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions_v2 (
                    start_time, end_time, duration_seconds, 
                    planned_duration_minutes, mode, completed, task_name, category, interruption_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                duration_sec, planned_min, mode, completed, task_name, category, interruption_count
            ))
            conn.commit()
            print(f"💾 V2 KAYIT: {mode} ({duration_sec} sn, {interruption_count} kesinti)")
        except sqlite3.Error as e:
            print(f"Kayıt hatası: {e}")
        finally:
            conn.close()

# --- AYAR FONKSİYONLARI ---
def load_settings():
    conn = create_connection()
    settings = {}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            for row in cursor.fetchall():
                settings[row['key']] = row['value']
        except: pass
        conn.close()
    return settings

def save_setting(key, value):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()

# --- ANALİZ FONKSİYONLARI (Grafikler İçin) ---
def get_daily_trend_v2(days=7):
    """Son X günün verileri (sadece Focus ve Free Timer modları)."""
    conn = create_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%Y-%m-%d', start_time) as day, 
                       SUM(duration_seconds) / 60 as minutes
                FROM sessions_v2
                WHERE (mode = 'Focus' OR mode = 'Free Timer')
                AND start_time >= date('now', ?, 'localtime')
                GROUP BY day
                ORDER BY day ASC
            """
            cursor.execute(query, (f'-{days-1} days',))
            rows = cursor.fetchall()
            db_data = {row['day']: row['minutes'] for row in rows}
            
            for i in range(days - 1, -1, -1):
                date_calc = datetime.date.today() - datetime.timedelta(days=i)
                date_str = date_calc.strftime('%Y-%m-%d')
                minutes = db_data.get(date_str, 0)
                display_date = date_calc.strftime('%d %b')
                data.append((display_date, minutes))
        except: pass
        finally: conn.close()
    return data

def get_hourly_productivity_v2():
    """Saatlik verimlilik (sadece Focus ve Free Timer modları)."""
    conn = create_connection()
    hours_data = [0] * 24
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%H', start_time) as hour, 
                       SUM(duration_seconds) / 60 as minutes
                FROM sessions_v2
                WHERE mode = 'Focus' OR mode = 'Free Timer'
                GROUP BY hour
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                hours_data[int(row['hour'])] = int(row['minutes'])
        except: pass
        finally: conn.close()
    return hours_data

def get_completion_rate_v2():
    """Tamamlama oranı (sadece Focus ve Free Timer modları)."""
    conn = create_connection()
    stats = {'completed': 0, 'interrupted': 0}
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT completed, COUNT(*) as count 
                FROM sessions_v2 
                WHERE mode = 'Focus' OR mode = 'Free Timer'
                GROUP BY completed
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                if row['completed'] == 1: stats['completed'] = row['count']
                else: stats['interrupted'] = row['count']
        except: pass
        finally: conn.close()
    return stats

# mfdp_app/db_manager.py (En alta ekle)

def get_focus_quality_stats():
    """
    Oturumları kesinti sayısına göre gruplar (sadece Focus ve Free Timer modları).
    Dönüş: {'Deep Work': 15, 'Moderate': 5, 'Distracted': 2}
    """
    conn = create_connection()
    stats = {'Deep Work (0 Kesinti)': 0, 'Moderate (1-2 Kesinti)': 0, 'Distracted (3+ Kesinti)': 0}
    
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT interruption_count, COUNT(*) as count
                FROM sessions_v2
                WHERE mode = 'Focus' OR mode = 'Free Timer'
                GROUP BY interruption_count
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                count = row['interruption_count']
                qty = row['count']
                
                if count == 0:
                    stats['Deep Work (0 Kesinti)'] += qty
                elif count <= 2:
                    stats['Moderate (1-2 Kesinti)'] += qty
                else:
                    stats['Distracted (3+ Kesinti)'] += qty
        except: pass
        finally: conn.close()
    return stats

# --- TASK FONKSİYONLARI ---
def insert_task(name, tag, planned_duration_minutes=None, color=None, parent_id=None, is_completed=False):
    """Yeni task oluştur."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO tasks (name, tag, planned_duration_minutes, created_at, color, parent_id, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, tag, planned_duration_minutes, created_at, color, parent_id, is_completed))
            task_id = cursor.lastrowid
            conn.commit()
            
            # Tag yoksa oluştur
            cursor.execute("SELECT name FROM tags WHERE name = ?", (tag,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO tags (name, color, created_at)
                    VALUES (?, ?, ?)
                """, (tag, color, created_at))
                conn.commit()
            
            return task_id
        except sqlite3.IntegrityError:
            return None  # Duplicate name
        except sqlite3.Error as e:
            print(f"Task ekleme hatası: {e}")
            return None
        finally:
            conn.close()
    return None

def update_task(task_id, name=None, tag=None, planned_duration_minutes=None, color=None, is_active=None, parent_id=None, is_completed=None):
    """Task güncelle."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if tag is not None:
                updates.append("tag = ?")
                params.append(tag)
            if planned_duration_minutes is not None:
                updates.append("planned_duration_minutes = ?")
                params.append(planned_duration_minutes)
            if color is not None:
                updates.append("color = ?")
                params.append(color)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            if parent_id is not None:
                updates.append("parent_id = ?")
                params.append(parent_id)
            if is_completed is not None:
                updates.append("is_completed = ?")
                params.append(is_completed)
            
            if updates:
                params.append(task_id)
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Task güncelleme hatası: {e}")
            return False
        finally:
            conn.close()
    return False

def get_task_by_id(task_id):
    """ID'ye göre task getir."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                from mfdp_app.models.data_models import Task
                return Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                )
        except Exception as e:
            print(f"Task getirme hatası: {e}")
        finally:
            conn.close()
    return None

def get_all_tasks(include_inactive=False):
    """Tüm taskları getir."""
    conn = create_connection()
    tasks = []
    if conn:
        try:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            else:
                cursor.execute("SELECT * FROM tasks WHERE is_active = 1 ORDER BY created_at DESC")
            
            from mfdp_app.models.data_models import Task
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        except Exception as e:
            print(f"Task listesi getirme hatası: {e}")
        finally:
            conn.close()
    return tasks

def get_tasks_by_tag(tag):
    """Tag'a göre taskları getir."""
    conn = create_connection()
    tasks = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE tag = ? AND is_active = 1 ORDER BY created_at DESC", (tag,))
            
            from mfdp_app.models.data_models import Task
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        except Exception as e:
            print(f"Tag task listesi getirme hatası: {e}")
        finally:
            conn.close()
    return tasks

def delete_task(task_id):
    """Task'ı soft delete yap (is_active=False)."""
    return update_task(task_id, is_active=False)

# --- TAG FONKSİYONLARI ---
def get_all_tags():
    """Tüm tagları getir."""
    conn = create_connection()
    tags = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name, color FROM tags ORDER BY name")
            for row in cursor.fetchall():
                tags.append({
                    'name': row['name'],
                    'color': row['color']
                })
        except Exception as e:
            print(f"Tag listesi getirme hatası: {e}")
        finally:
            conn.close()
    return tags

def assign_color_to_tag(tag, color):
    """Tag'a renk ata."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Tag var mı kontrol et
            cursor.execute("SELECT name FROM tags WHERE name = ?", (tag,))
            if cursor.fetchone():
                cursor.execute("UPDATE tags SET color = ? WHERE name = ?", (color, tag))
            else:
                created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO tags (name, color, created_at) VALUES (?, ?, ?)", (tag, color, created_at))
            
            # Task'lardaki tag renklerini de güncelle
            cursor.execute("UPDATE tasks SET color = ? WHERE tag = ?", (color, tag))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Tag renk atama hatası: {e}")
            return False
        finally:
            conn.close()
    return False

def get_tag_time_summary(tag, days=None):
    """Tag için toplam süre (dakika) - sadece Focus ve Free Timer modları."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if days:
                query = """
                    SELECT SUM(duration_seconds) / 60.0 as total_minutes
                    FROM sessions_v2
                    WHERE category = ?
                    AND (mode = 'Focus' OR mode = 'Free Timer')
                    AND start_time >= date('now', ?, 'localtime')
                """
                cursor.execute(query, (tag, f'-{days} days'))
            else:
                query = """
                    SELECT SUM(duration_seconds) / 60.0 as total_minutes
                    FROM sessions_v2
                    WHERE category = ?
                    AND (mode = 'Focus' OR mode = 'Free Timer')
                """
                cursor.execute(query, (tag,))
            
            row = cursor.fetchone()
            return row['total_minutes'] if row and row['total_minutes'] else 0.0
        except Exception as e:
            print(f"Tag süre özeti hatası: {e}")
            return 0.0
        finally:
            conn.close()
    return 0.0

def get_task_time_summary(task_id, days=None):
    """Task için toplam süre (dakika)."""
    conn = create_connection()
    if conn:
        try:
            # Önce task adını al
            task = get_task_by_id(task_id)
            if not task:
                return 0.0
            
            cursor = conn.cursor()
            if days:
                query = """
                    SELECT SUM(duration_seconds) / 60.0 as total_minutes
                    FROM sessions_v2
                    WHERE task_name = ?
                    AND (mode = 'Focus' OR mode = 'Free Timer')
                    AND start_time >= date('now', ?, 'localtime')
                """
                cursor.execute(query, (task.name, f'-{days} days'))
            else:
                query = """
                    SELECT SUM(duration_seconds) / 60.0 as total_minutes
                    FROM sessions_v2
                    WHERE task_name = ?
                    AND (mode = 'Focus' OR mode = 'Free Timer')
                """
                cursor.execute(query, (task.name,))
            
            row = cursor.fetchone()
            return row['total_minutes'] if row and row['total_minutes'] else 0.0
        except Exception as e:
            print(f"Task süre özeti hatası: {e}")
            return 0.0
        finally:
            conn.close()
    return 0.0

def get_daily_trend_by_tag(tag, days=7):
    """Tag bazlı günlük trend (sadece Focus ve Free Timer modları)."""
    conn = create_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%Y-%m-%d', start_time) as day, 
                       SUM(duration_seconds) / 60 as minutes
                FROM sessions_v2
                WHERE category = ?
                AND (mode = 'Focus' OR mode = 'Free Timer')
                AND start_time >= date('now', ?, 'localtime')
                GROUP BY day
                ORDER BY day ASC
            """
            cursor.execute(query, (tag, f'-{days-1} days'))
            rows = cursor.fetchall()
            db_data = {row['day']: row['minutes'] for row in rows}
            
            for i in range(days - 1, -1, -1):
                date_calc = datetime.date.today() - datetime.timedelta(days=i)
                date_str = date_calc.strftime('%Y-%m-%d')
                minutes = db_data.get(date_str, 0)
                display_date = date_calc.strftime('%d %b')
                data.append((display_date, minutes))
        except: pass
        finally: conn.close()
    return data

# --- RECURSIVE TASK FONKSİYONLARI ---
def get_child_tasks(parent_id):
    """Bir task'ın alt görevlerini getir."""
    conn = create_connection()
    tasks = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE parent_id = ? AND is_active = 1 ORDER BY created_at ASC", (parent_id,))
            
            from mfdp_app.models.data_models import Task
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        except Exception as e:
            print(f"Alt görev getirme hatası: {e}")
        finally:
            conn.close()
    return tasks

def get_root_tasks():
    """Tüm root (parent_id=None) görevleri getir."""
    conn = create_connection()
    tasks = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE parent_id IS NULL AND is_active = 1 ORDER BY created_at ASC")
            
            from mfdp_app.models.data_models import Task
            for row in cursor.fetchall():
                tasks.append(Task(
                    id=row['id'],
                    name=row['name'],
                    tag=row['tag'],
                    planned_duration_minutes=row['planned_duration_minutes'],
                    created_at=datetime.datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    is_active=bool(row['is_active']),
                    color=row['color'],
                    parent_id=row['parent_id'] if row['parent_id'] else None,
                    is_completed=bool(row['is_completed']) if row['is_completed'] is not None else False
                ))
        except Exception as e:
            print(f"Root görev getirme hatası: {e}")
        finally:
            conn.close()
    return tasks

def get_all_subtasks_recursive(task_id):
    """Bir task'ın tüm alt görevlerini recursive olarak getir."""
    all_subtasks = []
    direct_children = get_child_tasks(task_id)
    all_subtasks.extend(direct_children)
    
    for child in direct_children:
        all_subtasks.extend(get_all_subtasks_recursive(child.id))
    
    return all_subtasks

# --- ATOMIC ANALYZER FONKSİYONLARI (Event Sourcing) ---

def insert_atomic_events(events_data):
    """
    Atomik olayları toplu olarak veritabanına ekle.
    
    AtomicAnalyzer'dan flush_events() çağrısı ile kullanılır.
    Her olay ham veri olarak saklanır, bu sayede gelecekte farklı analizler yapılabilir.
    
    Args:
        events_data: Olaylar listesi, her biri şu yapıda:
        {
            'event_type': 'interruption_detected',
            'session_id': 123,
            'elapsed_seconds': 180,
            'timestamp': '2025-01-18T10:30:45.123456',
            'metadata': {'reason': 'user_pause', 'severity': 'low', ...}
        }
    
    Returns:
        True başarılı, False hata
    """
    if not events_data:
        return True
    
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        import json
        
        for event in events_data:
            # metadata sözlüğünü JSON string'e dönüştür
            metadata_json = json.dumps(event.get('metadata', {})) if event.get('metadata') else None
            
            cursor.execute("""
                INSERT INTO atomic_events 
                (session_id, event_type, timestamp, elapsed_seconds, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                event['session_id'],
                event['event_type'],
                event['timestamp'],
                event['elapsed_seconds'],
                metadata_json
            ))
        
        conn.commit()
        print(f"✅ {len(events_data)} atomik olay veritabanına kaydedildi.")
        return True
        
    except sqlite3.Error as e:
        print(f"Atomik olay ekleme hatası: {e}")
        return False
    finally:
        conn.close()

def get_atomic_events(session_id):
    """
    Belirli bir oturum için tüm atomik olayları getir.
    
    Oturum sırasında kaydedilen tüm olayları kronolojik sıraya göre döndürür.
    
    Args:
        session_id: Oturum ID'si (sessions_v2 tablosundan)
    
    Returns:
        Olaylar listesi, her biri şu yapıda:
        {
            'id': 1,
            'session_id': 123,
            'event_type': 'interruption_detected',
            'elapsed_seconds': 180,
            'timestamp': '2025-01-18T10:30:45',
            'metadata': {...},
            'created_at': '2025-01-18T10:30:45'
        }
    """
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, session_id, event_type, elapsed_seconds, timestamp, metadata, created_at
            FROM atomic_events
            WHERE session_id = ?
            ORDER BY elapsed_seconds ASC, id ASC
        """, (session_id,))
        
        events = []
        import json
        for row in cursor.fetchall():
            # metadata JSON string'ini sözlüğe dönüştür
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
        
    except sqlite3.Error as e:
        print(f"Atomik olay getirme hatası: {e}")
        return []
    finally:
        conn.close()

def get_atomic_events_by_range(start_date, end_date):
    """
    Belirtilen tarih aralığındaki tüm atomik olayları getir.
    
    Analiz amaçlı sorgulamalar için (örn. "bu haftanın olayları").
    
    Args:
        start_date: Başlangıç tarihi (datetime nesnesi)
        end_date: Bitiş tarihi (datetime nesnesi)
    
    Returns:
        Olaylar listesi
    """
    conn = create_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        # ISO format'a dönüştür
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        cursor.execute("""
            SELECT id, session_id, event_type, elapsed_seconds, timestamp, metadata, created_at
            FROM atomic_events
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC, id ASC
        """, (start_str, end_str))
        
        events = []
        import json
        for row in cursor.fetchall():
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
        
    except sqlite3.Error as e:
        print(f"Tarih aralığı olay getirme hatası: {e}")
        return []
    finally:
        conn.close()

def get_interruption_events(session_id):
    """
    Belirli bir oturumdaki kesinti olaylarını getir.
    
    Sadece 'interruption_detected' türü olayları filtreler.
    
    Args:
        session_id: Oturum ID'si
    
    Returns:
        Kesinti olayları listesi
    """
    all_events = get_atomic_events(session_id)
    return [e for e in all_events if e['event_type'] == 'interruption_detected']

def get_focus_shift_events(session_id):
    """
    Belirli bir oturumdaki fokus değişim olaylarını getir.
    
    Sadece 'focus_shift_detected' türü olayları filtreler.
    
    Args:
        session_id: Oturum ID'si
    
    Returns:
        Fokus değişim olayları listesi
    """
    all_events = get_atomic_events(session_id)
    return [e for e in all_events if e['event_type'] == 'focus_shift_detected']

def get_distraction_events(session_id):
    """
    Belirli bir oturumdaki dikkati dağıtıcı olayları getir.
    
    Sadece 'distraction_identified' türü olayları filtreler.
    
    Args:
        session_id: Oturum ID'si
    
    Returns:
        Dikkati dağıtıcı olaylar listesi
    """
    all_events = get_atomic_events(session_id)
    return [e for e in all_events if e['event_type'] == 'distraction_identified']

def delete_atomic_events_for_session(session_id):
    """
    Bir oturumun tüm atomik olaylarını sil (cascade delete).
    
    Oturum silindiğinde ilişkili olayları da silmek için kullanılır.
    
    Args:
        session_id: Oturum ID'si
    
    Returns:
        True başarılı, False hata
    """
    conn = create_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM atomic_events WHERE session_id = ?", (session_id,))
        conn.commit()
        print(f"✅ Oturum {session_id} için tüm atomik olaylar silindi.")
        return True
    except sqlite3.Error as e:
        print(f"Atomik olay silme hatası: {e}")
        return False
    finally:
        conn.close()

def get_event_statistics_for_session(session_id):
    """
    Bir oturum için atomik olay istatistiklerini getir.
    
    Kaç kesinti, kaç fokus değişimi vb. bilgisini hızlıca almak için.
    
    Args:
        session_id: Oturum ID'si
    
    Returns:
        İstatistikler sözlüğü:
        {
            'total_events': 42,
            'interruptions': 3,
            'focus_shifts': 5,
            'distractions': 2,
            'environment_changes': 1,
            'breaks': 0,
            'event_types': {...}
        }
    """
    events = get_atomic_events(session_id)
    
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