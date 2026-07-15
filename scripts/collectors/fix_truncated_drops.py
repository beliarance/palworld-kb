#!/usr/bin/env python3
"""Дочинка items.json: заменяет маркеры '...and N more drop sources' полными
списками источников со страниц paldb.cc.

Страница предмета содержит две таблицы:
  - дропы с палов/боссов: строки вида  <prob%> | <Имя> | <кол-во> | <prob%>
  - прочие источники:      строки вида  <Имя предмета> | <кол-во> | <Источник> | <prob%>

Запуск: python3 scripts/collectors/fix_truncated_drops.py [--dry-run]
"""

import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ITEMS = ROOT / "data" / "items.json"
UA = {"User-Agent": "Mozilla/5.0"}
MARKER = re.compile(r"^\.\.\.and \d+ more drop sources?$")


def fetch(slug):
    req = urllib.request.Request(f"https://paldb.cc/en/{slug}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_sources(page, item_name):
    """Return (pal_drops, other_sources) as lists of display strings."""
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pal_drops, others = [], []
    for i, l in enumerate(lines):
        if not re.fullmatch(r"\d{1,3}(?:\.\d+)?%", l) or i < 3:
            continue
        w = lines[i - 3 : i]  # три поля перед процентом
        if w[0] == item_name:
            qty, source = w[1], w[2]
            # служебные кодовые имена источников оставляем как есть — они читаемы
            others.append(f"{source}: x{qty} ({l})")
        elif re.fullmatch(r"\d{1,3}(?:\.\d+)?%|Probability", w[0]) and not re.fullmatch(r"Lv\.?\s*\d+", w[1]):
            name, qty = w[1], w[2]
            pal_drops.append(f"Dropped by {name} x{qty} ({l})")
    return pal_drops, others


def main():
    dry = "--dry-run" in sys.argv
    data = json.loads(ITEMS.read_text())
    slugs = {}
    slug_file = ROOT / "data" / "raw" / "item_slugs.json"
    if slug_file.exists():
        raw = json.loads(slug_file.read_text())
        if isinstance(raw, dict):
            slugs = {v if isinstance(v, str) else k: k for k, v in raw.items()}
    fixed = 0
    for it in data["items"]:
        srcs = it.get("obtained_from") or []
        if not any(MARKER.match(s) for s in srcs):
            continue
        slug = slugs.get(it["name"]) or it["name"].replace(" ", "_").replace("'", "")
        try:
            page = fetch(slug)
        except Exception as e:
            print(f"SKIP {it['name']}: fetch failed ({e})")
            continue
        pal_drops, others = parse_sources(page, it["name"])
        if not pal_drops and not others:
            print(f"SKIP {it['name']}: parsed nothing, keeping as is")
            continue
        kept = [s for s in srcs if not MARKER.match(s) and not s.startswith("Dropped by ")]
        it["obtained_from"] = pal_drops + kept + others
        # dedup, порядок сохраняем
        seen, dedup = set(), []
        for s in it["obtained_from"]:
            if s not in seen:
                seen.add(s)
                dedup.append(s)
        it["obtained_from"] = dedup
        fixed += 1
        print(f"OK   {it['name']}: {len(pal_drops)} pal drops, {len(others)} other sources")
        time.sleep(0.4)
    if not dry:
        note = "2026-07-14: truncated '...and N more' drop lists re-expanded from paldb item pages (fix_truncated_drops.py)."
        if note not in data["notes"]:
            data["notes"].append(note)
        ITEMS.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"\nFixed {fixed} items{' (dry run, not written)' if dry else ''}")


if __name__ == "__main__":
    main()
