"""
PlanScheduler - eğer-ise planlarının saati geldiğinde sinyal yayar.

Saatli planlar, o mantıksal gün için henüz bir sonuç ('started' / 'skipped') yoksa
saatinden itibaren GRACE_MINUTES boyunca bir kez sorulur. Ertelenen plan, erteleme
süresi dolunca yeniden sorulur. Uygulama kapalıyken geçen planlar sorulmaz;
analizde 'missed' sayılır (PlanRepository.get_adherence).
"""

import datetime
from typing import Dict, Set, Tuple

from PySide6.QtCore import QObject, QTimer, Signal

from mfdp_app.core.daily_report import DAY_START_HOUR, logical_day
from mfdp_app.db.plan_repository import PlanRepository


class PlanScheduler(QObject):
    plan_due = Signal(dict)

    CHECK_INTERVAL_MS = 30_000
    GRACE_MINUTES = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prompted: Set[Tuple[int, datetime.date]] = set()
        self._snoozed_until: Dict[int, datetime.datetime] = {}
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.check)
        self._timer.start(self.CHECK_INTERVAL_MS)

    @staticmethod
    def due_time(plan: dict, day: datetime.date) -> datetime.datetime:
        """Planın o mantıksal gündeki tetiklenme anı (03:00 öncesi saatler ertesi takvim gününe düşer)."""
        hour, minute = (int(x) for x in plan['time'].split(':'))
        due = datetime.datetime.combine(day, datetime.time(hour, minute))
        if hour < DAY_START_HOUR:
            due += datetime.timedelta(days=1)
        return due

    def check(self):
        now = datetime.datetime.now()
        day = logical_day(now)
        decided = PlanRepository.get_outcomes_for_day(day)
        for plan in PlanRepository.get_plans_for_weekday(day.weekday()):
            if not plan['time'] or plan['id'] in decided:
                continue
            due = self.due_time(plan, day)
            if not (due <= now <= due + datetime.timedelta(minutes=self.GRACE_MINUTES)):
                continue
            snoozed = self._snoozed_until.get(plan['id'])
            if snoozed and now < snoozed:
                continue
            if (plan['id'], day) in self._prompted and not snoozed:
                continue
            self._snoozed_until.pop(plan['id'], None)
            self._prompted.add((plan['id'], day))
            self.plan_due.emit(plan)

    def snooze(self, plan_id: int, minutes: int = 10):
        self._snoozed_until[plan_id] = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
