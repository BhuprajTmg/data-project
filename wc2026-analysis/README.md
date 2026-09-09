# FIFA World Cup 2026 Analytics

A statistics and linear-regression project built on real match, team, and
player data from the 2026 FIFA World Cup (Canada / Mexico / USA,
11 June – 19 July 2026, won by Spain).

## Structure

```
wc2026-analysis/
├── data/
│   ├── raw/          # Compiled extracts from FIFA.com, Wikipedia, fbref.com, Transfermarkt
│   └── processed/    # Cleaned tables + the two regression-ready datasets
├── notebooks/
│   ├── 01_discipline_cards.ipynb          # Objective 1, Task 1
│   ├── 02_attendance.ipynb                # Objective 1, Task 2
│   ├── 03_squad_market_value.ipynb        # Objective 1, Task 3
│   ├── 04_player_age.ipynb                # Objective 1, Task 4
│   ├── 05_regression_goal_difference.ipynb# Objective 2.1
│   └── 06_regression_team_goals.ipynb     # Objective 2.2
├── src/
│   ├── data_prep.py     # Loading, cleaning, feature engineering (single source of truth)
│   └── stats_utils.py   # Descriptive stats, CI, one-/two-sample t-test helpers
├── report/
│   ├── PROJECT_PLAN.md  # Design rationale for every task and variable
│   ├── REPORT.md        # Final write-up of methodology & findings
│   └── figs/            # Exported charts referenced by REPORT.md
└── requirements.txt
```

## Running it

```bash
pip install -r requirements.txt
cd src && python data_prep.py   # rebuilds data/processed/*.csv from data/raw/*.csv
cd ../notebooks && jupyter notebook
```

Run notebooks in numeric order. `01`–`04` cover Objective 1 (four distinct
analytic tasks); `05`–`06` cover Objective 2 (the two linear regression
models). See `report/PROJECT_PLAN.md` for the design rationale behind every
question and variable, and `report/REPORT.md` for the full write-up of
results.

## Data provenance

All data is real and describes the actual, completed 2026 FIFA World Cup.
It was compiled from:

- FIFA's official site (match centre results & statistics)
- Wikipedia's 2026 FIFA World Cup articles (schedule, groups, knockout stage)
- fbref.com (player/team match statistics)
- Transfermarkt (squad market values)
- thestatsdontlie.com and contemporaneous match reports (cross-checks)

See `data/raw/*.csv` for the compiled tables and `report/REPORT.md` for
notes on data quality / any estimated fields.
