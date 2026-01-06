import sqlite3
import datetime
import random

DB_NAME = 'focus_tracker.db'

def create_connection():
    return sqlite3.connect(DB_NAME)

def seed_database():
    """
    Yeni timer yapısına (FocusSession + PmdrCountdownTimer) uygun test verisi oluşturur.
    - Gerçek task'lar oluşturur
    - Gerçekçi interruption pattern'leri ekler
    - active_seconds (duraklatmalar hariç) kullanır
    - Interruptions tablosuna veri ekler (eğer varsa)
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    print("🌱 Veritabanı tohumlanıyor (Yeni Timer Yapısına Uygun)...")
    
    # Mevcut verileri temizle
    cursor.execute("DELETE FROM sessions_v2")
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM tags")
    
    # Interruptions tablosu var mı kontrol et ve temizle
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='interruptions'
    """)
    interruptions_table_exists = cursor.fetchone() is not None
    
    if interruptions_table_exists:
        try:
            cursor.execute("DELETE FROM interruptions")
        except sqlite3.OperationalError:
            pass  # Tablo yoksa hata verme
    
    conn.commit()
    print("🧹 Eski veriler temizlendi.")
    
    # Task'lar ve Tag'ler oluştur
    print("📋 Task'lar ve Tag'ler oluşturuluyor...")
    tasks_data = [
        {"name": "Python Projesi Geliştirme", "tag": "Development", "color": "#89b4fa"},
        {"name": "API Dokümantasyonu Yazma", "tag": "Documentation", "color": "#a6e3a1"},
        {"name": "Kod Review", "tag": "Development", "color": "#89b4fa"},
        {"name": "Test Yazma", "tag": "Testing", "color": "#f9e2af"},
        {"name": "Veritabanı Optimizasyonu", "tag": "Development", "color": "#89b4fa"},
        {"name": "UI Tasarımı", "tag": "Design", "color": "#f38ba8"},
        {"name": "Bug Fix", "tag": "Development", "color": "#89b4fa"},
        {"name": "Meeting Hazırlığı", "tag": "Planning", "color": "#cba6f7"},
        {"name": "Email Okuma", "tag": "Communication", "color": "#fab387"},
        {"name": "Öğrenme - Yeni Teknoloji", "tag": "Learning", "color": "#94e2d5"},
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            # Task ekle
            cursor.execute("""
                INSERT INTO tasks (name, tag, planned_duration_minutes, created_at, color, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                task_data["name"],
                task_data["tag"],
                random.choice([25, 50, 90]),  # Planlanan süre
                created_at,
                task_data["color"],
                1
            ))
            task_id = cursor.lastrowid
            
            # Tag ekle (yoksa)
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
            pass  # Duplicate task
    
    conn.commit()
    print(f"✅ {len(created_tasks)} task oluşturuldu.")
    
    # Son 14 gün için session verileri oluştur
    print("📊 Session verileri oluşturuluyor...")
    modes = ['Focus'] * 8 + ['Short Break'] * 3 + ['Long Break'] * 1
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=14)
    total_sessions = 0
    total_interruptions = 0
    
    for day_offset in range(14):
        current_day = start_date + datetime.timedelta(days=day_offset)
        
        # Hafta sonları daha az session
        if current_day.weekday() >= 5:
            num_sessions = random.randint(0, 4)
        else:
            num_sessions = random.randint(3, 12)
        
        start_hour = 9.0
        
        for session_num in range(num_sessions):
            # Saati ileri sar
            start_hour += random.uniform(0.5, 2.5)
            if start_hour >= 24:
                start_hour -= 24
            
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            session_start = current_day.replace(
                hour=int(start_hour),
                minute=minute,
                second=second
            )
            
            # Mod seçimi
            mode = random.choice(modes)
            
            # Planlanan süre
            planned_minutes = 25
            if mode == 'Short Break':
                planned_minutes = 5
            elif mode == 'Long Break':
                planned_minutes = 15
            
            # Tamamlandı mı? (%75 ihtimalle evet)
            completed = 1 if random.random() > 0.25 else 0
            
            # Gerçekleşen süre (active_seconds - duraklatmalar hariç)
            if completed:
                # Tamamlandıysa, planlanan süre kadar çalışıldı
                active_seconds = planned_minutes * 60
            else:
                # Yarım kaldıysa, 2-20 dakika arası
                active_seconds = random.randint(2 * 60, min(20 * 60, (planned_minutes - 2) * 60))
            
            # Duraklatma süreleri (pause_seconds)
            # %40 ihtimalle duraklatma var
            pause_seconds = 0
            pause_count = 0
            if random.random() < 0.4 and mode == 'Focus':
                pause_count = random.randint(1, 3)
                # Her duraklatma 30 saniye ile 5 dakika arası
                pause_seconds = sum([random.randint(30, 5 * 60) for _ in range(pause_count)])
            
            # Toplam süre = aktif süre + duraklatma süresi
            total_seconds = active_seconds + pause_seconds
            
            # Session bitiş zamanı
            session_end = session_start + datetime.timedelta(seconds=total_seconds)
            
            # Task seçimi (Focus modunda %80 ihtimalle task var)
            task_name = None
            category = None
            if mode == 'Focus' and random.random() < 0.8 and created_tasks:
                selected_task = random.choice(created_tasks)
                task_name = selected_task["name"]
                category = selected_task["tag"]
            
            # Interruption pattern'leri oluştur
            # 35-45 dakika arası daha fazla kesinti (pattern)
            interruption_count = 0
            interruption_seconds = []
            interruption_times = []
            interruption_types = []
            
            if mode == 'Focus' and active_seconds > 0:
                # Kesinti sayısı (0-4 arası)
                interruption_count = random.randint(0, 4)
                
                # Eğer kesinti varsa, zamanlarını belirle
                for i in range(interruption_count):
                    # Session içindeki saniye (0 ile active_seconds arası)
                    # Pattern: 35-45 dakika arası daha fazla kesinti (eğer session yeterince uzunsa)
                    if active_seconds >= 35 * 60 and random.random() < 0.3:  # %30 ihtimalle 35-45 dk arası
                        # 35-45 dakika arası (ama active_seconds'ı geçmemeli)
                        max_seconds = min(45 * 60, active_seconds)
                        seconds_into = random.randint(35 * 60, max_seconds)
                    else:
                        # Normal dağılım (tüm session boyunca)
                        seconds_into = random.randint(0, active_seconds)
                    
                    interruption_seconds.append(seconds_into)
                    
                    # Kesinti zamanı
                    interruption_time = session_start + datetime.timedelta(seconds=seconds_into)
                    interruption_times.append(interruption_time)
                    
                    # Kesinti tipi
                    interruption_types.append(random.choice(['pause', 'reset', 'mode_change']))
            
            # Session'ı veritabanına ekle
            cursor.execute("""
                INSERT INTO sessions_v2 (
                    start_time, end_time, duration_seconds,
                    planned_duration_minutes, mode, completed,
                    task_name, category, interruption_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_start.strftime('%Y-%m-%d %H:%M:%S'),
                session_end.strftime('%Y-%m-%d %H:%M:%S'),
                active_seconds,  # active_seconds kullanıyoruz (duraklatmalar hariç)
                planned_minutes,
                mode,
                completed,
                task_name,
                category,
                interruption_count
            ))
            
            session_id = cursor.lastrowid
            
            # Interruptions tablosuna ekle (eğer varsa)
            if interruptions_table_exists and interruption_count > 0:
                for sec, time, itype in zip(interruption_seconds, interruption_times, interruption_types):
                    cursor.execute("""
                        INSERT INTO interruptions (
                            session_id, seconds_into_session,
                            interruption_time, interruption_type
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        session_id,
                        sec,
                        time.strftime('%Y-%m-%d %H:%M:%S'),
                        itype
                    ))
                    total_interruptions += 1
            
            total_sessions += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Bitti!")
    print(f"   📊 {total_sessions} session eklendi")
    print(f"   📋 {len(created_tasks)} task oluşturuldu")
    if interruptions_table_exists:
        print(f"   🔔 {total_interruptions} interruption kaydedildi")
    else:
        print(f"   ⚠️  Interruptions tablosu henüz oluşturulmamış (sadece interruption_count kullanıldı)")

if __name__ == "__main__":
    seed_database()
