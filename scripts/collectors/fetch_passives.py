#!/usr/bin/env python3
"""Fetch and parse the Palworld 1.0 passive skills list from paldb.cc.

Usage:
    python3 fetch_passives.py [--cache /path/to/cached.html] [--out /path/to/out.json]

Parses https://paldb.cc/en/Passive_Skills (server-rendered). The page has
two tabs:
  - "Pal Passive Skills /114"  -> the standard obtainable pal passive list
  - "Pal Passive Skills /298"  -> extended list incl. hidden/NPC/raid passives

Each passive block looks like:
  <div class="mb-1 passive_banner_rank{N}"> ... tooltip (raw internal effects,
      weight, ToSelf/ToTrainer/ToBaseCampPal targets) ...
      <div class="passive-rank{N} ...">Name</div> ...
  <div class="p-2" ...><div>EFFECT TEXT</div><div>[exclusive pal <a> icons]</div></div>

Rank classes observed: -3..-1 (detrimental), 1..4, 5 (new 1.0 "rainbow+" tier).
"""
import argparse
import html as htmllib
import json
import re
import subprocess
import sys

URL = "https://paldb.cc/en/Passive_Skills"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

HEAD_RE = re.compile(
    r'passive_banner_rank(?P<rank>-?\d+)".*?'
    r'data-bs-title="(?P<tooltip>.*?)".*?'
    r'passive-rank(?P=rank)[^"]*"[^>]*>(?P<name>[^<]+)</div>.*?'
    r'<div class="p-2" style="position: relative">\s*',
    re.S)

PAL_LINK_RE = re.compile(r'href="([^"]+)"')
TAG_RE = re.compile(r'<[^>]+>')


def fetch(url: str) -> str:
    return subprocess.run(
        ["curl", "-sL", "-A", UA, url],
        check=True, capture_output=True, text=True).stdout


def clean_effect(raw: str) -> str:
    """Turn the effect HTML fragment into 'Attack +30%, Work Speed -50%'."""
    txt = re.sub(r'<span class="badge[^"]*">\s*\((ToSelf|None)\)\s*</span>', "", raw)
    txt = re.sub(r'<span class="badge[^"]*">\s*\(ToTrainer\)\s*</span>', "(Player)", txt)
    txt = re.sub(r'<span class="badge[^"]*">\s*\(ToBaseCampPal\)\s*</span>', "(Base Pals)", txt)
    txt = re.sub(r'</div>\s*', "\n", txt)
    txt = txt.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    txt = TAG_RE.sub("", txt)
    txt = htmllib.unescape(txt)
    parts = [re.sub(r"\s+", " ", p).strip() for p in txt.split("\n")]
    parts = [p for p in parts if p]
    return ", ".join(parts)


def balanced_div(html_str: str, start: int) -> tuple[str, int]:
    """Return inner HTML of the <div> whose content starts at `start`
    (i.e. just after its opening tag), plus the index after its close."""
    depth = 1
    i = start
    tag = re.compile(r'<(/?)div\b[^>]*>')
    while depth:
        m = tag.search(html_str, i)
        if not m:
            return html_str[start:], len(html_str)
        depth += -1 if m.group(1) else 1
        i = m.end()
    return html_str[start:m.start()], i


def parse_tab(tab_html: str) -> list[dict]:
    out = []
    for m in HEAD_RE.finditer(tab_html):
        name = htmllib.unescape(m.group("name")).strip()
        rank = int(m.group("rank"))
        # The p-2 container holds two sibling divs: effect text, then
        # exclusive-pal icon links. Extract them with balanced matching.
        pos = m.end()
        assert tab_html[pos:pos + 5] == "<div>", tab_html[pos:pos + 40]
        effect_html, pos = balanced_div(tab_html, pos + 5)
        pal_m = re.match(r'\s*<div[^>]*>', tab_html[pos:])
        pals_html = ""
        if pal_m:
            pals_html, _ = balanced_div(tab_html, pos + pal_m.end())
        effect = clean_effect(effect_html)
        tooltip = htmllib.unescape(m.group("tooltip"))
        weight_m = re.search(r"Weight (\d+)", tooltip)
        pals = PAL_LINK_RE.findall(pals_html)
        pals = [htmllib.unescape(p).replace("_", " ") for p in pals]
        out.append({
            "name": name,
            "rank": rank,
            "effect": effect,
            "tooltip_raw": re.sub(r"\s+", " ", TAG_RE.sub(" ", tooltip)).strip(),
            "weight": int(weight_m.group(1)) if weight_m else None,
            "exclusive_pals": pals,
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", help="use a previously downloaded HTML file")
    ap.add_argument("--out", default="paldb_passives_raw.json")
    args = ap.parse_args()

    if args.cache:
        page = open(args.cache, encoding="utf-8").read()
    else:
        page = fetch(URL)

    # Split into the two tabs.
    i114 = page.find('<div id="PalPassiveSkills" class="tab-pane')
    i298 = page.find('<div id="PalPassiveSkills_cache-1"')
    iend = page.find('<div id="PassiveSkills"')
    if min(i114, i298, iend) < 0:
        sys.exit("page structure changed: tab anchors not found")

    tab114 = parse_tab(page[i114:i298])
    tab298 = parse_tab(page[i298:iend])

    result = {"url": URL, "tab_standard_114": tab114, "tab_extended_298": tab298}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"standard tab: {len(tab114)} passives, extended tab: {len(tab298)}")
    ranks = sorted({p['rank'] for p in tab114})
    print("ranks in standard tab:", ranks)


if __name__ == "__main__":
    main()
