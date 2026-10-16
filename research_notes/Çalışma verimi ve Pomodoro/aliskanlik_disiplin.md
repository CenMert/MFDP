# Habit formation, self-discipline and self-monitoring for study/work routines and productivity apps (MFDP)

Notes are in English for the report writer; the final report is in Turkish. Each section ends with "MFDP feature" ideas tied to the cited evidence. Evidence-strength labels: [META] = meta-analysis, [RRR] = multi-lab registered replication, [RCT/FIELD] = randomized or field experiment, [SINGLE] = single study or small sample, [QUAL] = qualitative/HCI interview study.

## 1. Habit formation: how long it takes, context cues, automaticity, missed days

### Takeaway
Habits form gradually as an asymptotic curve of automaticity. In the one well-known field study, the median time to plateau was ~66 days, with a very wide range (18–254 days). Repeating the behaviour in a stable context (same time, place or preceding action) is what builds the cue-response link. Missing a single occasion did not materially hurt habit formation, but chronic inconsistency did. Habitual behaviour then runs on context cues more than on goals or willpower.

### Cited Findings
- Lally, van Jaarsveld, Potts & Wardle (2010), *European Journal of Social Psychology* 40, 998–1009, DOI 10.1002/ejsp.674. 96 volunteers each picked one daily health behaviour (eating, drinking or exercise) tied to a daily cue and self-reported automaticity for 84 days (12 weeks). 82 provided usable data. [SINGLE, small sample] — [Behavioral Scientist summary](https://www.thebehavioralscientist.com/articles/how-long-to-form-a-habit); [UCL news 2009](https://www.ucl.ac.uk/news/2009/aug/how-long-does-it-take-form-habit)
- Median time to reach 95% of the modelled automaticity plateau was 66 days, but only among participants whose data fitted the model well. The range was 18–254 days. Estimates beyond 84 days are extrapolations from the curve. — [Behavioral Scientist](https://www.thebehavioralscientist.com/articles/how-long-to-form-a-habit); [James Clear summary](https://jamesclear.com/new-habit)
- Abstract: "Missing one opportunity to perform the behaviour did not materially affect the habit formation process." Lally also noted that very inconsistent performers did not form habits, and that the level of consistency needed is unknown. — [UCL news](https://www.ucl.ac.uk/news/2009/aug/how-long-does-it-take-form-habit); summarized in [search of abstract / PCI RR preprint](https://rr.peercommunityin.org/download/t_recommendations.reply_pdf.8382af6b73bdd0f7.6d616e757363726970745f7072657072696e742e706466.pdf)
- Replication caveat: a later multi-centre registered-report preprint says the model-fitted subsample was small (39 participants) and that the study "has not been replicated yet". Automaticity was entirely self-reported. — [PCI Registered Reports preprint](https://rr.peercommunityin.org/download/t_recommendations.reply_pdf.8382af6b73bdd0f7.6d616e757363726970745f7072657072696e742e706466.pdf); [BPS Research Digest](https://bps.org.uk/research-digest/how-form-habit)
- Wood & Neal (2007), "A new look at habits and the habit–goal interface," *Psychological Review* 114(4), 843–863. Habits come from gradually learned associations between responses and context features (physical settings, preceding actions) that have repeatedly co-occurred with them. Once formed, perceiving the context triggers the response without a mediating goal. Goals act indirectly: they motivate the repetition and the exposure to cues. The paper's habit-change implications centre on regulating exposure to cues. [THEORY/REVIEW] — [Wood & Neal 2007 PDF](https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf)
- Wood, Tam & Guerrero Witt (2005), "Changing circumstances, disrupting habits," *JPSP* 88, 918–933. This session found only the citation, not its findings. Its premise is that a change of context (e.g., a life transition) disrupts habits. — [citation in BBS reference list](https://resolve.cambridge.org/core/journals/behavioral-and-brain-sciences/article/linking-addictions-to-everyday-habits-and-plans/A5304339C20E117B5CA8C7E708E9B3DD)

### Inferences
- "21 days" is folklore. Users should expect roughly 2–3 months for a study routine to feel automatic, longer for complex behaviours. Deep work is far more complex than "drink water at lunch", so the 66-day figure is probably a lower bound for it.
- MFDP feature: a **"habit anchor"** field on recurring sessions ("after morning coffee, at my desk → 2 pomodoros on Task X"). The app could show **consistency of start time and place** (e.g., "80% of your sessions started 09:00–09:30") as the key habit metric, rather than raw minutes.
- MFDP feature: an **automaticity curve** in the stats window, i.e. a rolling 7-day rate of performing the routine. Present the 66-day median and its 18–254 range as an honest expectation, not a promise.
- MFDP feature: **miss-tolerant consistency**. Use "never miss twice" or "X of the last 7 days" rather than a hard daily streak, because the evidence says single misses are harmless and chronic inconsistency is the real problem.
- MFDP feature: because context drives habits, the app can record the **active-window / location context at session start**. The existing `system_monitor` and `AtomicAnalyzer` are a natural fit. It can also warn when the context changes (new semester, travel), since that is when habits are most fragile (Wood et al. 2005 premise).

### Gaps
- No independent large replication of Lally et al. was found. The PCI multi-centre replication was a preprint and its results were not retrieved.
- No study was found that specifically measures habit formation time for *study/knowledge-work* routines.

## 2. Implementation intentions (if-then plans) and mental contrasting (WOOP/MCII)

### Takeaway
If-then plans ("If it is 9:00 and I sit at my desk, then I start a 25-min pomodoro on chapter 3") have one of the more robust medium-to-large effects in the behaviour-change literature (d ≈ 0.65 across 94 tests). Adding mental contrasting (WOOP/MCII) gives a smaller but still significant effect (g ≈ 0.34), and that estimate may be inflated by publication bias.

### Cited Findings
- Gollwitzer & Sheeran (2006), "Implementation intentions and goal achievement: A meta-analysis of effects and processes," *Advances in Experimental Social Psychology* 38, 69–119, DOI 10.1016/S0065-2601(06)38002-1. The effect on goal attainment was d = 0.65 across 94 independent tests, described by the authors as "medium-to-large". [META] — [KOPS Konstanz record](https://kops.uni-konstanz.de/entities/publication/2e749bfb-8533-437c-8203-7e788c910c5f); [Frontiers 2021 citing d = 0.65, 95% CI 0.6–0.7](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.565202/full)
- A 2024 follow-up by Sheeran, Listrom & Gollwitzer analysed 642 independent tests and built a taxonomy of the cues and responses used in if-then plans. — [goalsandprogress summary, secondary](https://goalsandprogress.com/implementation-intentions-research/)
- Wang, Wang & Gai (2021), "A meta-analysis of the effects of mental contrasting with implementation intentions on goal attainment," *Frontiers in Psychology* 12:565202. 21 studies, 24 effect sizes, N = 15,907. MCII had a small-to-medium effect, g = 0.336. The effect was larger when the participant interacted with an experimenter (g = 0.465) than with a document/self-guided format (g = 0.277). The authors flag publication bias, so the true effect may be smaller. [META] — [PMC8149892](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8149892/)
- Cross & Sheffield (2019), *Health Psychology Review*, a meta-analysis of mental contrasting for health behaviour. Its MCII subset (k = 7) gave g = 0.28 [0.14, 0.42]. Adding if-then plans did not significantly increase the effect of mental contrasting alone. [META] — [PubMed 30879403](https://pubmed.ncbi.nlm.nih.gov/30879403/)

### Inferences
- If-then planning has the best effect-to-cost ratio for an app: it is cheap to implement, and the evidence is strong.
- MFDP feature: an **"If-Then" planner** attached to tasks. When planning a task (`recursive_task_manager`), prompt: *When/where* (time + place/app context) → *then* (first concrete action + pomodoro count). Fire a reminder or notification at the cue time. Optionally export to a calendar (.ics).
- MFDP feature: an **obstacle plan** ("If I get the urge to open YouTube, then I write it on the distraction list and keep going"). This could link to the existing interruption logging in `AtomicAnalyzer`, so the app can show how often the planned response was used.
- MFDP feature: a lightweight **WOOP wizard** at the start of the week (Wish, Outcome, Obstacle, Plan; four short text fields). Self-guided formats show the smaller effect (g ≈ 0.28), so keep it short and interactive (e.g., a guided dialog rather than a static form).

### Gaps
- No WOOP-branded meta-analysis was found, only MCII meta-analyses.
- Few if-then studies are on knowledge-work or study productivity specifically; most are health behaviours.
- The participant count of Gollwitzer & Sheeran (often cited as ~8,000) was not verified.

## 3. Goal-setting theory (Locke & Latham)

### Takeaway
Specific, challenging goals outperform "do your best" goals, provided there is commitment, feedback and enough ability. For complex or new tasks, learning goals and proximal sub-goals tend to beat a single distal performance goal.

### Cited Findings
- Locke & Latham (2002), "Building a practically useful theory of goal setting and task motivation: A 35-year odyssey," *American Psychologist* 57(9), 705–717. The paper summarizes 35 years of research. Specific, difficult goals raise performance through four mechanisms: directing attention, energizing effort, persistence, and strategy discovery. Moderators are goal commitment, feedback, task complexity and ability. Goals also mediate the effects of incentives. [NARRATIVE REVIEW of a large literature] — [PDF (UBalt)](https://home.ubalt.edu/tmitch/642/articles%20syllabus/locke%20pract%20goal%20setting%202002%20am%20psy.pdf); [UMN copy](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf)
- The same paper discusses learning goals (e.g., "discover N strategies") versus performance goals on complex tasks, and proximal goals as feedback-generating milestones that help with distal goals. This comes from my knowledge of the paper and was not re-verified line by line this session. The search snippets did not show those sections. — [PDF](https://home.ubalt.edu/tmitch/642/articles%20syllabus/locke%20pract%20goal%20setting%202002%20am%20psy.pdf)

### Inferences
- MFDP feature: replace vague "study today" with **specific daily/weekly targets** (e.g., "6 pomodoros on Thesis ch.3 this week"). The existing `planned_duration_minutes` on `Task` is a ready hook. Show progress against it.
- MFDP feature: **auto-break distal goals into proximal ones**. A parent task's goal is split into weekly or daily sub-targets, and the recursive task tree already supports this structure.
- MFDP feature: **two goal types**. "Output" goals for routine work, and "learning" goals for new or complex material ("understand X, write 3 questions"), so the user is not punished by numeric targets while still learning a topic.
- Calibrate difficulty: suggest next week's target from the user's recent median (e.g., +10%) instead of an arbitrary number, so goals stay challenging but attainable.

### Gaps
- The exact learning-goal and proximal-goal effect sizes (e.g., Seijts & Latham studies) were not retrieved.

## 4. Self-monitoring and self-tracking (incl. reactivity and the quantified-self/HCI literature)

### Takeaway
Monitoring progress toward a goal reliably improves goal attainment (d ≈ 0.40, 138 studies). The effect is larger when progress is physically recorded and when it is reported to others or made public. However, quantification can lower the enjoyment and intrinsic motivation of activities, and people routinely lapse and abandon trackers. Design for lapsing and for reflection, not just for data collection.

### Cited Findings
- Harkin, Webb, Chang, Prestwich, Conner, Kellar, Benn & Sheeran (2016), "Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence," *Psychological Bulletin* 142(2), 198–229. 138 RCTs, N = 19,951. Interventions increased monitoring frequency (d+ = 1.98 [1.71, 2.24]) and goal attainment (d+ = 0.40 [0.32, 0.48]). Monitoring frequency mediated the effect. Effects were larger when outcomes were reported to others or made public, and when information was physically recorded. Most studies concerned health goals. [META] — [White Rose eprint](https://eprints.whiterose.ac.uk/id/eprint/91437/); [APA press release](https://www.apa.org/news/press/releases/2015/10/progress-goals.aspx)
- Etkin (2016), "The hidden cost of personal quantification," *Journal of Consumer Research* 42(6), 967–984. Six experiments. Measuring an activity increased how much people did it but decreased their enjoyment of it, because attention to numbers made the activity feel like work and undermined intrinsic motivation. Measurement also reduced the likelihood of continuing the activity later (per the paper's abstract; secondary sources partially confirm). [MULTI-STUDY LAB] — [Wharton working paper PDF](https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/Etkin-Jordan-11-12-15-Hidden-Cost.pdf)
- Epstein, Ping, Fogarty & Munson (2015), "A lived informatics model of personal informatics," *UbiComp 2015*. Survey plus 22 interviews with trackers of activity, finances and location. Tracking is embedded in everyday life with varied goals (not only behaviour change). The model covers deciding, selecting a tool, collection, integration, reflection, and **lapsing and resuming**. [QUAL/HCI] — [PDF](https://my.eng.utah.edu/~cs5540/au16/readings/PersonalInformatics-Epstein2015.pdf); [Self-research library](https://library.selfresearch.org/research/a-lived-informatics-model-of-personal-informatics/)
- Epstein et al. (2016), "Beyond abandonment to next steps: Understanding and designing for life after personal informatics tool use," *CHI 2016*. Survey of 193 people plus 12 interviews. It identifies six reasons people stop tracking and five perspectives on life after tracking. People may temporarily lapse or stop for good. [QUAL/HCI] — [Self-research library](https://library.selfresearch.org/research/beyond-abandonment-to-next-steps-understanding-and-designing-for-life-after-personal-informatics-tool-use/)

### Inferences
- Tracking is MFDP's core, and it is evidence-backed, but its value comes from **monitoring progress toward a goal**, not from logging alone. Always show tracked time *relative to a target*.
- MFDP feature: **explicit "record" acts**, such as a 1-click end-of-session note or a rating (focus 1–5, what got done). Physical or active recording was a moderator in Harkin et al.
- MFDP feature: an optional **accountability share**, e.g., exporting a weekly summary to a friend or study partner. "Made public" boosted effects, but keep it opt-in.
- MFDP feature, following Etkin: let users **hide numbers during the session** (minimal timer, no live counters) and show numbers only at review time. Avoid quantifying activities the user does for enjoyment.
- MFDP feature, following Epstein: **design for lapses**. Use a "welcome back" flow after N days without sessions (no guilt, a quick re-plan), allow pausing tracking without losing history, and offer a "light mode" (track only start/stop) for low-motivation periods.

### Gaps
- No meta-analysis specifically on productivity/time-tracking apps (e.g., Pomodoro apps) and objective work output was found.
- Etkin's continuation-intention result was taken from the abstract-level summary, not checked in the full text.

## 5. Self-control, procrastination, precommitment, temptation bundling, ego depletion

### Takeaway
Procrastination is best predicted by task aversiveness, low self-efficacy, impulsiveness/distractibility and the delay before rewards, consistent with temporal motivation theory. People who are good at self-control seem to rely less on effortful resistance and more on **habits and avoiding temptation conflicts**. The "willpower is a depletable resource" (ego depletion) idea failed a large multi-lab replication, so apps should not be built around "save your willpower". Temptation bundling and small rewards for returning after a miss show measurable but often short-lived effects.

### Cited Findings
- Steel (2007), "The nature of procrastination: A meta-analytic and theoretical review of quintessential self-regulatory failure," *Psychological Bulletin* 133(1), 65–94. Based on 691 correlations. Strong, consistent predictors are task aversiveness, task delay, self-efficacy, impulsiveness, and conscientiousness with its facets (self-control, distractibility, organization, achievement motivation). Neuroticism, rebelliousness and sensation seeking were weak. Findings fit temporal motivation theory, a hybrid of expectancy theory and hyperbolic discounting: Motivation = (Expectancy × Value) / (1 + Impulsiveness × Delay). [META] — [U Calgary PRISM](https://prism.ucalgary.ca/items/d0dea740-4751-4e9a-84da-2d8ad446830d/full); [Stafforini](https://stafforini.com/works/steel-2007-nature-procrastination-metaanalytic/)
- Galla & Duckworth (2015), "More than resisting temptation: Beneficial habits mediate the relationship between self-control and positive life outcomes," *JPSP* 109(3), 508–525, DOI 10.1037/pspp0000026. Six studies, total N = 2,274. People higher in self-control had stronger beneficial habits, and habits mediated the link to outcomes. Study habits were linked to less motivational interference after study–leisure conflicts. In high school seniors, study habits mediated self-control's effect on homework completion, GPA and first-year college persistence. [MULTI-STUDY, correlational/longitudinal] — [PMC4731333](https://pmc.ncbi.nlm.nih.gov/articles/PMC4731333)
- Hofmann, Baumeister, Förster & Vohs (2012), "Everyday temptations: An experience sampling study of desire, conflict, and self-control," *JPSP* 102(6), 1318–1335, DOI 10.1037/a0026545. 205 adults, 7,827 desire episodes. Desires are frequent and mostly unproblematic. As cited by Galla & Duckworth, individuals with higher trait self-control reported fewer attempts to inhibit temptations. The common "they experience fewer temptations" framing comes from the companion literature (Hofmann et al.; de Ridder et al.) and was not verified verbatim here. [ESM] — [UMN record](https://experts.umn.edu/en/publications/everyday-temptations-an-experience-sampling-study-of-desire-confl/); [PDF](https://carlsonschool-d8.prd.umn.edu/sites/carlsonschool.umn.edu/files/2019-04/hofmann_baumeister_forster_vohs_2012_jpsp.pdf); [Galla & Duckworth intro](https://pmc.ncbi.nlm.nih.gov/articles/PMC4731333)
- de Ridder et al. (2012), a meta-analysis of over 100 studies, as reported in Galla & Duckworth. Trait self-control predicted desirable *automatic* behaviours (r = .36) more strongly than desirable *controlled* behaviours (r = .15). [META, secondary citation] — [PMC4731333](https://pmc.ncbi.nlm.nih.gov/articles/PMC4731333)
- Hagger, Chatzisarantis et al. (2016), "A multilab preregistered replication of the ego-depletion effect," *Perspectives on Psychological Science* 11(4), 546–573. 23 labs, N = 2,141, sequential-task paradigm. The pooled effect was d = 0.04, 95% CI [−0.07, 0.15], so the CI includes zero. Baumeister & Vohs disputed the manipulation. Later commentators argue the evidence neither proves nor disproves ego depletion. [RRR] — [Tilburg record](https://research.tilburguniversity.edu/en/publications/a-multi-lab-pre-registered-replication-of-the-ego-depletion-effec/); [Frontiers commentary](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2016.00621/pdf); [PMC8134656 opinion](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8134656/)
- Milkman, Minson & Volpp (2014), "Holding the Hunger Games hostage at the gym: An evaluation of temptation bundling," *Management Science*. Field RCT at a university gym. Gym-only access to tempting audiobooks initially increased gym visits by 51% (full treatment) and 29% (encouragement only) versus control, but effects decayed over time, especially after Thanksgiving. 61% of participants later chose to pay for gym-only audiobook access, which signals demand for precommitment. [RCT/FIELD] — [Penn repository](https://repository.upenn.edu/oid_papers/150); [Wharton Knowledge](https://knowledge.wharton.upenn.edu/article/researchers-used-hunger-games-encourage-healthier-choices/)
- Milkman et al. (2021), "Megastudies improve the impact of applied behavioural science," *Nature* 600, 478–483. 61,000+ 24 Hour Fitness members tested 53–54 four-week digital programmes. 45% of interventions raised weekly visits by 9–27%. The best gave a small bonus for **returning after a missed workout**, raising visits by ~27%, versus ~9% for the base per-visit micro-incentive. Only ~8% of interventions had measurable effects after the four weeks ended. [MEGASTUDY RCT] — [Penn Today](https://penntoday.upenn.edu/news/wharton-study-best-ways-boost-workout-habits); [Scimex](https://www.scimex.org/newsfeed/which-programs-give-gym-goers-the-biggest-boost)
- Dai, Milkman & Riis (2014), "The fresh start effect: Temporal landmarks motivate aspirational behavior," *Management Science* 60(10), 2563–2582, DOI 10.1287/mnsc.2014.1901. Three archival field studies (Google "diet" searches, gym visits, commitment-contract creation). Aspirational behaviour rises after temporal landmarks such as a new week, month, semester or birthday. [ARCHIVAL FIELD] — [Wharton PDF](https://faculty.wharton.upenn.edu/wp-content/uploads/2014/06/Dai_Fresh_Start_2014_Mgmt_Sci.pdf)

### Inferences
- Map Steel's TMT terms to app levers:
  - *Expectancy*: show past success rates for similar tasks.
  - *Value*: link the task to the goal and why it matters.
  - *Delay*: create artificial near-term deadlines and proximal goals.
  - *Impulsiveness*: block or reduce distractions.
- MFDP feature, given task aversiveness: a **"just start 1 pomodoro / 5 minutes" button** for aversive tasks, plus a tag for tasks the user keeps postponing (detected from task age or repeated deferrals).
- MFDP feature (avoid rather than resist): **DND auto-on at session start** (MFDP already has KDE DND via D-Bus) and optional **distracting-app/site detection**. `system_monitor` could flag known distractor windows during a focus session. Frame this as "make the environment easy", not as willpower.
- MFDP feature (precommitment): allow scheduling sessions in advance ("committed blocks"), with an optional mild self-chosen consequence or a public pledge. Users show a revealed preference for such constraints (61% paid in Milkman 2014).
- MFDP feature (temptation bundling): let users attach a "reward" to focus sessions, e.g., a favourite playlist that only plays during pomodoros, or a guilty-pleasure activity unlocked after N pomodoros. Expect the effect to decay, so rotate the bundle.
- MFDP feature (megastudy result): a **"comeback bonus"**, i.e. explicit positive feedback or a celebratory badge for returning after a missed day. This was the single most effective element in the 24 Hour Fitness megastudy.
- MFDP feature (fresh start): offer re-planning prompts on Mondays, the 1st of the month and semester starts ("New week, fresh start; plan 3 key goals?").
- Do not build a "willpower meter" or messaging that says self-control runs out. The ego-depletion evidence is unreliable. Breaks (Pomodoro) are justified on other grounds such as fatigue and attention, not depletion.

### Gaps
- The precise result of the 2014 temptation-bundling follow-up (Kirgios et al. 2020, 24 Hour Fitness, ~10–14% weekly workout increase) was mentioned only by secondary sources and not verified.
- No evidence was retrieved on app-based distraction blocking for students' academic outcomes.

## 6. Gamification and streaks: benefits, the broken-streak penalty, overjustification, Goodhart's law

### Takeaway
Gamification has small positive average effects on learning outcomes (g ≈ 0.25–0.49), and the motivational and behavioural effects are less robust. Streaks motivate while intact, but a broken streak lowers subsequent engagement even when the break was not the person's fault, and the more salient the streak, the bigger the drop. Allowing "repair" softens this. Expected tangible rewards undermine intrinsic motivation. Metric-maximizing (Goodhart) is a real risk when pomodoro counts become the goal.

### Cited Findings
- Silverman & Barasch (2023), "On or off track: How (broken) streaks affect consumer decisions," *Journal of Consumer Research* 49(6), 1095–1117, DOI 10.1093/jcr/ucac029. Seven studies. Intact logged streaks increase later engagement compared with broken ones. Broken streaks reduce continuation **even when caused by external events**, and the effect holds regardless of streak length. The effect depends on how the *log* represents the behaviour, not on the actual past behaviour. It is amplified when people feel responsible for the break and **diminished when people can repair the streak**. Making streaks salient (tracking, framing) increases both the benefit and the harm. [MULTI-STUDY] — [UD repository](https://udspace.udel.edu/items/42ce576b-8e1f-429a-8541-e29e48dbcfbb/full); [CU Boulder summary](https://www.colorado.edu/business/faculty-research/2023/04/19/or-track-how-broken-streaks-affect-consumer-decisions); [Psychology Today](https://www.psychologytoday.com/us/blog/ulterior-motives/202306/how-broken-streaks-sap-motivation)
- Follow-up work by Silverman and colleagues (2024) shows that people come to care about the streak itself rather than the original goal, even for artificial streaks. — [UDaily 2024](https://udel.edu/udaily/2024/march/power-of-streaks-motivation-jackie-silverman); [INSEAD Knowledge](https://knowledge.insead.edu/marketing/consumer-streaks-are-motivating-the-key-is-keeping-them-alive-19011)
- "What-the-hell effect": originally a dieting/restraint concept (Polivy & Herman), where a lapse leads to abandoning restraint. No source in this session directly tested it for app streaks. The broken-streak demotivation findings are consistent with it but do not establish it. — [Psychology Today](https://www.psychologytoday.com/us/blog/ulterior-motives/202306/how-broken-streaks-sap-motivation) (gap noted)
- Sailer & Homner (2020), "The gamification of learning: A meta-analysis," *Educational Psychology Review* 32(1), 77–112, DOI 10.1007/s10648-019-09498-w. Small significant effects on cognitive (g = .49), motivational (g = .36) and behavioural (g = .25) learning outcomes. The cognitive effect was stable in high-rigour studies, but the motivational and behavioural effects were less stable. Game fiction, and combining competition with collaboration, moderated behavioural outcomes. [META] — [Springer](https://link.springer.com/article/10.1007/s10648-019-09498-w); [Augsburg OPUS](https://opus.bibliothek.uni-augsburg.de/opus4/frontdoor/index/index/docId/109056)
- Deci, Koestner & Ryan (1999), "A meta-analytic review of experiments examining the effects of extrinsic rewards on intrinsic motivation," *Psychological Bulletin* 125(6), 627–668. 128 experiments. Tangible expected rewards significantly undermined free-choice intrinsic motivation:
  - engagement-contingent d = −0.40
  - completion-contingent d = −0.36
  - performance-contingent d = −0.28

  Engagement- and completion-contingent rewards also lowered self-reported interest (d = −0.15, −0.17). Verbal rewards (positive feedback) tended to *enhance* intrinsic motivation; this is from the paper and not re-verified this session. This is contested by Cameron & Pierce, and the 2001 RER reply defends the undermining conclusion. [META] — [PDF](https://home.ubalt.edu/ntygmitc/642/Articles%20syllabus/Deci%20Koestner%20Ryan%20meta%20IM%20psy%20bull%2099.pdf); [Deci, Koestner & Ryan 2001 RER](https://journals.sagepub.com/doi/10.3102/00346543071001001)
- Etkin (2016) (see Section 4): quantification raises output but lowers enjoyment, which is an overjustification-like mechanism for metrics. — [Wharton PDF](https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/Etkin-Jordan-11-12-15-Hidden-Cost.pdf)
- Goodhart's law ("when a measure becomes a target, it ceases to be a good measure"): no empirical study specific to productivity apps was found this session. It is a conceptual risk, not a measured effect. (gap)

### Inferences
- Streaks are double-edged. Silverman & Barasch directly imply three design rules:
  - (a) Allow **streak repair or freeze**, e.g., one "rest day" token per week, or a make-up session the next day.
  - (b) Use **weekly or rolling consistency** ("5/7 days this week", "never miss twice") instead of an all-or-nothing daily streak.
  - (c) Frame breaks as external or neutral ("Life happens; streak paused") rather than blaming.
- MFDP feature: show a **"best 4-of-7-days" ring** or a heatmap calendar with intensity, not a single counter that resets to 0. Combine it with the **comeback bonus** from the Milkman megastudy.
- MFDP feature: prefer **informational feedback** (verbal, competence-affirming: "You focused 20% longer than your average on hard tasks") over points or badges for merely showing up. Avoid tangible-reward framing. If badges are used, tie them to mastery or milestones ("first 10-hour week on Thesis"), not engagement.
- Goodhart guardrails in MFDP:
  - Pair pomodoro count with an **outcome/quality field** (what was produced; focus rating).
  - Show **interruptions/focus shifts** from `AtomicAnalyzer` next to time, so inflating time with distracted sessions is visible.
  - Avoid leaderboards on raw minutes.
- Let advanced users switch gamification off entirely, since its motivational effects are small and unstable.

### Gaps
- No empirical test of the what-the-hell effect in streak-based productivity apps was found.
- No CHI paper specifically on streak design in focus/Pomodoro apps was retrieved. Duolingo-style streak-freeze evidence is industry blog material, not peer-reviewed, and was not collected.

## 7. Reflection: weekly reviews, journaling, planning fallacy and estimate-vs-actual calibration

### Takeaway
People systematically underestimate how long their own tasks will take (the planning fallacy). Forecasts improve when people explicitly connect predictions to past experience. In HCI models, reflection on tracked data is the stage that turns logging into behaviour change. A weekly review that compares estimated with actual pomodoros is directly supported by the planning-fallacy work.

### Cited Findings
- Buehler, Griffin & Ross (1994), "Exploring the 'planning fallacy': Why people underestimate their task completion times," *JPSP* 67(3), 366–381. People underestimate their own, but not others', completion times. Think-aloud protocols show forecasters focus on future scenarios and neglect past experience. The bias was eliminated when participants were instructed to connect past experiences to their forecasts. In the honours-thesis study (37 students), the mean best-guess prediction was 33.9 days versus 55.5 days actual, and only ~30% finished by their predicted date. The thesis figures come from secondary sources and should be verified against the original. [MULTI-STUDY] — [Buehler et al. 1994 PDF](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf); [Behavioral Scientist glossary](https://www.thebehavioralscientist.com/glossary/planning-fallacy)
- Epstein et al. (2015) lived informatics model: reflection is an integral stage interleaved with collection, and lapses in reflection or collection are normal. — [PDF](https://my.eng.utah.edu/~cs5540/au16/readings/PersonalInformatics-Epstein2015.pdf)
- Harkin et al. (2016): monitoring improves attainment mainly by increasing the frequency of progress checks (mediation). This supports a regular review cadence. — [White Rose](https://eprints.whiterose.ac.uk/id/eprint/91437/)

### Inferences
- MFDP feature: **estimate-vs-actual**. At task creation, ask for estimated pomodoros (or use `planned_duration_minutes`). At completion, show actual time and the ratio. Over time, display a **personal calibration factor** ("your estimates are typically 1.6× too low; suggested estimate: 8 pomodoros").
- MFDP feature, applying the Buehler fix: when the user enters an estimate, show **similar past tasks and their actual durations** (same tag/parent). This is the "connect to past experience" manipulation that eliminated the bias.
- MFDP feature: a **weekly review screen** on Sundays/Mondays, using the fresh-start timing:
  - planned vs done
  - estimate accuracy
  - consistency heatmap
  - top interruptions (AtomicAnalyzer)
  - 3 short prompts: what worked, what got in the way, if-then plan for next week
- MFDP feature: a short **end-of-session journal** (1 line plus a focus rating). It provides the "physically recorded" moderator from Harkin and data for the weekly review.

### Gaps
- No controlled study was found specifically on weekly-review screens or journaling inside productivity apps improving output. The recommendation is an inference from monitoring and planning-fallacy research.
- No meta-analytic effect size for planning-fallacy debiasing interventions was retrieved.

---

### Reference list (all retrieved or verified via search this session unless noted)
1. Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W., & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. *European Journal of Social Psychology*, 40(6), 998–1009. https://doi.org/10.1002/ejsp.674
2. Wood, W., & Neal, D. T. (2007). A new look at habits and the habit–goal interface. *Psychological Review*, 114(4), 843–863. https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf
3. Wood, W., Tam, L., & Guerrero Witt, M. (2005). Changing circumstances, disrupting habits. *Journal of Personality and Social Psychology*, 88(6), 918–933. (Citation only; content not retrieved.)
4. Gollwitzer, P. M., & Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. *Advances in Experimental Social Psychology*, 38, 69–119. https://doi.org/10.1016/S0065-2601(06)38002-1
5. Wang, G., Wang, Y., & Gai, X. (2021). A meta-analysis of the effects of mental contrasting with implementation intentions on goal attainment. *Frontiers in Psychology*, 12, 565202. https://doi.org/10.3389/fpsyg.2021.565202
6. Cross, A., & Sheffield, D. (2019). Mental contrasting for health behaviour change: A systematic review and meta-analysis of effects and moderator variables. *Health Psychology Review*, 13(2), 209–225. https://pubmed.ncbi.nlm.nih.gov/30879403/
7. Locke, E. A., & Latham, G. P. (2002). Building a practically useful theory of goal setting and task motivation: A 35-year odyssey. *American Psychologist*, 57(9), 705–717. https://doi.org/10.1037/0003-066X.57.9.705
8. Harkin, B., Webb, T. L., Chang, B. P. I., Prestwich, A., Conner, M., Kellar, I., Benn, Y., & Sheeran, P. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence. *Psychological Bulletin*, 142(2), 198–229. https://doi.org/10.1037/bul0000025
9. Etkin, J. (2016). The hidden cost of personal quantification. *Journal of Consumer Research*, 42(6), 967–984. https://doi.org/10.1093/jcr/ucv095
10. Epstein, D. A., Ping, A., Fogarty, J., & Munson, S. A. (2015). A lived informatics model of personal informatics. *Proceedings of UbiComp 2015*, 731–742. https://doi.org/10.1145/2750858.2804250
11. Epstein, D. A., Caraway, M., Johnston, C., Ping, A., Fogarty, J., & Munson, S. A. (2016). Beyond abandonment to next steps: Understanding and designing for life after personal informatics tool use. *Proceedings of CHI 2016*, 1109–1113. https://doi.org/10.1145/2858036.2858045
12. Steel, P. (2007). The nature of procrastination: A meta-analytic and theoretical review of quintessential self-regulatory failure. *Psychological Bulletin*, 133(1), 65–94. https://doi.org/10.1037/0033-2909.133.1.65
13. Galla, B. M., & Duckworth, A. L. (2015). More than resisting temptation: Beneficial habits mediate the relationship between self-control and positive life outcomes. *Journal of Personality and Social Psychology*, 109(3), 508–525. https://doi.org/10.1037/pspp0000026
14. Hofmann, W., Baumeister, R. F., Förster, G., & Vohs, K. D. (2012). Everyday temptations: An experience sampling study of desire, conflict, and self-control. *Journal of Personality and Social Psychology*, 102(6), 1318–1335. https://doi.org/10.1037/a0026545
15. de Ridder, D. T. D., Lensvelt-Mulders, G., Finkenauer, C., Stok, F. M., & Baumeister, R. F. (2012). Taking stock of self-control: A meta-analysis of how trait self-control relates to a wide range of behaviors. *Personality and Social Psychology Review*, 16(1), 76–99. https://doi.org/10.1177/1088868311418749 (cited via Galla & Duckworth)
16. Hagger, M. S., Chatzisarantis, N. L. D., et al. (2016). A multilab preregistered replication of the ego-depletion effect. *Perspectives on Psychological Science*, 11(4), 546–573. https://doi.org/10.1177/1745691616652873
17. Milkman, K. L., Minson, J. A., & Volpp, K. G. M. (2014). Holding the Hunger Games hostage at the gym: An evaluation of temptation bundling. *Management Science*, 60(2), 283–299. https://doi.org/10.1287/mnsc.2013.1784
18. Milkman, K. L., et al. (2021). Megastudies improve the impact of applied behavioural science. *Nature*, 600, 478–483. https://doi.org/10.1038/s41586-021-04128-4
19. Dai, H., Milkman, K. L., & Riis, J. (2014). The fresh start effect: Temporal landmarks motivate aspirational behavior. *Management Science*, 60(10), 2563–2582. https://doi.org/10.1287/mnsc.2014.1901
20. Silverman, J., & Barasch, A. (2023). On or off track: How (broken) streaks affect consumer decisions. *Journal of Consumer Research*, 49(6), 1095–1117. https://doi.org/10.1093/jcr/ucac029
21. Sailer, M., & Homner, L. (2020). The gamification of learning: A meta-analysis. *Educational Psychology Review*, 32(1), 77–112. https://doi.org/10.1007/s10648-019-09498-w
22. Deci, E. L., Koestner, R., & Ryan, R. M. (1999). A meta-analytic review of experiments examining the effects of extrinsic rewards on intrinsic motivation. *Psychological Bulletin*, 125(6), 627–668. https://doi.org/10.1037/0033-2909.125.6.627
23. Deci, E. L., Koestner, R., & Ryan, R. M. (2001). Extrinsic rewards and intrinsic motivation in education: Reconsidered once again. *Review of Educational Research*, 71(1), 1–27. https://doi.org/10.3102/00346543071001001
24. Buehler, R., Griffin, D., & Ross, M. (1994). Exploring the "planning fallacy": Why people underestimate their task completion times. *Journal of Personality and Social Psychology*, 67(3), 366–381. https://doi.org/10.1037/0022-3514.67.3.366

Note: page ranges and DOIs for items 9, 10, 11, 15, 16, 17 and 18 come from my own knowledge of these papers, not from pages retrieved this session. Spot-check them before publication.
