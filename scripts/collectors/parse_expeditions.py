#!/usr/bin/env python3
"""Parse palpedia.net/expeditions extracted text into structured JSON.

Input: text file produced by stripping tags from https://www.palpedia.net/expeditions
(one token per line). Output: JSON list of expeditions with rewards.

Usage: python3 parse_expeditions.py palpedia_text.txt > expeditions_raw.json
"""
import json
import re
import sys


def parse(path):
    lines = [l.strip() for l in open(path, encoding="utf-8").read().splitlines()]
    lines = [l for l in lines if l]

    expeditions = []
    cur = None
    section = None
    i = 0
    n = len(lines)
    while i < n:
        tok = lines[i]
        # section headers
        if tok in ("Regular Expeditions", "Grassland Expeditions", "Hard Expeditions",
                   "Sky Island Expeditions", "World Tree Expeditions"):
            section = tok
            i += 1
            continue
        if tok == "Duration" and i + 2 < n and lines[i + 1].isdigit():
            # previous non-keyword line is the expedition name
            name = lines[i - 1]
            cur = {"name": name, "section": section,
                   "duration_minutes": int(lines[i + 1]),
                   "difficulty": None, "firepower": None,
                   "element_multiplier": None,
                   "unlock_boss": None, "unlock_tower": None,
                   "rewards": []}
            expeditions.append(cur)
            i += 2
            continue
        if cur is None:
            i += 1
            continue
        if tok == "Difficulty":
            cur["difficulty"] = lines[i + 1]
            i += 2
            continue
        if tok == "Firepower":
            cur["firepower"] = lines[i + 1]
            i += 2
            continue
        if tok == "Element" and i + 2 < n and lines[i + 1].startswith("x"):
            cur["element_multiplier"] = int(lines[i + 2])
            i += 3
            continue
        if tok == "Unlock by defeating":
            cur["unlock_boss"] = lines[i + 1]
            if i + 3 < n and lines[i + 2].startswith("at"):
                cur["unlock_tower"] = lines[i + 3]
                i += 4
            else:
                i += 2
            continue
        # reward rows: slot number, item, "Qt.", qty, "Wt.", wt, "(", pct, "%)"
        m = re.fullmatch(r"\d+", tok)
        if m and i + 8 < n and lines[i + 2] == "Qt." and lines[i + 4] == "Wt.":
            cur["rewards"].append({
                "slot": int(tok),
                "item": lines[i + 1],
                "quantity": lines[i + 3],
                "weight": lines[i + 5],
                "chance_pct": float(lines[i + 7]),
            })
            i += 9
            continue
        i += 1
    return expeditions


if __name__ == "__main__":
    exps = parse(sys.argv[1])
    json.dump(exps, sys.stdout, indent=1)
    print(f"\n// {len(exps)} expeditions", file=sys.stderr)
