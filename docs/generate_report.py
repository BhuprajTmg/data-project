#!/usr/bin/env python3
"""Build the HIT140 Assessment 3 report as HTML + CSS.

All analysis is Python. The report page and figures are HTML/CSS (SVG charts).
Times New Roman 12 pt, A4, numbered headings.

    python code/clean_data.py
    python code/analytics.py
    python docs/generate_report.py
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "cleaned" / "model_results.json"
OUT = Path(__file__).resolve().parent / "HIT140_Assessment3_Group_Report.html"

CSS = """
@page { size: A4; margin: 18mm; }
* { box-sizing: border-box; }
body {
  margin: 0 auto;
  max-width: 210mm;
  padding: 18mm 20mm;
  font-family: "Times New Roman", Times, serif;
  font-size: 12pt;
  line-height: 1.35;
  color: #1a1a1a;
  background: #fff;
}
h1.title { font-size: 16pt; text-align: center; margin: 0 0 2pt; color: #1f4e79; }
h1.unit { font-size: 11pt; text-align: center; margin: 0 0 4pt; letter-spacing: 0.06em; }
h2.subtitle { font-size: 14pt; text-align: center; margin: 0 0 4pt; }
p.tagline { text-align: center; font-style: italic; margin: 0 0 14pt; }
h2 { font-size: 14pt; color: #1f4e79; margin: 14pt 0 6pt; }
h3 { font-size: 13pt; color: #1f4e79; margin: 10pt 0 4pt; }
p { margin: 0 0 8pt; text-align: justify; }
p.meta { text-align: left; font-style: italic; font-size: 11pt; }
p.caption { font-size: 10pt; font-style: italic; text-align: center; margin: 4pt 0 10pt; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 10.5pt; }
th, td { border: 1px solid #8faadc; padding: 4pt 6pt; vertical-align: top; }
th { background: #1f4e79; color: #fff; text-align: center; }
td.num { text-align: center; white-space: nowrap; }
tr:nth-child(even) td { background: #d6e3f0; }
.figures { display: flex; gap: 12px; align-items: stretch; margin: 8pt 0 0; }
.figures figure { flex: 1; margin: 0; }
.chart-svg { width: 100%; height: auto; display: block; background: #f7fafc; border: 1px solid #c5d4e8; }
.chart-title { font-family: "Times New Roman", Times, serif; font-size: 12px; font-weight: 700; fill: #1f4e79; text-anchor: middle; }
.chart-panel { fill: #ffffff; stroke: #1f4e79; stroke-width: 1.2; }
.chart-diag { stroke: #8c2f39; stroke-width: 1.6; stroke-dasharray: 6 4; fill: none; }
.chart-grid { stroke: #d9e4f0; stroke-width: 1; }
.chart-tick { font-family: "Times New Roman", Times, serif; font-size: 10px; fill: #334; text-anchor: middle; }
.chart-tick-y { text-anchor: end; dominant-baseline: middle; }
.chart-axis { font-family: "Times New Roman", Times, serif; font-size: 11px; fill: #1a1a1a; text-anchor: middle; }
.chart-axis-y { transform: rotate(-90deg); transform-box: fill-box; transform-origin: center; }
.chart-point { fill: #24402c; fill-opacity: 0.78; stroke: #fff; stroke-width: 0.6; }
.name-table td { height: 22pt; }
@media print {
  body { padding: 0; max-width: none; }
}
"""


def fmt(value, digits=3):
    return f"{value:.{digits}f}"


def coef_row(c, meaning):
    star = " *" if c["sig"] else ""
    name = escape(c["name"] + star)
    coef = f"{c['coef']:+.4f}" if abs(c["coef"]) < 1 else f"{c['coef']:+.3f}"
    p = f"{c['p']:.3f}"
    return f"<tr><td>{name}</td><td class='num'>{coef}</td><td class='num'>{p}</td><td>{escape(meaning)}</td></tr>"


def build():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    m1, m2 = data["model_21"], data["model_22"]
    meanings_21 = {
        "Intercept": "Not significant",
        "appearances_diff": "More prior World Cups than the opponent → more net goals",
        "days_into_tournament": "Shared calendar variable; not significant",
        "youth_share_diff": "More under-23 players; not significant at 5%",
        "age_spread_diff": "Wider age mix; not significant",
    }
    meanings_22 = {
        "Intercept": "Baseline when other X = 0",
        "team_appearances": "More own World Cup history → more goals",
        "days_into_tournament": "Shared calendar variable; not significant",
        "opp_appearances": "More World Cup history for the opponent → fewer goals",
        "is_uefa": "UEFA team scores about +0.50 goals, holding experience fixed",
    }
    rows_21 = "\n".join(coef_row(c, meanings_21[c["name"]]) for c in m1["coefs"])
    rows_22 = "\n".join(coef_row(c, meanings_22[c["name"]]) for c in m2["coefs"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>HIT140 Assessment 3 — Group Project Report</title>
  <style>{CSS}</style>
</head>
<body>
  <h1 class="unit">CHARLES DARWIN UNIVERSITY</h1>
  <h1 class="title">HIT140 Foundations of Data Science</h1>
  <h2 class="subtitle">Assessment 3: Group Project Report</h2>
  <p class="tagline">Objective 2 — Linear regression models of FIFA World Cup 2026 match outcomes</p>

  <p><strong>Group members (same group as Assessment 2)</strong></p>
  <table class="name-table">
    <tr><th>Name</th><th>Student ID</th><th>Contribution</th></tr>
    <tr><td>Bhupraj Tamang</td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td></tr>
    <tr><td></td><td></td><td></td></tr>
  </table>
  <p class="meta">Python code and dataset: https://github.com/BhuprajTmg/data-project/tree/cursor/assessment3-submission-0741</p>
  <p class="meta">Run order: python code/clean_data.py &nbsp; then &nbsp; python code/analytics.py &nbsp; then &nbsp; python docs/generate_report.py</p>

  <h2>1. Introduction</h2>
  <p>This report answers Objective 2 of the HIT140 project brief. The task is to predict FIFA World Cup 2026 match outcomes using only information that is known before kick-off. The tournament was hosted by Canada, Mexico and the United States from 11 June to 19 July 2026. Forty-eight teams played 104 official matches. Spain defeated Argentina 1–0 after extra time in the final.</p>
  <p>The linear regression models shown in Assessment 2 cannot be reused. Those models used FIFA rank, squad market value, mean squad age, previous titles, host status, rest days, same confederation and knockout. For Assessment 3 we rebuilt both models with new explanatory variables. Following the lecturer’s note, each model has four explanatory variables, and two of those variables are shared.</p>
  <p>Model 2.1 predicts the goal difference of a match (team 1 goals minus team 2 goals) using 104 rows. Model 2.2 predicts the number of goals scored by one team in one match using 208 rows (two rows per match). Every predictor is known before the referee starts the game. Shots, possession, cards in that match, tournament minutes and other in-match events are excluded. All wrangling and modelling were done in Python. The report and figures are HTML and CSS. Excel was used only to store the original raw tables. Both models use an 80/20 training/test split, random seed 42, and α = 0.05.</p>

  <h2>2. Data and cleaning</h2>
  <h3>2.1 Original data</h3>
  <p>The original workbook is data/original/fifa_data_original.xlsx. It contains three sheets compiled from the FIFA match centre, Wikipedia, Transfermarkt and the FIFA ranking freeze of 11 June 2026. The matches sheet has 104 games. The teams sheet has 48 national sides. The players sheet has 1,016 players who featured. Player goals and cards from this tournament are used only as a quality check (294 player goals plus 14 own goals = 308 official goals; 15 red cards). They are not put into the regressions.</p>
  <h3>2.2 Cleaning steps</h3>
  <p>Cleaning is in code/clean_data.py. Country names are mapped to one spelling so the three tables join (for example United States → USA, Turkey → Turkiye). Dates are parsed. Numeric fields are coerced. Duplicate rows are dropped. The host flag is stored as 0/1. Blank group cells for knockout matches, and blank penalty-winner cells, are labelled “Not applicable”. After cleaning there are no missing values in matches, teams or players. The script also builds a roster table from player age and position only (not minutes or goals). Cleaned files are saved in data/cleaned/.</p>
  <h3>2.3 New variables (four per model, two shared)</h3>
  <p>Shared variables (2): previous World Cup appearances, and days into the tournament from the published calendar (11 June 2026 = day 0). Unique to Model 2.1: youth_share_diff (gap in the share of the roster aged under 23) and age_spread_diff (gap in the standard deviation of roster ages). Unique to Model 2.2: opp_appearances (opponent’s previous World Cup appearances) and is_uefa (the team is a UEFA side). Model 2.1 stores appearances, youth share and age spread as team-1-minus-team-2 differences. These are not the Assessment 2 variables: we do not use rank, value, mean squad age, titles, host, rest, same confederation or knockout.</p>

  <h2>3. Linear Regression 2.1 — goal difference</h2>
  <p>The target is goal_diff. The sample is 104 matches, split into {m1['n_train']} training matches and {m1['n_test']} test matches. Training R² = {fmt(m1['r2'])} (adjusted R² = {fmt(m1['adj_r2'])}). On the held-out matches, test R² = {fmt(m1['test_r2'])}, RMSE = {fmt(m1['rmse'], 2)} goals and MAE = {fmt(m1['mae'], 2)} goals. Test R² is close to training R², so the model is not only fitting noise in the training sample.</p>
  <p class="caption">Table 1. OLS coefficients for Model 2.1 (training sample). An asterisk marks p &lt; 0.05.</p>
  <table>
    <tr><th>Variable</th><th>Coefficient</th><th>p-value</th><th>Interpretation</th></tr>
    {rows_21}
  </table>
  <p>Only appearances_diff is significant at 5%. Each extra previous World Cup appearance for team 1, relative to team 2, is associated with about +0.12 net goals. Youth share and age spread were included because they describe the shape of the squad, not the mean age used in Assessment 2. They are not significant once tournament experience is in the model. We keep all four variables because they were chosen before looking at p-values.</p>

  <h2>4. Linear Regression 2.2 — goals scored by one team</h2>
  <p>The target is goals scored by that team in that match. The sample is 208 rows, split into {m2['n_train']} training rows and {m2['n_test']} test rows. Training R² = {fmt(m2['r2'])} (adjusted R² = {fmt(m2['adj_r2'])}). Test R² = {fmt(m2['test_r2'])}, RMSE = {fmt(m2['rmse'], 2)} and MAE = {fmt(m2['mae'], 2)}. Test fit is weak. Counting one team’s goals is noisier than a match margin, and we are not allowed to recycle Assessment 2 predictors such as rank or value to inflate R².</p>
  <p class="caption">Table 2. OLS coefficients for Model 2.2 (training sample). An asterisk marks p &lt; 0.05.</p>
  <table>
    <tr><th>Variable</th><th>Coefficient</th><th>p-value</th><th>Interpretation</th></tr>
    {rows_22}
  </table>
  <p>Three coefficients are significant: team_appearances, opp_appearances and is_uefa. A team with more previous World Cups scores more. Facing a more experienced opponent is linked to about 0.07 fewer goals per extra appearance. UEFA sides score about half a goal more after those appearance counts are held fixed. Calendar day is not significant in either model.</p>

  <h2>5. Visualisation</h2>
  <div class="figures">
    <figure>{data['svg_21']}</figure>
    <figure>{data['svg_22']}</figure>
  </div>
  <p class="caption">Figure 1 (left) and Figure 2 (right). Test-set predicted versus actual values. The dashed line is a perfect prediction. Both charts are SVG drawn in Python and styled with CSS.</p>

  <h2>6. Diagnostics, limitations and conclusion</h2>
  <h3>6.1 Diagnostics</h3>
  <p>The largest variance inflation factor, excluding the intercept, is {fmt(m1['vif_max'], 2)} in Model 2.1 and {fmt(m2['vif_max'], 2)} in Model 2.2. Both are well below 5, so multicollinearity is not a problem. Shapiro–Wilk tests on the training residuals give p = {fmt(m1['shapiro_p'], 3)} for Model 2.1 (consistent with normal residuals) and p = {m2['shapiro_p']:.4f} for Model 2.2 (residuals are not normal). Goals are small counts (0, 1, 2, 3…), so OLS is a blunt tool. The brief asked for linear regression, which is why OLS is used. A Poisson model would be a reasonable next step for Model 2.2.</p>
  <h3>6.2 Limitations</h3>
  <p>Four limitations should be kept in mind. First, the 208 rows in Model 2.2 are not independent, because two rows come from the same match. Second, the test set for Model 2.1 is only 21 matches, so test R² = {fmt(m1['test_r2'])} is a rough check even though it matches the training fit. Third, youth share and age spread come from the published roster; they describe squad mix, not how many minutes those players later received. Fourth, the four variables were chosen in advance. Dropping the non-significant ones after seeing p-values would be p-hacking.</p>
  <h3>6.3 Conclusion</h3>
  <p>After rebuilding the models without the Assessment 2 variables, previous World Cup experience is the stable pre-match signal. In Model 2.1, the appearance gap is the only 5% significant driver of goal difference. In Model 2.2, a team scores more when it has more World Cup history, scores less against more experienced opponents, and UEFA sides score about half a goal more. The goal-difference model predicts held-out matches much better (test R² {fmt(m1['test_r2'], 2)} versus {fmt(m2['test_r2'], 2)}).</p>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
