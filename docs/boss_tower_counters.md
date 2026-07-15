# Palworld 1.0 — Tower Bosses & Boss Counters

Knowledge-base note. Game version: **Palworld 1.0** (released 10 July 2026). Compiled 14 Jul 2026.
Sources: game8.co/games/Palworld, nexttier.pro, thepalprofessor.com, palworld.fandom.com, allthings.how.

Tags used below:
- **(pre-1.0 guide)** = data from the Early-Access 7-tower / 10-minute-timer era; still broadly accurate for the original 7 towers but not re-verified for 1.0.
- **(PRELIMINARY 1.0)** = 1.0-specific info that is new/thin and may change.

---

## 1. Element (Type) Affinity Chart

Palworld has **9 elements**: Neutral, Fire, Water, Grass, Electric, Ice, Ground, Dark, Dragon.
Each element deals **bonus damage to exactly one element** and **takes bonus damage from exactly one element** (Fire is the exception on defense). Attacking with a super-effective element also means your Pal *resists* that target's attacks. There are no "double weak" defensive types like Pokémon — it's a clean 1-to-1 rock-paper-scissors loop plus a Neutral/Dark/Dragon/Ice sub-loop.

| Element  | Strong vs (deals bonus dmg to) | Weak to (takes bonus dmg from) |
| -------- | ------------------------------ | ------------------------------ |
| Neutral  | — (no offensive advantage)     | Dark                           |
| Fire     | Grass, **Ice**                 | Water                          |
| Water    | Fire                           | Electric                       |
| Electric | Water                          | Ground                         |
| Ground   | Electric                       | Grass                          |
| Grass    | Ground                         | Fire                           |
| Ice      | Dragon                         | Fire                           |
| Dark     | Neutral                        | Dragon                         |
| Dragon   | Dark                           | Ice                            |

**The two loops to memorize:**
- Main loop: **Fire → Grass → Ground → Electric → Water → Fire**
- Second loop: **Dark → Neutral** (Neutral has no counter of its own except Dark), and **Dragon → Dark**, **Ice → Dragon**, **Fire → Ice** (Fire double-dips into Ice).

Practical takeaways:
- **Neutral** Pals/bosses have no elemental weakness other than being hit hard by **Dark**. A truly *typeless* boss (see World Tree final boss) has NO exploitable weakness at all.
- **Dragon** is the go-to counter for **Dark** bosses (Shadowbeak, Selyne).
- **Ice** counters **Dragon**; **Fire** counters both **Grass** and **Ice**.

---

## 2. Tower Bosses — 1.0 Roster (9 total)

1.0 has **9 Tower Bosses**: 8 faction towers across Palpagos + Sakurajima + Sky Islands, plus the World Tree final boss. Each tower is a faction leader riding a signature Pal.

**1.0 changes vs Early Access:**
- Fight **timer cut from 10 min → 5 min**; boss HP/stats rebalanced to match. Bringing the correct counter element + real damage now matters much more (you can't stall-and-poke to a win).
- Arenas are now region-themed instead of copy-paste rooms; bosses shift tactics mid-fight.
- **Co-op:** up to 4 players — all queue at the door before anyone interacts.
- **1.0 post-fight quest can let you RECRUIT the boss Pal** you just beat (Grizzbolt, Lyleen, Orserk, Faleris, Shadowbeak, etc.). Most of these are also breedable.
- Two brand-new bosses added: **Auri & Shaolong** (Sunreach) and the final **Zanara/Zenara & Astralym** (World Tree).

### Master table

Notes on "Level": sources disagree slightly. **Boss-Pal level** is the actual in-game level of the ridden Pal (from game8 / thepalprofessor). **Rec. player level** is the faction/progression tier nexttier lists for when you should attempt it.

| # | Boss (Pal)              | Tower / Faction                    | Boss-Pal Lv | Rec. player Lv | Pal Element        | Counter element(s) |
| - | ----------------------- | ---------------------------------- | ----------- | -------------- | ------------------ | ------------------ |
| 1 | Zoe & **Grizzbolt**     | Rayne Syndicate                    | 10          | 10             | Electric           | **Ground**         |
| 2 | Lily & **Lyleen**       | Free Pal Alliance                  | 20–25       | 20             | Grass              | **Fire**           |
| 3 | Axel & **Orserk**       | Brothers of the Eternal Pyre       | 30–40       | 30             | Electric / Dragon  | **Ice** or **Ground** |
| 4 | Marcus & **Faleris**    | PIDF                               | 40–45       | 40             | Fire               | **Water**          |
| 5 | Victor & **Shadowbeak** | PAL Genetic Research Unit          | 50          | 50             | Dark               | **Dragon**         |
| 6 | Saya & **Selyne**       | Moonflower (Sakurajima)            | 55          | 55             | Dark               | **Dragon**         |
| 7 | Bjorn & **Bastigor**    | Feybreak                           | 58–60       | 60             | Ice                | **Fire**           |
| 8 | Auri & **Shaolong**     | Azure Covenant (Sunreach, Sky Is.) | 68          | 68             | Water / Dragon     | **Electric**, **Ice** *(PRELIMINARY 1.0)* |
| 9 | Zanara & **Astralym**   | World Tree (FINAL)                 | 80 (cap)    | 80             | **Neutral / typeless** | **None** *(PRELIMINARY 1.0)* |

Progression note: towers can be fought in almost any order, but **Auri (Sunreach)** requires beating **Bjorn (Feybreak)** first to open Sunreach, and **Zanara/Astralym (World Tree)** requires completing the **Sealed Calamity** questline after the 8 faction towers. Clearing all 8 faction towers opens the road to the World Tree finale.

**Rewards per tower:** one-time Ancient Technology Points (typically 5) + permanent fast-travel point + tech unlocks; Hard Mode adds a cosmetic hat / Training Crystals. **Tower Boss Pals themselves are NOT catchable during the fight in the normal way** — you recruit them via the 1.0 post-fight quest or breed them (see §5 on the old wanted-level catch trick).

---

## 3. Per-Boss Counters & Tactics

### 1. Zoe & Grizzbolt — Rayne Syndicate (Electric, Lv 10)
- **Counter: Ground.** Gumoss, Rushoar/Rushroar, Fuddler, Direhowl (Bog Blast + Fierce Fang), Foxparks (partner skill). A Lv 10 Direhowl can solo it.
- Smallest HP pool of any tower boss. Dodge **Lightning Claw** behind pillars / tank with shield. You out-level Zoe fast — easy to come back stronger.

### 2. Lily & Lyleen — Free Pal Alliance (Grass, Lv 20–25)
- **Counter: Fire.** Foxparks (flamethrower partner skill), Wixen, Incineram, Vanwyrm.
- **Lyleen heals** — you must out-DPS the regen; open with Fire + stack burn (note: burn/poison are heavily reduced vs tower bosses, ~1.5% total). Watch **Poison Fog**; grapple to break Root.

### 3. Axel & Orserk — Brothers of the Eternal Pyre (Electric/Dragon, Lv 30–40)
- **Counter: Ice OR Ground** (double weakness). Anubis, Warsect, Vanwyrm Cryst (Ice flyer), Wumpo, Gorirat Terra; keep a Dumud in party to buff Ground Pals.
- Volcano biome — **wear heat-resistant armor**. Orserk is a glass cannon; stay out of melee and punish after big casts (Kerauno, Dragon Cannon hit hard).

### 4. Marcus & Faleris — PIDF (Fire, Lv 40–45)
- **Counter: Water.** Jormuntide, Azurobe; a Gobfin in party boosts your damage. Faleris is very weak to **Holy Burst, Wall Splash, Hydro Slicer** (Yakumo, Lullu, Celesdir learn Holy Burst; many water Pals learn Hydro Slicer).
- Desert biome — **heat-resistant armor**. Faleris flies + stuns; keep the recall button ready. **Phoenix Flare** can redirect at you if you recall too early.

### 5. Victor & Shadowbeak — PAL Genetic Research Unit (Dark, Lv 50)
- **Counter: Dragon.** Jetragon (ideal), bred Jormuntide, Astegon, Xenogard, Silvegis; or Ice/Dark Pals carrying Dragon attacks (Shadowbeak itself, Chillet, Vanwyrm Cryst). Shadowbeak has a **huge hitbox** → weak to Beam Slicer / Blast Cannon / Holy Burst.
- Snowy peak — **cold-resistant armor**. Watch **Divine Disaster** (dodge behind pillars) and **Blizzard Spike** (jump). Boss uses many Ice attacks to punish Dragon Pals — pair with a Rocket Launcher for burst.

### 6. Saya & Selyne — Moonflower / Sakurajima (Dark, Lv 55)
- **Counter: Dragon** (same team as Shadowbeak carries over — often clear both back-to-back). Selyne hits hard with **Holy Blast / Moonlight Beam / Starlight Beam**.
- Run counter-clockwise; dodge Starlight Beam with a right roll. Very high attack (2009) but lower HP/DEF than Bjorn. Don't let your Pal get close (close-range Air Blade / Holy Burst can one-shot).

### 7. Bjorn & Bastigor — Feybreak (Ice, Lv 58–60)
- **Counter: Fire.** Wixen (grass attacks are fastest but not easiest), Ragnahawk, Knocklem, Shadowbeak, Bellanoir Libero, or another Bastigor. A **damage-amp passive (Legend)** on your carry ends it fast.
- **Warning:** Bjorn uses lots of **Water** attacks to punish Fire Pals — Faleris/Jormuntide Ignis are bad picks here. Grapple + Triple Jump Boots make dodging **Glacial Impact / Rockburst / Diamond Rain** much easier. Highest-HP normal tower boss.

### 8. Auri & Shaolong — Azure Covenant / Sunreach Sky Island (Water/Dragon, Lv 68) *(PRELIMINARY 1.0)*
- **Counter: Electric + Ice** (bring both for coverage vs the dual typing). Punish with ranged burst.
- Gated behind a short prep quest: fly around Sunreach and **disable 6 defense modules** to open the whirlwind housing Auri. Requires beating Bjorn/Feybreak first.

### 9. Zanara / Zenara & Astralym — World Tree, FINAL BOSS (Neutral / typeless, Lv 80) *(PRELIMINARY 1.0)*
- **No elemental weakness** — completely typeless. Pure gear-and-skill check: bring strongest **Awakened** Pals, top-tier weapons (Rocket/endgame guns), full endgame armor, learn to dodge everything.
- Reported HP **~420,000**; six-winged dragon Astralym. Has an **immune/immune-phase** and a **wing-charge** attack; at low HP expect adds/clone-style pressure. Unlocked by completing the **Sealed Calamity** questline after all 8 faction towers.
- **Astralym is NOT catchable** — only registered as a Paldeck "encountered" entry; boss-exclusive, appears nowhere else. Reward: story completion, Character + Pal EXP, and **5 Ancient Technology Points**.

---

## 4. Boss HP / Stats & Scaling

**Important:** the detailed HP table below is **(pre-1.0 guide)** data (Early-Access 7-tower, 10-minute-timer build). 1.0 rebalanced HP downward to fit the new 5-minute timer, so treat these as *ballpark / relative scaling* rather than exact 1.0 values. Key stats:
- **HP** = raw health (with heal bonus & damage reduction baked in).
- **EHP** = effective HP (HP × defense multiplier) — the real "how tanky it feels" number. Tower bosses have large built-in damage reduction, so EHP dwarfs raw HP.

### Normal Mode (pre-1.0 guide)
| Boss                | Lv | Attack | Def | HP        | EHP           | Kill XP |
| ------------------- | -- | ------ | --- | --------- | ------------- | ------- |
| Zoe & Grizzbolt     | 10 | 175    | 125 | 30,550    | 3,818,750     | 1,170   |
| Lily & Lyleen       | 25 | 306    | 246 | 69,375    | 17,066,250    | 9,570   |
| Axel & Orserk       | 40 | 490    | 350 | 72,900    | 25,515,000    | 63,990  |
| Marcus & Faleris    | 45 | 505    | 421 | 86,275    | 36,321,775    | 120,570 |
| Victor & Shadowbeak | 50 | 850    | 575 | 105,000   | 60,375,000    | 227,910 |
| Saya & Selyne       | 55 | 2,009  | 503 | 522,000   | 262,566,000   | 432,390 |
| Bjorn & Bastigor    | 58 | 2,740  | 590 | 1,050,000 | 619,500,000   | 821,490 |

### Hard Mode (pre-1.0 guide)
Unlocked after beating the first 6 towers. Adds boss level, huge attack/HP boosts, extra add-spawns, and new attack elements. Rewards Training Crystals, a cosmetic hat, sometimes Lotus flowers (Stat Elixirs). In 1.0 the Hard-Mode reward is **cosmetic** — most players save it for after endgame gear.

| Boss                | Lv | Attack | Def | HP        | EHP           |
| ------------------- | -- | ------ | --- | --------- | ------------- |
| Zoe & Grizzbolt     | 55 | 2,816  | 462 | 610,333   | 281,974,000   |
| Lily & Lyleen       | 55 | 2,489  | 483 | 690,909   | 333,709,091   |
| Axel & Orserk       | 55 | 3,180  | 462 | 587,500   | 271,425,000   |
| Marcus & Faleris    | 55 | 2,665  | 503 | 542,308   | 272,780,769   |
| Victor & Shadowbeak | 55 | 2,678  | 627 | 815,000   | 511,005,000   |
| Saya & Selyne       | 55 | 3,157  | 503 | 1,044,000 | 525,132,000   |
| Bjorn & Bastigor    | 60 | 6,850  | 590 | 2,333,333 | 1,376,666,667 |

**Hard-Mode add mechanics (pre-1.0 guide):**
- Grizzbolt: spawns a Lv 55 Syndicate Crusher add (stun it with a Rocket Launcher); Zoe also gains Grass attacks to punish Ground Pals.
- Lyleen: humans with an electric crossbow at start; Lily shifts to more Water than Grass (Fire less reliable).
- Faleris: only uses Fire + Electric in Hard Mode → equip Fire +2 and Electric +2 resistance rings.
- Shadowbeak: spawns a **clone** at low HP (ignore it, focus real Victor).
- Selyne: spawns **two basic Selynes** when Saya gets low.
- Bastigor: massive attack boost turns most attacks into one-shots — dodge, don't tank.

**1.0 final boss HP:** Zanara/Astralym ~**420,000 HP** (typeless) *(PRELIMINARY 1.0)*.

---

## 5. General Combat Tactics vs Bosses

- **Type advantage is king.** A counter-element Pal both deals bonus damage AND resists the boss's matching attacks. With the 5-minute 1.0 timer, an off-element team can literally time out.
- **Player weapon damage vs Pal skill damage** are two different scaling paths:
  - **Player-attack builds:** an element-swap carry Pal (Anubis / Ragnahawk / Chillet) + up to **4 Gobfins** (each Gobfin partner-skill stacks a big player-damage buff). Currently the highest-DPS approach; downside is the boss focuses *you*, so you must dodge. Add **Felbat/Lovander** partner skill for lifesteal → near-invincible.
  - **Pal-attack builds:** 2–5 **Knocklem** (Musclehead/Demon God/Legend) do the fighting for you via partner-skill Rockburst; 2 Knocklems = 100% uptime. Requires ~zero player aim and rarely draws boss aggro to the player.
- **Aggro:** boss targets whoever deals the most damage. **Sending out a Pal or using a Partner Skill resets aggro to the Pal.** Use this to peel the boss off yourself.
- **Recall/withdraw-dodge:** recall a Pal *just before* a big hit to save it and dodge (be careful — recalling too early can redirect some attacks, e.g. Faleris Phoenix Flare, at you).
- **Burn & Poison are ~useless on tower bosses** (reduced to ~1.5% of normal over full duration). Rely on direct-hit skills.
- **Best boss-killer active skills** (universal): Rockburst, Beam Slicer, Blast Cannon, Air Blade, Holy Burst, Hydro Slicer, Sand Tornado, Diamond Rain. Big-hitbox bosses (Shadowbeak, Selyne) take extra from AoE beams.
- **Armor to the biome, not the boss:** heat-resist for volcano (Orserk) & desert (Faleris); cold-resist for snow (Shadowbeak); +2 element **Resistance Rings** for Hard Mode.
- **Fast travel first:** unlock the tower's teleport on approach so a wipe respawns you at the door.
- **Pal Spheres / sphere-throwing:** you **cannot throw spheres to catch tower bosses** in the normal fight. Spheres are for wild Pals, alpha field bosses, and dungeon bosses (below).
  - **(pre-1.0 guide) wanted-level catch trick:** get a wanted level, let PIDF guards chase and damage the tower boss mid-fight, then you could catch it — caught tower-boss Pals kept their inflated boss HP (very tanky). In 1.0 the intended path is the **post-fight recruit quest** instead.

---

## 6. Alpha / Field Bosses & Dungeon Bosses

### Alpha (Field) Bosses
- **Scaled-up wild Pals** at fixed map spots: same species/moveset as the normal spawn but a fixed level boost, bigger HP bar, and larger loot drops. Marked on the map.
- **Catchable** — throwing spheres at a weakened alpha is one of the best ways to get a strong Pal ahead of the curve. Use the same **element counters** as the normal species.
- **Legendary alphas:** Paladius, Necromus, Frostallion, and Jetragon appear as **Level 50 Alpha Field Bosses** in fixed locations (catchable).
- **1.0 change:** Pocketpair relocated many alpha spawns so tougher ones sit deeper in mid/late game, matching each region's difficulty.

### Dungeon Bosses
- Every dungeon ends with an **Alpha Boss Pal**. **Catchable** like any Pal, and you can **reroll which Pal you fight** at the end of a dungeon. Dungeons also give guaranteed chests, Skill Fruits, schematics. High-level Feybreak dungeons drop **Xenolord Slab Fragments**.

### Predator Pals
- A **Predator** is a unique named "Rampaging" encounter (distinct from a plain alpha) that drops **Predator Cores** and **Giant Pal Souls** on top of normal species loot. Tougher, endgame-oriented.

---

## 7. Endgame Raid Bosses (NEW / expanded in 1.0)

Raid bosses are summoned by placing a crafted **Slab** in a **Summoning Altar**. They **cannot be caught** — instead they drop an **egg of themselves** + IV Fruits + endgame rewards on defeat (so you can still obtain the Pal). *(Some detail PRELIMINARY 1.0.)*

Roster (~6 bosses / ~11 encounters counting Ultra & Master variants):
- **Bellanoir** and its **Bellanoir Libero** form (Dark) — the catch-via-egg legendaries.
- **Blazamut Ryu** (Fire/Dragon-ish; top-tier S-tier Pal).
- **Xenolord** — Level 60 raid boss, **Dragon/Dark**, weak to **Ice** and **Dragon** damage; ~**1,316,000 HP**. Slab Fragments from high-level (Feybreak) dungeons / Pal expeditions.
- **Moon Lord** — Terraria crossover raid boss.
- **Hartalis** — additional 1.0 raid boss. *(PRELIMINARY 1.0)*

### World Tree "raid"/finale
- The **World Tree (Sealed Calamity)** finale is the story climax, culminating in the **Zanara/Zenara & Astralym** Lv 80 typeless fight (see §3 #9). Astralym is **not catchable** (registered only). This is the current pinnacle PvE encounter; catchable 1.0 legendaries come from the **raid bosses** (Xenolord, Bellanoir Libero) rather than the World Tree. *(PRELIMINARY 1.0 — endgame raid/World Tree data still thin and evolving.)*

---

## Source discrepancies to be aware of
- **Boss levels differ by source:** game8/thepalprofessor list the *ridden Pal's* level (Lyleen 25, Orserk 40, Faleris 45, Bastigor 58); nexttier lists cleaner *progression tiers* (20/30/40/60). Table §2 shows both.
- **Final boss name** appears as both **"Zanara"** and **"Zenara"** across sources; same boss (with Astralym).
- **HP tables (§4)** are pre-1.0; 1.0's 5-min timer came with an HP rebalance, so exact 1.0 tower HP values are not yet fully re-documented.
