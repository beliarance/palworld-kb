# Palworld 1.0 Knowledge Base

**Live:** https://beliarance.github.io/palworld-kb/web/ — web UI, works on any device
(redeployed on every `git push`).

A knowledge base for **Palworld 1.0** (full release, July 10 2026): structured data on all
299 pals + mechanics guides + a CLI tool + a dependency-free web app that answer practical
in-game questions.

> ⚠️ UI/docs are currently a Russian/English mix — full translation to English is planned,
> see [TODO.md](TODO.md).

## What it can do

- **Pal browser**: search + filters (elements, size, mount type, nocturnal, work suitability
  with AND-condition) + sortable columns — paldex #, HP/ATK/DEF, expedition Firepower
  (`(ATK + DEF + HP/5) × (stars+1)²`), run/sprint, transport speed, swim speed, combi rank.
  Only obtainable pals are listed.
- **Breeding**: three modes — pair → child, target → parent pairs, and shortest
  trait-carrying chain (BFS); exact 1.0 combi-rank formula (ties break to the HIGHER rank,
  verified in-game) + special combos; breeding FAQ (IV, passives, mutations, cakes, condenser).
- **Counters**: element chart, tower bosses, altar raids (fought AT YOUR BASE by assigned
  pals + turrets) vs world bosses, full combat parties with best-DPM skills, measured
  boss-DPS meta skills (multi-hit vs large hitbox), combat trait builds (simple grafted /
  rainbow with alternatives, raid EHP math), accessories with sources.
- **Party creator**: 5-pal parties per goal — combat (element/vs-enemy/2-fighters),
  open world, catching, fishing (resources vs pal-fishing), loot runs, egg collecting,
  exploration (cold/heat), XP; passive in-party regen aura included for boss fights.
- **Base planner**: presets (breeding / mine-craft / food hub / starter) with building
  bills of materials, worker rosters, Work Speed model calibrated to real measurements
  (baseline 100 / traits 255 / traits+4★ 357 / +souls 572), yield supports, food module.
- **Items**: 1195 items — recipes, stations, raw-material crafting breakdown, drop sources,
  84 accessories with effects and schematic drop locations.
- **Skills & passives**: 328 active skills with per-pal learnsets, 114 passives with exact
  numbers, 5 rainbow mutation passives (obtainable via mutation eggs, then inheritable).
- **Locations**: where to find/catch every pal (wild spawns, alphas with coordinates, eggs)
  and best resource farming spots; 38 merchant shops.
- **Expeditions**: all 18 missions with reward pools and the Firepower formula.

## Web UI

```bash
python3 -m http.server 8842        # from the repo root
# → http://localhost:8842/web/
```

**Standalone build** (single file, no server needed):
`python3 scripts/build_standalone.py` → `web/palworld_kb_standalone.html` (~1.8 MB, all data
embedded) — copy anywhere, open by double-click. Rebuild after changing `data/` or `web/index.html`.

Tabs: Pals (browser + full profile), Breeding (calculator + FAQ), Counters (elements & bosses),
Items, Tier lists, Expeditions, Resources, Passives, Skills, Party, Base planner.
No dependencies — the page reads JSON straight from `data/`.

## Quick start (CLI)

```bash
python3 scripts/query.py workers mining              # best miners
python3 scripts/query.py workers planting,watering   # multi-task AND filter
python3 scripts/query.py workers transporting --speed # sort by transport speed
python3 scripts/query.py mounts swim                 # swim mounts by swim-dash speed
python3 scripts/query.py counter dark                # what beats Dark
python3 scripts/query.py boss hartalis               # raid boss counter + traits
python3 scripts/query.py breed Anubis Penking        # breeding result
python3 scripts/query.py breed-to Anubis             # how to get Anubis
python3 scripts/query.py breed-chain Turtacle Menasting  # trait-carrying chain
python3 scripts/query.py party combat --vs water     # 5-pal party vs Water enemies
python3 scripts/query.py party fishing --fish pals   # fishing party (pal-fishing mode)
python3 scripts/query.py where Anubis                # spawns / alphas / eggs
python3 scripts/query.py item "Pal Sphere"           # recipe and sources
python3 scripts/query.py craft "Rocket Launcher"     # raw-material breakdown
python3 scripts/base_planner.py breeding --tech 80   # breeding base blueprint
```

No dependencies — plain Python 3.

## Layout

```
data/     — machine-readable data (csv/json), single source of truth
docs/     — mechanics guides (markdown)
scripts/  — query.py (CLI), base_planner.py, validate_data.py, collectors/
tests/    — python3 -m unittest discover tests
web/      — dependency-free SPA (reads data/*.json)
```

Data schemas are described in [CLAUDE.md](CLAUDE.md); every data update is logged with its
source in [DATA_SOURCES.md](DATA_SOURCES.md). Breeding/planner logic is intentionally
duplicated in Python (`scripts/`) and JS (`web/index.html`) — change both.

## Data status

The game shipped days ago; some community data is still settling. Markers:
`(pre-1.0 guide)` — early-access data, not re-verified; `(PRELIMINARY 1.0)` — fresh 1.0 data
that may change. On conflicts, trust sources explicitly updated for 1.0. Known gaps live in
`gaps`/`notes` fields inside the JSON files.
