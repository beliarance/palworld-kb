#!/usr/bin/env python3
"""Assemble data/base_building.json from the paldb raw parse.

Inputs:
  --raw   raw parse produced by fetch_base_building.py
  --work  work-speed level tables (scraped from paldb /en/<Suitability> pages)
  --out   final data/base_building.json

Everything numeric comes from paldb.cc; rates/mechanics text is sourced from
1.0 guides (see sources[]). Unknown values stay null and are listed in gaps[].
"""

import argparse
import json
import re

UPDATED = "2026-07-14"

# workers: which work suitability operates the structure (paldb badge where
# present; plantations per paldb description text). None = no work needed.
WORKERS_OVERRIDE = {
    "Berry Plantation": "Planting + Watering + Gathering",
    "Wheat Plantation": "Planting + Watering + Gathering",
    "Tomato Plantation": "Planting + Watering + Gathering",
    "Lettuce Plantation": "Planting + Watering + Gathering",
    "Potato Plantation": "Planting + Watering + Gathering",
    "Carrot Plantation": "Planting + Watering + Gathering",
    "Onion Plantation": "Planting + Watering + Gathering",
    "Skillfruit Orchard": "Planting + Watering + Gathering",
    "Ancient Farm": "Planting + Watering + Gathering",
    "Mill": "Watering",
    "Breeding Farm": "any 1 male + 1 female pal pair (not a work suitability)",
    "Ancient Hatchery": "any 1 male + 1 female pal pair (not a work suitability)",
    "Human-Powered Generator": "any pal (converts labor to power, drains SAN)",
    "Ranch": "Farming (pal partner skill determines produce)",
}

CAPACITY = {
    "Palbox": "defines base area; base pal slots managed via Palbox (15 base workers by default, expandable via base missions)",
    "Ranch": "4 pals assigned",
    "Breeding Farm": "2 pals (1 male + 1 female)",
    "Ancient Hatchery": "2 pals (pair) + 10 egg slots, auto-incubates",
    "Egg Incubator": "1 egg",
    "Electric Egg Incubator": "1 egg",
    "Large Incubator": "10 eggs",
    "Large-Scale Electric Egg Incubator": "10 eggs",
    "Straw Pal Bed": "1 pal",
    "Fluffy Pal Bed": "1 pal",
    "Large Pal Bed": "1 pal (fits large pals)",
    "Ancient Pal Bed": "1 pal (fits large pals)",
    "Pal Pod": "1 pal",
    "Large Power Generator": "2 pals",
    "Ancient Power Generator": "2 pals",
}


def one_line(desc):
    if not desc:
        return None
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


def build_structures(raw):
    out = []
    for name, s in raw["structures"].items():
        work = s.get("work") or []
        if name in WORKERS_OVERRIDE:
            workers = WORKERS_OVERRIDE[name]
        elif work:
            parts = []
            for w in work:
                t = w["type"].replace("All", "any pal")
                lvl = w.get("value") or 1
                parts.append(f"{t} (min Lv{lvl})" if lvl > 1 else t)
            workers = " + ".join(parts)
        else:
            workers = None
        entry = {
            "name": name,
            "tech_level": s.get("tech_level"),
            "ancient_tech": bool(s.get("ancient_tech")),
            "materials": s.get("materials"),
            "workers": workers,
            "capacity": CAPACITY.get(name)
            or (f"{s['stats']['Worker Max']} worker slots"
                if s.get("stats", {}).get("Worker Max") else None),
            "power": s.get("energy_per_sec") is not None,
            "function": one_line(s.get("description")),
        }
        if s.get("energy_per_sec") is not None:
            entry["energy_per_sec"] = s["energy_per_sec"]
        out.append(entry)
    out.sort(key=lambda e: (e["tech_level"] or 0, e["name"]))
    return out


def build_foods(raw):
    out = []
    for name, f in raw["foods"].items():
        buff = None
        if f.get("work_speed"):
            dur = f.get("recovery_time")
            buff = f"Work Speed +{f['work_speed']}" + (
                f" for {dur}s" if dur else "")
        spoil = None
        if f.get("corruption"):
            spoil = f"spoils in {f['corruption'].lower()} (base timer)"
        out.append({
            "name": name,
            "nutrition": f.get("nutrition"),
            "sanity": f.get("sanity"),
            "work_speed_buff": buff,
            "spoil_notes": spoil,
            "notes": one_line(f.get("description")),
        })
    out.sort(key=lambda e: (e["nutrition"] or 0, e["name"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = json.load(open(args.raw, encoding="utf-8"))
    work_tables = json.load(open(args.work, encoding="utf-8"))

    pal_food = {}
    pal_hunger_rate_nondefault = {}
    for pal, d in raw["pals"].items():
        pal_food[pal] = d.get("food_amount")
        r = d.get("full_stomach_decrease_rate")
        if r is not None and r != 1:
            pal_hunger_rate_nondefault[pal] = r

    speed_tables = {}
    for k, tbl in work_tables.items():
        name = k.replace("_", " ")
        speed_tables[name] = {str(lv): tbl[lv] for lv in sorted(tbl, key=int)}

    data = {
        "game_version": "1.0",
        "updated": UPDATED,
        "structures": build_structures(raw),
        "foods": build_foods(raw),
        "pal_food_amount": dict(sorted(pal_food.items())),
        "pal_hunger_rate_multiplier_nondefault": dict(
            sorted(pal_hunger_rate_nondefault.items())),
        "rates": {
            "breeding_egg_interval_minutes": 5,
            "cake_per_egg": 1,
            "breeding_notes": (
                "Breeding Farm: paldb lists 'Real Time 5 Mins' per egg cycle; "
                "1 cake consumed per egg. Babysitter passive: +30% Breeding "
                "Speed and Hatching Speed for the assigned pal. Ancient "
                "Hatchery (tech 76): fully automated egg production + "
                "incubation, ~10s per cycle (guide-reported, preliminary), "
                "10 egg slots, boosts inheritance rate of rare skills, does "
                "NOT raise Mutated Egg chance."),
            "cakes_breeding": {
                "Cake": "baseline; required for any breeding, no bonus",
                "Mushroom Cake": "talents (IVs) grow slightly faster",
                "Vegetable Cake": "pair lays two eggs at once",
                "Extravagant Vegetable Cake":
                    "mutation more likely + talents grow faster "
                    "(sometimes miscalled 'Deluxe Vegetable Cake' in "
                    "EA-era guides)",
                "Special Cake":
                    "more likely to inherit multiple passive skills "
                    "from parents",
            },
            "plantation_cycles": [],
            "ranch_drop_interval_notes": (
                "No fixed interval: ranch drops are per-pal partner-skill "
                "procs tied to the work animation; higher work speed = more "
                "procs. 4-star condensation drastically increases drop "
                "quantity. 1.0 caveat (guide-reported): Farming suitability "
                "level 5+ can bug ranch-pal AI, so producers are often kept "
                "at effective Farming <=4."),
            "work_suitability_speed": (
                "Suitability level 1-10 maps to a work-speed value per "
                "suitability (see work_speed_by_level; paldb per-suitability "
                "pages). Most crafting-type jobs (Kindling, Handiwork, "
                "Medicine, Cooling): 50/80/140/240/400/680/1100/1900/3200/"
                "5400. Field jobs (Planting, Watering, Lumbering, Mining, "
                "Gathering): 50/70/100/140/190/260/370/510/720/1000; "
                "Gathering also multiplies harvest drops (DropNumRate x1 at "
                "Lv1 to x5.5 at Lv10); Lumbering/Mining apply a DamageRate "
                "multiplier; Transporting value = carry capacity (pieces); "
                "Farming 12..30; Generating Electricity 250..4000."),
            "work_suitability_boosts": (
                "Base paldex levels cap at 8; effective levels 9-10 come "
                "from stacking: (1) Applied <Task> Handbook I items: +1 to "
                "that suitability, permanent, per individual pal (pal must "
                "already have the suitability); (2) Pal Essence Condenser: "
                "each star rank raises one existing suitability +1, max rank "
                "raises all; (3) partner-skill auras: certain pals give "
                "base-wide +1 to one job for all other base pals (12 such "
                "auras in 1.0, do not stack); (4) passives, e.g. Farmhand +1 "
                "/ Ranch Master +2 Farming. Pal Labor Research Lab research "
                "grants %-bonuses (work speed +5/10%, plantation growth "
                "+5/10%, harvest yield +10%), not suitability levels."),
            "work_speed_by_level": speed_tables,
            "hunger_drain_notes": (
                "Per-species hunger stats on paldb: FoodAmount (appetite "
                "1-10, see pal_food_amount) and FullStomachDecreaseRate "
                "(multiplier, 1 = default; see "
                "pal_hunger_rate_multiplier_nondefault). Absolute satiety/"
                "sec baseline undocumented. Passives: Diet Lover -15% "
                "hunger rate, Dainty Eater -10%, Mastery of Fasting -20%, "
                "Glutton +10%, Bottomless Stomach +15%. World setting "
                "PalStomachDecreaceRate (default 1.0) scales all pal "
                "hunger. SAN: Workaholic -15% SAN drain; Hot Spring "
                "restores SAN (base rate 0.5), higher tiers restore more; "
                "Ancient Hot Spring also restores HP."),
        },
        "notes": [
            "Pal appetite ('Food' icons on paldb) = FoodAmount stat; 1.0 "
            "scale is 1-10 (observed values 1-9 across all 299 pals).",
            "FullStomachDecreaseRate is 1.0 for every pal in the 1.0 data — "
            "species hunger differences come from FoodAmount alone.",
            "All five cakes are breeding cakes: placed in the Breeding Farm "
            "chest (paldb 1.0 item descriptions confirm each effect, see "
            "rates.cakes_breeding). Nutrition/SAN: Cake 656/82, Mushroom "
            "676/84, Vegetable 696/87, Extravagant Vegetable 717/90, "
            "Special 738/92.",
            "'Deluxe Vegetable Cake' in EA-era guides = 'Extravagant "
            "Vegetable Cake' (canonical 1.0 name; no Deluxe cake exists).",
            "Cake CAN be eaten by hungry pals if placed in the Feed Box "
            "(EA-era report, unverified for 1.0); cake in the Breeding Farm "
            "chest is not eaten by base pals and reportedly does not spoil "
            "there (EA-era, unverified for 1.0). Feed Box eating order: "
            "left-to-right slots; Feed Box has an allowed-items filter "
            "(EA-era Steam reports, unverified for 1.0).",
            "power=true means the structure consumes electricity; "
            "energy_per_sec is paldb's consumption figure. Generators "
            "produce power scaled by the worker's Generating Electricity "
            "level (250 at Lv1 to 4000 at Lv10); Electric Pylon boosts "
            "generation speed (only one counts); Accumulator stores excess.",
            "Egg temperature-comfort mechanic still present in 1.0: eggs "
            "hatch faster at their preferred temperature; electric "
            "incubators auto-regulate it.",
            "High Quality (tech 28) and Ancient (tech 71) Monitoring Stands "
            "reduce SAN drain of working pals; Clinic/Ancient Clinic "
            "(Medicine Production worker) reduce SAN depletion and prevent "
            "illness.",
            "Hot Spring SAN restore rate 0.5 (base tier); High Quality "
            "restores more; Ancient Hot Spring restores the most SAN and "
            "also heals HP.",
            "DISCREPANCY: expeditions.json lists Pal Expedition Station at "
            "tech 15 (Wood 20, Stone 20, Paldium Fragment 5); paldb 1.0 "
            "page shows tech 22 (Wooden Board 10, Stone 100, Paldium "
            "Fragment 20). This file follows paldb.",
            "In 1.0 there is no plain 'Pal Bed': tiers are Straw Pal Bed "
            "(3) -> Fluffy Pal Bed (24) -> Large Pal Bed (36) -> Pal Pod "
            "(56) -> Ancient Pal Bed (73).",
        ],
        "gaps": [
            "Per-crop plantation yield_per_harvest and absolute growth-"
            "cycle seconds are undocumented in fetched sources (yield "
            "scales with gatherer DropNumRate; see plantation_cycles).",
            "Absolute baseline hunger (satiety/sec) and SAN drain/sec are "
            "undocumented; only relative multipliers known.",
            "Ancient Hatchery ~10s cycle and near-instant incubation are "
            "guide-reported (preliminary), not confirmed on paldb.",
            "Palbox exact base-pal capacity and Feed Box slot count are "
            "not listed on their paldb pages.",
            "Incubator hatch-speed multipliers (Electric ~1.5x is EA-era) "
            "and per-egg-size base hatch times unknown.",
            "Farmer's Special Dish has no Nutrition/SAN listed on paldb.",
            "Whether Applied <Task> Handbook tiers II+ exist is "
            "unconfirmed (only tier I pages found).",
            "Feed Box eating order / cake-in-feed-box behavior not yet "
            "re-verified for 1.0 (EA-era sources).",
        ],
        "sources": [
            {"url": "https://paldb.cc/en/<structure slug>",
             "what": "58 structure pages: tech level, ancient-tech flag, "
                     "build materials, energy use, worker slots, function "
                     "text (e.g. /en/Breeding_Farm, /en/Ancient_Hatchery)",
             "fetched": UPDATED},
            {"url": "https://paldb.cc/en/<food slug>",
             "what": "56 food item pages: Nutrition, SAN, spoil timer "
                     "(Corruption), work-speed buffs, cake breeding effects",
             "fetched": UPDATED},
            {"url": "https://paldb.cc/en/<pal name>",
             "what": "299 pal pages: FoodAmount (appetite) and "
                     "FullStomachDecreaseRate stats",
             "fetched": UPDATED},
            {"url": "https://paldb.cc/en/Kindling ... /en/Farming",
             "what": "12 work-suitability pages: exact work-speed value per "
                     "level 1-10, DropNumRate/DamageRate multipliers, "
                     "Research Lab effect lists",
             "fetched": UPDATED},
            {"url": "https://paldb.cc/en/Applied_Kindling_Handbook_I",
             "what": "handbook item text: permanent +1 suitability per pal",
             "fetched": UPDATED},
            {"url": "https://nodecraft.com/support/games/palworld/general/"
                    "palworld-work-suitability-level-10-explained",
             "what": "1.0 mechanisms for reaching work suitability 9-10",
             "fetched": UPDATED},
            {"url": "https://www.palmods.gg/guides/whats-new/"
                    "work-suitability",
             "what": "1.0 suitability boosts: condensation +1/star, "
                     "partner-skill base-wide auras",
             "fetched": UPDATED},
            {"url": "https://allthings.how/everything-that-changed-about-"
                    "breeding-in-palworld-1-0/",
             "what": "1.0 breeding: 1 cake = 1 egg, Ancient Hatchery "
                     "automation/batching, cake effects",
             "fetched": UPDATED},
            {"url": "https://xgamingserver.com/blog/"
                    "palworld-eggs-incubator-guide/",
             "what": "1.0 incubator tiers, capacities, temperature mechanic",
             "fetched": UPDATED},
            {"url": "https://xgamingserver.com/blog/palworld-sanity-guide/",
             "what": "1.0 SAN drain/recovery, hot spring rate 0.5, "
                     "Depressed status",
             "fetched": UPDATED},
            {"url": "https://paldb.cc/en/Passive_Skills",
             "what": "hunger/SAN passives: Diet Lover -15%, Dainty Eater "
                     "-10%, Mastery of Fasting -20%, Glutton +10%, "
                     "Bottomless Stomach +15%, Workaholic -15% SAN",
             "fetched": UPDATED},
            {"url": "https://thepalprofessor.com/plantations-guide/",
             "what": "plantation workflow and gathering-level yield scaling "
                     "(EA-era, unverified for 1.0)",
             "fetched": UPDATED},
            {"url": "https://steamcommunity.com/app/1623730/discussions/0/"
                    "595151065797631882/",
             "what": "Feed Box eating order left-to-right, allowed-items "
                     "filter (EA-era)",
             "fetched": UPDATED},
            {"url": "https://docs.palworldgame.com/settings-and-operation/"
                    "configuration/",
             "what": "world setting PalStomachDecreaceRate (pal hunger "
                     "slider)",
             "fetched": UPDATED},
            {"url": "https://www.neonlightsmedia.com/blog/"
                    "palworld-1-0-ranch-drops-guide",
             "what": "1.0 ranch drop mechanics, 4-star condensation drop "
                     "boost, Farming Lv5+ ranch AI bug",
             "fetched": UPDATED},
        ],
    }

    # plantation cycle stubs from paldb descriptions
    speed_note = {
        "Berry Plantation": "harvest time is quick (paldb)",
        "Wheat Plantation": "average time to harvest (paldb)",
    }
    for s in raw["structures"]:
        if s.endswith("Plantation"):
            data["rates"]["plantation_cycles"].append({
                "plantation": s,
                "yield_per_harvest": None,
                "cycle_notes": speed_note.get(
                    s, "takes time to harvest (paldb); exact base yield and "
                       "cycle seconds undocumented"),
            })
    data["rates"]["plantation_cycles"].append({
        "plantation": "(all)",
        "yield_per_harvest": None,
        "cycle_notes": (
            "Cycle: Planting -> growth timer -> Watering -> harvest via "
            "Gathering; harvest quantity scales with the gatherer's "
            "DropNumRate (x1 at Gathering Lv1 ... x5.5 at Lv10). Research "
            "Lab: Plantation Crop Growth Rate +5%/+10%, Plantation Harvest "
            "Yield +10%."),
    })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"structures={len(data['structures'])} foods={len(data['foods'])} "
          f"pal_food={sum(1 for v in pal_food.values() if v is not None)}"
          f"/{len(pal_food)}")


if __name__ == "__main__":
    main()
