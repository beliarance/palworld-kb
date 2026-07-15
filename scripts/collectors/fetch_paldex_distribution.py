#!/usr/bin/env python3
"""Fetch in-game Paldex habitat distribution data from paldb.cc and reduce it.

Downloads:
  https://paldb.cc/DataTable/UI/DT_PaldexDistributionData.json  (~19 MB)
      per-pal (internal codename) day/night habitat spawn points, world coords
  https://paldb.cc/js/map_data_en.js
      contains `var regionData = [...]` - named map region labels + map coords
  https://paldb.cc/en/Pals
      used to build internal codename -> English pal name mapping

Reduces the big distribution file to per-pal nearest-region tallies and writes:
  data/raw/paldb_region_labels.json   - the 80 named region labels
  data/raw/paldb_codename_map.json    - codename -> English name
  data/raw/paldex_region_tallies.json - per codename: day/night point counts +
                                        {region name: point count} (day+night)

The 19 MB source file is discarded after reduction.

Coordinate transform (world "rpos" -> in-game map "ipos") reproduces
paldb.cc's map JS: config landScapeRealPosition bounds, perPixel=459,
ingame offsets from the map page inline script.
"""
import json
import os
import re
import urllib.request
from collections import Counter

ROOT = "/Users/ivanzhilinskiy/Projects/Pal"
RAW = os.path.join(ROOT, "data", "raw")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MINX, MAXX = -1099400, 349400
MINY, MAXY = -724400, 724400
PER = 459
TX = (MAXX - MINX) / PER
TY = (MAXY - MINY) / PER
IXS = 1000 + (-582888 - MINX) / PER
IYS = 1000 + (-301000 - MINY) / PER

# Region labels that are not wild-spawn habitat (POIs, arenas, rigs, villages)
REGION_EXCLUDE_IDS = {
    "REGION_Arena", "REGION_Array",
    "REGION_Oilrig_1", "REGION_Oilrig_2", "REGION_Oilrig_3",
    "REGION_Grass_1_Church", "REGION_PvP_1_Church", "REGION_PvP_2_Church",
    "REGION_PvP_3_Church", "REGION_Grass_1_Village",
    "REGION_Volcano_1_Village", "REGION_Desert_1_Village",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def rpos_to_ipos(x, y):
    sx = (x - MINX) / (MAXX - MINX)
    sy = (y - MINY) / (MAXY - MINY)
    return (round(sy * TY - IYS), round(sx * TX - IXS))


def main():
    os.makedirs(RAW, exist_ok=True)

    # --- region labels ---
    mapjs = get("https://paldb.cc/js/map_data_en.js")
    i = mapjs.find("var regionData =")
    j = mapjs.find("var ", i + 5)
    region_data = json.loads(
        mapjs[i + len("var regionData ="):j].strip().rstrip(";"))
    with open(os.path.join(RAW, "paldb_region_labels.json"), "w") as f:
        json.dump(region_data, f, indent=1, ensure_ascii=False)
    labels = [(r["item"], r["ipos"]["X"], r["ipos"]["Y"]) for r in region_data
              if r["id"] not in REGION_EXCLUDE_IDS]
    print(f"region labels: {len(region_data)} ({len(labels)} habitat)")

    # --- codename map ---
    idx = get("https://paldb.cc/en/Pals")
    pairs = re.findall(
        r'T_([A-Za-z0-9_]+?)_icon_normal\.webp[^>]*/></a>.*?'
        r'href="([A-Za-z0-9_%\']+)">([^<]+)</a>', idx, re.S)
    codename_map = {}
    for code, href, name in pairs:
        codename_map.setdefault(code, name)
    with open(os.path.join(RAW, "paldb_codename_map.json"), "w") as f:
        json.dump(codename_map, f, indent=1, ensure_ascii=False)
    print(f"codename map: {len(codename_map)} pals")

    # --- distribution -> tallies ---
    dist = json.loads(
        get("https://paldb.cc/DataTable/UI/DT_PaldexDistributionData.json"))
    rows = dist[0]["Rows"]
    tallies = {}
    for codename, row in rows.items():
        day = (row.get("dayTimeLocations") or {}).get("Locations") or []
        night = (row.get("nightTimeLocations") or {}).get("Locations") or []
        tally = Counter()
        for p in list(day) + list(night):
            ix, iy = rpos_to_ipos(p["X"], p["Y"])
            best, bd = None, None
            for item, lx, ly in labels:
                d = (ix - lx) ** 2 + (iy - ly) ** 2
                if bd is None or d < bd:
                    best, bd = item, d
            tally[best] += 1
        tallies[codename] = {
            "day_points": len(day),
            "night_points": len(night),
            "regions": dict(tally.most_common()),
        }
    out = os.path.join(RAW, "paldex_region_tallies.json")
    with open(out, "w") as f:
        json.dump(tallies, f, indent=1, ensure_ascii=False)
    print(f"wrote {out}: {len(tallies)} codenames")


if __name__ == "__main__":
    main()
