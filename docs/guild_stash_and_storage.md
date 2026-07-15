# Palworld — Guild, Shared Storage & Cross-Base Storage

Knowledge-base note. Game: Palworld 1.0 (released 10 July 2026, update 1.100.427).
Most storage/guild mechanics below carried over from the pre-1.0 "Feybreak" update and are believed unchanged in 1.0. Items marked **(pre-1.0 guide)** were documented before 1.0 and not yet re-verified against the 1.0 build; **(PRELIMINARY 1.0)** are 1.0-specific claims still being confirmed.

---

## 1. What a Guild is

- A **Guild** is the cooperative unit that ties players together and owns the shared bases, Palboxes, stored resources, and captured Pals.
- Every player is **automatically placed in an "Unnamed Guild"** on starting a game. In singleplayer you are a one-person guild.
- In multiplayer, a Guild forms when other players join. Approach another player to get the invite / request-to-join prompt.
- **Member limit:** default **20**, configurable **1–100** in World Settings.
- **Base limit (Palbox limit):** a Guild can have a maximum of **3 bases / 3 Palboxes total**, shared across all members regardless of member count. Dedicated-server admins can raise this via World Settings / `WorldOption.sav` (up to `BaseCampMaxNum`), but **3 is the default cap**. (pre-1.0 guide)
- **Ownership is guild-wide:** structures, chests, and Pals belong to the Guild, so guildmates can access and use each other's storage at a shared base.

---

## 2. CRITICAL: Is storage shared between bases?

**Short answer: NO — regular chests are NOT shared between bases.**

- Every base's chests are **local to that base**. Items in a Wooden/Metal/Refined Metal Chest at Base A **cannot** be accessed from Base B. There is no global "stash" that mirrors ordinary chests across bases. (pre-1.0 guide, still true in 1.0)
- What DOES travel with you between bases:
  - **Your player inventory** (what you personally carry).
  - **Pals in your party** and the **Palbox** roster (Pals are stored in the Palbox system, accessible from any of your Palboxes).
  - **NOT** the contents of base chests.
- **Guildmates** at the *same* base DO share that base's chest contents (guild-owned storage). This is "shared between players," not "shared between bases."

### The ONE exception that IS shared across bases: the Guild Chest

- The **Guild Chest** is a special late-game storage structure whose contents are **shared across every base where a Guild Chest is placed** ("instantly send and receive items through subspace").
- To use it as cross-base storage you must **build a Guild Chest in at least two bases**; items dropped in one appear in the other. **Limit: one Guild Chest per base.** (pre-1.0 guide)
- This is the only legitimate in-game shared-stash mechanic. Do not assume any other chest behaves this way.

---

## 3. Guild Chest details

| Property | Value |
|---|---|
| Unlock | Technology menu, **Level 41**, costs **4 Ancient Technology Points** |
| Craft cost | Paldium Fragment ×100, Ancient Civilization Parts ×10, Refined Ingot ×50 |
| Slots | **54 shared slots** (shared pool across all Guild Chests you place) |
| Cross-base | Contents shared across all bases that have a Guild Chest |
| Per base | Max **1** Guild Chest per base |
| Access | **Players only** — Pals cannot deposit/withdraw from it (unlike normal chests) |
| Food | Food inside has its **spoilage/depletion timer frozen** — good emergency food store |
| Settings | "Chest Settings" lets you restrict which items may be stored |

Notes:
- Because Pals can't stock a Guild Chest, it does **not** auto-fill from production lines; you move items into it manually.
- Origin: added in the pre-1.0 Feybreak update; present in 1.0. (pre-1.0 guide)

### Related: Item Retrieval Machine (single-base convenience, NOT cross-base)

- Unlocks at **Level 49**. **Not a container** — has no slots of its own.
- Lets you **pull items from every chest at that base** through one interface (saves walking to each chest). Works only within the base it's placed in; it does **not** link bases. (pre-1.0 guide)

---

## 4. How items actually move between bases

Because normal chests are local, moving goods between bases is manual:

1. **Carry them yourself** — load your player inventory (watch weight/carry capacity) and fast-travel or ride to the other base. Primary method.
2. **Guild Chest relay** — deposit at Base A's Guild Chest, withdraw at Base B's Guild Chest. Cleanest option once unlocked (Lv41).
3. **Pals do NOT auto-transport between bases.** Transport-suitability Pals only move items *within* a base (e.g., from crafting output to nearby chests). They never ferry goods base-to-base.
4. **Palbox / fast travel:** teleporting moves you and your held inventory, not base chest contents.

Practical tip: before Guild Chest is unlocked, designate one "main" base for stockpiling and periodically haul surplus there in inventory loads.

---

## 5. Organizing storage across multiple bases

- **Specialize bases:** e.g., Base 1 = ore/smelting hub, Base 2 = ranch/food, Base 3 = breeding. Store each base's outputs locally where they're produced.
- **Name your chests** to sort by category — chests can be **renamed** and storage controls were made easier to manage in 1.0. (PRELIMINARY 1.0)
- **Place chests next to production** so transport Pals auto-deposit outputs; keep a chest near the Palbox/entrance for player pickup.
- **Use the Item Retrieval Machine** at your main base to grab from all local chests at once.
- **Reserve the Guild Chest** for the handful of items you genuinely need at multiple bases (see below), since it's a limited shared 54-slot pool.
- **Refrigerator / Cooler Box** freeze/slow food spoilage — store perishables (cake ingredients, berries, cooked dishes) there, or in the Guild Chest for frozen timers.

### What to keep in commonly-accessed / shared storage

Good candidates for the Guild Chest or a main-base "grab-and-go" chest:
- **Paldium Fragments** — sphere crafting, base structures, Guild Chest itself.
- **Pal Spheres / higher spheres** — always want capture tools on hand.
- **Ore and Ingots** (base metal, refined ingot) — needed for crafting at any base.
- **Seeds** — for replanting plantations at any farming base.
- **Cake ingredients** (Flour, Milk, Egg, Honey, Red Berries) — for breeding cake; keep together, ideally chilled.
- **Ancient Civilization Parts / Ancient Tech materials** — for high-tier crafts and the Guild Chest recipe.

---

## 6. Chest tiers & capacity (single-base storage)

| Structure | Unlock (Lv) | Slots | Notes |
|---|---|---|---|
| Wooden Chest | 2 | **10** | Basic; Pals auto-transport into it |
| Wooden Box / Wooden Shelf | — | 10 | Furniture-style storage |
| Wooden Barrel | — | 8 | |
| Wooden Barrel Shelf | — | 15 | |
| Metal Chest | 13 | **24** | Pals auto-transport |
| Refrigerator | 38 | **25** | Food vault; assign an **Ice Pal** to prevent spoiling |
| Refined Metal Chest | 39 | **40** | Largest normal chest; Pals auto-transport |
| Guild Chest | 41 (4 Ancient pts) | **54 (shared)** | Cross-base shared; players only |
| Item Retrieval Machine | 49 | 0 (access tool) | Access all chests in one base |

(Slot counts and unlock levels: pre-1.0 guide data, believed current in 1.0.)

- Cooler Boxes and Refrigerators also slow/prevent food spoilage.
- Chests can be **password-protected** in multiplayer to restrict access.

---

## 7. Quick answers

- **Is there a shared guild storage?** Yes — the **Guild Chest** (54 shared slots, Lv41). It's the only structure whose contents are shared across bases and among guildmates.
- **Do normal chests share between bases?** **No.** Each base's chests are independent and local.
- **Do Pals move items between bases?** **No** — only within a single base.
- **How do most items travel between bases?** The **player carries them** (or via Guild Chest once unlocked).

---

## Sources
- Game8 — How to Get Guild Chest: https://game8.co/games/Palworld/archives/492223
- Game8 — List of All Storage (slot counts): https://game8.co/games/Palworld/archives/440876
- Game8 — How to Create and Join a Guild: https://game8.co/games/Palworld/archives/441166
- Palworld Wiki (Fandom) — Guild Chest: https://palworld.fandom.com/wiki/Guild_Chest
- Palworld Wiki (Fandom) — Storage: https://palworld.fandom.com/wiki/Storage
- Palworld Wiki (Fandom) — Guilds: https://palworld.fandom.com/wiki/Guilds
- TheGamer — How To Use Guild Chests: https://www.thegamer.com/palworld-guild-chest-crafting-recipe/
- allthings.how — Item Retrieval Machine: https://allthings.how/palworld-item-retrieval-machine-how-to-get-and-use-it/
- Palworld 1.0 patch notes (playday.one): https://playday.one/2026/07/10/palworld-1-0-is-now-live-full-patch-notes/
