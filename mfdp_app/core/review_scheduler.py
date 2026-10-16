"""
Review Scheduler - sınava bağlı aralıklı tekrar (1-3-7-14), Qt'den bağımsız.

Anki'deki "kart" yerine konu = görev (alt görev varsa yaprak görevler, yoksa dersin kendisi).
Kullanıcının günlük ek girişi yok:
- "okuma" / "soru" / "uretim" türünde bir oturum konuyu takvime alır (ilk tekrar yarın).
- "tekrar" türünde bir oturum + 1-4 hatırlama puanı konuyu ilerletir ya da başa sarar.
- Sınavlar takvimdeki `sinav` kayıtlarıdır; bir derse bağlandıklarında tekrarları sınavdan
  önceki güne çeker ve sınava 14 gün kala hiç çalışılmamış / bir haftadır dokunulmamış
  konuları kuyruğa getirir.

Hatırlatma OPT-IN'dir: yalnızca "tekrar takibi" açılmış derslerde (ana görev) çalışır. Plansız, boşluk
buldukça yapılan işler (ör. bitirme projesi) takipte değilse hiçbir etiket, sınav bağı ya da kuyruk girdisi
hatırlatma üretmez. Takip, ders günü bir konu girilince ya da Takip edilen dersler penceresinden açılır.

Sürdürülebilirlik: kuyruk günde en fazla MAX_QUEUE konu gösterir; gecikmiş konular birikip
borç olmaz (yalnızca sınav yakınlığına göre yeniden sıralanır). Kaçırılan gün ceza sayılmaz;
`lapses` yalnızca kötü hatırlama cevabıyla artar.

Takvim: INTERVALS = 1 -> 3 -> 7 -> 14 -> 30 gün. Bunlar pratik bir kuraldır (aralıklı tekrarın
kendisi güçlü kanıta dayanır, bu sayıların en iyi olduğu kanıtlanmış değildir); veri birikince
FSRS'e geçilebilir (research_notes/SM2 ve FSRS/sm2_fsrs.md).
"""

import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from mfdp_app.core.daily_report import logical_day
from mfdp_app.db.calendar_repository import CalendarRepository
from mfdp_app.db.review_repository import ReviewRepository
from mfdp_app.db.task_repository import TaskRepository

INTERVALS = [1, 3, 7, 14, 30]
START_KINDS = ("okuma", "soru", "uretim")
GOOD_RECALL = 3          # >= bu puan: bir sonraki adım; altı: başa dön
MAX_QUEUE = 5
EXAM_WINDOW_DAYS = 14    # sınava bu kadar gün kala çalışılmamış konular kuyruğa girer
STALE_DAYS = 7

REASON_TEXT = {
    'due': "tekrar zamanı",
    'exam': "sınav öncesi son tekrar",
    'never': "hiç çalışılmadı",
    'stale': "uzun süredir dokunulmadı",
}


@dataclass
class ReviewItem:
    task_id: int
    name: str
    course_name: str
    days_to_exam: Optional[int]
    reason: str
    lapses: int = 0
    due: Optional[datetime.date] = None
    idle_days: Optional[int] = None
    learned_on: Optional[datetime.date] = None   # derste işlendiği gün (varsa)

    @property
    def display_name(self) -> str:
        """'Anten · Dipol antenler' -> 'Dipol antenler' (ders adı zaten ayrıca gösterilir)."""
        prefix = f"{self.course_name} · "
        return self.name[len(prefix):] if self.name.startswith(prefix) else self.name

    @property
    def reason_text(self) -> str:
        if self.reason == 'stale' and self.idle_days:
            return f"{self.idle_days} gündür dokunulmadı"
        return REASON_TEXT[self.reason]


def _d(value: str) -> datetime.date:
    return datetime.date.fromisoformat(value)


def _root(task):
    seen = set()
    while task and task.parent_id and task.id not in seen:
        seen.add(task.id)
        parent = TaskRepository.get_task_by_id(task.parent_id)
        if not parent:
            break
        task = parent
    return task


def _topics_of(course) -> List:
    """Dersin konuları: yaprak alt görevler; alt görev yoksa dersin kendisi."""
    subs = TaskRepository.get_all_subtasks_recursive(course.id)
    parent_ids = {t.parent_id for t in subs}
    leaves = [t for t in subs if t.id not in parent_ids and not t.is_completed]
    return leaves or ([] if course.is_completed else [course])


def is_task_tracked(task_name: Optional[str]) -> bool:
    """Görev (ya da bağlı olduğu ders) tekrar takibinde mi?"""
    task_id = ReviewRepository.task_id_by_name(task_name)
    task = TaskRepository.get_task_by_id(task_id) if task_id else None
    return bool(task) and _root(task).id in ReviewRepository.get_tracked_course_ids()


def _next_due(step: int, day: datetime.date) -> str:
    return (day + datetime.timedelta(days=INTERVALS[min(step, len(INTERVALS) - 1)])).isoformat()


def _upcoming_exam_by_course(today: datetime.date) -> Dict[int, Dict]:
    exams: Dict[int, Dict] = {}
    for ex in CalendarRepository.get_upcoming_exams(today.isoformat()):
        exams.setdefault(ex['task_id'], ex)  # tarih sırasıyla geldiği için ilki en yakın
    return exams


# ---------------------------------------------------------------------------
# Derste işlenenler
# ---------------------------------------------------------------------------

def add_lecture_topics(course_id: int, day: datetime.date, titles: List[str]) -> Tuple[List[int], List[str]]:
    """
    Derste işlenen konuları kaydet. Her satır, dersin altında bir alt görev ("Ders · konu") olur ve
    ders günü ilk karşılaşma sayılır: ilk tekrar ertesi gün, gün geçmişteyse hemen sıraya gelir.
    Aynı konu yeniden girilirse yenisi açılmaz (var olan konunun durumuna dokunulmaz).

    Returns: (kaydedilen task_id'ler, atlanan/başarısız satırlar)
    """
    course = TaskRepository.get_task_by_id(course_id)
    if not course:
        return [], list(titles)
    ReviewRepository.set_course_tracked(course.id, True)  # konu girmek = hatırlatma isteği
    created, skipped, seen = [], [], set()
    for raw in titles:
        title = " ".join(raw.split())
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        name = f"{course.name} · {title}"
        task_id = ReviewRepository.task_id_by_name(name) or TaskRepository.insert_task(
            name, course.tag, None, course.color, parent_id=course.id)
        if not task_id:
            skipped.append(title)
            continue
        ReviewRepository.create_state(task_id, _next_due(0, day), day.isoformat(),
                                      learned_on=day.isoformat(), source='ders')
        created.append(task_id)
    return created, skipped


def recent_lecture_topics(days: int = 14, today: Optional[datetime.date] = None) -> List[Dict]:
    """Son `days` günde derste işlenen konular (ders adıyla), en yeni önce."""
    today = today or logical_day(datetime.datetime.now())
    since = (today - datetime.timedelta(days=days)).isoformat()
    courses = {c.id: c for c in TaskRepository.get_root_tasks()}
    rows = ReviewRepository.get_lecture_topics(list(courses), since)
    return [dict(r, course_name=courses[r['parent_id']].name) for r in rows if r['parent_id'] in courses]


# ---------------------------------------------------------------------------
# Olaylar
# ---------------------------------------------------------------------------

def on_session_kind(task_name: Optional[str], kind: str, today: Optional[datetime.date] = None) -> Optional[int]:
    """
    Oturum türü seçildi. Başlatan türlerde (okuma/soru/üretim) konuyu takvime al.
    Returns: konunun task_id'si (görevsiz oturumda None).
    """
    task_id = ReviewRepository.task_id_by_name(task_name)
    if not task_id or not is_task_tracked(task_name):
        return None
    today = today or logical_day(datetime.datetime.now())
    if kind in START_KINDS:
        ReviewRepository.create_state(task_id, _next_due(0, today), today.isoformat())
    return task_id


def apply_recall(task_name: Optional[str], session_id: int, recall: int,
                 today: Optional[datetime.date] = None) -> bool:
    """
    "Tekrar" oturumundan sonra 1-4 hatırlama puanı. Aynı oturum için yeniden cevap verilirse
    önceki cevabın etkisi geri alınıp yenisi uygulanır.
    """
    task_id = ReviewRepository.task_id_by_name(task_name)
    if not task_id or not is_task_tracked(task_name):
        return False
    today = today or logical_day(datetime.datetime.now())

    prior = ReviewRepository.get_log_for_session(session_id)
    if prior:
        ReviewRepository.set_state(task_id, prior['prev_step'], prior['prev_next_due'],
                                   prior['prev_last_review'], prior['prev_lapses'])
        ReviewRepository.delete_log(prior['id'])

    state = ReviewRepository.get_state(task_id)
    if not state:  # daha önce hiç başlatılmamış konuda tekrar: konuyu şimdi aç
        ReviewRepository.create_state(task_id, _next_due(0, today), today.isoformat())
        state = ReviewRepository.get_state(task_id)

    ReviewRepository.add_log(task_id, session_id, recall, today.isoformat(), state)
    if recall >= GOOD_RECALL:
        step = state['step'] + 1
        ReviewRepository.set_state(task_id, step, _next_due(step, today), today.isoformat(), state['lapses'])
    else:
        ReviewRepository.set_state(task_id, 0, _next_due(0, today), today.isoformat(), state['lapses'] + 1)
    return True


# ---------------------------------------------------------------------------
# Kuyruk
# ---------------------------------------------------------------------------

def effective_due(state: Dict, exam_date: Optional[datetime.date], today: datetime.date):
    """(due, sınav_nedeniyle_mi). Sınavdan bir gün önce, o güne kadar tekrar yapılmadıysa tekrar gelir."""
    due = _d(state['next_due'])
    if exam_date:
        cap = exam_date - datetime.timedelta(days=1)
        if cap >= today and _d(state['last_review']) < cap and due > cap:
            return cap, True
    return due, False


def build_queue(today: Optional[datetime.date] = None, limit: Optional[int] = MAX_QUEUE) -> List[ReviewItem]:
    """Bugünün tekrar kuyruğu: sınava en yakın önce, sonra çok unutulan, sonra tarihi eski olan."""
    today = today or logical_day(datetime.datetime.now())
    tracked = ReviewRepository.get_tracked_course_ids()
    exams = {cid: ex for cid, ex in _upcoming_exam_by_course(today).items() if cid in tracked}
    items: Dict[int, ReviewItem] = {}

    def days_to_exam(course_id):
        ex = exams.get(course_id)
        return (_d(ex['date']) - today).days if ex else None

    # 1) Zamanı gelmiş konular
    for state in ReviewRepository.get_all_states():
        task = TaskRepository.get_task_by_id(state['task_id'])
        if not task or not task.is_active or task.is_completed:
            continue
        course = _root(task)
        if course.id not in tracked:
            continue
        ex = exams.get(course.id)
        due, by_exam = effective_due(state, _d(ex['date']) if ex else None, today)
        if due <= today:
            items[task.id] = ReviewItem(
                task_id=task.id, name=task.name, course_name=course.name,
                days_to_exam=days_to_exam(course.id), reason='exam' if by_exam else 'due',
                lapses=state['lapses'], due=due,
                learned_on=_d(state['learned_on']) if state.get('learned_on') else None)

    # 2) Sınavı yaklaşan derslerde hiç çalışılmamış / bir haftadır dokunulmamış konular
    for course_id, ex in exams.items():
        left = (_d(ex['date']) - today).days
        if left > EXAM_WINDOW_DAYS:
            continue
        course = TaskRepository.get_task_by_id(course_id)
        if not course or not course.is_active:
            continue
        for topic in _topics_of(course):
            if topic.id in items:
                continue
            state = ReviewRepository.get_state(topic.id)
            days = []
            if state:
                days.append(_d(state['last_review']))
            session_day = ReviewRepository.last_session_day(topic.name)
            if session_day:
                days.append(_d(session_day))
            last = max(days) if days else None
            if last is None:
                items[topic.id] = ReviewItem(topic.id, topic.name, course.name, left, 'never',
                                             lapses=state['lapses'] if state else 0)
            elif (today - last).days > STALE_DAYS:
                items[topic.id] = ReviewItem(topic.id, topic.name, course.name, left, 'stale',
                                             lapses=state['lapses'] if state else 0,
                                             idle_days=(today - last).days)

    queue = sorted(items.values(), key=lambda i: (
        i.days_to_exam if i.days_to_exam is not None else 10_000,
        -i.lapses,
        i.due or today))
    return queue[:limit] if limit else queue
