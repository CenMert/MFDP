# SM-2 and FSRS for topic-level review scheduling in MFDP

Research date: 2026-10-16. Legend: **[V]** = verified by fetching the source during this research; **[R]** = recalled from prior knowledge, not re-fetched (treat as needing confirmation); **[C]** = computed locally from verified formulas.

---

## 1. SM-2: exact algorithm, weaknesses, Anki's modified SM-2

### Takeaway
SM-2 is a tiny, deterministic rule set (EF starts at 2.5, intervals 1 → 6 → I·EF, EF floor 1.3, reset to I(1) on grade < 3) with no explicit memory model or target retention. Anki's variant adds configurable learning steps, a 4-button scale and fixed ease deltas (−20/−15/0/+15 points), which causes the well-known "ease hell" drift.

### Cited Findings
- **[V] Origin:** Described by Piotr Wozniak in his 1990 master's thesis *Optimization of learning* (Poznan University of Technology); used in SuperMemo 1.0–3.0 from 13 Dec 1987 to 9 Mar 1989; named after SuperMemo 2.0 — [SuperMemo: SM-2](https://super-memory.com/english/ol/sm2.htm)
- **[V] Algorithm (verbatim steps):** — [SuperMemo: SM-2](https://super-memory.com/english/ol/sm2.htm)
  1. Split knowledge into smallest items; every item starts with E-Factor (EF) = 2.5.
  2. Intervals: I(1) = 1 day, I(2) = 6 days, I(n) = I(n−1) · EF for n > 2; round fractional intervals up.
  3. After each repetition grade q ∈ {0..5}.
  4. EF' = EF + (0.1 − (5 − q) · (0.08 + (5 − q) · 0.02)); if EF' < 1.3 set EF = 1.3. (q = 5 → +0.10; q = 4 → 0; q = 3 → −0.14; q = 2 → −0.32; q = 1 → −0.54; q = 0 → −0.80.)
  5. If q < 3, restart repetitions from I(1) **without changing EF**.
  6. Within the same day, repeat all items graded < 4 until they score ≥ 4.
- **[V] Grade semantics:** 5 perfect response; 4 correct after hesitation; 3 correct with serious difficulty; 2 incorrect, but the correct answer seemed easy to recall; 1 incorrect, but the correct answer was remembered; 0 complete blackout — [SuperMemo: SM-2](https://super-memory.com/english/ol/sm2.htm)
- **[V] Anki's modified SM-2:** user-configurable learning steps instead of the fixed 1/6 days; failures during learning do not lower ease. On review cards: Again → relearning, ease −20 points, interval × "new interval" setting; Hard → ease −15 points, interval × hard interval (default 1.2); Good → interval × ease, ease unchanged; Easy → interval × ease × easy bonus, ease +15 points; Hard/Good/Easy also × "interval modifier". Starting ease 2.5, minimum 130%. Each new interval (except after Again) is at least one day longer than the previous — [Anki FAQ: What spaced repetition algorithm does Anki use?](https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm)
- **[V] Lack of probability output:** SM-2 does not predict a recall probability, so RMSE/log loss cannot be computed on it natively; the srs-benchmark used an "SM-2-trainable" variant with added formulas to output probabilities — [Anki forum: FSRS vs SM2 in 2 separate profiles](https://forums.ankiweb.net/t/fsrs-vs-sm2-in-2-seperate-profiles/52171)
- **"Ease hell":** described as an effectively irreversible EF drift to the 1.3 floor (repeated Hard/Again lower ease by fixed steps, but Good never raises it, so only Easy recovers it) — [diane.app (commercial blog, 2026)](https://www.diane.app/en/guides/fsrs-vs-sm2). The mechanism follows directly from the verified Anki deltas above (Good = 0 change) — [Anki FAQ](https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm)
- **[R] Other SM-2 weaknesses** (well known in the SRS community): no forgetting-curve model, so no notion of "desired retention"; overdue/early reviews are handled identically to on-time reviews (the grade does not account for elapsed time); a single lapse resets to 1 day regardless of prior stability; the 1-day/6-day constants are fixed for all items. SuperMemo itself moved on to SM-17/SM-18 with a two-component (stability/retrievability) model.

### Inferences
- For MFDP, SM-2's main appeal is simplicity (≈15 lines, no dependency), but its fixed early intervals (1, 6, ~15 days) ignore exam deadlines and the "reset to 1 day" rule is harsh for coarse topic-level units where "failure" is partial.
- Anki's +15/−15/−20 deltas would need a fix for ease hell (e.g., mean reversion as in FSRS) if SM-2 were used.

### Gaps
- No primary-source (SuperMemo) text on "ease hell" was fetched; the term is community jargon.

---

## 2. FSRS: model, formulas, parameters, versions, evidence, adoption

### Takeaway
FSRS models each item with Difficulty D ∈ [1,10], Stability S (days until R drops to 90%) and Retrievability R; it uses a power forgetting curve and picks the next interval as the time at which predicted R falls to the user's desired retention (default 0.9). In the open srs-benchmark (≈10k Anki users, ~350M evaluated reviews) FSRS-6 has log loss 0.346 / RMSE(bins) 0.065, far better than HLR/Ebisu, and is reported to beat SM-2 variants for ~90–98% of users; it is built into Anki since 23.10 (FSRS-6 in Anki 25.07).

### Cited Findings

**Forgetting curve and interval [V]**
- FSRS-6: R(t,S) = (1 + factor · t/S)^(−w20), factor = 0.9^(−1/w20) − 1, chosen so R(S,S) = 0.9; w20 (decay) is trainable — [awesome-fsrs wiki: The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm)
- Interval: I(r,S) = (S / factor) · (r^(1/decay) − 1) with decay = −w20; rounded to whole days, floored at 1, capped at `maximum_interval` — [py-fsrs scheduler.py](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py). Hence at r = 0.9, I = S.
- FSRS-4.5: decay = −0.5, factor = 19/81. FSRS v4: R = (1 + t/(9S))^(−1), I = 9S(1/r − 1) — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm)

**Initial state [V]**
- S0(G) = w[G−1] (G: 1 Again, 2 Hard, 3 Good, 4 Easy) — [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py); [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm)
- D0(G) = w4 − e^(w5·(G−1)) + 1 (FSRS-5/6), clamped to [1,10]; v4 used D0(G) = w4 − (G−3)·w5 — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Difficulty update [V]**
- ΔD = −w6·(G−3); linear damping D' = D + ΔD·(10−D)/9; mean reversion D'' = w7·D0(4) + (1−w7)·D' (target changed from D0(3) in v4 to D0(4) in FSRS-5); clamp [1,10] — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Stability after success (recall) [V for structure; full formula from wiki v4 section + py-fsrs code fragments]**
- S'_r = S · ( e^(w8) · (11 − D) · S^(−w9) · (e^(w10·(1−R)) − 1) · [w15 if Hard] · [w16 if Easy] + 1 ). Interpretation: gain is larger when D is low, S is low (saturation), and R was low at review time (desirable difficulty / spacing effect) — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Stability after failure (lapse) [V]**
- S'_f = w11 · D^(−w12) · ((S+1)^(w13) − 1) · e^(w14·(1−R)); in FSRS-5/6 the result is min(S'_f, S / e^(w17·w18)) so a lapse can never increase stability — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Same-day (short-term) reviews [V]**
- FSRS-5: S' = S · e^(w17·(G − 3 + w18)); FSRS-6: S' = S · e^(w17·(G − 3 + w18)) · S^(−w19), with SInc ≥ 1 enforced for G ≥ 2 — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Default parameters [V]**
- FSRS-6 (21): [0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014, 1.8729, 0.5425, 0.0912, 0.0658, 0.1542] (so initial S for Again/Hard/Good/Easy ≈ 0.21 / 1.29 / 2.31 / 8.30 days; decay w20 = 0.1542) — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); same decay `FSRS_DEFAULT_DECAY = 0.1542` in [py-fsrs](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)
- FSRS-5 (19), FSRS-4.5 (17), FSRS v4 (17) default vectors are listed on the same wiki page — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm)
- **[C] Illustrative FSRS-6 default schedule** (all reviews rated Good, computed with the formulas above): desired retention 0.90 → intervals 2, 11, 46, 163, 497 days; 0.85 → 4, 31, 173, 772 days; 0.80 → 8, 76, 524 days. With the very flat default decay (0.1542), intervals are highly sensitive to desired retention. These defaults are fitted to Anki flashcard data, not to chapter-level review.

**Desired retention [V]**
- Users don't hand-tune weights; they set desired retention (default 0.9 in py-fsrs). Higher retention → more reviews per day — [Anki FAQ](https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm); [py-fsrs README](https://github.com/open-spaced-repetition/py-fsrs)

**Version history**
- v4 → 4.5: power curve changed from decay −1/factor 1/9 to decay −0.5/factor 19/81 [V]; FSRS-5: new D0 formula, mean reversion to D0(4), same-day stability term (w17, w18), 19 params [V]; FSRS-6: trainable decay w20, improved same-day formula with S^(−w19), 21 params [V] — [The Algorithm](https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm); "the formula for handling same-day reviews has been improved" — [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark)
- The benchmark README now also lists FSRS-7 variants (e.g., "FSRS-7 default param." log loss 0.3620 without same-day reviews) [V] — [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark). No FSRS-7 release in Anki/py-fsrs was confirmed.
- Release dates: wiki gives none [V]. Anki: FSRS available since 23.10 [V] — [Anki FAQ](https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm); FSRS-6 shipped with Anki 25.07 (per AnkiDroid 2.23.0 notes) [V, secondary] — [APKMirror: AnkiDroid 2.23.0](https://www.apkmirror.com/apk/ankidroid-open-source-team/ankidroid-flashcards/ankidroid-flashcards-2-23-0-release/); [Anki forum: FSRS 6 parameters](https://forums.ankiweb.net/t/bug-new-fsrs-6-parameters-not-appearing-after-reoptimizing/64921). [R] FSRS-4.5 arrived in Anki 23.12 and FSRS-5 in Anki 24.11 (not verified in this session). Latest Anki releases listed: 26.08 / 26.08.1 with fsrs-rs 6.6.1 [V] — [Anki releases](https://github.com/ankitects/anki/releases)

**Evidence [V]**
- KDD 2022: Ye, Su, Cao, "A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling", pp. 4381–4390: Markov memory model (DSR precursor) fitted on ~220M MaiMemo review logs; SSP scheduling to minimize review cost; 12.6% improvement over prior SOTA; deployed in MaiMemo — [HIT Scholar](https://scholar.hit.edu.cn/en/publications/a-stochastic-shortest-path-algorithm-for-optimizing-spaced-repeti/); [DBLP](https://dblp1.uni-trier.de/rec/conf/kdd/YeSC22.html)
- IEEE TKDE 2023 (vol. 35, no. 10, pp. 10085–10097): Su, Ye, Nie, Cao, Chen, "Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory": 64% lower recall-prediction error, 17% lower cost vs baselines; code at maimemo/SSP-MMC(-Plus) — [HIT Scholar](https://scholar.hit.edu.cn/en/publications/optimizing-spaced-repetition-schedule-by-capturing-the-dynamics-o/); [ecosyste.ms](https://science.ecosyste.ms/projects/15317)
- srs-benchmark: dataset from Anki users (README contains two conflicting statements: "20 thousand" users/~1.7B reviews [FSRS-Anki-20k] and "10 thousand" users/~727M reviews [anki-revlogs-10k]); results table over 9,999 collections, 349,923,850 evaluated reviews (without same-day) — [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark)
- Results (log loss / RMSE(bins) / AUC, without same-day reviews): FSRS-6 0.3460/0.0653/0.7034; FSRS-5 0.3561/0.0742/0.7010; FSRS-4.5 0.3625/0.0764/0.6891; FSRS v4 0.3726/0.0838/0.6853; HLR 0.4694/0.1275/0.6369; Ebisu v2 0.4989/0.1627/0.6051; LSTM 0.3332/0.0538/0.7329; GRU 0.3328/0.0549/0.7324; constant AVG baseline 0.3945/0.1034/0.4997; best: RWKV variants 0.2773 log loss — [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark). SM-2 rows were not present in the current README text (only as images/older versions).
- FSRS-5 beats SM-2-trainable in 97.4% of users; vs Anki-SM-2 (default), FSRS-5 default params better for 89.9% of users, optimized FSRS-5 for 98.1% (forum reports, secondary) — [Anki forum](https://forums.ankiweb.net/t/fsrs-vs-sm2-in-2-seperate-profiles/52171)
- Anki docs: FSRS needs fewer reviews for the same retention, handles long breaks better, preliminarily ≈ on par with SuperMemo's SM-17 — [Anki FAQ](https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm)

### Inferences
- The FSRS advantage is in *calibrated recall probability*, which matters for flashcards with thousands of reviews per user. Its parameter fitting needs hundreds+ of reviews; a single student with ~30–100 topic nodes will never produce enough data to optimize, so MFDP would rely on defaults (FSRS-7 "default param." still beats the AVG baseline in the benchmark, which suggests defaults are usable, but that's for flashcards).
- The key FSRS concept worth borrowing for MFDP is **R(t,S)**: it lets the app rank topics by "predicted current recall" and answer "what will R be on the exam date?", which SM-2 cannot.

### Gaps
- Exact FSRS-6 release date and default-parameter benchmark rows for FSRS-6/SM-2 could not be extracted from the README (results are partly images).
- No evidence that FSRS defaults are calibrated for multi-hour, chapter-sized review units.

---

## 3. Python implementations

### Takeaway
`py-fsrs` (PyPI `fsrs`, v6.3.2, MIT, Python ≥ 3.10) implements FSRS-6 with 21 parameters and has only `typing-extensions` as a runtime dependency; torch/numpy/pandas are needed only for the optional optimizer. It runs fully offline and serializes to JSON, so it fits a PySide6 + SQLite app. SM-2 is trivially implementable in pure Python.

### Cited Findings
- **[V]** `pyproject.toml`: version 6.3.2; `requires-python >= 3.10`; dependencies `["typing-extensions"]`; extra `optimizer = ["torch","numpy","pandas","tqdm"]`; MIT license classifier — [py-fsrs pyproject.toml](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/pyproject.toml)
- **[V]** API: `from fsrs import Scheduler, Card, Rating, ReviewLog`; `Scheduler(parameters=<21 weights>, desired_retention=0.9, learning_steps=(1 min, 10 min), relearning_steps=(10 min,), maximum_interval=36500, enable_fuzzing=True)`; `Card()` is due immediately; `Rating.Again=1, Hard=2, Good=3, Easy=4`; `card, review_log = scheduler.review_card(card, rating)`; `scheduler.get_card_retrievability(card)`; `to_json()/from_json()` on Scheduler, Card, ReviewLog; datetimes must be UTC; `Optimizer(review_logs).compute_optimal_parameters()`, `.compute_optimal_retention(parameters)`; `scheduler.reschedule_card(card, review_logs)`; setting `learning_steps=()` disables intra-day learning steps — [py-fsrs README](https://github.com/open-spaced-repetition/py-fsrs)
- **[V]** Implementation constants: `STABILITY_MIN = 0.001`, difficulty clamped to [1.0, 10.0], intervals rounded and floored at 1 day; retrievability uses whole elapsed days — [py-fsrs scheduler.py](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py)

**Minimal pure-Python SM-2 (derived from the verified SuperMemo spec):**
```python
import math
def sm2(q: int, reps: int, interval: int, ef: float) -> tuple[int, int, float]:
    """q in 0..5. Returns (reps, interval_days, ef)."""
    if q < 3:
        return 0, 1, ef                     # restart, EF unchanged
    ef = max(1.3, ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    reps += 1
    interval = 1 if reps == 1 else 6 if reps == 2 else math.ceil(interval * ef)
    return reps, interval, ef
```
(Note: the original spec updates EF only on the success path after "restart without changing EF"; many implementations also apply the EF formula on failure — a choice to document.)

### Inferences
- For MFDP, `pip install fsrs` adds one tiny dependency; alternatively the ~60 lines of FSRS-6 math can be vendored (MIT) to avoid a dependency and to control rounding/fuzzing. Set `learning_steps=()` and `relearning_steps=()` because minute-level steps are meaningless for chapter reviews; set `enable_fuzzing=False` for predictable calendar planning.
- Store `Card.to_json()` in SQLite or (better) store S, D, last_review explicitly in columns for querying.

### Gaps
- License file text itself not fetched (classifier says MIT).

---

## 4. Adapting to topic-level review without flashcards

### Takeaway
There's no validated way to turn a reading/review session into an FSRS grade; the most defensible signal is an explicit post-*tekrar* self-test rating ("how much could I recall/solve without notes?") mapped to Again/Hard/Good/Easy, not the 1–5 focus rating. Exam deadlines are best handled by anchoring: plan gaps so the last review falls shortly before the exam, with gaps ≈ 10–20% (up to 20–40% for ~1 week) of the remaining time (Cepeda et al. 2008). Self-ratings are biased (item JOL overconfidence, stability bias), so the app should use delayed, retrieval-based ratings and conservative retention targets.

### Cited Findings
- **[V] Cepeda, Vul, Rohrer, Wixted, Pashler (2008), *Psychological Science* 19(11):1095–1102:** >1,350 participants; gaps up to 3.5 months; final test up to 1 year later. Inverted-U: increasing the study gap first increases then gradually decreases final performance; optimal gap grows with test delay but, as a proportion, declines from ~20–40% of a 1-week test delay to ~5–10% of a 1-year delay — [PubMed 19076480](https://pubmed.ncbi.nlm.nih.gov/19076480/); [author PDF](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf); eScholarship abstract phrases it as ~20% for delays of a few weeks falling to ~5% for one year — [eScholarship](https://escholarship.org/uc/item/0kp5q19x)
- **[V]** Too-short gaps hurt retention much more than too-long gaps (press summary) — [YFile, York University](https://yfile.news.yorku.ca/?p=9454)
- **[V] Stability bias (Kornell & Bjork 2009, JEP: General):** across 12 experiments, learners predicted little or no benefit from additional study trials despite large actual gains; Koriat et al. (2004) found nearly identical recall predictions for 10-minute vs 1-week retention despite large real differences — [Kornell & Bjork 2009 PDF](https://web.williams.edu/Psychology/Faculty/Kornell/Publications/Kornell.Bjork.2009.pdf)
- **[V] Overconfidence/underconfidence:** item-by-item JOLs tend to be overconfident; aggregate judgments reduce overconfidence; across repeated study-test cycles calibration shifts to underconfidence ("underconfidence-with-practice", Koriat, Sheffer & Ma'ayan 2002) — [Koriat et al. 2002 PDF](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2002-KorShefMaaJEPG.pdf); [Koriat & Bjork 2005 PDF](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2005-Koriat-Bjork-JEPLMC-KBA.pdf); foresight bias and cue-only delayed judgments reducing the effect — [Koriat, Ma'ayan, Sheffer & Bjork 2006](https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2006-Koriat-Maayan-Sheffer-Bjork.pdf)
- **[V] Ease-of-processing heuristic:** fluency inflates JOLs (Kornell, Rhodes, Castel & Tauber 2011) — [Psych Science 2011 PDF](https://castel.psych.ucla.edu/wp-content/uploads/sites/111/2016/11/The-Ease-of-Processing-Heuristic-and-the-Stability-Bias-Psych-Science-Kornell-Rhodes-Castel-Tauber-2011.pdf)
- **[R] Delayed-JOL effect** (Nelson & Dunlosky 1991): judgments made after a delay and with cue-only (attempting retrieval) are far more accurate than immediate ones. Not fetched this session.
- **Existing topic-level tools [V, vendor claims]:**
  - *Mind the Gap* (MIT, terminal app, v0.6.0, 2026-04): explicitly "not a flashcard app"; after each session user rates confidence 1–10, each level maps to a configurable interval (level 1 = 1 day … level 10 = 21 days); optional per-book `exam_date` shown as countdown (no evidence it alters scheduling) — [zff.dev/gadonias/mind-the-gap](https://zff.dev/gadonias/mind-the-gap)
  - *Study Schedule Generator*: exam dates + target hours; reviews at ~1, 3, 7 days after first study plus a final pass just before the exam — [jasperbernaers.com](https://jasperbernaers.com/study-schedule-generator/)
  - *Recallity*: exam-date mode compresses the SR schedule to fit the countdown — [Product Hunt](https://www.producthunt.com/p/recallity/recallity)
  - Spreadsheet planner that shortens intervals as exams approach — [infoinspired.com](https://infoinspired.com/excel-formula/excel-adaptive-study-planner-with-auto-reschedule/); community practice of per-chapter "cards" (keywords/summary on the back) — [Art of Memory forum](https://forum.artofmemory.com/t/spaced-repetition-system/28780)
- **[R] Leitner system** (Sebastian Leitner, *So lernt man lernen*, 1972): boxes with doubling review periods; a failed item drops to box 1. Maps naturally to coarse topic "levels". **[R]** RemNote integrates FSRS for its "Rems" (concept notes), i.e., note-level rather than strict flashcard-level SR. Neither fetched this session.

### Inferences
- **Grade mapping proposal (MFDP):**
  - Only `kind = 'tekrar'` (self-testing/review) sessions — and optionally `'soru'` sessions on that topic — update the memory state. `okuma` sessions are *encoding*, not retrieval; they should create/reset the topic card (first exposure) rather than count as a successful review. `uretim`/`diger` do not update state.
  - Ask a separate **recall rating** after a tekrar session, phrased behaviorally to fight overconfidence: "Without notes, how much of this topic could you reproduce/solve?" 1 = "almost nothing" → Again; 2 = "fragments, needed notes a lot" → Hard; 3 = "most, with effort" → Good; 4 = "fluently, all key results/derivations" → Easy. Do **not** use the 1–5 focus rating as the grade (it measures attention, not memory); use it only as a confidence weight or a filter (e.g., focus ≤ 2 → treat Easy as Good).
  - Prefer ratings made at the *start* of a tekrar session (try to recall before opening notes = delayed, cue-only JOL), which the literature says is better calibrated than end-of-session ratings after rereading (fluency inflation).
- **Exam anchoring:** let T = days until exam. Choose a target "last review" at exam − 1…2 days, and earlier reviews with gaps ≈ 0.1–0.2·(time remaining to exam) (≈0.2–0.4 when the exam is ≤ 1 week away). Equivalently with FSRS: schedule next review at min(I_FSRS(r_target, S), exam_date − 1 − (buffer)) and, if the predicted R at the exam date R(t_exam, S') < target (e.g., 0.85–0.9), insert an extra review. Because too-short gaps are worse than too-long ones, avoid collapsing all reviews into the last 2–3 days.
- Topic units should be small enough to self-test in one 25–50 min tekrar session (e.g., one chapter/subtopic leaf of the task tree), not a whole course.

### Gaps
- No peer-reviewed study found that validates SR at the "chapter/topic" granularity or that maps session-level self-ratings to FSRS grades.
- No published evaluation of the exam-date features in the listed apps.

---

## 5. Recommendation for MFDP

### Takeaway
Use a **hybrid**: FSRS-6 math with default parameters (vendored or via `py-fsrs`, learning steps and fuzzing off) as the per-topic memory model, wrapped by an **exam-anchored planner** that caps intervals so reviews land before exams and adds a final review 1–2 days before. Don't use plain SM-2 (no R estimate, deadline-blind, ease hell) and don't attempt parameter optimization (too little data). A simple expanding schedule (1-3-7-… days + final pass) is a fine fallback/MVP and is what several existing topic tools do.

### Cited Findings
- FSRS outperforms SM-2 variants for ~90–98% of users and provides R(t,S) — [Anki forum](https://forums.ankiweb.net/t/fsrs-vs-sm2-in-2-seperate-profiles/52171); [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark)
- py-fsrs is MIT, offline, one dependency — [pyproject.toml](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/pyproject.toml)
- Optimal gap is a fraction of the retention interval, shrinking proportionally for longer delays — [Cepeda et al. 2008](https://pubmed.ncbi.nlm.nih.gov/19076480/)
- 1/3/7 + pre-exam pass used by Study Schedule Generator — [jasperbernaers.com](https://jasperbernaers.com/study-schedule-generator/)

### Inferences

**Why not pure SM-2:** fixed 1→6 day start, no deadline awareness, no "how much do I remember now?" estimate for the calendar/stats UI, and resets to 1 day on failure. **Why not tuned FSRS:** a single student will produce maybe 100–500 topic reviews per term; the optimizer needs far more. **Why FSRS defaults + exam cap:** gives a sensible stability growth + a retrievability number for prioritization ("weakest topics for exam X"), while the exam cap guarantees the hard deadline is respected. Use desired retention 0.90 (with default decay 0.1542 intervals expand very fast at lower retention; see §2 computed table), and `maximum_interval` ≈ days until the end of the semester.

**Data model sketch (SQLite, new tables; links to existing tasks/calendar):**
```sql
-- One memory card per reviewable topic (usually a leaf task under a course)
CREATE TABLE review_topics (
    id               INTEGER PRIMARY KEY,
    task_id          INTEGER NOT NULL UNIQUE REFERENCES tasks(id),
    tag              TEXT,                 -- course tag, for exam lookup
    state            TEXT NOT NULL DEFAULT 'new',  -- new|review|suspended
    stability        REAL,                 -- days (FSRS S)
    difficulty       REAL,                 -- 1..10 (FSRS D)
    last_review      TEXT,                 -- ISO UTC
    due              TEXT,                 -- ISO date (after exam cap)
    fsrs_due         TEXT,                 -- uncapped FSRS due, for analysis
    reps             INTEGER DEFAULT 0,
    lapses           INTEGER DEFAULT 0,
    algo_version     TEXT DEFAULT 'fsrs-6-default'
);

-- Immutable log; enables later re-fitting / switching algorithms
CREATE TABLE review_log (
    id               INTEGER PRIMARY KEY,
    topic_id         INTEGER NOT NULL REFERENCES review_topics(id),
    session_id       INTEGER REFERENCES sessions(id),   -- the tekrar session
    reviewed_at      TEXT NOT NULL,        -- ISO UTC
    rating           INTEGER NOT NULL,     -- 1 Again..4 Easy (recall self-rating)
    rating_timing    TEXT,                 -- 'pre' (before notes) | 'post'
    focus_rating     INTEGER,              -- copied 1..5 for context
    elapsed_days     REAL,
    r_before         REAL,                 -- predicted R at review time
    s_before REAL, d_before REAL, s_after REAL, d_after REAL
);

-- Many-to-many: which exam covers which topic (defaults: all topics under the exam's course tag)
CREATE TABLE exam_topics (
    event_id INTEGER NOT NULL,   -- calendar event with kind='sinav'
    topic_id INTEGER NOT NULL REFERENCES review_topics(id),
    PRIMARY KEY (event_id, topic_id)
);
```

**Pseudo-code:**
```python
DESIRED_R = 0.90
EXAM_TARGET_R = 0.90          # predicted R we want on exam morning
FINAL_GAP_DAYS = 1            # last review = exam - 1 day

def on_session_finished(session):
    topic = topic_for_task(session.task_id)
    if session.kind == "okuma" and topic.state == "new":
        init_card(topic, rating=GOOD_OR_ASK)          # first exposure = encoding
    elif session.kind in ("tekrar", "soru"):
        g = ask_recall_rating()                       # 1..4, prefer asked before notes
        if session.focus_rating and session.focus_rating <= 2 and g == 4:
            g = 3                                     # distrust 'Easy' when unfocused
        update_fsrs(topic, g, now_utc())              # D, S via FSRS-6 formulas
        topic.fsrs_due = topic.last_review + I(DESIRED_R, topic.stability)
        topic.due = exam_cap(topic)
    log(...)

def exam_cap(topic):
    exam = next_exam_covering(topic)                  # kind='sinav', date > today
    due = topic.fsrs_due
    if exam is None:
        return due
    days_left = (exam.date - today()).days
    final_slot = exam.date - FINAL_GAP_DAYS
    # Cepeda-style gap: ~10-20% of remaining time (20-40% if <= 7 days)
    frac = 0.3 if days_left <= 7 else 0.15
    gap_cap = max(1, round(frac * days_left))
    due = min(due, today() + gap_cap, final_slot)
    # If even the final slot would leave R(exam) below target, keep it at final_slot;
    # if FSRS predicts R(exam) >= target without another review, allow due > exam (skip).
    if R(days_between(topic.last_review, exam.date), topic.stability) >= EXAM_TARGET_R \
       and topic.fsrs_due > exam.date:
        return topic.fsrs_due
    return due

def todays_queue():
    # Overdue first, then by exam proximity, then by lowest current R
    return sorted(due_topics(today()),
                  key=lambda t: (days_to_exam(t), R_now(t)))
```

**MVP fallback (no FSRS):** for each topic, when first studied, schedule reviews at +1, +3, +7, +14 days, truncated so nothing falls after exam−1, and always add exam−1 (or exam−2) as the final pass; on a recall rating of 1 ("almost nothing") restart the ladder. This is essentially the Leitner/1-3-7 approach used by existing planners and can later be replaced by FSRS using the same `review_log`.

**UI implications:** calendar shows due topic reviews per day; stats show per-course "predicted R on exam day" (mean of R(t_exam, S) over exam topics) as a readiness indicator — clearly labelled as an estimate based on self-ratings.

### Gaps
- The fractions (0.15 / 0.3) and the "focus ≤ 2 → downgrade Easy" rule are heuristics derived from the cited literature, not validated parameters; they should be logged and revisited with the student's own data.

---

## Türkçe özet

- **SM-2** (Wozniak, 1987/1990): EF 2,5'ten başlar, aralıklar 1 → 6 → I·EF gün, EF tabanı 1,3, not < 3 ise tekrar 1 güne döner. Basit ama unutma eğrisi, hedef hatırlama oranı ve sınav tarihi kavramı yok; Anki'deki sürümünde "ease hell" sorunu var.
- **FSRS** (Jarrett Ye, open-spaced-repetition): her konu için Zorluk (D), Kararlılık (S) ve Hatırlanabilirlik (R) tutar. R(t,S) = (1 + factor·t/S)^(−w20). Bir sonraki tekrar, tahmini R'nin hedef değere (varsayılan 0,90) düştüğü güne konur. Güncel sürüm FSRS-6 (21 parametre). Anki'de 23.10'dan beri var, FSRS-6 Anki 25.07 ile geldi.
- **Kanıt:** srs-benchmark'ta (~10 bin Anki kullanıcısı, ~350 milyon değerlendirilmiş tekrar) FSRS-6'nın log loss değeri 0,346. Forum raporlarına göre FSRS, kullanıcıların %90–98'inde SM-2 türevlerinden daha iyi sonuç veriyor. Ancak bu sonuçlar flashcard verisinden geliyor, konu/bölüm düzeyinde doğrulanmış değil.
- **py-fsrs** (v6.3.2, MIT lisanslı, Python ≥ 3.10, tek bağımlılık typing-extensions) internet olmadan çalışır ve MFDP'ye kolayca eklenebilir. learning_steps=() ve enable_fuzzing=False ayarlanmalı.
- **Not eşlemesi:** Not, odak puanından (1–5) alınmamalı. Yalnızca 'tekrar' (ve isteğe bağlı 'soru') oturumlarından sonra ayrı bir **hatırlama puanı** sorulmalı: "Notlara bakmadan ne kadarını çıkarabildin?" 1–4 → Again/Hard/Good/Easy. Puan tercihen oturumun başında, notlar açılmadan alınmalı, çünkü anlık öz-değerlendirmeler aşırı iyimser oluyor (Koriat, Kornell & Bjork).
- **Sınav tarihi:** Cepeda vd. (2008) bulgusuna göre en iyi aralık, sınava kalan sürenin yaklaşık %10–20'si (1 haftalık süre için %20–40). Son tekrar sınavdan 1–2 gün önceye konmalı. Aralığın çok kısa olması, çok uzun olmasından daha zararlı.
- **Öneri:** Varsayılan parametreli FSRS-6 + sınava bağlı üst sınır (hibrit). Parametre optimizasyonu yapılmamalı, tek öğrencinin verisi bunun için yetmez. Başlangıç (MVP) için 1-3-7-14 gün + sınavdan önceki gün final tekrarı yeterli. Aynı `review_log` tablosuyla ileride FSRS'ye geçilebilir.
- **Veri modeli:** `review_topics` (task_id, S, D, last_review, due, fsrs_due), `review_log` (rating, focus_rating, r_before, s/d önce-sonra) ve `exam_topics` (sınav ↔ konu).

---

## References

1. Wozniak, P. — SuperMemo SM-2 algorithm description. https://super-memory.com/english/ol/sm2.htm
2. Anki Manual/FAQ — What spaced repetition algorithm does Anki use? https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm
3. open-spaced-repetition — The Algorithm (awesome-fsrs wiki; moved from fsrs4anki wiki, last edited 2026). https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm
4. Old location (redirect notice): https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm
5. ABC of FSRS (wiki; not fetched). https://github.com/open-spaced-repetition/fsrs4anki/wiki/abc-of-fsrs
6. open-spaced-repetition — srs-benchmark. https://github.com/open-spaced-repetition/srs-benchmark
7. py-fsrs README. https://github.com/open-spaced-repetition/py-fsrs
8. py-fsrs scheduler source. https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/fsrs/scheduler.py
9. py-fsrs pyproject.toml. https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/pyproject.toml
10. Ye, J., Su, J., Cao, Y. (2022). A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling. KDD '22, 4381–4390. https://scholar.hit.edu.cn/en/publications/a-stochastic-shortest-path-algorithm-for-optimizing-spaced-repeti/ ; https://dblp1.uni-trier.de/rec/conf/kdd/YeSC22.html
11. Su, J., Ye, J., Nie, L., Cao, Y., Chen, Y. (2023). Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory. IEEE TKDE 35(10), 10085–10097. https://scholar.hit.edu.cn/en/publications/optimizing-spaced-repetition-schedule-by-capturing-the-dynamics-o/
12. SSP-MMC-Plus project page. https://science.ecosyste.ms/projects/15317
13. Anki forum — FSRS vs SM2 in 2 separate profiles. https://forums.ankiweb.net/t/fsrs-vs-sm2-in-2-seperate-profiles/52171
14. Anki forum — New FSRS 6 parameters not appearing after reoptimizing. https://forums.ankiweb.net/t/bug-new-fsrs-6-parameters-not-appearing-after-reoptimizing/64921
15. AnkiDroid 2.23.0 release notes (Anki 25.07 / FSRS-6). https://www.apkmirror.com/apk/ankidroid-open-source-team/ankidroid-flashcards/ankidroid-flashcards-2-23-0-release/
16. Anki releases. https://github.com/ankitects/anki/releases
17. diane.app — FSRS vs SM-2 (commercial blog, May 2026; "ease hell"; unverified numbers). https://www.diane.app/en/guides/fsrs-vs-sm2
18. Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. Psychological Science 19(11), 1095–1102. https://pubmed.ncbi.nlm.nih.gov/19076480/ ; PDF: https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf ; https://escholarship.org/uc/item/0kp5q19x
19. York University YFile press summary of Cepeda et al. https://yfile.news.yorku.ca/?p=9454
20. Kornell, N., Bjork, R. A. (2009). A stability bias in human memory. JEP: General. https://web.williams.edu/Psychology/Faculty/Kornell/Publications/Kornell.Bjork.2009.pdf
21. Kornell, N., Rhodes, M. G., Castel, A. D., Tauber, S. K. (2011). The ease-of-processing heuristic and the stability bias. Psychological Science. https://castel.psych.ucla.edu/wp-content/uploads/sites/111/2016/11/The-Ease-of-Processing-Heuristic-and-the-Stability-Bias-Psych-Science-Kornell-Rhodes-Castel-Tauber-2011.pdf
22. Koriat, A., Sheffer, L., Ma'ayan, H. (2002). Comparing objective and subjective learning curves. JEP: General. https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2002-KorShefMaaJEPG.pdf
23. Koriat, A., Bjork, R. A. (2005). Illusions of competence in monitoring one's knowledge during study. JEP: LMC. https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2005-Koriat-Bjork-JEPLMC-KBA.pdf
24. Koriat, A., Ma'ayan, H., Sheffer, L., Bjork, R. A. (2006). https://newiipdm.haifa.ac.il/wp-content/uploads/2015/05/2006-Koriat-Maayan-Sheffer-Bjork.pdf
25. Mind the Gap (topic-level SR CLI, MIT). https://zff.dev/gadonias/mind-the-gap
26. Study Schedule Generator. https://jasperbernaers.com/study-schedule-generator/
27. Recallity. https://www.producthunt.com/p/recallity/recallity
28. Excel adaptive study planner. https://infoinspired.com/excel-formula/excel-adaptive-study-planner-with-auto-reschedule/
29. Art of Memory forum — Spaced repetition system (chapter-level review). https://forum.artofmemory.com/t/spaced-repetition-system/28780
30. [R, not fetched] Nelson, T. O., Dunlosky, J. (1991). When people's judgments of learning (JOLs) are extremely accurate at predicting subsequent recall: The "delayed-JOL effect". Psychological Science 2(4), 267–270.
31. [R, not fetched] Leitner, S. (1972). So lernt man lernen. Herder.
