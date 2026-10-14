# HIT140 Assessment 3 — Objective 2

All analysis is **Python**. The group report and figures are **HTML + CSS**.

The Assessment 2 regressions are not reused. Each new model has four explanatory variables. Two are shared.

```
data/original/     original Excel workbook (raw storage only)
data/cleaned/      cleaned CSV tables from the Python cleaning script
code/clean_data.py cleaning and quality checks
code/analytics.py  two OLS models + SVG figures
docs/              HTML report (Times New Roman 12 pt)
```

## How to run

```
python code/clean_data.py
python code/analytics.py
python docs/generate_report.py
```

Word file (this is the Learnline report): `docs/HIT140_Assessment3_Group_Report.docx`

HTML copy: `docs/HIT140_Assessment3_Group_Report.html`

## Models

| Model | Target | Rows | Shared (2) | Unique (2) |
|---|---|---|---|---|
| 2.1 | `goal_diff` | 104 | appearances, days into tournament | youth_share_diff, age_spread_diff |
| 2.2 | `goals` | 208 | appearances, days into tournament | opp_appearances, is_uefa |

Split: 80/20, seed 42. Every predictor is known before kick-off.

GitHub folder:

https://github.com/BhuprajTmg/data-project/tree/cursor/assessment3-submission-0741
