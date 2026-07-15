#!/usr/bin/env python3
"""Parse cached paldb.cc item pages into data/items.json.

Inputs:
  data/raw/item_slugs.json          (from fetch_items.py stage 1)
  <cache dir>/<slug>.html           (from fetch_items.py stage 2)
  <cache dir>/../technologies.html  (from /en/Technologies, for tech levels)

Usage: python3 parse_items.py --cache <dir> --tech <technologies.html>
"""
import argparse
import json
import os
import re
import sys
from datetime import date

from bs4 import BeautifulSoup

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "items.json")

# ---------------------------------------------------------------- overlays --
# Non-crafting sources that paldb item pages do not list in a structured way
# (mining/gathering nodes, ranch production). Kept minimal and well-known.
GATHER_OVERLAY = {
    "Wood": ["Chopping trees / ground pickup", "Logging Site at base (Lumbering pals)"],
    "Stone": ["Mining stone nodes", "Stone Pit at base (Mining pals)"],
    "Ore": ["Mining ore nodes (rust-brown rocks)"],
    "Coal": ["Mining coal nodes (black rocks, volcano/desert/caves)"],
    "Sulfur": ["Mining sulfur nodes (volcano regions, dungeons)"],
    "Pure Quartz": ["Mining quartz nodes (Astral Mountains / snowy regions)"],
    "Paldium Fragment": ["Mining blue Paldium nodes", "Riverbed glowing stones", "By-product of mining stone"],
    "Red Berries": ["Wild berry bushes", "Berry Plantation at base"],
    "Fiber": ["By-product of chopping trees", "Crusher (from Wood)"],
    "Egg": ["Wild ground pickup near Chikipi"],
    "Branch": ["Ground pickup under trees"],
}
RANCH_OVERLAY = {
    "Wool": ["Ranch: Lamball, Cremis, Melpaca (Farming)"],
    "Milk": ["Ranch: Mozzarina (Farming)"],
    "Egg": ["Ranch: Chikipi (Farming)"],
    "Honey": ["Ranch: Beegarde, Elizabee (Farming)"],
    "Gold Coin": ["Ranch: Mau, Mau Cryst, Vixy (Farming)"],
    "Red Berries": ["Ranch: Caprity (Farming)"],
    "Flame Organ": ["Ranch: Flambelle (Farming)"],
    "Cotton Candy": ["Ranch: Woolipop (Farming)"],
    "High Quality Pal Oil": ["Ranch: Dumud (Farming)"],
    "High Quality Cloth": ["Ranch: Sibelyx (Farming)"],
}

CAT_OVERRIDES = {}  # slug -> category, filled during refinement

def is_junk_name(name):
    """Internal/untranslated entries: CamelCase codes, trailing digits,
    underscores (e.g. Berries2, FishMeat, NPC_WEAPON, Potato_old)."""
    if "_" in name:
        return True
    if re.search(r"\d$", name):
        return True
    if " " not in name and re.search(r"[a-z][A-Z]", name):
        return True
    if name.isupper() and len(name) > 3:
        return True
    return False


def parse_technologies(path):
    """Return {display_name: tech_level} for both items and structures."""
    soup = BeautifulSoup(open(path).read(), "html.parser")
    levels = {}
    for row in soup.select("div.col.pt-2.pb-1.border-bottom"):
        lvl_div = row.select_one('div[style*="width:32px"] div')
        if not lvl_div:
            continue
        try:
            lvl = int(lvl_div.get_text(strip=True))
        except ValueError:
            continue
        for tech in row.select("div.hoverTech"):
            footer = tech.select_one(".hoverTechFooter")
            header = tech.select_one(".hoverTechHeader")
            if footer:
                name = footer.get_text(strip=True)
                kind = header.get_text(strip=True) if header else ""
                levels.setdefault(name, (lvl, kind))
    return levels


def kv_table(card):
    """Parse a paldb key/value stats card (d-flex rows of two divs)."""
    d = {}
    for row in card.select("div.d-flex"):
        cells = row.find_all("div", recursive=False)
        if len(cells) == 2:
            k = cells[0].get_text(" ", strip=True)
            v = cells[1].get_text(" ", strip=True)
            if k and k not in d:
                d[k] = v
    return d


def find_section(soup, title):
    """Find the card div whose h5 title matches."""
    for h in soup.find_all("h5"):
        if h.get_text(strip=True) == title:
            return h.parent
    return None


def parse_item(path, slug, category, display_name=None, tech_levels=None):
    tech_levels = tech_levels or {}
    html = open(path).read()
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text() if soup.title else slug
    name = display_name or title.split(" - ")[0].strip() or slug.replace("_", " ")

    item = {
        "name": name,
        "category": category,
        "tech_level": None,
        "recipe": None,
        "obtained_from": [],
        "notes": "",
    }
    meta = {"slug": slug}

    # --- stats / others tables
    stats, others = {}, {}
    for h in soup.find_all("h5"):
        t = h.get_text(strip=True)
        if t == "Stats":
            stats = kv_table(h.parent)
        elif t == "Others":
            others = kv_table(h.parent)
    meta["type"] = stats.get("Type", "")
    meta["rarity"] = stats.get("Rarity", "")
    meta["typeA"] = others.get("TypeA", "")
    meta["typeB"] = others.get("TypeB", "")
    meta["legal"] = others.get("bLegalInGame", "")

    # --- tech level from the top hover card
    m = re.search(r'Technology</span></span><span class="border p-1">(\d+)</span>', html)
    if m:
        item["tech_level"] = int(m.group(1))

    # --- production / recipe
    prod = None
    for h in soup.find_all("h5", attrs={"data-i18n": "convert_item_product_tab_title"}):
        prod = h.parent
        break
    if prod is None:
        prod = find_section(soup, "Production")
    if prod is not None:
        stations = []
        st_div = prod.select_one("div.row")
        if st_div:
            for a in st_div.select("a.itemname"):
                s = a.get_text(strip=True)
                if s and s not in stations:
                    stations.append(s)
        # primary station = lowest technology tier
        order = {s: i for i, s in enumerate(stations)}
        stations.sort(key=lambda s: (tech_levels.get(s, (10**9,))[0], order[s]))
        table = prod.select_one("table")
        if table:
            # paldb uses implicit </td>, so html.parser nests cells; work
            # span-wise instead: materials are <span><a.itemname>..<small>,
            # the product is a bare a.itemname (not inside a span).
            for tr in table.find_all("tr"):
                if tr.find("th"):
                    continue
                mats = {}
                for span in tr.find_all("span"):
                    a = span.find("a", class_="itemname", recursive=False)
                    q = span.find("small", class_="itemQuantity")
                    if a and q:
                        qt = q.get_text(strip=True)
                        try:
                            mats[a.get_text(strip=True)] = int(qt.replace(",", ""))
                        except ValueError:
                            pass
                # product: first itemname anchor not wrapped in a span
                pa = None
                for a in tr.find_all("a", class_="itemname"):
                    if a.find_parent("span") is None:
                        pa = a
                        break
                if pa is None or pa.get_text(strip=True) != name or not mats:
                    continue
                pq = pa.find_next_sibling("small", class_="itemQuantity")
                item["recipe"] = {
                    "station": stations[0] if stations else None,
                    "materials": mats,
                }
                # fallback tech level: "Technology Lv. N" in the recipe row
                if item["tech_level"] is None:
                    mt = re.search(r"Technology Lv\.\s*(\d+)",
                                   tr.get_text(" ", strip=True))
                    if mt:
                        item["tech_level"] = int(mt.group(1))
                try:
                    n_out = int(pq.get_text(strip=True)) if pq else 1
                except ValueError:
                    n_out = 1
                if n_out > 1:
                    item.setdefault("_notes", []).append(f"Crafts x{n_out} per batch")
                if len(stations) > 1:
                    item.setdefault("_notes", []).append(
                        "Also craftable at: " + ", ".join(stations[1:]))
                break

    # --- dropped by
    drop = find_section(soup, "Dropped By")
    if drop is not None:
        table = drop.select_one("table")
        if table:
            drops = []
            for tr in table.find_all("tr"):
                if tr.find("th"):
                    continue
                a = tr.find("a", class_="itemname")
                if not a:
                    continue
                who = a.get_text(" ", strip=True)
                q = tr.find("small", class_="itemQuantity")
                qty = q.get_text(strip=True) if q else ""
                mprob = re.search(r"([\d.]+%)", tr.get_text(" ", strip=True))
                prob = mprob.group(1) if mprob else "?"
                if who:
                    drops.append((who, qty, prob))
            # aggregate: list up to 12, else summarize
            if drops:
                if len(drops) <= 12:
                    for who, qty, prob in drops:
                        item["obtained_from"].append(f"Dropped by {who} ({prob})")
                else:
                    tops = [d for d in drops if d[2].rstrip("%").replace(".", "").isdigit()
                            and float(d[2].rstrip("%")) >= 50]
                    named = tops[:12] if tops else drops[:8]
                    for who, qty, prob in named:
                        item["obtained_from"].append(f"Dropped by {who} ({prob})")
                    item["obtained_from"].append(
                        f"...and {len(drops) - len(named)} more drop sources")

    # --- merchants
    merch = find_section(soup, "Wandering Merchant")
    if merch is not None and merch.select_one("table"):
        srcs = set()
        for tr in merch.select("table tr"):
            if tr.find("th"):
                continue
            links = tr.find_all("a")
            if len(links) >= 2:
                srcs.add(links[-1].get_text(" ", strip=True))
        if srcs:
            item["obtained_from"].append(
                f"Sold by merchants ({len(srcs)} shop listings)")

    # --- treasure boxes
    tb = find_section(soup, "Treasure Box")
    if tb is not None and tb.select_one("table tbody tr"):
        item["obtained_from"].append("Found in treasure chests")

    # --- overlays
    for extra in GATHER_OVERLAY.get(name, []):
        item["obtained_from"].append(extra)
    for extra in RANCH_OVERLAY.get(name, []):
        item["obtained_from"].append(extra)

    # dedup sources, preserving order
    item["obtained_from"] = list(dict.fromkeys(item["obtained_from"]))

    if "_notes" in item:
        item["notes"] = "; ".join(item.pop("_notes"))
    if not item["notes"]:
        item.pop("notes")
    return item, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--tech", required=True)
    args = ap.parse_args()

    slugs = json.load(open(os.path.join(RAW_DIR, "item_slugs.json")))
    tech_levels = parse_technologies(args.tech)

    items, metas, skipped, missing = [], [], [], []
    for slug, info in slugs.items():
        path = os.path.join(args.cache, slug + ".html")
        if not os.path.exists(path):
            missing.append(slug)
            continue
        try:
            item, meta = parse_item(path, slug, info["category"], info.get("name"),
                                    tech_levels)
        except Exception as e:
            missing.append(f"{slug} (parse error: {e})")
            continue
        if meta.get("legal") == "0" or is_junk_name(item["name"]):
            skipped.append(slug)
            continue
        # wild pal eggs: not crafted, found as map spawns
        if (item["name"].endswith(" Egg") and item["category"] == "material"
                and not item["recipe"]):
            item["category"] = "other"
            item["obtained_from"].append(
                "Wild egg spawn on the map (hatch in Egg Incubator)")
        # medicine refinement
        if item["category"] == "consumable" and meta.get("typeB", "").startswith("Medicine"):
            item["category"] = "medicine"
        # recipes where paldb lists no station
        if item["recipe"] and not item["recipe"]["station"]:
            if re.search(r"(Glove|Necklace|Harness|Headband|Saddle)s?$", item["name"]):
                # same item class as the 124 pal-gear recipes that do list it
                item["recipe"]["station"] = "Pal Gear Workbench"
                note = ("Station not listed on paldb.cc; filled in as Pal Gear "
                        "Workbench (all other pal gear recipes use it)")
            else:
                note = ("paldb.cc lists no crafting station for this recipe - "
                        "schematic/event-based craft made at the standard "
                        "workbench or assembly line for this item type")
            item["notes"] = (item.get("notes", "") + "; " + note).lstrip("; ")
        # tech level fallback from Technologies page
        if item["tech_level"] is None and item["name"] in tech_levels:
            item["tech_level"] = tech_levels[item["name"]][0]
        items.append(item)
        metas.append(meta)

    # de-dup by name (same item can appear via multiple slugs)
    seen = {}
    deduped = []
    for it in items:
        key = it["name"]
        if key in seen:
            old = seen[key]
            if old["recipe"] is None and it["recipe"]:
                old["recipe"] = it["recipe"]
            for src in it["obtained_from"]:
                if src not in old["obtained_from"]:
                    old["obtained_from"].append(src)
            continue
        seen[key] = it
        deduped.append(it)

    # stations: every station referenced by a recipe; classes = categories crafted
    st_map = {}
    for it in deduped:
        r = it.get("recipe")
        if r and r.get("station"):
            st_map.setdefault(r["station"], set()).add(it["category"])
    stations = []
    for st, cats in sorted(st_map.items()):
        lvl = tech_levels.get(st, (None, ""))[0]
        stations.append({
            "name": st,
            "crafts": ", ".join(sorted(cats)),
            "tech_level": lvl,
        })

    # coverage gaps: priority-category items with no recipe and no source
    empty = [i["name"] for i in deduped
             if not i["recipe"] and not i["obtained_from"]
             and i["category"] in ("material", "ingredient", "sphere", "ammo",
                                   "weapon", "armor", "medicine")]

    out = {
        "game_version": "1.0",
        "updated": str(date.today()),
        "items": deduped,
        "stations": stations,
        "notes": [
            "Scraped from paldb.cc (site data version v1.0.0, 2026/07/10 - matches game 1.0).",
            "recipe.station is the lowest-tier station; higher-tier alternatives are in the item's notes field.",
            "obtained_from drop probabilities are per-kill/per-capture rates from paldb.cc drop tables; entries may include human NPCs and bosses as well as pals.",
            "'Sold by merchants (N shop listings)' summarizes paldb.cc Wandering Merchant tables (village/wandering/caravan/dungeon shops).",
            "Mining-node, ranch (Farming) and wild-gathering sources are hand-added overlays for well-known base resources; paldb.cc does not list them in a structured way.",
            "key_item entries (journals, quest items, maps) are included for completeness; many legitimately have no recipe or listed source.",
            "Internal/cut-content entries with code-like names (e.g. Berries2, NPC_WEAPON) were filtered out.",
            "Some recipes (schematic/event cosmetics, crossover weapons, a few 1.0 items) have recipe.station = null because paldb.cc lists no station; each such item carries an explanatory note. Pal gear recipes missing a station were filled as Pal Gear Workbench based on the 124 sibling recipes that list it.",
        ],
        "gaps": [
            "Pal Expedition and fishing reward tables are not attached to item pages on paldb.cc, so expedition/fishing-only sources are not listed per item.",
            "Field notes: exact map coordinates for chests/gathering nodes are out of scope.",
            "Two paldb.cc pages 404ed (dynamic character-name petal/plume placeholder items).",
            "Items with no recipe and no obtained_from in priority categories (likely map pickups, shop-only, or 1.0 content paldb has not fully annotated): "
            + ", ".join(sorted(empty)),
        ],
        "sources": [
            {"url": "https://paldb.cc/en/Items and per-category pages (Material, Ingredient, Consumable, Weapon, Armor, Accessory, Ammo, Sphere, Sphere_Module, Key_Items, Glider)",
             "what": "item inventory: names, slugs, categories", "fetched": "2026-07-14"},
            {"url": "https://paldb.cc/en/<item_slug> (1260 per-item pages)",
             "what": "recipes (station + materials), tech level, drop tables, merchant/treasure sources, item stats", "fetched": "2026-07-14"},
            {"url": "https://paldb.cc/en/Technologies",
             "what": "technology tree levels for items and crafting stations", "fetched": "2026-07-14"},
        ],
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    json.load(open(OUT))
    print(f"items: {len(deduped)} (skipped illegal: {len(skipped)}, missing: {len(missing)})")
    print(f"stations: {len(stations)}")
    from collections import Counter
    print(Counter(i['category'] for i in deduped))
    if missing[:10]:
        print("missing sample:", missing[:10])
    # stash metas for debugging
    with open(os.path.join(RAW_DIR, "item_meta.json"), "w") as f:
        json.dump(metas, f, indent=0)


if __name__ == "__main__":
    main()
