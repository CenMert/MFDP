"""
Plan Repository - eğer-ise planları (implementation intentions) ve sonuç kayıtları.

Plan: "EĞER <gün(ler) + saat | durum> İSE <görev / eylem>".
weekdays: '0,2,4' gibi virgüllü liste (0 = Pazartesi). time: 'HH:MM' ya da NULL
(yalnızca durum ipucu olan planlar zamanla tetiklenmez, listede hatırlatılır).
plan_log: her plan için mantıksal gün başına sonuç ('started' | 'skipped' | 'snoozed').
"""

import datetime
from typing import Dict, List, Optional

from mfdp_app.db.base_repository import BaseRepository

_TIME_FMT = '%Y-%m-%d %H:%M:%S'


class PlanRepository(BaseRepository):
    """Handle if-then plan CRUD and outcome logging."""

    @staticmethod
    def add_plan(weekdays: List[int], time: Optional[str], cue: Optional[str],
                 task_id: Optional[int], action: Optional[str]) -> Optional[int]:
        return BaseRepository.execute_query(
            "INSERT INTO if_then_plans (weekdays, time, cue, task_id, action, is_active, created_at) "
            "VALUES (?, ?, ?, ?, ?, 1, ?)",
            (",".join(str(d) for d in sorted(weekdays)), time, cue, task_id, action,
             datetime.datetime.now().strftime(_TIME_FMT)),
            commit=True
        )

    @staticmethod
    def delete_plan(plan_id: int) -> bool:
        """Soft delete: geçmiş sonuçlar analiz için kalır."""
        return BaseRepository.execute_query(
            "UPDATE if_then_plans SET is_active = 0 WHERE id = ?", (plan_id,), commit=True
        ) is not None

    @staticmethod
    def get_active_plans() -> List[Dict]:
        rows = BaseRepository.execute_query(
            """
            SELECT p.id, p.weekdays, p.time, p.cue, p.task_id, p.action, p.created_at, t.name AS task_name
            FROM if_then_plans p LEFT JOIN tasks t ON t.id = p.task_id
            WHERE p.is_active = 1
            ORDER BY COALESCE(p.time, '99:99'), p.id
            """,
            fetch_all=True
        )
        plans = []
        for r in rows or []:
            d = dict(r)
            d['weekdays'] = [int(x) for x in d['weekdays'].split(',') if x != '']
            plans.append(d)
        return plans

    @staticmethod
    def get_plans_for_weekday(weekday: int) -> List[Dict]:
        return [p for p in PlanRepository.get_active_plans() if weekday in p['weekdays']]

    @staticmethod
    def log_outcome(plan_id: int, day: datetime.date, outcome: str,
                    session_id: Optional[int] = None) -> Optional[int]:
        return BaseRepository.execute_query(
            "INSERT INTO plan_log (plan_id, day, outcome, session_id, logged_at) VALUES (?, ?, ?, ?, ?)",
            (plan_id, day.isoformat(), outcome, session_id, datetime.datetime.now().strftime(_TIME_FMT)),
            commit=True
        )

    @staticmethod
    def attach_session(log_id: int, session_id: int) -> bool:
        return BaseRepository.execute_query(
            "UPDATE plan_log SET session_id = ? WHERE id = ?", (session_id, log_id), commit=True
        ) is not None

    @staticmethod
    def get_outcomes_for_day(day: datetime.date) -> Dict[int, str]:
        """plan_id -> o günün son kesin sonucu ('started' / 'skipped'); ertelemeler sayılmaz."""
        rows = BaseRepository.execute_query(
            "SELECT plan_id, outcome FROM plan_log WHERE day = ? AND outcome != 'snoozed' ORDER BY id",
            (day.isoformat(),),
            fetch_all=True
        )
        return {r['plan_id']: r['outcome'] for r in rows or []}

    @staticmethod
    def get_adherence(days: int = 28) -> Dict[str, int]:
        """
        Son N günde zamanlı planların kaç kez tetiklendiği ve sonuçları.
        Kayıt düşmeyen tetiklenmeler (uygulama kapalıydı) 'missed' sayılır.
        """
        today = datetime.date.today()
        start = today - datetime.timedelta(days=days - 1)
        plans = [p for p in PlanRepository.get_active_plans() if p['time']]
        rows = BaseRepository.execute_query(
            "SELECT plan_id, day, outcome FROM plan_log WHERE day >= ? AND outcome != 'snoozed'",
            (start.isoformat(),),
            fetch_all=True
        )
        logged = {(r['plan_id'], r['day']): r['outcome'] for r in rows or []}
        stats = {'due': 0, 'started': 0, 'skipped': 0, 'missed': 0}
        for i in range(days):
            day = start + datetime.timedelta(days=i)
            for p in plans:
                if day.weekday() not in p['weekdays'] or day.isoformat() < p['created_at'][:10]:
                    continue
                outcome = logged.get((p['id'], day.isoformat()))
                if day == today and not outcome:
                    continue  # bugün henüz cevaplanmadı: kaçırıldı sayma
                stats['due'] += 1
                stats[outcome or 'missed'] += 1
        return stats
