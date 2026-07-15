#!/usr/bin/env python3
"""Collect merchant/shop data from paldb.cc into data/merchants.json.

Sources (all server-rendered, fetched with plain HTTP GET):
  https://paldb.cc/en/Merchant           -- all "Wandering Merchant" shop listings (item -> shop id)
  https://paldb.cc/en/<Shop_Code>        -- per-shop stock table (item, qty, price, currency)
  https://paldb.cc/en/Caravan_Merchant   -- list of caravan merchant NPC pages
  https://paldb.cc/en/<NPC_Page>         -- NPC page embeds its shop table header "<code> Wandering Merchant"
  https://paldb.cc/js/map_data_en.js     -- world-map markers: merchant NPC spawn coordinates

Resumable: every fetched page is cached in --cache; existing non-empty files are
never re-fetched, so the script can be re-run after network failures.

Usage:
  python3 scripts/collectors/fetch_merchants.py --cache /tmp/merchant_cache \
      [--out data/merchants.json] [--enrich-items] [--skip-fetch]

--enrich-items rewrites the placeholder 'Sold by merchants (N shop listings)'
entries in data/items.json with concrete per-shop strings.
"""
import argparse
import json
import math
import os
import re
import sys
import time
import urllib.request

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = "https://paldb.cc/en/"
MAPJS = "https://paldb.cc/js/map_data_en.js"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

TODAY = time.strftime("%Y-%m-%d")

# Map-marker ids that identify token shops (map_data_en.js carries no shop href
# for them; the association is via the merchant NPC that runs the shop:
# Arena Merchant sells for Battle Ticket = Arena_Shop_1, Medal Merchant sells
# for Dog Coin = Medal_Shop_1, PIDF Bounty Officer sells for Successful Bounty
# Token = Bounty_Shop_1).
MARKER_ID_TO_SHOP = {
    "ArenaShop": "Arena_Shop_1",
    "MedalTrader": "Medal_Shop_1",
    "BountyTrader": "Bounty_Shop_1",
}
MARKER_ID_TO_MERCHANT = {
    "ArenaShop": "Arena Merchant",
    "MedalTrader": "Medal Merchant",
    "BountyTrader": "PIDF Bounty Officer",
}


def fetch(url, path, skip_fetch=False, sleep=0.5):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, errors="ignore").read()
    if skip_fetch:
        raise SystemExit(f"missing cache file {path} and --skip-fetch given")
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(data)
    time.sleep(sleep)
    return data


def parse_merchant_index(html):
    """paldb.cc/en/Merchant -> sorted list of shop codes."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.DataTable")
    codes = set()
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) == 3:
            code = tds[2].get_text(strip=True)
            if code:
                codes.add(code)
    return sorted(codes)


def parse_shop_page(html):
    """Shop page -> list of {name, qty, price, currency}. Empty price cell =
    sold for Gold Coin at the item's standard buy value (paldb leaves it blank)."""
    soup = BeautifulSoup(html, "html.parser")
    hdr = soup.select_one("h5.card-header")
    if hdr is None:
        return []
    table = hdr.find_parent("div").select_one("table.DataTable")
    out, seen = [], set()
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 2:
            continue
        a = tds[0].find("a")
        if a is None:
            continue
        name = a.get_text(" ", strip=True)
        q = tds[0].find("small")
        qty = int(q.get_text(strip=True)) if q and q.get_text(strip=True).isdigit() else 1
        pa = tds[1].find("a")
        pq = tds[1].find("small")
        currency = pa.get_text(" ", strip=True) if pa else None
        price = None
        if pq:
            t = pq.get_text(strip=True).replace(",", "")
            price = int(t) if t.isdigit() else None
        if name in seen:  # paldb occasionally repeats a row
            continue
        seen.add(name)
        out.append({"name": name, "qty": qty, "price": price, "currency": currency})
    return out


def parse_caravan_npcs(html):
    """Caravan_Merchant page -> [(href, display_name)]."""
    soup = BeautifulSoup(html, "html.parser")
    npcs = []
    for li in soup.select("li a.itemname.d-inline-block[href]"):
        href = li.get("href")
        name = li.get_text(" ", strip=True)
        if href and name and not href.startswith("Passive"):
            npcs.append((href, name))
    return npcs


def parse_npc_shop_codes(html):
    return re.findall(r'<h5 class="card-header">([A-Za-z_0-9]+) Wandering Merchant', html)


def parse_map_markers(js_text):
    m = re.search(r"var fixedDungeon\s*=\s*(\[.*?\]);?\s*var regionData", js_text, re.S)
    return json.loads(m.group(1)) if m else []


def nearest_region(regions, x, y):
    best = min(regions.items(), key=lambda kv: math.hypot(x - kv[1][0], y - kv[1][1]))
    dist = math.hypot(x - best[1][0], y - best[1][1])
    return best[0], dist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(ROOT, "data", "raw", "merchant_cache"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "merchants.json"))
    ap.add_argument("--enrich-items", action="store_true")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="fail instead of hitting the network (cache must be complete)")
    args = ap.parse_args()
    cache = args.cache

    regions = json.load(open(os.path.join(ROOT, "data", "regions.json")))["regions"]

    # 1. shop codes
    idx_html = fetch(BASE + "Merchant", os.path.join(cache, "Merchant.html"), args.skip_fetch)
    shop_codes = parse_merchant_index(idx_html)
    print(f"shop codes: {len(shop_codes)}")

    # 2. per-shop stock
    stock = {}
    for code in shop_codes:
        html = fetch(BASE + code, os.path.join(cache, "shops", code + ".html"), args.skip_fetch)
        stock[code] = parse_shop_page(html)

    # 3. caravan NPC -> shop code
    car_html = fetch(BASE + "Caravan_Merchant",
                     os.path.join(cache, "Caravan_Merchant.html"), args.skip_fetch)
    npc_name_by_shop = {}
    for href, disp in parse_caravan_npcs(car_html):
        safe = href.replace("%26", "and")
        html = fetch(BASE + href, os.path.join(cache, "npcs", safe + ".html"), args.skip_fetch)
        for code in parse_npc_shop_codes(html):
            npc_name_by_shop[code] = disp

    # 4. map markers -> shop locations
    js = fetch(MAPJS, os.path.join(cache, "map_data_en.js"), args.skip_fetch)
    markers = parse_map_markers(js)
    shop_locs = {}           # shop code -> [{area, coordinates}]
    pal_trader_locs = {}     # merchant display name -> [ ... ]
    for d in markers:
        pos = d.get("ipos")
        if not pos:
            continue
        x, y = pos["X"], pos["Y"]
        code = None
        if d.get("type") == "Wandering Merchant" and d.get("href"):
            code = d["href"]
            merchant = "Wandering Merchant"
        elif d.get("id") in MARKER_ID_TO_SHOP:
            code = MARKER_ID_TO_SHOP[d["id"]]
            merchant = MARKER_ID_TO_MERCHANT[d["id"]]
        elif d.get("item") in ("Pal Merchant", "Black Marketeer") and d.get("type") in (
                "Black Marketeer", "NPC"):
            area, dist = nearest_region(regions, x, y)
            pal_trader_locs.setdefault(d["item"], []).append(
                {"area": area, "coordinates": f"({x}, {y})", "level": d.get("lv")})
            continue
        else:
            continue
        area, dist = nearest_region(regions, x, y)
        shop_locs.setdefault(code, []).append(
            {"area": area, "coordinates": f"({x}, {y})", "level": d.get("lv"),
             "_merchant": merchant})

    # 5. compose shops
    shops = {}
    for code in shop_codes:
        items = stock.get(code, [])
        curs = {i["currency"] for i in items if i["currency"]}
        currency = sorted(curs)[0] if curs else "Gold Coin"
        if code in npc_name_by_shop:
            merchant = npc_name_by_shop[code]
            locations = [{"area": "Visits player base (caravan merchant event)",
                          "coordinates": None}]
        elif code in shop_locs:
            merchant = shop_locs[code][0]["_merchant"]
            locations = [{k: v for k, v in loc.items() if k != "_merchant"}
                         for loc in sorted(shop_locs[code],
                                           key=lambda l: l.get("level") or 0)]
        elif code.startswith("Dungeon_Shop"):
            merchant = "Wandering Merchant"
            locations = [{"area": "Inside dungeons (random)", "coordinates": None}]
        elif code.startswith("Wander_Shop"):
            merchant = "Wandering Merchant"
            locations = [{"area": "Random roaming spawns across the map",
                          "coordinates": None}]
        elif code.startswith("Vagrant_Trader"):
            merchant = "Vagrant Trader"
            locations = []
        else:
            merchant = "Wandering Merchant"
            locations = []
        out_items = []
        for i in items:
            e = {"name": i["name"], "price": i["price"]}
            if i["qty"] > 1:
                e["qty"] = i["qty"]
            out_items.append(e)
        shops[code] = {"merchant": merchant, "currency": currency,
                       "locations": locations, "items": out_items}

    pal_traders = {
        name.replace(" ", "_"): {
            "merchant": name,
            "trades": ("Sells and buys Pals for Gold Coin"
                       + (" (rare/illegal stock; 92 Pal listings on paldb.cc/en/Black_Marketeer)"
                          if name == "Black Marketeer" else " (common Pals)")),
            "locations": sorted(locs, key=lambda l: l["coordinates"]),
        }
        for name, locs in sorted(pal_trader_locs.items())
    }

    data = {
        "game_version": "1.0",
        "updated": TODAY,
        "shops": shops,
        "pal_traders": pal_traders,
        "notes": [
            "Shop stock/prices scraped from paldb.cc per-shop pages (site data v1.0.0, 2026/07/10).",
            "An empty price column on paldb.cc means the shop sells for Gold Coin at the item's standard buy value; such items carry price=null and the shop currency defaults to Gold Coin.",
            "items[].qty is the stack size sold per purchase (only present when >1), e.g. Bounty shop sells Gold Coin x2000 for 1 Successful Bounty Token.",
            "Coordinates are exact NPC map markers from paldb.cc map data (js/map_data_en.js); 'area' is the nearest label from data/regions.json.",
            "Arena_Shop_1/Medal_Shop_1/Bounty_Shop_1 were tied to their map markers via the merchant NPC that uses that currency (Arena Merchant/Battle Ticket, Medal Merchant/Dog Coin, PIDF Bounty Officer/Successful Bounty Token).",
            "Caravan_Shop_1-25 are the 1.0 visiting caravan merchants: they spawn at the player's base (frequency scales with base level), no fixed map location.",
            "Wander_Shop_1 is the roaming Wandering Merchant variant (internal id SalesPerson_Wander): random spawns, no fixed coordinates.",
            "Dungeon_Shop_01 is the Wandering Merchant found inside randomly generated dungeons (internal id NPC_Dungeon_Shop).",
            "pal_traders lists Pal-selling NPCs (Pal Merchant, Black Marketeer) with map coordinates; their Pal stock is out of scope for items.json.",
        ],
        "gaps": [
            "Vagrant_Trader_1_1/2/3: merchant identity and location are not documented on paldb.cc or community guides; internal name suggests a roaming trader. Location unknown.",
            "Gold prices for Gold Coin shops are not listed by paldb.cc (game uses the item's standard buy value), so price=null for those entries.",
            "Wander_Shop_1 and Dungeon_Shop_01 have no fixed coordinates by design (random spawns).",
        ],
        "sources": [
            {"url": "https://paldb.cc/en/Merchant",
             "what": "all 587 Wandering Merchant shop listings (item -> shop id)", "fetched": TODAY},
            {"url": "https://paldb.cc/en/<Shop_Code> (38 shop pages)",
             "what": "per-shop stock, prices, currencies", "fetched": TODAY},
            {"url": "https://paldb.cc/en/Caravan_Merchant + 23 NPC pages",
             "what": "caravan merchant NPC names -> Caravan_Shop_N mapping", "fetched": TODAY},
            {"url": "https://paldb.cc/js/map_data_en.js",
             "what": "merchant NPC map markers (exact coordinates)", "fetched": TODAY},
        ],
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(data, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {args.out}: {len(shops)} shops, "
          f"{sum(len(s['items']) for s in shops.values())} listings")

    if args.enrich_items:
        enrich_items(data)


# ---------------------------------------------------------------- items.json

def _shop_sort_key(code):
    order = ["Village_Shop", "Desert_Shop", "Volcano_Shop", "Arena_Shop", "Medal_Shop",
             "Bounty_Shop", "Dungeon_Shop", "Wander_Shop", "Caravan_Shop", "Vagrant_Trader"]
    for i, p in enumerate(order):
        if code.startswith(p):
            m = re.search(r"(\d+)$", code)
            return (i, int(m.group(1)) if m else 0)
    return (len(order), 0)


def _loc_string(shop):
    locs = shop["locations"]
    if not locs:
        return "location unknown"
    parts = []
    for loc in locs:
        if loc.get("coordinates"):
            parts.append(f"{loc['area']} {loc['coordinates']}")
        else:
            parts.append(loc["area"])
    return ", ".join(dict.fromkeys(parts))


def _price_part(shop, entry):
    cur = shop["currency"]
    if cur == "Gold Coin":
        return "Gold"
    part = f"{entry['price']} {cur}" if entry.get("price") is not None else cur
    if entry.get("qty", 1) > 1:
        part = f"x{entry['qty']} for {part}"
    return part


def sold_string(shop, entry):
    return f"Sold by {shop['merchant']} ({_price_part(shop, entry)}) - {_loc_string(shop)}"


PLACEHOLDER_RE = re.compile(r"^Sold by merchants \(\d+ shop listings?\)$")


def enrich_items(merchants):
    path = os.path.join(ROOT, "data", "items.json")
    doc = json.load(open(path))
    shops = merchants["shops"]
    # item name -> {dedupe_key: string}; twin shops at the same spot (e.g.
    # Desert_Shop_1/2, same merchant+areas+price) collapse to one string.
    by_item = {}
    for code in sorted(shops, key=_shop_sort_key):
        shop = shops[code]
        areas = tuple(loc["area"] for loc in shop["locations"])
        for entry in shop["items"]:
            key = (shop["merchant"], _price_part(shop, entry), areas)
            by_item.setdefault(entry["name"], {}).setdefault(
                key, sold_string(shop, entry))
    replaced = missing = 0
    for item in doc["items"]:
        srcs = item.get("obtained_from") or []
        for i, s in enumerate(srcs):
            if PLACEHOLDER_RE.match(s):
                strings = list(by_item.get(item["name"], {}).values())
                if strings:
                    srcs[i:i + 1] = strings
                    replaced += 1
                else:
                    missing += 1
                break
    # refresh the stale note about the placeholder format
    doc["notes"] = [
        ("Merchant sources are per-shop: 'Sold by <merchant> (<price>) - <location (coords)>'; "
         "full shop tables in data/merchants.json.")
        if n.startswith("'Sold by merchants") else n
        for n in doc.get("notes", [])
    ]
    json.dump(doc, open(path, "w"), ensure_ascii=False, indent=1)
    print(f"items.json: replaced placeholder in {replaced} items"
          + (f", {missing} items had no shop match (left as-is)" if missing else ""))


if __name__ == "__main__":
    main()
