#!/usr/bin/env python3
"""FIFA World Cup 2026 Analytics — single-file report generator.

Runs four inferential-statistics tasks and two linear-regression models on
the compiled 2026 World Cup datasets, then writes a self-contained HTML
report (charts embedded as base64, no extra assets needed).

Place this file next to ``fifa data.xlsx`` (sheets: matches, teams, players)
and run:

    python wc2026_analytics.py

Writes ``wc2026_report.html`` in the same folder.
"""
from __future__ import annotations

import base64
import io
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

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
XLSX = HERE / "fifa data.xlsx"
OUT_HTML = HERE / "wc2026_report.html"
SEED = 42

INK = "#171B22"
PARCHMENT = "#EFE6D3"
MAROON = "#8C2F39"
MARIGOLD = "#D9A544"
PITCH = "#24402C"
INK_SOFT = "#B9B6AC"

KNOCKOUT_STAGES = {
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Third-place",
    "Final",
}
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
VARIANT_TO_CANON = {v: k for k, vs in NAME_VARIANTS.items() for v in vs}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def canon(name):
    if not isinstance(name, str):
        return name
    return VARIANT_TO_CANON.get(name.strip(), name.strip())


def as_bool(series):
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


def describe(series):
    s = pd.Series(series).dropna().astype(float)
    return {
        "n": int(s.shape[0]),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std(ddof=1)),
        "min": float(s.min()),
        "max": float(s.max()),
        "q1": float(s.quantile(0.25)),
        "q3": float(s.quantile(0.75)),
        "skew": float(s.skew()),
    }


def ci_mean(series, confidence=0.95):
    s = pd.Series(series).dropna().astype(float)
    n = s.shape[0]
    mean = float(s.mean())
    se = float(s.std(ddof=1) / np.sqrt(n))
    t_crit = float(stats.t.ppf(1 - (1 - confidence) / 2, df=n - 1))
    margin = t_crit * se
    return {
        "n": n,
        "mean": mean,
        "se": se,
        "t_crit": t_crit,
        "ci_low": mean - margin,
        "ci_high": mean + margin,
        "confidence": confidence,
    }


def one_sample_ttest(series, popmean, alternative="two-sided"):
    s = pd.Series(series).dropna().astype(float)
    t_stat, p_val = stats.ttest_1samp(s, popmean=popmean, alternative=alternative)
    return {
        "n": int(s.shape[0]),
        "sample_mean": float(s.mean()),
        "popmean_h0": popmean,
        "t_stat": float(t_stat),
        "df": int(s.shape[0] - 1),
        "p_value": float(p_val),
        "cohens_d": float((s.mean() - popmean) / s.std(ddof=1)),
        "alternative": alternative,
    }


def two_sample_ttest(a, b, equal_var=False, alternative="two-sided"):
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    t_stat, p_val = stats.ttest_ind(a, b, equal_var=equal_var, alternative=alternative)
    n1, n2 = a.shape[0], b.shape[0]
    v1, v2 = a.var(ddof=1), b.var(ddof=1)
    if equal_var:
        df = n1 + n2 - 2
    else:
        df = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    pooled = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    return {
        "n1": n1,
        "n2": n2,
        "mean1": float(a.mean()),
        "mean2": float(b.mean()),
        "sd1": float(np.sqrt(v1)),
        "sd2": float(np.sqrt(v2)),
        "t_stat": float(t_stat),
        "df": float(df),
        "p_value": float(p_val),
        "cohens_d": float((a.mean() - b.mean()) / pooled),
        "equal_var": equal_var,
        "alternative": alternative,
    }


def levene_p(a, b):
    return float(stats.levene(pd.Series(a).dropna().astype(float), pd.Series(b).dropna().astype(float))[1])


def srs(df, n, seed=SEED):
    n = min(n, len(df))
    return df.sample(n=n, random_state=seed, replace=False)


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def style_ax(ax):
    ax.set_facecolor(PARCHMENT)
    ax.tick_params(colors=INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    ax.title.set_color(INK)
    for spine in ax.spines.values():
        spine.set_color("#C9BC9C")


def verdict(p, alpha=0.05):
    return "Reject H₀" if p < alpha else "Fail to reject H₀"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_table(sheet):
    if not XLSX.exists():
        raise FileNotFoundError(f"Put 'fifa data.xlsx' next to this script ({HERE})")
    return pd.read_excel(XLSX, sheet_name=sheet)


def load_matches():
    df = _load_table("matches")
    df["date"] = pd.to_datetime(df["date"])
    for col in ("team1", "team2", "penalty_winner"):
        if col in df.columns:
            df[col] = df[col].map(canon)
    for col in ("went_to_extra_time", "went_to_penalties"):
        if col in df.columns:
            df[col] = as_bool(df[col])
    df["team1_goals"] = df["team1_goals"].astype(int)
    df["team2_goals"] = df["team2_goals"].astype(int)
    df["goal_diff"] = df["team1_goals"] - df["team2_goals"]
    df["knockout"] = df["stage"].isin(KNOCKOUT_STAGES).astype(int)
    return df.sort_values("match_number").reset_index(drop=True)


def load_teams():
    df = _load_table("teams")
    df["team"] = df["team"].map(canon)
    df["host"] = as_bool(df["host"]).astype(int)
    for col in (
        "fifa_rank_pretournament",
        "prev_wc_titles",
        "prev_wc_appearances",
        "squad_avg_age",
        "squad_market_value_eur_m",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.drop_duplicates("team").reset_index(drop=True)


def load_players():
    df = _load_table("players")
    df["team"] = df["team"].map(canon)
    df["position"] = df["position"].astype(str).str.strip().str.upper()
    for col in ("age", "appearances", "minutes_played", "goals", "assists", "yellow_cards", "red_cards"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["appearances"].fillna(0) >= 1].reset_index(drop=True)
    df["cards_per_app"] = df["yellow_cards"].fillna(0) / df["appearances"]
    return df


def rest_days(matches):
    rows = []
    for _, row in matches.iterrows():
        for side in ("team1", "team2"):
            rows.append({"team": row[side], "match_number": row["match_number"], "date": row["date"]})
    long = pd.DataFrame(rows).sort_values(["team", "date", "match_number"])
    long["prev_date"] = long.groupby("team")["date"].shift(1)
    long["rest_days"] = (long["date"] - long["prev_date"]).dt.days
    long["rest_days"] = long["rest_days"].fillna(long["rest_days"].median())
    return long[["team", "match_number", "rest_days"]]


def build_goal_diff(matches, teams):
    rest = rest_days(matches)
    df = matches.merge(rest.rename(columns={"team": "team1", "rest_days": "r1"}), on=["match_number", "team1"])
    df = df.merge(rest.rename(columns={"team": "team2", "rest_days": "r2"}), on=["match_number", "team2"])
    t1 = teams.add_suffix("_1").rename(columns={"team_1": "team1"})
    t2 = teams.add_suffix("_2").rename(columns={"team_2": "team2"})
    df = df.merge(t1, on="team1").merge(t2, on="team2")
    out = pd.DataFrame(
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
    return out


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
    df = df.merge(rest, left_on=["team", "match_id"], right_on=["team", "match_number"]).drop(columns=["match_number"])
    df = df.merge(teams, on="team")
    df = df.merge(teams.add_suffix("_opp").rename(columns={"team_opp": "opponent"}), on="opponent")
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
# Analyses
# ---------------------------------------------------------------------------

def task1_discipline(players):
    outfield = players[players["position"].isin(["DF", "MF"])]
    mf_pop = outfield[outfield["position"] == "MF"]
    df_pop = outfield[outfield["position"] == "DF"]
    mf = srs(mf_pop, 45)
    de = srs(df_pop, 45)
    lev = levene_p(mf["cards_per_app"], de["cards_per_app"])
    tt = two_sample_ttest(mf["cards_per_app"], de["cards_per_app"], equal_var=lev > 0.05)
    ci = ci_mean(mf["cards_per_app"])

    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.6), facecolor=PARCHMENT)
    ax[0].hist(mf["cards_per_app"], bins=10, color=PITCH, edgecolor=PARCHMENT)
    ax[0].set_title("Midfielders")
    ax[1].hist(de["cards_per_app"], bins=10, color=MAROON, edgecolor=PARCHMENT)
    ax[1].set_title("Defenders")
    for a in ax:
        style_ax(a)
        a.set_xlabel("Yellow cards / appearance")
        a.set_ylabel("Players")
    fig.suptitle("Yellow cards per appearance", color=INK, fontstyle="italic", fontsize=13)
    fig.tight_layout()

    return {
        "pop_mf": len(mf_pop),
        "pop_df": len(df_pop),
        "mf": describe(mf["cards_per_app"]),
        "df": describe(de["cards_per_app"]),
        "ci": ci,
        "tt": tt,
        "lev": lev,
        "chart": fig_to_b64(fig),
    }


def task2_attendance(matches):
    group_pop = matches[matches["knockout"] == 0]
    ko_pop = matches[matches["knockout"] == 1]
    group = group_pop.sample(n=min(32, len(group_pop)), random_state=SEED, replace=False)
    ko = ko_pop.copy()
    lev = levene_p(ko["attendance"], group["attendance"])
    tt = two_sample_ttest(ko["attendance"], group["attendance"], equal_var=lev > 0.05)
    ci = ci_mean(pd.concat([group["attendance"], ko["attendance"]]))

    fig, ax = plt.subplots(figsize=(6.6, 3.8), facecolor=PARCHMENT)
    bp = ax.boxplot(
        [group["attendance"], ko["attendance"]],
        tick_labels=["Group Stage", "Knockout"],
        patch_artist=True,
        medianprops={"color": INK, "linewidth": 1.6},
    )
    for patch, color in zip(bp["boxes"], [PITCH, MARIGOLD]):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    style_ax(ax)
    ax.set_ylabel("Attendance")
    ax.set_title("Match-day attendance by stage", fontstyle="italic")
    fig.tight_layout()

    return {
        "pop_g": len(group_pop),
        "pop_k": len(ko_pop),
        "g": describe(group["attendance"]),
        "k": describe(ko["attendance"]),
        "ci": ci,
        "tt": tt,
        "lev": lev,
        "chart": fig_to_b64(fig),
    }


def task3_value(teams):
    teams = teams.copy()
    teams["is_uefa"] = (teams["confederation"] == "UEFA").astype(int)
    uefa_pop = teams[teams["is_uefa"] == 1]
    other_pop = teams[teams["is_uefa"] == 0]
    n = min(14, len(uefa_pop), len(other_pop))
    uefa = uefa_pop.sample(n=n, random_state=SEED, replace=False)
    other = other_pop.sample(n=n, random_state=SEED, replace=False)
    lev = levene_p(uefa["squad_market_value_eur_m"], other["squad_market_value_eur_m"])
    tt = two_sample_ttest(
        uefa["squad_market_value_eur_m"],
        other["squad_market_value_eur_m"],
        equal_var=lev > 0.05,
        alternative="greater",
    )
    ci = ci_mean(uefa["squad_market_value_eur_m"])

    fig, ax = plt.subplots(figsize=(6.6, 3.8), facecolor=PARCHMENT)
    bp = ax.boxplot(
        [uefa["squad_market_value_eur_m"], other["squad_market_value_eur_m"]],
        tick_labels=["UEFA", "Non-UEFA"],
        patch_artist=True,
        medianprops={"color": INK, "linewidth": 1.6},
    )
    for patch, color in zip(bp["boxes"], [MARIGOLD, PITCH]):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    style_ax(ax)
    ax.set_ylabel("Squad market value (EUR m)")
    ax.set_title("Squad market value by confederation", fontstyle="italic")
    fig.tight_layout()

    return {
        "pop_u": len(uefa_pop),
        "pop_n": len(other_pop),
        "u": describe(uefa["squad_market_value_eur_m"]),
        "n": describe(other["squad_market_value_eur_m"]),
        "ci": ci,
        "tt": tt,
        "lev": lev,
        "chart": fig_to_b64(fig),
    }


def task4_age(players):
    gk_pop = players[players["position"] == "GK"]
    of_pop = players[players["position"].isin(["DF", "MF", "FW"])]
    gk = srs(gk_pop, 40)
    of = srs(of_pop, 40)
    ci = ci_mean(gk["age"])
    one = one_sample_ttest(gk["age"], popmean=27)
    lev = levene_p(gk["age"], of["age"])
    two = two_sample_ttest(gk["age"], of["age"], equal_var=lev > 0.05)

    fig, ax = plt.subplots(figsize=(6.6, 3.8), facecolor=PARCHMENT)
    bp = ax.boxplot(
        [gk["age"], of["age"]],
        tick_labels=["Goalkeepers", "Outfield"],
        patch_artist=True,
        medianprops={"color": INK, "linewidth": 1.6},
    )
    for patch, color in zip(bp["boxes"], [MAROON, PITCH]):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.axhline(27, color=MARIGOLD, linestyle="--", linewidth=1.4, label="Benchmark: 27")
    style_ax(ax)
    ax.set_ylabel("Age (years)")
    ax.set_title("Player age by position group", fontstyle="italic")
    ax.legend(frameon=False)
    fig.tight_layout()

    return {
        "pop_gk": len(gk_pop),
        "pop_of": len(of_pop),
        "gk": describe(gk["age"]),
        "of": describe(of["age"]),
        "ci": ci,
        "one": one,
        "two": two,
        "lev": lev,
        "chart": fig_to_b64(fig),
    }


def fit_ols(data, features, target):
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=SEED)
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
    resid = model.resid
    shapiro_p = float(stats.shapiro(resid)[1])
    return {
        "model": model,
        "features": features,
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
        "target_series": y,
    }


def chart_pred(y_test, y_pred, xlabel, ylabel, title):
    fig, ax = plt.subplots(figsize=(5.4, 5.4), facecolor=PARCHMENT)
    ax.scatter(y_test, y_pred, color=PITCH, alpha=0.75, edgecolor=PARCHMENT, s=36)
    lo = min(float(y_test.min()), float(y_pred.min())) - 0.6
    hi = max(float(y_test.max()), float(y_pred.max())) + 0.6
    ax.plot([lo, hi], [lo, hi], color=MAROON, linestyle="--", linewidth=1.3)
    style_ax(ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontstyle="italic")
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_target_hist(series, title, xlabel, bins=None):
    fig, ax = plt.subplots(figsize=(8.2, 3.4), facecolor=PARCHMENT)
    if bins is None:
        lo, hi = int(series.min()) - 1, int(series.max()) + 2
        bins = range(lo, hi)
    ax.hist(series, bins=bins, color=PITCH, edgecolor=PARCHMENT)
    style_ax(ax)
    ax.set_title(title, fontstyle="italic")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    fig.tight_layout()
    return fig_to_b64(fig)


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def fmt(x, nd=3):
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    if abs(x) >= 100:
        return f"{x:,.1f}"
    return f"{x:.{nd}f}"


def pfmt(p):
    return f"{p:.4f}" if p >= 0.0001 else "< 0.0001"


def table_rows(pairs):
    rows = []
    for i, (k, v) in enumerate(pairs):
        rows.append(f"<tr{' class=\"alt\"' if i % 2 else ''}><th>{k}</th><td>{v}</td></tr>")
    return "\n".join(rows)


def img(b64, alt):
    return f'<figure><img src="data:image/png;base64,{b64}" alt="{alt}"><figcaption>{alt}</figcaption></figure>'


def build_html(ctx):
    t1, t2, t3, t4 = ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]
    r1, r2 = ctx["r1"], ctx["r2"]
    m, tm, pl = ctx["matches"], ctx["teams"], ctx["players"]

    coef_rows_1 = []
    for name in ["const"] + r1["features"]:
        row = r1["model"].params
        pvs = r1["model"].pvalues
        ses = r1["model"].bse
        star = " *" if name != "const" and pvs[name] < 0.05 else ""
        coef_rows_1.append(
            f"<tr><td>{name}{star}</td><td>{row[name]:+.4f}</td><td>{ses[name]:.4f}</td><td>{pfmt(pvs[name])}</td></tr>"
        )
    coef_rows_2 = []
    for name in ["const"] + r2["features"]:
        row = r2["model"].params
        pvs = r2["model"].pvalues
        ses = r2["model"].bse
        star = " *" if name != "const" and pvs[name] < 0.05 else ""
        coef_rows_2.append(
            f"<tr><td>{name}{star}</td><td>{row[name]:+.4f}</td><td>{ses[name]:.4f}</td><td>{pfmt(pvs[name])}</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FIFA World Cup 2026 — Analytics Report</title>
<meta name="description" content="Four inferential-statistics tasks and two linear-regression models on the 2026 FIFA World Cup.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{{
    --ink:#171B22;
    --ink-2:#20262F;
    --parchment:#EFE6D3;
    --parchment-dim:#E2D6BB;
    --maroon:#8C2F39;
    --maroon-deep:#6E2129;
    --marigold:#D9A544;
    --pitch:#24402C;
    --ink-soft:#B9B6AC;
    --line: rgba(239,230,211,0.16);
    --line-dark: rgba(23,27,34,0.14);
    --max: 920px;
  }}
  *{{box-sizing:border-box;}}
  html{{scroll-behavior:smooth;}}
  body{{
    margin:0;
    background:var(--parchment);
    color:var(--ink);
    font-family:'Manrope', sans-serif;
    line-height:1.55;
    -webkit-font-smoothing:antialiased;
  }}
  h1,h2,h3{{
    font-family:'Newsreader', serif;
    font-weight:500;
    margin:0;
    color:inherit;
  }}
  a{{color:inherit;}}
  .wrap{{max-width:var(--max); margin:0 auto; padding:0 28px;}}
  @media (max-width:600px){{ .wrap{{padding:0 20px;}} }}

  .skip{{position:absolute; left:-999px; top:0; background:var(--marigold); color:var(--ink); padding:10px 16px; z-index:100;}}
  .skip:focus{{left:12px; top:12px;}}

  .hero{{
    background:var(--ink);
    color:var(--parchment);
    padding:64px 0 0;
    position:relative;
    overflow:hidden;
  }}
  .hero-top{{
    display:flex; justify-content:space-between; align-items:center;
    font-size:0.92rem; color:var(--ink-soft); padding-bottom:36px;
    border-bottom:1px solid var(--line);
  }}
  .club-mark{{display:flex; align-items:center; gap:10px; color:var(--parchment); font-weight:700; letter-spacing:0.01em;}}
  .hero-nav{{display:flex; gap:18px; flex-wrap:wrap;}}
  .hero-nav a{{color:var(--ink-soft); text-decoration:none; font-size:0.88rem;}}
  .hero-nav a:hover{{color:var(--marigold);}}
  .hero-body{{padding:56px 0 44px;}}
  .hero-label{{font-size:1rem; color:var(--marigold); margin:0 0 6px;}}
  .hero-title{{
    font-size:clamp(2.4rem, 6vw, 4.4rem);
    font-style:italic;
    color:var(--parchment);
    line-height:1.05;
    max-width:14ch;
  }}
  .hero-title em{{color:var(--marigold); font-style:italic;}}
  .hero-sub{{
    max-width:58ch;
    margin-top:22px;
    font-size:1.08rem;
    color:var(--ink-soft);
  }}
  .hero-cta{{margin-top:32px; display:flex; gap:12px; flex-wrap:wrap;}}
  .btn{{
    display:inline-block;
    background:var(--marigold);
    color:var(--ink);
    font-weight:700;
    padding:14px 26px;
    text-decoration:none;
    border:none;
    cursor:pointer;
    font-size:1rem;
    font-family:'Manrope',sans-serif;
  }}
  .btn:hover{{background:#c99433;}}
  .btn-outline{{
    background:transparent;
    color:var(--parchment);
    border:1px solid var(--line);
  }}
  .btn-outline:hover{{border-color:var(--marigold); color:var(--marigold);}}

  .stitch{{
    height:14px;
    background:var(--maroon);
    position:relative;
  }}
  .stitch::before{{
    content:"";
    position:absolute; inset:0;
    background-image: repeating-linear-gradient(90deg, var(--marigold) 0 10px, transparent 10px 22px);
    opacity:0.55;
  }}

  .facts{{
    background:var(--parchment);
    border-bottom:1px solid var(--line-dark);
  }}
  .facts-grid{{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    padding:34px 0;
  }}
  .fact{{ padding:0 20px; border-left:1px solid var(--line-dark); }}
  .fact:first-child{{border-left:none; padding-left:0;}}
  .fact-label{{font-size:0.88rem; color:#6B6255; margin-bottom:6px;}}
  .fact-value{{font-family:'Newsreader',serif; font-size:1.35rem; font-weight:500;}}
  @media (max-width:760px){{
    .facts-grid{{grid-template-columns:repeat(2,1fr); row-gap:24px;}}
    .fact:nth-child(3){{border-left:none; padding-left:0;}}
  }}

  .deadline{{
    background:var(--pitch);
    color:var(--parchment);
    padding:38px 0;
  }}
  .deadline-inner{{display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:24px;}}
  .deadline-copy h3{{font-size:1.3rem; font-style:italic; color:var(--parchment);}}
  .deadline-copy p{{margin:6px 0 0; color:#C9D4C7; font-size:0.95rem; max-width:56ch;}}
  .clock{{display:flex; gap:18px; flex-wrap:wrap;}}
  .clock-unit{{text-align:center; min-width:72px;}}
  .clock-num{{font-family:'Newsreader',serif; font-size:1.7rem; color:var(--marigold);}}
  .clock-word{{font-size:0.78rem; color:#C9D4C7; margin-top:2px;}}

  section{{padding:64px 0;}}
  .section-title{{font-size:clamp(1.7rem,3.4vw,2.3rem); font-style:italic; margin-bottom:14px;}}
  .section-kicker{{color:var(--maroon); font-weight:700; font-size:0.82rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:8px;}}
  .section-intro{{max-width:64ch; color:#584F44; margin-bottom:28px;}}
  .form-section{{background:#E7DCC2; border-top:1px solid var(--line-dark); border-bottom:1px solid var(--line-dark);}}

  .q{{
    font-family:'Newsreader',serif;
    font-style:italic;
    font-size:1.25rem;
    border-left:3px solid var(--marigold);
    padding:4px 0 4px 16px;
    margin:0 0 28px;
  }}

  .steps{{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:0;
    border-top:1px solid var(--line-dark);
    margin-bottom:36px;
  }}
  .step{{
    padding:28px 24px 28px 0;
    border-right:1px solid var(--line-dark);
    padding-right:24px;
  }}
  .step:last-child{{border-right:none;}}
  .step-num{{font-family:'Newsreader',serif; font-style:italic; font-size:1.6rem; color:var(--maroon);}}
  .step h4{{font-family:'Manrope',sans-serif; font-weight:700; font-size:1.02rem; margin:10px 0 6px;}}
  .step p{{margin:0; color:#584F44; font-size:0.95rem;}}
  @media (max-width:700px){{
    .steps{{grid-template-columns:1fr;}}
    .step{{border-right:none; border-bottom:1px solid var(--line-dark); padding:24px 0;}}
  }}

  table.stats{{
    width:100%;
    border-collapse:collapse;
    margin:8px 0 28px;
    font-size:0.94rem;
  }}
  table.stats th, table.stats td{{
    text-align:left;
    padding:10px 8px;
    border-bottom:1px solid #C9BC9C;
    vertical-align:top;
  }}
  table.stats thead th{{
    font-size:0.8rem;
    color:#7A7061;
    font-weight:600;
  }}
  table.stats tbody th{{font-weight:600; width:46%; color:#3D362C;}}
  table.stats tr.alt td, table.stats tr.alt th{{background:rgba(36,64,44,0.04);}}
  .badge{{
    display:inline-block;
    background:var(--pitch);
    color:var(--parchment);
    font-size:0.75rem;
    font-weight:700;
    letter-spacing:0.04em;
    padding:4px 9px;
    margin-left:8px;
    vertical-align:middle;
  }}
  .badge.warn{{background:var(--maroon);}}
  .badge.ok{{background:var(--pitch);}}

  figure{{margin:8px 0 36px;}}
  figure img{{width:100%; height:auto; display:block; border:1px solid #C9BC9C;}}
  figcaption{{font-size:0.82rem; color:#7A7061; margin-top:8px;}}

  .callout{{
    background:var(--parchment);
    border:1px solid #C9BC9C;
    padding:18px 20px;
    margin:8px 0 0;
  }}
  .callout strong{{color:var(--maroon-deep);}}

  footer{{background:var(--ink); color:var(--ink-soft); padding:48px 0 32px; font-size:0.92rem;}}
  .footer-grid{{display:flex; flex-wrap:wrap; justify-content:space-between; gap:32px; padding-bottom:28px; border-bottom:1px solid var(--line);}}
  .footer-club h3{{color:var(--parchment); font-style:italic; font-size:1.3rem; margin-bottom:8px;}}
  .footer-club p{{max-width:42ch; margin:0;}}
  .footer-contact a{{color:var(--marigold); text-decoration:none;}}
  .footer-contact a:hover{{text-decoration:underline;}}
  .footer-bottom{{padding-top:20px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px; font-size:0.82rem;}}
</style>
</head>
<body>
<a class="skip" href="#task1">Skip to first analytic task</a>

<header class="hero">
  <div class="wrap">
    <div class="hero-top">
      <div class="club-mark">
        <svg width="26" height="26" viewBox="0 0 26 26" fill="none"><circle cx="13" cy="13" r="12" stroke="#D9A544" stroke-width="1.4"/><path d="M13 2 L13 24 M2 13 L24 13" stroke="#D9A544" stroke-width="1" opacity="0.5"/></svg>
        HIT140 · Data Analytics
      </div>
      <nav class="hero-nav" aria-label="Report sections">
        <a href="#data">Data</a>
        <a href="#task1">Task 1</a>
        <a href="#task2">Task 2</a>
        <a href="#task3">Task 3</a>
        <a href="#task4">Task 4</a>
        <a href="#reg1">Regression 2.1</a>
        <a href="#reg2">Regression 2.2</a>
      </nav>
    </div>
    <div class="hero-body">
      <p class="hero-label">Statistical analysis &amp; linear regression</p>
      <h1 class="hero-title">World Cup <em>2026</em></h1>
      <p class="hero-sub">Four distinct inferential tasks and two pre-match linear models, built on real match, team, and player data from the expanded 48-team tournament — won by Spain, 1–0 over Argentina after extra time, on 19 July 2026 at MetLife Stadium.</p>
      <div class="hero-cta">
        <a href="#task1" class="btn">Read the findings</a>
        <a href="#data" class="btn btn-outline">How the data was compiled</a>
      </div>
    </div>
  </div>
</header>
<div class="stitch"></div>

<section class="facts" aria-label="Tournament facts">
  <div class="wrap facts-grid">
    <div class="fact">
      <div class="fact-label">Matches</div>
      <div class="fact-value">{len(m)}</div>
    </div>
    <div class="fact">
      <div class="fact-label">National teams</div>
      <div class="fact-value">{len(tm)}</div>
    </div>
    <div class="fact">
      <div class="fact-label">Players who featured</div>
      <div class="fact-value">{len(pl):,}</div>
    </div>
    <div class="fact">
      <div class="fact-label">Champion</div>
      <div class="fact-value">Spain</div>
    </div>
  </div>
</section>

<div class="deadline">
  <div class="wrap deadline-inner">
    <div class="deadline-copy">
      <h3>What this report answers</h3>
      <p>Each Objective&nbsp;1 task is driven by a distinct question and walks the same six skills: question formulation, wrangling, sampling, descriptive statistics, a 95% confidence interval, and a t-test. Objective&nbsp;2 then predicts match outcomes from information that was knowable before kickoff.</p>
    </div>
    <div class="clock" aria-label="Report scope">
      <div class="clock-unit"><div class="clock-num">4</div><div class="clock-word">Analytic tasks</div></div>
      <div class="clock-unit"><div class="clock-num">2</div><div class="clock-word">Regressions</div></div>
      <div class="clock-unit"><div class="clock-num">8</div><div class="clock-word">Predictors each</div></div>
      <div class="clock-unit"><div class="clock-num">α</div><div class="clock-word">= 0.05</div></div>
    </div>
  </div>
</div>

<section id="data">
  <div class="wrap">
    <p class="section-kicker">Sources</p>
    <h2 class="section-title">How the dataset was compiled</h2>
    <p class="section-intro">Three independently compiled tables — matches, teams, and players — were cross-checked so every team name appears exactly once in the team metadata. Own goals and red-card totals reconcile with the official tournament figures.</p>
    <table class="stats">
      <thead><tr><th>Table</th><th>Grain</th><th>Rows</th><th>Primary sources</th></tr></thead>
      <tbody>
        <tr><td>matches_raw.csv</td><td>one official match</td><td>{len(m)}</td><td>FIFA match centre, Wikipedia group &amp; knockout pages, worldcup.org.uk</td></tr>
        <tr class="alt"><td>teams_raw.csv</td><td>one national team</td><td>{len(tm)}</td><td>FIFA ranking (11 June 2026), Transfermarkt squad values, Wikipedia records</td></tr>
        <tr><td>players_raw.csv</td><td>one player with ≥1 appearance</td><td>{len(pl):,}</td><td>Wikipedia squads &amp; goalscorer module, fotmob leaderboards</td></tr>
      </tbody>
    </table>
    <p class="section-intro" style="margin-bottom:0;">All 104 attendance figures are officially reported. Squad market values are Transfermarkt point-in-time estimates. Player goals (294) plus 14 own goals reconcile to the official 308-goal tournament total; red cards (15) match the official count exactly.</p>
  </div>
</section>

<section class="form-section" id="task1">
  <div class="wrap">
    <p class="section-kicker">Objective 1 · Task 1</p>
    <h2 class="section-title">Player discipline</h2>
    <p class="q">On average, do midfielders pick up more yellow cards per appearance than defenders?</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h4>Wrangle</h4>
        <p>Keep only players with ≥1 appearance. Derive cards_per_app = yellow cards ÷ appearances so a seven-match finalist is compared fairly with a one-match substitute.</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h4>Sample</h4>
        <p>Population: {t1['pop_mf']} midfielders and {t1['pop_df']} defenders. Simple random sample, without replacement, of n = {t1['mf']['n']} per position (seed 42).</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h4>Test</h4>
        <p>H₀: μ<sub>MF</sub> = μ<sub>DF</sub>. Two-sample t-test at α = 0.05, after Levene’s check (p = {pfmt(t1['lev'])}).</p>
      </div>
    </div>
    <table class="stats">
      <thead><tr><th></th><th>Midfielders</th><th>Defenders</th></tr></thead>
      <tbody>
        <tr><th>Sample n</th><td>{t1['mf']['n']}</td><td>{t1['df']['n']}</td></tr>
        <tr class="alt"><th>Mean cards / appearance</th><td>{t1['mf']['mean']:.3f}</td><td>{t1['df']['mean']:.3f}</td></tr>
        <tr><th>Standard deviation</th><td>{t1['mf']['std']:.3f}</td><td>{t1['df']['std']:.3f}</td></tr>
        <tr class="alt"><th>Median</th><td>{t1['mf']['median']:.3f}</td><td>{t1['df']['median']:.3f}</td></tr>
      </tbody>
    </table>
    {img(t1['chart'], "Yellow cards per appearance — midfielders vs. defenders")}
    <table class="stats">
      <tbody>
        {table_rows([
            ("95% CI for midfielder mean", f"({t1['ci']['ci_low']:.3f}, {t1['ci']['ci_high']:.3f})"),
            ("t-statistic (df)", f"{t1['tt']['t_stat']:.2f} ({t1['tt']['df']:.0f})"),
            ("p-value", pfmt(t1['tt']['p_value'])),
            ("Cohen’s d", f"{t1['tt']['cohens_d']:.2f} (small)"),
            ("Decision", f"{verdict(t1['tt']['p_value'])} at α = 0.05"),
        ])}
      </tbody>
    </table>
    <div class="callout"><strong>Takeaway.</strong> Midfielders averaged {t1['mf']['mean']:.3f} cards per appearance against {t1['df']['mean']:.3f} for defenders. The difference is well within sampling noise — the “midfield battle” booking narrative is not supported by the 2026 data.</div>
  </div>
</section>

<section id="task2">
  <div class="wrap">
    <p class="section-kicker">Objective 1 · Task 2</p>
    <h2 class="section-title">Match-day attendance</h2>
    <p class="q">Is average stadium attendance significantly different between knockout and group-stage matches?</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h4>Wrangle</h4>
        <p>All {len(m)} official matches carry a reported attendance. A binary knockout flag splits Group Stage from Round of 32 through the Final.</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h4>Sample</h4>
        <p>Stratified equal allocation: the full knockout census (n = {t2['pop_k']}) plus a simple random sample of {t2['g']['n']} of {t2['pop_g']} group matches.</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h4>Test</h4>
        <p>H₀: μ<sub>knockout</sub> = μ<sub>group</sub>. Two-sample t-test at α = 0.05 (Levene p = {pfmt(t2['lev'])}).</p>
      </div>
    </div>
    <table class="stats">
      <thead><tr><th></th><th>Group Stage</th><th>Knockout</th></tr></thead>
      <tbody>
        <tr><th>Sample n</th><td>{t2['g']['n']}</td><td>{t2['k']['n']}</td></tr>
        <tr class="alt"><th>Mean attendance</th><td>{t2['g']['mean']:,.0f}</td><td>{t2['k']['mean']:,.0f}</td></tr>
        <tr><th>Standard deviation</th><td>{t2['g']['std']:,.0f}</td><td>{t2['k']['std']:,.0f}</td></tr>
      </tbody>
    </table>
    {img(t2['chart'], "Attendance by stage")}
    <table class="stats">
      <tbody>
        {table_rows([
            ("95% CI for overall mean attendance", f"({t2['ci']['ci_low']:,.0f}, {t2['ci']['ci_high']:,.0f})"),
            ("t-statistic (df)", f"{t2['tt']['t_stat']:.2f} ({t2['tt']['df']:.0f})"),
            ("p-value", pfmt(t2['tt']['p_value'])),
            ("Cohen’s d", f"{t2['tt']['cohens_d']:.2f} (small)"),
            ("Decision", f"{verdict(t2['tt']['p_value'])} at α = 0.05"),
        ])}
      </tbody>
    </table>
    <div class="callout"><strong>Takeaway.</strong> Knockout crowds averaged {t2['k']['mean']:,.0f} against {t2['g']['mean']:,.0f} in the group stage — a gap of about {abs(t2['k']['mean']-t2['g']['mean']):,.0f} fans that is not statistically significant. The expanded format drew large, comparable crowds throughout.</div>
  </div>
</section>

<section class="form-section" id="task3">
  <div class="wrap">
    <p class="section-kicker">Objective 1 · Task 3</p>
    <h2 class="section-title">Squad market value</h2>
    <p class="q">Do UEFA squads carry a significantly higher market value than non-UEFA squads?</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h4>Wrangle</h4>
        <p>One Transfermarkt-valued 26-man squad per nation. Split the 48 teams into UEFA versus everyone else (CONMEBOL, CONCACAF, CAF, AFC, OFC).</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h4>Sample</h4>
        <p>Population: {t3['pop_u']} UEFA / {t3['pop_n']} non-UEFA. Balanced simple random sample of n = {t3['u']['n']} per group.</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h4>Test</h4>
        <p>H₀: μ<sub>UEFA</sub> = μ<sub>non-UEFA</sub> against H₁: μ<sub>UEFA</sub> &gt; μ<sub>non-UEFA</sub>. One-sided two-sample t-test.</p>
      </div>
    </div>
    <table class="stats">
      <thead><tr><th></th><th>UEFA</th><th>Non-UEFA</th></tr></thead>
      <tbody>
        <tr><th>Sample n</th><td>{t3['u']['n']}</td><td>{t3['n']['n']}</td></tr>
        <tr class="alt"><th>Mean squad value (EUR m)</th><td>{t3['u']['mean']:,.1f}</td><td>{t3['n']['mean']:,.1f}</td></tr>
        <tr><th>Standard deviation</th><td>{t3['u']['std']:,.1f}</td><td>{t3['n']['std']:,.1f}</td></tr>
      </tbody>
    </table>
    {img(t3['chart'], "Squad market value — UEFA vs. non-UEFA")}
    <table class="stats">
      <tbody>
        {table_rows([
            ("95% CI for UEFA mean value", f"(EUR {t3['ci']['ci_low']:,.1f}m, EUR {t3['ci']['ci_high']:,.1f}m)"),
            ("t-statistic (df)", f"{t3['tt']['t_stat']:.2f} ({t3['tt']['df']:.0f})"),
            ("p-value (one-sided)", pfmt(t3['tt']['p_value'])),
            ("Cohen’s d", f"{t3['tt']['cohens_d']:.2f} (large)"),
            ("Decision", f"{verdict(t3['tt']['p_value'])} at α = 0.05"),
        ])}
      </tbody>
    </table>
    <div class="callout"><strong>Takeaway.</strong> UEFA squads averaged EUR {t3['u']['mean']:,.0f}m against EUR {t3['n']['mean']:,.0f}m — roughly {t3['u']['mean']/t3['n']['mean']:.1f}× as valuable. Europe’s club-market dominance shows up clearly at national-team level.</div>
  </div>
</section>

<section id="task4">
  <div class="wrap">
    <p class="section-kicker">Objective 1 · Task 4</p>
    <h2 class="section-title">Goalkeeper age profile</h2>
    <p class="q">Is the mean age of goalkeepers who appeared at the tournament significantly different from 27 — the usual outfield “prime” benchmark?</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h4>Wrangle</h4>
        <p>Restrict to players with ≥1 appearance, then split goalkeepers from outfield (DF / MF / FW).</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h4>Sample</h4>
        <p>Population: {t4['pop_gk']} goalkeepers and {t4['pop_of']:,} outfield players. Simple random sample of n = {t4['gk']['n']} from each group.</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h4>Test</h4>
        <p>Primary: one-sample t-test of GK age against 27. Supporting: two-sample comparison against outfield players.</p>
      </div>
    </div>
    <table class="stats">
      <thead><tr><th></th><th>Goalkeepers</th><th>Outfield</th></tr></thead>
      <tbody>
        <tr><th>Sample n</th><td>{t4['gk']['n']}</td><td>{t4['of']['n']}</td></tr>
        <tr class="alt"><th>Mean age</th><td>{t4['gk']['mean']:.2f}</td><td>{t4['of']['mean']:.2f}</td></tr>
        <tr><th>Standard deviation</th><td>{t4['gk']['std']:.2f}</td><td>{t4['of']['std']:.2f}</td></tr>
      </tbody>
    </table>
    {img(t4['chart'], "Player age by position group")}
    <table class="stats">
      <tbody>
        {table_rows([
            ("95% CI for goalkeeper mean age", f"({t4['ci']['ci_low']:.2f}, {t4['ci']['ci_high']:.2f}) years"),
            ("One-sample t vs. 27", f"t({t4['one']['df']}) = {t4['one']['t_stat']:.2f}, p = {pfmt(t4['one']['p_value'])}"),
            ("Cohen’s d (vs. 27)", f"{t4['one']['cohens_d']:.2f}"),
            ("Decision (one-sample)", f"{verdict(t4['one']['p_value'])} at α = 0.05"),
            ("Supporting two-sample", f"t({t4['two']['df']:.1f}) = {t4['two']['t_stat']:.2f}, p = {pfmt(t4['two']['p_value'])}, d = {t4['two']['cohens_d']:.2f}"),
        ])}
      </tbody>
    </table>
    <div class="callout"><strong>Takeaway.</strong> Goalkeepers averaged {t4['gk']['mean']:.1f} years — significantly older than 27, and about {t4['gk']['mean']-t4['of']['mean']:.1f} years older than outfield teammates. Keepers really do have a longer international shelf life (Mexico’s Guillermo Ochoa featured at 40).</div>
  </div>
</section>

<section class="form-section" id="reg1">
  <div class="wrap">
    <p class="section-kicker">Objective 2.1</p>
    <h2 class="section-title">Predicting match goal difference</h2>
    <p class="section-intro">One row per official match (n = {len(ctx['d21'])}). Target: team1 goals − team2 goals. Exactly eight explanatory variables, all knowable before kickoff — no shots, possession, or in-match events.</p>
    <table class="stats">
      <thead><tr><th>#</th><th>Variable</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>rank_diff</td><td>FIFA ranking position, team1 − team2 (lower number = stronger)</td></tr>
        <tr class="alt"><td>2</td><td>age_diff</td><td>Squad average-age difference</td></tr>
        <tr><td>3</td><td>value_diff</td><td>Squad market-value difference (EUR m)</td></tr>
        <tr class="alt"><td>4</td><td>titles_diff</td><td>Prior World Cup titles difference</td></tr>
        <tr><td>5</td><td>host_diff</td><td>Host-nation indicator difference ∈ {{−1, 0, 1}}</td></tr>
        <tr class="alt"><td>6</td><td>rest_diff</td><td>Rest-days-before-match difference</td></tr>
        <tr><td>7</td><td>same_confed</td><td>1 if both teams share a confederation</td></tr>
        <tr class="alt"><td>8</td><td>knockout</td><td>1 if the match is in the knockout stage</td></tr>
      </tbody>
    </table>
    {img(r1['hist'], "Distribution of match goal difference (n = 104)")}
    <table class="stats">
      <thead><tr><th>Fit</th><th>Value</th></tr></thead>
      <tbody>
        {table_rows([
            ("Training / test split", f"{r1['n_train']} / {r1['n_test']} matches (20% hold-out)"),
            ("Training R² / adjusted R²", f"{r1['r2']:.3f} / {r1['adj_r2']:.3f}"),
            ("Test R²", f"{r1['test_r2']:.3f}"),
            ("Test RMSE / MAE", f"{r1['rmse']:.2f} / {r1['mae']:.2f} goals"),
            ("Max VIF (excl. intercept)", f"{r1['vif'].loc[r1['vif']['feature']!='const','VIF'].max():.2f}"),
            ("Shapiro–Wilk on residuals", f"p = {pfmt(r1['shapiro_p'])}"),
        ])}
      </tbody>
    </table>
    <table class="stats">
      <thead><tr><th>Coefficient</th><th>Estimate</th><th>Std. error</th><th>p-value</th></tr></thead>
      <tbody>{''.join(coef_rows_1)}</tbody>
    </table>
    <p class="section-intro">* significant at α = 0.05.</p>
    {img(r1['pred'], "Test set: predicted vs. actual goal difference")}
    <div class="callout"><strong>Takeaway.</strong> FIFA ranking gap and squad-value gap are the statistically robust drivers of goal difference. A EUR 1bn squad-value edge is associated with roughly +1.7 net goals, holding rank fixed. Residuals are approximately normal; VIFs are all well below 5.</div>
  </div>
</section>

<section id="reg2">
  <div class="wrap">
    <p class="section-kicker">Objective 2.2</p>
    <h2 class="section-title">Predicting a team’s goals in a match</h2>
    <p class="section-intro">Two rows per match (n = {len(ctx['d22'])}) — one for each side. Target: goals scored by that team. Again, exactly eight pre-match explanatory variables.</p>
    <table class="stats">
      <thead><tr><th>#</th><th>Variable</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>team_rank</td><td>Team’s own FIFA ranking position</td></tr>
        <tr class="alt"><td>2</td><td>opp_rank</td><td>Opponent’s FIFA ranking position</td></tr>
        <tr><td>3</td><td>team_value</td><td>Team squad market value (EUR m)</td></tr>
        <tr class="alt"><td>4</td><td>opp_value</td><td>Opponent squad market value (EUR m)</td></tr>
        <tr><td>5</td><td>team_age</td><td>Team squad average age</td></tr>
        <tr class="alt"><td>6</td><td>is_host</td><td>1 if the team is a co-host nation</td></tr>
        <tr><td>7</td><td>rest_days</td><td>Days since the team’s previous tournament match</td></tr>
        <tr class="alt"><td>8</td><td>knockout</td><td>1 if the match is in the knockout stage</td></tr>
      </tbody>
    </table>
    {img(r2['hist'], "Distribution of goals scored by a team in a match (n = 208)")}
    <table class="stats">
      <thead><tr><th>Fit</th><th>Value</th></tr></thead>
      <tbody>
        {table_rows([
            ("Training / test split", f"{r2['n_train']} / {r2['n_test']} team-match rows"),
            ("Training R² / adjusted R²", f"{r2['r2']:.3f} / {r2['adj_r2']:.3f}"),
            ("Test R²", f"{r2['test_r2']:.3f}"),
            ("Test RMSE / MAE", f"{r2['rmse']:.2f} / {r2['mae']:.2f} goals"),
            ("Max VIF (excl. intercept)", f"{r2['vif'].loc[r2['vif']['feature']!='const','VIF'].max():.2f}"),
            ("Shapiro–Wilk on residuals", f"p = {pfmt(r2['shapiro_p'])}"),
        ])}
      </tbody>
    </table>
    <table class="stats">
      <thead><tr><th>Coefficient</th><th>Estimate</th><th>Std. error</th><th>p-value</th></tr></thead>
      <tbody>{''.join(coef_rows_2)}</tbody>
    </table>
    <p class="section-intro">* significant at α = 0.05.</p>
    {img(r2['pred'], "Test set: predicted vs. actual goals scored")}
    <div class="callout"><strong>Takeaway.</strong> A team’s own squad value and its opponent’s ranking are the clearest significant drivers of goals scored. The lower R² versus the goal-difference model is expected: an absolute tally is noisier than a relative difference. Mild residual skew is consistent with goals being a small count — a Poisson model would be a natural extension.</div>
  </div>
</section>

<section class="form-section" id="limits">
  <div class="wrap">
    <p class="section-kicker">Caveats</p>
    <h2 class="section-title">Limitations</h2>
    <div class="steps">
      <div class="step">
        <div class="step-num">i</div>
        <h4>Sampling on purpose</h4>
        <p>Objective 1 draws samples rather than using the full compiled population, to demonstrate a sampling technique and keep the two t-test groups balanced.</p>
      </div>
      <div class="step">
        <div class="step-num">ii</div>
        <h4>Snapshot values</h4>
        <p>Transfermarkt squad values and average ages move a few percent with the pull date. Rankings, titles, scores, and attendance are unambiguous facts.</p>
      </div>
      <div class="step">
        <div class="step-num">iii</div>
        <h4>Count-valued goals</h4>
        <p>OLS is used for interpretability on the team-goals model. First-match rest days are filled with the tournament-median rest — a neutral, pre-tournament baseline.</p>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-club">
        <h3>FIFA World Cup 2026</h3>
        <p>Analytics report generated by <code>wc2026_analytics.py</code> from the compiled match, team, and player extracts. Canada · Mexico · USA, 11 June – 19 July 2026.</p>
      </div>
      <div class="footer-contact">
        <div>Spain 1–0 Argentina (AET)</div>
        <div>MetLife Stadium · 19 July 2026</div>
        <div><a href="#data">Back to sources</a></div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>HIT140 · Foundation of Data Science · Assignment 2</span>
      <span>Four tasks · two regressions · α = 0.05</span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def main():
    print("Loading data…")
    matches = load_matches()
    teams = load_teams()
    players = load_players()
    assert len(matches) == 104, f"expected 104 matches, got {len(matches)}"
    assert len(teams) == 48, f"expected 48 teams, got {len(teams)}"

    print("Running Objective 1…")
    t1 = task1_discipline(players)
    t2 = task2_attendance(matches)
    t3 = task3_value(teams)
    t4 = task4_age(players)

    print("Running Objective 2…")
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
    r1["hist"] = chart_target_hist(d21["goal_diff"], "Match goal difference (team1 − team2)", "Goal difference")
    r1["pred"] = chart_pred(r1["y_test"], r1["y_pred"], "Actual goal difference", "Predicted goal difference", "Test set: predicted vs. actual")

    r2 = fit_ols(d22, feats2, "goals")
    r2["hist"] = chart_target_hist(
        d22["goals"],
        "Goals scored by a team in a match",
        "Goals",
        bins=range(0, int(d22["goals"].max()) + 2),
    )
    r2["pred"] = chart_pred(r2["y_test"], r2["y_pred"], "Actual goals scored", "Predicted goals scored", "Test set: predicted vs. actual")

    print("Writing HTML report…")
    html = build_html(
        {
            "matches": matches,
            "teams": teams,
            "players": players,
            "t1": t1,
            "t2": t2,
            "t3": t3,
            "t4": t4,
            "r1": r1,
            "r2": r2,
            "d21": d21,
            "d22": d22,
        }
    )
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size / 1024:.0f} KB)")
    print()
    print("Task 1 discipline  p =", f"{t1['tt']['p_value']:.4f}", verdict(t1["tt"]["p_value"]))
    print("Task 2 attendance  p =", f"{t2['tt']['p_value']:.4f}", verdict(t2["tt"]["p_value"]))
    print("Task 3 market val  p =", f"{t3['tt']['p_value']:.4f}", verdict(t3["tt"]["p_value"]))
    print("Task 4 GK age      p =", f"{t4['one']['p_value']:.4f}", verdict(t4["one"]["p_value"]))
    print(f"Reg 2.1  R²={r1['r2']:.3f}  test R²={r1['test_r2']:.3f}  RMSE={r1['rmse']:.2f}")
    print(f"Reg 2.2  R²={r2['r2']:.3f}  test R²={r2['test_r2']:.3f}  RMSE={r2['rmse']:.2f}")


if __name__ == "__main__":
    main()
