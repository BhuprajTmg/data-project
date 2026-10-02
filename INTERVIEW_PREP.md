# HIT140 viva pack — Saturday 3 Oct 2026, 12:00 pm

Read this tonight. Print or keep open **`INTERVIEW_CHEATSHEET.md`** during the call.

The session is **20 minutes**, **all group members must speak**, and **marks come out after the interview**. Yakub’s email is a methodology viva on the work you already submitted. It is not a notice that you failed, and it is not a notice that you handed in the wrong assignment.

---

## 1. You are not in the trouble you think

### What the email actually is

Sameer moved the slot to **3 October**. Yakub is holding a **20-minute follow-up** on your **Assignment 2 submission and presentation**. The stated purpose is to ask about:

- methodology
- analytical approach
- decisions you made
- whether you understand the work on the slides

Marks are held until after the interview, and the interview **may count toward the outcome**. That wording is normal for a group oral defence: they want to hear that every member can explain the project, not just that a polished HTML file and PowerPoint landed in the dropbox.

### What the email is not

It does **not** say you submitted the wrong assignment. It does **not** mention Objective 2, Assignment 3, or a penalty. Do not invent a crisis that is not in the email.

### If Assignment 2 was meant to be Objective 1 only

You still completed Objective 1 in full:

1. a distinct question
2. wrangling
3. sampling
4. descriptive statistics
5. a 95% confidence interval
6. a t-test

That is four tasks, α = 0.05, seed 42. Objective 2 (the two pre-kickoff regressions) is **extra work on the same dataset**, not missing work.

Markers almost never fail a group for including extra completed analysis when the required Objective 1 skills are present. The real risk tomorrow is **not** “we also showed regressions.” The real risk is a group member going silent, guessing p-values, or being unable to say *why* a test or predictor was chosen.

### Do not send a confession email

Do **not** write: “Sorry we accidentally submitted Assignment 3 / both objectives.” That creates a problem the lecturers have not raised.

If 12:00 Saturday works, send only a short confirmation (or nothing, if the invitation already stands):

> Hi Yakub / Sameer,
>
> Thank you for the invitation. Our group will attend the follow-up interview on Saturday 3 October at 12:00 pm.
>
> Kind regards,
> [names]

If 12:00 is impossible, say so **within 24 hours of the invitation**, as they asked, and propose another **Saturday morning** slot. Do not discuss marks, Objective 2, or Assignment 3 in that email.

### If they ask tomorrow why the presentation includes Objective 2

Say this calmly. Do not apologise as if you cheated. Do not claim the brief ordered both if you are not sure it did.

> We treated the World Cup extract as one project. Assignment 2 required four inferential tasks on that data, and we completed those in full — question, wrangle, sample, describe, 95% CI, and a t-test, each at alpha 0.05. We also fitted the two pre-match linear models because they use the same three tables and they help interpret the inferential results. For example the UEFA market-value gap in Task 3 shows up as `value_diff` in the goal-difference model. If Objective 2 is formally Assessment 3, we can submit a deeper regression-focused report there without changing the compiled data.

Then stop talking. Do not volunteer “we mixed up the phases” unless they press.

If they do not ask, **do not raise it**. Answer the question in front of you.

### If they ask who used ChatGPT / Copilot / Cursor

Do not lie, and do not dump a confession. The viva *is* the test of authorship.

> We used coding tools to help with Python, charts, and slide layout. The research questions, the sampling design, which test to run, which predictors were allowed, and how we read the p-values are our decisions. Every number on the slides can be regenerated from `wc2026_analytics.py` and `fifa data.xlsx`.

Then prove it by explaining a decision well (sampling on purpose, pre-match-only predictors, one-sided UEFA test).

---

## 2. How to run a 20-minute viva

**Goal:** every person speaks; nobody owns a secret slide that the others cannot explain.

Suggested split (swap names tonight):

| Role | Primary | Must also be able to cover |
|------|---------|----------------------------|
| A — Data | scrape, joins, 308 goals / 15 reds, name cleaning | why no in-match stats in the models |
| B — Tasks 1–2 | discipline + attendance, non-results | p-value vs “fail to reject” |
| C — Tasks 3–4 | UEFA value + GK age, one-sided vs one-sample | Levene → Welch vs pooled |
| D — Regression | both OLS models, VIF, hold-out, Poisson note | coefficient signs for rank and value |

Open with **30 seconds**, then wait for their questions. Do not replay the 2.5-minute presentation unless they ask.

> We compiled 104 matches, 48 teams, and 1,016 players from public World Cup 2026 sources. Objective 1 is four inferential tasks with sampling, CIs, and t-tests. Objective 2 is two linear models using only information knowable before kickoff. Two of the inferential questions were non-significant; UEFA value and goalkeeper age were significant. Ranking gap and squad value are the robust pre-match predictors.

If they ask “who did what?”, be specific and overlapping: “A led compilation, B/C led the four tests, D led the regressions, and we all reviewed the HTML and slides.” Never say “one person did everything.”

**Rules in the room**

- Answer the question asked. Then stop.
- If you do not remember a digit, say the decision and the direction: “p was about 0.45, well above 0.05, small effect, we fail to reject.” Guessing `p = 0.004` when it was `0.45` is worse than rounding.
- “Fail to reject H₀” is **not** “H₀ is true” and **not** “no difference exists.”
- A p-value is **not** “the probability that H₀ is true.”
- If someone freezes, another member may add one sentence — do not talk over each other.

---

## 3. Pipeline — scrape to visualisation

Speak this as a story. This is the “from the start of the assignment to the finished product” answer.

### 3.1 What the tournament is

- Canada / Mexico / USA, **11 June – 19 July 2026**
- Expanded **48 teams**, **12 groups of 4**, then Round of 32 → 16 → QF → SF → third place → final
- **104 official matches**
- Spain beat Argentina **1–0 after extra time** in the final at **MetLife Stadium on 19 July 2026**
- Co-hosts: Mexico, Canada, USA

### 3.2 Three tables (the grain of the project)

| Table | Grain | Rows | In the Excel workbook |
|-------|--------|------|------------------------|
| matches | one official match | 104 | sheet `matches` |
| teams | one national team | 48 | sheet `teams` |
| players | one player with ≥1 appearance | 1,016 | sheet `players` |

Everything else (samples, CIs, t-tests, the two regression matrices) is **derived** from these three.

### 3.3 Where each field came from

**Matches** — FIFA match centre, Wikipedia group and knockout pages, worldcup.org.uk chronological list, BBC cross-checks.

Fields: match number, date, stage, group, venue, city, country, team1, team2, goals, extra time, penalties, attendance.

All **104 attendance figures are official**. None were guessed.

**Teams** — FIFA World Ranking **11 June 2026** (pre-tournament freeze), Transfermarkt squad market values and average ages, Wikipedia for titles / appearances / confederation / host flag.

Confederations in the 48: UEFA 16, CAF 10, AFC 9, CONCACAF 6, CONMEBOL 6, OFC 1.

**Players** — built in `scripts/build_dataset.py` by merging:

1. Wikipedia squad lists → name, team, position (GK/DF/MF/FW), age
2. fotmob minutes leaderboard → appearances and minutes
3. Wikipedia goalscorer module → goals
4. fotmob yellow and red leaderboards → cards
5. assists for high-profile players cross-checked from FIFA / news reports (assists were the messiest field and were **not** used in any of the six analyses)

A player with no verifiable appearance was **dropped**. The assignment population is players who **featured**, not the full 26-man lists.

Name matching: strip accents, Wikipedia `[[link|display]]` markup, Turkish ı/i, Korean/Japanese given-name vs family-name order, and a short alias list (`Hwang In-beom` ↔ `In-beom Hwang`, `Musa Al-Taamari` ↔ `Mousa Tamari`, etc.).

Team-name variants were canonicalised so the three tables join: USA / United States, Turkiye / Turkey / Türkiye, Ivory Coast / Côte d'Ivoire, Curacao / Curaçao, Czechia / Czech Republic, DR Congo variants, and so on. After that, **every team in matches and players maps to exactly one row in teams**.

### 3.4 Data-quality checks you should be proud of

- Player goals **294** + own goals **14** = official tournament total **308**
- Red cards **15** — matches the official count
- Yellow cards in the file: **244** (used for Task 1 as yellows per appearance)
- One fake “fact” was rejected: Argentina and Spain were **not** in the same group (Argentina Group J, Spain Group H). They only met in the **final**. We did not invent a group-stage 2–1.

Honest caveats:

- Transfermarkt values and average ages are **point-in-time snapshots** (a few percent either way depending on pull date)
- Assists are incomplete; we did not analyse them
- fotmob leaderboard parsing is not a live API scrape; we saved extracts and merged them

### 3.5 Wrangling into analysis columns

`wc2026_analytics.py` (and `src/data_prep.py`) then:

- `cards_per_app = yellow_cards / appearances` so a seven-match finalist is comparable to a one-match substitute
- `knockout` flag from stage ∈ {Round of 32, Round of 16, Quarter-final, Semi-final, Third-place, Final}
- `goal_diff = team1_goals − team2_goals`
- rest days: for each team, days since their previous tournament match; **first match of the tournament** has no prior match, so it is filled with the **median rest among observed gaps** (5 days)
- difference features for model 2.1 (`rank_diff`, `value_diff`, …)
- two rows per match for model 2.2 (one per side)

### 3.6 Sampling, tests, models, charts, slides

1. Four Objective 1 tasks: SRS without replacement, seed **42**, describe, 95% t-interval, t-test after Levene
2. Two OLS models: 80/20 hold-out, seed 42, VIF, Shapiro–Wilk on residuals
3. Matplotlib charts embedded as PNG in `wc2026_report.html`
4. Those same report images extracted onto slides 3–5 of `WC2026_Presentation.pptx`

That is the finished product they have in front of them.

---

## 4. Objective 1 — four tasks (this is the core of Assignment 2)

Common settings: **α = 0.05**, **seed 42**, **simple random sample without replacement**. Levene’s test first: if Levene p > 0.05 we used the **pooled** two-sample t (equal variances); if Levene p < 0.05 we used **Welch**.

### Task 1 — Discipline (non-significant)

**Question:** Do midfielders pick up more yellow cards **per appearance** than defenders?

**Why per appearance, not total yellows?** Otherwise players who played more matches inflate the count. A substitute with one yellow in one game would look “cleaner” than a starter with two yellows in seven games, which is the wrong comparison.

- Population: **319 MF**, **345 DF** (appearances ≥ 1)
- Sample: **n = 45** each
- Means: MF **0.098**, DF **0.131** cards/appearance
- SD: 0.196 vs 0.213
- 95% CI for MF mean: **(0.039, 0.157)**
- Levene p = **0.45** → pooled t, df = **88**
- t = **−0.76**, p = **0.45**, Cohen’s d = **−0.16** (small)
- **Fail to reject H₀:** μ_MF = μ_DF

Spoken takeaway: *The “midfield battle gets booked more” story is not in this sample. Defenders were slightly higher, but it is noise.*

### Task 2 — Attendance (non-significant)

**Question:** Is mean attendance different in knockout vs group stage?

- Population: **72 group**, **32 knockout**
- Sample: **stratified equal allocation** — **census of all 32 knockout** matches plus SRS of **32 of 72** group matches
- Why census the knockout half? Only 32 exist; sampling them would throw away a small complete group. Equal n keeps the t-test balanced.
- Means: group **65,747**, knockout **67,701** (about 2,000 fans)
- Levene p = **0.94** → pooled t, df = **62**
- t = **0.88**, p = **0.38**, d = **0.22** (small)
- 95% CI for the combined sample mean: **(64,519, 68,928)**
- **Fail to reject H₀**

Spoken takeaway: *The expanded 48-team World Cup drew large crowds throughout. There is no significant knockout premium in this sample.*

### Task 3 — UEFA market value (significant, **one-sided**)

**Question:** Do UEFA squads carry a **higher** market value than non-UEFA squads?

- Population: **16 UEFA**, **32 non-UEFA**
- Sample: **n = 14** each (equal allocation; 14 is just under the UEFA census of 16 so we still demonstrate sampling)
- Means: UEFA **EUR 669.6m**, non-UEFA **EUR 257.2m** (about **2.6×**)
- H₀: μ_UEFA = μ_non  H₁: μ_UEFA **>** μ_non
- Levene p = **0.13** → pooled t, df = **26**
- t = **2.87**, **one-sided p = 0.0041**, d = **1.08** (large)
- 95% CI for UEFA mean: **(406.2m, 932.9m)**
- **Reject H₀**

**Why one-sided?** The question is directional, and the football-economy story is directional (Europe’s club transfer market). A two-sided test would still have been significant (2 × 0.0041 = 0.0082 < 0.05), so the decision is not an artefact of the tail. Say that if they push.

### Task 4 — Goalkeeper age (significant)

**Primary question:** Is mean GK age different from **27** (outfield “prime” benchmark)?

**Support:** two-sample GK vs outfield.

- Population: **66 GK**, **950** outfield
- Sample: **n = 40** each
- GK mean **30.33** (SD 4.95); outfield mean **26.68** (SD 3.69)
- 95% CI for GK mean: **(28.74, 31.91)** — the interval does **not** contain 27, which already agrees with the test
- One-sample vs 27: t(**39**) = **4.25**, p = **0.0001**, d = **0.67**
- Two-sample: Levene p = **0.040** → **Welch**, t(**72.1**) = **3.74**, p = **0.0004**, d = **0.84**
- **Reject H₀** both times

Spoken takeaway: *Keepers are older. Mexico’s Ochoa featured at 40. That is a career-length difference, not a one-year blip.*

**Why 27?** It is a conventional outfield peak-age benchmark, not a FIFA official number. If they dislike the constant, point to the two-sample test against actual outfield teammates — that does not depend on 27.

---

## 5. Objective 2 — two pre-kickoff linear models

**Design rule you must say out loud:** every predictor was knowable **before kickoff**. No shots, possession, xG, cards in that match, or in-match events. Using those would be leakage: you would be “predicting” a result with information that only exists after the match is underway.

80/20 hold-out, `random_state=42`, OLS with intercept, VIF on the design matrix, Shapiro–Wilk on training residuals.

### 2.1 Goal difference (n = 104 matches)

Target: `goal_diff = team1_goals − team2_goals`

Predictors (8):

| Variable | Meaning |
|----------|---------|
| rank_diff | FIFA rank team1 − team2 (**lower rank number = stronger**) |
| age_diff | squad average-age difference |
| value_diff | squad market value, EUR m, team1 − team2 |
| titles_diff | prior World Cup titles difference |
| host_diff | host indicator difference ∈ {−1, 0, 1} |
| rest_diff | rest-days difference |
| same_confed | 1 if same confederation |
| knockout | 1 if knockout stage |

- Train **83** / test **21**
- Train R² **0.493**, adj. R² **0.438**
- Test R² **0.306**, RMSE **1.57**, MAE **1.18** goals
- Max VIF (excl. intercept) **3.30** (value_diff) — no multicollinearity problem (concern is VIF > 5 or 10)
- Shapiro–Wilk p = **0.937** — residuals look normal
- Durbin–Watson **2.11** — no leftover autocorrelation

Significant at α = 0.05:

- **rank_diff = −0.0232**, p = **0.002**
- **value_diff = +0.0017**, p = **0.004**

Marginal: knockout **−0.73**, p = **0.097** (knockouts trend tighter).

**Interpret rank_diff carefully.** Rank 1 is better than rank 20. If team1 is stronger, rank_diff is **negative**. The coefficient is negative, so a negative rank_diff pushes predicted goal_diff **up**. In words: *the better-ranked side is expected to win by more*.

**Interpret value_diff:** +0.0017 net goals per EUR million. A **EUR 1 billion** squad-value edge ≈ **+1.7** net goals, holding rank fixed.

### 2.2 Team goals (n = 208 = 2 rows per match)

Target: goals scored by **that** team in **that** match.

Predictors (8): team_rank, opp_rank, team_value, opp_value, team_age, is_host, rest_days, knockout.

- Train **166** / test **42**
- Train R² **0.290**, adj. R² **0.254**
- Test R² **0.221**, RMSE **1.23**, MAE **0.89**
- Max VIF **2.64**
- Shapiro–Wilk p = **0.034** — mild non-normality, expected for a small count

Significant:

- **opp_rank = +0.0128**, p = **0.038** — weaker opponent (higher rank number) → more goals
- **team_value = +0.0007**, p = **0.035** — richer squad → more goals

Marginal: team_rank p = 0.067, is_host p = 0.085, rest_days p = 0.073 (**negative** — likely a scheduling confound, not “more rest hurts”; do not over-claim).

Why is R² lower than 2.1? Predicting one team’s **absolute** tally is noisier than predicting the **difference** between two sides. 0–0 and 2–2 are different in 2.2 and identical in 2.1.

**Poisson / negative binomial:** OLS was used because the brief asked for linear regression and because coefficients stay in “goals per unit of X” units. Goals are a non-negative count, so a Poisson GLM is the natural extension. That is the sentence on slide 5. If they ask what you would do next, say: *refit 2.2 as Poisson, keep the same eight pre-match predictors, compare AIC and residual plots.*

**Independence caveat (smart answer):** the 208 rows are not fully independent — two rows share a match. That can understate standard errors. 2.1 (one row per match) does not have that problem. If they want a limitation, this is a good one.

---

## 6. Theory they are likely to ask

Memorise the **meaning**, not a textbook paragraph.

### Hypothesis test

- H₀: the sceptical default (no difference / mean = 27 / UEFA = non-UEFA)
- H₁: what the question claims
- α = 0.05: we accept a 5% Type I error rate (rejecting a true H₀)
- Type II: failing to reject a false H₀. We did not compute power; with n = 14 in Task 3 we still saw a large effect, so power was adequate there. Tasks 1–2 had small d, so a real tiny difference could exist and we would miss it.

### p-value (say this exactly)

> The p-value is the probability of seeing a result at least this extreme **if H₀ were true**. It is not the probability that H₀ is true, and it is not the probability that we made a mistake.

### Fail to reject vs accept

> We fail to reject H₀. That means the data are compatible with no difference. It does not prove the means are equal.

### Confidence interval

Mean ± t* × (s / √n), df = n − 1, t* from the t table at 95%.

If a 95% CI for a mean difference contains 0, a two-sided t-test at 5% will fail to reject. If the Task 4 CI for GK age is (28.7, 31.9), 27 is outside it, so the one-sample test rejects.

### t-test assumptions

1. Independent observations (we sampled without replacement from disjoint groups)
2. The sampling distribution of the mean is approximately normal — either the data are roughly symmetric or n is large enough (CLT). n = 45, 32, 40 are comfortable; n = 14 in Task 3 is smaller, which is why we mention the large effect size
3. For the **pooled** t: equal population variances. We **test that with Levene** rather than assuming it
4. Welch does **not** need equal variances; df are Satterthwaite (can be 72.1, not an integer)

### Why t, not z?

Population SD is unknown. We estimate it with sample s. That is the t distribution.

### Cohen’s d

(mean₁ − mean₂) / pooled SD. Roughly 0.2 small, 0.5 medium, 0.8 large. Report d so “significant” is not confused with “important.” Task 3 is both significant **and** large. Tasks 1–2 are neither.

### Why sample when we compiled the whole tournament?

Two honest reasons, both in the report:

1. The brief requires a **sampling technique**, not a census analysis
2. Equal group sizes keep the two-sample t balanced

We still inspected the full tables while wrangling. If they say “you should have used all 48 teams,” agree that a census is possible for Task 3, and say the sample result was large and significant so the conclusion is not a sampling fluke.

### SRS vs stratified

- Tasks 1, 3, 4: **SRS** inside each group, equal n
- Task 2: **stratified** (stage) with equal allocation, and a **census** of the smaller stratum

### OLS assumptions (for Objective 2)

Linearity; independent errors; constant variance; errors roughly normal for inference; no perfect collinearity.

We checked: VIF, Shapiro–Wilk, hold-out RMSE/MAE, predicted-vs-actual scatter. We did not run a full Breusch–Pagan write-up; if asked, that is a possible extra diagnostic.

### R² vs test R² vs adj. R² vs RMSE

- Train R²: share of **training** variance explained (can be optimistic)
- Adj. R²: penalises extra predictors
- Test R²: generalisation on unseen matches — the number to trust
- RMSE: typical size of a prediction error, in **goals**
- MAE: typical absolute error, less sensitive to one wild match

Drop from 0.49 train to 0.31 test on 2.1 is expected with n_test = 21. It is not a disaster; it is a reminder not to quote only training R².

### Why not include both rank and value only?

We pre-specified eight substantively motivated pre-match variables rather than p-hacking a subset. Rank and value survived; age, titles, host, rest, confederation mostly did not. That is a finding, not a failure.

---

## 7. Likely questions — spoken answers

Use these as scripts. Shorten on the day.

**Walk us through the project in two minutes.**  
Use the 30-second open plus: data in three tables; four tests; two models; two non-results; UEFA value and GK age significant; rank and value predict goal difference.

**Why these four questions?**  
Each uses a different grain and a different test flavour: player rate (two-sample), match attendance (stratified two-sample), team value (one-sided two-sample), player age (one-sample plus supporting two-sample). Together they cover the six required skills four times, not once.

**Why seed 42?**  
Reproducibility. Anyone running `wc2026_analytics.py` against `fifa data.xlsx` gets the same samples and the same p-values.

**What would change if you used the full population for Task 1?**  
Means would be computed on 319 vs 345 instead of 45 vs 45. We would no longer be demonstrating sampling. We would still expect a small difference — the sample d is only −0.16.

**Why is Task 3 one-sided but Task 1 two-sided?**  
Task 1’s popular claim could have gone either way (and the sample mean was actually higher for defenders). Task 3’s claim is “UEFA are more valuable,” which is one direction.

**Did you look at the data before choosing one-sided?**  
The *question* is one-sided. We did not flip the tail after seeing p. If they worry about that, mention the two-sided p would still be 0.008.

**Explain Levene in one sentence.**  
Levene tests whether the two groups have equal variances; that decides pooled t versus Welch.

**What is df = 72.1?**  
Welch’s approximation. Variances of GK and outfield age differed (Levene p = 0.04), so we did not use n1+n2−2 = 78.

**Someone in the group: what does Cohen’s d = 1.08 mean?**  
The UEFA/non-UEFA gap is about 1.08 pooled standard deviations — a large practical difference, not just a p-value.

**How do you know the data are real?**  
104 matches, 48 teams, 1,016 players; goals+OG = 308; 15 reds; Spain–Argentina final only; team names join cleanly.

**Why exclude in-match stats from the regressions?**  
They are not known before kickoff. Including shots would leak the outcome we are trying to predict from pre-match information.

**Why is rank_diff negative?**  
Better teams have smaller rank numbers. rank_diff = rank1 − rank2 is negative when team1 is stronger. Negative coefficient × negative gap → positive predicted goal difference for team1.

**Why rest_days negative in 2.2?**  
p = 0.07, not significant. First matches are imputed at the median. Knockout vs group scheduling also sits in the model. We would not claim “rest reduces goals.”

**Why not logistic regression for win/lose?**  
The brief asked for linear models of a numeric outcome. Goal difference keeps the margin, not just the winner.

**Independence in 2.2?**  
Two rows per match. Limitation. Model 2.1 avoids it.

**What are the main limitations?**  
(1) Sampling on purpose rather than census. (2) Transfermarkt snapshots. (3) OLS on a count in 2.2; Poisson next. (4) 208 rows not independent. (5) n_test = 21 is small. (6) Assists were too messy to analyse.

**If you had one more week?**  
Poisson for 2.2; residual-vs-fitted plots; maybe cluster-robust SEs by match; census sensitivity check for Task 3.

**What does the HTML report add beyond the slides?**  
Full CIs, Levene p-values, coefficient tables, embedded charts, and the exact pipeline. The slides are the briefing; `wc2026_analytics.py` is the source of truth.

---

## 8. Numbers to know cold

If you remember nothing else, remember these.

| Item | Number |
|------|--------|
| Matches / teams / players | 104 / 48 / 1,016 |
| Champion | Spain 1–0 Argentina AET, 19 July 2026, MetLife |
| Goals | 294 player + 14 OG = 308 |
| Red cards | 15 |
| α / seed | 0.05 / 42 |
| T1 | n=45, 0.098 vs 0.131, p=0.45, d=−0.16, fail to reject |
| T2 | n=32+32, 65,747 vs 67,701, p=0.38, d=0.22, fail to reject |
| T3 | n=14, 670m vs 257m, **one-sided p=0.004**, d=1.08, reject |
| T4 | n=40, GK 30.3 vs 27, p=0.0001, d=0.67, reject |
| 2.1 | train R² 0.49, test R² 0.31, RMSE 1.57; rank_diff & value_diff |
| 2.2 | train R² 0.29, test R² 0.22, RMSE 1.23; opp_rank & team_value |
| EUR 1bn value edge | ≈ +1.7 net goals |
| Max VIF | 3.30 and 2.64 |
| Shapiro | 0.94 (2.1 OK) / 0.034 (2.2 mild) |

---

## 9. The night before — 45 minutes

1. Read section 1 so nobody panics about Assignment 3 in the meeting.
2. Each person explains **one** Objective 1 task out loud, including H₀, sample, p, decision.
3. One person explains rank_diff’s **sign**. One person explains why shots were banned.
4. One person explains fail-to-reject without saying “the means are equal.”
5. Agree the 30-second opening and who says it.
6. Confirm Saturday 12:00, camera, whose screen if they want the HTML, and that **everyone talks**.

You already have the work. Tomorrow is showing that you understand it.
