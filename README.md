# HIT140 Assessment 3 — Objective 2

FIFA World Cup 2026 linear regression (goal difference and goals scored).

This branch contains only the files needed for Assessment 3:

```
data/original/     original Excel workbook
data/cleaned/      cleaned tables written by the cleaning script
code/clean_data.py cleaning and quality checks
code/analytics.py  the two OLS models and charts
docs/              formatted group report (Times New Roman 12 pt)
```

## How to run

From this folder:

```
python code/clean_data.py
python code/analytics.py
python docs/generate_report.py
```

`clean_data.py` reads `data/original/fifa_data_original.xlsx` and writes:

- `data/cleaned/matches.csv`
- `data/cleaned/teams.csv`
- `data/cleaned/players.csv`
- `data/cleaned/fifa_data_cleaned.xlsx`
- `data/cleaned/cleaning_log.txt`

`analytics.py` reads the cleaned tables, fits the two models, and writes charts to `charts/` and `docs/figures/`.

## Models

| Model | Target | Rows | Shared variables (4) | Unique variables (4) |
|---|---|---|---|---|
| 2.1 | `goal_diff` | 104 | knockout, rank, value, rest | age_diff, titles_diff, host_diff, same_confed |
| 2.2 | `goals` | 208 | knockout, rank, value, rest | team_appearances, opp_appearances, is_uefa, days_into_tournament |

Every predictor is known before kick-off. Split: 80/20, seed 42.

## Report

`docs/HIT140_Assessment3_Group_Report.docx`

A4, Times New Roman 12 pt, numbered headings. Type all four names and student IDs in the table on page 1 before submitting.
