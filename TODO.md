# TODO

## Translate everything back to English (no Russian anywhere)

The project drifted into mixed Russian/English. Goal: **all user-facing and repo text in English only.**
Canonical pal/item/skill names are already English — keep them untouched.

Scope checklist:

- [ ] `web/index.html` — all UI strings: tab names, filter labels/chips, table headers,
      pal card, breeding calculator + FAQ (11+ sections), counters tab (trait cards,
      raid card, top-3 fighters), party creator (goals, roles, notes), base planner
      (presets, options, notes/assumptions), tooltips, placeholders.
- [ ] `web/palworld_kb_standalone.html` — regenerate via `python3 scripts/build_standalone.py`
      after index.html is translated (do not edit by hand).
- [ ] `scripts/query.py` — CLI output strings (party/boss/workers/mounts/passive/breed-chain
      hints, trait blocks, help texts).
- [ ] `scripts/base_planner.py` — presets output: notes, assumptions, role labels, argparse help.
- [ ] `scripts/collectors/*.py` — docstrings and print messages.
- [ ] `data/*.json` — Russian text inside data fields:
      `bosses.json` (categories_note, world-boss notes), `combat_traits.json` (roles, effects,
      alternatives, ehp_math, surgery_table), `passives.json` (mutation notes),
      `skill_dps_meta.json` (notes/guidance), `breeding.json` (notes), `expeditions.json`,
      `pal_locations.json` / `regions.json` / `merchants.json` (any RU remnants).
- [ ] `docs/*.md` — mixed-language guides: boss_fighting.md, base_locations.md,
      breeding_mechanics.md (§9–10), base_setup.md (transport/farm section),
      resource_locations.md, expeditions.md, boss_tower_counters.md.
- [ ] `README.md` — done (English since 2026-07-19).
- [ ] `CLAUDE.md`, `DATA_SOURCES.md` — translate maintainer docs.
- [ ] Git: keep commit messages in English going forward; update repo About description.

Notes:
- Translate meaning, not word-for-word; keep game terms (work suitability, partner skill,
  combi rank, STAB) as-is.
- After translating `data/` or `web/`, run: `python3 scripts/build_index.py`,
  `python3 scripts/validate_data.py`, `python3 -m unittest discover tests`,
  `python3 scripts/build_standalone.py`.
