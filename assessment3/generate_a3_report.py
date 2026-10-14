#!/usr/bin/env python3
"""Build the HIT140 Assessment 3 Word report (A4, 10pt, single-spaced, ≤4 pages)."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
OUT = HERE / "HIT140_Assessment3_Group_Report.docx"

NAVY = RGBColor(0x17, 0x1B, 0x22)
MAROON = RGBColor(0x6E, 0x21, 0x29)


def set_run_font(run, size=10, bold=False, italic=False, color=NAVY, name="Times New Roman"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def shade(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def set_cell_border(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "C9BC9C")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def cell_text(cell, text, size=8, bold=False, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)
    set_cell_border(cell)


def add_para(doc, text, size=10, bold=False, italic=False, space_after=6, space_before=0, align="left"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    set_run_font(run, size=11, bold=True, color=MAROON)
    return p


def add_mixed(doc, parts, space_after=6, justify=True):
    """parts = list of (text, bold, italic)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for text, bold, italic in parts:
        run = p.add_run(text)
        set_run_font(run, size=10, bold=bold, italic=italic)
    return p


def make_table(doc, headers, rows, col_widths):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, h in enumerate(headers):
        cell_text(table.rows[0].cells[i], h, size=8, bold=True, center=True)
        shade(table.rows[0].cells[i], "EFE6D3")
        table.rows[0].cells[i].width = Cm(col_widths[i])
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell_text(table.rows[r].cells[c], val, size=8, center=(c > 0))
            table.rows[r].cells[c].width = Cm(col_widths[c])
            if r % 2 == 0:
                shade(table.rows[r].cells[c], "F7F1E6")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def build():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.6)
    section.right_margin = Cm(1.6)
    section.top_margin = Cm(1.4)
    section.bottom_margin = Cm(1.4)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10)
    style.paragraph_format.line_spacing = 1.0

    add_para(doc, "HIT140 Foundations of Data Science — Assessment 3", size=14, bold=True, space_after=2, align="center")
    add_para(
        doc,
        "Objective 2: Predicting FIFA World Cup 2026 match outcomes from information known before kick-off",
        size=11,
        italic=True,
        space_after=4,
        align="center",
    )
    add_para(
        doc,
        "Group members: Bhupraj Tamang (Student ID: ________)  ·  _______________ (ID: ________)  ·  _______________ (ID: ________)  ·  _______________ (ID: ________)",
        size=9,
        space_after=2,
        align="center",
    )
    add_para(
        doc,
        "Python code and dataset: https://github.com/BhuprajTmg/data-project   ·   Run: python wc2026_analytics.py",
        size=9,
        italic=True,
        space_after=8,
        align="center",
    )

    add_heading(doc, "1. Introduction and research questions")
    add_para(
        doc,
        "This report covers Objective 2 of the HIT140 group project. We use real match, team and player data from the 2026 FIFA World Cup (Canada, Mexico and USA; 11 June–19 July 2026; 48 teams; 104 official matches; won 1–0 after extra time by Spain against Argentina). The aim is to predict match outcomes using only information that a team would know before the referee starts the game. We do not use shots, possession, cards in that match, or any other in-match event. Including those would leak the result we are trying to predict.",
        space_after=5,
        align="justify",
    )
    add_para(
        doc,
        "We fit two ordinary least squares (OLS) linear regression models, each with eight explanatory variables. Model 2.1 predicts the goal difference of a match (team 1 goals minus team 2 goals; 104 rows). Model 2.2 predicts how many goals one team scores in one match (208 rows, two per match). Both models are trained on 80% of the rows and tested on the held-out 20% (random seed 42). Significance is assessed at α = 0.05. All wrangling, modelling and charts were done in Python (pandas, statsmodels, scikit-learn, matplotlib). Excel was used only to store the raw sheets.",
        space_after=5,
        align="justify",
    )

    add_heading(doc, "2. Data, cleaning and feature engineering")
    add_para(
        doc,
        "Three tables sit in fifa data.xlsx and are loaded by wc2026_analytics.py. matches (104 rows) has date, stage, teams, scores and attendance, compiled from the FIFA match centre, Wikipedia group and knockout pages, and worldcup.org.uk. teams (48 rows) has FIFA ranking at the 11 June 2026 freeze, confederation, host flag, previous World Cup titles, Transfermarkt squad value (EUR million) and squad average age. players (1,016 rows) is not used as a predictor here, but was used to check data quality: 294 player goals plus 14 own goals equal the official 308-goal tournament total, and 15 red cards match the official count.",
        space_after=5,
        align="justify",
    )
    add_para(
        doc,
        "Cleaning in Python: country names are mapped to one spelling (for example United States → USA, Turkey → Turkiye, Czech Republic → Czechia) so the three tables join with no unmatched teams. Dates are parsed. Numeric fields are coerced. Duplicate team rows are dropped. A knockout flag is 1 if the stage is Round of 32 through the Final (32 matches) and 0 for the group stage (72 matches). Rest days are the number of days since that team’s previous tournament match. A team’s first match has no previous date, so those 48 opening games are filled with the median rest observed in the rest of the tournament (5 days). That fill is known before kick-off and does not use the score.",
        space_after=5,
        align="justify",
    )
    add_para(
        doc,
        "Model 2.1 features are all differences (team 1 minus team 2): FIFA rank, squad age, squad value, previous titles, host status (−1, 0 or 1), rest days, whether both teams share a confederation, and knockout. Rank is a position number, so a smaller rank is a stronger team; a negative rank_diff means team 1 is ranked better. Model 2.2 uses each side’s own rank and value, the opponent’s rank and value, squad age, a host dummy, rest days and knockout. No predictor in either model is built from the match that is being predicted.",
        space_after=5,
        align="justify",
    )

    add_heading(doc, "3. Model 2.1 — match goal difference (n = 104)")
    add_para(
        doc,
        "Target: goal_diff = team1_goals − team2_goals. Training set 83 matches, test set 21 matches. Training R² = 0.493 (adjusted R² = 0.438). On the held-out matches, test R² = 0.306, RMSE = 1.57 goals and MAE = 1.18 goals. About half of the variation in goal difference is described in-sample; out of sample the fit is weaker, which is expected with only 21 test matches, but the model still predicts better than a mean-only baseline.",
        space_after=4,
        align="justify",
    )
    make_table(
        doc,
        ["Variable", "Coef.", "p-value", "Reading in plain English"],
        [
            ["Intercept", "+0.184", "0.383", "Not significant"],
            ["rank_diff *", "−0.0232", "0.002", "Better FIFA rank (smaller number) for team 1 → more net goals"],
            ["age_diff", "+0.113", "0.427", "Not significant"],
            ["value_diff *", "+0.0017", "0.004", "EUR 1 billion extra squad value ≈ +1.7 net goals"],
            ["titles_diff", "−0.132", "0.336", "Past World Cup titles add nothing once rank and value are in"],
            ["host_diff", "+0.366", "0.494", "No clear co-host edge"],
            ["rest_diff", "+0.172", "0.641", "Rest gap not significant"],
            ["same_confed", "+0.218", "0.684", "Same confederation not significant"],
            ["knockout", "−0.726", "0.097", "Knockouts trend tighter (marginal, p < 0.10)"],
        ],
        [3.4, 2.0, 2.2, 10.2],
    )
    add_para(
        doc,
        "Only rank_diff and value_diff are significant at 5%. The rank coefficient is negative because rank 1 is better than rank 20: if team 1 is stronger, rank_diff is negative, and a negative coefficient times a negative gap predicts a positive goal difference for team 1. Value works in the obvious direction: the richer squad is expected to outscore the poorer one. Age, titles, host, rest and confederation are not significant after rank and value are included. Knockout has a negative coefficient (tighter games) but p = 0.097, so we treat it as a hint, not a finding.",
        space_after=4,
        align="justify",
    )

    add_heading(doc, "4. Model 2.2 — goals scored by one team (n = 208)")
    add_para(
        doc,
        "Target: goals scored by that team in that match. Two rows per match keep the two sides as separate observations. Training set 166 rows, test set 42 rows. Training R² = 0.290 (adjusted R² = 0.254). Test R² = 0.221, RMSE = 1.23 goals, MAE = 0.89 goals. The lower R² compared with Model 2.1 is expected: predicting one team’s exact tally (0, 1, 2, …) is noisier than predicting the gap between two sides. A 0–0 and a 2–2 look the same in Model 2.1 and different in Model 2.2.",
        space_after=4,
        align="justify",
    )
    make_table(
        doc,
        ["Variable", "Coef.", "p-value", "Reading in plain English"],
        [
            ["Intercept", "+5.60", "0.064", "Baseline when other X = 0 (not a real match)"],
            ["team_rank", "−0.0112", "0.067", "Better own rank (smaller number) → more goals (marginal)"],
            ["opp_rank *", "+0.0128", "0.038", "Weaker opponent (higher rank number) → more goals"],
            ["team_value *", "+0.0007", "0.035", "Richer own squad → more goals"],
            ["opp_value", "−0.0003", "0.316", "Not significant"],
            ["team_age", "−0.111", "0.251", "Not significant"],
            ["is_host", "+0.666", "0.085", "Co-hosts trend to score more (marginal)"],
            ["rest_days", "−0.225", "0.073", "Negative; likely a schedule confound, not “rest hurts”"],
            ["knockout", "−0.287", "0.241", "Not significant"],
        ],
        [3.4, 2.0, 2.2, 10.2],
    )
    add_para(
        doc,
        "The two significant drivers are opponent rank and own squad value. Own rank and host are close to the 5% line. Rest days is negative with p = 0.073; we do not claim that more rest reduces goals. First matches are filled at the median, and knockout scheduling sits in the same model, so this sign is more likely a timetable artefact.",
        space_after=4,
        align="justify",
    )

    # side-by-side figures
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(str(FIGS / "reg1_pred.png"), width=Inches(3.15))
    run2 = p.add_run("  ")
    set_run_font(run2, size=10)
    run3 = p.add_run()
    run3.add_picture(str(FIGS / "reg2_pred.png"), width=Inches(3.15))
    add_para(
        doc,
        "Figure 1. Test-set predicted versus actual values. Left: Model 2.1 goal difference. Right: Model 2.2 team goals. The dashed line is a perfect prediction. Points scatter around the line; Model 2.1 tracks the diagonal more tightly.",
        size=8,
        italic=True,
        space_after=6,
        align="center",
    )

    add_heading(doc, "5. Diagnostics, comparison and limitations")
    add_para(
        doc,
        "Multicollinearity was checked with variance inflation factors. The largest VIF excluding the intercept is 3.30 in Model 2.1 (value_diff) and 2.64 in Model 2.2. Both are well below the usual concern of 5 or 10, so the two significant variables in each model are not simply copies of each other. Shapiro–Wilk on training residuals: p = 0.937 for Model 2.1 (compatible with normality) and p = 0.034 for Model 2.2 (mild non-normality). That second result is not a surprise: goals are a small count (0, 1, 2, 3…). OLS was used because the brief asked for linear regression and because coefficients stay in “goals per unit of X” units. A Poisson or negative-binomial model would be a natural next step for Model 2.2.",
        space_after=5,
        align="justify",
    )
    add_para(
        doc,
        "Limitations. (1) The 208 rows in Model 2.2 are not fully independent, because two rows share a match; this can make standard errors look too small. Model 2.1 does not have that problem. (2) Transfermarkt values and average ages are a snapshot and can move a few percent with the pull date. Rankings, scores and titles do not. (3) The test set for Model 2.1 is only 21 matches, so test R² = 0.306 should be read as a rough check, not a precise claim. (4) We pre-specified eight substantively motivated predictors rather than dropping variables until every p-value was below 0.05. Age, titles and host mostly dropping out is a result, not a failure. (5) Rest-day imputation for first matches is a simple median fill; it is honest but blunt.",
        space_after=5,
        align="justify",
    )

    add_heading(doc, "6. Conclusion")
    add_para(
        doc,
        "Before kick-off, the information that actually moves predicted outcomes in this tournament is FIFA ranking and squad market value. In Model 2.1 those two gaps are the only 5% significant drivers of goal difference; a billion-euro value edge is associated with about 1.7 extra net goals after rank is held fixed. In Model 2.2 a team scores more when it is richer and when its opponent is weaker on the ranking list. Host status, rest, age and previous titles do not survive once rank and value are in the model. The goal-difference model fits better than the team-goals model, which matches the idea that a relative margin is more predictable than an absolute count. We would next refit Model 2.2 as Poisson regression with the same eight pre-match predictors and compare residual plots and out-of-sample error.",
        space_after=4,
        align="justify",
    )
    add_para(
        doc,
        "Word count of the body is within the four-page A4, 10 pt, single-spaced limit. Figures are produced by the same Python file that fits the models.",
        size=9,
        italic=True,
        space_after=0,
        align="left",
    )

    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
