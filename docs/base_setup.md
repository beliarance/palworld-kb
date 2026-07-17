# Palworld 1.0 — Production Base Setup

Knowledge-base note for building a self-sufficient production base from scratch.
Game version: **Palworld 1.0** (released 10 July 2026). Crafting costs below are drawn from the
current palworld.wiki.gg (last edited Feb 2026, Feybreak-era data) and are marked **(pre-1.0 guide)**
where 1.0 has not been confirmed to change them. Limit/cap figures affected by 1.0 are marked
**(PRELIMINARY 1.0)**.

---

## 1. Base limits, worker slots, base count

- **Worker Pal slots per base — default cap: 15.** You reach 15 active workers around base level 15
  on default difficulty; extra Pal slots unlock as base level rises. (pre-1.0 guide)
- **Base count (per guild) — default cap: 4 bases.** (PRELIMINARY 1.0 — some sources still cite the
  older cap of 3; 1.0 raises the ceiling as base level climbs to the new max **Base Level 35**.)
- **Adjustable via World Settings sliders:** "Maximum number of work Pals at the base" and "Maximum
  number of bases for each guild." Feybreak raised the slider maximums to **50 work Pals** and
  **10 bases**; these remain the ceilings in 1.0. (PRELIMINARY 1.0)
- **Palbox upgrades raise the worker slot count** — keep upgrading the Palbox and completing each base
  level's objectives to unlock more slots. (pre-1.0 guide)
- **Base radius:** buildings must sit inside the Palbox's ~35 m blue claim circle. Anything built
  outside slowly deteriorates. The Ranch and similar structures MUST be inside the boundary.
- **Moving a base:** disassembling the Palbox refunds the materials used in base structures.

---

## 2. Core stations — what they do + crafting cost

All costs are per-1 build. Tech tier = required level to unlock; point cost = technology points.
(All figures pre-1.0 guide unless noted.)

| Station | Tech tier / pts | Materials | Function / worker used |
|---|---|---|---|
| **Palbox** | 2 / 1 | Paldium Fragment 1, Wood 8, Stone 3 | Core base anchor: Pal storage, fast-travel, respawn, defines claim radius, enables worker assignment. |
| **Wooden Chest** | 2 / 1 | Wood 15, Stone 5 | Storage, 10 slots. No power/worker. |
| **Feed Box** | 4 / 2 | Wood 20 | Food storage — Pals auto-eat from it. Place central/near work areas to cut travel. No power/worker. |
| **Ranch** | 5 / 2 | Wood 50, Stone 20, Fiber 30 | Pals with **Farming** graze and drop items (milk/eggs/honey/wool). Holds up to 4 Pals. |
| **Berry Plantation** | 5 / 2 | Berry Seeds 3, Wood 20, Stone 20 | Grows **Red Berries**. Workers: **Planting + Watering + Gathering**. |
| **Crusher** | 8 / 2 | Wood 50, Stone 20, Paldium Fragment 10 | Crushes materials (e.g. stone→Paldium routes, ingots). Worker: **Watering**. |
| **Hot Spring** | 9 / 2 | Wood 30, Stone 15, Paldium Fragment 10, Pal Fluids 10 | Restores Pal SAN / raises happiness. Holds 2 small or 1 large Pal. No worker. |
| **Primitive Furnace** | 10 / 3 | Wood 20, Stone 50, Flame Organ 3 | Smelts Ore→Ingot (2:1) and Wood→Charcoal (2:1). Worker: **Kindling** (1 at a time). |
| **Medieval Medicine Workbench** | 12 / 2 | Wood 30, Nail 5, Paldium Fragment 10 | Crafts meds (Low Grade Medical Supplies etc.). Worker: **Medicine Production**. |
| **Human-Powered Generator** | 13 / 1 | Wood 50, Electric Organ 5 | Early electricity. ANY Pal turns it (no Electricity suitability needed); drains their SAN. Low output. |
| **Mill** | 15 / 2 | Wood 50, Stone 40 | Wheat→**Flour**. Worker: **Watering** (1 at a time). |
| **Wheat Plantation** | 15 / 2 | Wheat Seeds 3, Wood 35, Stone 35 | Grows **Wheat**. Workers: **Planting + Watering + Gathering**. |
| **Cooking Pot** | 17 / 2 | Wood 20, Ingot 15, Flame Organ 3 | Advanced cooking incl. **Cake**. Worker: **Kindling**. |
| **Breeding Farm** | 19 / 2 | Wood 100, Stone 20, Fiber 50 | 1 male + 1 female + 1 Cake → Pal Egg. Runs on its own (no worker). |
| **Power Generator** | 26 / 3 | Ingot 50, Electric Organ 20 | Mid/late electricity. Worker: **Generating Electricity**. |

**Refinement/ratios worth memorizing:** Furnace Ore→Ingot 2:1; Mill Wheat→Flour ~3:1 (15 Wheat = 5 Flour).

**Support structures (build all work-speed boosters for up to ~20% efficiency):** Stump and Axe
(Lumbering), Mining Cart / Stone Pit boosters, Water Fountain, Flower Bed, Silo, Large Toolbox,
Monitoring Stand (locks a specialist Pal to one station so it never wanders). (pre-1.0 guide)

---

## 3. Starter material checklist (self-sufficient early base)

Approximate raw totals to lay down the core early buildings below (Palbox, 2–3 chests, Feed Box,
Ranch, Berry + Wheat Plantation, Mill, Primitive Furnace, Cooking Pot, Human-Powered Generator, Hot
Spring, plus foundations/walls/roof for a small shelter). (pre-1.0 guide)

- **Wood:** ~450–550 (biggest sink — Ranch 50, Wheat 35, Berry 20, Mill 50, Furnace 20, Cooking Pot 20,
  Generator 50, Hot Spring 30, chests + structure frames)
- **Stone:** ~250–350 (Furnace 50 alone, Mill 40, Wheat 35, Berry 20, Ranch 20, Hot Spring 15, walls)
- **Paldium Fragments:** ~30–40 (Palbox 1, Crusher 10, Hot Spring 10, Medicine bench 10, spheres)
- **Fiber:** ~80–100 (Ranch 30, Breeding Farm 50 when reached)
- **Ingot:** ~15–30 (Cooking Pot 15; needs Ore mined + Furnace running first)
- **Flame Organ:** ~6 (Furnace 3, Cooking Pot 3 — farm from fire Pals)
- **Electric Organ:** ~5 (Human-Powered Generator; more for Power Generator later)
- **Seeds:** Wheat Seeds 3, Berry Seeds 3 (consumed only at build; plot keeps producing after)
- **Pal Fluids:** ~10 (Hot Spring)

Tip: unlock Berry Plantation at Lv 5 and Wheat Plantation + Mill at Lv 15 to stop hand-gathering.
Set up **Logging Site / Stone Pit / Ore Mining Site** so Wood/Stone/Ore auto-generate.

---

## 4. Optimal worker role layout (balanced ~15-slot base)

Design philosophy (1.0 community consensus): **specialists beat generalists** — one Pal with a high
single suitability out-produces one Pal with many low ones and condenses far better. Use a
**Monitoring Stand** to pin single-skill Pals to a station. (PRELIMINARY 1.0 — role counts are a
practitioner guideline, not an official spec.)

Priority order to staff: **Handiwork and Mining first** (Handiwork runs every bench; Mining feeds all
ingots), then **Kindling + Electricity** (refining/power), then support jobs.

Suggested balanced spread for a ~15-worker production base:

- **Handiwork:** 3–4 (crafting benches, assembly lines — highest demand)
- **Mining:** 2–3 (ore/stone/coal feed)
- **Kindling:** 1–2 (furnace + cooking pot; fire type required)
- **Watering:** 1–2 (Mill, Crusher, plantations)
- **Planting:** 1 (plantations — pairs with Watering + Gathering)
- **Gathering:** 1 (harvest crops/berries; often doubled by planting/watering Pals)
- **Lumbering:** 1 (wood)
- **Transporting:** 1–2 (hauls output to storage — prevents pathing jams)
- **Generating Electricity:** 1 (once Power Generator is up)
- **Cooling:** 0–1 (only if you run a Cold Food Box / ice recipes)
- **Medicine Production:** covered situationally (assign as needed)

Layout tips: keep it **compact**; put storage chests **between mining sites and the furnace**, and the
**Feed Box central** so hungry Pals don't cross the whole base. Building all work-speed structures +
feeding a strong meal (e.g. Minestrone/Salad) keeps Pals faster for longer.

**Named best-in-slot workers (1.0):** Anubis (Handiwork 4 / Mining 3, best early all-rounder),
Selyne/Solenne (Handiwork), Blazamut / Astegon (Mining), Jormuntide Ignis / Blazamut Ryu (Kindling),
Jormuntide (Watering), Orserk (Electricity), Celesdir (Lumbering), Lyleen (Planting),
Frostallion Noct (Gathering), Wumpo (Transporting), Frostallion (Cooling), Bellanoir (Medicine).

---

## 5. What to produce — Cake chain (breeding) + food

### Cake (breeds Pals — 1 whole Cake per egg hatched via Breeding Farm)
- **Recipe (per 1 Cake, Cooking Pot, needs a Kindling Pal):**
  **Flour ×5, Red Berries ×8, Milk ×7, Eggs ×8, Honey ×2.** (Cooking Pot unlocks Lv 17.)
- **Full ingredient chain:**
  - **Flour** ← Wheat via **Mill** (~3 Wheat → 1 Flour, so ~15 Wheat per Cake). Wheat from **Wheat
    Plantation** (Planting + Watering + Gathering Pals).
  - **Red Berries** ← **Berry Plantation** (easiest to stockpile; also grow wild).
  - **Milk** ← **Mozzarina** on a **Ranch** (Milk Maker skill, produces passively).
  - **Eggs** ← **Chikipi** on a **Ranch** (lays eggs passively).
  - **Honey** ← **Beegarde** (or **Cinnamoth** / Warsect / Elizabee) on a **Ranch**.
- **Self-sufficient cake base = Wheat Plantation + Mill + Berry Plantation + Ranch (Mozzarina, Chikipi,
  Beegarde) + Cooking Pot.** A single Ranch holds 4 Pals — running all three producers + one spare.
  Some builders run a dedicated cake/breeding base and a separate mining/crafting base.

### Food / feed for workers
- **Feed Box** stocked with cooked meals keeps worker Pals fed and productive; a hungry Pal stops
  working. Cook simple dishes (Baked Berries early; Minestrone / Salad later for work-speed buffs).
- Same crop/ranch infrastructure that feeds the Cake chain also feeds worker meals — build the
  plantations and ranch once, feed both pipelines.

---

## Выбор палов: транспорт и ферма (1.0)

**Транспортники.** Уровень Transporting = сколько предметов пал несёт за раз из стопки;
**на скорость передвижения уровень НЕ влияет** (game8). Уровень легко добить книгами (+1
Applied Handbook) и 4★-конденсом (до 10) — поэтому при выборе транспортника смотри на
**скорость, а не на стартовый уровень**. ВАЖНО: у переноски **два** стата — `Transport Speed`
(скорость с грузом, ГЛАВНЫЙ) и `Run Speed` (общий бег). Это разные значения: высокий run
≠ хороший транспортник (напр. **Mimog** run 2000, но Transport Speed лишь 450). Лучшие
**по Transport Speed** (из данных paldb):
- **Eye of Cthulhu** — TS **600** (макс), T4. Топ по чистой скорости переноски.
- **Faleris / Faleris Aqua (#188)** — TS 500, run 1000 (быстры в обоих) — сбалансированный топ.
- **Silvance (#193)** TS 500; **Anubis (#139)** TS 480 T4; **Quivern (#124)** TS 470.
- **Eidrolon / Eidrolon Ignis (#171)** — TS 400, но run 1400 и стартовый **T6**; **Helzephyr Lux**
  — комьюнити хвалит за «transporting movespeed» (TS 450). Оба — частый выбор гайдов.
- **Wumpo** — TS низкий (150), но даёт базовую ауру **+1 Transporting всем**.

Итог: «самый быстрый по бегу» (Mimog) ≠ «лучший транспортник». По реальной скорости переноски
бери **Eye of Cthulhu / Faleris**, либо **Eidrolon** (высокий бег + сразу T6). Уровень докачаешь
книгами. (Вкладка «Рабочие», сортировка «по скорости ПЕРЕНОСКИ».)

**Трейты транспортника** — только **скорость передвижения**, НЕ work-speed: work-бонусы
(Workaholic/Serious/Artisan) на переноску **не влияют** (game8). Стак: **Swift +30% ·
Runner +20% · Legend +20% (легендарки) · Nimble +10%** (складываются). `Dimensional Leap`
+50% — но +15% к голоду (корми чаще). Ещё полезно `Diet Lover`/сытость, т.к. транспортник
много бегает.

**Один пал на всю плантацию?** Плантация требует 3 навыка — **Planting + Watering +
Gathering**. Палов со всеми 3 сразу **нет ни одного** (299/299), а **книги добавить
недостающий навык НЕ могут** — только поднимают уже имеющийся (game8). Максимум близко:
**Ophydia (#175)** — **единственный** пал с Planting **И** Watering (P7 W5). Сбор при этом
подхватывают простаивающие палы (авто-сбор), либо ставь отдельного гатерера. Так что «одним
палом» реально закрыть только посадку+полив (Ophydia), но не все три.
(Мультивыбор работ с условием «И» — во вкладке «Рабочие».)

---

## Sources
- Game8 Work Suitability / Transporting / passives — https://game8.co/games/Palworld/archives/440216 , /439560 , /440414
- thepalprofessor.com — Transporter Pals table
- Game8 Palworld Base Building Guide — https://game8.co/games/Palworld/archives/440240
- Game8 Feed Box / Base Level Rewards — https://game8.co/games/Palworld/archives/441175 , /440428
- palworld.wiki.gg station pages: Primitive Furnace, Ranch, Breeding Farm, Cooking Pot, Crusher, Mill,
  Power Generator, Human-Powered Generator, Hot Spring, Wheat/Berry Plantation, Medieval Medicine
  Workbench, Wooden Chest, Palbox, Feed Box — https://palworld.wiki.gg/wiki/Base
- Cake recipe — https://game8.co/games/Palworld/archives/440196 , https://xgamingserver.com/blog/palworld-cake-recipe/
- Best base Pals (1.0) — https://nexttier.pro/guide/palworld-best-base-pals , https://game8.co/games/Palworld/archives/440432
- Base limits — https://wiki.indifferentbroccoli.com/Palworld/Bases , https://palworld.wiki.gg/wiki/Base
