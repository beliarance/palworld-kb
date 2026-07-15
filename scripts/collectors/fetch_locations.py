#!/usr/bin/env python3
"""Fetch per-pal location data from paldb.cc pal pages.

For each pal in data/palworld_pals.csv (PaldbURL column), downloads the
server-rendered page and extracts:
  - egg type(s) (the "Egg" row in the header card)
  - Map card day/night spawn-point counts per map
  - Spawner table rows: (display name, alpha flag, level, location)
    where location is either a map link with coordinates or a raw
    spawner-area code (e.g. "desertisland_1", "sakurajima_grass2_2")

Writes a combined intermediate JSON to data/raw/paldb_locations_parsed.json.
Pages are fetched politely (sequential, small sleep) and discarded after
parsing. Re-runs skip pals already present in the output file unless
--refresh is given.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = "/Users/ivanzhilinskiy/Projects/Pal"
CSV_PATH = os.path.join(ROOT, "data", "palworld_pals.csv")
OUT_PATH = os.path.join(ROOT, "data", "raw", "paldb_locations_parsed.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
SLEEP = 0.35


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def strip_tags(s):
    import html as _html
    return _html.unescape(
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip())


def parse_page(html):
    out = {"egg": [], "maps": [], "spawners": []}

    # --- Egg row: <div>Egg</div> ... href="Huge_Rocky_Egg" ---
    m = re.search(r">Egg</div>(.{0,1200}?)</div>\s*<div", html, re.S)
    if m:
        for eh in re.findall(r'href="([A-Za-z_]*Egg)"', m.group(1)):
            name = eh.replace("_", " ")
            if name not in out["egg"]:
                out["egg"].append(name)

    # --- Map card: buttons like href="Palpagos_Islands?pal=X&t=dayTimeLocations" ... Day</span> (36) ---
    for mm in re.finditer(
            r'href="([A-Za-z_]+)\?pal=[^"]*&(?:amp;)?t=(dayTimeLocations|nightTimeLocations)"[^>]*>.*?\((\d+)\)</a>',
            html, re.S):
        out["maps"].append({
            "map": mm.group(1).replace("_", " "),
            "time": "day" if mm.group(2).startswith("day") else "night",
            "count": int(mm.group(3)),
        })

    # --- Spawner card ---
    m = re.search(r'>Spawner</h5>\s*<table.*?<tbody>(.*?)</table>', html, re.S)
    if m:
        body = m.group(1)
        rows = re.split(r"<tr>", body)
        for row in rows:
            if "itemname" not in row:
                continue
            cells = re.split(r"<td>", row)[1:]
            if len(cells) < 2:
                continue
            name = strip_tags(cells[0])
            alpha = "palAlpha" in cells[0]
            level = strip_tags(cells[1]) if len(cells) > 1 else None
            loc_raw = cells[2] if len(cells) > 2 else ""
            loc_link = re.search(
                r'href="([A-Za-z_]+)\?pos=([-\d.%C]+)"', loc_raw)
            if loc_link:
                coords = urllib.parse.unquote(loc_link.group(2))
                loc = {"type": "map", "map": loc_link.group(1).replace("_", " "),
                       "coords": coords, "text": strip_tags(loc_raw)}
            else:
                loc = {"type": "code", "code": strip_tags(loc_raw)}
            out["spawners"].append({
                "name": name, "alpha": alpha, "level": level, "loc": loc})
    return out


def main():
    refresh = "--refresh" in sys.argv
    pals = []
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            pals.append((row["Name"], row["PaldbURL"]))

    data = {}
    if os.path.exists(OUT_PATH) and not refresh:
        with open(OUT_PATH) as f:
            data = json.load(f)

    todo = [(n, u) for n, u in pals if n not in data]
    print(f"{len(pals)} pals total, {len(todo)} to fetch")
    for i, (name, url) in enumerate(todo, 1):
        try:
            html = fetch(url)
            data[name] = parse_page(html)
            data[name]["url"] = url
        except Exception as e:
            print(f"  FAIL {name}: {e}")
            data[name] = {"error": str(e), "url": url}
        if i % 20 == 0 or i == len(todo):
            print(f"  {i}/{len(todo)} done (last: {name})")
            with open(OUT_PATH, "w") as f:
                json.dump(data, f)
        time.sleep(SLEEP)

    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=1)
    ok = sum(1 for v in data.values() if "error" not in v)
    print(f"saved {OUT_PATH}: {ok} ok / {len(data)} total")


if __name__ == "__main__":
    main()
