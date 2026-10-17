# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

Always work inside the virtual environment. From the project root (`MFDP_base/`):

```bash
source .venv/bin/activate
python -m mfdp_app.main
```

Or use the shell script: `bash run.sh`

The app is a PySide6 GUI — no test suite or linter is configured. Manual testing requires a running display.

## Architecture Overview

MFDP is a Pomodoro/focus-tracking desktop app for Linux (KDE recommended). The codebase is organized as the `mfdp_app` package with four layers:

### `core/` — Business logic (no UI, no direct DB writes)
- `timer.py` — `PmdrCountdownTimer` (Pomodoro phase cycling) and `CountUpTimer` (FreeTimer mode, the default; no pause — start → mark internal/external interruptions → finish, sessions tagged `timer_model: "countup_v1"`). Both use Qt `QTimer` and emit signals (`timeout_signal`, `state_changed_signal`, `finished_signal`, `task_changed_signal`). `FocusSession` is a pure dataclass holding runtime state; the timer class owns the logic.
- `atomic_analyzer.py` — Event sourcing engine. Records `AtomicEvent` instances (interruptions, focus shifts, DND toggles, milestones) with elapsed-time offsets. Designed for future ML analysis.
- `task_manager.py` / `recursive_task_manager.py` — Flat and tree-structured task CRUD. The recursive manager auto-completes parents when all children are done.
- `dnd_manager.py` — KDE D-Bus DND integration (enable/disable system notifications).
- `system_monitor.py` — Active window detection via KDE D-Bus. Intended to feed `AtomicAnalyzer.record_focus_shift`, but not instantiated anywhere yet.
- `notifier.py` — Qt sound effects for session start/pause/complete and hourly gong.
- `review_scheduler.py` — Exam-aware spaced review (1-3-7-14-30 days), Qt-free; topic = task, linked to exams via `calendar_events.task_id`. `plan_scheduler.py` — fires if-then plan prompts. `streak.py` — contribution-grid and tolerant streak maths.

### `db/` — Data access layer
- `base_repository.py` — Thread-safe `ConnectionPool` (SQLite). All repos inherit from `BaseRepository`. Call `BaseRepository.initialize_pool(pool_size=5)` once at startup.
- `database_initializer.py` — Idempotent schema setup + migrations. Call `DatabaseInitializer.setup_database()` once at startup.
- `db_manager.py` — Backward-compatibility facade that re-exports all repository methods through a single import.
- Specialized repos: `session_repository.py`, `atomic_event_repository.py`, `task_repository.py`, `tag_repository.py`, `settings_repository.py`, `calendar_repository.py`. App code calls these directly; `db_manager.py` is unused legacy.
- Foreign keys are not enforced (no `PRAGMA foreign_keys = ON`), so `ON DELETE CASCADE` in the schema does nothing.
- Full data map (every table/column/format, file-based state, who reads/writes what): `documentation/VERI_HARITASI.md` — update it when the schema or event types change.
- Database file: `focus_tracker.db` (created at project root on first run). Test/seed databases live in `MyDataBases/`.

### `ui/` — PySide6 windows and dialogs
- `main_window.py` — Owns `Notifier`, `DNDManager`, `TaskManager`, `AtomicAnalyzer`, and both timer instances. Wires Qt signals between core and UI. The two timer instances (`timer_logic_countdown`, `timer_logic_countup`) are created once and swapped via `self.timer_logic`.
- `stats_window.py` — Lazy tab loading: Matplotlib charts render only when a tab is first opened.
- `task_window.py` — Flat task UI (non-modal). `plan_panel.py` — right-hand collapsible panel (Ctrl+P, open by default) beside the timer: hierarchical task tree (add/rename/delete/complete) plus the session plan. Starting a session requires a chosen task and, in FreeTimer, an estimate (minutes); an optional first-step note goes into the `session_started` event (`plan_note`). The estimate is stored in `sessions_v2.planned_duration_minutes` and remembered on the task. Estimate and the one-line note are saved per task via the panel's Save button (Ctrl+S; also auto-saved when switching tasks) — note lives in `tasks.notes`.
- `settings_dialog.py` — Persists settings via `SettingsRepository`.
- `styles.py` — Single QSS string (`MODERN_DARK_THEME`) applied globally at startup; earthy palette defined in `palette.py`.

### `models/`
- `data_models.py` — `Task` dataclass (id, name, tag, color, parent_id, planned_duration_minutes, is_completed).

## Key Conventions

- Qt signals are the sole communication path between `core/` and `ui/`. Core classes never import from `ui/`.
- DB connections must always be returned to the pool. Use `BaseRepository.get_connection()` / `BaseRepository.return_connection(conn)`.
- `AtomicAnalyzer` events carry a `metadata` dict serialized to JSON in the DB — keep it JSON-serializable.
- KDE D-Bus features (DND, window tracking) degrade gracefully on non-KDE desktops.
- The `resources/` directory holds `icons/`, `sounds/`, and `styles/` — loaded at runtime via relative paths from the package root.
