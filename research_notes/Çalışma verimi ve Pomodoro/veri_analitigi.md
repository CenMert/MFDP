# Data analytics for focus/productivity tracking, mapped onto MFDP's data model

Scope: (1) behavioral signals linked to focus/productivity/learning, (2) metrics and analyses derived from them in research and products, (3) what MFDP can compute today from `sessions_v2`, `atomic_events`, `tasks`, `calendar_events`/`calendar_ranges`, and which extra data is worth adding. Schema checked against `mfdp_app/db/database_initializer.py` (atomic_events.session_id is a FK to sessions_v2.id; calendar kinds = `sinav`, `odev`, `toplanti`, `diger` per `mfdp_app/core/calendar_io.py`).

Evidence labels used below: **[R]** = peer-reviewed research; **[V]** = vendor/app documentation or vendor-published data (not independently verified); **[A]** = anecdotal/practitioner; **[I]** = my inference.

---

## Q1. Which behavioral signals are known to relate to focus, productivity and learning?

### Takeaway
The best-evidenced signals are (a) attention fragmentation, meaning how long someone stays on one screen or task before switching; (b) interruptions, split into self-initiated and external ones; (c) time of day and day of week, interacting with chronotype; and (d) breaks. All of the cited studies use small samples of information workers or students (n ≈ 14–90). The exception is FlowLight (n = 449). Their effects show up within a person, but they are correlational. MFDP already captures (b) partially (pauses), (c) fully (timestamps) and (d) partially (break sessions). It captures nothing yet for (a), because `focus_shift_detected` is not wired.

### Cited Findings
**Attention span and switching (Gloria Mark and colleagues)**
- [R] Screen attention has shrunk over time: about 2.5 min on a screen before switching in 2004 (in-person observation of 14 information workers at one organisation), about 75 s in 2012, and about 47 s on average from around 2016 onward (automatic computer logging). The median is about 40 s, and one replication found 44 s. Mark herself cautions that this measures *screen switching*, not a biological attention limit, and that a switch is not necessarily a distraction. — [Steelcase podcast transcript with G. Mark (2023)](https://www.steelcase.com/research/articles/our-47-second-attention-span-with-gloria-mark-s5-ep3-transcript/); [UCI podcast (2023)](https://news.uci.edu/2023/05/05/uci-podcast-if-you-cant-pay-attention-youre-not-alone); [Annie Duke Q&A on *Attention Span* (2023)](https://annieduke.substack.com/p/q-and-a-with-gloria-mark-author-of)
- [R] "Neurotics Can't Focus" (Mark, Iqbal, Czerwinski, Johns, Sano; CHI 2016) logged the online activity of 40 information workers over 2 work weeks. Median screen focus was about 40 s. Higher Neuroticism went with shorter focus, while higher Impulsivity-Urgency went with *longer* focus. **Shorter focus duration was associated with lower self-rated productivity at the end of the day.** A "lack of control" factor predicted multitasking. Stress and short sleep showed only trend-level associations. — [Microsoft Research page](https://www.microsoft.com/en-us/research/?p=238240); [MIT Media Lab entry](https://www.media.mit.edu/publications/neurotics-cant-focus-an-in-situ-study-of-online-multitasking-in-the-workplace/)
- [R] "Bored Mondays and Focused Afternoons" (Mark, Iqbal, Czerwinski, Johns; CHI 2014, pp. 3025–3034) followed 32 information workers for 5 days, combining logging with experience sampling. Self-reported focus **peaked mid-afternoon**, boredom was highest in early afternoon, and Mondays were both the most bored and the most focused days. People were happiest doing rote work and most stressed doing focused work. A Microsoft listing gives a conflicting title ("Bored Tuesdays") and says boredom peaked in the morning. The published abstract is the more reliable version. — [UCI ISR entry](https://isr.uci.edu/node/2035.html); [PDF](https://Www.Gwern.net/doc/psychology/writing/2014-mark.pdf); [MSR listing (conflicting)](https://microsoft.com/en-us/research/?p=166217)
- [A/R?] A widely repeated claim says it takes about 23–25 min to return to an interrupted task. It appears in coverage of Mark's book, but I found no primary source in this session. Treat it as unverified. — [Silicon Canals coverage](https://siliconcanals.com/t-screen-attention-47-seconds-gloria-mark/)

**Interruptions: external vs self**
- [R] "The Cost of Interrupted Work: More Speed and Stress" (Mark, Gudith, Klocke; CHI 2008, pp. 107–110) was a lab study. Interrupted participants finished tasks **faster with no quality loss**, but reported **higher stress, frustration, time pressure and effort**. The context of the interruption made no difference. Openness and need for structure predicted the cost. — [PDF](https://www.interruptions.net/literature/Mark-CHI08.pdf)
- [R] "Why Do I Keep Interrupting Myself?" (Dabbish, Mark, González; CHI 2011) analysed 889 h of observed task switching by 36 people in 3 organisations. Self-interruption depends on environment (more in open-plan offices), on individual differences, **and on the external interruptions a person has recently experienced**. Self-interruptions are often made to *return* to central solitary work, which suggests prospective memory plays a role. — [PDF](https://www.ics.uci.edu/~gmark/Home_page/Publications_files/CHI%202011%20Self-interruption.pdf); [UCI entry](https://isr.uci.edu/node/1353.html)
- [A] Cirillo's Pomodoro Technique classifies interruptions as **internal** (self-initiated) or **external** (caused by others). External ones are handled with "inform, negotiate, call back". Interruptions are marked on the To-Do sheet, and a daily **Records** sheet logs date, task, pomodoros used, interruption counts and wrong estimates. Secondary sources disagree on which mark (apostrophe or dash) denotes which type. — [U. Waterloo handout citing Cirillo 2007](https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf); [FacileThings blog](https://facilethings.com/blog/en/interruptions-on-pomodoro); [Befreed summary](https://www.befreed.ai/book/the-pomodoro-technique-by-francesco-cirillo)
- [R] FlowLight (Züger et al., CHI 2017, Honorable Mention) paired a traffic-light LED with an automatic interruptibility measure based on keyboard and mouse activity. In a field study with 449 participants across 12 countries, it **cut interruptions by 46%**, raised awareness of how disruptive interruptions are, and most participants kept using it. — [UBC CS news](https://www.cs.ubc.ca/news/2017/05/computer-science-professor-thomas-fritzs-flowlight-research-featured-new-yorker); [DOI 10.1145/3025453.3025662](https://unpaywall.org/10.1145%2F3025453.3025662)

**Time of day / chronotype**
- [R] Schmidt, Collette, Cajochen & Peigneux (2007), "A Time to Think: Circadian Rhythms in Human Cognition," *Cognitive Neuropsychology* 24(7):755–789. Performance on attention, executive-function and memory tasks varies with time of day. It also depends on the **synchrony** between a person's chronotype and the time of testing. — [ORBi](https://orbi.uliege.be/handle/2268/4666)

**Breaks**
- [R] Biwer, Wiradhany, oude Egbrink & de Bruin (2023), *British Journal of Educational Psychology*, studied 87 students in a real study session under three schedules: 24/6 min (Pomodoro-like), 12/3 min, or self-regulated breaks. Self-regulated breakers took longer study and break periods and reported **more fatigue and distractedness and less concentration and motivation**. Task completion and mental effort did not differ. Fixed breaks appeared to bring mood and efficiency benefits. The citation details conflict across sources: 93(2):353–367 vs 93(3):1096–1113, with DOI 10.1111/bjep.12593. — [Maastricht CRIS](https://cris.maastrichtuniversity.nl/en/publications/understanding-effort-regulation-comparing-pomodoro-breaks-and-sel); [ERIC record](https://nufind.nu.edu.sa/EdsRecord/eric,EJ1386535)
- [R] A follow-up by Smits, Wenzel & de Bruin (2025) reportedly found that fatigue rose *faster* under Pomodoro than under self-regulated breaks, with no productivity or completion difference. The two studies therefore disagree on fatigue. I saw this only in a search summary and did not verify it in the full paper. — [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/)

**Planning / estimation and deadlines**
- [R] Buehler, Griffin & Ross (1994), "Exploring the 'planning fallacy'," *JPSP* 67:366–381. 37 honours students predicted their thesis completion. The mean "best" estimate was 33.9 days (one source gives 27.4 days for the "everything goes well" case), the worst case was 48.6 days, and actual completion took **55.5 days**. Only about 30% finished by their predicted date. People were more optimistic about their own work than about others'. — [PDF](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf); [Wikipedia summary](https://en.wikipedia.org/wiki/Planning_fallacy)
- [R] Ariely & Wertenbroch (2002, *Psychological Science*) reported that people voluntarily set costly deadlines for themselves, and that these helped but less than evenly spaced external deadlines. **A 2026 replication of Study 2 (Hyndman & Bisin, *Psychological Science*) found negligible effects of deadline structure on performance.** Treat "self-imposed deadlines curb procrastination" as contested. — [Stafforini abstract](https://stafforini.com/works/ariely-2002-procrastination-deadlines-performance/); [Replication, Psych Science 2026](https://journals.sagepub.com/doi/full/10.1177/09567976261460772)

### Inferences
- [I] Of the classic signals, MFDP already captures timing (start/end, hour, weekday), completion, pause and interruption counts with their offsets, and planned vs actual duration. It is blind to *what happened during* a session: no window switching, no interruption reason, no subjective rating. That is the main gap compared with Mark-style research.
- [I] In MFDP a "pause" (`interruption_detected`, reason `user_pause`) mixes internal and external interruptions. Dabbish 2011 shows the two types feed each other, and Cirillo's method treats them differently, so recording the type is cheap and high in value.
- [I] Mark 2008 implies that interruptions may not lower measurable output in MFDP (completion), but may raise stress. That is another reason a subjective post-session rating adds information that duration and completion cannot.

### Gaps
- The primary source for "23 min 15 s to resume" (often attributed to Mark, González & Harris 2005, "No task left behind?", CHI 2005) could not be retrieved; my search failed. Do not quote the number without verification.
- I found no primary study on window switching specifically during *student* self-study with Pomodoro timers.
- Effect sizes for time-of-day effects on real-world study output (as opposed to lab cognitive tasks) were not found.

---

## Q2. What metrics and analyses do researchers and tools derive, and what do they show about dashboards that change behavior?

### Takeaway
Research tools such as PersonalAnalytics/WorkAnalytics, TimeAware and FlowLight, and commercial tools such as RescueTime, Rize and Focus To-Do derive time-on-category, context-switch rate, focus-session length, interruption counts and composite scores. The evidence on behavior change is mixed. Awareness rises reliably. Actual behavior change needs **actionable insights**, low-effort ambient feedback, and (per one study) **framing that highlights distraction rather than productivity**. Small single-user data favour descriptive statistics, survival-type and logistic models, change-point detection and N-of-1 self-experiments over complex ML.

### Cited Findings
**Research tools and dashboard effects**
- [R] Meyer et al., "Design Recommendations for Self-Monitoring in the Workplace" (CSCW 2018 / PACM HCI). The authors iterated with 20 developers, surveyed 413 and built the **WorkAnalytics** probe. In a 3-week field study with 43 developers, self-monitoring combined with experience sampling (periodic self-reported productivity) **increased awareness and motivated many to improve**. A wide variety of metrics was needed, and **actionable insights, possibly enriched with co-worker benchmarks**, are likely needed for behavior change. — [UZH Merlin](https://www.merlin.uzh.ch/publication/show/15499); [ZORA preprint](https://www.zora.uzh.ch/server/api/core/bitstreams/f6202968-ef6f-406e-8cec-df836cf77231/content)
- [R] An earlier PersonalAnalytics field study found the tool gave meaningful insights to **82%** of participants, but for **41%** those insights were not actionable enough to change behavior. The tool was revived in 2024 as a cross-platform TypeScript/Electron app, though without the retrospection feature yet. — [UZH PersonalAnalytics project page](https://www.ifi.uzh.ch/en/seal/people/meyer/personal-analytics.html); [ecosyste.ms repo record](https://science.ecosyste.ms/projects/58372)
- [R] TimeAware (Kim, Jeon, Choe, Lee, K. Kim, Seo; CHI 2016, pp. 272–283) combined an ambient desktop widget with a web dashboard in an 8-week deployment with 24 participants. **Only the negative framing condition, which emphasised distracting time, improved productivity.** The ambient widget helped keep people engaged. — [CHI 2016 PDF](https://terpconnect.umd.edu/~choe/download/CHI-2016-Kim-TimeAware.pdf); [MSR page](https://www.microsoft.com/en-us/research/?p=337619)
- [R] Epstein, Ping, Fogarty & Munson, "A Lived Informatics Model of Personal Informatics" (UbiComp 2015, pp. 731–742). The study surveyed 105, 99 and 83 trackers and interviewed 22. Their model runs from deciding and selecting a tool, through collection, integration and reflection, to **lapsing and resuming**. Many people track without a strict behavior-change goal, and lapsing is normal, so designs should support it. The paper won the UbiComp 2025 10-year impact award. — [PDF](https://my.eng.utah.edu/~cs5540/au16/readings/PersonalInformatics-Epstein2015.pdf); [UW HCDE news (2025)](https://www.hcde.washington.edu/index.php/news/article/2025-10-15/professor-sean-munson-and-collaborators-recognized-10-year-impact-award)
- [R] FlowLight (above) shows that ambient, automatic signals (an interruptibility light) changed *others'* behavior: interruptions fell 46%. — [UBC](https://www.cs.ubc.ca/news/2017/05/computer-science-professor-thomas-fritzs-flowlight-research-featured-new-yorker)

**Commercial tools: what they compute**
- [V] **RescueTime Productivity Pulse** (0–100) is a time-weighted score. Each activity's time is weighted Focus Work = 4 (100), Other Work = 3 (75), Neutral = 2 (50), Personal = 1 (25), Distracting = 0 (0), divided by total time and scaled to 100. Focus Work is defined by how the user categorises apps and sites. Older docs use 5 buckets, newer ones 4 levels. — [RescueTime help: Pulse](https://help.rescuetime.com/article/73-how-is-my-productivity-pulse-calculated); [Understanding Your Data](https://help.rescuetime.com/article/461-understanding-your-data); [Focus Work goal](https://help.rescuetime.com/article/292-focus-work-goal)
- [V] **Rize** has a "Focus Quality Score" built from more than 20 work attributes, notably context switching, focus-session length and daily focus time. It reports the apps and sites that interrupted each focus session most, automatically detects "deep work" as stretches without app switches or idle gaps, and offers suggested breaks, a blocker, and daily and weekly reports. A Rize blog post (2026, vendor data) claims the average user switched context 559 times a day, about once every 35 s. — [Rize weekly assessment](https://rize.io/blog/releasing-the-new-weekly-productivity-assessment); [Rize context-switching post](https://rize.io/blog/the-hidden-cost-of-context-switching); [Ness Labs interview](https://nesslabs.com/rize-featured-tool)
- [V] **Focus To-Do** reports time distribution, completed-task counts, a trend chart of completed tasks vs focus time, and daily, weekly and monthly views. The vendor claims 200M focus hours logged. — [App Store listing](https://apps.apple.com/app/id1258530160)
- [V/A] **Forest** offers statistics, labels and tree-growing gamification, per third-party reviews only. — [emelia.io review](https://emelia.io/hub/the-5-best-pomodoro-timer-apps-in-2025)

**Statistical methods suitable for N = 1**
- [R] N-of-1 self-experimentation: TummyTrials (Karkar et al., CHI 2017) let 15 IBS patients run structured self-experiments reliably. It also found a **tension between scientific validity and the lived experience** of following a protocol. Participants wanted more flexibility in experimental design. Related platforms include QuantifyMe, StudyU, StudyMe and SelfE (Daskalova et al., 2021). — [PMC5432136](https://pmc.ncbi.nlm.nih.gov/articles/PMC5432136); [TummyTrials PDF](https://people.cs.umass.edu/~rkarkar/pubs/conf-chi2017-tummytrials.pdf); [Hypothesis formation workshop paper](https://homes.cs.washington.edu/~jfogarty/publications/workshop-chi2017-hypothesisformationandtesting.pdf); [arXiv review 2026](https://arxiv.org/pdf/2608.03251)

### Inferences
- [I] **Method fit for MFDP (single user, roughly 100s–1000s of sessions):**
  - *Descriptive statistics with medians and IQR* by hour, weekday, tag and planned length. These should come first.
  - *Survival analysis* (Kaplan–Meier) on "time to first pause", where sessions completed without any pause are right-censored at their duration. This handles censoring correctly, whereas a plain mean of time to first pause is biased. Python's `lifelines` library can run it locally.
  - *Logistic regression* (or a Bayesian beta-binomial per bucket) for P(completed) given hour, planned length, tag, sessions already done today, and days to the nearest exam. Keep it to 3–5 predictors because of the small n.
  - *Change-point detection* (e.g. `ruptures`) on daily focus minutes to spot regime shifts such as exam periods or a semester start.
  - *Bayesian updating* (beta prior on completion rate) gives stable estimates for sparse buckets, such as "Sunday 07:00".
  - *N-of-1 A/B tests:* randomise the day or session length (25 vs 50 min) and the break regime (fixed vs self-regulated). Biwer 2023 and Smits 2025 disagree on fatigue, which makes this a sensible personal experiment. Alternate assignments (ABAB) or randomise daily to reduce time confounding.
- [I] **Pitfalls:**
  - Small n and multiple comparisons: hour × weekday × tag cells will be noisy, so shrink estimates or pool them.
  - Confounding: exam proximity drives both hours worked and choice of task.
  - Selection: abandoned sessions include "mode change", which is not failure.
  - Goodhart's law: if "completion rate" becomes the target, the user may plan shorter sessions or avoid hard tasks. Show planned minutes alongside it.
  - Reactivity: tracking itself changes behavior.
  - Lapses (Epstein 2015): gaps in data are normal and should not be treated as zero productivity without a flag.
  - Privacy: window titles are sensitive, so keep everything local, store app class rather than full title, and offer opt-in.
- [I] **Dashboard design implications:** surface 1–3 *actionable* insights rather than many charts (Meyer 2018; 41% non-actionable in PersonalAnalytics). Consider distraction-framed messages, e.g. "You lost 34 min to pauses this week" (TimeAware). Use an ambient indicator, since MFDP already has a Plasma widget and DND. Treat lapses gently.

### Gaps
- No peer-reviewed validation exists of composite vendor scores (RescueTime Pulse, Rize Focus Quality) against outcomes such as grades or output.
- Toggl and "Session" app analytics were not researched for lack of tool budget. Toggl Track is known for time-entry reports by project and tag, but that is not cited here.
- Goodhart's law in personal tracking: no specific empirical study was retrieved. It is presented as a general principle.
- Meyer et al., "The Work Life of Developers: Activities, Switches and Perceived Productivity" (IEEE TSE 2017, DOI 10.1109/TSE.2017.2656886) is relevant: developers switch frequently, and self-perceived productivity relates to fragmentation. I recall this from training knowledge but did **not** verify it in this session.

---

## Q3. What can MFDP compute from current data, and what additional data would be most valuable?

### Takeaway
With no schema change, MFDP can already compute about 15 research-aligned metrics: hourly and weekday chronotype profiles, completion rate, interruption rate per focus hour, time to first pause (with survival curves), pause-length distribution, planned-vs-actual estimate accuracy at session and task level, break compliance, streaks, fatigue within a day, and workload around exams. The cheapest high-value additions are a **1–5 focus/energy rating plus an internal/external interruption reason**, which take 2 clicks per session. Next is **wiring `focus_shift_detected`** to get Mark-style switch metrics, followed by optional outcome measures linked to calendar events.

### Cited Findings
(Support for the importance of each metric is cited in Q1 and Q2. The SQL below is my design [I], based on the schema in `mfdp_app/db/database_initializer.py`.)
- Self-rated productivity correlates with focus duration, which makes a subjective post-session rating a meaningful label — [Mark et al. CHI 2016](https://www.microsoft.com/en-us/research/?p=238240)
- Experience sampling paired with logs increased awareness in a field deployment — [Meyer et al. CSCW 2018](https://www.merlin.uzh.ch/publication/show/15499)
- The internal/external split is the canonical Pomodoro interruption record — [Waterloo/Cirillo](https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf); self-interruptions are driven by external ones — [Dabbish et al. 2011](https://isr.uci.edu/node/1353.html)
- Window-switch logging is the basis of the 40–47 s attention findings — [Mark, Steelcase transcript](https://www.steelcase.com/research/articles/our-47-second-attention-span-with-gloria-mark-s5-ep3-transcript/)
- Planned-vs-actual tracking fits planning-fallacy evidence — [Buehler et al. 1994](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf)

### Inferences

#### A. Computable today (SQL / analysis sketches, SQLite)
Conventions: logical day = `date(start_time, '-3 hours')`, focus rows = `mode='Focus'`, and `start_time` is local ISO text.

1. **Chronotype profile (focus minutes and completion by hour and weekday).**
   ```sql
   SELECT strftime('%H', start_time) AS hr,
          strftime('%w', date(start_time,'-3 hours')) AS wd,
          SUM(duration_seconds)/60.0 AS focus_min,
          AVG(completed) AS completion_rate, COUNT(*) AS n
   FROM sessions_v2 WHERE mode='Focus' GROUP BY hr, wd;
   ```
   - Peak hours = argmax of completion_rate × focus_min, shown only where n ≥ 5. Compare with Mark 2014 (mid-afternoon focus peak) and Schmidt 2007 (synchrony).

2. **Completion rate and its breakdown by abandonment reason.**
   - Join `atomic_events` rows with `event_type='session_abandoned'` and group by `json_extract(metadata,'$.reason')`. Mode changes and app exits should not count as "failures".

3. **Interruption rate per focus hour.**
   ```sql
   SELECT SUM(interruption_count)*3600.0/SUM(duration_seconds) FROM sessions_v2 WHERE mode='Focus';
   ```
   - Trend this weekly, and compare by tag and by hour.

4. **Time to first interruption, using survival analysis.**
   ```sql
   SELECT s.id, s.completed, s.duration_seconds,
          MIN(e.elapsed_seconds) AS t_first_pause
   FROM sessions_v2 s LEFT JOIN atomic_events e
     ON e.session_id=s.id AND e.event_type='interruption_detected'
   WHERE s.mode='Focus' GROUP BY s.id;
   ```
   - The event is t_first_pause. If it is NULL, the session is censored at duration_seconds.
   - Run Kaplan–Meier overall and stratified by planned length (25 vs 50), tag, or morning vs evening. The median survival time is a personal "focus span" metric, the Pomodoro-scale analogue of Mark's 40–47 s.

5. **Pause-duration distribution.**
   - Take `json_extract(metadata,'$.pause_seconds')` from `session_resumed`. Plot a histogram or ECDF and track median and P90.
   - Long pauses above some threshold (say 10 min) are likely external or abandoned contexts.
   - Total pause time ÷ (active + pause) gives a fragmentation ratio.

6. **Milestone attrition curve.**
   - Count focus sessions reaching 25%, 50%, 75% and completion (`milestone_reached` metadata). This shows *where* sessions die.

7. **Estimate accuracy at session level.**
   - Compute `duration_seconds/(planned_duration_minutes*60)` for completed and abandoned sessions.
   - At task level: `SUM(duration_seconds)` per task_name vs `tasks.planned_duration_minutes` for completed tasks. The median ratio is greater than 1 under the planning fallacy.
   - Track the ratio by tag and over time (is calibration improving?). The personal median ratio can serve as an automatic "reference-class" correction factor for future estimates.

8. **Break compliance.**
   - For each completed focus session, check whether the next session within N minutes is a Short or Long Break and whether it was completed. Also measure the break's actual length vs planned. Gaps longer than X with no break session count as "untracked break".
   - Relate this to the next focus session's completion and time to first pause. That is a personal test of the Biwer 2023 idea.

9. **Fatigue within a day.**
   - Assign each focus session its ordinal k within the logical day: `ROW_NUMBER() OVER (PARTITION BY date(start_time,'-3 hours') ORDER BY start_time)`.
   - Plot completion rate and interruption rate against k, and against cumulative focus minutes before the session. A declining slope suggests a fatigue threshold, which can drive "daily cap" advice.

10. **Consistency and streaks.**
    - Count consecutive logical days with at least X focus minutes, plus the coefficient of variation of daily minutes and the number of active days per week. Per Epstein 2015, show lapses neutrally.

11. **Deep blocks.**
    - The existing "blocks" (same task within 30 min) give block length distribution, sessions per block, and the share of focus time inside blocks of 2 or more sessions. This is a proxy for sustained engagement and a switch rate between tasks per day (count of distinct task_name transitions).

12. **Deadline proximity and procrastination curve.**
    - For each `calendar_events` row of kind `sinav` or `odev`, sum focus minutes per day for days −21…0, optionally filtered to sessions whose tag or task matches the course.
    - Average these across exams to get a personal "cramming curve": the share of total prep done in the last 3 days, and the day by which 50% of prep was done.
    - `calendar_ranges` can mark exam weeks as a covariate.
    - Caveat: Ariely & Wertenbroch's deadline findings did not replicate in 2026, so frame this as descriptive only.

13. **Best session length for completion.**
    - Group by planned_duration_minutes and compute completion rate (with Bayesian beta(1,1) intervals) and minutes per completed session. Pick the length that maximises *expected completed focus minutes* = planned × P(complete), not raw completion rate. This avoids Goodhart's law, since shorter sessions trivially complete more often.

14. **DND effect.**
    - Compare interruption rate in sessions where `dnd_toggled` was on vs off. This is observational and confounded by intent.

15. **Change-point and trend.**
    - Run change-point detection on weekly focus minutes, completion rate and interruption rate to flag regime changes, such as a semester start or a new habit.

16. **Simple prediction model.**
    - Logistic regression of completed on planned length, hour bucket, k-th session today, days to next exam, tag, and pauses so far. Use it for a live "risk" hint or for choosing the default session length.
    - Evaluate with time-ordered cross-validation rather than random splits.

#### B. Additions ranked by value-to-cost [I]

| # | Addition | Cost | Enables |
|---|---|---|---|
| 1 | **Post-session 1–5 focus rating** (and optionally 1–5 energy/mood) stored in a `session_completed` or abandoned metadata field, or a new `session_ratings` table | 1 click/session | Ground-truth label of *quality*, not just quantity. Validates that completion and interruptions mean "good focus" for this user (cf. Mark 2016 self-rated productivity; Meyer 2018 experience sampling). Rating by hour gives a subjective chronotype. Turns metrics into a supervised model. |
| 2 | **Interruption reason at pause: internal / external** (plus optional free-text or category such as phone, person, hunger or tiredness) added to `interruption_detected.metadata` | 1 click/pause | Cirillo's records sheet. Internal vs external rates by hour and tag. Tests Dabbish 2011 (external triggers self-interruption). Targeted advice: DND helps with external, task-chunking with internal. |
| 3 | **Wire `focus_shift_detected`** (app class from KDE active window; hash or omit titles; local only, opt-in) | Medium dev; privacy design | Mark-style screen-focus duration, switch rate per hour, top distracting apps per session (like Rize), RescueTime-like category time. Lets MFDP *verify* self-reports. Also yields `distraction_identified` via a user-labelled app list. |
| 4 | **Task difficulty / type** (1–3, or new / review / practice) on tasks | Once per task | Controls a key confounder in completion and estimate analyses. Makes the planning-fallacy ratio difficulty-specific. |
| 5 | **Outcome measures**: a grade or score attached to a `calendar_events` exam; optional per-session output count (pages, problems) | Low, occasional | Links process metrics to results: hours, cramming share and completion vs grade. This is the only way to test whether the analytics matter. n is tiny, so treat results as descriptive. |
| 6 | **Daily check-in: sleep hours / quality**, optional morning energy | 1 entry/day | Covariate for daily focus. Mark 2016 found trend-level sleep effects. Useful in N-of-1 analyses. |
| 7 | **`break_started/ended` with an activity tag** (screen / walk / phone) | Low | Break-quality analysis: does a phone break predict more interruptions next session? |
| 8 | **Location, music and environment** (`environment_changed`, e.g. home/library, music on/off) | Low–medium | Personal A/B tests of environment. Dabbish 2011 links the physical environment to self-interruption. |
| 9 | **Phone use** | High (needs phone integration) | Probably the biggest unmeasured distractor for students, but too costly now. A manual "phone" interruption reason (#2) approximates it. |
| 10 | **Experiment flag** (`experiment_id`, arm) on sessions | Very low | Proper N-of-1 trials, e.g. 25 vs 50 min or fixed vs self-regulated breaks (Biwer 2023 vs Smits 2025), with randomised daily assignment and analysis by arm (TummyTrials lessons: keep the protocol flexible). |

### Gaps
- I have not verified the exact JSON metadata keys in `atomic_events` beyond those named in the brief (`pause_seconds`, `active_seconds`, `reason`, `focus_completion_ratio`). The SQL assumes these names. The writer should check `mfdp_app/core/atomic_analyzer.py`.
- I found no published guidance on minimum session counts for reliable single-user chronotype estimates. The "n ≥ 5 per cell" rule above is a heuristic.
- I found no research on whether one-click post-session ratings cause rating fatigue or response bias over months of use. The ESM literature generally suggests keeping prompts short, but no specific source was retrieved.

---

### Reference list (as verified in this session; venues and years from the cited pages)
1. Mark, G., Iqbal, S. T., Czerwinski, M., Johns, P., Sano, A. (2016). Neurotics Can't Focus: An in situ Study of Online Multitasking in the Workplace. *CHI 2016*, pp. 1739–1744. https://www.microsoft.com/en-us/research/?p=238240
2. Mark, G., Iqbal, S. T., Czerwinski, M., Johns, P. (2014). Bored Mondays and Focused Afternoons: The Rhythm of Attention and Online Activity in the Workplace. *CHI 2014*, pp. 3025–3034. https://isr.uci.edu/node/2035.html
3. Mark, G., Gudith, D., Klocke, U. (2008). The Cost of Interrupted Work: More Speed and Stress. *CHI 2008*, pp. 107–110. https://www.interruptions.net/literature/Mark-CHI08.pdf
4. Dabbish, L., Mark, G., González, V. M. (2011). Why Do I Keep Interrupting Myself? Environment, Habit and Self-Interruption. *CHI 2011*. https://isr.uci.edu/node/1353.html
5. Mark, G. (2023). *Attention Span: A Groundbreaking Way to Restore Balance, Happiness and Productivity*. Hanover Square Press. Interview transcript: https://www.steelcase.com/research/articles/our-47-second-attention-span-with-gloria-mark-s5-ep3-transcript/
6. Meyer, A. N., et al. (2018). Design Recommendations for Self-Monitoring in the Workplace: Studies in Software Development. *PACM HCI (CSCW 2018)*. https://www.merlin.uzh.ch/publication/show/15499
7. Meyer, A. N., et al. PersonalAnalytics project (UZH). https://www.ifi.uzh.ch/en/seal/people/meyer/personal-analytics.html
8. Züger, M., et al. (2017). Reducing Interruptions at Work: A Large-Scale Field Study of FlowLight. *CHI 2017*. DOI 10.1145/3025453.3025662
9. Kim, Y.-H., Jeon, J. H., Choe, E. K., Lee, B., Kim, K., Seo, J. (2016). TimeAware: Leveraging Framing Effects to Enhance Personal Productivity. *CHI 2016*, pp. 272–283. https://terpconnect.umd.edu/~choe/download/CHI-2016-Kim-TimeAware.pdf
10. Epstein, D. A., Ping, A., Fogarty, J., Munson, S. A. (2015). A Lived Informatics Model of Personal Informatics. *UbiComp 2015*, pp. 731–742. DOI 10.1145/2750858.2804250
11. Karkar, R., Schroeder, J., Epstein, D. A., et al. (2017). TummyTrials: A Feasibility Study of Using Self-Experimentation to Detect Individualized Food Triggers. *CHI 2017*. https://pmc.ncbi.nlm.nih.gov/articles/PMC5432136
12. Schmidt, C., Collette, F., Cajochen, C., Peigneux, P. (2007). A Time to Think: Circadian Rhythms in Human Cognition. *Cognitive Neuropsychology* 24(7):755–789. https://orbi.uliege.be/handle/2268/4666
13. Biwer, F., Wiradhany, W., oude Egbrink, M., de Bruin, A. (2023). Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks. *British Journal of Educational Psychology* 93. DOI 10.1111/bjep.12593 (issue and pages conflict across sources). https://cris.maastrichtuniversity.nl/en/publications/understanding-effort-regulation-comparing-pomodoro-breaks-and-sel
14. Smits, Wenzel, de Bruin (2025). Follow-up Pomodoro vs self-regulated breaks study. Unverified summary. https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/
15. Buehler, R., Griffin, D., Ross, M. (1994). Exploring the "planning fallacy": Why people underestimate their task completion times. *JPSP* 67:366–381. https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf
16. Ariely, D., Wertenbroch, K. (2002). Procrastination, Deadlines, and Performance: Self-Control by Precommitment. *Psychological Science* 13(3). https://stafforini.com/works/ariely-2002-procrastination-deadlines-performance/
17. Hyndman, K., Bisin, A. (2026). Replication of Ariely & Wertenbroch (2002) Study 2. *Psychological Science*. https://journals.sagepub.com/doi/full/10.1177/09567976261460772
18. Cirillo, F. (2006/2007). *The Pomodoro Technique*. Summary handout: https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf
19. RescueTime Help Center: How is my Productivity Pulse calculated? https://help.rescuetime.com/article/73-how-is-my-productivity-pulse-calculated
20. Rize: Weekly productivity assessment / Hidden cost of context switching (vendor blog). https://rize.io/blog/releasing-the-new-weekly-productivity-assessment ; https://rize.io/blog/the-hidden-cost-of-context-switching
21. Focus To-Do App Store listing. https://apps.apple.com/app/id1258530160
22. (Unverified this session) Meyer, A. N., Barton, L. E., Murphy, G. C., Zimmermann, T., Fritz, T. (2017). The Work Life of Developers: Activities, Switches and Perceived Productivity. *IEEE TSE* 43(12). DOI 10.1109/TSE.2017.2656886
