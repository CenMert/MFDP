# MFDP

A local-first focus tracker for Linux. MFDP measures how you actually work: how long each session lasts, what interrupts it, what you studied and when you should review it. Everything is stored in a local SQLite database. There is no account and no cloud.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.1.0-orange)

## Features

### Timer

- **Free Timer (default).** A count-up timer with no pause. You start, mark interruptions, and finish. Continuing afterwards is a new session, so the gap between sessions is your real break length. Sessions shorter than one minute are discarded as accidental starts.
- **Interruptions.** Mark an internal interruption (your own distraction) with `I` or an external one (someone or something else) with `E`. The session keeps running.
- **Pomodoro.** The classic Focus / Short Break / Long Break cycle, with configurable durations.
- **Mini window.** A small always-on-top window showing the task color and elapsed time. A click starts or finishes the session.

### Planning a session

- **Plan panel (Ctrl+P).** A task tree on the right: add, rename, delete and complete tasks, with subtasks. A parent completes automatically when all its children are done.
- **Start requires a plan.** Pick a task and, in Free Timer, an estimate in minutes. An optional one-line first step is recorded with the session. The estimate and note are remembered per task.
- **Estimate alert.** You are notified when the estimate is reached; you can finish or carry on.
- **If-then plans.** Define plans such as "at 09:00 start this task". MFDP prompts you at that time with Start, snooze or skip.

### Streaks and review

- **Streak panel (Ctrl+B).** An 18-week contribution grid of daily focus minutes, a tolerant streak that survives a single empty day, a last-7-days count and plan adherence.
- **Spaced review.** For courses you choose to track, topics come back on a 1-3-7-14-30 day schedule. Exam dates pull reviews earlier, and the daily queue is capped so it never builds up debt.
- **Lecture log.** Record what was covered in a lecture; each topic becomes a subtask that enters the review schedule.
- **Session feedback.** After each work session you rate focus from 1 to 5 and label the kind of work (reading, problems, review, production, other). On review sessions you also answer a short recall question.

### Calendar

- A month view for exams, homework, meetings and date ranges.
- Exams can be linked to a course, which drives the review schedule.
- JSON import and export with validation and a preview, plus a prompt you can give an AI assistant to convert a messy schedule into calendar entries.

### Statistics

| Tab | Content |
|-----|---------|
| Daily Trend | Focused minutes over the last 7 days |
| Tag-Based Trend | Daily minutes broken down by tag |
| Tag Distribution | Total time per tag |
| Hourly Heatmap | Activity by hour of day |
| Quality Analysis | Deep work versus interrupted sessions, with a text insight |

Charts render only when a tab is opened. You can also add a session manually (simple or detailed mode) if you forgot to start the timer. The day panel on the main window summarizes today as blocks of consecutive work, and each block has a detail report with net work, efficiency, interruptions and a timeline.

### Responsive window

The main window has no hard minimum size. It scales down to a 150 by 240 px strip so it can sit at the edge of your screen. Controls fold into a menu as the window narrows, the timer font fits the available space, and side panels never resize the window: they sit beside the timer when there is room and overlay it when there is not.

### System integration

- **Do Not Disturb.** Toggle KDE Do Not Disturb with the DND button or Ctrl+D. The inhibition is released when MFDP exits.
- **Plasma panel widget.** Show the timer in a KDE panel. See below.
- **Sounds.** Cues for session start and completion, plus an optional chime on the hour and half hour.
- **In-app updates.** Check for new releases from the settings dialog.

### Event tracking

Sessions are recorded at the event level (start, complete, interruptions, DND toggles, milestones) with elapsed-time offsets and JSON metadata, so they can be analyzed later. The full data map, including every table and file, is in [`documentation/VERI_HARITASI.md`](documentation/VERI_HARITASI.md).

## Installation

Requirements: Python 3.10 or later and Linux. KDE is recommended for Do Not Disturb and the panel widget; other desktops work without those two features.

```bash
git clone https://github.com/CenMert/MFDP.git
cd MFDP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Arch Linux users may need the `qt6-tools` system package for some Qt multimedia features.

## Usage

```bash
python3 -m mfdp_app.main
```

or

```bash
bash run.sh
```

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Ctrl+P | Toggle the plan panel |
| Ctrl+B | Toggle the streak panel |
| Ctrl+S | Save the plan for the selected task |
| Ctrl+D | Toggle Do Not Disturb |
| I / E | Mark an internal / external interruption |
| Esc | Close the open side panel |

### KDE panel widget

```bash
bash install_plasmoid.sh
```

Then right-click the panel, choose Add Widgets, and pick "MFDP Timer". The widget shows the task color and elapsed time; clicking it starts or finishes the session. It shows a dim icon when MFDP is closed. The app writes its state to `$XDG_RUNTIME_DIR/mfdp/state.json` and receives commands through the `org.mfdp.Timer.Toggle` D-Bus call.

## Updating

Open Settings and choose "Güncellemeleri Kontrol Et". If a newer [GitHub release](https://github.com/CenMert/MFDP/releases) exists, MFDP can update itself when it was installed with `git clone`, has no local changes and `git` is on the path. It reinstalls dependencies when `requirements.txt` changed and offers to restart. Your database is never touched. In any other case it opens the release page.

Release history is in [`CHANGELOG.md`](CHANGELOG.md).

### Publishing a release (maintainer)

1. Set `__version__` in `mfdp_app/version.py` and make sure `CHANGELOG.md` has a section for that version.
2. Commit, then `git tag vX.Y.Z && git push origin main --tags`.
3. Create a GitHub Release from the tag, using the changelog section as the description.

## Technology

| Layer | Library |
|-------|---------|
| Language | Python 3.10+ |
| GUI | PySide6 |
| Charts | Matplotlib |
| Database | SQLite3, connection-pooled |
| Styling | QSS, earthy dark theme (`ui/palette.py`) |

## Project structure

```
mfdp_app/
  core/    timer, event recording, task managers, review and plan schedulers,
           streak maths, DND, calendar import/export, updater, panel bridge
  db/      connection pool, schema setup and migrations, one repository per area
  ui/      main window, plan and streak panels, calendar, statistics, dialogs,
           theme and palette, responsive layout helpers
  models/  data classes
plasmoid/  KDE Plasma panel widget
documentation/  data map, architecture notes, proposals
```

`core/` never imports from `ui/`; Qt signals are the only path between them. See [`CLAUDE.md`](CLAUDE.md) for architecture details and conventions.

## License

MIT. See [LICENSE](LICENSE).
