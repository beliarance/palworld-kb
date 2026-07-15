#!/usr/bin/env python3
"""Build data/passives.json from scraped raw passive data.

Inputs (produced by fetch_passives.py and fetch_passives_palworldgg.py):
    paldb_passives_raw.json       (primary: paldb.cc, 114 standard pal passives)
    palworldgg_passives_raw.json  (cross-check: palworld.gg, partial list)

Usage:
    python3 build_passives_json.py --paldb paldb_passives_raw.json \
        --gg palworldgg_passives_raw.json \
        --pals /Users/ivanzhilinskiy/Projects/Pal/data/palworld_pals.csv \
        --out /Users/ivanzhilinskiy/Projects/Pal/data/passives.json
"""
import argparse
import csv
import json
import re

# Manual category overrides (name -> category); everything else is rule-based.
CATEGORY_OVERRIDES = {
    "Lucky": "mixed",
    "Legend": "mixed",
    "Vampiric": "mixed",
    "Idiosyncratic": "combat",
    "Immortality": "combat",
    "Serenity": "combat",
    "Impatient": "combat",
    "Heavily Armored": "combat",
    "Vanguard": "combat",
    "Stronghold Strategist": "combat",
    "Reload Master": "combat",
    "Motivational Leader": "work",
    "Mine Foreman": "work",
    "Logging Foreman": "work",
    "Insomnia": "work",
    "Philanthropist": "work",
    "Babysitter": "work",
    "Ranch Master": "work",
    "Farmhand": "work",
    "Noble": "utility",
    "Fine Furs": "utility",
    "Service-Minded": "utility",
    "Lavish Hospitality": "utility",
    "Wellness Watcher": "utility",
    "Healing Coach": "utility",
    "Mastery of Fasting": "work",
    "Heart of the Immovable King": "work",
    "Diet Lover": "work",
    "Workaholic": "work",
    "Dainty Eater": "work",
    "Positive Thinker": "work",
    "Lightfooted": "mount",
    "Skymarcher": "mount",
    # rank 5 (World Tree) set — categorized by their dominant effect
    "Twin-Edged Holy Blade": "combat",
    "Sanctified Meat Shield": "combat",
    "God of Destruction": "combat",
    "Demon’s Hand": "work",
    "World Tree Seedbed": "work",
    "Hermit Sage": "work",
    "Dimensional Leap": "mount",
}

MOUNT_PAT = re.compile(
    r"movement speed|move ?speed|max stamina|mounted jump|swim|on water", re.I)
COMBAT_PAT = re.compile(
    r"attack|defense|damage|life steal|health regen|cooldown", re.I)
WORK_PAT = re.compile(r"work speed|SAN|hunger|breeding|egg|suitability", re.I)


def categorize(name: str, rank: int, effect: str) -> str:
    if name in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[name]
    if rank < 0:
        return "detrimental"
    if MOUNT_PAT.search(effect) and not COMBAT_PAT.search(effect):
        return "mount"
    if WORK_PAT.search(effect) and COMBAT_PAT.search(effect):
        # attack/work tradeoffs keep their primary (first-listed) intent
        first = effect.split(",")[0]
        return "work" if WORK_PAT.search(first) else "combat"
    if WORK_PAT.search(effect):
        return "work"
    if COMBAT_PAT.search(effect):
        return "combat"
    return "utility"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paldb", required=True)
    ap.add_argument("--gg", required=True)
    ap.add_argument("--pals", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    paldb = json.load(open(args.paldb, encoding="utf-8"))
    gg = json.load(open(args.gg, encoding="utf-8"))
    with open(args.pals, encoding="utf-8") as f:
        pal_names = {row["Name"] for row in csv.DictReader(f)}

    gg_by_name = {p["name"].replace("’", "'"): p for p in gg["passives"]}

    passives, unmatched = [], []
    for p in paldb["tab_standard_114"]:
        name = p["name"]
        # pool badge: 'Pal' = wild random pool, 'RarePal' = lucky pals,
        # absent = never randomly rolled (species/other-exclusive).
        m = re.search(r"Weight (\d+)\s*(Pal|RarePal)?\s*$", p["tooltip_raw"])
        pool = m.group(2) if m else None
        in_random_pool = pool in ("Pal", "RarePal")

        exclusive = None
        native = None
        srcs = []
        for s in p["exclusive_pals"]:
            if s in pal_names:
                srcs.append(s)
            else:
                srcs.append(f"item: {s}")
                if not s.startswith("item"):
                    unmatched.append((name, s))
        if srcs:
            if in_random_pool:
                native = srcs  # guaranteed-native pals, but not exclusive
            else:
                exclusive = srcs
        rank5_world_tree = p["rank"] == 5

        entry = {
            "name": name.replace("’", "'"),
            "tier": p["rank"],
            "effects": p["effect"],
            "category": categorize(name, p["rank"], p["effect"]),
            "exclusive_source": exclusive,
            "breedable": (True if (in_random_pool or exclusive) else
                          None),
        }
        if rank5_world_tree:
            entry["breedable"] = None
            entry["world_tree_set"] = True
        if native:
            entry["native_pals"] = native
        if pool == "RarePal":
            entry["lucky_pal_pool"] = True
        # cross-check flag vs palworld.gg
        ggp = gg_by_name.get(entry["name"])
        if ggp:
            n1 = re.findall(r"[+-]?\d+(?:\.\d+)?%", entry["effects"])
            n2 = re.findall(r"[+-]?\d+(?:\.\d+)?%", ggp["effect"])
            if n1 != n2:
                entry["crosscheck_conflict_palworld_gg"] = ggp["effect"]
        passives.append(entry)

    if unmatched:
        print("WARN unmatched pal names:", unmatched)

    out = {
        "game_version": "1.0",
        "updated": "2026-07-14",
        "tier_scale": "paldb.cc rank: -3..-1 detrimental, 1..4 positive, "
                      "5 = new 1.0 'World Tree' gold tier (weight 5, not in "
                      "wild random pool)",
        "passives": passives,
        "notes": [
            "Primary source is paldb.cc's 'Pal Passive Skills /114' tab (1.0 data). "
            "paldb also has an extended 298-entry tab, but the extra 184 entries are "
            "gear/accessory/sphere-module/NPC-boss effects, not obtainable pal passives; "
            "they are excluded here.",
            "tier uses paldb's rank scale: -3..-1 detrimental, 1..4 positive, 5 = new 1.0 "
            "gold 'World Tree' tier.",
            "'native_pals' (extra field) lists pals that always spawn with a passive that "
            "is ALSO in the wild random pool (e.g. Heavyweight on Kingpaca) - these are "
            "not exclusives. 'exclusive_source' is reserved for passives absent from the "
            "random pool.",
            "'lucky_pal_pool': true marks Lucky as rolled only by rare/shiny ('lucky') "
            "wild pals (paldb 'RarePal' pool tag).",
            "Weight field on paldb: most pool passives are Weight 100; the new 1.0 "
            "additions (Remarkable Craftsmanship, Demon God, Diamond Body, Swift, "
            "Eternal Engine, Vampiric, Mastery of Fasting, Heart of the Immovable King, "
            "King of the Waves, Lavish Hospitality, Ranch Master, Lightfooted) are "
            "Weight 5, i.e. rare random rolls.",
            "CONFLICT vs docs/breeding_mechanics.md section 9: the doc's game8 table "
            "lists element Emperor/Lord passives at +20%; paldb 1.0 shows 30% for all "
            "nine (Celestial/Flame/Ice/Earth/Spirit Emperor, Lord of Lightning/the Sea/"
            "the Underworld, Divine Dragon). Doc's +30% values for Eternal Flame/Invader/"
            "Siren of the Void match paldb.",
            "CONFLICT vs docs/breeding_mechanics.md section 10: doc claims Eternal Engine "
            "= 'Move Speed +75%, Attack +20%, Max Stamina +75%' (PRELIMINARY tag); paldb "
            "1.0 shows only 'Max stamina +75% (rideable pals only)'. Doc value looks wrong "
            "or outdated.",
            "Doc's Legend 'Move Speed +15-20%' resolves to exactly +20% per paldb.",
            "Doc values confirmed by paldb: Demon God (Atk +30%, Def +5%), Remarkable "
            "Craftsmanship (WS +75%), Musclehead, Ferocious, Burly Body, Lucky, Hooligan "
            "(Atk +15%, WS -10%), Conceited (WS +10%, Def -10%), Artisan, Work Slave, "
            "Serious, Swift/Runner/Nimble, Vanguard, Stronghold Strategist, Motivational "
            "Leader, Mine/Logging Foreman.",
            "Lord of the Underworld is native to both Necromus and Frostallion Noct per "
            "paldb (doc lists only Necromus).",
            "Legend is native to 6 pals in 1.0: Paladius, Necromus, Frostallion, "
            "Frostallion Noct, Jetragon, and new legendary Neptilius (which also has "
            "exclusive Lunker). Hartalis has exclusive Savior; Xenolord has Invader; "
            "Otherworldly Cells is native to the Xeno line (Xenovader/Xenogard/Xenolord).",
            "The seven tier-5 'World Tree' passives (Twin-Edged Holy Blade, Sanctified "
            "Meat Shield, Demon's Hand, World Tree Seedbed, Hermit Sage, Dimensional "
            "Leap, God of Destruction) all carry 'World Tree resources will not vanish "
            "when approached' and Weight 5, and are NOT in the wild pool. These are the "
            "best candidates for the 'mutation-exclusive' passives mentioned in "
            "docs/breeding_mechanics.md section 7 (which says FIVE) - count and "
            "acquisition method unconfirmed.",
            "Mercy Hit is granted by items (Ring of Mercy, Pal Tamers Glasses) per "
            "paldb's source links, though it is also tagged as being in the pal pool.",
            "palworld.gg cross-check: 54 of its 58 listed pal passives overlap this set; "
            "0 numeric conflicts. Its remaining 4 (Aerial Dash +1..+4) are gear effects.",
        ],
        "gaps": [
            "Mutation-exclusive passive names unconfirmed: docs say five unique mutation "
            "passives exist; paldb does not label any passive as mutation-sourced. The "
            "seven tier-5 World Tree passives are the likely set (breedable=null on them).",
            "Acquisition source unknown (not in wild pool, no exclusive pal listed) for: "
            "Babysitter, Idiosyncratic, Immortality, Heavily Armored, Skymarcher - "
            "possibly raid/expedition/research or event rewards.",
            "Breedability of tier-5 World Tree passives and of the five unknown-source "
            "tier-4 passives above is unverified (null).",
            "Inheritance behavior of species-exclusive passives beyond Legend/Emperors "
            "(e.g. Savior, Lunker, Invader, Siren of the Void, Eternal Flame) assumed "
            "breedable=true by analogy with Legend; not individually verified.",
            "game8/fandom/wiki.gg could not be fetched (bot-blocked) - no third-source "
            "verification of the 1.0 numeric changes (e.g. Emperor 20%->30%).",
        ],
        "sources": [
            {"url": "https://paldb.cc/en/Passive_Skills",
             "what": "primary: full 114-passive 1.0 list with ranks, effect values, "
                     "weights, pool tags, native/exclusive pal links (+ extended "
                     "298-entry gear/NPC tab, excluded)",
             "fetched": "2026-07-14"},
            {"url": "https://palworld.gg/passive-skills",
             "what": "cross-check: 58 passives with rank + effect text; 54 overlap, "
                     "0 numeric conflicts",
             "fetched": "2026-07-14"},
            {"url": "https://xgamingserver.com/blog/palworld-mutations-guide/",
             "what": "checked for mutation-exclusive passive names; confirms mutated "
                     "pals get a unique passive but names not listed",
             "fetched": "2026-07-14"},
        ],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(e["category"] for e in passives))
    print("total:", len(passives),
          "| exclusives:", sum(1 for e in passives if e["exclusive_source"]),
          "| gg cross-checked:",
          sum(1 for e in passives if e["name"] in gg_by_name))


if __name__ == "__main__":
    main()
