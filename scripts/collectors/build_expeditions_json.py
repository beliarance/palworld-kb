#!/usr/bin/env python3
"""Build data/expeditions.json from the parsed palpedia expedition data.

Usage: python3 build_expeditions_json.py expeditions_raw.json > ../../data/expeditions.json
(expeditions_raw.json comes from parse_expeditions.py)
"""
import json
import sys

FIREPOWER = {"25K": 25000, "56K": 56000, "144K": 144000, "209K": 209000,
             "286K": 286000, "375K": 375000, "476K": 476000, "589K": 589000,
             "851K": 851000, "1.6M": 1600000, "2.1M": 2100000}

# Element requirement per expedition (from palpedia.net element icons +
# palworld.wiki.gg Expeditions table). Value = element name; count comes
# from the "Element x N" multiplier field (= number of Pals of that
# element required, per wiki.gg).
ELEMENTS = {
    "Verdant Hollow": None,
    "Secret Realm of the Forest": "Grass",
    "Blazing Cavern": "Fire",
    "Hidden Sanctum of the Desert": "Ground",
    "Astral Frost Cavern": "Ice",
    "Celestial Sakura Cavern": "Water",
    "Dark Cave of Feybreak": "Dark",
    "Sunreach Isle": "Dragon",
    "World Tree Subterrenean City Ruins": None,
    "Rayne Syndicate Smuggling Warehouse": "Neutral",
    "Free Pal Alliance Illicit Trading Post": "Grass",
    "Eternal Pyre's Forbidden Market": "Fire",
    "PIDF Illegal Factory": "Ground",
    "PAL Genetic Research Laboratory": "Ice",
    "Moonflower's Secret Hideout": "Water",
    "Ancient Feybreak Ruins": "Dark",
    "Sunreach Dragon Husk": "Dragon",
    "The World Tree's Forbidden Area": None,
}

# Missions that did not exist before 1.0 (Sunreach / World Tree content),
# or whose values were rebalanced in 1.0 -> preliminary flag.
NEW_IN_1_0 = {"Sunreach Isle", "World Tree Subterrenean City Ruins",
              "Sunreach Dragon Husk", "The World Tree's Forbidden Area"}

HARD_MODE_UNLOCK = {"Rayne Syndicate Smuggling Warehouse",
                    "Free Pal Alliance Illicit Trading Post",
                    "Eternal Pyre's Forbidden Market", "PIDF Illegal Factory",
                    "PAL Genetic Research Laboratory",
                    "Moonflower's Secret Hideout", "Ancient Feybreak Ruins",
                    "Sunreach Dragon Husk", "The World Tree's Forbidden Area"}


def build(raw_path):
    raw = json.load(open(raw_path))
    missions = []
    for e in raw:
        name = e["name"]
        elem = ELEMENTS.get(name)
        m = {
            "name": name,
            "category": e["section"],
            "duration_hours": e["duration_minutes"] / 60,
            "duration_minutes": e["duration_minutes"],
            "difficulty": e["difficulty"],
            "required_level": None,
            "required_firepower": FIREPOWER.get(e["firepower"]),
            "element_requirement": (
                {"element": elem, "pals_required": e["element_multiplier"]}
                if elem else None),
            "unlock": {
                "boss": e["unlock_boss"],
                "tower": e["unlock_tower"],
                "boss_difficulty": ("Hard" if name in HARD_MODE_UNLOCK
                                    else "Normal"),
            },
            "rewards": [
                {"slot": r["slot"], "item": r["item"],
                 "quantity": r["quantity"], "chance_pct": r["chance_pct"]}
                for r in e["rewards"]
            ],
            "preliminary": name in NEW_IN_1_0,
        }
        missions.append(m)
    return missions


if __name__ == "__main__":
    doc = {
        "game_version": "1.0",
        "updated": "2026-07-14",
        "unlock": {
            "structure": "Pal Expedition Station",
            "tech_level": 15,
            "tech_points": 2,
            "materials": {"Wood": 20, "Stone": 20, "Paldium Fragment": 5},
            "workload": 10000,
            "limit_per_base": 1,
            "additional_requirement":
                "Defeat at least one tower faction leader; each expedition "
                "is gated behind a specific tower boss (Normal or Hard mode)",
        },
        "mechanics": {
            "pals_per_expedition": 100,
            "notes": [
                "Pals are sent from the Palbox; a Pal on expedition cannot "
                "be used in the party, at a base, or for condensation until "
                "it returns. Party/base Pals cannot be selected.",
                "Each expedition has a minimum recommended Firepower; below "
                "it rewards are reduced, above it reward quantities increase "
                "(since v0.6.4 exceeding Firepower no longer shortens "
                "duration).",
                "Firepower per Pal = (Attack + Defense + HP/5) x rank^2, "
                "where rank is condensation stars: 0*=x1, 1*=x4, 2*=x9, "
                "3*=x16, 4*=x25.",
                "Most expeditions additionally require N Pals of a specific "
                "element (element_requirement.pals_required).",
                "Expeditions cannot fail; rewards scale with Firepower.",
                "Auto-assign picks the highest-Firepower eligible Pals.",
                "Pal Labor Research Laboratory research (mainly the Mining "
                "tree) can boost expedition rewards / reduce duration.",
                "Reward slots roll independently; slots listing several "
                "items with <100% chance pick one item from a weighted pool.",
            ],
        },
        "missions": build(sys.argv[1]),
        "notes": [
            "Expeditions introduced pre-1.0 in patch v0.4.11 (Feybreak era, "
            "Jan 2025); hard-mode expeditions and firepower->quantity "
            "scaling added by v0.6.4.",
            "1.0 (update 1.100.427) extended expeditions into Sunreach and "
            "the World Tree and appears to have rebalanced VeryHard "
            "expeditions (pre-1.0 wiki listed them at 60 min / 500K "
            "firepower; 1.0 data shows 120 min / 1.6M).",
            "VeryHard expeditions each guarantee a specific raid-slab "
            "fragment (e.g. Eternal Pyre's Forbidden Market and PAL Genetic "
            "Research Laboratory -> Xenolord Slab Fragment) plus a Kinship "
            "Peach.",
            "World Tree expeditions are the expedition source of Ancient "
            "Relics and Radiant Gems (1.0 Awakening mechanic).",
        ],
        "gaps": [
            "World Tree expedition unlock boss name hidden as '???' on "
            "palpedia (story spoiler); World Tree Subterrenean City Ruins "
            "unlock condition unconfirmed (presumed World Tree boss, Normal "
            "mode).",
            "Sunreach Isle reward table as parsed has no slot-3 entry; "
            "possibly an unparsed sphere row on the source page.",
            "Exact reward-quantity scaling curve vs Firepower not published.",
            "Whether passive skills/traits (as opposed to raw stats and "
            "condensation rank) affect Firepower is unconfirmed; the "
            "published formula uses only Attack/Defense/HP and rank.",
            "Player level requirements: none documented (gating is tech "
            "level 15 + tower bosses + firepower).",
            "Palpedia lists Auri & Shaolong (Sunreach boss) at 'PIDF "
            "Tower' - likely a source labeling quirk; actual Sunreach "
            "tower name unverified.",
        ],
        "sources": [
            {"url": "https://www.palpedia.net/expeditions",
             "what": "Full 1.0 mission list: names, durations, difficulty, "
                     "firepower, element multipliers, unlock bosses, "
                     "complete reward pools with quantities and chances",
             "fetched": "2026-07-14"},
            {"url": "https://palworld.wiki.gg/wiki/Expeditions",
             "what": "Mechanics: 100-pal cap, firepower formula, element "
                     "requirement meaning, v0.4.11/v0.6.4 history, research "
                     "lab bonuses; pre-1.0 mission table for comparison",
             "fetched": "2026-07-14"},
            {"url": "https://palworld.wiki.gg/wiki/Pal_Expedition_Station",
             "what": "Station unlock (tech 15, 2 points), build materials "
                     "(20 Wood, 20 Stone, 5 Paldium Fragment), workload, HP",
             "fetched": "2026-07-14"},
            {"url": "https://xgamingserver.com/blog/palworld-1-0-patch-notes/",
             "what": "1.0 patch notes: expedition content extended into "
                     "Sunreach and the World Tree; update 1.100.427",
             "fetched": "2026-07-14"},
            {"url": "https://game8.co/games/Palworld/archives/492119",
             "what": "Corroboration of unlock flow and one-station-per-base "
                     "limit (via search snippets; page fetch failed)",
             "fetched": "2026-07-14"},
        ],
    }
    json.dump(doc, sys.stdout, indent=1, ensure_ascii=False)
