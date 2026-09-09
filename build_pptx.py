#!/usr/bin/env python3
"""Build a 6-slide, 2.5-minute presentation of the WC 2026 analytics report."""

from __future__ import annotations

import base64
import io
import os
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

INK = RGBColor(0x17, 0x1B, 0x22)
INK2 = RGBColor(0x20, 0x26, 0x2F)
PARCHMENT = RGBColor(0xEF, 0xE6, 0xD3)
PARCHMENT_DIM = RGBColor(0xE2, 0xD6, 0xBB)
MAROON = RGBColor(0x8C, 0x2F, 0x39)
MAROON_DEEP = RGBColor(0x6E, 0x21, 0x29)
MARIGOLD = RGBColor(0xD9, 0xA5, 0x44)
PITCH = RGBColor(0x24, 0x40, 0x2C)
INK_SOFT = RGBColor(0xB9, 0xB6, 0xAC)
CREAM = RGBColor(0xE7, 0xDC, 0xC2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x58, 0x4F, 0x44)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
ROOT = Path("/workspace")
ASSETS = ROOT / "slides_assets"
ASSETS.mkdir(exist_ok=True)

SCRIPT = {
    1: (
        "This is HIT 140 Assignment 2: World Cup 2026 analytics. "
        "Spain won the first 48-team tournament, 1–0 after extra time over Argentina. "
        "We analysed 104 matches, 48 national teams, and 1,016 players who featured. "
        "There are four inferential tasks and two pre-match linear models, all at alpha 0.05."
    ),
    2: (
        "The data sits in three tables: matches, teams, and players. "
        "Player goals plus own goals reconcile to the official 308-goal total, and 15 red cards match FIFA. "
        "Each Objective 1 task follows the same six skills: question, wrangle, sample, describe, a 95 percent CI, and a t-test. "
        "Objective 2 predicts outcomes using only information knowable before kickoff — ranking, squad value, age, titles, host, rest, confederation, and knockout. "
        "No shots, no possession, no in-match events."
    ),
    3: (
        "Two questions came back non-significant. "
        "First: do midfielders pick up more yellows per appearance than defenders? "
        "In samples of 45, the means were 0.098 versus 0.131. p equals 0.45, Cohen’s d is tiny. We fail to reject. "
        "Second: do knockout crowds beat group-stage crowds? "
        "About two thousand extra fans, but p is 0.38. The expanded format drew large, comparable crowds throughout."
    ),
    4: (
        "Two questions were significant. "
        "UEFA squads averaged 670 million euros against 257 million for everyone else — about 2.6 times as valuable. "
        "The one-sided t-test gives p of 0.004 and a large effect, d of 1.08. We reject. "
        "Goalkeepers averaged 30.3 years — well above the outfield prime of 27. "
        "The one-sample p is 0.0001, and they were also 3.6 years older than outfield teammates."
    ),
    5: (
        "Objective 2. Model 2.1 predicts match goal difference. Training R-squared is 0.49; on the hold-out it is 0.31. "
        "Only FIFA ranking gap and squad-value gap are significant. A billion-euro value edge is about plus 1.7 net goals. "
        "Model 2.2 predicts a team’s own goals. Fit is weaker, as expected for a noisy count: test R-squared 0.22. "
        "Significant drivers are opponent rank and own squad value. Residuals are slightly skewed, so a Poisson model would be a natural next step."
    ),
    6: (
        "So: the midfield-booking story and the knockout-crowd premium are not in this data. "
        "Europe’s market-value gap is large, and keepers really do last longer. "
        "Before kickoff, ranking and squad value are the robust predictors. "
        "Thank you."
    ),
}


def rgb_hex(c: RGBColor) -> str:
    return f"#{int(c):06x}"


def set_run(run, text, size=14, bold=False, italic=False, color=INK, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font


def add_rect(slide, l, t, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
    sh.shadow.inherit = False
    return sh


def add_tb(slide, l, t, w, h):
    return slide.shapes.add_textbox(l, t, w, h)


def p_text(tf, text, size=14, bold=False, italic=False, color=INK, align=PP_ALIGN.LEFT, space_after=4, font="Calibri"):
    p = tf.paragraphs[0] if not tf.paragraphs[0].text and len(tf.paragraphs) == 1 else tf.add_paragraph()
    if tf.paragraphs[0].text == "" and p is not tf.paragraphs[0] and len(tf.paragraphs) == 2:
        # first para unused
        p = tf.paragraphs[0]
    p.clear() if hasattr(p, "clear") else None
    p.alignment = align
    p.space_after = Pt(space_after)
    r = p.add_run()
    set_run(r, text, size=size, bold=bold, italic=italic, color=color, font=font)
    return p


def write_box(slide, l, t, w, h, lines):
    """lines: list of dicts with keys text, size, bold, italic, color, align, space_after"""
    tb = add_tb(slide, l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for spec in lines:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.alignment = spec.get("align", PP_ALIGN.LEFT)
        p.space_after = Pt(spec.get("sa", 4))
        r = p.add_run()
        set_run(
            r,
            spec["t"],
            size=spec.get("s", 14),
            bold=spec.get("b", False),
            italic=spec.get("i", False),
            color=spec.get("c", INK),
            font=spec.get("f", "Calibri"),
        )
    return tb


def set_notes(slide, text):
    notes = slide.notes_slide.notes_text_frame
    notes.text = text


def extract_html_pngs() -> list[Path]:
    html = (ROOT / "wc2026_report.html").read_text(encoding="utf-8")
    blobs = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=\s]+)"', html)
    names = [
        "task1_cards.png",
        "task2_attendance.png",
        "task3_value.png",
        "task4_gk_age.png",
        "reg1_gd_hist.png",
        "reg1_pred.png",
        "reg2_goals_hist.png",
        "reg2_pred.png",
    ]
    out = []
    for name, b64 in zip(names, blobs):
        raw = base64.b64decode(re.sub(r"\s+", "", b64))
        p = ASSETS / name
        p.write_bytes(raw)
        out.append(p)
        print(f"extracted {p.name} ({len(raw):,} bytes)")
    return out


def try_regen_from_code() -> dict[str, Path]:
    """Best-effort: regenerate the same figures the HTML report uses."""
    paths: dict[str, Path] = {}
    try:
        import wc2026_analytics as A
        raw = A.load_workbook()
        matches, teams, players = A.build_tables(raw)
        t1 = A.task1_discipline(players)
        t2 = A.task2_attendance(matches)
        t3 = A.task3_uefa_value(teams)
        t4 = A.task4_gk_age(players)
        r1 = A.regression_goal_diff(matches, teams)
        r2 = A.regression_team_goals(matches, teams)
        mapping = [
            ("task1_cards.png", t1),
            ("task2_attendance.png", t2),
            ("task3_value.png", t3),
            ("task4_gk_age.png", t4),
            ("reg1_pred.png", r1),
            ("reg2_pred.png", r2),
        ]
        for name, obj in mapping:
            fig = obj.get("fig") or obj.get("fig_pred")
            if fig is None:
                continue
            dest = ASSETS / name
            fig.savefig(dest, dpi=140, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            paths[name] = dest
            print(f"regenerated {name}")
        return paths
    except Exception as e:
        print(f"code regen skipped: {e}")
        return paths


def build():
    # Always extract the report images so the deck matches the website even if regen fails.
    extract_html_pngs()
    try_regen_from_code()  # overwrites with live figures when possible

    t1 = ASSETS / "task1_cards.png"
    t2 = ASSETS / "task2_attendance.png"
    t3 = ASSETS / "task3_value.png"
    t4 = ASSETS / "task4_gk_age.png"
    r1 = ASSETS / "reg1_pred.png"
    r2 = ASSETS / "reg2_pred.png"

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # ── 1. Title ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, INK)
    add_rect(s, 0, Inches(7.22), SLIDE_W, Inches(0.16), MAROON)
    add_rect(s, 0, Inches(7.38), SLIDE_W, Inches(0.12), MARIGOLD)
    write_box(s, Inches(0.7), Inches(0.45), Inches(12), Inches(0.4), [
        {"t": "HIT140  ·  Foundation of Data Science  ·  Assignment 2", "s": 15, "b": True, "c": MARIGOLD},
    ])
    write_box(s, Inches(0.7), Inches(1.15), Inches(12), Inches(1.7), [
        {"t": "World Cup  2026", "s": 54, "i": True, "c": PARCHMENT, "f": "Georgia", "sa": 0},
        {"t": "Statistical analysis  &  linear regression", "s": 20, "c": INK_SOFT, "sa": 0},
    ])
    write_box(s, Inches(0.7), Inches(3.15), Inches(11.5), Inches(1.1), [
        {"t": "Four inferential tasks and two pre-match linear models on the first 48-team tournament — won by Spain, 1–0 after extra time over Argentina, 19 July 2026 at MetLife Stadium.",
         "s": 16, "c": INK_SOFT},
    ])
    facts = [("104", "Matches"), ("48", "National teams"), ("1,016", "Players who featured"), ("Spain", "Champion")]
    for i, (val, lab) in enumerate(facts):
        x = Inches(0.7 + i * 3.1)
        if i:
            add_rect(s, x - Inches(0.18), Inches(4.55), Inches(0.015), Inches(1.35), RGBColor(0x3A, 0x40, 0x4A))
        write_box(s, x, Inches(4.5), Inches(2.8), Inches(1.5), [
            {"t": lab.upper(), "s": 11, "b": True, "c": INK_SOFT, "sa": 2},
            {"t": val, "s": 32, "c": MARIGOLD, "f": "Georgia", "sa": 0},
        ])
    set_notes(s, SCRIPT[1])

    # ── 2. Data + method ──────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, PARCHMENT)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.95), INK)
    write_box(s, Inches(0.55), Inches(0.22), Inches(12), Inches(0.6), [
        {"t": "How the dataset was compiled", "s": 28, "i": True, "c": PARCHMENT, "f": "Georgia"},
    ])
    write_box(s, Inches(0.55), Inches(1.15), Inches(12.2), Inches(0.55), [
        {"t": "Three independently compiled tables. Own goals and red-card totals reconcile with official FIFA figures.",
         "s": 14, "c": MUTED},
    ])

    headers = ["Table", "Grain", "Rows", "Primary sources"]
    rows = [
        ["matches_raw.csv", "one official match", "104", "FIFA match centre, Wikipedia, worldcup.org.uk"],
        ["teams_raw.csv", "one national team", "48", "FIFA ranking 11 June 2026, Transfermarkt, Wikipedia"],
        ["players_raw.csv", "players with ≥1 appearance", "1,016", "Wikipedia squads, FotMob leaderboards"],
    ]
    col_w = [Inches(2.5), Inches(3.0), Inches(1.1), Inches(5.4)]
    table = s.shapes.add_table(4, 4, Inches(0.55), Inches(1.75), Inches(12.2), Inches(2.05)).table
    for i, w in enumerate(col_w):
        table.columns[i].width = w
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = INK
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = PARCHMENT
            p.font.name = "Calibri"
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CREAM if i % 2 else PARCHMENT
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = INK
                p.font.name = "Calibri"
                if j == 0:
                    p.font.bold = True

    write_box(s, Inches(0.55), Inches(3.95), Inches(12.2), Inches(0.45), [
        {"t": "All 104 attendances are official. Player goals (294) + 14 own goals = 308 tournament goals. Red cards (15) match the official count.",
         "s": 13, "c": MUTED},
    ])

    # two method cards
    add_rect(s, Inches(0.55), Inches(4.5), Inches(5.95), Inches(2.6), WHITE, RGBColor(0xC9, 0xBC, 0x9C))
    add_rect(s, Inches(6.85), Inches(4.5), Inches(5.95), Inches(2.6), WHITE, RGBColor(0xC9, 0xBC, 0x9C))
    write_box(s, Inches(0.75), Inches(4.65), Inches(5.55), Inches(2.3), [
        {"t": "OBJECTIVE 1  ·  FOUR TASKS", "s": 12, "b": True, "c": MAROON, "sa": 8},
        {"t": "Each task uses a distinct question and the same six skills: formulate, wrangle, sample, describe, 95% CI, t-test at α = 0.05.", "s": 13, "c": INK, "sa": 8},
        {"t": "Samples are drawn on purpose (seed 42) so the two groups stay balanced — not because the population is unknown.", "s": 13, "c": MUTED},
    ])
    write_box(s, Inches(7.05), Inches(4.65), Inches(5.55), Inches(2.3), [
        {"t": "OBJECTIVE 2  ·  TWO REGRESSIONS", "s": 12, "b": True, "c": MAROON, "sa": 8},
        {"t": "Exactly eight pre-match predictors. No shots, possession, or in-match events. 20% hold-out, VIF check, Shapiro–Wilk on residuals.", "s": 13, "c": INK, "sa": 8},
        {"t": "2.1  goal difference  (n = 104)     2.2  team goals  (n = 208)", "s": 13, "b": True, "c": PITCH},
    ])
    set_notes(s, SCRIPT[2])

    # ── 3. Non-significant ────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, PARCHMENT)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.95), INK)
    write_box(s, Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.6), [
        {"t": "Objective 1  ·  two questions the data does not support", "s": 26, "i": True, "c": PARCHMENT, "f": "Georgia"},
    ])

    # left panel
    add_rect(s, Inches(0.35), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(0.55), Inches(1.22), Inches(5.9), Inches(1.15), [
        {"t": "TASK 1  ·  PLAYER DISCIPLINE", "s": 12, "b": True, "c": MAROON, "sa": 4},
        {"t": "Do midfielders pick up more yellow cards per appearance than defenders?", "s": 15, "i": True, "c": INK, "f": "Georgia"},
    ])
    if t1.exists():
        s.shapes.add_picture(str(t1), Inches(0.55), Inches(2.42), width=Inches(5.85), height=Inches(3.50))
    write_box(s, Inches(0.55), Inches(5.35), Inches(5.9), Inches(1.7), [
        {"t": "n = 45 vs 45   ·   means 0.098 vs 0.131", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "t(88) = −0.76   ·   p = 0.4485   ·   d = −0.16", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Fail to reject H₀. The “midfield battle” booking narrative is not supported.", "s": 13, "c": MAROON_DEEP},
    ])

    # right panel
    add_rect(s, Inches(6.75), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(6.95), Inches(1.22), Inches(5.9), Inches(1.15), [
        {"t": "TASK 2  ·  MATCH-DAY ATTENDANCE", "s": 12, "b": True, "c": MAROON, "sa": 4},
        {"t": "Is average attendance different between knockout and group-stage matches?", "s": 15, "i": True, "c": INK, "f": "Georgia"},
    ])
    if t2.exists():
        s.shapes.add_picture(str(t2), Inches(6.95), Inches(2.42), width=Inches(5.85), height=Inches(3.50))
    write_box(s, Inches(6.95), Inches(5.35), Inches(5.9), Inches(1.7), [
        {"t": "n = 32 vs 32   ·   means 65,747 vs 67,701", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "t(62) = 0.88   ·   p = 0.3801   ·   d = 0.22", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Fail to reject H₀. The extra ~2,000 fans is sampling noise.", "s": 13, "c": MAROON_DEEP},
    ])
    set_notes(s, SCRIPT[3])

    # ── 4. Significant ────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, PARCHMENT)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.95), INK)
    write_box(s, Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.6), [
        {"t": "Objective 1  ·  two findings that hold", "s": 26, "i": True, "c": PARCHMENT, "f": "Georgia"},
    ])

    add_rect(s, Inches(0.35), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(0.55), Inches(1.22), Inches(5.9), Inches(1.15), [
        {"t": "TASK 3  ·  SQUAD MARKET VALUE", "s": 12, "b": True, "c": MAROON, "sa": 4},
        {"t": "Do UEFA squads carry a higher market value than non-UEFA squads?", "s": 15, "i": True, "c": INK, "f": "Georgia"},
    ])
    if t3.exists():
        s.shapes.add_picture(str(t3), Inches(0.55), Inches(2.42), width=Inches(5.85), height=Inches(3.50))
    write_box(s, Inches(0.55), Inches(5.35), Inches(5.9), Inches(1.7), [
        {"t": "n = 14 vs 14   ·   €669.6m vs €257.2m", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "t(26) = 2.87   ·   one-sided p = 0.0041   ·   d = 1.08 (large)", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Reject H₀. UEFA squads are roughly 2.6× as valuable.", "s": 13, "c": PITCH, "b": True},
    ])

    add_rect(s, Inches(6.75), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(6.95), Inches(1.22), Inches(5.9), Inches(1.15), [
        {"t": "TASK 4  ·  GOALKEEPER AGE", "s": 12, "b": True, "c": MAROON, "sa": 4},
        {"t": "Is mean GK age different from 27 — the usual outfield prime?", "s": 15, "i": True, "c": INK, "f": "Georgia"},
    ])
    if t4.exists():
        s.shapes.add_picture(str(t4), Inches(6.95), Inches(2.42), width=Inches(5.85), height=Inches(3.50))
    write_box(s, Inches(6.95), Inches(5.35), Inches(5.9), Inches(1.7), [
        {"t": "n = 40   ·   mean 30.32 years   ·   95% CI (28.7, 31.9)", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "t(39) = 4.25   ·   p = 0.0001   ·   d = 0.67", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Reject H₀. Keepers were also 3.6 years older than outfielders.", "s": 13, "c": PITCH, "b": True},
    ])
    set_notes(s, SCRIPT[4])

    # ── 5. Regressions ────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, PARCHMENT)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.95), INK)
    write_box(s, Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.6), [
        {"t": "Objective 2  ·  two pre-match linear models", "s": 26, "i": True, "c": PARCHMENT, "f": "Georgia"},
    ])

    add_rect(s, Inches(0.35), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(0.5), Inches(1.2), Inches(6.0), Inches(0.85), [
        {"t": "2.1  GOAL DIFFERENCE   ·   n = 104 matches", "s": 13, "b": True, "c": MAROON, "sa": 2},
        {"t": "Train R² 0.49  ·  Test R² 0.31  ·  RMSE 1.57", "s": 13, "c": MUTED},
    ])
    if r1.exists():
        s.shapes.add_picture(str(r1), Inches(0.5), Inches(2.12), width=Inches(5.95), height=Inches(3.85))
    write_box(s, Inches(0.5), Inches(5.35), Inches(6.0), Inches(1.7), [
        {"t": "Significant:  rank_diff  (p = 0.002)   ·   value_diff  (p = 0.004)", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "A €1bn squad-value edge ≈ +1.7 net goals, holding rank fixed.", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Max VIF 3.30  ·  Shapiro–Wilk p = 0.94  ·  residuals look normal.", "s": 12, "c": MUTED},
    ])

    add_rect(s, Inches(6.75), Inches(1.12), Inches(6.25), Inches(6.1), CREAM)
    write_box(s, Inches(6.9), Inches(1.2), Inches(6.0), Inches(0.85), [
        {"t": "2.2  TEAM GOALS SCORED   ·   n = 208 team-matches", "s": 13, "b": True, "c": MAROON, "sa": 2},
        {"t": "Train R² 0.29  ·  Test R² 0.22  ·  RMSE 1.23", "s": 13, "c": MUTED},
    ])
    if r2.exists():
        s.shapes.add_picture(str(r2), Inches(6.9), Inches(2.12), width=Inches(5.95), height=Inches(3.85))
    write_box(s, Inches(6.9), Inches(5.35), Inches(6.0), Inches(1.7), [
        {"t": "Significant:  opp_rank  (p = 0.038)   ·   team_value  (p = 0.035)", "s": 13, "b": True, "c": INK, "sa": 3},
        {"t": "Weaker fit is expected — an absolute tally is noisier than a difference.", "s": 13, "c": MUTED, "sa": 3},
        {"t": "Shapiro–Wilk p = 0.034  ·  mild skew  ·  a Poisson model is a natural next step.", "s": 12, "c": MUTED},
    ])
    set_notes(s, SCRIPT[5])

    # ── 6. Close ──────────────────────────────────────────────────────────
    s = prs.slides.add_slide(blank)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, INK)
    add_rect(s, 0, Inches(7.22), SLIDE_W, Inches(0.16), MAROON)
    add_rect(s, 0, Inches(7.38), SLIDE_W, Inches(0.12), MARIGOLD)
    write_box(s, Inches(0.7), Inches(0.35), Inches(12), Inches(0.7), [
        {"t": "What to take away", "s": 32, "i": True, "c": PARCHMENT, "f": "Georgia"},
    ])

    takeaways = [
        ("01", "Not supported", "Midfielders are not booked more than defenders, and knockout crowds are not significantly larger."),
        ("02", "Europe’s market", "UEFA squads are ~2.6× as valuable as the rest of the field — a large, statistically clear gap."),
        ("03", "Keepers last longer", "Goalkeepers averaged 30.3 years, well above the outfield prime of 27. Ochoa featured at 40."),
        ("04", "Pre-match signal", "FIFA ranking and squad market value are the robust drivers of goal difference and goals scored."),
    ]
    for i, (num, title, body) in enumerate(takeaways):
        y = Inches(1.15 + i * 1.25)
        write_box(s, Inches(0.7), y, Inches(1.1), Inches(1.1), [
            {"t": num, "s": 28, "i": True, "c": MARIGOLD, "f": "Georgia"},
        ])
        write_box(s, Inches(2.0), y + Inches(0.05), Inches(10.5), Inches(1.1), [
            {"t": title, "s": 18, "b": True, "c": PARCHMENT, "sa": 4},
            {"t": body, "s": 15, "c": INK_SOFT},
        ])
    set_notes(s, SCRIPT[6])

    out1 = ROOT / "WC2026_Presentation.pptx"
    out2 = ROOT / "WC2026_3min.pptx"
    prs.save(out1)
    prs.save(out2)
    print(f"saved {out1} ({out1.stat().st_size:,} bytes)")
    print(f"saved {out2}")

    script_md = ROOT / "PRESENTATION_SCRIPT.md"
    lines = [
        "# World Cup 2026 — 2.5-minute speaking script",
        "",
        "Read at a calm ~150 words per minute. **Total ≈ 2 minutes 30 seconds.**",
        "The same words are in PowerPoint **Presenter View** (Notes).",
        "",
        "| Slide | Clock | Title |",
        "|------:|:------|:------|",
        "| 1 | 0:00–0:22 | Title |",
        "| 2 | 0:22–0:48 | Data & method |",
        "| 3 | 0:48–1:18 | Two non-results |",
        "| 4 | 1:18–1:48 | Two significant findings |",
        "| 5 | 1:48–2:18 | Two regressions |",
        "| 6 | 2:18–2:30 | Close |",
        "",
    ]
    titles = {
        1: "Title",
        2: "Data & method",
        3: "Two non-results",
        4: "Two significant findings",
        5: "Two regressions",
        6: "Close",
    }
    clocks = {
        1: "0:00–0:22",
        2: "0:22–0:48",
        3: "0:48–1:18",
        4: "1:18–1:48",
        5: "1:48–2:18",
        6: "2:18–2:30",
    }
    total_words = 0
    for i in range(1, 7):
        words = len(SCRIPT[i].split())
        total_words += words
        lines += [
            f"## Slide {i} — {titles[i]} ({clocks[i]}, ~{words} words)",
            "",
            SCRIPT[i],
            "",
        ]
    lines += [
        f"**Total spoken words:** {total_words}  ·  **Pace:** ~{int(total_words / 2.5)} words/minute.",
        "",
        "If you over-run, drop the Poisson sentence on slide 5 and the Ochoa aside on slide 6.",
        "",
    ]
    script_md.write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "PRESENTATION_SCRIPT.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"script {total_words} words → {script_md}")


if __name__ == "__main__":
    build()
