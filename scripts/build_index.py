#!/usr/bin/env python3
"""Строит data/index.json — денормализованный индекс по палам.

Одна выгрузка вместо ручной сшивки 5 файлов: по каждому палу всё сразу
(статы, работы, ранч-продукция, дропы, где ловить, ранг бридинга, теги partner skill),
плюс обратные индексы для мгновенных ответов:
  ranch_produce   {предмет: [палы с уровнем Farming]}   — кто производит на ранче
  drops           {предмет: [палы]}                      — кто дропает
  work            {задача: [[пал, уровень], ...]}        — ранжированные рабочие
  partner_tags    {тег: [палы]}                          — fishing/capture/player_buff/...

Запуск: python3 scripts/build_index.py  (перезапускать после изменения данных в data/)
"""

import csv
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

WORK_COLS = ["Kindling", "Watering", "Planting", "Generating_Electricity", "Handiwork",
             "Gathering", "Lumbering", "Mining", "Medicine", "Cooling", "Transporting", "Farming"]

PARTNER_TAGS = {
    "fishing": r"fishing",
    "capture": r"captur|sphere consumption|spheres home",
    "player_attack": r"player'?s? attack|player and party|attack type to",
    "drops_boost": r"drop \d+~?\d*% more|more items when defeated",
    "mount_combat": r"can be ridden.*(attack|damage)",
    "base_work": r"work speed|when assigned",
}


def load():
    pals = {}
    with open(DATA / "palworld_pals.csv") as f:
        for r in csv.DictReader(f):
            pals[r["Name"]] = {
                "number": r["Number"],
                "elements": [e for e in (r["Element_1"], r["Element_2"]) if e],
                "work": {w: int(r[w]) for w in WORK_COLS if r[w]},
            }
    combat = json.loads((DATA / "pals_combat.json").read_text())
    loc = json.loads((DATA / "pal_locations.json").read_text())["pals"]
    br = json.loads((DATA / "breeding.json").read_text())
    tiers = json.loads((DATA / "tier_lists.json").read_text())
    return pals, combat, loc, br, tiers


def main():
    pals, combat, loc, br, tiers = load()

    # тир-листы: в каких списках пал упомянут
    tier_hits = {}
    def note_tier(cat, entries):
        for rank, e in enumerate(entries, 1):
            tier_hits.setdefault(e["name"], []).append(f"{cat}#{rank}")
    for k, v in tiers.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and "name" in v[0]:
            note_tier(k.replace("best_", ""), v)
    for task, v in (tiers.get("best_base_workers_by_task") or {}).items():
        note_tier(f"work_{task}", v)

    index, drops_inv, ranch_inv, tags_inv = {}, {}, {}, {}
    for c in combat:
        name = c["name"]
        base = pals.get(name, {"number": None, "elements": c["elements"], "work": {}})
        eff = (c.get("partner_skill") or {}).get("effect") or ""
        ps_name = (c.get("partner_skill") or {}).get("name") or ""

        # ранч-продукция из текста partner skill
        raw_prod = re.findall(
            r"(?:drops?|lays?|digs? up|makes?|produc\w+)\s+(?:an?\s+)?([^.]+?)\s*(?:from its back\s*)?when assigned to(?: the| a)? Ranch",
            eff, re.I)
        produce = []
        for chunk in raw_prod:
            for p in re.split(r"\s+or\s+", chunk):
                p = p.strip().rstrip(".")
                p = {"Iceorgan": "Ice Organ"}.get(p, p)  # опечатка paldb
                produce.append(p)

        tags = [tag for tag, pat in PARTNER_TAGS.items() if re.search(pat, eff, re.I)]

        # структурированные базовые баффы (действуют на всю базу, "Does not stack")
        base_support = {}
        m = re.search(r"increases the ([A-Za-z ]+?) Work Suitability Level for all other Base Pals by \+(\d+)", eff)
        if m:
            base_support = {"type": "suitability", "task": m.group(1).strip(), "bonus": int(m.group(2))}
        elif re.search(r"egg production speed", eff, re.I):
            base_support = {"type": "egg_speed", "effect": "egg production speed +20~50% at Breeding Farm"}
        elif re.search(r"incubate eggs", eff, re.I):
            base_support = {"type": "incubation", "effect": "egg incubation time -20~40%"}
        elif re.search(r"SAN value of allies at the base decreases", eff, re.I):
            base_support = {"type": "sanity_save", "effect": "base SAN drain -10~15%"}
        elif re.search(r"reduces Hunger depletion rate of Base Pals", eff, re.I):
            base_support = {"type": "hunger_save", "effect": "base hunger drain reduced"}
        elif re.search(r"growth rate of the crops", eff, re.I):
            base_support = {"type": "crop_growth", "effect": "crop growth rate +50~70%"}
        elif re.search(r"increasing their harvest", eff, re.I):
            base_support = {"type": "crop_yield", "effect": "harvest +18~35%"}
        elif re.search(r"Jelliette and Jellroy are in your base", eff):
            base_support = {"type": "pair_watering", "effect": "watering speed +50~120% when Jelliette & Jellroy are both at base"}
        elif re.search(r"boosts Anubis's work speed", eff):
            base_support = {"type": "pair_anubis", "effect": "Anubis work speed +20~40%; self +30~60% at workbenches"}
        elif re.search(r"working at a Weapon Workbench", eff):
            base_support = {"type": "station_efficiency", "effect": "+200~400% at weapon workbenches"}
        elif re.search(r"patrols the skies and bombards intruders", eff):
            base_support = {"type": "base_defense", "effect": "patrols base airspace vs raids (1 per base)"}

        # партийные бонусы на сбор яиц (важно для бридинг-цикла)
        if re.search(r"becoming an Alpha Pal Egg", eff):
            tags.append("egg_alpha_chance")
        if re.search(r"chance of receiving one extra", eff) and "Egg" in eff:
            tags.append("egg_extra_pickup")

        l = loc.get(name, {})
        entry = {
            "number": base["number"], "elements": base["elements"], "work": base["work"],
            "rarity": c.get("rarity"), "hp": c.get("hp"),
            "atk": max(c.get("melee_attack") or 0, c.get("shot_attack") or 0),
            "def": c.get("defense"),
            "mount": c.get("mount_type"), "sprint": (c.get("movement") or {}).get("sprint"),
            "partner_skill": ps_name, "partner_effect": eff,
            "partner_tags": tags, "ranch_produce": produce, "base_support": base_support or None,
            "drops": c.get("notable_drops") or [],
            "combi_rank": br["combi_ranks"].get(name),
            "tier_hits": tier_hits.get(name, []),
            "regions": l.get("regions") or [],
            "alpha": l.get("alpha_locations") or [],
            "eggs": l.get("egg_types") or [],
            "get_via": l.get("other_sources") or [],
        }
        index[name] = entry
        for d in entry["drops"]:
            drops_inv.setdefault(d, []).append(name)
        for p in produce:
            ranch_inv.setdefault(p, []).append(name)
        for t in tags:
            tags_inv.setdefault(t, []).append(name)
        if base_support:
            key = base_support["type"] + (f":{base_support['task']}" if base_support.get("task") else "")
            tags_inv.setdefault("base_support:" + key, []).append(name)

    # ранч-продюсеры сортируем по уровню Farming
    for item, names in ranch_inv.items():
        names.sort(key=lambda n: -(index[n]["work"].get("Farming") or 0))
    work_inv = {}
    for w in WORK_COLS:
        ranked = sorted(((n, e["work"][w]) for n, e in index.items() if e["work"].get(w)),
                        key=lambda x: -x[1])
        work_inv[w] = [[n, lv] for n, lv in ranked]

    out = {
        "generated_from": "palworld_pals.csv, pals_combat.json, pal_locations.json, breeding.json, tier_lists.json",
        "pals": index,
        "inverted": {"drops": drops_inv, "ranch_produce": ranch_inv,
                     "work": work_inv, "partner_tags": tags_inv},
    }
    (DATA / "index.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"index.json: {len(index)} pals; ranch items: {len(ranch_inv)}; "
          f"drop items: {len(drops_inv)}; partner tags: { {k: len(v) for k, v in tags_inv.items()} }")
    print("ranch produce map:", {k: v[:3] for k, v in sorted(ranch_inv.items())})


if __name__ == "__main__":
    main()
