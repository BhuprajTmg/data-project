#!/usr/bin/env python3
"""HIT140 Assessment 3 — data cleaning

Reads the original Excel workbook and writes cleaned tables.

Run from the repository root:

    python code/clean_data.py

Outputs (data/cleaned/):
    matches.csv
    teams.csv
    players.csv
    team_roster.csv   (pre-match roster mix from age and position only)
    fifa_data_cleaned.xlsx
    cleaning_log.txt
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "data" / "original" / "fifa_data_original.xlsx"
CLEANED = ROOT / "data" / "cleaned"

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

KNOCKOUT_STAGES = {
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Third-place",
    "Final",
}

TEAM_NUMERIC = [
    "fifa_rank_pretournament",
    "prev_wc_titles",
    "prev_wc_appearances",
    "squad_avg_age",
    "squad_market_value_eur_m",
]
PLAYER_NUMERIC = [
    "age",
    "appearances",
    "minutes_played",
    "goals",
    "assists",
    "yellow_cards",
    "red_cards",
]


def canon(name):
    if not isinstance(name, str):
        return name
    return VARIANT_TO_CANON.get(name.strip(), name.strip())


def as_bool(series):
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


def clean_matches(raw):
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["team1"] = df["team1"].map(canon)
    df["team2"] = df["team2"].map(canon)
    df["team1_goals"] = pd.to_numeric(df["team1_goals"], errors="coerce").astype("Int64")
    df["team2_goals"] = pd.to_numeric(df["team2_goals"], errors="coerce").astype("Int64")
    df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce")
    df["went_to_extra_time"] = as_bool(df["went_to_extra_time"]).astype(int)
    df["went_to_penalties"] = as_bool(df["went_to_penalties"]).astype(int)
    df["knockout"] = df["stage"].isin(KNOCKOUT_STAGES).astype(int)
    # Knockout matches have no group; penalty winner is blank unless the match went to penalties
    df["group"] = df["group"].fillna("Not applicable").astype(str)
    df["penalty_winner"] = df["penalty_winner"].fillna("Not applicable").map(
        lambda x: canon(x) if x != "Not applicable" else x
    )
    df = df.drop_duplicates("match_number").sort_values("match_number").reset_index(drop=True)
    return df


def clean_teams(raw):
    df = raw.copy()
    df["team"] = df["team"].map(canon)
    df["host"] = as_bool(df["host"]).astype(int)
    df["confederation"] = df["confederation"].astype(str).str.strip()
    for col in TEAM_NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates("team").sort_values("team").reset_index(drop=True)
    return df


def clean_players(raw):
    df = raw.copy()
    df["player_name"] = df["player_name"].astype(str).str.strip()
    df["team"] = df["team"].map(canon)
    df["position"] = df["position"].astype(str).str.strip()
    for col in PLAYER_NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates(["player_name", "team"]).reset_index(drop=True)
    return df


def build_roster(players):
    """Pre-match squad mix. Uses only age and position, not this tournament's
    minutes, goals or cards (those would leak the result).
    """
    g = players.groupby("team", sort=True)
    out = pd.DataFrame(
        {
            "roster_size": g.size(),
            "n_fw": g["position"].apply(lambda s: int((s == "FW").sum())),
            "n_mf": g["position"].apply(lambda s: int((s == "MF").sum())),
            "n_df": g["position"].apply(lambda s: int((s == "DF").sum())),
            "n_gk": g["position"].apply(lambda s: int((s == "GK").sum())),
            "youth_share": g["age"].apply(lambda s: float((s < 23).mean())),
            "veteran_share": g["age"].apply(lambda s: float((s >= 32).mean())),
            "age_spread": g["age"].std(ddof=1),
        }
    ).reset_index()
    out["fwd_share"] = out["n_fw"] / out["roster_size"]
    return out


def quality_checks(matches, teams, players, roster):
    lines = []
    lines.append("HIT140 Assessment 3 — cleaning log")
    lines.append("")
    lines.append(f"Matches: {len(matches)} rows (expected 104)")
    lines.append(f"Teams:   {len(teams)} rows (expected 48)")
    lines.append(f"Players: {len(players)} rows (expected 1016)")

    match_teams = set(matches["team1"]) | set(matches["team2"])
    team_names = set(teams["team"])
    player_teams = set(players["team"])
    lines.append(f"Match teams missing from teams table: {sorted(match_teams - team_names) or 'none'}")
    lines.append(f"Player teams missing from teams table: {sorted(player_teams - team_names) or 'none'}")

    lines.append(f"Missing values in matches after cleaning: {int(matches.isna().sum().sum())}")
    lines.append(f"Missing values in teams after cleaning:   {int(teams.isna().sum().sum())}")
    lines.append(f"Missing values in players after cleaning: {int(players.isna().sum().sum())}")

    player_goals = int(players["goals"].sum())
    match_goals = int(matches["team1_goals"].sum() + matches["team2_goals"].sum())
    own_goals = match_goals - player_goals
    lines.append(f"Player goals: {player_goals}")
    lines.append(f"Match goals:  {match_goals}")
    lines.append(f"Own goals implied: {own_goals}  (player goals + own goals should equal match goals)")
    lines.append(f"Red cards (players table): {int(players['red_cards'].sum())}")
    lines.append(f"Knockout matches: {int(matches['knockout'].sum())}")
    lines.append(f"Group-stage matches: {int((matches['knockout'] == 0).sum())}")
    lines.append(f"Roster rows: {len(roster)} (one per team)")
    lines.append("Roster features use player age and position only (pre-match).")
    return "\n".join(lines) + "\n"


def main():
    if not ORIGINAL.exists():
        raise FileNotFoundError(f"Original workbook not found: {ORIGINAL}")

    CLEANED.mkdir(parents=True, exist_ok=True)

    matches = clean_matches(pd.read_excel(ORIGINAL, sheet_name="matches"))
    teams = clean_teams(pd.read_excel(ORIGINAL, sheet_name="teams"))
    players = clean_players(pd.read_excel(ORIGINAL, sheet_name="players"))
    roster = build_roster(players)

    matches.to_csv(CLEANED / "matches.csv", index=False)
    teams.to_csv(CLEANED / "teams.csv", index=False)
    players.to_csv(CLEANED / "players.csv", index=False)
    roster.to_csv(CLEANED / "team_roster.csv", index=False)

    with pd.ExcelWriter(CLEANED / "fifa_data_cleaned.xlsx", engine="openpyxl") as writer:
        matches.to_excel(writer, sheet_name="matches", index=False)
        teams.to_excel(writer, sheet_name="teams", index=False)
        players.to_excel(writer, sheet_name="players", index=False)
        roster.to_excel(writer, sheet_name="team_roster", index=False)

    log = quality_checks(matches, teams, players, roster)
    (CLEANED / "cleaning_log.txt").write_text(log, encoding="utf-8")
    print(log)
    print(f"Wrote cleaned files to {CLEANED}")


if __name__ == "__main__":
    main()
