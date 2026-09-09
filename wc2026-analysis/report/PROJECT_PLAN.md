# FIFA World Cup 2026 — Project Plan

## Context

The 2026 FIFA World Cup (Canada / Mexico / USA) ran from 11 June to 19 July
2026 with an expanded 48-team, 104-match format (12 groups of 4, then Round
of 32, Round of 16, quarter-finals, semi-finals, third-place match, and
final). Spain beat Argentina 1–0 (a.e.t.) in the final at MetLife Stadium on
19 July 2026 to win their second title.

All data used here is real, tournament data compiled from public sources
(FIFA.com, Wikipedia, fbref.com, Transfermarkt, thestatsdontlie.com, and
contemporaneous match reports). Raw compiled extracts live in
`data/raw/`; cleaned, analysis-ready tables live in `data/processed/`.

## Objective 1 — Four distinct analytic tasks

Each task below is built on the six required skills (question formulation,
data wrangling, data preparation & sampling, descriptive statistics,
confidence interval, and a one-/two-sample t-test), and each has a distinct
focal point:

| # | Notebook | Focal point | Data used |
|---|----------|-------------|-----------|
| 1 | `01_discipline_cards.ipynb` | Player discipline (yellow cards) | `players_raw.csv` |
| 2 | `02_attendance.ipynb` | Match-day attendance | `matches_raw.csv` |
| 3 | `03_squad_market_value.ipynb` | Squad market value by confederation | `teams_raw.csv` |
| 4 | `04_player_age.ipynb` | Player age by position | `players_raw.csv` |

1. **Discipline** — Do midfielders average more yellow cards per appearance
   than defenders? (two-sample t-test on cards/appearance; CI for the
   population mean cards/appearance of midfielders.)
2. **Attendance** — Is average attendance at knockout-stage matches
   significantly different from group-stage matches? (two-sample t-test;
   CI for mean attendance across all 104 matches.)
3. **Squad market value** — Do UEFA (European) squads carry a significantly
   higher market value than non-UEFA squads? (two-sample t-test; CI for
   mean UEFA squad value.)
4. **Player age** — Are goalkeepers who appeared in the tournament
   significantly older, on average, than a reference age of 27? (one-sample
   t-test; CI for mean goalkeeper age.) A secondary two-sample comparison
   (GK vs. outfield) is also included for robustness.

## Objective 2 — Two linear regression tasks

### 2.1 Goal-difference model (104 rows = 1 per match)

Target: `goal_diff = team1_goals - team2_goals`.

Eight pre-match explanatory variables (none derived from in-match events):

1. `rank_diff` — FIFA ranking position difference (team1 − team2; lower rank number = better)
2. `age_diff` — squad average-age difference
3. `value_diff` — squad market-value difference (EUR m)
4. `titles_diff` — prior World Cup titles difference
5. `host_diff` — host-nation indicator difference (∈ {-1,0,1})
6. `rest_diff` — rest-days-before-match difference
7. `same_confed` — 1 if both teams share a confederation, else 0
8. `knockout` — 1 if match is in the knockout stage, else 0 (group stage = 0)

### 2.2 Team-goals model (208 rows = 2 per match, one per team)

Target: `goals` scored by that team in that match.

Eight pre-match explanatory variables:

1. `team_rank` — team's own FIFA ranking position
2. `opp_rank` — opponent's FIFA ranking position
3. `team_value` — team's squad market value (EUR m)
4. `opp_value` — opponent's squad market value (EUR m)
5. `team_age` — team's squad average age
6. `is_host` — 1 if team is a co-host nation, else 0
7. `rest_days` — days since the team's previous tournament match (first match uses tournament-median rest)
8. `knockout` — 1 if match is in the knockout stage, else 0

All derived fields (`rank_diff`, `rest_days`, `knockout`, etc.) are computed
in `src/data_prep.py` from the three raw tables so that every explanatory
variable is verifiably known before kickoff.
