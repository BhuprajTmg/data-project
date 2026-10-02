# Viva cheat sheet — print this

Saturday 3 Oct 2026, 12:00 pm · 20 min · everyone speaks · marks after the interview

**Do not email a confession about Objective 2.** If asked why regressions are in A2: *Obj1 is complete; Obj2 uses the same three tables and explains Task 3’s value gap. If Obj2 is A3 we can deepen it there.* If not asked, do not raise it.

**30-second open:** 104 matches, 48 teams, 1,016 players. Four inferential tasks + two pre-kickoff linear models, α = 0.05, seed 42. Two questions non-significant; UEFA value and GK age significant. Ranking gap and squad value are the robust predictors.

---

## Data

| | |
|--|--|
| Tournament | CAN/MEX/USA, 11 Jun–19 Jul 2026, 48 teams, 104 matches |
| Final | Spain 1–0 Argentina AET, MetLife, 19 Jul 2026 |
| Tables | matches 104 · teams 48 · players 1,016 (≥1 appearance) |
| Sources | FIFA match centre, Wikipedia, fotmob, Transfermarkt, FIFA rank **11 Jun 2026** |
| QA | 294 goals + 14 OG = **308** · reds **15** · all 104 attendances official |
| Joins | every team name canonicalised; no unmatched teams |
| Rejected fake | Argentina (Grp J) vs Spain (Grp H) never met in groups — only the final |
| Hosts | Mexico, Canada, USA |
| UEFA / others | 16 / 32 (CAF 10, AFC 9, CONCACAF 6, CONMEBOL 6, OFC 1) |
| Positions | DF 345, MF 319, FW 286, GK 66 |

Pipeline: scrape/merge → clean names → derive cards/app, knockout, rest days, diffs → sample & t-tests → OLS 80/20 → HTML charts → PowerPoint.

Rest days: days since that team’s previous match; first match filled with **median rest = 5**.

---

## Objective 1 (α = 0.05, seed 42, SRS without replacement)

Levene p > 0.05 → pooled t. Levene p < 0.05 → Welch.

### T1 Discipline — fail to reject
Do MF get more yellows **per appearance** than DF?  
Pop 319 / 345 → n=45 / 45  
Means 0.098 vs 0.131 · CI_MF (0.039, 0.157)  
Levene 0.45 → pooled, t(88)= −0.76, **p=0.45**, d= −0.16  
*Per appearance so 7-match finalists comparable to 1-match substitutes.*

### T2 Attendance — fail to reject
Knockout vs group attendance?  
Pop 72 group / 32 KO → **census 32 KO + SRS 32 group**  
Means 65,747 vs 67,701 · combined CI (64,519, 68,928)  
Levene 0.94 → pooled, t(62)= 0.88, **p=0.38**, d= 0.22  

### T3 UEFA value — reject (one-sided)
Is μ_UEFA **>** μ_non?  
Pop 16 / 32 → n=14 / 14  
Means **669.6m vs 257.2m** (~2.6×) · CI_UEFA (406, 933)  
Levene 0.13 → pooled, t(26)= 2.87, **p=0.0041**, d= 1.08  
Two-sided would be ~0.008 — still significant.

### T4 GK age — reject
Is μ_GK ≠ 27? Support: GK vs outfield.  
Pop 66 / 950 → n=40 / 40  
GK 30.33 (SD 4.95) vs OF 26.68 · CI_GK **(28.74, 31.91)** — 27 not inside  
One-sample t(39)= 4.25, **p=0.0001**, d= 0.67  
Welch (Levene 0.04) t(72.1)= 3.74, **p=0.0004**, d= 0.84  

---

## Objective 2 — pre-match only (no shots / possession / in-match)

80/20 hold-out, seed 42, OLS.

### 2.1 Goal difference · n=104 · train 83 / test 21
Target: team1 − team2 goals  
X: rank_diff, age_diff, value_diff, titles_diff, host_diff, rest_diff, same_confed, knockout  
Train R² **0.493** adj **0.438** · test R² **0.306** · RMSE **1.57** · MAE **1.18**  
Max VIF **3.30** · Shapiro **0.94** · DW 2.11  
**rank_diff −0.0232 (p=0.002)** · **value_diff +0.0017 (p=0.004)**  
Knockout −0.73 (p=0.097) marginal.  
EUR 1bn value edge ≈ **+1.7 net goals**.  
Rank: *smaller number = stronger*. Negative rank_diff (team1 better) × negative coef → team1 predicted to outscore.

### 2.2 Team goals · n=208 · train 166 / test 42
Target: that team’s goals  
X: team_rank, opp_rank, team_value, opp_value, team_age, is_host, rest_days, knockout  
Train R² **0.290** adj **0.254** · test R² **0.221** · RMSE **1.23** · MAE **0.89**  
Max VIF **2.64** · Shapiro **0.034** (count data — Poisson next)  
**opp_rank +0.0128 (p=0.038)** · **team_value +0.0007 (p=0.035)**  
Limitation: two rows/match are not independent.

---

## Theory one-liners

- **p-value:** P(data this extreme or more | H₀ true). Not P(H₀ true).
- **Fail to reject ≠ H₀ is true.** Data are compatible with no difference.
- **t not z:** σ unknown, estimated by s.
- **Cohen d:** 0.2 small / 0.5 medium / 0.8 large.
- **Why sample a compiled census?** Brief requires sampling; equal n; results still line up with the story.
- **Why no in-match X?** Leakage — not knowable before kickoff.
- **OLS on goals:** brief asked for linear; Poisson is the natural extension for 2.2.
- **Type I:** false reject (α=0.05). **Type II:** miss a real effect (Tasks 1–2 have small d, so possible).

---

## If you freeze

Say the **decision and the direction**, not a fake digit.  
“p was well above 0.05, small effect, fail to reject.”  
“p was about 0.004, large d, we reject — UEFA more valuable.”
