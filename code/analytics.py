#!/usr/bin/env python3
"""HIT140 Assessment 3 — Objective 2 analytics

Reads the cleaned tables produced by code/clean_data.py.
Fits two OLS models with at most four shared explanatory ideas.

Run from the repository root after cleaning:

    python code/clean_data.py
    python code/analytics.py

Linear Regression 2.1  goal difference     (104 rows, one per match)
Linear Regression 2.2  goals scored        (208 rows, two per match)

Shared ideas (4): knockout, FIFA rank, squad value, rest days
Unique to 2.1 (4): age_diff, titles_diff, host_diff, same_confed
Unique to 2.2 (4): team_appearances, opp_appearances, is_uefa, days_into_tournament

Every predictor is known before kick-off.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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

SHARED = ["knockout", "rank", "value", "rest"]
UNIQUE_21 = ["age_diff", "titles_diff", "host_diff", "same_confed"]
UNIQUE_22 = ["team_appearances", "opp_appearances", "is_uefa", "days_into_tournament"]

FEATS_21 = [
    "rank_diff",
    "value_diff",
    "rest_diff",
    "knockout",
    "age_diff",
    "titles_diff",
    "host_diff",
    "same_confed",
]
FEATS_22 = [
    "team_rank",
    "team_value",
    "rest_days",
    "knockout",
    "team_appearances",
    "opp_appearances",
    "is_uefa",
    "days_into_tournament",
]


def load_cleaned():
    matches = pd.read_csv(CLEANED / "matches.csv", parse_dates=["date"])
    teams = pd.read_csv(CLEANED / "teams.csv")
    teams["is_uefa"] = (teams["confederation"] == "UEFA").astype(int)
    matches["goal_diff"] = matches["team1_goals"] - matches["team2_goals"]
    start = matches["date"].min()
    matches["days_into_tournament"] = (matches["date"] - start).dt.days
    return matches, teams


def rest_days(matches):
    """Days since that team's previous tournament match.

    Opening matches have no previous date. Those 48 first games are filled
    with the median rest observed later in the tournament (known from the
    published schedule, not from the score).
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


def build_21(matches, teams):
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
            "value_diff": df["squad_market_value_eur_m_1"] - df["squad_market_value_eur_m_2"],
            "rest_diff": df["r1"] - df["r2"],
            "knockout": df["knockout"],
            "age_diff": df["squad_avg_age_1"] - df["squad_avg_age_2"],
            "titles_diff": df["prev_wc_titles_1"] - df["prev_wc_titles_2"],
            "host_diff": df["host_1"] - df["host_2"],
            "same_confed": (df["confederation_1"] == df["confederation_2"]).astype(int),
        }
    )


def build_22(matches, teams):
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
                    "days_into_tournament": m["days_into_tournament"],
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
            "team_value": df["squad_market_value_eur_m"],
            "rest_days": df["rest_days"],
            "knockout": df["knockout"],
            "team_appearances": df["prev_wc_appearances"],
            "opp_appearances": df["prev_wc_appearances_opp"],
            "is_uefa": df["is_uefa"],
            "days_into_tournament": df["days_into_tournament"],
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


def save_chart(y_test, y_pred, xlabel, ylabel, title, path):
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    ax.scatter(y_test, y_pred, color="#24402C", alpha=0.75, s=36)
    lo = min(float(y_test.min()), float(y_pred.min())) - 0.6
    hi = max(float(y_test.max()), float(y_pred.max())) + 0.6
    ax.plot([lo, hi], [lo, hi], color="#8C2F39", linestyle="--", linewidth=1.3)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


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

    d21 = build_21(matches, teams)
    d22 = build_22(matches, teams)
    assert len(d21) == 104, len(d21)
    assert len(d22) == 208, len(d22)

    CLEANED.mkdir(parents=True, exist_ok=True)
    d21.to_csv(CLEANED / "model21_goal_diff.csv", index=False)
    d22.to_csv(CLEANED / "model22_team_goals.csv", index=False)

    print("HIT140 Assessment 3 — Objective 2")
    print(f"Shared ideas (4): {SHARED}")
    print(f"Unique to 2.1:    {UNIQUE_21}")
    print(f"Unique to 2.2:    {UNIQUE_22}")

    r1 = fit_ols(d21, FEATS_21, "goal_diff")
    r2 = fit_ols(d22, FEATS_22, "goals")
    print_model("Linear Regression 2.1  target = goal_diff  (104 matches)", r1)
    print_model("Linear Regression 2.2  target = goals scored  (208 rows)", r2)

    CHARTS.mkdir(exist_ok=True)
    figs = ROOT / "docs" / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    save_chart(
        r1["y_test"], r1["y_pred"],
        "Actual goal difference", "Predicted goal difference",
        "Figure 1. Model 2.1 test set: predicted vs actual",
        CHARTS / "reg1_pred.png",
    )
    save_chart(
        r2["y_test"], r2["y_pred"],
        "Actual goals scored", "Predicted goals scored",
        "Figure 2. Model 2.2 test set: predicted vs actual",
        CHARTS / "reg2_pred.png",
    )
    # copies for the Word report
    save_chart(
        r1["y_test"], r1["y_pred"],
        "Actual goal difference", "Predicted goal difference",
        "Figure 1. Model 2.1 test set: predicted vs actual",
        figs / "reg1_pred.png",
    )
    save_chart(
        r2["y_test"], r2["y_pred"],
        "Actual goals scored", "Predicted goals scored",
        "Figure 2. Model 2.2 test set: predicted vs actual",
        figs / "reg2_pred.png",
    )
    print(f"\nCharts: {CHARTS}")


if __name__ == "__main__":
    main()
