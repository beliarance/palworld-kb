# Palworld 1.0 — Breeding Mechanics (Knowledge Base)

Game version: **Palworld 1.0** (full release, 10 July 2026). Notes tagged **(pre-1.0 guide)** are from Early-Access-era guides that remain valid unless changed; **(PRELIMINARY 1.0)** flags newly-added 1.0 systems where community data is still thin — verify in-game.

Primary sources: game8.co/games/Palworld, xgamingserver.com, hostedgg.com, palworld.fandom.com.

---

## 1. Breeding Farm / Ranch Basics

- **Breeding Farm** is the structure that produces eggs. Place a **male + female of any breedable Pals** inside, keep it stocked with **Cake**, and the pair periodically produces an **egg**. (pre-1.0 guide)
- The offspring species is determined by a fixed **breeding combination table** (each parent pair maps to a specific child). In 1.0 the **breeding combinations were reviewed/rebalanced** overall to better match progression — always re-check a combo in an updated breeding calculator. (1.0 change)
- **Cake is consumed per egg** and is the gating resource for breeding.
- **Ranch** is a separate structure — it is where you assign Pals to **produce Cake ingredients** (Milk, Eggs, Honey, Wool, etc.). It does NOT breed.
- **Egg incubation** is done in an **Egg Incubator**; temperature must match the egg type. 1.0 **halves egg incubation time in newly created Normal and Hard worlds**. (1.0 change)
- **Ancient Hatchery** (PRELIMINARY 1.0): unlocked via Ancient Technology around **Level 76**; holds the breeding pair directly, produces eggs in batches, and with maxed research incubates them near-instantly. (PRELIMINARY 1.0 — verify)

---

## 2. Cake Recipe (EXACT ingredients)

Standard **Cake** — cooked in a **Cooking Pot**; recipe unlocks at **Technology Level 17**. (pre-1.0 guide, still current)

| Ingredient | Quantity |
|---|---|
| **Flour** | 5 |
| **Red Berries** | 8 |
| **Milk** | 7 |
| **Egg** | 8 |
| **Honey** | 2 |

### Ingredient sourcing
- **Flour** — grow **Wheat** at a Wheat Plantation, then mill **3 Wheat → 1 Flour** at a **Mill**.
- **Red Berries** — Berry Plantation, or foraged in the wild (common near the Plateau of Beginnings).
- **Milk** — assign a **Mozzarina** to a Ranch.
- **Eggs** — assign a **Chikipi** to a Ranch.
- **Honey** — assign a **Beegarde** (or Cinnamoth) to a Ranch.

### New 1.0 Cakes (breeding-effect cakes) — effects confirmed from paldb.cc item descriptions, 2026-07-14
Recipes: см. `items.json` (Cake/Mushroom Cake @ Cooking Pot, Vegetable Cake @ Electric Kitchen,
Extravagant Vegetable Cake @ Large-Scale Stone Oven, Special Cake @ Ancient Kitchen).
Nutrition/SAN всех тортов — в `data/base_building.json`.

| Cake | Effect (paldb 1.0 text) |
|---|---|
| **Cake** | Enables breeding (baseline requirement), no bonus. |
| **Mushroom Cake** | "The talents of the resulting Pals will grow slightly more easily" (стат-рост/IV). |
| **Vegetable Cake** | "Lay eggs twice at once" — **two eggs per cycle**, doubles throughput / mutation rolls. |
| **Extravagant Vegetable Cake** | "Mutations are more likely to occur, and talents will grow more easily" — **best mutation cake**. В EA-гайдах ошибочно звался "Deluxe Vegetable Cake" — такого предмета в 1.0 нет. |
| **Special Cake** | "More likely inherit multiple passive skills from their parents". |

> Match the cake to the batch goal: **Special Cake** for stacking passives, **Extravagant Vegetable Cake** for chasing mutations, **Vegetable Cake** for raw egg volume.

---

## 3. Passive Skill Inheritance

- Each Pal has **4 passive skill slots**. Up to **all 4 passives can be inherited** from the parents' combined pool (max 8 candidate passives across two 4-passive parents). Max passives on any Pal = **4**. (pre-1.0 guide, still current)
- **Per-passive inheritance probabilities** (game8, ~100-egg sample): (pre-1.0 guide)
  - From **Male parent**: **24%**
  - From **Female parent**: **20%**
  - **No passive inherited**: **34%** (highest single outcome)
- **Male-parent bias:** passives pass more reliably from the **male**. To lock a target passive, put it on the **male** parent.
- If **fewer than 4** passives are inherited, empty slots may be filled by a **random passive**.
- **Both parents having the same target passive does NOT guarantee it** — even then it passes only ~**46%** of the time, with ~**33%** chance of no passive inherited (game8 100-egg sample). (pre-1.0 guide)
- 1.0: **inherited active (attack) skills** are now randomly picked from the **three active-skill slots** set on the parents. (1.0 change)

---

## 4. IVs (Individual Values)

- Hidden **0–100 rolls** for **HP, Attack, Defense**; each is worth up to roughly **+30% of that stat** at max. (pre-1.0 guide)
- **At least one IV is always inherited** from a parent.
- Roughly **~30% chance per stat** to inherit from a given parent; **~40%** rolled randomly.
- Same-species parents with high IVs → breed to concentrate high IVs into offspring. IVs are checkable with an IV checker tool.

---

## 5. Farming a Target 4-Passive Pal (chain-breeding method)

Goal: produce a Pal with an exact set of **4 desired passives** (e.g. Legend + Ferocious + Musclehead + an elemental booster). (pre-1.0 guide, method unchanged in 1.0)

**Core idea:** consolidate the 4 target passives onto two "carrier" parents over several generations, then pair them.

1. **Acquire each passive on a Pal.** Catch or breed Pals each carrying one (or more) of the target passives. Rare passives (Legend, Lucky) can only be **obtained from Pals that already have them**, then passed down — they are not sold by merchants and cannot be randomly rolled.
2. **Combine passives 2-at-a-time.** Breed carrier A (passive 1) × carrier B (passive 2); keep offspring that inherited **both**. Repeat with passive 3, then passive 4 — each generation stacking one more onto a "super-parent."
3. **Prefer putting the hardest-to-pass passive on the MALE** (higher inheritance %).
4. **Pair two loaded parents.** Once you have parents collectively holding all 4 targets, breed them repeatedly and cull until an egg inherits exactly the 4-passive set with no junk random passives.
5. **Use Special Cake** to raise the odds of inheriting multiple passives per egg. Run high volume (Vegetable Cake for 2 eggs/cycle) since inheritance is probabilistic.

### Legend chain-breed example (game8)
- **Legend** is native to **Legendary Pals** (e.g. Paladius, Jetragon, Necromus, Frostallion). Only route to Legend on non-legendaries is inheritance.
- Steps: ① catch a Legendary Pal Ⓐ → ② breed Ⓐ × any parent → Legend-carrier Ⓑ → ③ breed Ⓑ × another parent → Legend-carrier Ⓒ, progressively folding in other desired passives. Legend passes by probability, never guaranteed.

---

## 6. Pal Essence Condenser (Star Ranks)

The **Pal Essence Condenser** ranks up a base Pal by sacrificing **duplicates of the same species** (butchered/caught copies act as "Pal essence"). Boosts stats per star. (game8, current numbers)

| Star rank | Duplicates consumed at THIS tier | Cumulative duplicates (material Pals) |
|---|---|---|
| **1★** | 4 | 4 |
| **2★** | 16 | 20 |
| **3★** | 32 | 52 |
| **4★** | 64 | 116 |

- **Total to reach 4★ = 116 material Pals** (117 copies including the base Pal being upgraded).
- **Already-condensed Pals count as their full sacrifice value** when fed in — e.g. a 1★ Pal counts as 5 copies (itself + its 4). This lets you feed condensed Pals to reach higher tiers more efficiently.
- **Note on older guides:** some pre-patch guides list different per-tier counts (e.g. 8 at 1★, or a 1/2/4/8/16 doubling scheme). Those are **outdated (pre-1.0 guide)** — the **4/16/32/64 (=116 total)** figures are the current game8 numbers. Verify in-game if precision matters.

---

## 7. Mutation (NEW in 1.0)

**(PRELIMINARY 1.0 — datamined/community figures; verify)**

- **What it is:** every breed has a **low chance** the egg hatches as a **mutated** Pal instead of the normal result.
- **Effect:** a mutated Pal has **higher base stats** than the standard version of its species **PLUS one unique "mutation passive"** that cannot be obtained any other way (five mutation-exclusive passives reported).
- Some sources say a mutated egg can even hatch a **different species** than the parent pair normally produces (verify).
- **Base chance ≈ 1%** per egg, rising to **≈3%** with the right cake (community datamine — PRELIMINARY). Practical expectation: **~1–3 mutations per 100 eggs**.
- **How to boost it:**
  - **Extravagant Vegetable Cake** — directly raises mutation chance + stat growth (best cake).
  - **Vegetable Cake** — 2 eggs/cycle → more rolls.
  - **Mushroom Cake** — higher-stat newborns.
- **Strategy:** it's a **volume game** — build a clean passive set on the parents first, run always-on high-throughput breeding, cull everything except mutated/high-stat results.

---

## 8. Awakening (NEW in 1.0)

**(PRELIMINARY 1.0 — verify; exact stat % not yet published)**

- **What it is:** an **endgame, post-hatch** power-up applied to a **finished** Pal — separate from breeding. Stacks on top of **Pal Souls** and **Condenser** ranks.
- **Powered by Radiant Gems**, a new resource hidden deep in the **World Tree** (the 1.0 endgame region). Explore the World Tree depths to collect them; the zone also holds **Paloxite** ore and the **Ancient Civilization Relic**.
- Some guides state **Awakening Gems are crafted by combining Radiant Gems of each element**, and are **spent on Pals of the same elemental type** — i.e. it's an **element-by-element investment**, not universal. (PRELIMINARY 1.0 — verify)
- **Effect:** a **significant boost to the Pal's overall stats**; the Awakening bonus is shown in the Pal's status screen alongside Soul bonuses. (Exact % unconfirmed.)
- **Correct build order (all three stack):**
  1. **Breed** for species + clean passives (chain breeding).
  2. **Chase the Mutation** (higher base stats + unique passive).
  3. **Level + Condense + Souls** the keeper.
  4. **Awaken last** with Radiant Gems, per element, only on final keepers (gems are scarce/endgame-gated — don't waste them on a Pal you'll out-breed).

---

## 9. Best Combat Passives (game8 effect values)

| Passive | Effect | Notes |
|---|---|---|
| **Legend** | **Attack +20%, Defense +20%, Move Speed +15–20%** | Rainbow tier; from Legendary Pals only. |
| **Demon God** | **Attack +30%, Defense +5%** | Rainbow tier (1.0-era top attack passive). (PRELIMINARY 1.0) |
| **Musclehead** | **Attack +30%, Work Speed −50%** | Best raw attack; kills work speed (combat-only). |
| **Ferocious** | **Attack +20%** | No downside — cleanest attack passive. |
| **Burly Body** | **Defense +20%** (immune to flinch) | Tank passive. |
| **Lucky** | **Attack +15%, Defense +15%, Work Speed +20%** | Rainbow; generalist combat+work. |
| **Hooligan** | Attack +15%, Work Speed −10% | Budget attack. |
| **Brave** | Attack +10% | Low tier. |

- **Meta combat stack:** **Legend + Musclehead + Ferocious + an elemental booster** (below). These stack **multiplicatively**; community cites ~**+74% attack** over baseline with the top combo, and a theoretical max stack line of **Attack +100% / Elemental Dmg +50% / Defense +25% / Move Speed +15%**.
- **Serenity** (community note): reduces skill cooldown / boosts skill uptime (applies to active skills like Meteor Rain, Rock Burst, Air Blade, etc.) — strong for skill-based DPS; exact % debated, verify.

### Exclusive Elemental Damage Passives (species-locked, +20% unless noted)

> **1.0 CORRECTION (2026-07-14):** paldb.cc 1.0 data shows all nine Emperor/Lord passives buffed to **+30%** elemental damage (the +20% values below are pre-1.0). Cross-check pending a third source — see `data/passives.json` for current values.

| Passive | Effect | Native Pal |
|---|---|---|
| Celestial Emperor | +20% Neutral dmg | Paladius |
| Divine Dragon | +20% Dragon dmg | Jetragon |
| Earth Emperor | +20% Ground dmg | Anubis |
| Flame Emperor | +20% Fire dmg | Blazamut |
| Ice Emperor | +20% Ice dmg | Frostallion |
| Lord of Lightning | +20% Electric dmg | Orserk |
| Lord of the Sea | +20% Water dmg | Jormuntide |
| Lord of the Underworld | +20% Dark dmg | Necromus |
| Spirit Emperor | +20% Grass dmg | Lyleen |
| **Eternal Flame** | +30% Fire, +30% Lightning dmg | Blazamut Ryu |
| **Invader** | +30% Dark, +30% Dragon dmg | Xenolord |
| **Siren of the Void** | +30% Dark, +30% Ice dmg | Bellanoir Libero |

---

## 10. Best Work Passives (game8 effect values)

| Passive | Effect | Tier |
|---|---|---|
| **Remarkable Craftsmanship** | **Work Speed +75%** | ★★★★★ (top; 1.0-era) (PRELIMINARY 1.0) |
| **Artisan** | **Work Speed +50%** | ★★★★★ (biggest single non-exclusive work buff) |
| **Work Slave** ("Serious/Work Slave") | **Work Speed +30%, Attack −30%** | ★★★★☆ |
| **Serious** | **Work Speed +20%** | ★★★☆☆ |
| **Lucky** | Work Speed +20%, Attack +15%, Defense +15% | ★★☆☆☆ |
| **Conceited** | Work Speed +10%, Defense −10% | ★☆☆☆☆ |

- **Best breedable worker stack:** **Artisan + Work Slave + Serious + Lucky** ≈ **+120–135% Work Speed** (numbers vary by source). Swapping in **Remarkable Craftsmanship** for Artisan pushes higher (**Work Speed +175%** with the top-tier 4-passive line per game8).
- Support/economy passives worth stacking on base Pals: **Diet Lover / Workaholic** (reduce hunger / sanity drain — keep Pals working longer).

### Player-boost / party passives (active party Pal)
| Passive | Effect |
|---|---|
| Motivational Leader | +25% Player Work Speed |
| Mine Foreman | +25% Player Mining Efficiency |
| Logging Foreman | +25% Player Logging Efficiency |
| Vanguard | +10% Player Attack |
| Stronghold Strategist | +10% Player Defense |

### Movement / mount passives
| Passive | Effect |
|---|---|
| **Swift** | +30% Move Speed |
| **Runner** | +20% Move Speed |
| **Nimble** | +10% Move Speed |
| **Legend** | +15–20% Move Speed (plus atk/def) |
| **Eternal Engine** | Move Speed +75%, Attack +20%, Max Stamina +75% (top mount line) (PRELIMINARY 1.0) |

---

## Sources
- game8 — Cake: https://game8.co/games/Palworld/archives/440196
- game8 — Chain Breed Passives / inheritance %: https://game8.co/games/Palworld/archives/441878
- game8 — Best Passive Skills (effect values): https://game8.co/games/Palworld/archives/440414
- game8 — Pal Essence Condenser: https://game8.co/games/Palworld/archives/440237
- game8 — IV Calculator/inheritance: https://game8.co/games/Palworld/archives/445888
- xgamingserver — Mutations (1.0): https://xgamingserver.com/blog/palworld-mutations-guide/
- xgamingserver — Awakening & Radiant Gems (1.0): https://xgamingserver.com/blog/palworld-awakening-radiant-gems/
- hostedgg — Awakening & Mutation (1.0): https://hostedgg.com/blog/palworld-awakening-mutation-guide
- Fandom — Pal Essence Condenser: https://palworld.fandom.com/wiki/Pal_Essence_Condenser


## 9. Наследование: что переходит, а что НЕТ (сводка)

**(1.0 + EA-числа; альфа-% и мутационные пассивки — PRELIMINARY, комьюнити)**

**Переходит потомку:** вид (по ранговой формуле / спец-комбо), пассивки (из пула обоих
родителей, самец 24% / самка 20% / ничего 34% на слот), IV (30% от каждого родителя,
40% рандом; ≥1 всегда), одна атака из пула родителей.

**НЕ переходит (навешивается на потомка заново):**
- **Альфа-статус** — не наследуется; пара альфа+альфа не гарантирует. У яйца бридинга
  лишь ~5% (комьюнити) вылупить альфу независимо от родителей; раздутые статы альфы не идут.
- **Звёзды Condenser** — потомок всегда 0★, конденсировать заново (снова 116 дублей).
- **Уровень** — вылупляется 1-го уровня.
- **Рарность** — не наследуется напрямую: у потомка рарность его ВИДА; ранги/рарность
  родителей лишь определяют вид по формуле.
- **Work-апгрейды мануалом** (Applied Technique Handbook), **апгрейд активок**, **Awakening**
  — все per-pal, не наследуются.

**Статы потомка:** база ВИДА-потомка × вклад IV (до ~+30%) × уровень × звёзды × Pal Souls ×
Awakening. Сырые статы родителей НЕ усредняются — переходят только IV.

**Активные скиллы:** бридинг не задаёт мувсет; потомок наследует какую-то атаку из пула
родителей, конкретный набор ставится **Skill Fruit**'ами уже на потомке.

**Пассивки, которые НЕ вывести бридингом:** мутационно-эксклюзивные — **Babysitter,
Idiosyncratic, Immortality, Heavily Armored, Skirmisher** (из слота мутации, не из пула
родителей; редко «протекают» из ловли) → в data/passives.json помечены `breedable:false,
mutation_exclusive:true`. Партнёрский/сигнатурный скилл пала — не наследуемая пассивка.
Legend/Lucky/«эмперор»-серии наследуются (chain-breeding), но зарождаются только у конкретных палов.

Источники: palworld.wiki.gg/Breeding, allthings.how (1.0 trait inheritance, 2026-07), thepalprofessor
breeding guide, switchbladegaming, boostmatch (mutation-exclusive пассивки), game8.
