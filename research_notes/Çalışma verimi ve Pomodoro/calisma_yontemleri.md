# Evidence-based study techniques and work/productivity methods (çalışma biçimleri ve verim yöntemleri)

Notes for the report writer. The final report is in Turkish for a university student who builds MFDP, a Pomodoro/focus-tracking desktop app with tasks, tags, an exam/homework calendar, session logs and an event log of interruptions. Evidence ratings used below:
- **A (strong):** several meta-analyses or a large, consistent experimental literature.
- **B (moderate):** some experiments or meta-analyses with important moderators, or mixed results.
- **C (weak/popular):** mainly books, anecdote, observational data or extrapolation.

A note on verification: claims marked "(abstract/secondary)" were checked against an abstract, a repository page or press coverage, not the full paper. Items marked "[not verified this session]" come from well-known primary sources whose DOI I am confident of, but whose text I did not read in this session. The writer should phrase those cautiously.

## 1. Learning techniques: what does the evidence say?

### Takeaway
Practice testing (retrieval practice) and distributed (spaced) practice are the two best-supported techniques (rating A), with meta-analytic effects of roughly g/d ≈ 0.5–0.6 over restudy or massed study. Interleaving helps moderately (g ≈ 0.42), but it depends on the material: it works for discriminating similar categories (math problem types, visual categories) and can backfire for word lists. Elaborative interrogation and self-explanation are moderate (B). Rereading, highlighting, summarization, the keyword mnemonic and imagery for text are low-utility.

### Cited Findings
**Dunlosky et al. 2013 (the anchor review)**
- Dunlosky, Rawson, Marsh, Nathan & Willingham (2013), *Psychological Science in the Public Interest* 14(1), 4–58, rated 10 techniques by generalizability across learners, materials, criterion tasks and learning conditions. Only **practice testing** and **distributed practice** received "high utility" — [APS press release](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html); [ScienceDaily](https://www.sciencedaily.com/releases/2013/01/130110111734.htm)
- **Low utility:** summarization, highlighting/underlining, the keyword mnemonic, imagery use for text learning, and rereading. Summarization and imagery help only some students under limited conditions. The keyword mnemonic is hard to implement and helps only for some materials and short retention intervals — [APS](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html); [Kent State](https://www.kent.edu/node/295736)
- **Moderate utility:** elaborative interrogation, self-explanation and interleaved practice. The authors said these show enough promise to recommend in appropriate situations — [Scott Barry Kaufman summary of the monograph](https://scottbarrykaufman.com/study-alert-improving-students-learning-with-effective-learning-techniques-from-cognitive-and-educational-psychology). The tier membership is from standard knowledge of the monograph, and the APS release lists only the high and low tiers.
- A 2021 meta-analysis of the same ten techniques (Donoghue & Hattie, *Frontiers in Education*) re-examined Dunlosky's ratings. It notes that four earlier spaced-vs-massed meta-analyses (about 300 studies) found an average effect of about 0.60 — [Frontiers in Education 2021](https://www.frontiersin.org/articles/10.3389/feduc.2021.581216/full)

**Retrieval practice (geri çağırma / kendini test etme): A**
- Adesope, Trevisan & Sundararajan (2017), *Review of Educational Research* 87(3), 659–701: practice tests beat restudying and all other comparison conditions. Effects were moderated by test format, feedback, participant characteristics and outcome type. Reported mean effects are medium-to-large, roughly g ≈ 0.50–0.61 — [SAGE abstract](https://journals.sagepub.com/doi/10.3102/0034654316689306); [WSU PDF](https://education.wsu.edu/documents/2018/01/rethinking-use-tests.pdf/); [Learning Scientists summary](https://www.learningscientists.org/blog/2017/2/9-1)
  - Conflicting secondary counts: one says 118 articles, 272 effect sizes and 15,472 participants; another says 188 articles. Check the PDF before citing a count.
  - Adesope found multiple-choice practice tests produced larger effects than short-answer tests. Rowland (2014) found the opposite pattern (recall > recognition) — [Frontiers 2018 review citing both](https://www.frontiersin.org/articles/10.3389/fpsyg.2018.02412/pdf)
- Rowland (2014), *Psychological Bulletin* 140(6), 1432–1463 (61 studies): testing vs. restudy d ≈ 0.50. The benefit was larger for recall than recognition tests and for retention intervals of 1 day or more. Feedback and initial retrieval success moderate the effect — [Rowland 2014 PDF (EPFL courseware)](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1%3AEPFL%2BDEMO%2B2020%2Btype%40asset%2Bblock/Rowland2014-meta-analysis.pdf); [Frontiers 2021](https://www.frontiersin.org/articles/10.3389/feduc.2021.581216/full)

**Distributed / spaced practice (aralıklı tekrar): A**
- Cepeda, Pashler, Vul, Wixted & Rohrer (2006), *Psychological Bulletin* 132(3), 354–380: 839 assessments in 317 experiments from 184 articles. Spacing beats massing. The optimal inter-study interval (ISI) increases as the retention interval (time to test) increases — [PubMed 16719566](https://pubmed.ncbi.nlm.nih.gov/16719566/); [USF repository](https://digitalcommons.usf.edu/psy_facpub/1771/)
- Cepeda, Vul, Rohrer, Wixted & Pashler (2008), *Psychological Science* 19(11), 1095–1102: more than 1,350 participants, study gaps up to 3.5 months and final tests up to 1 year later. For a fixed test delay, performance first rises then falls as the gap grows (a "ridgeline"). The optimal gap is about **20–40% of the test delay for a 1-week test** and about **5–10% for a 1-year test** — [PubMed 19076480](https://pubmed.ncbi.nlm.nih.gov/19076480/); [PDF](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf)
- A gap that is too short hurts retention much more than a gap that is too long — [York University news](https://yfile.news.yorku.ca/?p=9454)
- The authors concluded that many educational practices are "highly inefficient" — [PubMed](https://pubmed.ncbi.nlm.nih.gov/19076480/)

**Interleaving (karışık/serpiştirilmiş çalışma): B (material-dependent)**
- Brunmair & Richter (2019), *Psychological Bulletin*, "Similarity matters: A meta-analysis of interleaved learning and its moderators" (DOI 10.1037/bul0000209): 59 studies, 158 samples, 238 effect sizes. Overall **g = 0.42**. Paintings/visual categories **g = 0.67**. Mathematics **g = 0.34** (small). Word-based materials favored *blocking*, **g = −0.39**. Interleaving helps most when categories are similar and hard to discriminate — [Würzburg PDF](https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf); [X-MOL record](https://www.x-mol.com/paper/1213055298318831616)
- The math result in the published version is small but significant. An earlier conference version found no math effect — [Frontiers correction notice](https://frontiersin.org/articles/10.3389/fpsyg.2019.02296/full)

**Elaborative interrogation and self-explanation: B (moderate)**
- Both were rated moderate utility by Dunlosky et al. (2013) — [summary](https://scottbarrykaufman.com/study-alert-improving-students-learning-with-effective-learning-techniques-from-cognitive-and-educational-psychology); [Frontiers 2021 meta-analysis of ten techniques](https://www.frontiersin.org/articles/10.3389/feduc.2021.581216/full)

**Low-utility techniques: rereading, highlighting, summarization**
- Rated low utility by Dunlosky et al. 2013 — [APS](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html)

### Inferences
- In practice, the "big two" can be combined into **spaced retrieval**: self-quizzing spread over days. For MFDP this means a session type such as "Tekrar/Test" (review/quiz), distinct from a "Yeni konu/Okuma" (new material/reading) session.
- The Cepeda ridgeline gives the app a simple scheduling heuristic from the exam date in the calendar. For an exam 1 week away, review gaps of about 1–2 days. For about 1 month away, about 1 week. For a final at the end of term (about 3 months), about 1–2 weeks. Err on the side of longer gaps rather than shorter ones.
- Interleaving can be supported by tags: within one session, suggest mixing tasks tagged with related but different topics. This fits math or physics problem types, and fits vocabulary lists poorly.
- The app could flag sessions tagged "rereading" or "summarizing" and suggest converting them into retrieval (for example, closed-book recall followed by a check).

### Gaps
- **Dual coding and concrete examples:** I found no meta-analysis in this session. Both appear in the Learning Scientists' "six strategies" (Weinstein, Madan & Sumeracki 2018, *Cognitive Research: Principles and Implications*, DOI 10.1186/s41235-017-0087-y [not verified this session]). Their evidence is weaker and more indirect than for retrieval and spacing, so rate them B/C.
- Exact effect sizes for elaborative interrogation and self-explanation were not retrieved. The Frontiers 2021 meta-analysis (Donoghue & Hattie) has them, but I did not extract the numbers.
- The Adesope study count conflicts across secondary sources (118 vs. 188 articles).

## 2. Work structuring: deep work, time blocking, Flowtime, GTD, Eisenhower, eat-the-frog, single-tasking, interruptions

### Takeaway
The cognitive basis for single-tasking is solid: task-switch costs are robust in the lab (Monsell 2003), and attention residue from unfinished tasks impairs the next task (Leroy 2009). The popular "23 minutes to recover from an interruption" figure is a rounded, secondhand number. Mark et al. (2005) actually reported that interrupted work was resumed after about 25 minutes on average, in a small observational sample, and that is a resumption delay, not a recovery-to-full-focus time. Named methods (Deep Work, GTD, Eisenhower, eat-the-frog, timeboxing) are mostly practitioner frameworks with little direct experimental testing (rating C). Their plausible mechanisms (fewer switches, planning, implementation intentions) are better supported than the methods themselves. On Pomodoro vs. Flowtime, a few recent controlled studies exist, with mixed results.

### Cited Findings
**Task switching and multitasking**
- Monsell (2003), "Task switching," *Trends in Cognitive Sciences* 7(3), 134–140 (DOI 10.1016/S1364-6613(03)00028-7) reviews the control processes for reconfiguring task sets. Switch costs persist even when there is time to prepare (a "residual switch cost") — [citation record](https://modeldb.science/citations/102732); [Bremen bibliography](https://cindy.informatik.uni-bremen.de/www3/www.sfbtr8.spatial-cognition.de/aigaion/index.php/publications/show/1871.html). Details are from a secondary copy.
- Ophir, Nass & Wagner (2009, *PNAS*): heavy media multitaskers filtered irrelevant stimuli worse and showed larger switch costs (one summary reports 426 ms slower on switch trials than light multitaskers) — [Learning Guild](https://www.learningguild.com/articles/is-media-multitasking-a-myth); [Boing Boing interview](https://boingboing.net/2011/11/07/eyal-ophir-on-the-science-of-multitasking.html). Later replications are **mixed** — [PMC5662702](https://pmc.ncbi.nlm.nih.gov/articles/PMC5662702); [MSU dissertation](https://d.lib.msu.edu/etd/2473?q=W+P)

**Attention residue**
- Leroy (2009), "Why is it so hard to do my work? The challenge of attention residue when switching between work tasks," *Organizational Behavior and Human Decision Processes* 109(2), 168–181 (DOI 10.1016/j.obhdp.2009.04.002). In two experiments, people who switched away from an unfinished task kept thinking about it, and performance on the next task suffered — [UW Bothell faculty page](https://www.uwb.edu/faculty/?p=144); [UW Bothell news](https://www.uwb.edu/news/?p=30821) (secondary)
- Leroy & Schmidt (2016), *OBHDP* 137, 218–235: regulatory focus affects transitions after interruptions. A related press report says that making a quick "plan for returning" to the interrupted task reduces residue — [RePEc](https://ideas.repec.org/a/eee/jobhdp/v137y2016icp218-235.html); [UW news 2018](https://www.washington.edu/news/2018/01/16/task-interrupted-a-plan-for-returning-helps-you-move-on/)

**Interruptions (the "23 minutes" claim)**
- Mark, Gonzalez & Harris (2005, CHI), "No Task Left Behind? Examining the Nature of Fragmented Work": shadowed 24 information workers at one company. Work resumed the same day was resumed after **25 min 26 s** on average. After an external interruption it was **22 min 37 s**, and after a self-interruption **29 min 1 s**. The "23 min 15 s" figure is a popular rounding from Mark's interviews and does not appear in the paper. The measure is time until a task is *resumed*, not time to regain focus — [Feedbagel investigation](https://feedbagel.com/post/investigating-the-origin-of-the-23-minute-interruption-recovery-time-claim); [ScienceBlog](https://scienceblog.com/t-23-minutes-return-focus-after-interruption/)
- Mark, Gudith & Klocke (2008, CHI), "The Cost of Interrupted Work: More Speed and Stress," pp. 107–110: in a simulated email task, interrupted participants finished *faster* with no loss of quality. However, they reported significantly more stress, frustration, time pressure and effort. Openness to experience and need for structure predicted the costs — [PDF](https://www.interruptions.net/literature/Mark-CHI08.pdf); [dblp](https://dblp1.uni-trier.de/rec/conf/chi/MarkGK08.html)

**Pomodoro vs. self-regulated breaks vs. Flowtime (directly relevant to MFDP)**
- Biwer, Wiradhany, oude Egbrink & de Bruin (2023), *British Journal of Educational Psychology*: 87 Dutch university students in real self-study. Systematic breaks (including a Pomodoro-like 24 min work / 6 min break) were compared with self-regulated breaks. The self-regulated group took longer blocks and breaks and reported **more fatigue and distractedness, and less concentration and motivation**. There was no difference in mental effort or task completion. The authors conclude that predetermined breaks improve mood and are more efficient — [PubMed 36859717](https://pubmed.ncbi.nlm.nih.gov/36859717/); [Maastricht CRIS](https://cris.maastrichtuniversity.nl/en/publications/understanding-effort-regulation-comparing-pomodoro-breaks-and-sel)
- Smits, Wenzel & de Bruin (2025): 94 students in a 2-hour session compared Pomodoro, Flowtime (self-chosen break time, with the break length proportional to the work length) and self-regulated breaks. The preprint reports that Flowtime gave a *slower increase in fatigue*, with no difference in motivation, productivity, task completion or flow. The peer-reviewed version (PMC) reports that Pomodoro gave a faster fatigue increase than self-regulated breaks, but overall fatigue and motivation levels did not differ — [Preprints.org](https://www.preprints.org/manuscript/202503.0845/v1); [PMC12292963](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/). Note the conflict between the two Dutch studies on whether fixed or flexible breaks are better. Both find little difference in output.

**Breaks in general**
- Albulescu et al. (2022), "Give me a break!", *PLOS ONE* 17(8): e0272460. A meta-analysis of micro-breaks (10 minutes or less): 22 samples, N = 2,335. Micro-breaks increased vigor (**d = .36**) and reduced fatigue (**d = .35**). The overall performance effect was not significant (**d = .16**, p = .116). Performance benefits appeared only for less cognitively demanding tasks, and longer breaks gave larger performance boosts. Recovery from highly depleting tasks may need breaks longer than 10 minutes — [DOAJ](https://doaj.org/article/c6f37b6ba159469296b2cb968b65505f); [EurekAlert](https://www.eurekalert.org/news-releases/962663); [ScienceDaily](https://Www.sciencedaily.com/releases/2022/08/220831152754.htm)

**Named methods (rating C, practitioner frameworks)**
- *Deep Work* (Newport, 2016) cites Ericsson's deliberate-practice work as the source of a "~4 hours/day" limit on demanding cognitive work. The original 1993 paper does not state a hard cap (see Section 4) — [Unhustle blog discussing the chain of citations](https://unhustle.substack.com/p/the-10000-hour-rule-myth-and-the)
- **Pomodoro** itself: Wikipedia notes it was created by Francesco Cirillo in the late 1980s as a personal technique, and controlled studies are recent and few — [Wikipedia](https://en.wikipedia.org/wiki/Pomodoro_Technique)

### Inferences
- MFDP's existing interruption logging (AtomicAnalyzer interruptions, focus shifts, DND) maps directly onto this literature. Useful metrics are: switches per session, time from an interruption until the same task is resumed (Mark 2005's measure), and self- vs. external interruptions (self-interruptions resumed more slowly in Mark 2005).
- Attention residue suggests a cheap feature: when a session is paused or interrupted, prompt for a one-line "where I left off / next step" note. This mirrors Leroy's "plan for returning".
- The Pomodoro vs. Flowtime evidence suggests offering both modes (MFDP already has a countdown and a FreeTimer count-up). Flowtime breaks could be auto-proposed at about 1/5 to 1/3 of the work length. It is fair to tell users that output differences are small and the main effect is on fatigue and mood.
- Time blocking, Eisenhower and eat-the-frog can be supported cheaply through task priority/urgency fields and a "first task of the day" marker. The report should present them as reasonable heuristics, not proven methods.
- Batching shallow work: there is no direct study. The rationale comes from switch costs and residue (Monsell; Leroy). The app could offer a "shallow/admin" tag and suggest scheduling those tasks in one block.

### Gaps
- No controlled studies were found on GTD, the Eisenhower matrix, eat-the-frog or time blocking as such. An academic theoretical paper on GTD exists (Heylighen & Vidal 2008, "Getting Things Done: the science behind stress-free productivity," *Long Range Planning* [not verified this session]).
- The underlying evidence on implementation intentions and planning (Gollwitzer & Sheeran 2006 meta-analysis, d ≈ 0.65 [not verified this session]) would strengthen the timeboxing rationale but was not fetched.
- Monsell 2003's specific switch-cost magnitudes (typically on the order of 100–200+ ms in the lab) were not extracted from the full text.

## 3. Time of day and biology: chronotype, circadian performance, ultradian rhythms, sleep, post-lunch dip

### Takeaway
A synchrony effect (better performance at one's preferred time of day) exists but is inconsistent in young adults: about 45% of studies find it, mostly for attention, inhibition and memory. It is more consistent in older adults. The "90-minute ultradian work cycle" (Kleitman's BRAC) is well established *in sleep* only. The claim that it should structure waking work rests on weak, mostly anecdotal evidence (C). Sleep is strongly linked to grades: regular, sufficient sleep over the preceding weeks predicts exam performance, while the night before does not.

### Cited Findings
- May, Hasher & Stoltzfus (1993), *Psychological Science* 4, 326–330: most younger adults were evening or neutral types, and nearly all older adults were morning types. Age differences in recognition memory appeared in late-afternoon testing but disappeared in the morning, when older adults were at their peak — [Hasher lab abstract](https://hasherlab.psych.utoronto.ca/abstracts/may_etal_93.htm); [APS journal page](https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1993.tb00573.x/)
- Chauhan et al. (2025), "Chronotype and synchrony effects in human cognitive performance: a systematic review," *Chronobiology International* 42(4), 463–499 (DOI 10.1080/07420528.2025.2490495). Of 65 studies, more than 80% found no main effect of chronotype on cognition. A synchrony effect appeared in 29 of 64 studies (45%) of adults aged 18–45, mostly for attention, inhibition and memory, and in 10 of 12 studies (83%) of older adults, especially for fluid abilities. Task complexity and lighting moderate the effect — [Kingston repository](https://researchinnovation.kingston.ac.uk/en/publications/chronotype-and-synchrony-effects-in-human-cognitive-performance-a/); [Brunel full text](https://bura.brunel.ac.uk/bitstream/2438/31067/6/FullText.pdf)
- **BRAC / ultradian:** Kleitman proposed a roughly 90-minute (80–120 minute) basic rest-activity cycle, best observed in the NREM/REM sleep cycle. As early as 1977, critics argued there was no evidence for a BRAC outside sleep. A *Nature* study found the REM cycle is sleep-dependent rather than an activity-independent clock. Despite this, BRAC is widely used as a productivity tool — [Wikipedia: Basic rest–activity cycle](https://en.wikipedia.org/wiki/Basic_rest%E2%80%93activity_cycle); [Nature 1977 PDF](https://www.nature.com/articles/265360a0.pdf)
- **Sleep and grades:** Okano, Kaczmarzyk, Dave, Gabrieli & Grossman (2019), *npj Science of Learning* (DOI 10.1038/s41539-019-0055-z). Fitbit-tracked sleep of 88 students in an MIT intro chemistry course was compared with their grades. Better quality, longer duration and more consistent sleep correlated with better grades and together explained **about 24% of grade variance**. Sleep the *single night before* a test did not predict scores, but sleep over the prior week and month did. Press coverage adds that going to bed after a personal threshold (often around 2 a.m.) predicted lower scores regardless of sleep length. The study is correlational and covers a single course — [PMC6773696](https://pmc.ncbi.nlm.nih.gov/articles/PMC6773696); [MIT DSpace](https://dspace.mit.edu/handle/1721.1/127257); [Neuroscience News](https://neurosciencenews.com/sleep-college-grades-15007/)
- Hogan et al. (2009) studied optimal time of day and the consolidation of learning in younger and older adults (Hasher lab) — [PDF](https://hasherlab.psych.utoronto.ca/PDF/2009%20(Hogan%20et%20al.)%20Optimal%20time-of-day%20and%20consolidation%20of%20learning%20in%20younger%20and%20older%20adult.pdf)

### Inferences
- MFDP already logs session start times and could estimate each user's personal "best hours" from their own data (for example, focus score or interruption rate by hour of day). That is more defensible than imposing generic chronotype rules, given that only about 45% of young-adult studies find synchrony effects.
- 90-minute blocks should be offered as an option, not presented as biology.
- Okano's finding supports a calendar feature that warns against all-nighters: in the last week before an exam, the app could nudge toward consistent sleep and away from late-night sessions (for example, sessions after 01:00–02:00).

### Gaps
- **Post-lunch dip:** no source was retrieved in this session. It is a commonly reported early-afternoon dip in alertness, with circadian and partly meal-related contributions (Monk 2005, "The post-lunch dip in performance," *Clinics in Sports Medicine* [not verified this session]).
- **Sleep-dependent memory consolidation** at the mechanistic level (for example, Diekelmann & Born 2010, *Nature Reviews Neuroscience*; Walker) was not fetched.
- I found no evidence-based figure on whether waking ultradian rhythms predict an optimal work-block length. The Wikipedia claim of "overwhelming evidence" from a meta-analysis could not be verified.

## 4. Fatigue and practice: deliberate practice, the ~4-hour limit, cognitive fatigue

### Takeaway
Deliberate practice matters, but it explains far less of performance than Ericsson's framing implied. Macnamara et al. (2014) found about 12% of variance overall, ranging from about 26% in games to 4% in education and under 1% in professions. The popular "~4 hours of deep work per day" limit traces to the observation that Ericsson's expert violinists practiced about that much in total per day. It is an observational, small-sample, single-domain figure, not a measured cognitive ceiling (C). There is new neurometabolic evidence of cognitive fatigue after a day of demanding control tasks (Wiehler et al. 2022), but it comes from a single study.

### Cited Findings
- Ericsson, Krampe & Tesch-Römer (1993), *Psychological Review* 100(3), 363–406: violin students at a Berlin academy. Accumulated practice by age 18 was about 4,000 hours for future teachers, about 8,000 for "very good" students and more than 10,000 for the best — [Creativity Post summary](https://www.creativitypost.com/arts/the_most_valuable_lesson_i_learned_from_playing_the_violin). A daily limit of about 4 hours of deliberate practice is widely attributed to this paper and repeated by Newport, but I found **no direct quote of a hard cap** in the sources searched. One critic notes that some of the paper's practice-amount claims rest on thin sources — [Andy Matuschak notes](https://notes.andymatuschak.org/z6xWa5QDyUmvuDqZ9Z7sANrfjf8sLoJ7BnspW); [AcesoUnderGlass](https://acesounderglass.com/2019/05/); [Unhustle](https://unhustle.substack.com/p/the-10000-hour-rule-myth-and-the)
- Macnamara, Hambrick & Oswald (2014), *Psychological Science* 25(8), 1608–1618 (DOI 10.1177/0956797614535810). Deliberate practice explained **26%** of performance variance in games, **21%** in music, **18%** in sports, **4%** in education and **<1%** in professions. The authors concluded that deliberate practice is important but not as important as claimed. The overall average was about 12% [overall figure not verified this session] — [ScienceDaily](https://www.sciencedaily.com/releases/2014/07/140716123835.htm); [Stafforini summary](https://stafforini.com/works/macnamara-2014-deliberate-practice-and/)
- Hambrick et al. (commentary, "Facing facts about deliberate practice," *Frontiers in Psychology* 2014) defend the meta-analysis. They report that correcting for measurement error gives about 19% on average, and that earlier reanalyses gave about 34% (chess) and 30% (music) — [PMC4101876](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/)
- Macnamara, Moreau & Hambrick (2016), a sports meta-analysis: deliberate practice explained 18% of sports performance overall but only **1% among elite athletes** — [Purdue PDF](https://hhs.purdue.edu/skill-learning-and-performance-lab/wp-content/uploads/sites/43/2024/08/macnamara-et-al-2016-the-relationship-between-deliberate-practice-and-performance-in-sports-a-meta-analysis.pdf)
- Counterpoint (2021, *Current Psychology*): the meta-analyses ignore how *individualized* practice is. In chess, effect sizes were more than three times larger at high individualization and quality — [Springer](https://link.springer.com/article/10.1007/s12144-021-02326-x)
- **Cognitive fatigue:** Wiehler, Branzoli, Adanyeguh, Mochel & Pessiglione (2022), *Current Biology* 32, 3564–3575. After roughly a workday of high-demand cognitive-control tasks, glutamate in the lateral prefrontal cortex was higher than in a low-demand group. The high-demand group's choices also shifted toward short-delay, low-effort options, and their pupil dilation decreased. N was about 40 (press reports differ: 39 vs. 40). Outside experts call for causal confirmation — [HAL abstract](https://hal.sorbonne-universite.fr/hal-04534917); [BrainFacts](https://brainfacts.org/neuroscience-in-society/neuroscience-in-the-news/2022/icymi-glutamate-buildup-in-prefrontal-cortex-may-indicate-mental-fatigue-090722); [Disabled World](https://www.disabled-world.com/health/neurology/brain/thinking.php)

### Inferences
- A daily "deep focus budget" (for example, 3–4 h of logged focus time) is a reasonable *heuristic target and warning threshold* in MFDP. It should be framed as an experience-based guideline, not a scientific limit. Showing a user's historical distribution of daily focus minutes, and how focus quality degrades late in the day, would be more honest.
- Wiehler's results suggest scheduling the hardest tasks (new material, problem solving) earlier in the day and lighter work (review flashcards, admin) later. This fits with the user's own best hours.
- For students, the education-domain figure (about 4% of variance) suggests that *how* one studies (retrieval, spacing) matters more than raw hours. The app should not reward hours alone. It could highlight the share of sessions spent on retrieval vs. passive review.

### Gaps
- The exact daily practice hours reported in Ericsson 1993 (often summarized as about 3.5–4 h/day of solitary practice for the best groups, with naps) could not be verified from the primary text in this session.
- I did not fetch the ego-depletion replication failures (Hagger et al. 2016, multi-lab registered replication [not verified this session]). They are relevant to "willpower runs out" claims.

## 5. Practical study session design: session length, mixing retrieval and spacing in a Pomodoro app, exam prep timelines

### Takeaway
No study establishes a single optimal session length. Experimental evidence supports short fixed work blocks with breaks for mood and fatigue (Biwer 2023: 24/6), but not for higher output. Micro-breaks of 10 minutes or less help vigor and fatigue, while demanding work may need longer breaks. The clearest design guidance comes from spacing: spread retrieval over days, with gaps scaled to the exam date (Cepeda 2008), and protect sleep in the run-up to the exam (Okano 2019).

### Cited Findings
- Fixed Pomodoro-like breaks (24/6) produced less fatigue and distraction and more concentration and motivation than self-regulated breaks, with equal task completion — [PubMed 36859717](https://pubmed.ncbi.nlm.nih.gov/36859717/)
- Flowtime was comparable on productivity and showed a slower fatigue rise in one preprint, but the peer-reviewed results are mixed — [Preprints.org](https://www.preprints.org/manuscript/202503.0845/v1); [PMC12292963](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/)
- Micro-breaks of 10 minutes or less: vigor d = .36, fatigue d = .35, with performance benefits only on less demanding tasks. Longer breaks gave more performance benefit — [EurekAlert](https://www.eurekalert.org/news-releases/962663)
- Optimal review gap ≈ 20–40% of the time to test for short horizons (1 week), shrinking to 5–10% for long horizons (1 year). Too short is worse than too long — [PubMed 19076480](https://pubmed.ncbi.nlm.nih.gov/19076480/); [York U](https://yfile.news.yorku.ca/?p=9454)
- The testing effect is larger at retention intervals of 1 day or more and with feedback — [Rowland 2014 PDF](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1%3AEPFL%2BDEMO%2B2020%2Btype%40asset%2Bblock/Rowland2014-meta-analysis.pdf)
- Sleep in the week and month before a test predicts grades. The single night before does not — [PMC6773696](https://pmc.ncbi.nlm.nih.gov/articles/PMC6773696)

### Inferences
Practical template for MFDP. These are derived recommendations, not tested protocols.
- **Inside one Pomodoro (about 25 min):** the first 3–5 minutes are closed-book recall of the previous session's material ("brain dump" / free recall). Then about 15–18 minutes of new material, studied with self-explanation or elaborative "why?" questions. The last 3–5 minutes are self-quizzing on today's material, with checking against the notes (feedback). The break is 5 minutes, away from the screen.
- **Across a day:** put new or hard material in the user's personally best hours. Put interleaved practice problems mid-session. Put light flashcard review late in the day. Use a daily focus target of about 3–4 h, framed as a soft cap.
- **Exam timeline (from a calendar exam date):**
  - T−4 weeks or more: first pass through the material, plus a short retrieval quiz after each topic.
  - Then reviews at roughly weekly gaps (about 20–25% of the remaining time).
  - T−1 week: daily mixed (interleaved) practice tests across topics.
  - T−1 day: light retrieval only and a normal bedtime, with no all-nighter.
  - The app can auto-generate "review" tasks at expanding dates when a study task is completed (spaced-repetition-lite), with the gap tied to the exam date.
- **App metrics that align with evidence:**
  - Share of sessions tagged retrieval vs. reread.
  - Number of distinct study days per exam topic (spacing).
  - Interruptions and switches per session.
  - Late-night session count in the week before an exam.

### Gaps
- There is no experimental basis for 25 minutes specifically (vs. 50/10 or 90). Biwer's study used 24/6 and the comparison was fixed vs. self-regulated, not different fixed lengths.
- No study was found that tests a combined Pomodoro + spaced retrieval protocol end to end.
- Expanding vs. uniform spacing schedules: Cepeda 2006 discussed expanding intervals, but I did not extract the conclusion. Literature generally finds expanding schedules not reliably better than equal ones [not verified this session].

### Reference list
1. Adesope, O. O., Trevisan, D. A., & Sundararajan, N. (2017). Rethinking the use of tests: A meta-analysis of practice testing. *Review of Educational Research, 87*(3), 659–701. https://doi.org/10.3102/0034654316689306
2. Albulescu, P., Macsinga, I., Rusu, A., Sulea, C., Bodnaru, A., & Tulbure, B. T. (2022). "Give me a break!" A systematic review and meta-analysis on the efficacy of micro-breaks for increasing well-being and performance. *PLOS ONE, 17*(8), e0272460. https://doi.org/10.1371/journal.pone.0272460
3. Biwer, F., Wiradhany, W., oude Egbrink, M. G. A., & de Bruin, A. B. H. (2023). Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks. *British Journal of Educational Psychology, 93*(S2), 353–367. https://pubmed.ncbi.nlm.nih.gov/36859717/
4. Brunmair, M., & Richter, T. (2019). Similarity matters: A meta-analysis of interleaved learning and its moderators. *Psychological Bulletin, 145*(11), 1029–1052. https://doi.org/10.1037/bul0000209
5. Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychological Bulletin, 132*(3), 354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/
6. Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. *Psychological Science, 19*(11), 1095–1102. https://pubmed.ncbi.nlm.nih.gov/19076480/
7. Chauhan, S., et al. (2025). Chronotype and synchrony effects in human cognitive performance: A systematic review. *Chronobiology International, 42*(4), 463–499. https://doi.org/10.1080/07420528.2025.2490495
8. Donoghue, G. M., & Hattie, J. A. C. (2021). A meta-analysis of ten learning techniques. *Frontiers in Education, 6*, 581216. https://doi.org/10.3389/feduc.2021.581216
9. Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques. *Psychological Science in the Public Interest, 14*(1), 4–58. https://doi.org/10.1177/1529100612453266
10. Ericsson, K. A., Krampe, R. T., & Tesch-Römer, C. (1993). The role of deliberate practice in the acquisition of expert performance. *Psychological Review, 100*(3), 363–406. https://doi.org/10.1037/0033-295X.100.3.363
11. Hambrick, D. Z., Altmann, E. M., Oswald, F. L., Meinz, E. J., Gobet, F., & Campitelli, G. (2014). Facing facts about deliberate practice. *Frontiers in Psychology, 5*, 751. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/
12. Kleitman's BRAC: overview and critiques. https://en.wikipedia.org/wiki/Basic_rest%E2%80%93activity_cycle
13. Leroy, S. (2009). Why is it so hard to do my work? The challenge of attention residue when switching between work tasks. *Organizational Behavior and Human Decision Processes, 109*(2), 168–181. https://doi.org/10.1016/j.obhdp.2009.04.002
14. Leroy, S., & Schmidt, A. M. (2016). The effect of regulatory focus on attention residue and performance during interruptions. *OBHDP, 137*, 218–235. https://ideas.repec.org/a/eee/jobhdp/v137y2016icp218-235.html
15. Macnamara, B. N., Hambrick, D. Z., & Oswald, F. L. (2014). Deliberate practice and performance in music, games, sports, education, and professions: A meta-analysis. *Psychological Science, 25*(8), 1608–1618. https://doi.org/10.1177/0956797614535810
16. Macnamara, B. N., Moreau, D., & Hambrick, D. Z. (2016). The relationship between deliberate practice and performance in sports: A meta-analysis. *Perspectives on Psychological Science, 11*(3), 333–350. https://hhs.purdue.edu/skill-learning-and-performance-lab/wp-content/uploads/sites/43/2024/08/macnamara-et-al-2016-the-relationship-between-deliberate-practice-and-performance-in-sports-a-meta-analysis.pdf
17. Mark, G., Gonzalez, V. M., & Harris, J. (2005). No task left behind? Examining the nature of fragmented work. *Proc. CHI 2005*, 321–330. https://doi.org/10.1145/1054972.1055017
18. Mark, G., Gudith, D., & Klocke, U. (2008). The cost of interrupted work: More speed and stress. *Proc. CHI 2008*, 107–110. https://www.interruptions.net/literature/Mark-CHI08.pdf
19. May, C. P., Hasher, L., & Stoltzfus, E. R. (1993). Optimal time of day and the magnitude of age differences in memory. *Psychological Science, 4*(5), 326–330. https://hasherlab.psych.utoronto.ca/abstracts/may_etal_93.htm
20. Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences, 7*(3), 134–140. https://doi.org/10.1016/S1364-6613(03)00028-7
21. Newport, C. (2016). *Deep Work: Rules for Focused Success in a Distracted World*. Grand Central Publishing. (Book; practitioner source.)
22. Okano, K., Kaczmarzyk, J. R., Dave, N., Gabrieli, J. D. E., & Grossman, J. C. (2019). Sleep quality, duration, and consistency are associated with better academic performance in college students. *npj Science of Learning, 4*, 16. https://doi.org/10.1038/s41539-019-0055-z
23. Ophir, E., Nass, C., & Wagner, A. D. (2009). Cognitive control in media multitaskers. *PNAS, 106*(37), 15583–15587. https://doi.org/10.1073/pnas.0903620106
24. Rowland, C. A. (2014). The effect of testing versus restudy on retention: A meta-analytic review of the testing effect. *Psychological Bulletin, 140*(6), 1432–1463. https://doi.org/10.1037/a0037559
25. Smits, E., Wenzel, K., & de Bruin, A. (2025). Pomodoro vs. Flowtime vs. self-regulated breaks [preprint / PMC version]. https://www.preprints.org/manuscript/202503.0845/v1 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/
26. Wiehler, A., Branzoli, F., Adanyeguh, I., Mochel, F., & Pessiglione, M. (2022). A neuro-metabolic account of why daylong cognitive work alters the control of economic decisions. *Current Biology, 32*(16), 3564–3575. https://hal.sorbonne-universite.fr/hal-04534917
27. Allen, D. (2001/2015). *Getting Things Done*. Penguin. (Book; practitioner source, not empirically tested as a package.)
28. Weinstein, Y., Madan, C. R., & Sumeracki, M. A. (2018). Teaching the science of learning. *Cognitive Research: Principles and Implications, 3*, 2. https://doi.org/10.1186/s41235-017-0087-y [not verified this session]
