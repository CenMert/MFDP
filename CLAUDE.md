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
- `timer.py` — `PmdrCountdownTimer` (Pomodoro phase cycling) and `CountUpTimer` (FreeTimer mode). Both use Qt `QTimer` and emit signals (`timeout_signal`, `state_changed_signal`, `finished_signal`, `task_changed_signal`). `FocusSession` is a pure dataclass holding runtime state; the timer class owns the logic.
- `atomic_analyzer.py` — Event sourcing engine. Records `AtomicEvent` instances (interruptions, focus shifts, DND toggles, milestones) with elapsed-time offsets. Designed for future ML analysis.
- `task_manager.py` / `recursive_task_manager.py` — Flat and tree-structured task CRUD. The recursive manager auto-completes parents when all children are done.
- `dnd_manager.py` — KDE D-Bus DND integration (enable/disable system notifications).
- `system_monitor.py` — Active window detection via KDE D-Bus, used by `AtomicAnalyzer` for focus-shift events.
- `notifier.py` — Qt sound effects for session start/pause/complete and hourly gong.

### `db/` — Data access layer
- `base_repository.py` — Thread-safe `ConnectionPool` (SQLite). All repos inherit from `BaseRepository`. Call `BaseRepository.initialize_pool(pool_size=5)` once at startup.
- `database_initializer.py` — Idempotent schema setup + migrations. Call `DatabaseInitializer.setup_database()` once at startup.
- `db_manager.py` — Backward-compatibility facade that re-exports all repository methods through a single import.
- Specialized repos: `session_repository.py`, `atomic_event_repository.py`, `task_repository.py`, `tag_repository.py`, `settings_repository.py`.
- Database file: `focus_tracker.db` (created at project root on first run). Test/seed databases live in `MyDataBases/`.

### `ui/` — PySide6 windows and dialogs
- `main_window.py` — Owns `Notifier`, `DNDManager`, `TaskManager`, `AtomicAnalyzer`, and both timer instances. Wires Qt signals between core and UI. The two timer instances (`timer_logic_countdown`, `timer_logic_countup`) are created once and swapped via `self.timer_logic`.
- `stats_window.py` — Lazy tab loading: Matplotlib charts render only when a tab is first opened.
- `task_window.py` / `recursive_task_window.py` — Flat and hierarchical task UIs (non-modal).
- `settings_dialog.py` — Persists settings via `SettingsRepository`.
- `styles.py` — Single QSS string (`MODERN_DARK_THEME`) applied globally at startup; Catppuccin Mocha-inspired.

### `models/`
- `data_models.py` — `Task` dataclass (id, name, tag, color, parent_id, planned_duration_minutes, is_completed).

## Key Conventions

- Qt signals are the sole communication path between `core/` and `ui/`. Core classes never import from `ui/`.
- DB connections must always be returned to the pool. Use `BaseRepository.get_connection()` / `BaseRepository.return_connection(conn)`.
- `AtomicAnalyzer` events carry a `metadata` dict serialized to JSON in the DB — keep it JSON-serializable.
- KDE D-Bus features (DND, window tracking) degrade gracefully on non-KDE desktops.
- The `resources/` directory holds `icons/`, `sounds/`, and `styles/` — loaded at runtime via relative paths from the package root.
