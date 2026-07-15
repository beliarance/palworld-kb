#!/usr/bin/env python3
"""Fetch Palworld 1.0 item data from paldb.cc (server-rendered).

Stage 1: fetch category index pages -> slug list (data/raw/item_slugs.json)
Stage 2: fetch every per-item page -> cached HTML (scratchpad or --cache dir)
Stage 3 lives in parse_items.py.

Usage: python3 fetch_items.py --cache <dir> [--stage 1|2|all]
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup

BASE = "https://paldb.cc/en/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) item-db-collector"}

# category page slug -> our schema category
CATEGORY_PAGES = {
    "Material": "material",
    "Ingredient": "ingredient",
    "Consumable": "consumable",
    "Weapon": "weapon",
    "Armor": "armor",
    "Accessory": "accessory",
    "Ammo": "ammo",
    "Sphere": "sphere",
    "Sphere_Module": "other",
    "Key_Items": "key_item",
    "Glider": "technology",
}

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")


def fetch(url, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def stage1():
    """Collect item slugs per category from category index pages."""
    slugs = {}  # slug -> {name, category}
    for page, cat in CATEGORY_PAGES.items():
        html = fetch(BASE + page)
        soup = BeautifulSoup(html, "html.parser")
        n = 0
        for col in soup.select("div.col > div.card.itemPopup, div.col > div.d-flex.border.rounded"):
            a = col.select_one("a.itemname")
            if not a:
                continue
            href = (a.get("href") or "").strip()
            name = a.get_text(strip=True)
            if not href or href in ("-",) or href.startswith(("http", "#", "?")):
                continue
            if href not in slugs:
                slugs[href] = {"name": name, "category": cat}
                n += 1
        print(f"{page}: {n} items", flush=True)
        time.sleep(0.5)
    os.makedirs(RAW_DIR, exist_ok=True)
    out = os.path.join(RAW_DIR, "item_slugs.json")
    with open(out, "w") as f:
        json.dump(slugs, f, indent=1, ensure_ascii=False)
    print(f"total {len(slugs)} unique slugs -> {out}")
    return slugs


def stage2(cache_dir, slugs):
    os.makedirs(cache_dir, exist_ok=True)
    todo = [s for s in slugs if not os.path.exists(os.path.join(cache_dir, s + ".html"))]
    print(f"fetching {len(todo)} of {len(slugs)} pages", flush=True)
    errors = {}

    def one(slug):
        html = fetch(BASE + slug)
        with open(os.path.join(cache_dir, slug + ".html"), "w") as f:
            f.write(html)
        return slug

    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(one, s): s for s in todo}
        for fut in as_completed(futs):
            s = futs[fut]
            try:
                fut.result()
            except Exception as e:
                errors[s] = str(e)
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(todo)}", flush=True)
    if errors:
        with open(os.path.join(cache_dir, "_errors.json"), "w") as f:
            json.dump(errors, f, indent=1)
        print(f"{len(errors)} errors -> _errors.json")
    print("stage2 done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--stage", default="all")
    args = ap.parse_args()

    slug_file = os.path.join(RAW_DIR, "item_slugs.json")
    if args.stage in ("1", "all"):
        slugs = stage1()
    else:
        slugs = json.load(open(slug_file))
    if args.stage in ("2", "all"):
        stage2(args.cache, slugs)
