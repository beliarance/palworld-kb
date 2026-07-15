#!/usr/bin/env python3
"""Валидация файлов в /data/: JSON корректен, схемы на месте, имена палов согласованы.

Запуск: python3 scripts/validate_data.py
Выход 0 = всё ок; непустой список WARN допустим (например, пока не собраны breeding/tier данные).
"""

import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
errors, warnings = [], []


def load(name, required=True):
    path = DATA / name
    if not path.exists():
        (errors if required else warnings).append(f"{name}: missing")
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{name}: invalid JSON — {e}")
        return None


# --- canonical names from CSV
csv_path = DATA / "palworld_pals.csv"
if not csv_path.exists():
    sys.exit("FATAL: data/palworld_pals.csv missing")
with open(csv_path) as f:
    rows = list(csv.DictReader(f))
names = {r["Name"] for r in rows}
if len(rows) != 299:
    warnings.append(f"palworld_pals.csv: {len(rows)} rows (expected 299)")

# --- pals_combat.json
combat = load("pals_combat.json")
if combat:
    combat_names = {c["name"] for c in combat}
    for missing in sorted(names - combat_names):
        errors.append(f"pals_combat.json: no entry for CSV pal '{missing}'")
    for extra in sorted(combat_names - names):
        warnings.append(f"pals_combat.json: '{extra}' not in CSV")
    for c in combat:
        for field in ("hp", "melee_attack", "shot_attack", "defense"):
            if not isinstance(c.get(field), (int, float)):
                warnings.append(f"pals_combat.json: {c['name']}.{field} is {c.get(field)!r}")

# --- type_chart.json
tc = load("type_chart.json")
if tc:
    els = set(tc["elements"])
    if len(els) != 9:
        errors.append(f"type_chart.json: {len(els)} elements (expected 9)")
    for el, node in tc["chart"].items():
        for ref in node["strong_vs"] + node["weak_to"]:
            if ref not in els:
                errors.append(f"type_chart.json: {el} references unknown element '{ref}'")
    # symmetry: if A strong_vs B, then B weak_to A
    for el, node in tc["chart"].items():
        for target in node["strong_vs"]:
            if el not in tc["chart"][target]["weak_to"]:
                errors.append(f"type_chart.json: {el} strong_vs {target}, but {target} not weak_to {el}")

# --- bosses.json
bosses = load("bosses.json")
if bosses and tc:
    for b in bosses["tower_bosses"] + bosses["raid_bosses"]:
        for el in b["elements"] + b["counter_elements"]:
            if el not in tc["elements"]:
                errors.append(f"bosses.json: {b['pal']} has unknown element '{el}'")

# --- breeding.json (may not be collected yet)
br = load("breeding.json", required=False)
if br:
    unknown = sorted(set(br["combi_ranks"]) - names)
    if unknown:
        warnings.append(f"breeding.json: {len(unknown)} rank names not in CSV: {unknown[:10]}")
    covered = len(set(br["combi_ranks"]) & names)
    if covered < len(names):
        warnings.append(f"breeding.json: combi ranks cover {covered}/{len(names)} pals")
    for c in br["special_combos"]:
        for k in ("parent_a", "parent_b", "child"):
            if c[k] not in names:
                warnings.append(f"breeding.json: special combo name '{c[k]}' not in CSV")

# --- tier_lists.json (may not be collected yet)
tiers = load("tier_lists.json", required=False)
if tiers:
    def check_list(key, entries):
        for e in entries:
            if e["name"] not in names:
                warnings.append(f"tier_lists.json: {key} entry '{e['name']}' not in CSV")
    for key, val in tiers.items():
        if isinstance(val, list) and val and isinstance(val[0], dict) and "name" in val[0]:
            check_list(key, val)
    for task, entries in (tiers.get("best_base_workers_by_task") or {}).items():
        check_list(f"workers/{task}", entries)

# --- items.json (may not be collected yet)
items = load("items.json", required=False)
if items:
    item_names = {i["name"] for i in items["items"]}
    if len(item_names) != len(items["items"]):
        warnings.append("items.json: duplicate item names present")
    unresolved = set()
    for i in items["items"]:
        r = i.get("recipe")
        if r:
            if not r.get("station"):
                warnings.append(f"items.json: {i['name']} recipe has no station")
            for m, q in (r.get("materials") or {}).items():
                if not isinstance(q, (int, float)) or q <= 0:
                    errors.append(f"items.json: {i['name']} material {m} qty {q!r}")
                if m not in item_names:
                    unresolved.add(m)
    if unresolved:
        warnings.append(f"items.json: {len(unresolved)} recipe components have no own item entry: {sorted(unresolved)[:10]}")

# --- expeditions.json (may not be collected yet)
exp = load("expeditions.json", required=False)
if exp:
    for m in exp.get("missions", []):
        if not m.get("name"):
            errors.append("expeditions.json: mission without name")

# --- active_skills.json (may not be collected yet)
ELEMENTS = set(tc["elements"]) if tc else set()
sk = load("active_skills.json", required=False)
if sk:
    skill_names = {s["name"] for s in sk["skills"]}
    for s in sk["skills"]:
        if ELEMENTS and s.get("element") not in ELEMENTS:
            errors.append(f"active_skills.json: {s['name']} has unknown element '{s.get('element')}'")
        for pal in s.get("exclusive_to") or []:
            if pal not in names:
                warnings.append(f"active_skills.json: exclusive_to '{pal}' not in CSV")
    for pal, learned in (sk.get("learnsets") or {}).items():
        if pal not in names:
            warnings.append(f"active_skills.json: learnset pal '{pal}' not in CSV")
        for e in learned:
            if e["skill"] not in skill_names:
                warnings.append(f"active_skills.json: {pal} learns unknown skill '{e['skill']}'")
    covered = len(set(sk.get("learnsets") or {}) & names)
    if covered < len(names):
        warnings.append(f"active_skills.json: learnsets cover {covered}/{len(names)} pals")

# --- passives.json (may not be collected yet)
pv = load("passives.json", required=False)
if pv:
    for p in pv["passives"]:
        if not p.get("effects"):
            warnings.append(f"passives.json: {p['name']} has no effects text")

# --- pal_locations.json (may not be collected yet)
pl = load("pal_locations.json", required=False)
if pl:
    unknown = sorted(set(pl["pals"]) - names)
    if unknown:
        warnings.append(f"pal_locations.json: {len(unknown)} keys not in CSV: {unknown[:10]}")
    covered = len(set(pl["pals"]) & names)
    if covered < len(names):
        warnings.append(f"pal_locations.json: covers {covered}/{len(names)} pals")

# --- resource_nodes.json (may not be collected yet)
rn = load("resource_nodes.json", required=False)
if rn:
    for r in rn["resources"]:
        if not r.get("best_locations") and not r.get("other_sources"):
            warnings.append(f"resource_nodes.json: {r['name']} has no locations or sources")

# --- base_building.json (may not be collected yet)
bb = load("base_building.json", required=False)
if bb:
    for s in bb.get("structures", []):
        if not s.get("name"):
            errors.append("base_building.json: structure without name")
            continue
        if s.get("tech_level") is not None and not isinstance(s["tech_level"], int):
            errors.append(f"base_building.json: {s['name']} tech_level {s['tech_level']!r}")
        for m, q in (s.get("materials") or {}).items():
            if not isinstance(q, int) or q <= 0:
                errors.append(f"base_building.json: {s['name']} material {m} qty {q!r}")
        if not s.get("materials"):
            warnings.append(f"base_building.json: {s['name']} has no materials")
    for f in bb.get("foods", []):
        if f.get("nutrition") is not None and not isinstance(f["nutrition"], int):
            errors.append(f"base_building.json: food {f.get('name')} nutrition {f['nutrition']!r}")
    pf = bb.get("pal_food_amount", {})
    unknown = sorted(set(pf) - names)
    if unknown:
        errors.append(f"base_building.json: {len(unknown)} pal_food_amount keys not in CSV: {unknown[:10]}")
    covered = len(set(pf) & names)
    if covered < len(names):
        warnings.append(f"base_building.json: pal_food_amount covers {covered}/{len(names)} pals")
    for pal, v in pf.items():
        if v is not None and (not isinstance(v, int) or not 1 <= v <= 10):
            errors.append(f"base_building.json: pal_food_amount[{pal}] = {v!r} (expect 1-10)")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\n{len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
