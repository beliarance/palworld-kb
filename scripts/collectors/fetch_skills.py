#!/usr/bin/env python3
"""Collect Palworld active skills + per-pal learnsets from paldb.cc.

Usage:
    python3 fetch_skills.py --cache-dir /path/to/cache --out /path/to/active_skills.json

Steps:
  1. Fetch https://paldb.cc/en/Active_Skills (server-rendered card list) -> skills.
  2. Fetch each pal page listed in data/palworld_pals.csv (PaldbURL column)
     -> "Active Skills" section cards carry "Lv. N <skill>" learnset entries.
All pages are cached on disk so re-runs are cheap.
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
from datetime import date

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125 Safari/537.36")
CANON_ELEMENTS = {"Neutral", "Fire", "Water", "Electric", "Grass", "Ice",
                  "Ground", "Dark", "Dragon"}

CARD_SPLIT = '<div class="card itemPopup activeSkill">'
TAG_RE = re.compile(r"<[^>]+>")


def fetch(url, cache_path, retries=3):
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 5000:
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            if len(body) > 5000:
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(body)
                return body
            last_err = f"short body ({len(body)} bytes)"
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def clean_text(fragment):
    txt = TAG_RE.sub("", fragment)
    txt = htmllib.unescape(txt)
    return re.sub(r"\s+", " ", txt).strip()


def parse_skill_card(card):
    """Parse one activeSkill card (from the index or a pal page)."""
    m = re.search(
        r'<a data-hover="\?s=Waza[^"]*" href="[^"]*"[^>]*>([^<]+)</a>', card)
    if not m:
        return None
    skill = {"name": htmllib.unescape(m.group(1)).strip()}

    # learnset level if present ("Lv. 7 <a ...")
    lv = re.search(r'Lv\.\s*(\d+)\s*<a data-hover="\?s=Waza', card)
    skill["_level"] = int(lv.group(1)) if lv else None

    # element: the banner span next to the element icon
    el = re.search(r'padding-left:\s*35px">([A-Za-z]+)</span>', card)
    skill["element"] = el.group(1) if el else None

    ct = re.search(
        r'CoolTime[^:]*</?[^>]*>?:\s*<span[^>]*>(\d+)</span>', card)
    if not ct:
        ct = re.search(
            r'T_Icon_PalSkillCoolTime[^:]*class="size24"/>:\s*<span[^>]*>(\d+)</span>',
            card)
    skill["cooldown_seconds"] = int(ct.group(1)) if ct else None

    pw = re.search(r'Power:\s*<span[^>]*>(\d+)</span>', card)
    skill["power"] = int(pw.group(1)) if pw else None

    rng = re.search(r'data-bs-title="([^"]*Attack Range[^"]*)"', card)
    skill["range"] = htmllib.unescape(rng.group(1)) if rng else None

    skill["skill_fruit_exists"] = "Skill_Fruit" in card

    body = re.search(r'<div class="card-body">(.*?)</div>\s*</div>', card,
                     re.S)
    desc_raw = body.group(1) if body else ""
    skill["description"] = clean_text(desc_raw)

    # exclusives: "<a href="Pal">Pal</a>['s| and ...] exclusive skill."
    exclusive = None
    if "exclusive skill" in desc_raw:
        head = desc_raw.split("exclusive skill")[0]
        exclusive = [htmllib.unescape(x).strip()
                     for x in re.findall(r'<a href="[^"]+">([^<]+)</a>', head)]
        exclusive = exclusive or None
    skill["exclusive_to"] = exclusive
    return skill


def parse_active_skills_index(html):
    skills = []
    for card in html.split(CARD_SPLIT)[1:]:
        s = parse_skill_card(card)
        if s:
            s.pop("_level", None)
            skills.append(s)
    return skills


def parse_pal_learnset(html):
    """Return [(skill_name, level), ...] from a pal page."""
    sec = re.search(
        r'data-i18n="common_active_skill">Active Skills</h5>(.*?)'
        r'(?:<h5|<div class="card mt-3">\s*<div class="card-body">\s*<h5)',
        html, re.S)
    scope = sec.group(1) if sec else html
    out = []
    for card in scope.split(CARD_SPLIT)[1:]:
        s = parse_skill_card(card)
        if s and s.get("_level") is not None:
            out.append((s["name"], s["_level"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv", default=os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "palworld_pals.csv"))
    ap.add_argument("--raw-dir", default=None,
                    help="where to keep the raw index page")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    os.makedirs(args.cache_dir, exist_ok=True)

    idx_cache = os.path.join(args.raw_dir or args.cache_dir,
                             "paldb_active_skills.html")
    if args.raw_dir:
        os.makedirs(args.raw_dir, exist_ok=True)
    index_html = fetch("https://paldb.cc/en/Active_Skills", idx_cache)
    skills = parse_active_skills_index(index_html)
    print(f"parsed {len(skills)} skills from index", file=sys.stderr)

    # pals
    with open(args.csv, newline="", encoding="utf-8") as f:
        pals = [(row["Name"], row["PaldbURL"]) for row in csv.DictReader(f)]
    print(f"{len(pals)} pals in CSV", file=sys.stderr)

    learnsets, failures = {}, []

    def job(name, url):
        slug = url.rsplit("/", 1)[-1]
        page = fetch(url, os.path.join(args.cache_dir, slug + ".html"))
        return name, parse_pal_learnset(page)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(job, n, u): n for n, u in pals if u}
        done = 0
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                n, ls = fut.result()
                if ls:
                    learnsets[n] = [{"skill": s, "level": lv} for s, lv in ls]
                else:
                    failures.append(name + " (no learnset parsed)")
            except Exception as e:  # noqa: BLE001
                failures.append(f"{name} ({e})")
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(futs)} pal pages", file=sys.stderr)

    result = {
        "skills": skills,
        "learnsets": dict(sorted(learnsets.items())),
        "failures": failures,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"skills={len(skills)} learnsets={len(learnsets)} "
          f"failures={len(failures)}", file=sys.stderr)


if __name__ == "__main__":
    main()
