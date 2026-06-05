# Hedef (Goal) Sistemi — Tasarım Planı

## Amaç

Task sekmesine bir "orkestratör" katmanı ekleniyor. Kullanıcı, mevcut task'ları ve planlanan pomodoro sayılarını bir Hedef altında toplayabiliyor. Timer bir pomodoro tamamladığında, o task hangi hedeflere bağlıysa ilerleme otomatik güncelleniyor. İlerleme %100'ü geçebilir (4/3 = %133). Manuel tamamlama da mevcut.

**MVP kapsamı:** Düz hedefler — `parent_goal_id` alanı eklenir ama hiyerarşik mantık şimdilik uygulanmaz.

---

## Veri Modeli

### `mfdp_app/models/data_models.py`

```python
@dataclass
class GoalItem:
    id: int
    goal_id: int
    task_id: int
    planned_pomodoros: int
    completed_pomodoros: int = 0

@dataclass
class Goal:
    id: int
    name: str
    created_at: datetime
    items: List[GoalItem] = field(default_factory=list)   # goal altındaki task'lar
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    parent_goal_id: Optional[int] = None   # ileride hiyerarşi için
```

`GoalRepository.get_goal_by_id()` ve `get_all_goals()`, her Goal nesnesi dönüşünde
`goal_tasks` tablosunu join'leyerek `items` listesini doldurur.
`get_goals_for_task()` ise sadece Goal nesneleri döner (items boş bırakılır, hafif sorgu).

---

## Veritabanı

### `mfdp_app/db/database_initializer.py`

Mevcut pattern ile (CREATE TABLE IF NOT EXISTS + indeksler):

```sql
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT 0,
    completed_at TEXT,
    parent_goal_id INTEGER,
    FOREIGN KEY (parent_goal_id) REFERENCES goals(id)
);
CREATE INDEX IF NOT EXISTS idx_goals_is_completed ON goals(is_completed);

CREATE TABLE IF NOT EXISTS goal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    planned_pomodoros INTEGER NOT NULL DEFAULT 1,
    completed_pomodoros INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
CREATE INDEX IF NOT EXISTS idx_goal_tasks_goal_id ON goal_tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_goal_tasks_task_id ON goal_tasks(task_id);
```

---

## Repository

### `mfdp_app/db/goal_repository.py` — yeni dosya

```python
class GoalRepository:
    @staticmethod
    def insert_goal(name) -> int
    @staticmethod
    def get_goal_by_id(goal_id) -> Optional[Goal]
    @staticmethod
    def get_all_goals(include_completed=False) -> List[Goal]
    @staticmethod
    def complete_goal(goal_id, completed_at)
    @staticmethod
    def delete_goal(goal_id)               # hard delete, cascade goal_tasks

    @staticmethod
    def add_task_to_goal(goal_id, task_id, planned_pomodoros) -> int
    @staticmethod
    def remove_task_from_goal(goal_id, task_id)
    @staticmethod
    def get_goal_items(goal_id) -> List[GoalItem]
    @staticmethod
    def get_goals_for_task(task_id) -> List[Goal]
    @staticmethod
    def increment_completed_pomodoros(goal_id, task_id)
```

---

## GoalManager

### `mfdp_app/core/goal_manager.py` — yeni dosya

TaskManager pattern'ını takip eder (QObject + Signal):

```python
class GoalManager(QObject):
    goal_created_signal   = Signal(int)        # goal_id
    goal_updated_signal   = Signal(int)        # goal_id
    goal_completed_signal = Signal(int)        # goal_id
    goal_progress_signal  = Signal(int, float) # goal_id, progress (0.0..n.nn)

    def create_goal(name) -> int
    def add_task_to_goal(goal_id, task_id, planned_pomodoros)
    def remove_task_from_goal(goal_id, task_id)
    def complete_goal_manually(goal_id)
    def delete_goal(goal_id)
    def get_all_goals(include_completed=False) -> List[Goal]
    def get_goal_items(goal_id) -> List[GoalItem]
    def calculate_progress(goal_id) -> float

    def on_pomodoro_completed(task_id: int):
        # get_goals_for_task → her hedef için increment + progress signal
```

---

## Timer Hooku

### `mfdp_app/core/timer.py`

`PmdrCountdownTimer`'a yeni sinyal:

```python
pomodoro_completed_signal = Signal(int)  # task_id
```

`_save_current_session(completed)` içinde `SessionRepository.log_session()` sonrasına:

```python
if completed == 1 and self.current_session.current_task_id:
    self.pomodoro_completed_signal.emit(self.current_session.current_task_id)
```

### `mfdp_app/ui/main_window.py`

```python
self.goal_manager = GoalManager()
self.countdown_timer.pomodoro_completed_signal.connect(self.goal_manager.on_pomodoro_completed)
```

---

## İlerleme Hesabı

```python
def calculate_progress(goal_id) -> float:
    items = GoalRepository.get_goal_items(goal_id)
    total_planned   = sum(i.planned_pomodoros for i in items)
    total_completed = sum(i.completed_pomodoros for i in items)
    if total_planned == 0:
        return 0.0
    return total_completed / total_planned  # 4/3 = 1.333...
```

UI'da `f"%{progress * 100:.0f}"` formatında gösterilir.

---

## Kapsam Dışı (MVP Sonrası)

- Hiyerarşik hedef mantığı (`parent_goal_id` kullanımı, alt hedef propagasyonu)
- CountUpTimer'a `pomodoro_completed_signal` eklenmesi
- Hedef penceresi / UI
