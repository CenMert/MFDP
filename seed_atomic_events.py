"""
atomic_events tablosuna gerçekçi örnek veri ekler (son 14 gün).
Kullanım: python seed_atomic_events.py
"""
import sqlite3
import random
import datetime

DB = "focus_tracker.db"
random.seed(42)

SESSION_IDS = [119, 120, 121, 122, 123]

# Sabah ve öğleden sonra yoğunlaşmış, gece seyrek
HOUR_WEIGHTS = [
    0.1, 0.0, 0.0, 0.0, 0.0, 0.1,   # 00-05
    0.3, 0.8, 1.5, 2.0, 2.5, 2.0,   # 06-11
    1.2, 1.5, 2.0, 2.5, 2.2, 1.8,   # 12-17
    1.5, 1.0, 0.8, 0.5, 0.3, 0.1,   # 18-23
]
total_weight = sum(HOUR_WEIGHTS)
HOUR_PROBS = [w / total_weight for w in HOUR_WEIGHTS]

EVENT_TYPES = [
    ("interruption_detected",  0.35),
    ("focus_shift_detected",   0.25),
    ("session_started",        0.15),
    ("session_completed",      0.10),
    ("milestone_reached",      0.08),
    ("distraction_identified", 0.05),
    ("dnd_toggled",            0.02),
]
event_pool, event_weights = zip(*EVENT_TYPES)


def random_ts(days_ago: int, hour: int) -> str:
    base = datetime.date.today() - datetime.timedelta(days=days_ago)
    dt = datetime.datetime(
        base.year, base.month, base.day,
        hour,
        random.randint(0, 59),
        random.randint(0, 59),
    )
    return dt.isoformat()


def main():
    con = sqlite3.connect(DB)

    # Mevcut örnek veriyi temizle (tekrar çalıştırmak için)
    deleted = con.execute(
        "DELETE FROM atomic_events WHERE session_id IN (119,120,121,122,123)"
    ).rowcount
    if deleted:
        print(f"{deleted} eski örnek kayıt silindi.")

    rows = []
    for days_ago in range(13, -1, -1):          # 14 gün
        n_events = random.randint(8, 25)
        for _ in range(n_events):
            hour = random.choices(range(24), weights=HOUR_PROBS)[0]
            ts = random_ts(days_ago, hour)
            etype = random.choices(event_pool, weights=event_weights)[0]
            sid = random.choice(SESSION_IDS)
            elapsed = random.randint(0, 1500)
            rows.append((sid, etype, ts, elapsed, None))

    con.executemany(
        """INSERT INTO atomic_events
           (session_id, event_type, timestamp, elapsed_seconds, metadata, created_at)
           VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
        rows
    )
    con.commit()
    con.close()
    print(f"{len(rows)} örnek atomic event eklendi ({len(rows)//14:.0f}/gün ortalama).")
    print("Uygulamayı açıp İstatistikler → Atomic Harita sekmesine gidin.")


if __name__ == "__main__":
    main()
