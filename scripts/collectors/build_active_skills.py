#!/usr/bin/env python3
"""Build data/active_skills.json from the raw paldb.cc collection
(produced by fetch_skills.py). Filters internal boss-only skill ids,
fixes exclusive_to names to match data/palworld_pals.csv, validates.
"""

import csv
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
CANON_ELEMENTS = {"Neutral", "Fire", "Water", "Electric", "Grass", "Ice",
                  "Ground", "Dark", "Dragon"}
INTERNAL_RE = re.compile(r"_")  # display names never contain underscores


def main():
    raw_path = sys.argv[1]
    out_path = sys.argv[2]
    raw = json.load(open(raw_path, encoding="utf-8"))

    with open(os.path.join(ROOT, "data", "palworld_pals.csv"),
              newline="", encoding="utf-8") as f:
        csv_names = {r["Name"] for r in csv.DictReader(f)}

    # who learns which skill (used to repair internal exclusive ids)
    learners = {}
    for pal, ls in raw["learnsets"].items():
        for e in ls:
            learners.setdefault(e["skill"], set()).add(pal)

    notes, gaps, skills = [], [], []
    internal_dropped = 0
    for s in raw["skills"]:
        if INTERNAL_RE.search(s["name"]):
            internal_dropped += 1
            continue
        if s["element"] not in CANON_ELEMENTS:
            gaps.append(f"skill '{s['name']}' has non-canonical element "
                        f"{s['element']!r}; set to null")
            s["element"] = None
        # repair exclusive_to entries that are internal codenames
        if s["exclusive_to"]:
            fixed = []
            for n in s["exclusive_to"]:
                if n in csv_names:
                    fixed.append(n)
                else:
                    cands = sorted(learners.get(s["name"], set()) & csv_names)
                    if len(cands) == 1:
                        fixed.append(cands[0])
                        notes.append(
                            f"exclusive_to for '{s['name']}': paldb shows "
                            f"internal id '{n}', mapped to '{cands[0]}' "
                            f"(only pal that learns it)")
                    else:
                        gaps.append(
                            f"exclusive_to for '{s['name']}': '{n}' not in "
                            f"pal CSV and could not be resolved; dropped")
            s["exclusive_to"] = fixed or None
        skills.append({
            "name": s["name"],
            "element": s["element"],
            "power": s["power"],
            "cooldown_seconds": s["cooldown_seconds"],
            "range": s["range"],
            "description": s["description"],
            "exclusive_to": s["exclusive_to"],
            "skill_fruit_exists": s["skill_fruit_exists"],
        })

    # dedupe: paldb lists per-pal internal variants under the same display
    # name (slightly different range/cooldown, sometimes placeholder text).
    # Keep the best entry per name: real description > has skill fruit >
    # first occurrence.
    by_name = {}
    dup_names = set()
    for i, s in enumerate(skills):
        key = s["name"]
        score = (s["description"] not in ("", "en Text"),
                 bool(s["skill_fruit_exists"]), -i)
        if key in by_name:
            dup_names.add(key)
            if score > by_name[key][0]:
                by_name[key] = (score, s)
        else:
            by_name[key] = (score, s)
    if dup_names:
        skills = [by_name[s["name"]][1] for s in skills
                  if by_name[s["name"]][1] is s]
        notes.append(
            f"duplicate variant entries merged for: "
            f"{', '.join(sorted(dup_names))} (paldb lists per-pal internal "
            f"variants of these skills with slightly different "
            f"range/cooldown; kept the primary entry)")

    skill_names = {s["name"] for s in skills}
    learnsets = {}
    for pal, ls in sorted(raw["learnsets"].items()):
        assert pal in csv_names, f"learnset pal {pal} not in CSV"
        for e in ls:
            assert e["skill"] in skill_names, \
                f"{pal} learnset skill {e['skill']} missing from skills list"
        learnsets[pal] = sorted(ls, key=lambda e: e["level"])

    if internal_dropped:
        notes.append(
            f"{internal_dropped} internal/boss-only skill entries "
            f"(untranslated Unique_*/PartnerSkill ids, e.g. raid & tower "
            f"boss moves) were excluded from the skills list; raw HTML kept "
            f"in data/raw/paldb_active_skills.html")
    notes.append("power/cooldown/range/description scraped from paldb.cc "
                 "Active Skills index (server-rendered, reflects game v1.0 "
                 "as of fetch date); power 0 = status/utility skill")
    notes.append("range is given verbatim from paldb.cc tooltips, e.g. "
                 "'Shot Attack Range 500-5000' (game units)")
    notes.append("skill_fruit_exists = a Skill Fruit item exists for the "
                 "skill on paldb.cc")

    for f in raw.get("failures", []):
        gaps.append(f"learnset missing: {f}")
    missing_pals = sorted(csv_names - set(learnsets))
    if missing_pals:
        gaps.append(f"learnsets cover {len(learnsets)}/{len(csv_names)} "
                    f"pals; missing: {', '.join(missing_pals)}")

    out = {
        "game_version": "1.0",
        "updated": date.today().isoformat(),
        "skills": skills,
        "learnsets": learnsets,
        "notes": notes,
        "gaps": gaps,
        "sources": [
            {"url": "https://paldb.cc/en/Active_Skills",
             "what": "full active skills index: name, element, power, "
                     "cooldown, range, description, exclusivity, skill fruit",
             "fetched": date.today().isoformat()},
            {"url": "https://paldb.cc/en/<PalName> (299 pal pages)",
             "what": "per-pal level-up learnsets (Active Skills section)",
             "fetched": date.today().isoformat()},
        ],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"skills={len(skills)} learnsets={len(learnsets)}/{len(csv_names)} "
          f"exclusives={sum(1 for s in skills if s['exclusive_to'])} "
          f"gaps={len(gaps)}")


if __name__ == "__main__":
    main()
