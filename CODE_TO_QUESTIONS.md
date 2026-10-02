# Question → code map (say this in the viva)

File: `wc2026_analytics.py`. One script, three Excel sheets (`matches`, `teams`, `players`), four Objective 1 questions.

**How to talk:** “Each task is one function. Shared helpers do the cleaning, the CI, and the t-test. `main()` runs them in order.”

```
fifa data.xlsx
   matches 104  →  load_matches()  →  task2_attendance()
   teams    48  →  load_teams()    →  task3_value()
   players 1016 →  load_players()  →  task1_discipline() + task4_age()
                                              ↓
                                    describe / ci_mean / t-test / Levene
                                              ↓
                                    HTML report (H₀, numbers, chart)
```

Do not walk Objective 2 unless they ask. If they do: `build_goal_diff` / `build_team_goals` / `fit_ols` — skip for Assignment 2.

---

## Shared tools (every question uses these)

| If they ask | Function | What to say |
|-------------|----------|-------------|
| Seed / reproducibility | `SEED = 42` | Same sample every run. |
| Cleaning names | `canon()` | USA, Turkiye, Ivory Coast… one spelling so tables join. |
| Missing / types | `load_*` + `dropna()` inside helpers | Coerce numbers; dropna is a safety net on the test column. |
| Sampling | `srs()` | SRS **without replacement**, seed 42. |
| Describe | `describe()` | n, mean, median, SD, min/max, quartiles, skew. |
| 95% CI | `ci_mean()` | x̄ ± t* × (s/√n). |
| Two-sample t | `two_sample_ttest()` | scipy `ttest_ind`; Levene decides pooled vs Welch. |
| One-sample t | `one_sample_ttest()` | Task 4 only, vs 27. |
| Equal variance | `levene_p()` | `equal_var = (lev > 0.05)`. |
| Decision | `verdict()` | Reject H₀ if p < 0.05, else fail to reject. |

**Levene line you must be able to point at:**

`equal_var=lev > 0.05`  
If Levene p > 0.05, variances look equal → pooled t. If not → Welch.

---

## Task 1 — `task1_discipline(players)`

**Question:** Do midfielders pick up more yellow cards **per appearance** than defenders?

**H₀:** μ_MF = μ_DF  **H₁:** μ_MF ≠ μ_DF  two-sided

**Sheet:** `players`

| Skill | Code | Say |
|-------|------|-----|
| Wrangle | `load_players`: keep appearances ≥ 1; `cards_per_app = yellows / appearances` | Rate, not totals, so a 7-match player is fair vs a substitute. |
| Filter | keep position DF or MF | FW/GK out of this question. |
| Sample | `srs(..., 45)` twice | n = 45 per group, seed 42. |
| Describe | `describe(cards_per_app)` | Means 0.098 vs 0.131; median 0 (skew). |
| CI | `ci_mean(mf["cards_per_app"])` | 95% CI for the MF mean. |
| Test | Levene then two-sample t, default two-sided | p = 0.45 → fail to reject. |
| Chart | two histograms | Shows the pile of zeros. |

**Spoken:** *The question is a two-group mean comparison. The function samples 45 MF and 45 DF, checks variance with Levene, then runs a two-sample t on cards per appearance.*

---

## Task 2 — `task2_attendance(matches)`

**Question:** Is mean attendance different in knockout vs group stage?

**H₀:** μ_KO = μ_group  **H₁:** μ_KO ≠ μ_group  two-sided

**Sheet:** `matches`

| Skill | Code | Say |
|-------|------|-----|
| Wrangle | `load_matches`: `knockout = stage in KNOCKOUT_STAGES` | 72 group, 32 knockout. |
| Sample | full `ko_pop.copy()` + SRS 32 of group | Stratified equal allocation; census of the small stratum. |
| Describe | `describe(attendance)` | ~65,747 vs ~67,701. |
| CI | `ci_mean` on the **combined** 64 matches | 95% CI for overall mean attendance. |
| Test | Levene then two-sample t | p = 0.38 → fail to reject. |
| Chart | box plot | Two stages side by side. |

**Spoken:** *We did not sample knockout matches — there are only 32, so we used all of them, and sampled 32 group matches so the t-test is balanced.*

---

## Task 3 — `task3_value(teams)`

**Question:** Do UEFA squads carry a **higher** market value than non-UEFA?

**H₀:** μ_UEFA = μ_non  **H₁:** μ_UEFA **>** μ_non  **one-sided**

**Sheet:** `teams`

| Skill | Code | Say |
|-------|------|-----|
| Wrangle | `is_uefa = (confederation == "UEFA")` | 16 vs 32. |
| Sample | `n = min(14, ...)` then `.sample` | Equal n = 14 (just under UEFA census of 16). |
| Describe | mean value EUR m | 670 vs 257. |
| CI | `ci_mean` on UEFA sample | CI for the UEFA mean. |
| Test | `alternative="greater"` | This is the only one-sided test. p = 0.004 → reject. |
| Chart | box plot | UEFA vs rest. |

**Spoken:** *`alternative="greater"` is why this p-value is one-sided. The question was directional before we saw the sample.*

---

## Task 4 — `task4_age(players)`

**Question:** Is mean GK age different from **27**? Support: GK vs outfield.

**H₀:** μ_GK = 27  **H₁:** μ_GK ≠ 27  two-sided one-sample  
Support: μ_GK = μ_outfield

**Sheet:** `players`

| Skill | Code | Say |
|-------|------|-----|
| Wrangle | `position == "GK"` vs DF/MF/FW | 66 vs 950. |
| Sample | `srs(..., 40)` each | n = 40. |
| Describe | `describe(age)` | GK 30.3 vs OF 26.7. |
| CI | `ci_mean(gk["age"])` | (28.74, 31.91) — 27 is outside. |
| Primary test | `one_sample_ttest(..., popmean=27)` | t(39) = 4.25, p = 0.0001 → reject. |
| Support | Levene then two-sample t | Levene p = 0.04 → Welch, df = 72.1. |
| Chart | box plot + dashed line at 27 | The benchmark is visible. |

**Spoken:** *Primary test is one-sample against a number, 27. The two-sample vs outfield does not depend on that benchmark.*

---

## Cleaning and missing — point here, not at the t-tests

`load_matches` / `load_teams` / `load_players`:

- `canon()` — name variants  
- `to_numeric(..., errors="coerce")` — bad strings become NaN then dropna in helpers  
- `appearances >= 1` — unused squad names out  
- `fillna(0)` on yellows — real zeros, safety net  
- `drop_duplicates("team")`  
- `assert len(matches)==104` and `len(teams)==48` in `main()` — row-count error check  

Structural blanks (`group` on knockout matches, `penalty_winner` when no pens) are **not** used in these four functions.

---

## `main()` — the story in four calls

```
load matches / teams / players
task1_discipline(players)   ← yellows
task2_attendance(matches)   ← crowds
task3_value(teams)          ← UEFA value
task4_age(players)          ← GK age
write HTML
```

If they open the script, start at `main()`, then jump to the `task*_` function for the question they asked.
