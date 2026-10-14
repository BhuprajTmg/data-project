#!/usr/bin/env python3
"""HIT140 Assessment 3 — Objective 2 analytics (rebuilt models)

The Assessment 2 regressions cannot be reused. Those models used FIFA rank,
squad value, mean squad age, titles, host, rest days, same confederation and
knockout. This file uses four *new* pre-match variables in each model.

Lecturer note: at least four explanatory variables per model; two may be shared.

Linear Regression 2.1  goal difference     (104 rows, one per match)
Linear Regression 2.2  goals scored        (208 rows, two per match)

Shared (2):
    previous World Cup appearances, days into the tournament
Unique to 2.1 (2):
    youth_share_diff, age_spread_diff
Unique to 2.2 (2):
    opp_appearances, is_uefa

Every predictor is known before kick-off.
Tournament minutes, goals, cards, shots and possession are not used.

Run from the repository root after cleaning:

    python code/clean_data.py
    python code/analytics.py
"""
import json
from html import escape
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.stats.outliers_influence import variance_inflation_factor

ROOT = Path(__file__).resolve().parent.parent
CLEANED = ROOT / "data" / "cleaned"
CHARTS = ROOT / "charts"
SEED = 42
ALPHA = 0.05

# Banned (Assessment 2): rank, value, mean age, titles, host, rest, same_confed, knockout
SHARED = ["appearances", "days_into_tournament"]
UNIQUE_21 = ["youth_share_diff", "age_spread_diff"]
UNIQUE_22 = ["opp_appearances", "is_uefa"]

FEATS_21 = [
    "appearances_diff",      # shared idea: previous World Cup appearances
    "days_into_tournament",  # shared idea: published calendar
    "youth_share_diff",      # unique to 2.1  (share of roster aged under 23)
    "age_spread_diff",       # unique to 2.1  (std of roster ages)
]
FEATS_22 = [
    "team_appearances",      # shared idea: previous World Cup appearances
    "days_into_tournament",  # shared idea: published calendar
    "opp_appearances",       # unique to 2.2
    "is_uefa",               # unique to 2.2
]


def load_cleaned():
    matches = pd.read_csv(CLEANED / "matches.csv", parse_dates=["date"])
    teams = pd.read_csv(CLEANED / "teams.csv")
    roster = pd.read_csv(CLEANED / "team_roster.csv")
    teams = teams.merge(roster, on="team")
    teams["is_uefa"] = (teams["confederation"] == "UEFA").astype(int)
    matches["goal_diff"] = matches["team1_goals"] - matches["team2_goals"]
    start = matches["date"].min()
    matches["days_into_tournament"] = (matches["date"] - start).dt.days
    return matches, teams


def build_21(matches, teams):
    t1 = teams.add_suffix("_1").rename(columns={"team_1": "team1"})
    t2 = teams.add_suffix("_2").rename(columns={"team_2": "team2"})
    df = matches.merge(t1, on="team1").merge(t2, on="team2")
    return pd.DataFrame(
        {
            "match_id": df["match_number"],
            "team1": df["team1"],
            "team2": df["team2"],
            "goal_diff": df["goal_diff"],
            "appearances_diff": df["prev_wc_appearances_1"] - df["prev_wc_appearances_2"],
            "days_into_tournament": df["days_into_tournament"],
            "youth_share_diff": df["youth_share_1"] - df["youth_share_2"],
            "age_spread_diff": df["age_spread_1"] - df["age_spread_2"],
        }
    )


def build_22(matches, teams):
    rows = []
    for _, m in matches.iterrows():
        for team_col, opp_col, goals_col in (
            ("team1", "team2", "team1_goals"),
            ("team2", "team1", "team2_goals"),
        ):
            rows.append(
                {
                    "match_id": m["match_number"],
                    "team": m[team_col],
                    "opponent": m[opp_col],
                    "goals": m[goals_col],
                    "days_into_tournament": m["days_into_tournament"],
                }
            )
    df = pd.DataFrame(rows)
    df = df.merge(teams, on="team")
    df = df.merge(
        teams.add_suffix("_opp").rename(columns={"team_opp": "opponent"}),
        on="opponent",
    )
    return pd.DataFrame(
        {
            "match_id": df["match_id"],
            "team": df["team"],
            "opponent": df["opponent"],
            "goals": df["goals"],
            "team_appearances": df["prev_wc_appearances"],
            "days_into_tournament": df["days_into_tournament"],
            "opp_appearances": df["prev_wc_appearances_opp"],
            "is_uefa": df["is_uefa"],
        }
    )


def fit_ols(data, features, target):
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED
    )
    X_tr = sm.add_constant(X_train)
    model = sm.OLS(y_train, X_tr).fit()
    X_te = sm.add_constant(X_test, has_constant="add")[X_tr.columns]
    y_pred = model.predict(X_te)
    X_all = sm.add_constant(X)
    vif = pd.DataFrame(
        {
            "feature": X_all.columns,
            "VIF": [variance_inflation_factor(X_all.values, i) for i in range(X_all.shape[1])],
        }
    )
    return {
        "model": model,
        "n_train": int(X_train.shape[0]),
        "n_test": int(X_test.shape[0]),
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "test_r2": float(r2_score(y_test, y_pred)),
        "rmse": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "vif": vif,
        "shapiro_p": float(stats.shapiro(model.resid)[1]),
        "y_test": y_test,
        "y_pred": y_pred,
    }


def scatter_svg(y_test, y_pred, xlabel, ylabel, title):
    """Predicted vs actual chart as SVG (drawn by Python, styled in HTML/CSS)."""
    xs = [float(v) for v in y_test]
    ys = [float(v) for v in y_pred]
    lo = min(xs + ys) - 0.6
    hi = max(xs + ys) + 0.6
    left, right, top, bottom = 58, 18, 36, 48
    width, height = 420, 420
    inner_w = width - left - right
    inner_h = height - top - bottom

    def tx(v):
        return left + (v - lo) / (hi - lo) * inner_w

    def ty(v):
        return top + (1 - (v - lo) / (hi - lo)) * inner_h

    ticks = []
    step = 1 if hi - lo <= 8 else 2
    start = int(lo) - 1
    while start <= hi:
        if lo <= start <= hi:
            ticks.append(start)
        start += step

    parts = [
        f'<svg class="chart-svg" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f'<text class="chart-title" x="{width / 2}" y="22">{escape(title)}</text>',
        f'<rect class="chart-panel" x="{left}" y="{top}" width="{inner_w}" height="{inner_h}"/>',
        f'<line class="chart-diag" x1="{tx(lo):.1f}" y1="{ty(lo):.1f}" x2="{tx(hi):.1f}" y2="{ty(hi):.1f}"/>',
    ]
    for t in ticks:
        parts.append(
            f'<line class="chart-grid" x1="{tx(t):.1f}" y1="{top}" x2="{tx(t):.1f}" y2="{top + inner_h}"/>'
        )
        parts.append(
            f'<line class="chart-grid" x1="{left}" y1="{ty(t):.1f}" x2="{left + inner_w}" y2="{ty(t):.1f}"/>'
        )
        parts.append(f'<text class="chart-tick" x="{tx(t):.1f}" y="{height - 28}">{t}</text>')
        parts.append(f'<text class="chart-tick chart-tick-y" x="{left - 8}" y="{ty(t):.1f}">{t}</text>')
    for x, y in zip(xs, ys):
        parts.append(f'<circle class="chart-point" cx="{tx(x):.1f}" cy="{ty(y):.1f}" r="5"/>')
    parts.append(f'<text class="chart-axis" x="{left + inner_w / 2}" y="{height - 8}">{escape(xlabel)}</text>')
    parts.append(
        f'<text class="chart-axis chart-axis-y" x="16" y="{top + inner_h / 2}">{escape(ylabel)}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def result_payload(result):
    m = result["model"]
    vif_max = float(result["vif"].loc[result["vif"]["feature"] != "const", "VIF"].max())
    coefs = []
    for name in m.params.index:
        p = float(m.pvalues[name])
        coefs.append(
            {
                "name": "Intercept" if name == "const" else name,
                "coef": float(m.params[name]),
                "p": p,
                "sig": name != "const" and p < ALPHA,
            }
        )
    return {
        "n_train": result["n_train"],
        "n_test": result["n_test"],
        "r2": result["r2"],
        "adj_r2": result["adj_r2"],
        "test_r2": result["test_r2"],
        "rmse": result["rmse"],
        "mae": result["mae"],
        "vif_max": vif_max,
        "shapiro_p": result["shapiro_p"],
        "coefs": coefs,
    }


def print_model(title, result):
    m = result["model"]
    vif_max = result["vif"].loc[result["vif"]["feature"] != "const", "VIF"].max()
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)
    print(f"Train / test           {result['n_train']} / {result['n_test']}")
    print(f"Training R² / adj R²   {result['r2']:.3f} / {result['adj_r2']:.3f}")
    print(f"Test R²                {result['test_r2']:.3f}")
    print(f"Test RMSE / MAE        {result['rmse']:.2f} / {result['mae']:.2f}")
    print(f"Max VIF (excl. const)  {vif_max:.2f}")
    print(f"Shapiro–Wilk p         {result['shapiro_p']:.4f}")
    print()
    print(f"{'variable':<24} {'coef':>10} {'p-value':>10}  sig")
    for name in m.params.index:
        p = float(m.pvalues[name])
        star = "*" if name != "const" and p < ALPHA else " "
        print(f"{name:<24} {m.params[name]:+10.4f} {p:10.4f}  {star}")


def main():
    matches, teams = load_cleaned()
    assert len(matches) == 104, len(matches)
    assert len(teams) == 48, len(teams)
    assert len(FEATS_21) == 4 and len(FEATS_22) == 4
    assert len(SHARED) == 2

    d21 = build_21(matches, teams)
    d22 = build_22(matches, teams)
    assert len(d21) == 104, len(d21)
    assert len(d22) == 208, len(d22)
    assert d21[FEATS_21].isna().sum().sum() == 0
    assert d22[FEATS_22].isna().sum().sum() == 0

    CLEANED.mkdir(parents=True, exist_ok=True)
    d21.to_csv(CLEANED / "model21_goal_diff.csv", index=False)
    d22.to_csv(CLEANED / "model22_team_goals.csv", index=False)

    print("HIT140 Assessment 3 — Objective 2 (rebuilt; A2 variables not reused)")
    print("Not used: rank, value, mean age, titles, host, rest, same_confed, knockout")
    print(f"Shared ideas (2): {SHARED}")
    print(f"Unique to 2.1:    {UNIQUE_21}")
    print(f"Unique to 2.2:    {UNIQUE_22}")

    r1 = fit_ols(d21, FEATS_21, "goal_diff")
    r2 = fit_ols(d22, FEATS_22, "goals")
    print_model("Linear Regression 2.1  target = goal_diff  (104 matches)", r1)
    print_model("Linear Regression 2.2  target = goals scored  (208 rows)", r2)

    svg1 = scatter_svg(
        r1["y_test"], r1["y_pred"],
        "Actual goal difference", "Predicted goal difference",
        "Figure 1. Model 2.1 test set",
    )
    svg2 = scatter_svg(
        r2["y_test"], r2["y_pred"],
        "Actual goals scored", "Predicted goals scored",
        "Figure 2. Model 2.2 test set",
    )
    CHARTS.mkdir(exist_ok=True)
    figs = ROOT / "docs" / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    (CHARTS / "reg1_pred.svg").write_text(svg1, encoding="utf-8")
    (CHARTS / "reg2_pred.svg").write_text(svg2, encoding="utf-8")
    (figs / "reg1_pred.svg").write_text(svg1, encoding="utf-8")
    (figs / "reg2_pred.svg").write_text(svg2, encoding="utf-8")
    payload = {
        "shared": SHARED,
        "unique_21": UNIQUE_21,
        "unique_22": UNIQUE_22,
        "feats_21": FEATS_21,
        "feats_22": FEATS_22,
        "model_21": result_payload(r1),
        "model_22": result_payload(r2),
        "svg_21": svg1,
        "svg_22": svg2,
    }
    (CLEANED / "model_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nCharts (SVG): {CHARTS}")


if __name__ == "__main__":
    main()
