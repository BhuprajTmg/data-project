#!/usr/bin/env python3
"""HIT140 Assessment 3 group report — A4, 10pt, single-spaced, one .docx, ≤4 pages."""
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
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def set_cell_border(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "B0A48A")
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


def add_para(doc, text, size=10, bold=False, italic=False, space_after=5, space_before=0, align="justify"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.alignment = {
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    }[align]
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    set_run_font(run, size=11, bold=True, color=MAROON)
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
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(2)
    return table


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(1.7)
    sec.right_margin = Cm(1.7)
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.5)
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(10)

    add_para(doc, "HIT140 Foundations of Data Science", size=14, bold=True, space_after=1, align="center")
    add_para(doc, "Assessment 3 — Group Project Report (Objective 2)", size=12, bold=True, space_after=2, align="center")
    add_para(
        doc,
        "Two linear regression models of FIFA World Cup 2026 outcomes using only pre-match information",
        size=10,
        italic=True,
        space_after=6,
        align="center",
    )

    add_para(doc, "Group members (same group as Assessment 2)", size=9, bold=True, space_after=2, align="left")
    make_table(
        doc,
        ["Name", "Student ID"],
        [
            ["Bhupraj Tamang", ""],
            ["", ""],
            ["", ""],
            ["", ""],
        ],
        [10.0, 7.6],
    )
    add_para(
        doc,
        "Python code and dataset: https://github.com/BhuprajTmg/data-project   ·   File to run: assignment3_final_code.py",
        size=9,
        italic=True,
        space_after=6,
        align="left",
    )

    add_heading(doc, "1. What we were asked to do")
    add_para(
        doc,
        "This report is Assessment 3. It answers Objective 2 of the project brief. We built two related but different linear regression models on the completed 2026 FIFA World Cup (Canada, Mexico and USA; 11 June to 19 July 2026; 48 teams; 104 official matches). Spain beat Argentina 1–0 after extra time in the final.",
    )
    add_para(
        doc,
        "Linear Regression 2.1 predicts the goal difference of a match (team 1 goals minus team 2 goals). The dataset has 104 rows, one row per match, and exactly eight explanatory variables. Linear Regression 2.2 predicts how many goals one team scores in one match. That dataset has 208 rows, two rows per match, and another eight explanatory variables. The brief says at most four explanatory variables can be shared between the two models. Every predictor must be known before kick-off. We therefore did not use shots, possession, cards in that match, or any other in-match event.",
    )
    add_para(
        doc,
        "All wrangling, modelling and charts were done in Python (pandas, statsmodels, scikit-learn, matplotlib). Excel was used only to store the raw tables in fifa data.xlsx. We used an 80/20 training/test split, random seed 42, and α = 0.05.",
    )

    add_heading(doc, "2. Data, cleaning and choice of variables")
    add_para(
        doc,
        "We compiled three tables from public sources (FIFA match centre, Wikipedia, Transfermarkt, FIFA ranking of 11 June 2026). matches has 104 games. teams has 48 national sides (ranking, confederation, host, previous titles, previous World Cup appearances, squad value in EUR million, average age). players (1,016 players who featured) is not a predictor here; we used it only as a quality check (294 player goals + 14 own goals = 308 official goals; 15 red cards).",
    )
    add_para(
        doc,
        "Cleaning is in assignment3_final_code.py. Country names are standardised so the tables join (for example United States → USA, Turkey → Turkiye). Dates and numbers are parsed. Duplicate team rows are dropped. knockout = 1 for Round of 32 through the Final (32 matches) and 0 for the group stage (72 matches). Rest days are days since that team’s last tournament match. A first match has no previous date, so we fill those with the median rest from the other matches (5 days). The fill uses the schedule, not the score.",
    )
    add_para(
        doc,
        "Shared variables (4): knockout, FIFA rank, squad market value, and rest days. Unique to 2.1 (4): age_diff, titles_diff, host_diff, same_confed. Unique to 2.2 (4): team_appearances, opp_appearances, is_uefa, days_into_tournament (days since 11 June, from the published calendar). Model 2.1 stores rank, value and rest as team-1-minus-team-2 differences. Model 2.2 stores them as the team’s own rank, value and rest. A smaller rank number means a stronger team.",
    )

    add_heading(doc, "3. Linear Regression 2.1 — goal difference (104 matches)")
    add_para(
        doc,
        "Target: goal_diff. Training n = 83, test n = 21. Training R² = 0.493 (adjusted R² = 0.438). Test R² = 0.306, RMSE = 1.57 goals, MAE = 1.18 goals. The model explains about half of the training variation. Test fit is lower, which is normal with 21 held-out matches, but it is still better than guessing the mean.",
    )
    make_table(
        doc,
        ["Variable", "Coef.", "p-value", "Meaning"],
        [
            ["Intercept", "+0.184", "0.383", "Not significant"],
            ["rank_diff *", "−0.0232", "0.002", "Better rank for team 1 (smaller number) → more net goals"],
            ["value_diff *", "+0.0017", "0.004", "EUR 1bn extra squad value ≈ +1.7 net goals"],
            ["rest_diff", "+0.172", "0.641", "Not significant"],
            ["knockout", "−0.726", "0.097", "Knockouts look tighter (only marginal)"],
            ["age_diff", "+0.113", "0.427", "Not significant (unique to 2.1)"],
            ["titles_diff", "−0.132", "0.336", "Not significant (unique to 2.1)"],
            ["host_diff", "+0.366", "0.494", "Not significant (unique to 2.1)"],
            ["same_confed", "+0.218", "0.684", "Not significant (unique to 2.1)"],
        ],
        [3.5, 2.1, 2.2, 9.8],
    )
    add_para(
        doc,
        "Only rank_diff and value_diff are significant at 5%. rank_diff is negative because rank 1 is better than rank 20. If team 1 is stronger, rank_diff is negative; a negative coefficient then predicts a positive goal difference for team 1. Value has the expected sign: the richer squad is predicted to outscore the poorer one. Age, titles, host and same confederation add little once rank and value are in the model. We keep them because the brief asked for eight thoughtful variables, not a hunt for small p-values.",
    )

    add_heading(doc, "4. Linear Regression 2.2 — goals scored by one team (208 rows)")
    add_para(
        doc,
        "Target: goals scored by that team in that match. Training n = 166, test n = 42. Training R² = 0.264 (adjusted R² = 0.227). Test R² = 0.074, RMSE = 1.34, MAE = 1.01. Test fit is weak. Two reasons: counting one team’s goals is noisier than a match margin, and the sharing rule stops us putting opponent rank or opponent value into this model as well. We report the weak test R² rather than breaking the four-shared limit.",
    )
    make_table(
        doc,
        ["Variable", "Coef.", "p-value", "Meaning"],
        [
            ["Intercept", "+3.14", "0.000", "Baseline when other X = 0"],
            ["team_rank *", "−0.0133", "0.037", "Better own rank → more goals (shared idea: rank)"],
            ["team_value", "+0.0003", "0.535", "Not significant (shared idea: value)"],
            ["rest_days", "−0.207", "0.102", "Not significant (shared idea: rest)"],
            ["knockout", "−0.372", "0.313", "Not significant (shared idea: knockout)"],
            ["team_appearances", "+0.015", "0.558", "Own prior WC appearances (unique to 2.2)"],
            ["opp_appearances *", "−0.0645", "0.000", "More WC history for opponent → fewer goals"],
            ["is_uefa", "+0.303", "0.241", "UEFA dummy (unique to 2.2), not significant"],
            ["days_into_tournament", "+0.008", "0.668", "Schedule day (unique to 2.2), not significant"],
        ],
        [3.5, 2.1, 2.2, 9.8],
    )
    add_para(
        doc,
        "Two coefficients are significant: team_rank and opp_appearances. A better-ranked team scores more. Facing an opponent with more previous World Cups is linked to about 0.06 fewer goals per extra appearance. Value, rest, knockout, UEFA and calendar day are not significant after those two.",
    )

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run()
    r.add_picture(str(FIGS / "reg1_pred.png"), width=Inches(3.1))
    p.add_run("  ")
    r2 = p.add_run()
    r2.add_picture(str(FIGS / "reg2_pred.png"), width=Inches(3.1))
    add_para(
        doc,
        "Figure 1. Test set: predicted versus actual. Left = Model 2.1 (goal difference). Right = Model 2.2 (goals scored). The dashed line is a perfect prediction. Charts were produced in Python by assignment3_final_code.py.",
        size=8,
        italic=True,
        space_after=5,
        align="center",
    )

    add_heading(doc, "5. Diagnostics, limitations and conclusion")
    add_para(
        doc,
        "VIF (excluding the intercept) is at most 3.30 in Model 2.1 and 3.44 in Model 2.2, so collinearity is not a problem. Shapiro–Wilk on training residuals: p = 0.937 for 2.1 (consistent with normal residuals) and p = 0.017 for 2.2 (not normal). Goals are 0, 1, 2, 3… so OLS is a rough tool. The brief asked for linear regression, so we used OLS. A Poisson model would be a fair next step for 2.2.",
    )
    add_para(
        doc,
        "Limitations: (1) The 208 rows in 2.2 are not independent, because two rows come from the same match. (2) Transfermarkt values and ages are a snapshot. Rankings, scores and titles are not. (3) Test n = 21 in 2.1 is small. (4) First-match rest is a median fill. (5) We chose eight variables in advance; dropping the non-significant ones after seeing p-values would be p-hacking.",
    )
    add_para(
        doc,
        "Conclusion. With only pre-match information, FIFA ranking is the most stable signal. Model 2.1: rank gap and squad-value gap are the significant drivers of goal difference. Model 2.2: own rank and the opponent’s World Cup history are the significant drivers of goals scored. The goal-difference model predicts held-out matches much better (test R² 0.31 versus 0.07), both because a margin is easier than a count and because the sharing rule blocks opponent rank from appearing in both models.",
        space_after=2,
    )


    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
