#!/usr/bin/env python3
"""Palworld 1.0 knowledge-base query tool.

Читает данные из /data/ и отвечает на игровые вопросы:

  python scripts/query.py pal <name>              — профиль пала (статы, работы, маунт, дропы)
  python scripts/query.py workers <task>          — лучшие рабочие для работы (kindling, mining, ...)
  python scripts/query.py mounts <ground|flying|swim>  — лучшие маунты по скорости
  python scripts/query.py fighters [--element E]  — лучшие бойцы по статам
  python scripts/query.py counter <element>       — чем бить эту стихию (+ топ палов-контрпиков)
  python scripts/query.py boss <name>             — каунтер под конкретного босса/башню
  python scripts/query.py breed <A> <B>           — кто родится от пары
  python scripts/query.py breed-to <X> [--with A] — как получить пала X бридингом
  python scripts/query.py team <task>             — команда из 5 палов (fishing, combat, mining, lumbering, production, ranch)
  python scripts/query.py tiers <category>        — тир-лист из tier_lists.json
"""

import argparse
import csv
import json
import re
import sys
from collections import deque
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

WORK_TASKS = {
    "kindling": "Kindling", "watering": "Watering", "planting": "Planting",
    "electricity": "Generating_Electricity", "generating_electricity": "Generating_Electricity",
    "handiwork": "Handiwork", "gathering": "Gathering", "lumbering": "Lumbering",
    "mining": "Mining", "medicine": "Medicine", "cooling": "Cooling",
    "transporting": "Transporting", "transport": "Transporting", "farming": "Farming",
}


# ---------------------------------------------------------------- loading

def _load_json(name):
    path = DATA_DIR / name
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_db():
    """Merge CSV work data and combat JSON into one dict keyed by pal name."""
    db = {}
    with open(DATA_DIR / "palworld_pals.csv") as f:
        for row in csv.DictReader(f):
            work = {}
            for task, col in WORK_TASKS.items():
                if col in row and row[col]:
                    work[col] = int(row[col])
            db[row["Name"]] = {
                "name": row["Name"],
                "number": row["Number"],
                "elements": [e for e in (row["Element_1"], row["Element_2"]) if e],
                "work": work,
                "paldb_url": row["PaldbURL"],
            }
    combat = _load_json("pals_combat.json") or []
    for c in combat:
        entry = db.setdefault(c["name"], {"name": c["name"], "work": {}, "elements": c.get("elements", [])})
        entry.update({
            "rarity": c.get("rarity"), "hp": c.get("hp"),
            "melee_attack": c.get("melee_attack"), "shot_attack": c.get("shot_attack"),
            "defense": c.get("defense"), "ride": c.get("ride"),
            "mount_type": c.get("mount_type"), "movement": c.get("movement") or {},
            "size": c.get("size"),
            "partner_skill": c.get("partner_skill") or {},
            "notable_drops": c.get("notable_drops") or [],
            "role_tags": c.get("role_tags") or [],
        })
    return db


def find_pal(db, name):
    """Case-insensitive lookup with prefix fallback."""
    for k in db:
        if k.lower() == name.lower():
            return db[k]
    matches = [k for k in db if k.lower().startswith(name.lower())]
    if len(matches) == 1:
        return db[matches[0]]
    if matches:
        sys.exit(f"Ambiguous name '{name}': {', '.join(sorted(matches))}")
    sys.exit(f"Pal '{name}' not found.")


def attack(p):
    return max(p.get("melee_attack") or 0, p.get("shot_attack") or 0)


def label(p):
    """Имя пала с палдекс-номером: 'Anubis (#139)'."""
    return f"{p['name']} (#{p['number']})" if p.get("number") else p["name"]


def label_name(db, name):
    return label(db[name]) if name in db else name


# ---------------------------------------------------------------- commands

def cmd_pal(db, args):
    p = find_pal(db, args.name)
    print(f"#{p.get('number', '?')} {p['name']}  [{'/'.join(p['elements'])}]  rarity: {p.get('rarity', '?')}")
    print(f"  HP {p.get('hp')}  ATK {p.get('melee_attack')}/{p.get('shot_attack')} (melee/shot)  DEF {p.get('defense')}")
    if p.get("work"):
        print("  Work: " + ", ".join(f"{k} {v}" for k, v in sorted(p["work"].items(), key=lambda x: -x[1])))
    if p.get("ride"):
        mv = p.get("movement") or {}
        print(f"  Mount: {p.get('mount_type')}  (run {mv.get('run')}, sprint {mv.get('sprint')})")
    ps = p.get("partner_skill") or {}
    if ps.get("name"):
        print(f"  Partner skill: {ps['name']} — {ps.get('effect', '')}")
    if p.get("notable_drops"):
        print("  Drops: " + ", ".join(p["notable_drops"]))
    if p.get("role_tags"):
        print("  Roles: " + ", ".join(p["role_tags"]))


def rank_workers(db, task, element=None):
    col = WORK_TASKS.get(task.lower())
    if not col:
        sys.exit(f"Unknown task '{task}'. Tasks: {', '.join(sorted(set(WORK_TASKS)))}")
    pals = [p for p in db.values() if p["work"].get(col)]
    if element:
        pals = [p for p in pals if element.capitalize() in p["elements"]]
    # sort: work level desc, then total work versatility, then HP (survivability at base)
    pals.sort(key=lambda p: (-p["work"][col], -sum(p["work"].values()), -(p.get("hp") or 0)))
    return col, pals


def cmd_workers(db, args):
    # можно несколько задач через запятую → условие И (пал должен уметь ВСЕ)
    tasks = [t.strip() for t in args.task.split(",") if t.strip()]
    cols = []
    for t in tasks:
        c = WORK_TASKS.get(t.lower())
        if not c:
            sys.exit(f"Unknown task '{t}'. Tasks: {', '.join(sorted(set(WORK_TASKS)))}")
        cols.append(c)
    pals = [p for p in db.values() if all(p["work"].get(c) for c in cols)]
    if args.element:
        pals = [p for p in pals if args.element.capitalize() in p["elements"]]

    def run(p):
        return (p.get("movement") or {}).get("run") or 0

    def walk(p):
        return (p.get("movement") or {}).get("walk") or 0
    if args.speed:  # уровень качается книгами → для транспорта важнее скорость бега
        pals.sort(key=lambda p: (-run(p), -sum(p["work"][c] for c in cols)))
    else:
        pals.sort(key=lambda p: (-sum(p["work"][c] for c in cols), -run(p)))
    join = " И ".join(cols)
    print(f"Лучшие для: {join}" + (" (условие И)" if len(cols) > 1 else "")
          + f" — {len(pals)} палов. Уровень качается книгами/4★ → для транспорта смотри «бег» (скорость бег/ход):")
    for p in pals[: args.top]:
        lv = " ".join(f"{c}{p['work'][c]}" for c in cols)
        others = ", ".join(f"{k} {v}" for k, v in sorted(p["work"].items(), key=lambda x: -x[1]) if k not in cols)
        spd = f"{run(p) or '—'}/{walk(p) or '—'}"
        print(f"  [{lv}] {label(p):<26} разм={p.get('size') or '?':<2} бег/ход={spd:<9} [{'/'.join(p['elements'])}]"
              + (f"  ещё: {others}" if others else ""))


def cmd_mounts(db, args):
    kind = args.kind.lower()
    pals = [p for p in db.values() if p.get("ride") and p.get("mount_type") == kind]
    pals.sort(key=lambda p: -((p.get("movement") or {}).get("sprint") or (p.get("movement") or {}).get("run") or 0))
    print(f"Best {kind} mounts (by sprint speed):")
    for p in pals[: args.top]:
        mv = p.get("movement") or {}
        print(f"  sprint {mv.get('sprint', '?'):>5}  {label(p):<28} [{'/'.join(p['elements'])}]  ATK {attack(p)}")


def cmd_fighters(db, args):
    pals = list(db.values())
    if args.element:
        pals = [p for p in pals if args.element.capitalize() in p["elements"]]
    pals = [p for p in pals if p.get("hp")]
    # combat score: attack weighted, plus bulk
    pals.sort(key=lambda p: -(attack(p) * 2 + (p.get("hp") or 0) + (p.get("defense") or 0)))
    print("Best fighters (score = 2*ATK + HP + DEF):")
    for p in pals[: args.top]:
        ps = (p.get("partner_skill") or {}).get("name", "")
        print(f"  ATK {attack(p):>3} HP {p['hp']:>3} DEF {p['defense']:>3}  {label(p):<28} [{'/'.join(p['elements'])}]  {ps}")


def counters_for(chart, element):
    """Elements that deal bonus damage TO `element`."""
    el = element.capitalize()
    if el not in chart:
        sys.exit(f"Unknown element '{element}'. Elements: {', '.join(chart)}")
    return chart[el]["weak_to"]


def cmd_counter(db, args):
    tc = _load_json("type_chart.json")
    if not tc:
        sys.exit("data/type_chart.json missing.")
    chart = tc["chart"]
    el = args.element.capitalize()
    strong = counters_for(chart, el)
    print(f"{el} takes bonus damage from: {', '.join(strong) or 'nothing (typeless-like)'}")
    print(f"{el} deals bonus damage to: {', '.join(chart[el]['strong_vs']) or 'nothing'}")
    for s in strong:
        pals = [p for p in db.values() if s in p["elements"] and p.get("hp")]
        pals.sort(key=lambda p: -attack(p))
        names = ", ".join(f"{label(p)} (ATK {attack(p)})" for p in pals[:5])
        print(f"  Top {s} attackers: {names}")


def cmd_boss(db, args):
    bosses = _load_json("bosses.json")
    if not bosses:
        sys.exit("data/bosses.json missing.")
    q = args.name.lower()
    all_bosses = bosses["tower_bosses"] + bosses["raid_bosses"] + bosses.get("world_bosses", [])
    hits = [b for b in all_bosses if q in b.get("pal", "").lower() or q in b.get("leader", "").lower()]
    if not hits:
        sys.exit(f"Boss '{args.name}' not found. Known: " + ", ".join(b["pal"] for b in all_bosses))
    for b in hits:
        title = f"{b.get('leader', '')} & {b['pal']}".strip(" &")
        prelim = "  (PRELIMINARY 1.0)" if b.get("preliminary") else ""
        print(f"{title} — {b.get('faction', b.get('notes', ''))}{prelim}")
        if b.get("boss_pal_level"):
            print(f"  Level: {b['boss_pal_level']} (recommended player level {b['recommended_player_level']})")
        print(f"  Elements: {'/'.join(b['elements']) or 'typeless'}   Counter with: {', '.join(b['counter_elements']) or 'no elemental counter'}")
        if b.get("tactics"):
            print(f"  Tactics: {b['tactics']}")
        for el in b["counter_elements"]:
            pals = sorted((p for p in db.values() if el in p["elements"] and p.get("hp")), key=lambda p: -attack(p))
            print(f"  Top {el} picks: " + ", ".join(label(p) for p in pals[:5]))


# ---------------------------------------------------------------- breeding

def load_breeding():
    br = _load_json("breeding.json")
    if not br:
        sys.exit("data/breeding.json missing (breeding data not collected yet).")
    return br


def breed_child(br, a, b):
    """Deterministic breeding result for parents a, b (canonical names)."""
    if a == b:
        return a, "same-species pair always yields the same species"
    for combo in br["special_combos"]:
        pair = {combo["parent_a"], combo["parent_b"]}
        if pair == {a, b}:
            return combo["child"], "special combination (overrides rank formula)"
    ranks = br["combi_ranks"]
    if a not in ranks or b not in ranks:
        missing = [x for x in (a, b) if x not in ranks]
        return None, f"no combi rank data for: {', '.join(missing)}"
    target = (ranks[a] + ranks[b] + 1) // 2
    special_children = {c["child"] for c in br["special_combos"]}
    # pals that only come from special combos can't appear as rank-formula results
    candidates = {n: r for n, r in ranks.items() if n not in special_children}
    # тай-брейк 1.0: при равном расстоянии побеждает БÓЛЬШИЙ CombiRank (-rank)
    child = min(candidates, key=lambda n: (abs(candidates[n] - target), -candidates[n]))
    return child, f"rank formula: floor(({ranks[a]}+{ranks[b]}+1)/2)={target}, closest rank {candidates[child]}"


def cmd_breed(db, args):
    br = load_breeding()
    a, b = find_pal(db, args.parent_a)["name"], find_pal(db, args.parent_b)["name"]
    child, why = breed_child(br, a, b)
    if child is None:
        print(f"{label_name(db, a)} + {label_name(db, b)} = ?  ({why})")
    else:
        print(f"{label_name(db, a)} + {label_name(db, b)} = {label_name(db, child)}\n  ({why})")


def cmd_breed_to(db, args):
    br = load_breeding()
    target = find_pal(db, args.target)["name"]
    print(f"How to breed {label_name(db, target)}:")
    combos = [c for c in br["special_combos"]
              if c["child"] == target and c["parent_a"] != c["parent_b"]]
    if combos:
        print("  Special combos (exact pairs required):")
        for c in combos:
            print(f"    {label_name(db, c['parent_a'])} + {label_name(db, c['parent_b'])}")
    print(f"  Same-species: {target} + {target} (always works if you have a pair)")
    if target in {c["child"] for c in br["special_combos"]} and not args.with_pal:
        print("  Note: special-combo pals cannot be produced by the rank formula.")
        return
    ranks = br["combi_ranks"]
    if target not in ranks:
        print("  (no combi rank data for this pal — rank-based pairs unknown)")
        return
    pairs = []
    parents = [args.with_pal] if args.with_pal else sorted(ranks)
    for a in parents:
        a = find_pal(db, a)["name"] if args.with_pal else a
        for b in sorted(ranks):
            if a > b and not args.with_pal:
                continue  # avoid duplicate unordered pairs in full scan
            child, _ = breed_child(br, a, b)
            if child == target and a != target and b != target:
                pairs.append((a, b))
    if pairs:
        shown = pairs[: args.top]
        label = f"with {args.with_pal}" if args.with_pal else "sample"
        print(f"  Rank-formula pairs ({label}, {len(pairs)} found, showing {len(shown)}):")
        for a, b in shown:
            print(f"    {label_name(db, a)} + {label_name(db, b)}")
    elif not combos:
        print("  No rank-formula pairs found (pal may be catch-only or data incomplete).")


def breed_chain(br, start, target):
    """Кратчайшая цепочка бридинга start → target (BFS по видам).
    Для переноса дроп-онли трейта: держишь трейт-носителя одним родителем на каждом шаге."""
    if start == target:
        return []
    ranks = br["combi_ranks"]
    if start not in ranks:
        return None
    special_children = {c["child"] for c in br["special_combos"]}
    special_pair = {}
    for c in br["special_combos"]:
        special_pair[(c["parent_a"], c["parent_b"])] = c["child"]
        special_pair[(c["parent_b"], c["parent_a"])] = c["child"]
    candidates = sorted(((n, r) for n, r in ranks.items() if n not in special_children), key=lambda x: x[1])
    nr_cache = {}

    def nearest(t):
        if t not in nr_cache:
            # тай-брейк 1.0: больший CombiRank выигрывает (-c[1])
            nr_cache[t] = min(candidates, key=lambda c: (abs(c[1] - t), -c[1]))[0]
        return nr_cache[t]

    def child_of(a, b):
        if a == b:
            return a
        if (a, b) in special_pair:
            return special_pair[(a, b)]
        if a not in ranks or b not in ranks:
            return None
        return nearest((ranks[a] + ranks[b] + 1) // 2)

    partners = list(ranks.keys())
    prev, via, q = {start: None}, {}, deque([start])
    while q:
        cur = q.popleft()
        for b in partners:
            if b == cur:
                continue
            ch = child_of(cur, b)
            if not ch or ch in prev:
                continue
            prev[ch], via[ch] = cur, b
            if ch == target:
                steps, c = [], target
                while prev[c]:
                    steps.append((prev[c], via[c], c))
                    c = prev[c]
                return list(reversed(steps))
            q.append(ch)
    return None


def cmd_breed_chain(db, args):
    br = load_breeding()
    start = find_pal(db, args.start)["name"]
    target = find_pal(db, args.target)["name"]
    if start == target:
        print(f"{label_name(db, start)} — уже нужный вид; разводи парой {start} + {start}, оставляя потомка с трейтом.")
        return
    chain = breed_chain(br, start, target)
    if chain is None:
        sys.exit(f"Цепочку {start} → {target} ранговой формулой не построить "
                 f"(цель может быть особым видом только из спец-комбо).")
    print(f"Цепочка {label_name(db, start)} → {label_name(db, target)} ({len(chain)} шаг.):")
    for i, (frm, partner, child) in enumerate(chain, 1):
        print(f"  {i}. {label_name(db, frm)} + {label_name(db, partner)} → {label_name(db, child)}")
    print("  💡 На каждом шаге один родитель — носитель трейта (старт или его потомок с трейтом), "
          "второй — партнёр для смены вида; потомок берёт до 3 пассивок из пула обоих — оставляй "
          "яйцо с нужным трейтом. Так дроп-онли/эксклюзивный трейт попадает на вид, который сам его не даёт.")


# ---------------------------------------------------------------- items

def load_items():
    data = _load_json("items.json")
    if not data:
        sys.exit("data/items.json missing (items data not collected yet).")
    return data


def find_item(items, name):
    by_name = {i["name"].lower(): i for i in items}
    if name.lower() in by_name:
        return by_name[name.lower()]
    matches = [i for i in items if name.lower() in i["name"].lower()]
    if len(matches) == 1:
        return matches[0]
    if matches:
        sys.exit(f"Ambiguous item '{name}': {', '.join(sorted(i['name'] for i in matches))}")
    sys.exit(f"Item '{name}' not found.")


def pals_dropping(db, item_name):
    return sorted(
        (p for p in db.values() if any(item_name.lower() == d.lower() for d in p.get("notable_drops", []))),
        key=lambda p: p["name"])


def cmd_item(db, args):
    data = load_items()
    it = find_item(data["items"], args.name)
    print(f"{it['name']}  [{it.get('category', '?')}]" + (f"  tech lvl {it['tech_level']}" if it.get("tech_level") else ""))
    r = it.get("recipe")
    if r:
        mats = ", ".join(f"{m} x{q}" for m, q in r["materials"].items())
        station = r.get("station") or "(station not listed — see note)"
        print(f"  Craft at: {station}  <-  {mats}")
    else:
        print("  Not craftable (or recipe unknown).")
    for src in it.get("obtained_from") or []:
        print(f"  Source: {src}")
    droppers = pals_dropping(db, it["name"])
    if droppers:
        print("  Dropped by pals: " + ", ".join(label(p) for p in droppers[:15]))
    if it.get("notes"):
        print(f"  Note: {it['notes']}")


def cmd_craft(db, args):
    """Recursive raw-material breakdown for a craftable item."""
    data = load_items()
    by_name = {i["name"]: i for i in data["items"]}
    target = find_item(data["items"], args.name)
    if not target.get("recipe"):
        sys.exit(f"{target['name']} has no known recipe.")
    raw, steps = {}, []

    def expand(name, qty, depth):
        it = by_name.get(name)
        r = it.get("recipe") if it else None
        if r and depth < 6 and not args.flat:
            steps.append((depth, name, qty, r.get("station") or "?"))
            for m, q in r["materials"].items():
                expand(m, q * qty, depth + 1)
        else:
            raw[name] = raw.get(name, 0) + qty

    r = target["recipe"]
    steps.append((0, target["name"], args.qty, r.get("station") or "?"))
    for m, q in r["materials"].items():
        expand(m, q * args.qty, 1)
    print(f"Craft {target['name']} x{args.qty}:")
    for depth, name, qty, station in steps:
        print("  " * (depth + 1) + f"{name} x{qty}  @ {station}")
    print("Raw materials total:")
    for m, q in sorted(raw.items()):
        srcs = (by_name.get(m) or {}).get("obtained_from") or []
        hint = f"  ({srcs[0]})" if srcs else ""
        print(f"  {m} x{q}{hint}")


def cmd_drops(db, args):
    droppers = pals_dropping(db, args.item)
    matches = sorted({d for p in db.values() for d in p.get("notable_drops", []) if args.item.lower() in d.lower()})
    if not droppers and matches:
        sys.exit(f"No exact match for '{args.item}'. Did you mean: {', '.join(matches[:10])}")
    if not droppers:
        sys.exit(f"No pal drops '{args.item}' (check data/items.json for other sources).")
    print(f"Pals dropping {args.item}:")
    for p in droppers:
        print(f"  {label(p):<28} [{'/'.join(p['elements'])}]  HP {p.get('hp')}  ATK {attack(p)}")


# ---------------------------------------------------------------- skills / passives / locations / resources

def cmd_skills(db, args):
    data = _load_json("active_skills.json")
    if not data:
        sys.exit("data/active_skills.json missing (not collected yet).")
    p = find_pal(db, args.name)
    learnset = (data.get("learnsets") or {}).get(p["name"])
    by_name = {s["name"]: s for s in data["skills"]}
    if learnset:
        print(f"{label(p)} learnset:")
        for entry in sorted(learnset, key=lambda e: e["level"]):
            s = by_name.get(entry["skill"], {})
            pw = f" pow {s['power']}" if s.get("power") else ""
            cd = f" cd {s['cooldown_seconds']}s" if s.get("cooldown_seconds") else ""
            print(f"  lv {entry['level']:>2}  {entry['skill']:<24} [{s.get('element', '?')}]{pw}{cd}")
    else:
        print(f"No learnset data for {p['name']} (see gaps in active_skills.json).")
    excl = [s for s in data["skills"] if p["name"] in (s.get("exclusive_to") or [])]
    for s in excl:
        print(f"  Exclusive: {s['name']} [{s.get('element')}] pow {s.get('power')} — {s.get('description', '')}")


def cmd_skill(db, args):
    data = _load_json("active_skills.json")
    if not data:
        sys.exit("data/active_skills.json missing (not collected yet).")
    matches = [s for s in data["skills"] if args.name.lower() in s["name"].lower()]
    if not matches:
        sys.exit(f"Skill '{args.name}' not found.")
    for s in matches[:5]:
        pw = f"  power {s.get('power')}" if s.get("power") is not None else ""
        cd = f"  cooldown {s.get('cooldown_seconds')}s" if s.get("cooldown_seconds") is not None else ""
        print(f"{s['name']}  [{s.get('element')}]{pw}{cd}  range: {s.get('range', '?')}")
        if s.get("description"):
            print(f"  {s['description']}")
        if s.get("exclusive_to"):
            print(f"  Exclusive to: {', '.join(s['exclusive_to'])}")
        if s.get("skill_fruit_exists"):
            print("  Skill Fruit exists — can be taught to any pal.")


def cmd_passive(db, args):
    data = _load_json("passives.json")
    if not data:
        sys.exit("data/passives.json missing (not collected yet).")
    q = args.name.lower()
    matches = [p for p in data["passives"] if q in p["name"].lower()]
    if not matches:
        sys.exit(f"Passive '{args.name}' not found.")
    for p in matches[:10]:
        tier = f"  tier {p['tier']}" if p.get("tier") is not None else ""
        print(f"{p['name']}  [{p.get('category')}]{tier} — {p.get('effects')}")
        if p.get("exclusive_source"):
            print(f"  Source: {', '.join(p['exclusive_source'])}")


def region_coords():
    data = _load_json("regions.json") or {}
    return data.get("regions") or {}


def with_coords(region, coords_map):
    import re as _re
    base = _re.sub(r"\s*\[Lv\.[^\]]*\]$", "", region).strip()
    c = coords_map.get(region) or coords_map.get(base)
    return f"{region} ({c[0]}, {c[1]})" if c else region


def cmd_where(db, args):
    data = _load_json("pal_locations.json")
    if not data:
        sys.exit("data/pal_locations.json missing (not collected yet).")
    p = find_pal(db, args.name)
    loc = data["pals"].get(p["name"])
    if not loc:
        sys.exit(f"No location data for {p['name']}.")
    rc = region_coords()
    print(f"Where to get {label(p)}:")
    if loc.get("regions"):
        dn = f" ({loc['day_night']})" if loc.get("day_night") and loc["day_night"] != "both" else ""
        print(f"  Wild spawns{dn}: " + "; ".join(with_coords(r, rc) for r in loc["regions"]))
    for a in loc.get("alpha_locations") or []:
        print(f"  Alpha boss: {a}")
    if loc.get("egg_types"):
        print("  Hatches from: " + ", ".join(loc["egg_types"]))
    for o in loc.get("other_sources") or []:
        print(f"  Also: {o}")
    if loc.get("notes"):
        print(f"  Note: {loc['notes']}")


def cmd_resource(db, args):
    data = _load_json("resource_nodes.json")
    if not data:
        sys.exit("data/resource_nodes.json missing (not collected yet).")
    q = args.name.lower()
    matches = [r for r in data["resources"] if q in r["name"].lower()]
    if not matches:
        sys.exit(f"Resource '{args.name}' not found. Known: " + ", ".join(r["name"] for r in data["resources"]))
    for r in matches[:3]:
        print(f"{r['name']}:")
        for loc in r.get("best_locations") or []:
            coords = f" {loc['coordinates']}" if loc.get("coordinates") else ""
            nodes = f", ~{loc['node_count']} nodes" if loc.get("node_count") else ""
            note = f" — {loc['notes']}" if loc.get("notes") else ""
            print(f"  {loc['area']}{coords}{nodes}{note}")
        if r.get("base_recommendation"):
            print(f"  Base tip: {r['base_recommendation']}")
        for o in r.get("other_sources") or []:
            print(f"  Also from: {o}")


# ---------------------------------------------------------------- produce (через index.json)

def cmd_produce(db, args):
    """Как добывать предмет в объёме: ранч, дропы, крафт, плантации."""
    idx = _load_json("index.json")
    if not idx:
        sys.exit("data/index.json missing — собери: python3 scripts/build_index.py")
    q = args.item.lower()
    inv = idx["inverted"]
    ranch = {k: v for k, v in inv["ranch_produce"].items() if q in k.lower()}
    drops = {k: v for k, v in inv["drops"].items() if q in k.lower()}
    if not ranch and not drops:
        sys.exit(f"'{args.item}' никто не производит и не дропает (см. `item` для крафта/сундуков).")
    for item, names in ranch.items():
        print(f"{item} — производится на ранче:")
        for n in names:
            p = idx["pals"][n]
            farm = p["work"].get("Farming", "?")
            print(f"  {label_name(db, n):<28} Farming {farm}  [{'/'.join(p['elements'])}]")
    for item, names in drops.items():
        if item in ranch:
            continue
        pals = sorted(names, key=lambda n: -(idx["pals"][n]["hp"] or 0))
        print(f"{item} — дропается с: " + ", ".join(label_name(db, n) for n in pals[:10]))
    it = (_load_json("items.json") or {}).get("items", [])
    hit = next((i for i in it if i["name"].lower() == q and i.get("recipe")), None)
    if hit:
        mats = ", ".join(f"{m} x{v}" for m, v in hit["recipe"]["materials"].items())
        print(f"Крафт: {hit['recipe'].get('station')} <- {mats}")


# ---------------------------------------------------------------- expeditions

def _exp_element(m):
    req = m.get("element_requirement")
    if isinstance(req, dict):
        return f"{req.get('pals_required', '?')}x {req.get('element', '?')}"
    return req


def cmd_expeditions(db, args):
    data = _load_json("expeditions.json")
    if not data:
        sys.exit("data/expeditions.json missing (not collected yet).")
    if args.name:
        missions = [m for m in data["missions"] if args.name.lower() in m["name"].lower()]
        if not missions:
            sys.exit(f"Mission '{args.name}' not found. Known: " + ", ".join(m["name"] for m in data["missions"]))
        for m in missions:
            el = f"  requires: {_exp_element(m)}" if m.get("element_requirement") else ""
            fp = f"  firepower: {m['required_firepower']:,}" if m.get("required_firepower") else ""
            print(f"{m['name']}  [{m.get('difficulty')}]  {m.get('duration_minutes')} min{fp}{el}")
            u = m.get("unlock") or {}
            if u.get("boss"):
                print(f"  Unlock: beat {u['boss']} ({u.get('boss_difficulty', '')} {u.get('tower', '')})")
            for r in m.get("rewards") or []:
                print(f"    {r['item']} x{r['quantity']}  ({r['chance_pct']:.0f}%)")
    else:
        u = data.get("unlock") or {}
        mats = ", ".join(f"{k} x{v}" for k, v in (u.get("materials") or {}).items())
        print(f"Expeditions — {u.get('structure')} (tech lv {u.get('tech_level')}, {mats})")
        for m in data["missions"]:
            fp = f"  FP {m['required_firepower']:,}" if m.get("required_firepower") else ""
            el = f"  [{_exp_element(m)}]" if m.get("element_requirement") else ""
            print(f"  {m['name']:<38} {m.get('duration_minutes'):>4} min  {m.get('difficulty', ''):<9}{fp}{el}")


# ---------------------------------------------------------------- teams

TEAM_TASKS = ("fishing", "combat", "mining", "lumbering", "production", "ranch", "transport", "cake")


def cmd_team(db, args):
    task = args.task.lower()
    tiers = _load_json("tier_lists.json")
    picks = []  # (name, reason)

    def from_tier(key, n, reason_prefix):
        if not tiers or key not in (tiers or {}):
            return []
        entries = tiers[key] if isinstance(tiers[key], list) else []
        return [(e["name"], f"{reason_prefix}: {e.get('note', 'tier list pick')}") for e in entries[:n]]

    if task == "fishing":
        picks = from_tier("best_for_fishing", 5, "fishing tier list")
        if not picks:
            sys.exit("Fishing team needs data/tier_lists.json (not collected yet).")
    elif task == "combat":
        picks = from_tier("best_fighters", 5, "combat tier list")
        if not picks:
            pals = sorted((p for p in db.values() if p.get("hp")), key=lambda p: -(attack(p) * 2 + p["hp"] + p["defense"]))
            picks = [(p["name"], f"top combat stats (ATK {attack(p)}, HP {p['hp']})") for p in pals[:5]]
    elif task in ("mining", "lumbering"):
        col, pals = rank_workers(db, task)
        picks = [(p["name"], f"{col} {p['work'][col]}") for p in pals[:4]]
        _, movers = rank_workers(db, "transporting")
        movers = [p for p in movers if p["name"] not in {n for n, _ in picks}]
        if movers:
            p = movers[0]
            picks.append((p["name"], f"Transporting {p['work']['Transporting']} — hauls output to chests"))
    elif task == "production":
        # greedy coverage of key production jobs
        needed = ["handiwork", "kindling", "watering", "transporting", "electricity"]
        used = set()
        for t in needed:
            col, pals = rank_workers(db, t)
            for p in pals:
                if p["name"] not in used:
                    used.add(p["name"])
                    others = ", ".join(f"{k} {v}" for k, v in sorted(p["work"].items(), key=lambda x: -x[1]))
                    picks.append((p["name"], f"covers {col} {p['work'][col]} ({others})"))
                    break
    elif task == "cake":
        # торт: Молоко(ранч) + Яйца(ранч) + Мёд(ранч) + плантации ягод/пшеницы + мельница/переноска
        idx = _load_json("index.json") or {"inverted": {"ranch_produce": {}}}
        rp = idx["inverted"]["ranch_produce"]
        for ing in ("Milk", "Egg", "Honey"):
            for n in rp.get(ing, [])[:1]:
                picks.append((n, f"ранч: {ing} (единственный/лучший источник)"))
        _, growers = rank_workers(db, "planting")
        grower = next((p for p in growers if p["work"].get("Watering")), growers[0]) if growers else None
        if grower:
            others = ", ".join(f"{k} {v}" for k, v in sorted(grower["work"].items(), key=lambda x: -x[1]))
            picks.append((grower["name"], f"плантации ягод+пшеницы ({others})"))
        _, hands = rank_workers(db, "handiwork")
        hand = next((p for p in hands if p["work"].get("Transporting")), hands[0]) if hands else None
        if hand:
            others = ", ".join(f"{k} {v}" for k, v in sorted(hand["work"].items(), key=lambda x: -x[1]))
            picks.append((hand["name"], f"мельница (Flour) + готовка + переноска ({others})"))
    elif task == "ranch":
        col, pals = rank_workers(db, "farming")
        picks = [(p["name"], f"Farming {p['work'][col]} — ranch producer") for p in pals[:5]]
    elif task == "transport":
        col, pals = rank_workers(db, "transporting")
        picks = [(p["name"], f"Transporting {p['work'][col]}") for p in pals[:5]]
    else:
        sys.exit(f"Unknown team task '{task}'. Tasks: {', '.join(TEAM_TASKS)}")

    print(f"Team of {len(picks[:5])} for {task}:")
    for name, reason in picks[:5]:
        print(f"  {label_name(db, name):<28} — {reason}")


PARTY_GOALS = ["combat", "openworld", "catch", "fishing", "loot", "eggs", "explore", "xp"]


def _party_accessories(goal, fe=None, enemy=None, weightless=False):
    """Аксессуары под цель пати — data-driven по items.json (поле effect)."""
    data = _load_json("items.json") or {"items": []}
    acc = [i for i in data["items"] if i.get("category") == "accessory" and i.get("effect")]

    def find(pattern):
        rx = re.compile(pattern, re.S)
        return next((i for i in acc if rx.search(i["effect"])), None)

    def by_name(name):
        return next((i for i in acc if i["name"] == name), None)

    out = []

    def obtain(it):
        if it.get("schematic_sources"):
            return ("🧾 схема падает: " + "; ".join(it["schematic_sources"])
                    + (f" → крафт @ {it['recipe']['station']}" if it.get("recipe") else ""))
        if it.get("tech_level"):
            return f"крафт: тех-дерево tech {it['tech_level']} @ {(it.get('recipe') or {}).get('station', '?')}"
        if it.get("recipe"):
            return f"крафт @ {it['recipe']['station']} (разблокировка на paldb не указана)"
        return "источник на paldb не указан"

    def push(it, why):
        if it and not any(n == it["name"] for n, _, _ in out):
            out.append((it["name"], why, obtain(it)))

    if goal == "combat" and fe:
        push(find(rf"Pal Attack Up.*{fe} Damage Enhancement|{fe} Damage Enhancement.*Pal Attack Up"),
             f"бойцу: +атака и +{fe}-урон (батон)")
        push(find(rf"Pal Defense Up.*{fe} Damage Enhancement|{fe} Damage Enhancement.*Pal Defense Up"),
             f"бойцу: +защита и +{fe}-урон (талисман)")
        if enemy:
            push(find(rf"reduces incoming {enemy} damage of the Pal"), f"бойцу: резист от {enemy} (кольцо)")
        push(find(r"raises your Attack, and that of the Pal"), "тебе и палу: +атака (эмблема)")
        if enemy:
            push(by_name(f"Ring of {enemy} Resistance"), f"тебе: резист от {enemy}")
    elif goal == "catch":
        push(find(r"Reveals hidden Pal potentials") or find(r"Mercy Hit"),
             "не убьёшь цель: урон не опускает HP ниже 1 (Mercy Hit)")
        push(by_name("Ring of Trust"), "быстрее растёт доверие палов")
    elif goal in ("loot", "eggs", "fishing"):
        if not weightless:
            push(find(r"Max Carrying Capacity Lv\. 4.*work speed|work speed.*Max Carrying") or find(r"Max Carrying Capacity"),
                 "вес: грузоподъёмность")
            push(find(r"Heat and Cold Resistance.*carrying capacity"), "вес + климат (для дальних ранов)")
        if goal == "loot":
            push(find(r"raises your Attack, and that of the Pal"), "тебе и палу: +атака (эмблема)")
    elif goal == "explore":
        push(find(r"quadruple dashes|triple dashes") or find(r"dash in mid-air"), "мобильность: воздушные дэши")
        push(by_name("Night Vision Goggles"), "ночное зрение")
        push(find(r"Heat and Cold Resistance.*Health"), "климат + HP")
    elif goal == "xp":
        push(find(r"raises Pal EXP"), "+EXP палам")
    elif goal == "openworld":
        push(find(r"Heat and Cold Resistance.*carrying capacity"), "климат + вес")
        push(find(r"extends the invincibility period"), "длиннее i-frames доджа")
    return out


def cmd_party(db, args):
    """Пати из 5 под цель: активен 1 выпущенный пал, остальные дают ауры 'While in party'
    (ключевые не стакаются) — поэтому дефолт: 1 боец + 4 ауры."""
    idx = _load_json("index.json")
    tc_raw = _load_json("type_chart.json")
    if not idx or not tc_raw:
        sys.exit("нужны data/index.json и data/type_chart.json")
    tc = tc_raw["chart"]
    inv = idx["inverted"]["partner_tags"]
    P = idx["pals"]
    goal = args.goal.lower()
    picks, used, notes = [], set(), []
    fighter_skills = {}  # имя пала -> строки с лучшими скиллами против врага

    def eff(n, maxlen=120):
        e = P[n].get("partner_effect") or ""
        return e[:maxlen] + ("…" if len(e) > maxlen else "")

    def best_skills(name, enemy, n_top=3):
        """Топ скиллов из ленсета пала по ДПМ = power x 60/max(кд,5), x2 к стихии слабости.
        baseline CD 5 (метод thepalprofessor) душит спам-скиллы с мелким кд.
        ОЦЕНКА ПО ОДИНОЧНОЙ ЦЕЛИ — по большому боссу решает мульти-хит (см. мета-блок)."""
        sk = _load_json("active_skills.json") or {}
        by = {s["name"]: s for s in sk.get("skills", [])}
        bonus = tc.get(enemy, {}).get("weak_to", []) if enemy else []

        def dpm(s, mult):
            return round(mult * s["power"] * 60 / max(s.get("cooldown_seconds") or 60, 5))

        rows = []
        for e in sk.get("learnsets", {}).get(name, []):
            s = by.get(e["skill"])
            if not s or not s.get("power") or not s.get("cooldown_seconds"):
                continue
            mult = 2 if s["element"] in bonus else 1
            rows.append((dpm(s, mult), mult, e["level"], s))
        rows.sort(key=lambda r: -r[0])
        return [f"{s['name']} [{s['element']}] {s['power']}/{s['cooldown_seconds']}с"
                + (" ×2" if mult > 1 else "") + f" = {d} DPM (Lv{lv})"
                for d, mult, lv, s in rows[:n_top]]

    def meta_skills(fe, n_top=4):
        """Мета-скиллы под босса из skill_dps_meta.json (замеренный сообществом DPS).
        fe = стихия каунтера (если слабость есть), иначе None → универсальный топ."""
        meta = _load_json("skill_dps_meta.json") or {}
        acq = {"exclusive": "эксклюзив", "breeding": "бридинг", "fruit": "Skill Fruit",
               "melee": "ближний бой", "learn": "по уровню"}
        pool = sorted(meta.get("skills", []), key=lambda s: -(s.get("dps_large") or 0))
        picks = [s for s in pool if s["element"] == fe][:3] if fe else pool[:4]
        # ровные all-rounder'ы (учатся любому палу, любой хитбокс) — безопасный филл
        flats = [s for s in pool if not s.get("multi_hit") and (s.get("dps_small") or 0) >= 30
                 and s.get("acquire") in ("fruit", "breeding")]
        for f in flats:
            if len(picks) >= 5:
                break
            if f not in picks:
                picks.append(f)
        out = []
        for s in picks:
            dps = "/".join(filter(None, [f"{s['dps_large']} большой" if s.get("dps_large") is not None else "",
                                          f"{s['dps_small']} мелкий" if s.get("dps_small") is not None else ""]))
            mh = ""
            if s.get("multi_hit"):
                mh = " [мульти-хит]"
                if s.get("dps_large") and s.get("dps_small"):
                    mh += f" ×{s['dps_large'] / s['dps_small']:.1f} по большому телу"
            tag = (" ×2-слабость" if fe and s["element"] == fe else "") + mh
            out.append(f"{s['skill']} [{s['element']}] {dps} DPS{tag} — {acq.get(s['acquire'], s['acquire'])}"
                       + (f" ({s['pal']})" if s.get("pal") else ""))
        return out

    def pick(role, *tags):
        for t in tags:
            for n in inv.get("party:" + t, []) + inv.get(t, []):
                if n not in used:
                    used.add(n)
                    picks.append((n, role, eff(n)))
                    return n
        return None

    def fighter_rank(p):
        """Ранг из консенсусного тир-листа (fighters#N); формула урона множит только Attack."""
        for h in (P.get(p["name"], {}).get("tier_hits") or []):
            if h.startswith("fighters#"):
                return int(h[9:])
        return 999

    def fighter_key(p):
        return (fighter_rank(p), -attack(p), -(p["hp"] + p["defense"]))

    def top_fighter(element=None, exclude=()):
        pool = [p for p in db.values() if p.get("hp") and p["name"] not in used and p["name"] not in exclude]
        if element:
            pool = [p for p in pool if element in p["elements"]]
        pool.sort(key=fighter_key)
        return pool[0]["name"] if pool else None

    def add(n, role):
        if n:
            used.add(n)
            picks.append((n, role, eff(n)))

    def pick_weight(role, *tags):
        """Слот грузоподъёмности: пропускается при настройке мира «без веса»."""
        if getattr(args, "weightless", False):
            return None
        return pick(role, *tags)

    def backfill(target):
        """Добить пати до target полезными аурами (после снятых весовых слотов), без дубля ролей."""
        chosen = {n for n, _, _ in picks}
        for role, *tags in [("выживание: хил/сустейн", "survival"),
                            ("бафф игрока: +Attack", "player_atk_unique", "player_atk"),
                            ("стак с пуль: +ATK/DEF активному палу (Orserk)", "bullet_stack", "cd_support")]:
            if len(picks) >= target:
                break
            tag_pals = {p for t in tags for p in (inv.get("party:" + t, []) + inv.get(t, []))}
            if chosen & tag_pals:  # роль уже покрыта кем-то из пати — пропуск
                continue
            pick(role, *tags)

    if goal == "combat" and args.raw:
        # босс без стихийного каунтера (Zanara & Astralym): топ по статам
        def fpool(mount=None):
            pool = [p for p in db.values() if p.get("hp") and p["name"] not in used
                    and p["name"] != "Astralym"]  # сам босс — Not catchable
            if mount:
                pool = [p for p in pool if p.get("mount_type") == mount]
            pool.sort(key=fighter_key)
            return pool
        f1 = (fpool("flying") if args.sea else fpool())[0]["name"]
        add(f1, "⚔ боец-флаер: топ тир-листа + пережить цунами верхом" if args.sea else "⚔ боец (топ тир-листа бойцов)")
        fighter_skills[f1] = best_skills(f1, None)
        f2 = (fpool("swim") or fpool())[0]["name"] if args.sea else fpool()[0]["name"]
        add(f2, "⚔ 2-й боец + плавающий маунт (морская арена) — свап" if args.sea else "⚔ 2-й боец (свап)")
        fighter_skills[f2] = best_skills(f2, None)
        rraw = pick("реген/сустейн: HP пассивно, пока в ПАТИ (не выпускать)", "regen", "survival")
        pick("бафф игрока: +Attack", "player_atk_unique", "player_atk")
        pick("стак с пуль: +ATK/DEF активному палу (до x30)", "bullet_stack", "cd_support")
        notes.append("Стихийного каунтера НЕТ — бойцы по консенсусу тир-листов 1.0; решают Awakening, 4★, пассивки (Legend/Musclehead), уровень")
        if rraw:
            notes.append(f"🌿 Сустейн: {rraw} лечит ПАССИВНО из пати (выпускать не надо, в отличие от Petallia). Бой долгий — реген важнее")
        if args.sea:
            notes.append("Арена — открытое море: плавающий пал ОБЯЗАТЕЛЕН; летающий маунт помогает пережить цунами (player-reported)")
        notes.append("⚡ скиллы у бойцов — оценка по одиночной цели. По большому боссу решает мульти-хит → см. блок 🎯 Мета-скиллы")
    elif goal == "combat":
        fe = args.element and args.element.capitalize()
        enemy = args.vs and args.vs.capitalize()
        if enemy and enemy not in tc:
            sys.exit(f"стихии {enemy} нет. Есть: {', '.join(tc)}")
        if not fe and enemy:
            fe = tc[enemy]["weak_to"][0]
        if not fe:
            sys.exit("укажи --element (стихия твоего бойца) или --vs (стихия врага)")
        if fe not in tc:
            sys.exit(f"стихии {fe} нет. Есть: {', '.join(tc)}")
        if not enemy:
            enemy = (tc[fe]["strong_vs"] or [None])[0]  # None у Neutral (нет strong_vs)
        def fe_pool(mount=None):
            pool = [p for p in db.values() if p.get("hp") and p["name"] not in used and fe in p["elements"]]
            if mount:
                pool = [p for p in pool if p.get("mount_type") in mount]
            pool.sort(key=fighter_key)
            return pool
        f1p = (fe_pool(("flying", "swim")) or fe_pool())[0] if args.sea else fe_pool()[0]
        f1 = f1p["name"]
        add(f1, f"⚔ боец {fe} (выпускаешь его)"
            + (f" — {'летающий' if f1p.get('mount_type') == 'flying' else 'плавающий'} маунт"
               if args.sea and f1p.get("mount_type") else ""))
        fighter_skills[f1] = best_skills(f1, enemy)

        def room():
            return len(picks) < 5
        # приоритет аур: дамаг-множитель бойцу → РЕГЕН/сустейн (пассивно) → бафф твоей атаки
        if room():
            pick(f"аура: +15~30% атаки {fe}-палам", f"elem_team_atk:{fe}", f"weak_point:{fe}", "weak_point:any")
        regen_pick = pick("реген/сустейн: HP пассивно, пока в ПАТИ (не выпускать)", "regen") if room() else None
        # усиление твоей атаки: смена стихии (метка верна) ИЛИ, если такого пала нет, просто +Attack
        if room() and not pick(f"бафф игрока: атаки становятся {fe}", f"attack_type:{fe}:active", f"attack_type:{fe}:mount"):
            pick("бафф игрока: +Attack", "player_atk_unique", "player_atk")
        # последний слот: 2-й боец (свап) при --two-fighters, иначе резист/живучесть
        if args.two_fighters:
            n = None
            if args.sea and room():
                cand = fe_pool(("swim",)) or fe_pool(("flying",))
                if cand:
                    n = cand[0]["name"]
                    add(n, f"2-й боец — {'плавающий' if cand[0].get('mount_type') == 'swim' else 'летающий'} маунт (свап)")
            if not n and room():
                n = pick("2-й боец: гибрид (сам дерётся + стак-аура)", f"stack_atk:{fe}")
            if not n and room():
                n = top_fighter(fe)
                if n:
                    add(n, "2-й боец (запасной)")
            if n:
                fighter_skills[n] = best_skills(n, enemy)
        elif room():
            if enemy:
                pick(f"аура: резист от {enemy} (стихия врага)", f"resist:{enemy}", f"elem_team_def:{fe}", "survival")
            else:  # Neutral-боец: конкретного врага нет — даём живучесть
                pick(f"аура: живучесть ({fe} без стихийного бонуса)", f"elem_team_def:{fe}", "survival")
        if room():  # остался слот — стак с пуль (gun-билд)
            pick("стак с пуль: +ATK/DEF активному палу (до x30)", "bullet_stack", "cd_support")
        if regen_pick:
            notes.append(f"🌿 Сустейн: {regen_pick} лечит ПАССИВНО, пока сидит в пати — выпускать не надо (в отличие от Petallia/Lyleen). "
                         "Celesdir (#157) — непрерывный реген в бою; лайфстил (Felbat/Lovander) масштабируется от твоего урона")
        notes.append("Gun-билд: если бьёшь очередями, замени ауру на Orserk (bullet-stack, +ATK/DEF за пули)")
        if args.sea:
            notes.append("Арена — открытое море: плавающий пал ОБЯЗАТЕЛЕН; летающий маунт помогает пережить цунами (player-reported)")
        if enemy:
            notes.append(f"Пати против {enemy}-врагов ({fe} бьёт {', '.join(tc[fe]['strong_vs']) or '—'}); "
                         f"сам {fe} каунтерится {', '.join(tc[fe]['weak_to']) or '—'}")
        else:
            notes.append(f"{fe} не даёт стихийного бонуса урона (нет strong_vs) — универсальный боец; "
                         f"сам каунтерится {', '.join(tc[fe]['weak_to']) or '—'}")
        if any("Orserk" == n for n, _, _ in picks):
            notes.append("Orserk (#187): стаки дают ПУЛИ — стреляй очередями; Drone Launcher (tech 77, 9 дронов, "
                         "без патронов) набивает стаки сам, в руках — Mechanical Bow (tech 67) сингл-таргет "
                         "(мета-гайды июля 2026, PRELIMINARY)")
        if any("Solenne" == n for n, _, _ in picks):
            notes.append("Solenne: +30~80% атаки игрока ТОЛЬКО если все 5 палов разных видов — не бери дублей")
        notes.append("Глайдер-пал не нужен: в 1.0 есть Wing Pack (слот глайдера) и Air Dash Boots — слот пати не трать")
        notes.append("⚡ скиллы у бойцов — оценка по одиночной цели. По большому боссу решает мульти-хит → см. блок 🎯 Мета-скиллы")
    elif goal == "openworld":
        pick("маунт + бафф атак игрока", "attack_type:Electric:mount", "attack_type:Fire:mount", "attack_type:Ice:mount")
        pick("сферы самонаводятся + вес +300~600", "capture_homing")
        pick("10~50% шанс не потратить сферу", "capture_save")
        pick("детект данжей/сундуков/скрапа", "detect")
        pick("бафф игрока: +Attack", "player_atk_unique", "player_atk", "survival")
        notes.append("Повседневка: транспорт, ловля встречных палов, сундуки, бой. Solenne любит разношёрстную пати")
    elif goal == "catch":
        pick("сферы самонаводятся + вес", "capture_homing")
        pick("шанс не потратить сферу", "capture_save")
        pick("капча выше при броске в спину", "capture_back")
        st = pick("капча выше на статусных целях", "capture_status:Freeze", "capture_status:Ivy-Covered")
        if st and "Freeze" in (P[st].get("partner_effect") or ""):
            add(top_fighter("Ice"), "боец-статусник: морозит цель (Freeze)")
        elif st:
            add(top_fighter("Grass"), "боец-статусник: Ivy-Covered")
        notes.append("Порядок: статусник вешает Freeze/Ivy → капча-бонус Muffly/Souffline срабатывает")
    elif goal == "fishing":
        n = pick("бафф шкалы миниигры", "fishing_gauge")
        n2 = pick("бафф шкалы миниигры", "fishing_gauge")
        for nn in (n, n2):
            if nn and "more slowly" in (P[nn].get("partner_effect") or ""):
                picks[[x[0] for x in picks].index(nn)] = (nn, "шкала миниигры медленнее падает", eff(nn))
            elif nn:
                picks[[x[0] for x in picks].index(nn)] = (nn, "старт шкалы выше + быстрее растёт", eff(nn))
        pick("чаще талантливые палы + водный маунт", "fishing_talent")
        if args.fish == "pals":
            pick("ещё шанс талантливых палов", "fishing_talent")  # Solmora Lux — 2-й талант
            fm = sorted((p for p in db.values() if p.get("mount_type") == "flying" and p["name"] not in used),
                        key=lambda p: -((p.get("movement") or {}).get("sprint") or 0))
            if fm:
                add(fm[0]["name"], "быстрый маунт до точек лова")
            notes.append("Рыбалка на ПАЛОВ: Jelliette (+предметы) НЕ нужна — важны шкала миниигры + "
                         "шанс талантливых (Solmora); выуженного пала ловишь как обычного")
        else:
            pick("+55~95% предметов с рыбалки (Jelliette)", "fishing_loot")
            pick_weight("вес улова (грузоподъёмность)", "weight")
            notes.append("Рыбалка на РЕСУРСЫ: Jelliette +55~95% предметов — ключевая")
        notes.append("Места фарма рыбы/Coralum — query.py resource <название>")
    elif goal == "loot":
        enemy = (args.vs or "Neutral").capitalize()
        add(top_fighter(tc.get(enemy, {}).get("weak_to", [None])[0]), f"боец-каунтер против {enemy}")
        pick(f"+40~80% дропа с {enemy}-врагов", f"loot:{enemy}")
        pick_weight("вес +300~600 + сферы", "capture_homing", "weight")
        pick_weight("вес груза (руда/уголь/еда — смотри замены)", "weight_cargo", "weight")
        pick("бафф игрока: +Attack", "player_atk_unique", "player_atk")
        notes.append(f"--vs {enemy}: фармим {enemy}-палов; лут-ауры есть под каждую стихию (loot:*)")
    elif goal == "eggs":
        pick("45~55% шанс альфа-яйца при подборе", "egg_alpha_chance")
        pick("50~75% шанс второго яйца", "egg_extra_pickup")
        m = [p for p in db.values() if p.get("mount_type") == "flying" and p["name"] not in used]
        m.sort(key=lambda p: -((p.get("movement") or {}).get("sprint") or 0))
        if m:
            add(m[0]["name"], "летающий маунт: облёт точек яиц")
        pick_weight("вес", "weight")
        pick("страховка: хил/защита", "survival")
        notes.append("Ауры яиц работают при ПОДБОРЕ яйца — держи обоих в пати весь маршрут")
    elif goal == "xp":
        pick("аура: +40~80% EXP всем палам пати", "exp_boost")
        add(top_fighter(), "боец-убийца: фармит килы, пока качаемые сидят в пати")
        pick("бафф игрока: +Attack (ты выносишь толпы быстрее)", "player_atk_unique", "player_atk")
        notes.append("Остальные 2 слота — КАЧАЕМЫЕ палы: экспа с каждого кила капает всем в пати")
        notes.append("Аксессуар игрока: Growth Acceleration Bell (Pal EXP Up Lv.3) — "
                     "Ingot x25 + Paldium Fragment x30 + Mysterious Mushroom x10 + Ancient Civ. Parts x3 "
                     "(High Quality Workbench); точный % на paldb не указан")
        notes.append("Ещё быстрее: Applied Technique Handbook (+уровень работ) и Statue of Power — это не EXP, но качает силу")
    elif goal == "explore":
        biome = (args.biome or "").lower()
        if biome == "cold":
            pick("+2 Cold Resistance", "climate_cold")
        elif biome in ("heat", "desert"):
            pick("+2 Heat Resistance", "climate_heat")
        if biome in ("heat", "desert"):
            pick("+50~100% скорость по песку (маунт)", "terrain:sand")
        pick("детект данжей/сундуков/скрапа", "detect")
        pick("открывает сундуки без ключей", "treasure_open")
        pick("инвиз для игрока и пала", "stealth")
        m = [p for p in db.values() if p.get("mount_type") == "flying" and p["name"] not in used]
        m.sort(key=lambda p: -((p.get("movement") or {}).get("sprint") or 0))
        while len(picks) < 5 and m:
            add(m.pop(0)["name"], "летающий маунт")
        notes.append("--biome cold|heat: слот климата (Arsox/Reindrix) вместо пятого")
    else:
        sys.exit(f"Неизвестная цель '{goal}'. Цели: {', '.join(PARTY_GOALS)}")

    if getattr(args, "weightless", False) and goal in ("loot", "fishing", "eggs"):
        if goal == "fishing":  # рыбалка — не бой: быстрый маунт до точек лова вместо сустейна
            fm = sorted((p for p in db.values() if p.get("mount_type") == "flying" and p["name"] not in used),
                        key=lambda p: -((p.get("movement") or {}).get("sprint") or 0))
            if fm:
                add(fm[0]["name"], "быстрый летающий маунт — добраться до точек лова")
            notes.append("Настройка мира «без веса»: слот грузоподъёмности заменён на быстрый маунт (до точек лова)")
        else:
            backfill(5)
            notes.append("Настройка мира «без веса»: слоты грузоподъёмности убраны, заменены на сустейн/атаку")

    title = {"combat": "боя", "openworld": "опенворлда", "catch": "ловли палов", "fishing": "рыбалки",
             "loot": "лут-рана", "eggs": "сбора яиц", "explore": "исследования", "xp": "прокачки палов"}[goal]
    print(f"Пати для {title} (активен 1 пал, остальные — ауры из пати):")
    for n, role, e in picks[:5]:
        print(f"  {label_name(db, n):<28} — {role}")
        print(f"      {e}")
        for line in fighter_skills.get(n, []):
            print(f"      ⚡ {line}")
    if goal == "combat":
        meta_fe = locals().get("fe") if not args.raw else None
        ms = meta_skills(meta_fe)
        if ms:
            hb = f"каунтер {meta_fe}" if meta_fe else "бестиповый босс"
            print(f"  🎯 Мета-скиллы под босса ({hb}) — замеренный DPS, учи фруктом/бридингом:")
            for line in ms:
                print(f"    {line}")
            meta = _load_json("skill_dps_meta.json") or {}
            for g in (meta.get("guidance") or [])[:2]:
                print(f"    · {g}")
    accs = _party_accessories(goal, locals().get("fe"), locals().get("enemy"), getattr(args, "weightless", False))
    if accs:
        print("  🎗 Аксессуары:")
        for name, why, src in accs:
            print(f"    {name:<28} — {why}")
            print(f"        📥 {src}")
    for note in notes:
        print(f"  ! {note}")


def cmd_tiers(db, args):
    tiers = _load_json("tier_lists.json")
    if not tiers:
        sys.exit("data/tier_lists.json missing (not collected yet).")
    key = args.category
    node = tiers.get(key) or (tiers.get("best_base_workers_by_task") or {}).get(key)
    if node is None:
        flat = [k for k in tiers if isinstance(tiers[k], list)]
        work = list((tiers.get("best_base_workers_by_task") or {}).keys())
        sys.exit(f"Unknown category '{key}'. Available: {', '.join(flat + work)}")
    for e in node:
        print(f"  {label_name(db, e['name']):<28} — {e.get('note', '')}")


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="Palworld 1.0 KB query tool")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pal"); p.add_argument("name")
    p = sub.add_parser("workers"); p.add_argument("task", help="задача или НЕСКОЛЬКО через запятую (условие И): planting,watering")
    p.add_argument("--top", type=int, default=10); p.add_argument("--element")
    p.add_argument("--speed", action="store_true", help="сортировать по скорости бега (для транспорта: уровень качается книгами)")
    p = sub.add_parser("mounts"); p.add_argument("kind", choices=["ground", "flying", "swim"]); p.add_argument("--top", type=int, default=10)
    p = sub.add_parser("fighters"); p.add_argument("--top", type=int, default=10); p.add_argument("--element")
    p = sub.add_parser("counter"); p.add_argument("element")
    p = sub.add_parser("boss"); p.add_argument("name")
    p = sub.add_parser("breed"); p.add_argument("parent_a"); p.add_argument("parent_b")
    p = sub.add_parser("breed-to"); p.add_argument("target"); p.add_argument("--with", dest="with_pal"); p.add_argument("--top", type=int, default=15)
    p = sub.add_parser("breed-chain"); p.add_argument("start"); p.add_argument("target")
    p = sub.add_parser("team"); p.add_argument("task")
    p = sub.add_parser("tiers"); p.add_argument("category")
    p = sub.add_parser("item"); p.add_argument("name")
    p = sub.add_parser("craft"); p.add_argument("name"); p.add_argument("--qty", type=int, default=1); p.add_argument("--flat", action="store_true", help="don't expand sub-recipes")
    p = sub.add_parser("drops"); p.add_argument("item")
    p = sub.add_parser("skills"); p.add_argument("name")
    p = sub.add_parser("skill"); p.add_argument("name")
    p = sub.add_parser("passive"); p.add_argument("name")
    p = sub.add_parser("where"); p.add_argument("name")
    p = sub.add_parser("resource"); p.add_argument("name")
    p = sub.add_parser("expeditions"); p.add_argument("name", nargs="?")
    p = sub.add_parser("produce"); p.add_argument("item")
    p = sub.add_parser("party"); p.add_argument("goal", help=f"цель: {', '.join(PARTY_GOALS)}")
    p.add_argument("--element", help="(combat) стихия твоего бойца")
    p.add_argument("--vs", help="(combat/loot) стихия врага")
    p.add_argument("--two-fighters", action="store_true", help="(combat) 2 бойца + 3 ауры вместо 1+4")
    p.add_argument("--raw", action="store_true", help="(combat) босс без стихийного каунтера: топ по статам")
    p.add_argument("--sea", action="store_true", help="(combat --raw) морская арена: swim обязателен, флаер от цунами")
    p.add_argument("--biome", help="(explore) cold | heat | desert")
    p.add_argument("--fish", choices=["loot", "pals"], default="loot",
                   help="(fishing) loot = ради ресурсов (Jelliette); pals = выуживать палов (без Jelliette)")
    p.add_argument("--weightless", action="store_true", help="настройка мира «без веса»: убрать весовые ауры")

    args = ap.parse_args(argv)
    db = load_db()
    {
        "pal": cmd_pal, "workers": cmd_workers, "mounts": cmd_mounts,
        "fighters": cmd_fighters, "counter": cmd_counter, "boss": cmd_boss,
        "breed": cmd_breed, "breed-to": cmd_breed_to, "breed-chain": cmd_breed_chain,
        "team": cmd_team, "tiers": cmd_tiers,
        "item": cmd_item, "craft": cmd_craft, "drops": cmd_drops,
        "skills": cmd_skills, "skill": cmd_skill, "passive": cmd_passive,
        "where": cmd_where, "resource": cmd_resource, "expeditions": cmd_expeditions,
        "produce": cmd_produce, "party": cmd_party,
    }[args.cmd](db, args)


if __name__ == "__main__":
    main()
