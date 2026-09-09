#!/usr/bin/env python3
"""
Build players_raw.csv for the 2026 FIFA World Cup by merging:
  - Wikipedia squad lists (team, position, age)
  - fotmob minutes-played leaderboard (appearances, minutes)
  - Wikipedia Goalscorers module data (goals)
  - fotmob yellow/red card leaderboards (cards)
  - manually curated assist figures for known top assist providers (from
    multiple cross-checked news sources: FIFA/Al Jazeera/thefootball.cafe/LiveScore/Sky Sports)
"""
import re
import csv
import unicodedata
from collections import defaultdict

BASE = "/workspace/wc2026-analysis/scripts"

COUNTRY_CODE_TO_TEAM = {
    "ALG": "Algeria", "ARG": "Argentina", "AUS": "Australia", "AUT": "Austria",
    "BEL": "Belgium", "BIH": "Bosnia and Herzegovina", "BRA": "Brazil", "CAN": "Canada",
    "CPV": "Cape Verde", "COL": "Colombia", "CRO": "Croatia", "CUW": "Curacao",
    "CZE": "Czechia", "COD": "DR Congo", "ECU": "Ecuador", "EGY": "Egypt",
    "ENG": "England", "FRA": "France", "GER": "Germany", "GHA": "Ghana",
    "HAI": "Haiti", "IRN": "Iran", "IRQ": "Iraq", "CIV": "Ivory Coast",
    "JPN": "Japan", "JOR": "Jordan", "MEX": "Mexico", "MAR": "Morocco",
    "NED": "Netherlands", "NZL": "New Zealand", "NOR": "Norway", "PAR": "Paraguay",
    "POR": "Portugal", "QAT": "Qatar", "KSA": "Saudi Arabia", "SCO": "Scotland",
    "SEN": "Senegal", "RSA": "South Africa", "KOR": "South Korea", "ESP": "Spain",
    "SWE": "Sweden", "SUI": "Switzerland", "TUN": "Tunisia", "TUR": "Turkiye",
    "USA": "USA", "URU": "Uruguay", "UZB": "Uzbekistan",
}

# Wikipedia section header -> canonical team name required by the task
SECTION_TO_TEAM = {
    "Czech Republic": "Czechia",
    "Mexico": "Mexico",
    "South Africa": "South Africa",
    "South Korea": "South Korea",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "Canada": "Canada",
    "Qatar": "Qatar",
    "Switzerland": "Switzerland",
    "Brazil": "Brazil",
    "Haiti": "Haiti",
    "Morocco": "Morocco",
    "Scotland": "Scotland",
    "Australia": "Australia",
    "Paraguay": "Paraguay",
    "Turkey": "Turkiye",
    "United States": "USA",
    "Curaçao": "Curacao",
    "Ecuador": "Ecuador",
    "Germany": "Germany",
    "Ivory Coast": "Ivory Coast",
    "Japan": "Japan",
    "Netherlands": "Netherlands",
    "Sweden": "Sweden",
    "Tunisia": "Tunisia",
    "Belgium": "Belgium",
    "Egypt": "Egypt",
    "Iran": "Iran",
    "New Zealand": "New Zealand",
    "Cape Verde": "Cape Verde",
    "Saudi Arabia": "Saudi Arabia",
    "Spain": "Spain",
    "Uruguay": "Uruguay",
    "France": "France",
    "Iraq": "Iraq",
    "Norway": "Norway",
    "Senegal": "Senegal",
    "Algeria": "Algeria",
    "Argentina": "Argentina",
    "Austria": "Austria",
    "Jordan": "Jordan",
    "Colombia": "Colombia",
    "DR Congo": "DR Congo",
    "Portugal": "Portugal",
    "Uzbekistan": "Uzbekistan",
    "Croatia": "Croatia",
    "England": "England",
    "Ghana": "Ghana",
    "Panama": "Panama",
}


def strip_accents(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


TURKISH_MAP = str.maketrans({"ı": "i", "İ": "I"})


def norm_name(s):
    """Normalize a player name for fuzzy matching."""
    s = s.replace("&nbsp;", " ")
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)  # [[target|display]] -> display
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)  # [[target]] -> target
    s = s.translate(TURKISH_MAP)
    s = strip_accents(s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Manual aliases for names that differ substantially between Wikipedia squad
# listings and the fotmob leaderboard (nicknames, reordered names, transliteration
# variants) that automated normalization cannot resolve.
NAME_ALIASES = {
    "hwang in beom": "in beom hwang",
    "oh hyeon gyu": "hyeon gyu oh",
    "maximiliano araujo": "maxi araujo",
    "musa al taamari": "mousa tamari",
    "hassan al haydos": "hassan al haidos",
    "abbosbek fayzullaev": "abbosbek fayzullayev",
    "homam ahmed": "homam elamin",
}


def last_token(s):
    toks = norm_name(s).split()
    return toks[-1] if toks else ""


# ---------------------------------------------------------------------------
# 1. Parse Wikipedia squads -> list of dicts {name, team, position, age}
# ---------------------------------------------------------------------------
def parse_wikipedia_squads():
    with open(f"{BASE}/wikipedia_squads.txt", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    squads = []
    current_team = None
    for line in lines:
        m = re.match(r"^###\s+(.+?)\s*$", line.strip())
        if m:
            header = m.group(1).strip()
            current_team = SECTION_TO_TEAM.get(header)
            continue
        if current_team is None:
            continue
        # table rows: | No | Pos | Player | DOB (age) | Caps | Goals | Club |
        row = line.strip()
        if not row.startswith("|"):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 4:
            continue
        no_cell, pos_cell = cells[0], cells[1]
        if pos_cell not in ("GK", "DF", "MF", "FW"):
            continue
        if not re.match(r"^\d+$", no_cell):
            continue
        player_cell = cells[2]
        age_cell = cells[3]
        player_name = re.sub(r"\(captain\)", "", player_cell).strip()
        player_name = re.sub(r"\s+", " ", player_name)
        age_m = re.search(r"aged\s+(\d+)", age_cell)
        age = int(age_m.group(1)) if age_m else None
        squads.append({
            "name": player_name,
            "team": current_team,
            "position": pos_cell,
            "age": age,
        })
    return squads


# ---------------------------------------------------------------------------
# 2. Parse fotmob minutes-played leaderboard -> {norm_name: (matches, minutes, display_name)}
# ---------------------------------------------------------------------------
def parse_fotmob_minutes():
    with open(f"{BASE}/fotmob_minutes.txt", encoding="utf-8") as f:
        text = f.read()
    result = {}
    pattern = re.compile(r"^\d+\.\s*\d+(.+?)Total matches:\s*(\d)(\d+)\s*$")
    for line in text.split("\n"):
        m = pattern.match(line.strip())
        if not m:
            continue
        name, matches, minutes = m.group(1), int(m.group(2)), int(m.group(3))
        key = norm_name(name)
        # keep first occurrence (list already de-duplicated by fotmob)
        if key not in result:
            result[key] = (matches, minutes, name)
    return result


# ---------------------------------------------------------------------------
# 3. Parse Wikipedia goalscorers module -> {(norm_name): (country_code, goals, display)}
# ---------------------------------------------------------------------------
def parse_goalscorers():
    with open(f"{BASE}/wikipedia_goalscorers.txt", encoding="utf-8") as f:
        text = f.read()
    result = {}
    # lines like: {"[[Name]]", "CODE", N },  or with piped links, or nested {{...}}
    pattern = re.compile(
        r'\{(?:\{"(\[\[[^\]]+\]\])",\s*"[^"]+"\s*\}|"(\[\[[^\]]+\]\])")\s*,\s*"([A-Z]{3})",\s*(\d+)\s*\}'
    )
    for m in pattern.finditer(text):
        raw_name = m.group(1) or m.group(2)
        code = m.group(3)
        goals = int(m.group(4))
        display = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", raw_name)
        display = re.sub(r"\[\[([^\]]+)\]\]", r"\1", display)
        display = display.replace("&nbsp;", " ")
        key = norm_name(display)
        result[key] = (code, goals, display)
    return result


# ---------------------------------------------------------------------------
# 4. Parse fotmob card leaderboards -> {norm_name: (yellow, red, display)}
# ---------------------------------------------------------------------------
def parse_yellow_cards():
    with open(f"{BASE}/fotmob_yellow_cards.txt", encoding="utf-8") as f:
        text = f.read()
    result = {}
    pattern = re.compile(r"^\d+\.\s*\d+(.+?)Red cards:\s*([01])(\d+)\s*$")
    for line in text.split("\n"):
        m = pattern.match(line.strip())
        if not m:
            continue
        name, red, yellow = m.group(1), int(m.group(2)), int(m.group(3))
        key = norm_name(name)
        result[key] = (yellow, red, name)
    return result


def parse_red_cards():
    with open(f"{BASE}/fotmob_red_cards.txt", encoding="utf-8") as f:
        text = f.read()
    result = {}
    pattern = re.compile(r"^\d+\.\s*\d+(.+?)Yellow cards:\s*([01])(\d+)\s*$")
    for line in text.split("\n"):
        m = pattern.match(line.strip())
        if not m:
            continue
        name, yellow, red = m.group(1), int(m.group(2)), int(m.group(3))
        key = norm_name(name)
        result[key] = (yellow, red, name)
    return result


# ---------------------------------------------------------------------------
# Manually curated / cross-checked assist counts for prominent players
# (from FIFA / Al Jazeera / thefootball.cafe / LiveScore / Sky Sports / AS)
# ---------------------------------------------------------------------------
ASSISTS_OVERRIDE = {
    "michael olise": 7,
    "kylian mbappe": 4,
    "lionel messi": 4,
    "bruno guimaraes": 4,
    "martin odegaard": 4,
    "brahim diaz": 4,
    "alexander isak": 3,
    "leandro trossard": 3,
    "roberto alvarado": 3,
    "florian wirtz": 3,
    "andreas schjelderup": 3,
    "anthony gordon": 3,
    "bukayo saka": 3,
    "ousmane dembele": 2,
    "harry kane": 2,
    "vinicius junior": 1,
    "julian quinones": 1,
    "ismaila sarr": 1,
    "mikel oyarzabal": 1,
    "jude bellingham": 1,
    "cristian romero": 0,
}


def build():
    squads = parse_wikipedia_squads()
    minutes_map = parse_fotmob_minutes()
    goals_map = parse_goalscorers()
    yellow_map = parse_yellow_cards()
    red_map = parse_red_cards()

    # merge card maps (they should agree; union them)
    cards_map = {}
    for k, (y, r, disp) in yellow_map.items():
        cards_map[k] = [y, r, disp]
    for k, (y, r, disp) in red_map.items():
        if k in cards_map:
            cards_map[k][0] = max(cards_map[k][0], y)
            cards_map[k][1] = max(cards_map[k][1], r)
        else:
            cards_map[k] = [y, r, disp]

    rows = []
    matched_minutes = 0
    matched_goals = 0
    matched_cards = 0
    seen_keys = set()

    for p in squads:
        key = norm_name(p["name"])
        if key in seen_keys:
            continue

        lookup_key = NAME_ALIASES.get(key, key)

        # Korean/Japanese-style two-token names are often given in reversed
        # (family-name given-name) order on Wikipedia versus (given-name
        # family-name) order on fotmob. Build a reversed candidate too.
        raw_tokens = p["name"].split()
        reversed_key = None
        if len(raw_tokens) == 2:
            reversed_key = norm_name(raw_tokens[1] + " " + raw_tokens[0])

        candidate_keys = [k for k in (lookup_key, reversed_key) if k]

        appearances = minutes = None
        for ck in candidate_keys:
            if ck in minutes_map:
                appearances, minutes, _ = minutes_map[ck]
                matched_minutes += 1
                break
        else:
            # fallback: try last-name only match against minutes map values
            lt = last_token(p["name"])
            candidates = [v for k2, v in minutes_map.items() if k2.split()[-1] == lt and lt]
            if len(candidates) == 1:
                appearances, minutes, _ = candidates[0]
                matched_minutes += 1

        if appearances is None:
            continue  # cannot verify appearances >= 1 -> skip per instructions

        goals = 0
        if key in goals_map:
            code, g, _ = goals_map[key]
            goals = g
            matched_goals += 1

        yellow = red = 0
        for ck in candidate_keys:
            if ck in cards_map:
                yellow, red, _ = cards_map[ck]
                matched_cards += 1
                break

        assists = ASSISTS_OVERRIDE.get(key, 0)

        seen_keys.add(key)
        rows.append({
            "player_name": p["name"],
            "team": p["team"],
            "position": p["position"],
            "age": p["age"],
            "appearances": appearances,
            "minutes_played": minutes,
            "goals": goals,
            "assists": assists,
            "yellow_cards": yellow,
            "red_cards": red,
        })

    print(f"Squad entries: {len(squads)}")
    print(f"Matched minutes/appearances: {matched_minutes}")
    print(f"Matched goals: {matched_goals}")
    print(f"Matched cards: {matched_cards}")
    print(f"Final rows: {len(rows)}")

    # also report any goalscorers we FAILED to place in the final rows (data-quality check)
    final_keys = {norm_name(r["player_name"]) for r in rows}
    missing_scorers = [(v[2], v[0], v[1]) for k, v in goals_map.items() if k not in final_keys]
    if missing_scorers:
        print("\nGoalscorers NOT matched to a squad row (need manual review):")
        for disp, code, g in missing_scorers:
            print(f"  {disp} ({code}) - {g} goal(s)")

    return rows


if __name__ == "__main__":
    rows = build()
    out_path = "/workspace/wc2026-analysis/data/raw/players_raw.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player_name", "team", "position", "age", "appearances",
                          "minutes_played", "goals", "assists", "yellow_cards", "red_cards"])
        for r in rows:
            writer.writerow([r["player_name"], r["team"], r["position"], r["age"],
                              r["appearances"], r["minutes_played"], r["goals"],
                              r["assists"], r["yellow_cards"], r["red_cards"]])
    print(f"\nWrote {len(rows)} rows to {out_path}")
