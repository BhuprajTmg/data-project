#!/usr/bin/env python3
"""HIT140 Assessment 3 — Objective 2 only.

Two linear regressions on FIFA World Cup 2026 data, using only information
knowable before kick-off (no shots, possession or in-match events).

Place this file next to ``fifa data.xlsx`` (sheets: matches, teams) and run:

    python objective2.py

Model 2.1  goal difference, 104 matches
Model 2.2  goals scored by one team, 208 rows (two per match)
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.stats.outliers_influence import variance_inflation_factor

HERE = Path(__file__).resolve().parent
XLSX = HERE / "fifa data.xlsx"
SEED = 42
ALPHA = 0.05

KNOCKOUT_STAGES = {
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Third-place",
    "Final",
}

# Same country under different spellings → one name so matches join to teams
NAME_VARIANTS = {
    "USA": {"USA", "United States", "US", "United States of America"},
    "South Korea": {"South Korea", "Korea Republic", "Republic of Korea", "Korea"},
    "Turkiye": {"Turkiye", "Turkey", "Türkiye"},
    "Ivory Coast": {"Ivory Coast", "Cote d'Ivoire", "Côte d'Ivoire", "Cote dIvoire"},
    "Curacao": {"Curacao", "Curaçao"},
    "Cape Verde": {"Cape Verde", "Cabo Verde"},
    "DR Congo": {
        "DR Congo",
        "Democratic Republic of the Congo",
        "Congo DR",
        "DRC",
        "DR Congo (Congo DR)",
    },
    "Bosnia and Herzegovina": {"Bosnia and Herzegovina", "Bosnia & Herzegovina", "Bosnia"},
    "Czechia": {"Czechia", "Czech Republic"},
}
VARIANT_TO_CANON = {v: k for k, variants in NAME_VARIANTS.items() for v in variants}


def canon(name):
    if not isinstance(name, str):
        return name
    return VARIANT_TO_CANON.get(name.strip(), name.strip())


def as_bool(series):
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


# ---------------------------------------------------------------------------
# Load and clean
# ---------------------------------------------------------------------------

def load_matches():
    df = pd.read_excel(XLSX, sheet_name="matches")
    df["date"] = pd.to_datetime(df["date"])
    for col in ("team1", "team2"):
        df[col] = df[col].map(canon)
    df["team1_goals"] = df["team1_goals"].astype(int)
    df["team2_goals"] = df["team2_goals"].astype(int)
    df["goal_diff"] = df["team1_goals"] - df["team2_goals"]
    df["knockout"] = df["stage"].isin(KNOCKOUT_STAGES).astype(int)
    return df.sort_values("match_number").reset_index(drop=True)


def load_teams():
    df = pd.read_excel(XLSX, sheet_name="teams")
    df["team"] = df["team"].map(canon)
    df["host"] = as_bool(df["host"]).astype(int)
    for col in (
        "fifa_rank_pretournament",
        "prev_wc_titles",
        "squad_avg_age",
        "squad_market_value_eur_m",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.drop_duplicates("team").reset_index(drop=True)


def rest_days(matches):
    """Days since that team's previous tournament match.
    First match of the tournament has no previous date, so we fill with
    the median rest from all other matches (5 days). That fill is known
    before kick-off and does not use the score.
    """
    rows = []
    for _, row in matches.iterrows():
        for side in ("team1", "team2"):
            rows.append(
                {"team": row[side], "match_number": row["match_number"], "date": row["date"]}
            )
    long = pd.DataFrame(rows).sort_values(["team", "date", "match_number"])
    long["prev_date"] = long.groupby("team")["date"].shift(1)
    long["rest_days"] = (long["date"] - long["prev_date"]).dt.days
    long["rest_days"] = long["rest_days"].fillna(long["rest_days"].median())
    return long[["team", "match_number", "rest_days"]]


# ---------------------------------------------------------------------------
# Model 2.1 dataset: one row per match, target = goal difference
# ---------------------------------------------------------------------------

def build_goal_diff(matches, teams):
    rest = rest_days(matches)
    df = matches.merge(
        rest.rename(columns={"team": "team1", "rest_days": "r1"}),
        on=["match_number", "team1"],
    )
    df = df.merge(
        rest.rename(columns={"team": "team2", "rest_days": "r2"}),
        on=["match_number", "team2"],
    )
    t1 = teams.add_suffix("_1").rename(columns={"team_1": "team1"})
    t2 = teams.add_suffix("_2").rename(columns={"team_2": "team2"})
    df = df.merge(t1, on="team1").merge(t2, on="team2")
    return pd.DataFrame(
        {
            "match_id": df["match_number"],
            "team1": df["team1"],
            "team2": df["team2"],
            "goal_diff": df["goal_diff"],
            "rank_diff": df["fifa_rank_pretournament_1"] - df["fifa_rank_pretournament_2"],
            "age_diff": df["squad_avg_age_1"] - df["squad_avg_age_2"],
            "value_diff": df["squad_market_value_eur_m_1"] - df["squad_market_value_eur_m_2"],
            "titles_diff": df["prev_wc_titles_1"] - df["prev_wc_titles_2"],
            "host_diff": df["host_1"] - df["host_2"],
            "rest_diff": df["r1"] - df["r2"],
            "same_confed": (df["confederation_1"] == df["confederation_2"]).astype(int),
            "knockout": df["knockout"],
        }
    )


# ---------------------------------------------------------------------------
# Model 2.2 dataset: two rows per match (one per team), target = goals scored
# ---------------------------------------------------------------------------

def build_team_goals(matches, teams):
    rest = rest_days(matches)
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
                    "knockout": m["knockout"],
                }
            )
    df = pd.DataFrame(rows)
    df = df.merge(rest, left_on=["team", "match_id"], right_on=["team", "match_number"])
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
            "team_rank": df["fifa_rank_pretournament"],
            "opp_rank": df["fifa_rank_pretournament_opp"],
            "team_value": df["squad_market_value_eur_m"],
            "opp_value": df["squad_market_value_eur_m_opp"],
            "team_age": df["squad_avg_age"],
            "is_host": df["host"],
            "rest_days": df["rest_days"],
            "knockout": df["knockout"],
        }
    )


# ---------------------------------------------------------------------------
# OLS: 80/20 hold-out, VIF, Shapiro–Wilk on residuals
# ---------------------------------------------------------------------------

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
    shapiro_p = float(stats.shapiro(model.resid)[1])
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
        "shapiro_p": shapiro_p,
        "y_test": y_test,
        "y_pred": y_pred,
    }


def save_pred_chart(y_test, y_pred, xlabel, ylabel, title, path):
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    ax.scatter(y_test, y_pred, color="#24402C", alpha=0.75, s=36)
    lo = min(float(y_test.min()), float(y_pred.min())) - 0.6
    hi = max(float(y_test.max()), float(y_pred.max())) + 0.6
    ax.plot([lo, hi], [lo, hi], color="#8C2F39", linestyle="--", linewidth=1.3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def print_model(title, result):
    m = result["model"]
    vif_max = result["vif"].loc[result["vif"]["feature"] != "const", "VIF"].max()
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)
    print(f"Train / test          {result['n_train']} / {result['n_test']}")
    print(f"Training R² / adj R²  {result['r2']:.3f} / {result['adj_r2']:.3f}")
    print(f"Test R²               {result['test_r2']:.3f}")
    print(f"Test RMSE / MAE       {result['rmse']:.2f} / {result['mae']:.2f}")
    print(f"Max VIF (excl. const) {vif_max:.2f}")
    print(f"Shapiro–Wilk p        {result['shapiro_p']:.4f}")
    print()
    print(f"{'variable':<14} {'coef':>10} {'p-value':>10}  sig")
    for name in m.params.index:
        p = m.pvalues[name]
        star = "*" if name != "const" and p < ALPHA else " "
        print(f"{name:<14} {m.params[name]:+10.4f} {p:10.4f}  {star}")


def main():
    if not XLSX.exists():
        raise FileNotFoundError(f"Put 'fifa data.xlsx' next to this script ({HERE})")

    matches = load_matches()
    teams = load_teams()
    assert len(matches) == 104, f"expected 104 matches, got {len(matches)}"
    assert len(teams) == 48, f"expected 48 teams, got {len(teams)}"

    d21 = build_goal_diff(matches, teams)
    d22 = build_team_goals(matches, teams)
    assert len(d21) == 104 and len(d22) == 208

    feats1 = [
        "rank_diff",
        "age_diff",
        "value_diff",
        "titles_diff",
        "host_diff",
        "rest_diff",
        "same_confed",
        "knockout",
    ]
    feats2 = [
        "team_rank",
        "opp_rank",
        "team_value",
        "opp_value",
        "team_age",
        "is_host",
        "rest_days",
        "knockout",
    ]

    r1 = fit_ols(d21, feats1, "goal_diff")
    r2 = fit_ols(d22, feats2, "goals")

    print_model("Model 2.1  target = goal_diff  (104 matches)", r1)
    print_model("Model 2.2  target = goals scored  (208 team-match rows)", r2)

    out = HERE / "objective2_charts"
    out.mkdir(exist_ok=True)
    save_pred_chart(
        r1["y_test"],
        r1["y_pred"],
        "Actual goal difference",
        "Predicted goal difference",
        "Model 2.1 test set",
        out / "reg1_pred.png",
    )
    save_pred_chart(
        r2["y_test"],
        r2["y_pred"],
        "Actual goals scored",
        "Predicted goals scored",
        "Model 2.2 test set",
        out / "reg2_pred.png",
    )
    print(f"\nCharts saved in {out}")


if __name__ == "__main__":
    main()
