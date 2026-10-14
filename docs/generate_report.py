#!/usr/bin/env python3
"""Build the HIT140 Assessment 3 Word report.

Assignment format: A4, Times New Roman 12 pt, single-spaced,
numbered headings. Run from the repository root after analytics:

    python code/clean_data.py
    python code/analytics.py
    python docs/generate_report.py
"""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIGS = Path(__file__).resolve().parent / "figures"
OUT = Path(__file__).resolve().parent / "HIT140_Assessment3_Group_Report.docx"

NAVY = RGBColor(0x1A, 0x1A, 0x1A)
HEADING = RGBColor(0x1F, 0x4E, 0x79)


def set_run_font(run, size=12, bold=False, italic=False, color=NAVY, name="Times New Roman"):
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
        el.set(qn("w:color"), "8FAADC")
        tcBorders.append(el)
    tcPr.append(tcBorders)


def cell_text(cell, text, size=10, bold=False, center=False):
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


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.font.color.rgb = NAVY
    normal.paragraph_format.line_spacing = 1.0
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    normal.paragraph_format.space_after = Pt(8)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    rfonts.set(qn("w:eastAsia"), "Times New Roman")

    for style_name, size, space_before, space_after in (
        ("Heading 1", 14, 12, 6),
        ("Heading 2", 13, 10, 4),
    ):
        st = doc.styles[style_name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = HEADING
        st.paragraph_format.space_before = Pt(space_before)
        st.paragraph_format.space_after = Pt(space_after)
        st.paragraph_format.line_spacing = 1.0
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        rfonts.set(qn("w:ascii"), "Times New Roman")
        rfonts.set(qn("w:hAnsi"), "Times New Roman")
        rfonts.set(qn("w:eastAsia"), "Times New Roman")


def add_para(doc, text, size=12, bold=False, italic=False, space_after=8, align="justify"):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
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


def add_h1(doc, text):
    p = doc.add_heading(text, level=1)
    for run in p.runs:
        set_run_font(run, size=14, bold=True, color=HEADING)
    return p


def add_h2(doc, text):
    p = doc.add_heading(text, level=2)
    for run in p.runs:
        set_run_font(run, size=13, bold=True, color=HEADING)
    return p


def make_table(doc, headers, rows, col_widths):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, h in enumerate(headers):
        cell_text(table.rows[0].cells[i], h, size=10, bold=True, center=True)
        shade(table.rows[0].cells[i], "1F4E79")
        for p in table.rows[0].cells[i].paragraphs:
            for run in p.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)
                run.bold = True
        table.rows[0].cells[i].width = Cm(col_widths[i])
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell_text(table.rows[r].cells[c], val, size=10, center=(c > 0))
            table.rows[r].cells[c].width = Cm(col_widths[c])
            if r % 2 == 0:
                shade(table.rows[r].cells[c], "D6E3F0")
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(4)
    return table


def build():
    doc = Document()
    configure_styles(doc)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    add_para(doc, "CHARLES DARWIN UNIVERSITY", size=11, bold=True, space_after=2, align="center")
    add_para(doc, "HIT140 Foundations of Data Science", size=16, bold=True, space_after=2, align="center")
    add_para(doc, "Assessment 3: Group Project Report", size=14, bold=True, space_after=2, align="center")
    add_para(
        doc,
        "Objective 2 — Linear regression models of FIFA World Cup 2026 match outcomes",
        size=12,
        italic=True,
        space_after=10,
        align="center",
    )

    add_para(doc, "Group members (same group as Assessment 2)", size=12, bold=True, space_after=4, align="left")
    make_table(
        doc,
        ["Name", "Student ID", "Contribution"],
        [
            ["Bhupraj Tamang", "", ""],
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ],
        [6.5, 4.5, 6.0],
    )
    add_para(
        doc,
        "Python code and dataset: https://github.com/BhuprajTmg/data-project/tree/cursor/assessment3-submission-0741",
        size=11,
        italic=True,
        space_after=4,
        align="left",
    )
    add_para(
        doc,
        "Run order:  python code/clean_data.py    then    python code/analytics.py",
        size=11,
        italic=True,
        space_after=8,
        align="left",
    )

    add_h1(doc, "1. Introduction")
    add_para(
        doc,
        "This report answers Objective 2 of the HIT140 project brief. The task is to predict FIFA World Cup 2026 match outcomes using only information that is known before kick-off. The tournament was hosted by Canada, Mexico and the United States from 11 June to 19 July 2026. Forty-eight teams played 104 official matches. Spain defeated Argentina 1–0 after extra time in the final.",
    )
    add_para(
        doc,
        "The linear regression models shown in Assessment 2 cannot be reused. Those models used FIFA rank, squad market value, mean squad age, previous titles, host status, rest days, same confederation and knockout. For Assessment 3 we rebuilt both models with new explanatory variables. Following the lecturer’s note, each model has four explanatory variables, and two of those variables are shared.",
    )
    add_para(
        doc,
        "Model 2.1 predicts the goal difference of a match (team 1 goals minus team 2 goals) using 104 rows. Model 2.2 predicts the number of goals scored by one team in one match using 208 rows (two rows per match). Every predictor is known before the referee starts the game. Shots, possession, cards in that match, tournament minutes and other in-match events are excluded. All wrangling, modelling and figures were produced in Python. Excel was used only to store the original raw tables. Both models use an 80/20 training/test split, random seed 42, and α = 0.05.",
    )

    add_h1(doc, "2. Data and cleaning")
    add_h2(doc, "2.1 Original data")
    add_para(
        doc,
        "The original workbook is data/original/fifa_data_original.xlsx. It contains three sheets compiled from the FIFA match centre, Wikipedia, Transfermarkt and the FIFA ranking freeze of 11 June 2026. The matches sheet has 104 games. The teams sheet has 48 national sides. The players sheet has 1,016 players who featured. Player goals and cards from this tournament are used only as a quality check (294 player goals plus 14 own goals = 308 official goals; 15 red cards). They are not put into the regressions.",
    )
    add_h2(doc, "2.2 Cleaning steps")
    add_para(
        doc,
        "Cleaning is in code/clean_data.py. Country names are mapped to one spelling so the three tables join (for example United States → USA, Turkey → Turkiye). Dates are parsed. Numeric fields are coerced. Duplicate rows are dropped. The host flag is stored as 0/1. Blank group cells for knockout matches, and blank penalty-winner cells, are labelled “Not applicable”. After cleaning there are no missing values in matches, teams or players. The script also builds a roster table from player age and position only (not minutes or goals). Cleaned files are saved in data/cleaned/.",
    )
    add_h2(doc, "2.3 New variables (four per model, two shared)")
    add_para(
        doc,
        "Shared variables (2): previous World Cup appearances, and days into the tournament from the published calendar (11 June 2026 = day 0). Unique to Model 2.1: youth_share_diff (gap in the share of the roster aged under 23) and age_spread_diff (gap in the standard deviation of roster ages). Unique to Model 2.2: opp_appearances (opponent’s previous World Cup appearances) and is_uefa (the team is a UEFA side). Model 2.1 stores appearances, youth share and age spread as team-1-minus-team-2 differences. These are not the Assessment 2 variables: we do not use rank, value, mean squad age, titles, host, rest, same confederation or knockout.",
    )

    add_h1(doc, "3. Linear Regression 2.1 — goal difference")
    add_para(
        doc,
        "The target is goal_diff. The sample is 104 matches, split into 83 training matches and 21 test matches. Training R² = 0.321 (adjusted R² = 0.286). On the held-out matches, test R² = 0.339, RMSE = 1.53 goals and MAE = 1.10 goals. Test R² is close to training R², so the model is not only fitting noise in the training sample.",
    )
    add_para(doc, "Table 1. OLS coefficients for Model 2.1 (training sample). An asterisk marks p < 0.05.", size=11, italic=True, space_after=4, align="left")
    make_table(
        doc,
        ["Variable", "Coefficient", "p-value", "Interpretation"],
        [
            ["Intercept", "+0.489", "0.200", "Not significant"],
            ["appearances_diff *", "+0.1249", "0.000", "More prior World Cups than the opponent → more net goals"],
            ["days_into_tournament", "−0.0271", "0.232", "Shared calendar variable; not significant"],
            ["youth_share_diff", "+2.798", "0.111", "More under-23 players; not significant at 5%"],
            ["age_spread_diff", "−0.175", "0.496", "Wider age mix; not significant"],
        ],
        [4.2, 2.4, 2.2, 8.2],
    )
    add_para(
        doc,
        "Only appearances_diff is significant at 5%. Each extra previous World Cup appearance for team 1, relative to team 2, is associated with about +0.12 net goals. Youth share and age spread were included because they describe the shape of the squad, not the mean age used in Assessment 2. They are not significant once tournament experience is in the model. We keep all four variables because they were chosen before looking at p-values.",
    )

    add_h1(doc, "4. Linear Regression 2.2 — goals scored by one team")
    add_para(
        doc,
        "The target is goals scored by that team in that match. The sample is 208 rows, split into 166 training rows and 42 test rows. Training R² = 0.213 (adjusted R² = 0.193). Test R² = 0.072, RMSE = 1.34 and MAE = 1.04. Test fit is weak. Counting one team’s goals is noisier than a match margin, and we are not allowed to recycle Assessment 2 predictors such as rank or value to inflate R².",
    )
    add_para(doc, "Table 2. OLS coefficients for Model 2.2 (training sample). An asterisk marks p < 0.05.", size=11, italic=True, space_after=4, align="left")
    make_table(
        doc,
        ["Variable", "Coefficient", "p-value", "Interpretation"],
        [
            ["Intercept", "+1.342", "0.000", "Baseline when other X = 0"],
            ["team_appearances *", "+0.0553", "0.002", "More own World Cup history → more goals"],
            ["days_into_tournament", "+0.0059", "0.634", "Shared calendar variable; not significant"],
            ["opp_appearances *", "−0.0654", "0.000", "More World Cup history for the opponent → fewer goals"],
            ["is_uefa *", "+0.504", "0.023", "UEFA team scores about +0.50 goals, holding experience fixed"],
        ],
        [4.2, 2.4, 2.2, 8.2],
    )
    add_para(
        doc,
        "Three coefficients are significant: team_appearances, opp_appearances and is_uefa. A team with more previous World Cups scores more. Facing a more experienced opponent is linked to about 0.07 fewer goals per extra appearance. UEFA sides score about half a goal more after those appearance counts are held fixed. Calendar day is not significant in either model.",
    )

    add_h1(doc, "5. Visualisation")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run()
    r.add_picture(str(FIGS / "reg1_pred.png"), width=Inches(3.05))
    p.add_run("  ")
    r2 = p.add_run()
    r2.add_picture(str(FIGS / "reg2_pred.png"), width=Inches(3.05))
    add_para(
        doc,
        "Figure 1 (left) and Figure 2 (right). Test-set predicted versus actual values. Left: Model 2.1 goal difference. Right: Model 2.2 team goals. The dashed line is a perfect prediction. Both charts were produced by code/analytics.py.",
        size=10,
        italic=True,
        space_after=8,
        align="center",
    )

    add_h1(doc, "6. Diagnostics, limitations and conclusion")
    add_h2(doc, "6.1 Diagnostics")
    add_para(
        doc,
        "The largest variance inflation factor, excluding the intercept, is 1.21 in Model 2.1 and 1.25 in Model 2.2. Both are well below 5, so multicollinearity is not a problem. Shapiro–Wilk tests on the training residuals give p = 0.802 for Model 2.1 (consistent with normal residuals) and p = 0.0006 for Model 2.2 (residuals are not normal). Goals are small counts (0, 1, 2, 3…), so OLS is a blunt tool. The brief asked for linear regression, which is why OLS is used. A Poisson model would be a reasonable next step for Model 2.2.",
    )
    add_h2(doc, "6.2 Limitations")
    add_para(
        doc,
        "Four limitations should be kept in mind. First, the 208 rows in Model 2.2 are not independent, because two rows come from the same match. Second, the test set for Model 2.1 is only 21 matches, so test R² = 0.339 is a rough check even though it matches the training fit. Third, youth share and age spread come from the published roster; they describe squad mix, not how many minutes those players later received. Fourth, the four variables were chosen in advance. Dropping the non-significant ones after seeing p-values would be p-hacking.",
    )
    add_h2(doc, "6.3 Conclusion")
    add_para(
        doc,
        "After rebuilding the models without the Assessment 2 variables, previous World Cup experience is the stable pre-match signal. In Model 2.1, the appearance gap is the only 5% significant driver of goal difference. In Model 2.2, a team scores more when it has more World Cup history, scores less against more experienced opponents, and UEFA sides score about half a goal more. The goal-difference model predicts held-out matches much better (test R² 0.34 versus 0.07).",
        space_after=4,
    )

    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
