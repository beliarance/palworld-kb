#!/usr/bin/env python3
"""Fetch and parse passive skills from palworld.gg (second source for cross-check).

Usage: python3 fetch_passives_palworldgg.py [--cache page.html] [--out out.json]
"""
import argparse
import html as htmllib
import json
import re
import subprocess

URL = "https://palworld.gg/passive-skills"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

CARD_RE = re.compile(
    r'<article class="([^"]*)skill-card passive-skill">.*?'
    r'alt="Rank (-?\d+)".*?'
    r'<div class="name">([^<]+)</div>.*?'
    r'<p class="descr">(.*?)</p>',
    re.S)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    ap.add_argument("--out", default="palworldgg_passives_raw.json")
    args = ap.parse_args()

    if args.cache:
        page = open(args.cache, encoding="utf-8").read()
    else:
        page = subprocess.run(["curl", "-sL", "-A", UA, URL],
                              check=True, capture_output=True, text=True).stdout

    out = []
    for cls, rank, name, descr in CARD_RE.findall(page):
        descr = htmllib.unescape(re.sub(r"<[^>]+>", "", descr))
        lines = [re.sub(r"\s+", " ", l).strip() for l in descr.split("\n")]
        out.append({
            "name": htmllib.unescape(name).strip(),
            "rank": int(rank),
            "css_class": cls.strip(),
            "effect": ", ".join(l for l in lines if l),
        })
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"url": URL, "passives": out}, f, ensure_ascii=False, indent=1)
    print(f"parsed {len(out)} passives")


if __name__ == "__main__":
    main()
