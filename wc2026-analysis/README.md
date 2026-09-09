# FIFA World Cup 2026 Analytics

A statistics and linear-regression project built on real match, team, and
player data from the 2026 FIFA World Cup (Canada / Mexico / USA,
11 June – 19 July 2026, won by Spain).

## Structure

```
wc2026-analysis/
├── wc2026_analytics.py       # the analysis (one file)
├── fifa data.xlsx            # matches / teams / players sheets
├── fifa data - original.xlsx # untouched copy of the same workbook
├── report/wc2026_report.html # generated when you run the .py
├── data/                     # same tables as CSV (optional)
├── notebooks/                # optional cell-by-cell walkthroughs
└── requirements.txt
```

## Running it

The intended final product is one Python file. From this folder:

```bash
pip install -r requirements.txt
python wc2026_analytics.py
```

That runs all four inferential tasks and both regressions, then writes
`report/wc2026_report.html` (charts are embedded; open the file in any
browser). Notebooks under `notebooks/` are optional walkthroughs of the
same work.

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
