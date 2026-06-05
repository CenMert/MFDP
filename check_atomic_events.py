"""
atomic_events tablosunu görüntüler.
Kullanım: python check_atomic_events.py
"""
import sqlite3
import sys

DB = "focus_tracker.db"

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    # Tablo var mı?
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "atomic_events" not in tables:
        print("atomic_events tablosu henüz yok.")
        con.close()
        return

    total = con.execute("SELECT COUNT(*) FROM atomic_events").fetchone()[0]
    print(f"Toplam kayıt: {total}\n")

    if total == 0:
        print("Henüz kayıt yok. Uygulamayı açıp bir timer başlatın.")
        con.close()
        return

    # Olay türü dağılımı
    print("--- Olay Türü Dağılımı ---")
    for row in con.execute(
        "SELECT event_type, COUNT(*) as n FROM atomic_events GROUP BY event_type ORDER BY n DESC"
    ):
        print(f"  {row['event_type']:35s} {row['n']:>4}")

    # Son 20 olay
    print("\n--- Son 20 Olay ---")
    rows = con.execute(
        """SELECT id, session_id, event_type, elapsed_seconds, timestamp
           FROM atomic_events ORDER BY id DESC LIMIT 20"""
    ).fetchall()
    for r in reversed(rows):
        print(f"  [{r['id']:>4}] session={r['session_id']}  {r['event_type']:35s}  "
              f"+{r['elapsed_seconds']:>5}s  {r['timestamp']}")

    # Son 14 günlük gün/saat özeti
    print("\n--- Son 14 Gün, Saatlik Dağılım (top 10) ---")
    for row in con.execute(
        """SELECT strftime('%Y-%m-%d', timestamp) as day,
                  CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                  COUNT(*) as n
           FROM atomic_events
           WHERE timestamp >= date('now', '-13 days')
           GROUP BY day, hour
           ORDER BY n DESC
           LIMIT 10"""
    ):
        print(f"  {row['day']}  {row['hour']:02d}:00  →  {row['n']} olay")

    con.close()

if __name__ == "__main__":
    main()
