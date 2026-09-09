"""Data loading, cleaning, and feature-engineering for the FIFA World Cup
2026 analytics project.

Raw extracts (compiled from FIFA.com, Wikipedia, fbref.com, Transfermarkt,
and contemporaneous match reports) live in ``data/raw/``. This module turns
those three raw tables (matches, teams, players) into the analysis-ready
tables used across the notebooks, and is the single source of truth for how
every derived/engineered variable (rest days, knockout flag, rank/value
diffs, etc.) is computed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

KNOCKOUT_STAGES = {
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Third-place",
    "Final",
}

# Canonical team name -> set of variant spellings that may appear across
# the three raw sources scraped independently. Keys are the canonical form
# used throughout this project.
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

_VARIANT_TO_CANON = {
    variant: canon for canon, variants in NAME_VARIANTS.items() for variant in variants
}


def normalize_team_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    name = name.strip()
    return _VARIANT_TO_CANON.get(name, name)


def normalize_team_col(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].map(normalize_team_name)
    return df


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_matches(path: Path | str = RAW_DIR / "matches_raw.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    for col in ("team1", "team2", "penalty_winner"):
        if col in df.columns:
            df = normalize_team_col(df, col)
    for bool_col in ("went_to_extra_time", "went_to_penalties"):
        if bool_col in df.columns:
            df[bool_col] = (
                df[bool_col].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
            )
    df["team1_goals"] = df["team1_goals"].astype(int)
    df["team2_goals"] = df["team2_goals"].astype(int)
    df["goal_diff"] = df["team1_goals"] - df["team2_goals"]
    df["knockout"] = df["stage"].isin(KNOCKOUT_STAGES).astype(int)
    df["stage"] = pd.Categorical(
        df["stage"],
        categories=[
            "Group Stage",
            "Round of 32",
            "Round of 16",
            "Quarter-final",
            "Semi-final",
            "Third-place",
            "Final",
        ],
        ordered=True,
    )
    df = df.sort_values("match_number").reset_index(drop=True)
    return df


def load_teams(path: Path | str = RAW_DIR / "teams_raw.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df = normalize_team_col(df, "team")
    df["host"] = (
        df["host"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    ).astype(int)
    for col in (
        "fifa_rank_pretournament",
        "prev_wc_titles",
        "prev_wc_appearances",
        "squad_avg_age",
        "squad_market_value_eur_m",
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates(subset="team", keep="first").reset_index(drop=True)
    return df


def load_players(path: Path | str = RAW_DIR / "players_raw.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df = normalize_team_col(df, "team")
    df["position"] = df["position"].astype(str).str.strip().str.upper()
    for col in ("age", "appearances", "minutes_played", "goals", "assists", "yellow_cards", "red_cards"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["appearances"].fillna(0) >= 1].reset_index(drop=True)
    df["cards_per_app"] = (df["yellow_cards"].fillna(0)) / df["appearances"]
    df["goals_per_app"] = (df["goals"].fillna(0)) / df["appearances"]
    return df


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def compute_rest_days(matches: pd.DataFrame) -> pd.DataFrame:
    """Long-format (team, match_number, rest_days) table: days since that
    team's previous tournament match. A team's first match of the
    tournament has no prior match, so it is filled with the median rest
    days observed across all teams' non-first matches (a neutral,
    pre-tournament-knowable baseline).
    """
    long_rows = []
    for _, row in matches.iterrows():
        for side in ("team1", "team2"):
            long_rows.append(
                {"team": row[side], "match_number": row["match_number"], "date": row["date"]}
            )
    long_df = pd.DataFrame(long_rows).sort_values(["team", "date", "match_number"])
    long_df["prev_date"] = long_df.groupby("team")["date"].shift(1)
    long_df["rest_days"] = (long_df["date"] - long_df["prev_date"]).dt.days
    median_rest = long_df["rest_days"].median()
    long_df["rest_days"] = long_df["rest_days"].fillna(median_rest)
    return long_df[["team", "match_number", "rest_days"]]


def build_match_level_dataset(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Objective 2.1 dataset: 104 rows, one per match, target = goal_diff,
    with exactly 8 pre-match explanatory variables.
    """
    rest = compute_rest_days(matches)
    rest1 = rest.rename(columns={"team": "team1", "rest_days": "rest_days_1"})
    rest2 = rest.rename(columns={"team": "team2", "rest_days": "rest_days_2"})

    df = matches.merge(rest1, on=["match_number", "team1"], how="left")
    df = df.merge(rest2, on=["match_number", "team2"], how="left")

    t1 = teams.add_suffix("_1").rename(columns={"team_1": "team1"})
    t2 = teams.add_suffix("_2").rename(columns={"team_2": "team2"})
    df = df.merge(t1, on="team1", how="left").merge(t2, on="team2", how="left")

    out = pd.DataFrame()
    out["match_id"] = df["match_number"]
    out["team1"] = df["team1"]
    out["team2"] = df["team2"]
    out["goal_diff"] = df["goal_diff"]

    out["rank_diff"] = df["fifa_rank_pretournament_1"] - df["fifa_rank_pretournament_2"]
    out["age_diff"] = df["squad_avg_age_1"] - df["squad_avg_age_2"]
    out["value_diff"] = df["squad_market_value_eur_m_1"] - df["squad_market_value_eur_m_2"]
    out["titles_diff"] = df["prev_wc_titles_1"] - df["prev_wc_titles_2"]
    out["host_diff"] = df["host_1"] - df["host_2"]
    out["rest_diff"] = df["rest_days_1"] - df["rest_days_2"]
    out["same_confed"] = (df["confederation_1"] == df["confederation_2"]).astype(int)
    out["knockout"] = df["knockout"]

    return out.reset_index(drop=True)


def build_team_match_dataset(matches: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Objective 2.2 dataset: 208 rows (one per team per match), target =
    goals scored by that team in that match, with exactly 8 pre-match
    explanatory variables.
    """
    rest = compute_rest_days(matches)

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
    df = df.merge(rest, left_on=["team", "match_id"], right_on=["team", "match_number"], how="left")
    df = df.drop(columns=["match_number"])

    t = teams.copy()
    df = df.merge(t, on="team", how="left")
    df = df.merge(
        t.add_suffix("_opp").rename(columns={"team_opp": "opponent"}),
        on="opponent",
        how="left",
    )

    out = pd.DataFrame()
    out["match_id"] = df["match_id"]
    out["team"] = df["team"]
    out["opponent"] = df["opponent"]
    out["goals"] = df["goals"]

    out["team_rank"] = df["fifa_rank_pretournament"]
    out["opp_rank"] = df["fifa_rank_pretournament_opp"]
    out["team_value"] = df["squad_market_value_eur_m"]
    out["opp_value"] = df["squad_market_value_eur_m_opp"]
    out["team_age"] = df["squad_avg_age"]
    out["is_host"] = df["host"]
    out["rest_days"] = df["rest_days"]
    out["knockout"] = df["knockout"]

    return out.reset_index(drop=True)


def sanity_check_team_names(matches: pd.DataFrame, teams: pd.DataFrame, players: pd.DataFrame) -> dict:
    """Return sets of team names that appear in matches/players but are
    missing from the teams metadata table (should be empty once cleaned)."""
    team_set = set(teams["team"])
    match_teams = set(matches["team1"]) | set(matches["team2"])
    player_teams = set(players["team"])
    return {
        "missing_from_teams_table__matches": sorted(match_teams - team_set),
        "missing_from_teams_table__players": sorted(player_teams - team_set),
        "n_teams": len(team_set),
        "n_match_teams": len(match_teams),
    }


if __name__ == "__main__":
    matches = load_matches()
    teams = load_teams()
    players = load_players()
    print("matches:", matches.shape)
    print("teams:", teams.shape)
    print("players:", players.shape)
    print(sanity_check_team_names(matches, teams, players))
    m21 = build_match_level_dataset(matches, teams)
    m22 = build_team_match_dataset(matches, teams)
    print("2.1 dataset:", m21.shape)
    print("2.2 dataset:", m22.shape)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    matches.to_csv(PROCESSED_DIR / "matches_clean.csv", index=False)
    teams.to_csv(PROCESSED_DIR / "teams_clean.csv", index=False)
    players.to_csv(PROCESSED_DIR / "players_clean.csv", index=False)
    m21.to_csv(PROCESSED_DIR / "reg_goal_difference_104.csv", index=False)
    m22.to_csv(PROCESSED_DIR / "reg_team_goals_208.csv", index=False)
