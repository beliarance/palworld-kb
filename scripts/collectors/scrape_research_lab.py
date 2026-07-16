#!/usr/bin/env python3
"""
Collector: Pal Labor Research Lab research effects (Palworld 1.0).

paldb.cc exposes the COMPLETE research list on the facility page
    https://paldb.cc/en/Pal_Labor_Research_Laboratory
(168 research projects in 1.0). Each project is a `card itemPopup` block with a
title, an effect line (e.g. "Work Speed for Mining 10%") and a Technology-point
cost. The same projects are ALSO cross-listed on each Work Suitability page's
"Research" tab (https://paldb.cc/en/<Suitability>), split by which suitability
tree unlocks them; parsing those and summing double-counts nothing only if you
dedupe, so we treat the single facility page as canonical.

This script downloads the facility page, parses every research card, groups them
into effect families, and reports the cumulative maximum bonus per family
(sum of all tiers). Research effects are permanent and account-wide (apply to
all of the player's bases). Confirmed vs palworld.wiki.gg / game8, 2026-07-16.

Usage:
    python3 scripts/collectors/scrape_research_lab.py            # parse cached HTML in $RL_CACHE (default .)
    python3 scripts/collectors/scrape_research_lab.py --fetch    # (re)download the page first

Output: prints a per-family table and writes research_lab_parsed.json to $RL_CACHE.
"""
import re
import html
import json
import os
import sys
import urllib.request

CANON_SLUG = "Pal_Labor_Research_Laboratory"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
CACHE = os.environ.get("RL_CACHE", ".")


def fetch(slug):
    url = "https://paldb.cc/en/%s" % slug
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    with open(os.path.join(CACHE, "paldb_%s.html" % slug), "w", encoding="utf-8") as f:
        f.write(data)
    return data


def load(slug):
    return open(os.path.join(CACHE, "paldb_%s.html" % slug),
               encoding="utf-8", errors="ignore").read()


def parse_cards(page):
    cards = []
    for part in page.split('<div class="card itemPopup">')[1:]:
        m_name = re.search(r'font-size: x-large;[^>]*>([^<]+)</div>', part)
        m_req = re.search(r'class="me-auto"[^>]*>([^<]+)</span>', part)
        m_body = re.search(r'card-body py-2">(.*?)</div>', part, re.S)
        if not m_body:
            continue
        eff = re.sub(r'<[^>]+>', ' ', m_body.group(1))
        eff = re.sub(r'\s+', ' ', html.unescape(eff)).strip()
        m_pct = re.search(r'([+-]?\d+)\s*%', eff)
        m_cost = re.search(r'T_icon_status_05\.webp"[^>]*>\s*</div>\s*<div>(\d+)</div>', part)
        cards.append({
            "name": html.unescape(m_name.group(1)).strip() if m_name else None,
            "requirement": html.unescape(m_req.group(1)).strip() if m_req else None,
            "effect_text": eff,
            "pct": int(m_pct.group(1)) if m_pct else None,
            "tech_point_cost": int(m_cost.group(1)) if m_cost else None,
        })
    return cards


def family_key(effect_text):
    # Collapse the numeric magnitude so tiers of the same effect group together.
    return re.sub(r'[+-]?\d+%?', '#', effect_text).strip()


def main():
    if "--fetch" in sys.argv:
        fetch(CANON_SLUG)
        print("fetched", CANON_SLUG, file=sys.stderr)

    page = load(CANON_SLUG)
    cards = parse_cards(page)

    families = {}
    for c in cards:
        k = family_key(c["effect_text"])
        fam = families.setdefault(k, {"tiers": 0, "cumulative_pct": 0,
                                      "has_pct": False, "entries": []})
        fam["tiers"] += 1
        if c["pct"] is not None:
            fam["cumulative_pct"] += c["pct"]
            fam["has_pct"] = True
        fam["entries"].append(c)

    result = {
        "game_version": "1.0",
        "source": "https://paldb.cc/en/%s" % CANON_SLUG,
        "total_research_projects": len(cards),
        "effects_are_permanent": True,
        "effects_are_account_wide": True,   # apply to ALL bases (wiki.gg / game8)
        "families": families,
    }

    for k in sorted(families):
        f = families[k]
        val = ("%+d%%" % f["cumulative_pct"]) if f["has_pct"] else "(unlock)"
        print("%2d tiers  max=%8s   %s" % (f["tiers"], val, k))
    print("\nTOTAL PROJECTS:", len(cards))

    with open(os.path.join(CACHE, "research_lab_parsed.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    return result


if __name__ == "__main__":
    main()
