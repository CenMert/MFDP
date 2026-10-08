"""
Daily Report Module

Focus ekranındaki hızlı "Gün" paneli ve blok detay raporu için veri hazırlar.
Qt bağımlılığı yoktur; yalnızca repository'lerden okur.

Kavramlar:
- Mantıksal gün: DAY_START_HOUR'da başlar ve ertesi gün aynı saatte biter.
  Gece 01:30'da başlayan oturum önceki güne aittir. Oturum, başladığı ana göre
  tek bir güne yazılır; böylece hiçbir oturum iki kere sayılmaz.
- Blok: Aynı tag + görev için art arda gelen iş oturumları. Aradaki boşluk
  BLOCK_GAP_MINUTES'ı geçmediği sürece oturumlar aynı blokta birleşir. Aradaki
  mola (Short/Long Break) oturumları bloğu bölmez.
- Duraklama: Bir oturumun içinde kullanıcının timer'ı durdurması.
- Ara: Bir bloktaki iki oturum arasındaki boşluk (ör. pomodoro molası).
"""

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from mfdp_app.db.session_repository import SessionRepository
from mfdp_app.db.atomic_event_repository import AtomicEventRepository
from mfdp_app.db.tag_repository import TagRepository


DAY_START_HOUR = 3
BLOCK_GAP_MINUTES = 30
WORK_MODES = ("Focus", "Free Timer")
MIN_GAP_SECONDS = 60  # Bundan kısa oturum arası boşluklar "ara" sayılmaz

NO_TAG = "Etiketsiz"
NO_TASK = "Görevsiz"
DEFAULT_TAG_COLOR = "#89b4fa"

_DB_TIME_FMT = '%Y-%m-%d %H:%M:%S'
_TR_MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
_TR_WEEKDAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Pause:
    """Oturum içi tek bir duraklama."""
    start: datetime.datetime
    end: datetime.datetime
    active_before_seconds: Optional[int]  # Blok içinde kaçıncı net saniyede durdu
    measured_seconds: Optional[int] = None  # Timer'ın ölçtüğü süre (varsa daha kesin)

    @property
    def seconds(self) -> int:
        if self.measured_seconds is not None:
            return max(0, self.measured_seconds)
        return max(0, int((self.end - self.start).total_seconds()))


@dataclass
class Segment:
    """Kesintisiz çalışma dilimi (zaman çizelgesi için)."""
    start: datetime.datetime
    end: datetime.datetime
    kind: str  # "work", "pause", "gap", "unknown"

    @property
    def seconds(self) -> int:
        return max(0, int((self.end - self.start).total_seconds()))


@dataclass
class WorkBlock:
    tag: str
    task_name: str
    start: datetime.datetime
    end: datetime.datetime
    active_seconds: int
    sessions: List[Dict] = field(default_factory=list)


@dataclass
class TagGroup:
    tag: str
    color: str
    total_active: int
    blocks: List[WorkBlock] = field(default_factory=list)


@dataclass
class DaySummary:
    day: datetime.date
    total_active: int
    groups: List[TagGroup] = field(default_factory=list)


@dataclass
class BlockReport:
    block: WorkBlock
    color: str
    wall_seconds: int              # Ayrılan süre (ilk başlangıç → son bitiş)
    active_seconds: int            # Net çalışma
    efficiency: float              # active / wall (0..1)
    planned_seconds: int           # Pomodoro planlanan toplam (Free Timer hariç)
    pauses: List[Pause]            # Kesin bilinen oturum içi duraklamalar
    estimated_pause_count: int     # Detayı olmayan eski kayıtlardan gelen duraklamalar
    estimated_pause_seconds: int
    gaps: List[Segment]            # Oturumlar arası aralar
    timeline: List[Segment]        # Çalışma / duraklama / ara dilimleri
    longest_focus_seconds: int
    average_focus_seconds: int
    phase_counts: Dict[str, int]   # Bölünmelerin bloğun ilk/orta/son üçte birine dağılımı
    completed_sessions: int
    abandoned_sessions: int
    abandon_reasons: Dict[str, int]
    has_legacy: bool               # Olay detayı olmayan eski oturum var mı

    @property
    def pause_count(self) -> int:
        return len(self.pauses) + self.estimated_pause_count

    @property
    def pause_seconds(self) -> int:
        return sum(p.seconds for p in self.pauses) + self.estimated_pause_seconds

    @property
    def gap_seconds(self) -> int:
        return sum(g.seconds for g in self.gaps)

    @property
    def plan_ratio(self) -> Optional[float]:
        if self.planned_seconds <= 0:
            return None
        planned_active = sum(
            s['duration_seconds'] or 0 for s in self.block.sessions
            if s.get('planned_duration_minutes')
        )
        return planned_active / self.planned_seconds


# ============================================================================
# DAY HELPERS
# ============================================================================

def logical_day(dt: datetime.datetime) -> datetime.date:
    """Verilen anın ait olduğu mantıksal gün (DAY_START_HOUR öncesi önceki güne sayılır)."""
    return (dt - datetime.timedelta(hours=DAY_START_HOUR)).date()


def day_window(day: datetime.date) -> Tuple[datetime.datetime, datetime.datetime]:
    """Mantıksal günün [başlangıç, bitiş) aralığı."""
    start = datetime.datetime.combine(day, datetime.time(hour=DAY_START_HOUR))
    return start, start + datetime.timedelta(days=1)


def format_day_label(day: datetime.date, today: Optional[datetime.date] = None) -> str:
    """'Bugün', 'Dün' veya '1 Eki Çar'."""
    today = today or logical_day(datetime.datetime.now())
    if day == today:
        return "Bugün"
    if day == today - datetime.timedelta(days=1):
        return "Dün"
    return f"{day.day} {_TR_MONTHS[day.month - 1]} {_TR_WEEKDAYS[day.weekday()]}"


def format_duration(seconds: float) -> str:
    """3725 -> '1s 02dk', 1500 -> '25dk', 42 -> '42sn'."""
    seconds = int(max(0, seconds))
    if seconds < 60:
        return f"{seconds}sn"
    hours, rem = divmod(seconds, 3600)
    minutes = rem // 60
    if hours:
        return f"{hours}s {minutes:02d}dk"
    return f"{minutes}dk"


def format_duration_precise(seconds: float) -> str:
    """270 -> '4dk 30sn' (duraklama listesi için)."""
    seconds = int(max(0, seconds))
    if seconds < 60:
        return f"{seconds}sn"
    minutes, secs = divmod(seconds, 60)
    if minutes >= 60:
        return format_duration(seconds)
    return f"{minutes}dk {secs:02d}sn" if secs else f"{minutes}dk"


# ============================================================================
# SUMMARY
# ============================================================================

def _parse_db_time(value: Optional[str]) -> Optional[datetime.datetime]:
    if not value:
        return None
    try:
        return datetime.datetime.strptime(value, _DB_TIME_FMT)
    except ValueError:
        return datetime.datetime.fromisoformat(value)


def _tag_colors() -> Dict[str, str]:
    return {t['name']: t['color'] for t in TagRepository.get_all_tags() if t.get('color')}


def build_day_summary(day: datetime.date) -> DaySummary:
    """Mantıksal gün için tag → blok özetini oluştur."""
    start, end = day_window(day)
    sessions = [
        s for s in SessionRepository.get_sessions_between(start, end)
        if s['mode'] in WORK_MODES
    ]

    blocks: List[WorkBlock] = []
    max_gap = datetime.timedelta(minutes=BLOCK_GAP_MINUTES)

    for s in sessions:
        s_start = _parse_db_time(s['start_time'])
        s_end = _parse_db_time(s['end_time']) or s_start
        tag = s['category'] or NO_TAG
        task = s['task_name'] or NO_TASK
        active = s['duration_seconds'] or 0

        prev = blocks[-1] if blocks else None
        if prev and prev.tag == tag and prev.task_name == task and s_start - prev.end <= max_gap:
            prev.end = max(prev.end, s_end)
            prev.active_seconds += active
            prev.sessions.append(s)
        else:
            blocks.append(WorkBlock(tag, task, s_start, s_end, active, [s]))

    colors = _tag_colors()
    groups: Dict[str, TagGroup] = {}
    for b in blocks:
        group = groups.get(b.tag)
        if not group:
            group = groups[b.tag] = TagGroup(b.tag, colors.get(b.tag, DEFAULT_TAG_COLOR), 0)
        group.blocks.append(b)
        group.total_active += b.active_seconds

    ordered = sorted(groups.values(), key=lambda g: g.total_active, reverse=True)
    return DaySummary(day, sum(g.total_active for g in ordered), ordered)


# ============================================================================
# BLOCK REPORT
# ============================================================================

def _session_timeline(session: Dict, events: List[Dict]) -> Tuple[List[Segment], List[Pause], bool]:
    """
    Tek oturumun çalışma/duraklama dilimlerini olaylardan çıkar.

    Returns:
        (segments, pauses, has_detail). has_detail False ise oturum, olayları
        kaydedilmemiş eski bir kayıttır ve tek "unknown" dilim olarak döner.
    """
    s_start = _parse_db_time(session['start_time'])
    s_end = _parse_db_time(session['end_time']) or s_start

    # Yeni kayıtlarda her oturum, bitişinden hemen önce yazılan bir completed/abandoned
    # olayıyla kapanır. Bu yoksa (bug'lı dönem ya da seed veri) olaylara güvenilmez.
    tolerance = datetime.timedelta(seconds=5)
    has_detail = any(
        e['event_type'] in ('session_completed', 'session_abandoned')
        and s_start - tolerance <= datetime.datetime.fromisoformat(e['timestamp']) <= s_end + tolerance
        for e in events
    )
    if not has_detail:
        kind = "work" if not session['interruption_count'] else "unknown"
        return [Segment(s_start, s_end, kind)], [], False

    segments: List[Segment] = []
    pauses: List[Pause] = []
    cursor = s_start
    paused = False
    pause_active: Optional[int] = None

    for e in events:
        ts = min(max(datetime.datetime.fromisoformat(e['timestamp']), s_start), s_end)
        meta = e['metadata'] or {}
        if e['event_type'] == 'interruption_detected' and meta.get('reason') == 'user_pause' and not paused:
            segments.append(Segment(cursor, ts, "work"))
            cursor, paused = ts, True
            pause_active = meta.get('active_seconds')
        elif e['event_type'] == 'session_resumed' and paused:
            segments.append(Segment(cursor, ts, "pause"))
            pauses.append(Pause(cursor, ts, pause_active, meta.get('pause_seconds')))
            cursor, paused = ts, False

    # Duraklamadayken bitirilen/sıfırlanan oturumda son dilim duraklamadır
    if paused:
        segments.append(Segment(cursor, s_end, "pause"))
        pauses.append(Pause(cursor, s_end, pause_active))
    else:
        segments.append(Segment(cursor, s_end, "work"))

    return [seg for seg in segments if seg.seconds > 0], pauses, True


def build_block_report(block: WorkBlock, color: str = DEFAULT_TAG_COLOR) -> BlockReport:
    """Bir blok için duraklama, ara ve bölünme analizini hesapla."""
    session_ids = [s['id'] for s in block.sessions]
    events_by_session = AtomicEventRepository.get_events_for_sessions(session_ids)

    timeline: List[Segment] = []
    pauses: List[Pause] = []
    gaps: List[Segment] = []
    est_pause_count = 0
    est_pause_seconds = 0
    has_legacy = False
    completed = abandoned = 0
    abandon_reasons: Dict[str, int] = {}
    planned_seconds = 0
    active_before = 0  # Önceki oturumlardaki net süre (blok içi net dakikayı bulmak için)

    prev_end: Optional[datetime.datetime] = None
    for s in block.sessions:
        s_start = _parse_db_time(s['start_time'])
        s_end = _parse_db_time(s['end_time']) or s_start
        events = events_by_session.get(s['id'], [])

        if prev_end and (s_start - prev_end).total_seconds() >= MIN_GAP_SECONDS:
            gap = Segment(prev_end, s_start, "gap")
            gaps.append(gap)
            timeline.append(gap)

        segs, s_pauses, detailed = _session_timeline(s, events)
        timeline.extend(segs)
        for p in s_pauses:
            if p.active_before_seconds is not None:
                p.active_before_seconds += active_before
            pauses.append(p)

        if not detailed and s['interruption_count']:
            has_legacy = True
            est_pause_count += s['interruption_count']
            wall = (s_end - s_start).total_seconds()
            est_pause_seconds += max(0, int(wall) - (s['duration_seconds'] or 0))

        if s['completed']:
            completed += 1
        else:
            abandoned += 1
            reason = next(
                (e['metadata'].get('reason') for e in events if e['event_type'] == 'session_abandoned'),
                None
            ) if detailed else None
            label = _ABANDON_LABELS.get(reason, "bilinmiyor")
            abandon_reasons[label] = abandon_reasons.get(label, 0) + 1

        if s.get('planned_duration_minutes'):
            planned_seconds += s['planned_duration_minutes'] * 60

        active_before += s['duration_seconds'] or 0
        prev_end = s_end

    wall_seconds = max(1, int((block.end - block.start).total_seconds()))
    efficiency = min(1.0, block.active_seconds / wall_seconds)

    # Kesintisiz odak dilimleri: art arda gelen "work" dilimleri (arada duraklama/ara yoksa) birleşir
    focus_lengths: List[int] = []
    run = 0
    for seg in timeline:
        if seg.kind == "work":
            run += seg.seconds
        else:
            if run:
                focus_lengths.append(run)
            run = 0
    if run:
        focus_lengths.append(run)

    # Bölünme noktaları: duraklama ve ara başlangıçları, bloğun hangi üçte birinde?
    phase_counts = {"İlk": 0, "Orta": 0, "Son": 0}
    for seg in timeline:
        if seg.kind in ("pause", "gap"):
            pos = (seg.start - block.start).total_seconds() / wall_seconds
            key = "İlk" if pos < 1 / 3 else ("Orta" if pos < 2 / 3 else "Son")
            phase_counts[key] += 1

    return BlockReport(
        block=block,
        color=color,
        wall_seconds=wall_seconds,
        active_seconds=block.active_seconds,
        efficiency=efficiency,
        planned_seconds=planned_seconds,
        pauses=pauses,
        estimated_pause_count=est_pause_count,
        estimated_pause_seconds=est_pause_seconds,
        gaps=gaps,
        timeline=timeline,
        longest_focus_seconds=max(focus_lengths) if focus_lengths else 0,
        average_focus_seconds=int(sum(focus_lengths) / len(focus_lengths)) if focus_lengths else 0,
        phase_counts=phase_counts,
        completed_sessions=completed,
        abandoned_sessions=abandoned,
        abandon_reasons=abandon_reasons,
        has_legacy=has_legacy,
    )


_ABANDON_LABELS = {
    "reset": "sıfırlama",
    "mode_change": "mod değişimi",
    "app_exit": "uygulama kapandı",
}
