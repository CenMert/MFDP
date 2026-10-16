"""
Streak Module - GitHub tarzı katkı ızgarası ve seri hesabı (Qt bağımsız).

- Gün: daily_report ile aynı mantıksal gün (03:00'te başlar). Yalnızca iş modları
  (Focus / Free Timer) sayılır.
- Renk seviyesi (0-4): GitHub gibi, dönemdeki çalışılan günlerin çeyreklerine göre.
- Seri: Bir gün ACTIVE_MINUTES kadar çalışıldıysa "aktif"tir. Tek bir boş gün seriyi
  bozmaz, iki gün üst üste boşluk bozar ("iki kere kaçırma"). Alışkanlık araştırması:
  tek kaçırma alışkanlık oluşumunu bozmuyor (Lally 2010), kırılan seri ise motivasyonu
  düşürüyor, onarılabilir seri bu düşüşü azaltıyor (Silverman & Barasch 2023).
  Bugün henüz aktif değilse seri bozulmuş sayılmaz.
"""

import datetime
from dataclasses import dataclass, field
from typing import Dict, List

from mfdp_app.core.daily_report import DAY_START_HOUR, logical_day, day_window
from mfdp_app.db.session_repository import SessionRepository

GRID_WEEKS = 18
ACTIVE_MINUTES = 25
MAX_MISSES = 1  # Seri bu kadar ardışık boş güne dayanır

_DB_TIME_FMT = '%Y-%m-%d %H:%M:%S'


@dataclass
class StreakData:
    start: datetime.date                      # Izgaranın ilk günü (Pazartesi)
    today: datetime.date
    minutes: Dict[datetime.date, float] = field(default_factory=dict)
    levels: Dict[datetime.date, int] = field(default_factory=dict)
    thresholds: List[float] = field(default_factory=list)  # seviye 2, 3, 4 alt sınırları (dk)
    current_streak: int = 0
    best_streak: int = 0
    active_last_7: int = 0
    total_minutes: float = 0.0

    def days(self) -> List[datetime.date]:
        n = (self.today - self.start).days + 1
        return [self.start + datetime.timedelta(days=i) for i in range(n)]


def _quartiles(values: List[float]) -> List[float]:
    vals = sorted(values)
    if not vals:
        return []
    return [vals[int(len(vals) * q)] if int(len(vals) * q) < len(vals) else vals[-1]
            for q in (0.25, 0.5, 0.75)]


def _level(minutes: float, thresholds: List[float]) -> int:
    if minutes <= 0:
        return 0
    level = 1
    for t in thresholds:
        if minutes >= t:
            level += 1
    return min(level, 4)


def _streaks(days: List[datetime.date], minutes: Dict[datetime.date, float],
             today: datetime.date):
    current = best = misses = 0
    for day in days:
        active = minutes.get(day, 0) >= ACTIVE_MINUTES
        if active:
            current += 1
            misses = 0
        elif day == today:
            continue  # gün bitmedi
        else:
            misses += 1
            if misses > MAX_MISSES:
                current = 0
        best = max(best, current)
    return current, best


def build_streak_data(weeks: int = GRID_WEEKS) -> StreakData:
    today = logical_day(datetime.datetime.now())
    # Izgara Pazartesi başlar; son sütun bugünün haftası
    start = today - datetime.timedelta(days=today.weekday() + 7 * (weeks - 1))
    window_start, _ = day_window(start)

    minutes: Dict[datetime.date, float] = {}
    for s in SessionRepository.get_work_sessions_since(window_start):
        try:
            started = datetime.datetime.strptime(s['start_time'], _DB_TIME_FMT)
        except (TypeError, ValueError):
            continue
        day = logical_day(started)
        minutes[day] = minutes.get(day, 0) + (s['duration_seconds'] or 0) / 60

    data = StreakData(start=start, today=today, minutes=minutes)
    data.thresholds = _quartiles([m for m in minutes.values() if m > 0])
    data.levels = {d: _level(m, data.thresholds) for d, m in minutes.items()}
    data.current_streak, data.best_streak = _streaks(data.days(), minutes, today)
    data.active_last_7 = sum(
        1 for i in range(7)
        if minutes.get(today - datetime.timedelta(days=i), 0) >= ACTIVE_MINUTES)
    data.total_minutes = sum(minutes.values())
    return data
