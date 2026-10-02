# Objective 1 cheat sheet — print this

Saturday 3 Oct 2026, 12:00 pm · 20 min · everyone speaks

Assignment 2 = **four inferential tasks**. Do not study the regressions. If they appear on a slide and nobody asks, ignore them.

**30-second open:** 104 matches, 48 teams, 1,016 players. Four questions, each with wrangle, sample, describe, 95% CI, t-test. α = 0.05, seed 42. Non-significant: MF vs DF yellows, knockout vs group attendance. Significant: UEFA squad value (one-sided), goalkeeper age vs 27.

---

## Data (only what Obj 1 uses)

| | |
|--|--|
| Tournament | CAN/MEX/USA, 11 Jun–19 Jul 2026 · Spain 1–0 Argentina AET, MetLife |
| Tables | matches 104 · teams 48 · players 1,016 (≥1 appearance) |
| Sources | FIFA match centre, Wikipedia, fotmob, Transfermarkt, FIFA rank 11 Jun 2026 |
| QA | 294 goals + 14 OG = 308 · 15 reds · all 104 attendances official |
| Positions | DF 345 · MF 319 · FW 286 · GK 66 |
| Confederations | UEFA 16 · CAF 10 · AFC 9 · CONCACAF 6 · CONMEBOL 6 · OFC 1 |

Pipeline: compile three tables → clean team names → derive cards/app, knockout flag, UEFA flag → **sample → describe → 95% CI → t-test**.

---

## Method (every task)

α = 0.05 · seed 42 · SRS **without replacement**  
Levene p > 0.05 → **pooled t** (df = n₁+n₂−2)  
Levene p < 0.05 → **Welch t** (df can be 72.1)

**Why sample a compiled census?** Brief requires sampling; equal n.  
**Why t not z?** σ unknown.  
**p-value:** P(data this extreme or more \| H₀ true). **Not** P(H₀ true).  
**Fail to reject ≠ means are equal.** Data are compatible with no difference.  
**Cohen d:** 0.2 small / 0.5 medium / 0.8 large.  
**Type I:** false reject (α=0.05). **Type II:** miss a real effect (possible in T1–T2; small d).

CI for a mean: mean ± t* × s/√n.

---

## Task 1 — Discipline · fail to reject

Do MF get more yellows **per appearance** than DF? (two-sided)  
Why per appearance: so 7-match finalists comparable to 1-match substitutes.  
Pop 319 MF / 345 DF → n=45 / 45  
Means **0.098 vs 0.131** · CI_MF **(0.039, 0.157)**  
Levene 0.45 → pooled · t(88)= **−0.76** · **p=0.45** · d= **−0.16**

---

## Task 2 — Attendance · fail to reject

Knockout vs group attendance? (two-sided)  
Pop 72 group / 32 KO → **census of 32 KO + SRS 32 group** (stratified equal allocation)  
Means **65,747 vs 67,701** (~2,000 fans) · combined CI **(64,519, 68,928)**  
Levene 0.94 → pooled · t(62)= **0.88** · **p=0.38** · d= **0.22**

---

## Task 3 — UEFA value · reject (one-sided)

H₁: μ_UEFA **>** μ_non  
Pop 16 / 32 → n=14 / 14  
Means **669.6m vs 257.2m** (~2.6×) · CI_UEFA **(406m, 933m)**  
Levene 0.13 → pooled · t(26)= **2.87** · **p=0.0041** · d= **1.08** (large)  
Two-sided p would be ~0.008 — still significant.  
Snapshot caveat: Transfermarkt values move a few percent; the gap is hundreds of millions.

---

## Task 4 — GK age · reject

Primary: μ_GK ≠ 27 (two-sided one-sample). Support: GK vs outfield.  
Pop 66 GK / 950 OF → n=40 / 40  
GK **30.33** (SD 4.95) vs OF **26.68** · CI_GK **(28.74, 31.91)** — 27 not inside  
One-sample t(39)= **4.25** · **p=0.0001** · d= **0.67**  
Welch (Levene 0.04) t(72.1)= **3.74** · **p=0.0004** · d= **0.84**  
27 is a conventional outfield-prime benchmark, not a FIFA official number.

---

## Theory traps (say these exactly)

**p-value:** P(result this extreme or more **if H₀ is true**). Not P(H₀ is true). Not effect size.

**95% CI:** if we repeated the sampling, 95% of such intervals would cover μ. This interval either contains μ or not — do not say “95% probability μ is inside.” Two-sided test at 5% rejects μ₀ iff μ₀ is outside the 95% CI (Task 4: 27 ∉ (28.74, 31.91)).

**Fail to reject ≠ accept H₀.** Compatible with no difference; a small real gap could be missed (Type II). Type I = false reject, rate α = 0.05.

**t not z:** σ unknown. t-test needs approx. normal **sampling distribution of the mean** (CLT), not normal raw data. Task 1 is right-skewed with median 0; n = 45 still OK for a mean.

**Levene:** equal-variance check. p > 0.05 → pooled t. p < 0.05 → Welch (Task 4 df = 72.1).

**One-sided only if the question is directional before seeing data** (Task 3). Two-sided p would still be ~0.008.

**Significant ≠ important.** Report Cohen’s d. T1/T2 small d; T3 d = 1.08 large.

**Not paired / not ANOVA / not chi-square:** two independent groups, numeric means.

**Bonferroni if asked:** α = 0.05/4 = 0.0125. T3 p = 0.004 and T4 p = 0.0001 still reject.

SE = s/√n (spread of the **mean**). SD = spread of **individuals**.  
One-sample t = (x̄ − μ₀) / (s/√n).

---

## If you freeze

Say **decision + direction**, not a fake digit.  
“p well above 0.05, small effect, fail to reject.”  
“one-sided p about 0.004, large d, reject — UEFA more valuable.”  
“p about 0.0001, keepers older than 27, reject.”
