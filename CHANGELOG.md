# Changelog

## 1.1.0

This release turns MFDP from a Pomodoro timer into a tool for planning, measuring and reviewing study work. It collects everything merged since 1.0.0.

### Timer

- Free Timer (count-up) is now the default mode. There is no pause: start, mark interruptions, finish. Continuing is a new session, so break length is the gap between sessions.
- Internal (`I`) and external (`E`) interruptions are logged without stopping the session. Closing the app no longer counts as an interruption.
- Sessions under 60 seconds are discarded as accidental starts.
- New sessions are tagged `timer_model = countup_v1`, and `session_completed` carries an `end_reason`.
- Pomodoro mode is unchanged.
- Mini always-on-top window with the task color and elapsed time; a click starts or finishes the session.

### Planning

- Plan panel (Ctrl+P) replaces the separate hierarchical task window. It holds the task tree and the session plan.
- Starting a session requires a task and, in Free Timer, an estimate. An optional first-step note is stored with the session. Estimate and note are saved per task (Ctrl+S, or automatically when switching tasks).
- A notification fires when the estimate is reached.
- If-then plans: scheduled prompts with Start, snooze (10 minutes) or skip, linked to the saved session.

### Streaks and spaced review

- Streak panel (Ctrl+B): 18-week contribution grid, tolerant streak, last-7-days count and 28-day plan adherence.
- Post-session feedback: focus rating (1 to 5) and session kind (reading, problems, review, production, other).
- Exam-aware spaced review on a 1-3-7-14-30 day schedule, built from the existing task tree. Exam dates pull due dates earlier, and the queue is capped at 5 per day without accumulating debt.
- Review is opt-in per course, so open-ended work such as a thesis is never forced into a schedule.
- Lecture log: record what was covered; each topic becomes a subtask that enters the review schedule.
- Recall answers on review sessions advance or reset a topic.

### Calendar

- Month-view calendar for exams, homework, meetings and date ranges.
- Exams can be linked to a course.
- JSON import and export with validation, a preview and an AI prompt for converting a schedule.

### Statistics

- Manual session entry (simple and detailed modes) with a clock picker, duration presets and a 03:00 logical-day boundary.
- Day panel with blocks of consecutive work and a per-block detail report.

### Window and interface

- Responsive main window usable down to a 150 by 240 px strip. Density steps by width, the timer font fits the window, controls fold into a menu, and long text is elided.
- Side panels (streak on the left, plan on the right) never resize the window: side by side at 640 px or wider, an overlay with a back button below that. Esc closes the open panel.
- Earthy color palette replaces the previous theme.

### System integration

- KDE Plasma panel widget with a state file and a D-Bus toggle bridge.
- Do Not Disturb now holds the inhibition correctly through a private D-Bus connection. It is controlled by one button (Ctrl+D), is released on exit, and is recorded as `dnd_toggled` events. The automatic-on-focus checkbox was removed.
- In-app update check through GitHub Releases.

### Database

- New tables and columns, all migrated automatically: review state and log, if-then plans and plan log, `tasks.review_enabled`, `calendar_events.task_id`, `sessions_v2.focus_rating`, `session_kind` and `planned_duration_minutes`. Existing data is kept.

### Documentation

- Full data map in `documentation/VERI_HARITASI.md`.
- Count-up-first proposal, study-optimization research notes and refreshed architecture documents.
- Icon checklist under `mfdp_app/resources/icons`.

### Fixes

- Courses marked completed no longer produce review reminders.
- Disabled buttons look disabled.
- The hamburger menu is readable on the dark theme.
- Layout no longer breaks at small window sizes.

## 1.0.0

Initial release: Pomodoro and count-up timers, flat and hierarchical tasks, atomic event tracking, statistics, DND integration and gong mode.
