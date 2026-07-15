# Palworld — Pal Expeditions

Knowledge-base note. Game: Palworld 1.0 (released 10 July 2026, update 1.100.427).
Expeditions were introduced pre-1.0 (patch v0.4.11, Feybreak era, Jan 2025) and expanded in 1.0. Items marked **(pre-1.0 guide)** were documented before 1.0 and not yet re-verified against the 1.0 build; **(PRELIMINARY 1.0)** are 1.0-specific claims still being confirmed.

Machine-readable companion: `data/expeditions.json` (full reward pools with quantities and drop chances).

---

## 1. What Expeditions are

- **Expeditions** let you dispatch Pals from your **Palbox** on timed, offline missions ("explore areas, engage in battles, and gather resources"). They run in the background while you keep playing and pay out a loot bundle when the timer ends.
- They are the main passive source of hard-to-get items: **Ancient Civilization Parts/Cores, Chromite, Pal Souls, high-tier Spheres, raid Slab Fragments** (Bellanoir, Bellanoir Libero, Blazamut Ryu, **Xenolord**, Hartalis) and — in 1.0 — **Ancient Relics and Radiant Gems** for the new Awakening mechanic. (PRELIMINARY 1.0 for the relic/gem part)
- Expeditions cannot "fail"; underpowered teams simply bring back reduced rewards.

## 2. How to unlock

| Requirement | Value |
|---|---|
| Structure | **Pal Expedition Station** (Pal Management category) |
| Technology | **Level 22** *(corrected 2026-07-15 per paldb 1.0; wiki.gg's Level 15 is EA-era)*, costs **2 Technology Points** |
| Build materials | **Wood ×20, Stone ×20, Paldium Fragment ×5** (workload 10,000) |
| Limit | **1 station per base** (pre-1.0 guide) |
| Content gate | Each expedition unlocks by defeating a specific **tower faction leader** (Normal mode for regular expeditions, Hard mode for VeryHard expeditions) |

The station is one of the largest base structures; placement inside the base area doesn't affect outcomes. 4,000 HP; nothing can be built on top of it. (pre-1.0 guide)

## 3. How it works

- **Up to 100 Pals** can be sent on a single expedition. Selection is manual or **"auto assign"** (picks the highest-Firepower eligible Pals).
- Pals are drawn from the **Palbox**. While away they are **fully unavailable** — not usable in your party, at any base, or for condensation — until they return. Party/base Pals can't be selected. (pre-1.0 guide)
- **Firepower** is the core stat. Per Pal:

  `Firepower = (Attack + Defense + HP/5) × rank²`

  where *rank* is the Pal's **condensation star rank**: 0★ = ×1, 1★ = ×4, 2★ = ×9, 3★ = ×16, 4★ = ×25. (pre-1.0 guide)
- Each expedition lists a **minimum recommended Firepower**:
  - **Below** it → rewards are reduced.
  - **Above** it → reward **quantities increase**. (Since v0.6.4; before that, excess firepower shortened the duration instead.) (pre-1.0 guide)
- **Element requirements:** most expeditions require a set **number of Pals of a specific element** (e.g. "×20 Fire" = at least 20 Fire Pals in the group).
- **Durations:** 30 / 45 / 60 minutes for regular expeditions, **120 minutes** for VeryHard ones (PRELIMINARY 1.0 — pre-1.0 sources listed VeryHard at 60 min).
- **Pal Labor Research Laboratory** research (primarily the Mining tree) can increase expedition rewards / reduce duration. (pre-1.0 guide)
- No player-level or work-suitability requirements are documented — gating is tech level 22 (paldb 1.0), tower bosses, element counts, and Firepower.

## 4. Mission list (1.0)

Firepower = minimum recommended. "Element" = required count of Pals of that element. Full reward pools with quantities and per-slot drop chances are in `data/expeditions.json`; the Rewards column below is the highlights.

### Regular expeditions (unlock: tower boss on Normal)

| Expedition | Dur. | Firepower | Element | Unlock (Normal) | Headline rewards |
|---|---|---|---|---|---|
| Verdant Hollow | 30 min | 25K | — | Zoe & Grizzbolt (Rayne Syndicate) | Pal/Mega Spheres, Ore, Paldium, Small Pal Souls, Ancient Civ. Parts 1–2 |
| Secret Realm of the Forest | 30 min | 56K | 15× Grass | Lily & Lyleen (Free Pal Alliance) | Mega/Giga Spheres, Small/Med Souls, **Bellanoir Slab Frag.**, Anc. Civ. Parts 2–3 |
| Blazing Cavern | 45 min | 144K | 20× Fire | Axel & Orserk (Eternal Pyre) | Hyper Spheres, Sulfur, Med/Lg Souls, Bellanoir (Libero) Slab Frags, Anc. Civ. Parts 3–4 |
| Hidden Sanctum of the Desert | 45 min | 209K | 20× Ground | Marcus & Faleris (PIDF) | Hyper/Ultra Spheres, Coal, **Bellanoir Slab Frag. (guaranteed)**, Anc. Civ. Parts 4–5 |
| Astral Frost Cavern | 60 min | 286K | 20× Ice | Victor & Shadowbeak (PAL Genetic Research Unit) | Ultra/Legendary Spheres, Pure Quartz, Bellanoir Libero / Blazamut Ryu Slab Frags, first **Ancient Civ. Core** |
| Celestial Sakura Cavern | 60 min | 375K | 20× Water | Saya & Selyne (Moonflower Tower) | Legendary/Ultimate Spheres, Crude Oil, **Xenolord/Hartalis/Blazamut Ryu Slab Frags (33% each)**, Anc. Civ. Core 1–2 |
| Dark Cave of Feybreak | 60 min | 476K | 20× Dark | Bjorn & Bastigor (Feybreak Tower) | Ultimate/Exotic Spheres, **Chromite 30–50**, Giant Souls, Xenolord/Hartalis/Blazamut Ryu Slab Frags, Anc. Civ. Core 2–3 |
| Sunreach Isle (PRELIMINARY 1.0) | 60 min | 589K | 20× Dragon | Auri & Shaolong (Sunreach tower) | **Sol Spheres, Soralite, Coralum Ore**, Giant Souls, Xenolord/Hartalis/Blazamut Ryu Slab Frags, Anc. Civ. Core 3–4 |
| World Tree Subterrenean City Ruins (PRELIMINARY 1.0) | 60 min | 851K | — | World Tree boss (name spoiler-hidden in sources) | **Ancient Spheres, Paloxite, Ancient Relics (5 tiers), Radiant Gems (all 9 elements)**, Giant Souls 8–12, slab frags, Anc. Civ. Core 3–5 |

### VeryHard expeditions (unlock: tower boss on **Hard**; 120 min, Firepower 1.6M, 20 Pals of listed element) (PRELIMINARY 1.0 values)

Each guarantees a specific **Slab Fragment ×1–2** and a **Kinship Peach** per run, plus Ancient Pal Manuscripts ×25–30 and Sol/Ancient Spheres ×10–20.

| Expedition | Element | Unlock (Hard) | Guaranteed slab | Other notable rewards |
|---|---|---|---|---|
| Rayne Syndicate Smuggling Warehouse | 20× Neutral | Zoe & Grizzbolt | **Bellanoir** | Aquatic Pal Fluids, Leather, Ore, meats |
| Free Pal Alliance Illicit Trading Post | 20× Grass | Lily & Lyleen | **Bellanoir Libero** | Coal, Mushrooms, Kinship Peach ×1–3 |
| Eternal Pyre's Forbidden Market | 20× Fire | Axel & Orserk | **Xenolord** | Sulfur, Flame Organs, Leather |
| PIDF Illegal Factory | 20× Ground | Marcus & Faleris | **Blazamut Ryu** | Coal, Electric Organs, High Quality Pal Oil |
| PAL Genetic Research Laboratory | 20× Ice | Victor & Shadowbeak | **Xenolord** | Pure Quartz, Ice Organs, **Diamond ×6–12** |
| Moonflower's Secret Hideout | 20× Water | Saya & Selyne | **Blazamut Ryu** | Crude Oil, Large Souls ×7–11, Giant Souls ×5–10 |
| Ancient Feybreak Ruins | 20× Dark | Bjorn & Bastigor | **Hartalis** | Chromite, Hexolite Quartz, Venom Glands |
| Sunreach Dragon Husk | 20× Dragon | Auri & Shaolong | **Hartalis** | Soralite, Coralum Ore, Electric Organs |
| The World Tree's Forbidden Area | — (FP **2.1M**) | World Tree boss (Hard) | — | **Ancient Relics (Gorgeous/Glowing/Glistening ×2–4), Radiant Gems ×2–5 (all elements)**, Anc. Civ. Parts 9–11 / Cores 6–9, Dog Coins |

## 5. What affects rewards

- **Firepower vs. the minimum** is the only published reward lever: hitting it gives full listed rewards; exceeding it multiplies quantities; falling short reduces them. Duration is fixed per mission (since v0.6.4). (pre-1.0 guide)
- Firepower depends only on **Attack, Defense, HP and condensation rank** per the published formula — level and IVs matter insofar as they raise those stats. Passive skills/traits are **not documented** to affect expeditions.
- **Number of Pals** matters simply because group Firepower is the sum over up to 100 Pals.
- Reward pools are **weighted slots**, so slab fragments etc. are luck-based on regular expeditions (e.g. 33% per slot roll on Dark Cave of Feybreak) but **guaranteed** on VeryHard ones.
- **Pal Labor Research Laboratory** upgrades boost expedition yields. (pre-1.0 guide)

## 6. Strategy

- **Condense first.** The rank² term dominates: a 4★ Pal counts ×25, so one maxed Pal outweighs two dozen 0★ Pals. Condense your surplus catches into a core of starred "expedition mules."
- Keep **20+ Pals of each element** (Grass, Fire, Ground, Ice, Water, Dark, Dragon, Neutral) in the Palbox to satisfy element requirements — breeding/catching filler Pals of the right element is enough; then a few high-firepower carries of any element push the total over the minimum.
- Expedition Pals are locked out of base work — use **dedicated expedition rosters**, not your base workers.
- **Xenolord Slab Fragments:** farm **Eternal Pyre's Forbidden Market** or **PAL Genetic Research Laboratory** (guaranteed 1–2 per 2-hour run after the Hard-mode tower kill); before Hard towers, RNG rolls from Celestial Sakura Cavern / Dark Cave of Feybreak / Sunreach Isle. Four fragments assemble a summon slab. (pre-1.0 guide for the crafting part)
- **Awakening materials (1.0):** run the two World Tree expeditions for Ancient Relics and element Radiant Gems. (PRELIMINARY 1.0)
- Overshoot the Firepower minimum where you can — extra Firepower converts directly into larger reward stacks.

## 7. 1.0 changes vs the Feybreak-era feature

- Feature introduced in **v0.4.11** (post-Feybreak, Jan 2025); **v0.6.4** reworked excess Firepower to boost reward quantity instead of shortening duration and added hard-mode expeditions. (pre-1.0 guide)
- **1.0 additions** (PRELIMINARY 1.0):
  - Patch notes: expedition content **"extended into Sunreach and the World Tree"** — 4 new missions: Sunreach Isle, World Tree Subterrenean City Ruins, Sunreach Dragon Husk, The World Tree's Forbidden Area (18 total, up from 14).
  - New 1.0 reward items in expedition pools: **Sol/Ancient Spheres, Soralite, Coralum Ore, Paloxite, Ancient Relics, Radiant Gems, Kinship Peach, Hexolite Quartz**.
  - Apparent **rebalance of VeryHard expeditions**: pre-1.0 wiki listed them at 60 min / 500K Firepower; current 1.0 data shows **120 min / 1.6M** (2.1M for World Tree's Forbidden Area).

## 8. Known gaps / unverified

- World Tree expedition unlock boss name is spoiler-hidden ("？？？") in sources; Subterrenean City Ruins presumably needs the World Tree boss on Normal — unconfirmed.
- Palpedia lists Auri & Shaolong's tower as "PIDF Tower" — likely a source labeling quirk; the actual Sunreach tower name is unverified.
- Exact reward-quantity scaling curve vs. excess Firepower is unpublished.
- Sunreach Isle's parsed reward table lacks a slot-3 entry (possibly a missing sphere row on the source page).

---

## Sources

- https://www.palpedia.net/expeditions — full 1.0 mission list: durations, difficulty, firepower, element multipliers, unlock bosses, complete reward pools (fetched 2026-07-14, site banner "1.0 Launch – v1.0.0")
- https://palworld.wiki.gg/wiki/Expeditions — mechanics: 100-Pal cap, firepower formula, element requirements, v0.4.11/v0.6.4 history, research-lab bonuses; pre-1.0 mission table used for the 1.0-rebalance comparison
- https://palworld.wiki.gg/wiki/Pal_Expedition_Station — station tech level/cost, build materials, workload, HP
- https://xgamingserver.com/blog/palworld-1-0-patch-notes/ — 1.0 patch notes ("expedition/fishing content extended into Sunreach and the World Tree", update 1.100.427)
- https://game8.co/games/Palworld/archives/492119 — unlock flow, one-station-per-base (via search snippets)
- https://www.4netplayers.com/en/blog/palworld/palworld-expeditions-best-pals-rewards/ — general expedition overview (search corroboration)
