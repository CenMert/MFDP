"""
Review Repository - konu başına aralıklı tekrar durumu (review_state) ve tekrar geçmişi (review_log).

Konu = bir görev (task). Tarihler `YYYY-MM-DD` (mantıksal gün). review_log her tekrarın
öncesindeki durumu da saklar; böylece aynı oturum için hatırlama puanı değiştirilirse
önceki durum geri yüklenip yeniden uygulanabilir.
"""

import datetime
from typing import Dict, List, Optional, Tuple

from mfdp_app.db.base_repository import BaseRepository

_TIME_FMT = '%Y-%m-%d %H:%M:%S'


class ReviewRepository(BaseRepository):
    """Handle review state and log operations."""

    # ---- durum ---------------------------------------------------------
    @staticmethod
    def get_state(task_id: int) -> Optional[Dict]:
        row = BaseRepository.execute_query(
            "SELECT * FROM review_state WHERE task_id = ?", (task_id,), fetch_one=True)
        return dict(row) if row else None

    @staticmethod
    def get_all_states() -> List[Dict]:
        rows = BaseRepository.execute_query("SELECT * FROM review_state", fetch_all=True)
        return [dict(r) for r in rows] if rows else []

    @staticmethod
    def create_state(task_id: int, next_due: str, last_review: str,
                     learned_on: Optional[str] = None, source: str = 'calisma') -> bool:
        """Konu için durum aç (varsa dokunmaz). source: 'ders' (derste işlendi) | 'calisma'."""
        return BaseRepository.execute_query(
            "INSERT OR IGNORE INTO review_state "
            "(task_id, step, next_due, last_review, lapses, created_at, learned_on, source) "
            "VALUES (?, 0, ?, ?, 0, ?, ?, ?)",
            (task_id, next_due, last_review, datetime.datetime.now().strftime(_TIME_FMT),
             learned_on or last_review, source),
            commit=True
        ) is not None

    @staticmethod
    def get_lecture_topics(course_ids: List[int], since: str) -> List[Dict]:
        """Derste işlenen konular (en yeni önce): bir dersin alt görevleri, `since` tarihinden itibaren."""
        if not course_ids:
            return []
        marks = ",".join("?" * len(course_ids))
        rows = BaseRepository.execute_query(
            f"SELECT t.id, t.name, t.parent_id, r.learned_on FROM review_state r "
            f"JOIN tasks t ON t.id = r.task_id "
            f"WHERE r.source = 'ders' AND t.parent_id IN ({marks}) AND r.learned_on >= ? "
            f"ORDER BY r.learned_on DESC, t.id DESC",
            tuple(course_ids) + (since,),
            fetch_all=True
        )
        return [dict(r) for r in rows] if rows else []

    @staticmethod
    def set_state(task_id: int, step: int, next_due: str, last_review: str, lapses: int) -> bool:
        return BaseRepository.execute_query(
            "UPDATE review_state SET step = ?, next_due = ?, last_review = ?, lapses = ? WHERE task_id = ?",
            (step, next_due, last_review, lapses, task_id),
            commit=True
        ) is not None

    # ---- geçmiş --------------------------------------------------------
    @staticmethod
    def get_log_for_session(session_id: int) -> Optional[Dict]:
        row = BaseRepository.execute_query(
            "SELECT * FROM review_log WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,), fetch_one=True)
        return dict(row) if row else None

    @staticmethod
    def add_log(task_id: int, session_id: Optional[int], recall: int, day: str, prev: Dict) -> Optional[int]:
        return BaseRepository.execute_query(
            "INSERT INTO review_log (task_id, session_id, recall, day, reviewed_at, "
            "prev_step, prev_next_due, prev_last_review, prev_lapses) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task_id, session_id, recall, day, datetime.datetime.now().strftime(_TIME_FMT),
             prev['step'], prev['next_due'], prev['last_review'], prev['lapses']),
            commit=True
        )

    @staticmethod
    def delete_log(log_id: int) -> bool:
        return BaseRepository.execute_query(
            "DELETE FROM review_log WHERE id = ?", (log_id,), commit=True) is not None

    @staticmethod
    def count_reviews_on(day: str) -> int:
        row = BaseRepository.execute_query(
            "SELECT COUNT(*) AS n FROM review_log WHERE day = ?", (day,), fetch_one=True)
        return row['n'] if row else 0

    # ---- ders düzeyinde takip anahtarı ----------------------------------
    @staticmethod
    def set_course_tracked(task_id: int, tracked: bool) -> bool:
        """Dersi (ana görev) tekrar takibine al / çıkar. Kapalıyken hiçbir hatırlatma üretilmez."""
        return BaseRepository.execute_query(
            "UPDATE tasks SET review_enabled = ? WHERE id = ?", (1 if tracked else 0, task_id), commit=True
        ) is not None

    @staticmethod
    def get_tracked_course_ids() -> set:
        rows = BaseRepository.execute_query(
            "SELECT id FROM tasks WHERE parent_id IS NULL AND is_active = 1 AND review_enabled = 1",
            fetch_all=True)
        return {r['id'] for r in rows} if rows else set()

    # ---- yardımcı sorgular --------------------------------------------
    @staticmethod
    def task_id_by_name(name: Optional[str]) -> Optional[int]:
        """Oturumlar görevi ada göre tutar (tasks.name UNIQUE)."""
        if not name:
            return None
        row = BaseRepository.execute_query(
            "SELECT id FROM tasks WHERE name = ?", (name,), fetch_one=True)
        return row['id'] if row else None

    @staticmethod
    def last_session_day(task_name: str) -> Optional[str]:
        """Görevde son iş oturumunun günü (takvim günü) ya da None."""
        row = BaseRepository.execute_query(
            "SELECT MAX(start_time) AS t FROM sessions_v2 "
            "WHERE task_name = ? AND mode IN ('Focus', 'Free Timer')",
            (task_name,), fetch_one=True)
        return row['t'][:10] if row and row['t'] else None

    @staticmethod
    def feedback_fill_rate(since: datetime.datetime) -> Tuple[int, int]:
        """(etiketlenen, toplam) iş oturumu sayısı: geri bildirim şeridi ne kadar kullanılıyor."""
        row = BaseRepository.execute_query(
            "SELECT COUNT(*) AS n, COALESCE(SUM(session_kind IS NOT NULL), 0) AS k FROM sessions_v2 "
            "WHERE mode IN ('Focus', 'Free Timer') AND start_time >= ?",
            (since.strftime(_TIME_FMT),), fetch_one=True)
        return (row['k'], row['n']) if row else (0, 0)
