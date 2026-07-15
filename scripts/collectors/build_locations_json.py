#!/usr/bin/env python3
"""Build data/pal_locations.json from collected paldb.cc data.

Inputs:
  data/palworld_pals.csv                      - canonical pal list (Name column)
  data/raw/paldb_locations_parsed.json        - per-pal page extract (fetch_locations.py)
  data/raw/paldex_region_tallies.json         - per-codename nearest-region tallies of
                                                in-game paldex habitat points
                                                (fetch_paldex_distribution.py)
  data/raw/paldb_codename_map.json            - internal codename -> English pal name
  data/breeding.json (optional)               - used to note breeding availability

Region derivation: each paldex habitat point (world coords) was projected to
in-game map coords and assigned to the nearest region label; regions covering
>= REGION_MIN_SHARE of a pal's points (or >= 3 points) are listed, ordered by
share. This is an approximation (nearest-label), noted in the output "notes".
"""
import csv
import json
import os
import re

ROOT = "/Users/ivanzhilinskiy/Projects/Pal"
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
OUT = os.path.join(DATA, "pal_locations.json")

REGION_MIN_SHARE = 0.05
REGION_MAX = 6

LEVEL_PREFIX = re.compile(r"^Lv\.[\d\-. ]+\s*")

# Names for spawner-code families whose spawns are NOT part of the in-game
# paldex habitat overlay (the World Tree is a separate level). The 1.0 islet
# codes (desertisland_*, volcanoiskand_*) are already covered by the paldex
# distribution tallies, which name the actual islets.
CODE_REGIONS = [
    (re.compile(r"^worldtree_"), "The World Tree"),
    (re.compile(r"^Sunreach Skies$"), "Sunreach Skies"),
    (re.compile(r"^Rotmist Root$"), "Rotmist Root (World Tree)"),
]

# Spawner-code families -> other_sources labels.
# aggregate=True: merge repeated rows into one line with a combined Lv range.
CODE_SOURCES = [
    (re.compile(r"mimic", re.I), "dungeon (as chest Mimog ambush)", False),
    (re.compile(r"^(grass|desert|glacier|volcanic|Sakurajima|tenraku)_grade_"),
     "dungeons", True),
    (re.compile(r"FBOSS", re.I), None, False),  # handled as alpha/dungeon boss
    (re.compile(r"^Captured Cage"),
     "caged pal in enemy camps (free to recruit)", True),
    (re.compile(r"^Pal Recruiter"),
     "Pal Recruiter (recruitable wandering pal)", True),
    (re.compile(r"Fishing Pond"), "fishing", True),
    (re.compile(r"^Raid \d"), "attacks bases during raids (catchable)", True),
    (re.compile(r"^IncidentSpawner"), "incident/outbreak events", True),
    (re.compile(r"^NPCCamp"), "enemy camps", True),
    (re.compile(r"^sanctuary_1"), "No. 1 Wildlife Sanctuary", False),
    (re.compile(r"^sanctuary_2"), "No. 2 Wildlife Sanctuary", False),
    (re.compile(r"^sanctuary_3"), "No. 3 Wildlife Sanctuary", False),
    (re.compile(r"^allarea_"), "roams all areas (rare wandering spawn)", False),
]

# Named dungeon/cavern spawner entries are already human-readable.
NAMED_DUNGEON = re.compile(
    r"(?:Cavern|Cave|Grotto|Root)(?:\s|$)")

# "<raid boss title> NN%" = that summoned raid boss drops this pal's egg
RAID_BOSS_EGG = re.compile(r"^(.*\S)\s+(\d+(?:\.\d+)?)%$")
NOT_RAID = re.compile(r"^(Pal Recruiter|Fishing Pond|Large Fishing Pond)")
UNKNOWN_CODE = re.compile(r"^[?？]+$")
LV_RANGE = re.compile(r"Lv\.?\s*(\d+)(?:\s*-\s*(\d+))?")


# Terraria-collab pals: paldb lists their wild spawner area as "???".
# Their actual home is the Terraria dungeon on the Sealed Realm of Terraria
# island (SE of Fisherman's Point, near the Isle of Eternal Summer) --
# confirmed via game8.co / bisecthosting.com guides (Tides of Terraria).
TERRARIA_REGION = ("Sealed Realm of Terraria - Terraria dungeon island "
                   "SE of Fisherman's Point, near Isle of Eternal Summer")
TERRARIA_PALS = {
    "Blue Slime", "Green Slime", "Red Slime", "Purple Slime",
    "Rainbow Slime", "Illuminant Slime", "Cave Bat", "Illuminant Bat",
    "Demon Eye", "Enchanted Sword", "Eye of Cthulhu",
}
EYE_OF_CTHULHU_ALPHA = ("Eye of Cthulhu (Lv. 45) - Sealed Realm of Terraria, "
                        "Eternal Summer Isle (-422, -795)")

# Astralym is the story final boss (with Zenara) inside the Sealed Sanctum /
# World Tree; in 1.0 it cannot be caught, bred, or hatched - defeating it
# only registers a Paldex entry (game8.co "Can You Catch Astralym?").
ASTRALYM_SOURCES = [
    "story final boss (fought alongside Zenara in the Sealed Sanctum, "
    "World Tree questline)",
    "not obtainable in 1.0 - defeating it only adds a Paldex entry "
    "(cannot be caught, bred, or hatched)",
]


def clean_region(item):
    return LEVEL_PREFIX.sub("", item).strip()


def split_dungeons(code):
    """paldb sometimes lists several dungeon names in one cell; separate them.
    e.g. 'Hillside Cavern Isolated Island Cavern' ->
         'Hillside Cavern, Isolated Island Cavern'"""
    return re.sub(r"\b(Cavern|Cave|Grotto|Root)\s+(?=[A-Z])", r"\1, ", code)


def main():
    pals = []
    with open(os.path.join(DATA, "palworld_pals.csv")) as f:
        for row in csv.DictReader(f):
            pals.append(row["Name"])

    parsed = json.load(open(os.path.join(RAW, "paldb_locations_parsed.json")))
    tallies = json.load(
        open(os.path.join(RAW, "paldex_region_tallies.json")))
    code_map = json.load(open(os.path.join(RAW, "paldb_codename_map.json")))
    name_to_code = {v: k for k, v in code_map.items()}

    # child -> list of non-self parent combos; self_only = breeds only true
    combo_parents = {}
    self_only = set()
    bpath = os.path.join(DATA, "breeding.json")
    if os.path.exists(bpath):
        b = json.load(open(bpath))
        for c in b.get("special_combos", []):
            child = c["child"]
            if c["parent_a"] == child and c["parent_b"] == child:
                self_only.add(child)
            else:
                combo_parents.setdefault(child, []).append(
                    f"{c['parent_a']} + {c['parent_b']}")

    def regions_from_distribution(codename):
        row = tallies.get(codename)
        if not row:
            return [], 0, 0
        tally = row.get("regions", {})
        total = sum(tally.values()) or 1
        regions = []
        for item, n in sorted(tally.items(), key=lambda kv: -kv[1]):
            if n / total >= REGION_MIN_SHARE or n >= 3:
                regions.append(clean_region(item))
            if len(regions) >= REGION_MAX:
                break
        return regions, row.get("day_points", 0), row.get("night_points", 0)

    out_pals = {}
    gaps = []
    for name in pals:
        p = parsed.get(name, {})
        entry = {
            "regions": [],
            "day_night": None,
            "alpha_locations": [],
            "egg_types": p.get("egg", []) or [],
            "other_sources": [],
            "notes": None,
        }

        # --- regions from in-game paldex habitat data ---
        codename = name_to_code.get(name)
        dist_regions, nday, nnight = ([], 0, 0)
        if codename:
            dist_regions, nday, nnight = regions_from_distribution(codename)
        entry["regions"] = list(dist_regions)

        # --- day/night from the Map card counts (server-rendered) ---
        day_ct = sum(m["count"] for m in p.get("maps", []) if m["time"] == "day")
        night_ct = sum(m["count"] for m in p.get("maps", []) if m["time"] == "night")
        if day_ct == 0 and night_ct == 0:
            day_ct, night_ct = nday, nnight
        if day_ct and night_ct:
            entry["day_night"] = "both"
        elif day_ct:
            entry["day_night"] = "day"
        elif night_ct:
            entry["day_night"] = "night"

        # --- walk spawner rows ---
        sources = []           # plain source strings
        agg = {}               # label -> [minLv, maxLv] for aggregated sources
        notes = []
        has_wild = False
        wild_unlisted = False

        def lv_bounds(lvl):
            m = LV_RANGE.search(lvl)
            if not m:
                return None
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            return lo, hi

        for s in p.get("spawners", []):
            loc = s["loc"]
            lvl = (s.get("level") or "").replace("–", "-")
            if s["alpha"]:
                if loc["type"] == "map":
                    entry["alpha_locations"].append(
                        f"{s['name']} ({lvl}) - {loc['map']} ({loc['coords']})")
                else:
                    code = loc.get("code", "")
                    if "FBOSS" in code:
                        entry["alpha_locations"].append(
                            f"{s['name']} ({lvl}) - as dungeon end-boss")
                    elif UNKNOWN_CODE.match(code):
                        entry["alpha_locations"].append(
                            f"{s['name']} ({lvl}) - location not listed on "
                            "source (???)")
                    elif code:
                        entry["alpha_locations"].append(
                            f"{s['name']} ({lvl}) - {split_dungeons(code)}")
                continue
            if loc["type"] == "map":
                has_wild = True
                continue
            code = loc.get("code", "")
            if not code:
                continue
            if UNKNOWN_CODE.match(code):
                has_wild = True
                wild_unlisted = True
                notes.append(
                    f"wild spawn ({lvl}) exists but its area is not listed "
                    "on the source (???)")
                continue
            m = RAID_BOSS_EGG.match(code)
            if m and not NOT_RAID.match(code):
                egg = lvl if lvl.endswith("Egg") else "egg"
                sources.append(
                    f"raid-boss reward: {m.group(1)} drops its {egg} "
                    f"({m.group(2)}%)")
                continue
            matched_src = False
            for rx, label, aggregate in CODE_SOURCES:
                if rx.search(code):
                    if label:
                        if lvl.endswith("Egg") and label == "dungeons":
                            label = f"dungeon loot egg ({lvl})"
                            sources.append(label)
                        elif aggregate:
                            b = lv_bounds(lvl)
                            if b:
                                cur = agg.setdefault(label, list(b))
                                cur[0] = min(cur[0], b[0])
                                cur[1] = max(cur[1], b[1])
                            else:
                                agg.setdefault(label, None)
                        else:
                            sources.append(
                                f"{label} ({lvl})" if lvl else label)
                    matched_src = True
                    break
            if matched_src:
                continue
            matched_region = False
            for rx, label in CODE_REGIONS:
                if rx.search(code):
                    entry["regions"].append(
                        label + (f" [{lvl}]" if lvl else ""))
                    has_wild = True
                    matched_region = True
                    break
            if matched_region:
                continue
            if NAMED_DUNGEON.search(code):
                sources.append(
                    f"dungeon: {split_dungeons(code)}"
                    + (f" ({lvl})" if lvl else ""))
                continue
            # remaining raw wild spawner code (e.g. green_A, yamijima_rock_pink_D)
            has_wild = True

        for label, b in agg.items():
            if b:
                rng = f"Lv. {b[0]}" if b[0] == b[1] else f"Lv. {b[0]}-{b[1]}"
                sources.append(f"{label} ({rng})")
            else:
                sources.append(label)

        if dist_regions:
            has_wild = True

        # de-dup, preserve order
        def dedup(seq):
            seen, out = set(), []
            for x in seq:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        entry["regions"] = dedup(entry["regions"])
        entry["other_sources"] = dedup(sources)
        entry["alpha_locations"] = dedup(entry["alpha_locations"])

        # --- curated overrides for source blind spots ---
        if name in TERRARIA_PALS:
            entry["regions"] = dedup(entry["regions"] + [TERRARIA_REGION])
            has_wild = True
            wild_unlisted = False
            notes = [n for n in notes if "???" not in n]
            if name == "Eye of Cthulhu":
                entry["alpha_locations"] = [EYE_OF_CTHULHU_ALPHA]
                notes.append("wild spawn is the alpha only "
                             "(Terraria dungeon boss)")
        if name == "Astralym":
            entry["other_sources"] = list(ASTRALYM_SOURCES)
            gaps.append("Astralym: not obtainable in 1.0 (story boss only); "
                        "no location/egg data applies")
            out_pals[name] = entry
            continue

        if not has_wild and not entry["regions"]:
            if entry["alpha_locations"]:
                entry["other_sources"].insert(
                    0, "no regular wild spawn - catch its boss/alpha "
                    "(see alpha_locations)")
            elif entry["egg_types"] or entry["other_sources"]:
                entry["other_sources"].insert(0, "no regular wild spawn")
            else:
                entry["other_sources"].append(
                    "no acquisition data found on source")
                gaps.append(f"{name}: no acquisition data on paldb.cc "
                            "(no spawner, egg, or boss entry)")
            if name in combo_parents:
                entry["other_sources"].append(
                    "breeding combo: " + "; ".join(combo_parents[name]))
            elif name in self_only:
                entry["other_sources"].append(
                    "breeding: same-species pair only (breeds true, no "
                    "cross-combo produces it)")
            else:
                entry["other_sources"].append("obtainable via breeding")
        if wild_unlisted and not entry["regions"]:
            gaps.append(f"{name}: has a wild spawn but its area is "
                        "unlisted on the source (???)")
        if notes:
            entry["notes"] = "; ".join(dedup(notes))
        out_pals[name] = entry

    result = {
        "game_version": "1.0",
        "updated": "2026-07-14",
        "pals": out_pals,
        "notes": [
            "regions are derived from the in-game Paldex habitat point data "
            "(paldb.cc DT_PaldexDistributionData.json): each habitat point is "
            "assigned to the nearest named map region label from paldb.cc map "
            "data, so region lists are a close approximation of the in-game "
            "habitat map, ordered by share of spawn points.",
            "day_night comes from the pal's day/night habitat point counts on "
            "paldb.cc ('both' = points in both overlays).",
            "alpha_locations coordinates are in-game map coordinates (X, Y) "
            "on the named map (Palpagos Islands or The World Tree); "
            "'as dungeon end-boss' means the alpha also appears as a boss at "
            "the end of randomized dungeons.",
            "other_sources are decoded from paldb.cc spawner-table entries "
            "(dungeons, caged pals in enemy camps, Pal Recruiter, fishing, "
            "base-raid attackers, incident/outbreak events, wildlife "
            "sanctuaries, raid-boss reward eggs).",
            "egg_types is the egg family the pal can hatch from (the game "
            "also uses Large/Huge size variants of the same family).",
        ],
        "gaps": [],
        "sources": [
            {"url": "https://paldb.cc/en/<PalName> (299 per-pal pages)",
             "what": "Spawner tables (wild/alpha/dungeon/raid spawn entries "
                     "with levels and map coordinates), hatchable egg type, "
                     "day/night habitat point counts",
             "fetched": "2026-07-14"},
            {"url": "https://paldb.cc/DataTable/UI/DT_PaldexDistributionData.json",
             "what": "in-game Paldex habitat spawn-point coordinates per pal "
                     "(day/night), reduced to nearest-region tallies in "
                     "data/raw/paldex_region_tallies.json",
             "fetched": "2026-07-14"},
            {"url": "https://paldb.cc/js/map_data_en.js",
             "what": "named map region labels with in-game coordinates "
                     "(regionData), used to turn habitat points into region "
                     "names; saved to data/raw/paldb_region_labels.json",
             "fetched": "2026-07-14"},
            {"url": "https://paldb.cc/en/Pals",
             "what": "internal codename -> English pal name mapping "
                     "(data/raw/paldb_codename_map.json)",
             "fetched": "2026-07-14"},
            {"url": "https://game8.co/games/Palworld/archives/609977",
             "what": "Astralym is the story final boss and cannot be "
                     "caught/owned in 1.0 (via web search summary)",
             "fetched": "2026-07-14"},
            {"url": "https://www.bisecthosting.com/blog/palworld-terraria-"
                     "dungeon-guide-location-walkthrough-new-pals-eye-of-"
                     "cthulhu-boss",
             "what": "Terraria-collab pals spawn in the Terraria dungeon on "
                     "the Sealed Realm of Terraria island SE of Fisherman's "
                     "Point; Eye of Cthulhu alpha at (-422, -795) "
                     "(via web search summary, with game8.co)",
             "fetched": "2026-07-14"},
        ],
    }
    # coverage-level gap notes
    n_no_reg = sum(1 for v in out_pals.values() if not v["regions"])
    n_no_dn = sum(1 for v in out_pals.values() if not v["day_night"])
    gaps.append(
        f"{n_no_reg} pals have no wild-spawn regions (legendary alpha-only, "
        "raid-boss-only, or dungeon/special encounters) - each states how to "
        "obtain it in other_sources")
    gaps.append(
        f"day_night is null for {n_no_dn} pals that have no in-game paldex "
        "habitat overlay (mostly the no-wild-spawn pals above)")
    gaps.append(
        "region names are nearest-label approximations of the in-game "
        "habitat map (see notes); exact spawn sub-areas and spawn rates are "
        "not captured")
    gaps.append(
        "merchant availability (Pal Merchants / Black Marketeer stock) is "
        "not covered by the sources used")
    result["gaps"] = gaps
    with open(OUT, "w") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(out_pals)} pals, {len(gaps)} gaps")

    # quick coverage stats
    n_reg = sum(1 for v in out_pals.values() if v["regions"])
    n_alpha = sum(1 for v in out_pals.values() if v["alpha_locations"])
    n_egg = sum(1 for v in out_pals.values() if v["egg_types"])
    n_dn = sum(1 for v in out_pals.values() if v["day_night"])
    print(f"regions: {n_reg}, alpha: {n_alpha}, egg: {n_egg}, day_night: {n_dn}")


if __name__ == "__main__":
    main()
