import sqlite3
import datetime
import random

DB_NAME = 'focus_tracker.db'

def create_connection():
    return sqlite3.connect(DB_NAME)

def seed_database():
    conn = create_connection()
    cursor = conn.cursor()
    
    print("🌱 Veritabanı tohumlanıyor (Fake Data Injection)...")
    
    # Mevcut verileri temizlemek ister misin? (İsteğe bağlı, şimdilik temizleyelim ki grafik net olsun)
    cursor.execute("DELETE FROM sessions_v2")
    conn.commit()
    print("🧹 Eski veriler temizlendi.")

    # Son 14 gün için veri üretelim
    modes = ['Focus'] * 8 + ['Short Break'] * 3 + ['Long Break'] * 1 # Ağırlıklı olarak Focus olsun
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=14)
    
    total_inserted = 0
    
    for day_offset in range(14):
        current_day = start_date + datetime.timedelta(days=day_offset)
        
        # O gün kaç oturum yapılsın? (0 ile 12 arası rastgele)
        # Hafta sonları daha az olsun (Cumartesi=5, Pazar=6)
        if current_day.weekday() >= 5:
            num_sessions = random.randint(0, 4)
        else:
            num_sessions = random.randint(3, 12)
            
        # Rastgele saatler belirle (09:00 ile 23:00 arası ağırlıklı)
        start_hour = 9
        
        for _ in range(num_sessions):
            # Saati biraz ileri sar
            start_hour += random.uniform(0.5, 2.0) 
            if start_hour >= 24: start_hour -= 24
            
            # Dakika ve saniye
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            # Session Başlangıç Zamanı
            session_start = current_day.replace(hour=int(start_hour), minute=minute, second=second)
            
            # Mod Seçimi
            mode = random.choice(modes)
            
            # Süreler (Planlanan)
            planned = 25
            if mode == 'Short Break': planned = 5
            elif mode == 'Long Break': planned = 15
            
            # Tamamlandı mı? (%80 ihtimalle evet)
            completed = 1 if random.random() > 0.2 else 0
            
            # Gerçekleşen Süre
            if completed:
                duration = planned * 60
            else:
                # Yarım kaldıysa 2 dk ile 20 dk arası bir yerde kesilsin
                duration = random.randint(2 * 60, (planned - 2) * 60)
            
            session_end = session_start + datetime.timedelta(seconds=duration)
            
            # Veritabanına Ekle
            cursor.execute("""
                INSERT INTO sessions_v2 (
                    start_time, end_time, duration_seconds, 
                    planned_duration_minutes, mode, completed, 
                    task_name, interruption_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_start.strftime('%Y-%m-%d %H:%M:%S'),
                session_end.strftime('%Y-%m-%d %H:%M:%S'),
                duration,
                planned,
                mode,
                completed,
                "Fake Task",
                random.randint(0, 3) # 0-3 arası kesinti
            ))
            total_inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Bitti! Toplam {total_inserted} adet sahte oturum eklendi.")

if __name__ == "__main__":
    seed_database()