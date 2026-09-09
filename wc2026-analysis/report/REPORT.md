# FIFA World Cup 2026 — Analytics Report

*Status: draft — descriptive/inferential and regression results below are
filled in after executing the notebooks in `notebooks/` against the
compiled real-world datasets in `data/raw/`.*

## 1. Data sources & compilation

| File | Rows | Grain | Primary sources |
|------|------|-------|------------------|
| `data/raw/matches_raw.csv` | 104 | one row per official match | FIFA.com match centre, Wikipedia, RSSSF, contemporaneous match reports |
| `data/raw/teams_raw.csv` | 48 | one row per national team | FIFA World Ranking, Wikipedia squad pages, Transfermarkt |
| `data/raw/players_raw.csv` | ~800 | one row per player with ≥1 appearance | fbref.com, FIFA.com statistics, Wikipedia |

All three tables describe the real, completed 2026 FIFA World Cup
(Canada/Mexico/USA, 11 June – 19 July 2026), won by Spain (1–0 over
Argentina in the final, after extra time). See `src/data_prep.py` for the
exact cleaning/normalisation logic and `report/PROJECT_PLAN.md` for why
each variable was chosen.

## 2. Objective 1 — Four analytic tasks

### Task 1 — Player discipline: yellow cards, midfielders vs. defenders

*(filled in from `notebooks/01_discipline_cards.ipynb`)*

### Task 2 — Match attendance: knockout vs. group stage

*(filled in from `notebooks/02_attendance.ipynb`)*

### Task 3 — Squad market value: UEFA vs. non-UEFA

*(filled in from `notebooks/03_squad_market_value.ipynb`)*

### Task 4 — Goalkeeper age profile

*(filled in from `notebooks/04_player_age.ipynb`)*

## 3. Objective 2 — Two linear regression models

### 2.1 — Goal-difference model (104 matches)

*(filled in from `notebooks/05_regression_goal_difference.ipynb`)*

### 2.2 — Team-goals model (208 team-match rows)

*(filled in from `notebooks/06_regression_team_goals.ipynb`)*

## 4. Limitations & notes on data quality

*(filled in — flags any estimated vs. directly-sourced figures, and any
methodological caveats.)*
