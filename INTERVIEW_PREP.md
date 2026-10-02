# HIT140 viva pack — Objective 1 only

Saturday 3 Oct 2026, 12:00 pm · 20 minutes · all group members speak · marks after the interview

Study **`INTERVIEW_THEORY.md`** if he is theory-heavy. Keep **`INTERVIEW_CHEATSHEET.md`** open during the call. This file is the four-task walkthrough.

Assignment 2 is the four inferential tasks. Each task walks the same six skills: **question → wrangle → sample → describe → 95% CI → t-test**, at **α = 0.05**, **seed 42**. That is what they will examine. Do not study the regressions.

If a slide with Objective 2 appears and they do not ask about it, ignore it. If they ask why it is there: *Objective 1 is complete in full; the regressions were extra on the same dataset.* Then go back to the four tasks.

---

## How to run the 20 minutes

Every person must be able to explain **any** of the four tasks. Suggested lead roles (swap names tonight):

| Role | Lead | Must also know |
|------|------|----------------|
| A — Data | how the three tables were compiled and checked | why players need ≥1 appearance |
| B — Tasks 1–2 | discipline + attendance (the two non-results) | what “fail to reject” means |
| C — Tasks 3–4 | UEFA value + GK age (the two rejections) | one-sided vs two-sided; one-sample vs two-sample |
| D — Method | sampling, Levene, Welch vs pooled, CI, Cohen’s d | why sample instead of using the full census |

**30-second open** (one person, then wait for questions):

> We compiled 104 matches, 48 teams, and 1,016 players who featured at World Cup 2026. Objective 1 is four distinct questions, each with wrangling, a sample, descriptive statistics, a 95 percent confidence interval, and a t-test at alpha 0.05. Two questions came back non-significant: midfielder versus defender yellows, and knockout versus group attendance. Two were significant: UEFA squads are more valuable than non-UEFA squads, and goalkeepers are older than 27.

**Rules in the room**

- Answer the question asked, then stop.
- If you forget a digit, give the **decision and the direction**: “p was about 0.45, well above 0.05, small effect, we fail to reject.” Guessing the wrong p is worse than rounding.
- “Fail to reject H₀” is **not** “H₀ is true” and **not** “there is no difference.”
- A p-value is **not** the probability that H₀ is true.
- If someone freezes, another member adds **one** sentence. Do not talk over each other.

If they ask about coding tools:

> We used tools to help with Python, charts, and slides. The questions, the sampling design, which test to run, one-sided versus two-sided, and how we read the p-values are our decisions. The numbers regenerate from `wc2026_analytics.py` and `fifa data.xlsx`.

Then prove it by explaining a decision (per-appearance cards, stratified attendance sample, one-sided UEFA test, why 27).

---

## Data used in Objective 1

Three independently compiled tables, then joined.

| Table | Grain | Rows | Used in |
|-------|--------|------|---------|
| matches | one official match | 104 | Task 2 |
| teams | one national team | 48 | Task 3 |
| players | one player with ≥1 appearance | 1,016 | Tasks 1 and 4 |

**Matches.** FIFA match centre, Wikipedia group and knockout pages, worldcup.org.uk. Fields include stage, teams, score, venue, **attendance**. All 104 attendances are official. None were guessed.

**Teams.** FIFA ranking 11 June 2026, Transfermarkt squad market value (EUR m) and average age, Wikipedia for confederation / host / titles. Split for Task 3: **16 UEFA** vs **32 non-UEFA** (CAF 10, AFC 9, CONCACAF 6, CONMEBOL 6, OFC 1). Hosts: Mexico, Canada, USA.

**Players.** Wikipedia squads (name, team, position GK/DF/MF/FW, age) merged with fotmob minutes and card leaderboards and Wikipedia goalscorers. A player with no verifiable appearance was dropped — the population is players who **featured**, not full 26-man lists.

Position counts: **DF 345, MF 319, FW 286, GK 66**.

**Cleaning.** Team names canonicalised so the three tables join (USA / United States, Turkiye / Turkey, Ivory Coast, Curacao, Czechia, DR Congo, …). After that, every team in matches and players maps to exactly one row in teams.

**Checks you should mention if they ask “is the data real?”**

- 294 player goals + 14 own goals = official **308**
- **15** red cards matches the official count
- Argentina were Group J, Spain Group H — they only met in the **final**. We did not invent a group-stage meeting.

**Honest caveats (Objective 1):** Transfermarkt values and ages are point-in-time snapshots; they can move a few percent with the pull date. Rankings, scores, attendance, confederations, and titles are unambiguous.

**Derived fields used in the four tests**

- `cards_per_app = yellow_cards / appearances` (Task 1)
- `knockout` = 1 if stage is Round of 32 through Final (Task 2). Group stage = 72 matches, knockout = 32
- `is_uefa` from confederation == UEFA (Task 3)
- `age` for GK vs the constant 27, and vs outfield DF/MF/FW (Task 4)

---

## The six skills (say this once, then apply it four times)

For every task we did the same loop:

1. **Question** — a population mean comparison, written as H₀ / H₁
2. **Wrangle** — restrict to the right rows, derive the variable
3. **Sample** — simple random sample **without replacement**, seed 42 (Task 2 is stratified)
4. **Describe** — n, mean, SD (median if useful)
5. **95% CI** for a mean, using the t distribution: mean ± t* × (s / √n)
6. **t-test** at α = 0.05, after **Levene** for two-sample tests

**Why sample when we compiled the whole tournament?** Two reasons, both honest:

1. The brief requires a **sampling technique**, not a census analysis
2. Equal group sizes keep the two-sample t balanced

We still inspected the full tables while wrangling.

**Why t, not z?** Population SD is unknown. We estimate it with sample s.

**Levene → which t-test**

- Levene p **> 0.05**: variances look equal → **pooled** (Student’s) t, df = n₁ + n₂ − 2
- Levene p **< 0.05**: variances differ → **Welch** t, df can be a decimal (Satterthwaite)

Tasks 1, 2, 3: pooled. Task 4 two-sample: Welch (df = 72.1).

---

## Task 1 — Player discipline (fail to reject)

**Question.** On average, do midfielders pick up more yellow cards **per appearance** than defenders?

**Why per appearance, not total yellows?** Otherwise players who played more matches inflate the count. A substitute with one yellow in one game would look “dirtier” than a starter with two yellows in seven games — the wrong comparison.

**Wrangle.** Keep players with ≥1 appearance. Keep positions MF and DF. `cards_per_app = yellow_cards / appearances`.

**Population.** 319 midfielders, 345 defenders.

**Sample.** SRS, n = **45** per position, seed 42, without replacement.

**H₀:** μ_MF = μ_DF  
**H₁:** μ_MF ≠ μ_DF (two-sided — the popular “midfield battle” claim could go either way, and in the sample defenders were actually slightly higher)

| | Midfielders | Defenders |
|--|-------------|-----------|
| n | 45 | 45 |
| Mean cards/app | **0.098** | **0.131** |
| SD | 0.196 | 0.213 |
| Median | 0 | 0 |

- 95% CI for MF mean: **(0.039, 0.157)**
- Levene p = **0.45** → pooled t, df = **88**
- t = **−0.76**, p = **0.45**, Cohen’s d = **−0.16** (small)
- **Fail to reject H₀** at α = 0.05

**Takeaway.** The midfield-booking story is not in this sample. Defenders were slightly higher; the gap is sampling noise.

**If they ask “so midfielders and defenders get the same cards?”**  
No. We failed to reject equality. A small real difference could exist (d is only −0.16). We do not have evidence of a difference.

**Chart on the slides.** Two histograms of cards per appearance.

---

## Task 2 — Match-day attendance (fail to reject)

**Question.** Is average stadium attendance significantly different between knockout and group-stage matches?

**Wrangle.** All 104 matches have reported attendance. `knockout` = 1 for Round of 32, Round of 16, QF, SF, third place, Final.

**Population.** 72 group, 32 knockout.

**Sample.** **Stratified equal allocation:** census of **all 32 knockout** matches + SRS of **32 of 72** group matches, seed 42.

**Why census the knockout half?** Only 32 exist. Sampling them would throw away a small complete group. Equal n keeps the t-test balanced.

**H₀:** μ_knockout = μ_group  
**H₁:** μ_knockout ≠ μ_group (two-sided — knockout crowds could have been larger or, in a 48-team tournament with huge group interest, not)

| | Group | Knockout |
|--|-------|----------|
| n | 32 | 32 |
| Mean | **65,747** | **67,701** |
| SD | 9,058 | 8,619 |

- 95% CI for the **combined sample** mean: **(64,519, 68,928)**
- Levene p = **0.94** → pooled t, df = **62**
- t = **0.88**, p = **0.38**, Cohen’s d = **0.22** (small)
- **Fail to reject H₀**

**Takeaway.** About 2,000 extra fans in knockout, not statistically significant. The expanded 48-team format drew large, comparable crowds throughout.

**If they ask “why CI for overall mean, not for the difference?”**  
The brief asks for a CI as one of the six skills. We reported a 95% CI for mean attendance on the sampled matches. The t-test is what compares the two stages.

**Chart.** Box plot, group vs knockout.

---

## Task 3 — UEFA squad value (reject, one-sided)

**Question.** Do UEFA squads carry a **significantly higher** market value than non-UEFA squads?

**Wrangle.** One Transfermarkt-valued squad per nation. Split 48 teams into UEFA vs everyone else.

**Population.** 16 UEFA, 32 non-UEFA.

**Sample.** Balanced SRS, n = **14** per group. 14 is just under the UEFA census of 16, so we still demonstrate sampling rather than using every European team.

**H₀:** μ_UEFA = μ_non-UEFA  
**H₁:** μ_UEFA **>** μ_non-UEFA  ← **one-sided**

| | UEFA | Non-UEFA |
|--|------|----------|
| n | 14 | 14 |
| Mean (EUR m) | **669.6** | **257.2** |
| SD | 456.0 | 286.1 |

- 95% CI for UEFA mean: **(406.2m, 932.9m)**
- Levene p = **0.13** → pooled t, df = **26**
- t = **2.87**, **one-sided p = 0.0041**, Cohen’s d = **1.08** (large)
- **Reject H₀**

**Why one-sided?** The question is directional, and the football-economy story is directional (Europe’s club transfer market). We did not flip the tail after seeing the means.

**If they worry you peeked:** a two-sided p would be 2 × 0.0041 ≈ **0.008**, still < 0.05. The decision is not an artefact of the one-sided tail.

**Why n = 14 not 16?** Equal allocation, and we wanted a sample not a UEFA census. The effect is large (d = 1.08), so the conclusion is not a small-sample fluke.

**Takeaway.** UEFA squads about **2.6×** as valuable. Significant and practically large.

**Chart.** Box plot, UEFA vs non-UEFA.

**Caveat.** Transfermarkt values move with the pull date. The gap is hundreds of millions of euros, so a few percent of snapshot noise does not change the rejection.

---

## Task 4 — Goalkeeper age (reject)

**Primary question.** Is the mean age of goalkeepers who appeared at the tournament significantly different from **27** (a conventional outfield “prime” benchmark)?

**Support.** Two-sample: GK vs outfield (DF / MF / FW).

**Wrangle.** Appearances ≥ 1. Split position == GK vs the three outfield positions.

**Population.** 66 goalkeepers, 950 outfield.

**Sample.** SRS, n = **40** per group, seed 42.

**One-sample**  
H₀: μ_GK = 27  
H₁: μ_GK ≠ 27 (two-sided)

**Two-sample**  
H₀: μ_GK = μ_outfield  
H₁: μ_GK ≠ μ_outfield

| | Goalkeepers | Outfield |
|--|-------------|----------|
| n | 40 | 40 |
| Mean age | **30.33** | **26.68** |
| SD | 4.95 | 3.69 |

- 95% CI for GK mean: **(28.74, 31.91)** — **27 is not inside the interval**, which already agrees with the test
- One-sample: t(**39**) = **4.25**, p = **0.0001**, d = **0.67**
- Two-sample: Levene p = **0.040** → **Welch**, t(**72.1**) = **3.74**, p = **0.0004**, d = **0.84**
- **Reject H₀** both times

**Why 27?** It is a conventional outfield peak-age benchmark, not a FIFA official number. If they dislike the constant, point to the two-sample test against actual outfield teammates — that does not depend on 27.

**Why Welch here but pooled elsewhere?** Levene p = 0.04, so GK age is more spread out than outfield age (SD 4.95 vs 3.69). Welch does not assume equal variances; df = 72.1 is Satterthwaite, not n₁+n₂−2 = 78.

**Takeaway.** Keepers are older than 27 and about **3.6 years** older than outfield teammates. Mexico’s Ochoa featured at 40. That is career length, not a one-year blip.

**Chart.** Box plot with a dashed line at 27.

---

## Theory they will ask (Objective 1 only)

### Hypotheses
H₀ is the sceptical default (no difference / mean = 27). H₁ is what the question claims. We never “accept H₀.” We reject it or we fail to reject it.

### p-value — say this exactly
> The p-value is the probability of seeing a result at least this extreme **if H₀ were true**. It is not the probability that H₀ is true, and it is not the probability that we made a mistake.

### Fail to reject vs “no difference”
Tasks 1 and 2: the data are compatible with no difference. A small real gap could still exist. Cohen’s d tells you the gap we saw was small (−0.16 and 0.22).

### Type I and Type II
- **Type I:** reject a true H₀. We set this risk at α = 0.05.
- **Type II:** fail to reject a false H₀. We did not compute power. Tasks 1–2 have small d, so a tiny real effect could have been missed. Task 3 has large d and still rejected with n = 14, so power was adequate there.

### Confidence interval
mean ± t* × (s / √n), df = n − 1 for a one-sample mean.

Link to the test: if a 95% CI for a mean difference contains 0, a two-sided t-test at 5% fails to reject. Task 4 CI (28.74, 31.91) does not contain 27, so the one-sample test rejects.

### t-test assumptions
1. Independent observations (SRS without replacement from disjoint groups)
2. Sampling distribution of the mean approximately normal — data not wildly skewed, or n large enough (CLT). n = 45, 32, 40 are comfortable; n = 14 in Task 3 is smaller, which is why we also report the large effect size
3. Pooled t needs equal variances — we **test that with Levene** rather than assuming it
4. Welch does not need equal variances

Independence note they might raise: two players from the same team are not fully independent. Honest limitation. We still sampled at player level because that is the grain of Tasks 1 and 4.

### Why not z?
σ unknown.

### Cohen’s d
(mean₁ − mean₂) / pooled SD. Roughly 0.2 small, 0.5 medium, 0.8 large.

| Task | d | Read it as |
|------|---|------------|
| 1 | −0.16 | small, and not significant |
| 2 | 0.22 | small, and not significant |
| 3 | 1.08 | large, and significant — this is a real practical gap |
| 4 vs 27 | 0.67 | medium–large |
| 4 vs outfield | 0.84 | large |

Do not say “significant means important.” Task 3 is both. Tasks 1–2 are neither.

### One-sided vs two-sided
Use one-sided only when the **question** is directional **before** seeing the sample. That is Task 3 only. Task 1 looked like a “midfielders get more cards” story, but we kept it two-sided because the opposite was plausible (and occurred in the sample).

### One-sample vs two-sample
- One-sample: one group versus a **number** (GK age vs 27)
- Two-sample: two groups versus **each other** (MF vs DF, knockout vs group, UEFA vs non-UEFA, GK vs outfield)

### SRS vs stratified
- Tasks 1, 3, 4: SRS **inside each group**, equal n
- Task 2: stratified by stage, equal allocation, census of the smaller stratum

### Seed 42
Reproducibility. Anyone running the script against the Excel file gets the same samples and the same p-values.

---

## Likely questions — spoken answers

**Walk us through Objective 1.**  
Four questions, six skills each, α = 0.05, seed 42. Two non-results (cards, attendance). Two rejections (UEFA value, GK age).

**Why these four questions?**  
Different grain (player / match / team / player), and different test flavours: two-sample two-sided, stratified two-sample, one-sided two-sample, one-sample plus a supporting two-sample.

**Why sample?**  
Required skill, and balanced n. Not because we lacked the population.

**What would change if you used all 319 midfielders?**  
We would be doing a census, not demonstrating sampling. We would still expect a small cards gap — sample d is only −0.16.

**Why Task 3 one-sided but Task 1 two-sided?**  
Task 3’s claim is “UEFA are more valuable,” one direction. Task 1 could go either way.

**Explain Levene in one sentence.**  
It tests equal variances and decides pooled t versus Welch.

**What is df = 72.1?**  
Welch’s approximation for Task 4, because GK and outfield age variances differed.

**What does d = 1.08 mean?**  
The UEFA/non-UEFA value gap is about 1.08 pooled standard deviations — large in practice, not just a small p.

**How do you know the data are real?**  
104 / 48 / 1,016; goals+OG = 308; 15 reds; Spain–Argentina final only; team names join.

**Why not compare total yellows?**  
Playing-time bias. We used cards per appearance.

**Why is failing to reject not proof of equality?**  
Absence of evidence is not evidence of absence. Small d and p >> 0.05 means we did not detect a difference.

**Main limitations?**  
(1) Sampling on purpose rather than census. (2) Transfermarkt snapshot values. (3) n = 14 in Task 3 is modest (offset by a large effect). (4) Players from the same squad are not fully independent. (5) 27 is a benchmark, not an official FIFA parameter — that is why we also compared GK to outfield.

**If you had more time on Objective 1?**  
Census sensitivity check for Task 3; bootstrap CIs as a robustness check; maybe cards per 90 minutes using the minutes column.

---

## Numbers to know cold

| Item | Number |
|------|--------|
| Matches / teams / players | 104 / 48 / 1,016 |
| Champion | Spain 1–0 Argentina AET, 19 July 2026, MetLife |
| α / seed | 0.05 / 42 |
| T1 | n=45, 0.098 vs 0.131, p=0.45, d=−0.16, fail to reject |
| T2 | n=32+32, 65,747 vs 67,701, p=0.38, d=0.22, fail to reject |
| T3 | n=14, 670m vs 257m, **one-sided p=0.004**, d=1.08, reject |
| T4 | n=40, GK 30.3 vs 27, p=0.0001, d=0.67, reject |

---

## Tonight — 40 minutes

1. Each person explains **one** task out loud: question, H₀/H₁, sample, mean, p, decision, one “why.”
2. Everyone says, once: “fail to reject does not mean the means are equal.”
3. Everyone says, once: “p is not the probability H₀ is true.”
4. One person explains Levene → pooled vs Welch using Task 4.
5. One person explains why Task 3 is one-sided.
6. Agree who says the 30-second open.

That is Assignment 2. Stay there.
