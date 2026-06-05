# MFDP — Multi-Functional Distraction Preventer

MFDP is a local-first, data-driven Pomodoro focus assistant for Linux. It goes beyond a simple timer: it tracks your work sessions at the atomic event level, monitors context switches, and surfaces behavioral insights through detailed statistics — all stored privately in a local SQLite database with no cloud dependency.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active_Development-orange)

---

## Features

### Timer

- **Pomodoro mode** — classic countdown timer cycling through Focus, Short Break, and Long Break phases.
- **FreeTimer mode** — open-ended count-up timer for unstructured work sessions.
- All durations are configurable from the settings dialog.

### Task Management

- **Flat tasks** — create tasks with a name, tag, color, and optional planned duration.
- **Hierarchical tasks** — build tree-structured task lists where completing all subtasks automatically marks the parent complete.
- Attach a task to the active session so every focused minute is attributed to a specific piece of work.

### Atomic Event Tracking

Each session is instrumented at a granular level through the `AtomicAnalyzer`:

- Records interruptions with a severity classification (minor / moderate / severe).
- Detects and logs focus shifts by reading the active window via KDE D-Bus.
- Captures distraction events, DND toggle actions, environment changes, and session milestones.
- All events are persisted to the database with elapsed-time offsets for replay and analysis.

### Do Not Disturb Integration

- Automatically enables system DND at session start and restores it when the session ends.
- Manual override toggle available directly in the main window.
- Integrates with KDE's notification system via D-Bus.

### Statistics

The statistics window uses lazy tab loading — charts render only when the tab is opened:

| Tab | Content |
|-----|---------|
| Daily Trend | Bar chart of total focused minutes over the last 7 days |
| Tag-Based Trend | Grouped bar chart breaking down daily minutes by tag |
| Tag Distribution | Pie/bar chart of total time per tag across all sessions |
| Hourly Heatmap | Dual-panel view: activity heatmap by hour-of-day and a bar summary |
| Quality Analysis | Pie chart of deep-work vs. interrupted sessions, plus a generated text insight |

### Awareness (Gong) Mode

An optional background chime plays at every hour and half-hour (XX:00, XX:30) to keep you grounded in real time without interrupting your flow.

### Audio Feedback

Distinct sounds play on session start, pause, completion, and for the periodic gong — loaded as Qt sound effects with no external media player required.

---

## Technology Stack

| Layer | Library |
|-------|---------|
| Language | Python 3.10+ |
| GUI | PySide6 (Qt for Python) |
| Charts | Matplotlib |
| Database | SQLite3 (connection-pooled via internal `BaseRepository`) |
| Styling | QSS — dark theme inspired by Catppuccin Mocha |

---

## Installation

### Requirements

- Python 3.10 or later
- Linux (tested on KDE/GNOME; KDE recommended for DND and window-tracking features)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/CenMert/MFDP.git
   cd MFDP
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > Arch Linux users may need the `qt6-tools` system package for certain Qt multimedia features.

---

## Usage

Launch the app as a module from the project root:

```bash
python3 -m mfdp_app.main
```

Or use the provided shell script:

```bash
bash run.sh
```

---

## Project Structure

```
mfdp_app/
  core/
    timer.py               # Pomodoro countdown and count-up timer logic
    atomic_analyzer.py     # Atomic event recording and session instrumentation
    task_manager.py        # Flat task CRUD and tag management
    recursive_task_manager.py  # Hierarchical task tree logic
    dnd_manager.py         # Do Not Disturb integration
    system_monitor.py      # Active window detection via KDE D-Bus
    notifier.py            # Sound effects and hourly chime
  db/
    database_initializer.py
    base_repository.py     # Connection pool
    session_repository.py
    atomic_event_repository.py
    task_repository.py
    tag_repository.py
    settings_repository.py
  ui/
    main_window.py
    stats_window.py
    task_window.py
    recursive_task_window.py
    settings_dialog.py
    styles.py
```

---

## License

MIT — see [LICENSE](LICENSE).
