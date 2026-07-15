#!/usr/bin/env python3
"""Parse palworld.gg tier-list pages (downloaded HTML) into tiered pal lists.

Structure: <div class="tier S"><div class="t-name">S</div> ... <div class="pal">
  <img ... alt="PalName"> [work-type icons with alt + level text] ...
"""
import json
import re
import sys


def parse(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    # Split into tier blocks
    tiers = {}
    blocks = re.split(r'<div class="tier ([SABCDEF])">', html)
    # blocks: [prefix, 'S', block, 'A', block, ...]
    for i in range(1, len(blocks) - 1, 2):
        tier, block = blocks[i], blocks[i + 1]
        pals = []
        for pal_m in re.finditer(r'<div class="pal">(.*?)(?=<div class="pal">|$)', block, re.S):
            seg = pal_m.group(1)
            name_m = re.search(r'alt="([^"]+)"', seg)
            if not name_m:
                continue
            name = name_m.group(1)
            # work suitability icons: alt="Kindling" etc followed by <span>level</span>
            works = re.findall(r'alt="((?:Kindling|Watering|Planting|Generating Electricity|Handiwork|Gathering|Lumbering|Mining|Medicine Production|Cooling|Transporting|Farming))"[^>]*>\s*(?:<[^>]+>)*\s*(\d+)?', seg)
            pals.append({"name": name, "works": {w: (int(l) if l else None) for w, l in works}})
        tiers[tier] = pals
    return tiers


if __name__ == "__main__":
    print(json.dumps(parse(sys.argv[1]), indent=1))
