# HIT140 Assessment 3 — Objective 2

FIFA World Cup 2026 linear regression (goal difference and goals scored).

The Assessment 2 regressions are **not** reused. Those models used rank, squad value, mean age, titles, host, rest days, same confederation and knockout. These models use four **new** variables each. Two variables are shared.

```
data/original/     original Excel workbook
data/cleaned/      cleaned tables written by the cleaning script
code/clean_data.py cleaning and quality checks
code/analytics.py  the two rebuilt OLS models and charts
docs/              formatted group report (Times New Roman 12 pt)
```

## How to run

```
python code/clean_data.py
python code/analytics.py
python docs/generate_report.py
```

## Models

| Model | Target | Rows | Shared (2) | Unique (2) |
|---|---|---|---|---|
| 2.1 | `goal_diff` | 104 | appearances, days into tournament | youth_share_diff, age_spread_diff |
| 2.2 | `goals` | 208 | appearances, days into tournament | opp_appearances, is_uefa |

Every predictor is known before kick-off. Split: 80/20, seed 42.

## Report

`docs/HIT140_Assessment3_Group_Report.docx`

A4, Times New Roman 12 pt, numbered headings. Type names and student IDs on page 1 before submitting.

GitHub folder for Learnline:

https://github.com/BhuprajTmg/data-project/tree/cursor/assessment3-submission-0741
