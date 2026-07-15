#!/usr/bin/env python3
"""Collect Palworld 1.0 base-building data from paldb.cc (server-rendered).

Fetches:
  1. Structure pages (Palbox, beds, plantations, kitchens, generators, ...)
     -> tech level, ancient-tech flag, build materials, energy use, worker slots,
        description, misc stats (Worker Max etc).
  2. Food item pages -> Nutrition / SAN / Corruption (spoil) values.
  3. All 299 pal pages (data/palworld_pals.csv) -> FoodAmount (appetite 1-10)
     and FullStomachDecreaseRate (hunger drain modifier).

Raw parse is written to --raw-out (data/raw/paldb_base_building_raw.json);
the final data/base_building.json is assembled by build_base_building.py.

Usage:
    python3 fetch_base_building.py --cache-dir CACHE --raw-out RAW.json
"""

import argparse
import csv
import html as htmllib
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125 Safari/537.36")
BASE = "https://paldb.cc/en/"
TAG_RE = re.compile(r"<[^>]+>")

# slug -> display name (canonical 1.0 names from paldb construction category pages)
STRUCTURES = {
    # Pal category
    "Palbox": "Palbox",
    "Ranch": "Ranch",
    "Monitoring_Stand": "Monitoring Stand",
    "High_Quality_Monitoring_Stand": "High Quality Monitoring Stand",
    "Ancient_Monitoring_Stand": "Ancient Monitoring Stand",
    "Egg_Incubator": "Egg Incubator",
    "Electric_Egg_Incubator": "Electric Egg Incubator",
    "Large_Incubator": "Large Incubator",
    "Large-Scale_Electric_Egg_Incubator": "Large-Scale Electric Egg Incubator",
    "Breeding_Farm": "Breeding Farm",
    "Ancient_Hatchery": "Ancient Hatchery",
    "Pal_Labor_Research_Lab": "Pal Labor Research Lab",
    "Pal_Expedition_Station": "Pal Expedition Station",
    "Pal_Essence_Condenser": "Pal Essence Condenser",
    "Statue_of_Power": "Statue of Power",
    # Food category
    "Campfire": "Campfire",
    "Feed_Box": "Feed Box",
    "Cold_Food_Box": "Cold Food Box",
    "Berry_Plantation": "Berry Plantation",
    "Wheat_Plantation": "Wheat Plantation",
    "Tomato_Plantation": "Tomato Plantation",
    "Lettuce_Plantation": "Lettuce Plantation",
    "Potato_Plantation": "Potato Plantation",
    "Carrot_Plantation": "Carrot Plantation",
    "Onion_Plantation": "Onion Plantation",
    "Skillfruit_Orchard": "Skillfruit Orchard",
    "Ancient_Farm": "Ancient Farm",
    "Cooking_Pot": "Cooking Pot",
    "Electric_Kitchen": "Electric Kitchen",
    "Large-Scale_Stone_Oven": "Large-Scale Stone Oven",
    "Ancient_Kitchen": "Ancient Kitchen",
    # Production (food/medicine adjacent)
    "Mill": "Mill",
    "Medieval_Medicine_Workbench": "Medieval Medicine Workbench",
    "Electric_Medicine_Workbench": "Electric Medicine Workbench",
    "Advanced_Medicine_Workbench": "Advanced Medicine Workbench",
    # Storage (food preservation)
    "Cooler_Box": "Cooler Box",
    "Refrigerator": "Refrigerator",
    # Infrastructure
    "Straw_Pal_Bed": "Straw Pal Bed",
    "Fluffy_Pal_Bed": "Fluffy Pal Bed",
    "Large_Pal_Bed": "Large Pal Bed",
    "Ancient_Pal_Bed": "Ancient Pal Bed",
    "Pal_Pod": "Pal Pod",
    "Hot_Spring": "Hot Spring",
    "High_Quality_Hot_Spring": "High Quality Hot Spring",
    "Ancient_Hot_Spring": "Ancient Hot Spring",
    "Medicine_Rack": "Medicine Rack",
    "Clinic": "Clinic",
    "Ancient_Clinic": "Ancient Clinic",
    "Human-Powered_Generator": "Human-Powered Generator",
    "Power_Generator": "Power Generator",
    "Large_Power_Generator": "Large Power Generator",
    "Ancient_Power_Generator": "Ancient Power Generator",
    "Accumulator": "Accumulator",
    "Heater": "Heater",
    "Cooler": "Cooler",
    "Electric_Heater": "Electric Heater",
    "Electric_Cooler": "Electric Cooler",
    "Electric_Pylon": "Electric Pylon",
}

# slug -> display name for food/consumable item pages
FOODS = {
    "Red_Berries": "Red Berries",
    "Baked_Berries": "Baked Berries",
    "Wheat": "Wheat",
    "Flour": "Flour",
    "Bread": "Bread",
    "Jam-Filled_Bun": "Jam-Filled Bun",
    "Tomato": "Tomato",
    "Lettuce": "Lettuce",
    "Potato": "Potato",
    "Carrot": "Carrot",
    "Onion": "Onion",
    "Mushroom": "Mushroom",
    "Baked_Mushroom": "Baked Mushroom",
    "Marinated_Mushrooms": "Marinated Mushrooms",
    "Mushroom_Soup": "Mushroom Soup",
    "Mushroom_Quiche": "Mushroom Quiche",
    "Egg": "Egg",
    "Fried_Egg": "Fried Egg",
    "Omelet": "Omelet",
    "Milk": "Milk",
    "Hot_Milk": "Hot Milk",
    "Pancake": "Pancake",
    "Honey": "Honey",
    "Salad": "Salad",
    "Pizza": "Pizza",
    "Carbonara": "Carbonara",
    "Cake": "Cake",
    "Mushroom_Cake": "Mushroom Cake",
    "Vegetable_Cake": "Vegetable Cake",
    "Extravagant_Vegetable_Cake": "Extravagant Vegetable Cake",
    "Special_Cake": "Special Cake",
    "Raw_Meat": "Raw Meat",
    "Grilled_Meat": "Grilled Meat",
    "Stir-Fried_Vegetables": "Stir-Fried Vegetables",
    "French_Fries": "French Fries",
    "Spring_Rolls": "Spring Rolls",
    "Gratin": "Gratin",
    "Minestrone": "Minestrone",
    "Seafood_Salad": "Seafood Salad",
    "Seafood_Pasta": "Seafood Pasta",
    "Potage": "Potage",
    "Corn": "Corn",
    "Corn_Soup": "Corn Soup",
    "Pumpkin": "Pumpkin",
    "Grape": "Grape",
    "Stew": "Stew",
    "Curry": "Curry",
    "Hamburger": "Hamburger",
    "Cheeseburger": "Cheeseburger",
    "Sandwich": "Sandwich",
    "BLT": "BLT",
    "Hot_Dog": "Hot Dog",
    "Mushroom_Stew": "Mushroom Stew",
    "Grilled_Fish": "Grilled Fish",
    "Seafood_Soup": "Seafood Soup",
    "Farmers_Special_Dish": "Farmer's Special Dish",
}

# work-suitability handbook sample pages (level 9-10 mechanism research)
EXTRA_PAGES = {
    "Applied_Kindling_Handbook_I": "Applied Kindling Handbook I",
    "Applied_Handiwork_Handbook_I": "Applied Handiwork Handbook I",
}


def fetch(url, cache_path, retries=3, min_size=5000):
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > min_size:
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            if len(body) > min_size:
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(body)
                time.sleep(0.4)  # politeness
                return body
            last_err = f"short body ({len(body)} bytes)"
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def clean(fragment):
    txt = TAG_RE.sub(" ", fragment)
    txt = htmllib.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def parse_summary(html):
    """Parse the top summary strip: technology, energy, work slots, real time."""
    out = {}
    m = re.search(
        r'data-hover="\?s=Technology%2F([^"]+)">Technology</span></span>'
        r'<span class="border p-1">(\d+)</span>', html)
    if m:
        out["tech_id"] = htmllib.unescape(m.group(1))
        out["tech_level"] = int(m.group(2))
        out["ancient_tech"] = m.group(1).startswith("Special_")
    m = re.search(
        r'>Energy</span><span class="border p-1">([\d,]+)\s*Per Sec</span>',
        html)
    if m:
        out["energy_per_sec"] = int(m.group(1).replace(",", ""))
    m = re.search(
        r'>Real Time</span><span class="border p-1">([^<]+)</span>', html)
    if m:
        out["real_time"] = m.group(1).strip()
    # work suitability badges: <a href="Planting"><img ...palwork_XX...></a></span>
    #                          <span class="border p-1">N</span>
    for wm in re.finditer(
            r'<a href="([A-Za-z_]+)"><img[^>]*T_icon_palwork_\d+[^>]*/?></a>'
            r'</span><span class="border p-1">(\d+)</span>', html):
        out.setdefault("work", []).append(
            {"type": wm.group(1).replace("_", " "), "value": int(wm.group(2))})
    return out


def parse_description(html):
    m = re.search(r'<div class="card-body py-2">\s*<div>(.*?)</div>', html,
                  re.S)
    return clean(m.group(1)) if m else None


def parse_materials(html):
    """Build materials from the recipes strip under the description."""
    start = html.find('<div class="recipes">')
    if start >= 0:
        end = html.find('<div class="card', start)
        scope = html[start:end if end > 0 else start + 8000]
    else:
        scope = html[:20000]
    mats = {}
    for m in re.finditer(
            r'<div class="d-flex justify-content-between p-2 align-items-center '
            r'border-top">\s*<div><a class="itemname"[^>]*href="[^"]*"[^>]*>'
            r'(?:<img[^>]*/?>)?\s*([^<]+)</a></div>\s*<div>([\d,]+)</div>',
            scope):
        mats[htmllib.unescape(m.group(1)).strip()] = int(
            m.group(2).replace(",", ""))
    return mats or None


def parse_summary_badges(html):
    """All Key/Value badge pairs from the top summary strip."""
    out = {}
    for m in re.finditer(
            r'<span class="bg-dark bg-gradient p-1">([^<]+)</span>'
            r'<span class="border p-1">([^<]+)</span>', html):
        out[htmllib.unescape(m.group(1)).strip()] = htmllib.unescape(
            m.group(2)).strip()
    return out


def parse_stat_rows(html):
    rows = {}
    for m in re.finditer(
            r'<div class="d-flex justify-content-between p-2 align-items-center '
            r'border-bottom">\s*<div>([^<]+)</div>\s*<div>([^<]*)</div>', html):
        rows[m.group(1).strip()] = m.group(2).strip()
    return rows


def parse_structure(html):
    d = parse_summary(html)
    d["description"] = parse_description(html)
    d["materials"] = parse_materials(html)
    stats = parse_stat_rows(html)
    keep = ("Worker Max", "Code", "TypeA", "TypeB", "Hp", "SortId")
    d["stats"] = {k: stats[k] for k in keep if k in stats}
    return d


def parse_food(html):
    d = {}
    badges = parse_summary_badges(html)
    sec = re.search(
        r'<h5 class="card-title text-info">\s*Foods\s*</h5>(.*?)'
        r'(?:<h5|<div class="card )', html, re.S)
    rows = parse_stat_rows(sec.group(1)) if sec else {}
    for key in ("Nutrition", "SAN", "Corruption", "Work Speed",
                "Recovery Time"):
        if key not in rows and key in badges:
            rows[key] = badges[key]
    d["nutrition"] = int(rows["Nutrition"]) if rows.get("Nutrition") else None
    d["sanity"] = float(rows["SAN"]) if rows.get("SAN") else None
    d["corruption"] = rows.get("Corruption")
    d["work_speed"] = rows.get("Work Speed")
    d["recovery_time"] = rows.get("Recovery Time")
    d["description"] = parse_description(html)
    return d


def parse_pal(html):
    d = {}
    m = re.search(r'<div>FoodAmount</div>\s*<div>(\d+)</div>', html)
    d["food_amount"] = int(m.group(1)) if m else None
    m = re.search(r'<div>FullStomachDecreaseRate</div>\s*<div>([\d.]+)</div>',
                  html)
    d["full_stomach_decrease_rate"] = float(m.group(1)) if m else None
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--raw-out", required=True)
    ap.add_argument("--csv", default=os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "palworld_pals.csv"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--skip-pals", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.cache_dir, exist_ok=True)

    result = {"structures": {}, "foods": {}, "extra_pages": {}, "pals": {},
              "failures": []}

    def grab(slug, cache_prefix=""):
        path = os.path.join(args.cache_dir, cache_prefix + slug.replace("%27", "") + ".html")
        return fetch(BASE + slug, path)

    for group, pages, parser in (
            ("structures", STRUCTURES, parse_structure),
            ("foods", FOODS, parse_food)):
        for slug, name in pages.items():
            try:
                result[group][name] = parser(grab(slug))
                result[group][name]["slug"] = slug
            except Exception as e:  # noqa: BLE001
                result["failures"].append(f"{group}:{name} ({e})")
        print(f"{group}: {len(result[group])} parsed", file=sys.stderr)

    for slug, name in EXTRA_PAGES.items():
        try:
            html = grab(slug)
            result["extra_pages"][name] = {
                "description": parse_description(html),
                "stats": parse_stat_rows(html)}
        except Exception as e:  # noqa: BLE001
            result["failures"].append(f"extra:{name} ({e})")

    if not args.skip_pals:
        with open(args.csv, newline="", encoding="utf-8") as f:
            pals = [(row["Name"], row["PaldbURL"])
                    for row in csv.DictReader(f) if row["PaldbURL"]]

        def job(name, url):
            slug = url.rsplit("/", 1)[-1]
            page = fetch(url, os.path.join(args.cache_dir, "pal_" + slug + ".html"))
            return name, parse_pal(page)

        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(job, n, u): n for n, u in pals}
            done = 0
            for fut in as_completed(futs):
                name = futs[fut]
                try:
                    n, d = fut.result()
                    result["pals"][n] = d
                except Exception as e:  # noqa: BLE001
                    result["failures"].append(f"pal:{name} ({e})")
                done += 1
                if done % 50 == 0:
                    print(f"  {done}/{len(futs)} pal pages", file=sys.stderr)
        print(f"pals: {len(result['pals'])} parsed", file=sys.stderr)

    result["pals"] = dict(sorted(result["pals"].items()))
    with open(args.raw_out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"failures: {len(result['failures'])}", file=sys.stderr)
    for x in result["failures"]:
        print("  " + x, file=sys.stderr)


if __name__ == "__main__":
    main()
