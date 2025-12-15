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

    conn.commit()
    print("Veritabanı V2 Şeması Hazır.")

# --- KAYIT FONKSİYONU ---
def log_session_v2(start_time, end_time, duration_sec, planned_min, mode, completed, task_name=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions_v2 (
                    start_time, end_time, duration_seconds, 
                    planned_duration_minutes, mode, completed, task_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                duration_sec, planned_min, mode, completed, task_name
            ))
            conn.commit()
            print(f"💾 V2 KAYIT: {mode} ({duration_sec} sn)")
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
    """Son X günün verileri."""
    conn = create_connection()
    data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%Y-%m-%d', start_time) as day, 
                       SUM(duration_seconds) / 60 as minutes
                FROM sessions_v2
                WHERE mode = 'Focus' 
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
    """Saatlik verimlilik."""
    conn = create_connection()
    hours_data = [0] * 24
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%H', start_time) as hour, 
                       SUM(duration_seconds) / 60 as minutes
                FROM sessions_v2
                WHERE mode = 'Focus'
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
    """Tamamlama oranı."""
    conn = create_connection()
    stats = {'completed': 0, 'interrupted': 0}
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT completed, COUNT(*) as count FROM sessions_v2 WHERE mode = 'Focus' GROUP BY completed"
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
    Focus oturumlarını kesinti sayısına göre gruplar.
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
                WHERE mode = 'Focus'
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