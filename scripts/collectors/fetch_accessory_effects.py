#!/usr/bin/env python3
"""Собирает эффекты аксессуаров с paldb.cc в items.json (поле effect).

paldb отдаёт описание предмета в <meta name="description"> (server-rendered).
Запуск: python3 scripts/collectors/fetch_accessory_effects.py [--category accessory]
Не найденные страницы/описания пропускаются честно (effect не пишется).
"""

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0 (palworld-kb collector)"}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def effect_from_page(page):
    # описание — в <meta property="og:description"> (server-rendered)
    m = re.search(r'<meta property="og:description" content="([^"]+)"', page)
    if not m:
        return None
    eff = html.unescape(m.group(1)).strip()
    # paldb клеит предложения без пробела: "...raises Attack.Attack Up Lv. 3"
    eff = re.sub(r"\.(?=[A-Z])", ". ", eff)
    # отрезать хвост-шаблон paldb ("... | Palworld Database" и т.п.)
    eff = re.sub(r"\s*\|\s*Palworld.*$", "", eff)
    return eff or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="accessory")
    ap.add_argument("--sleep", type=float, default=0.4)
    args = ap.parse_args()

    d = json.loads((DATA / "items.json").read_text())
    targets = [i for i in d["items"] if i.get("category") == args.category]
    done = missing = 0
    for it in targets:
        slug = urllib.parse.quote(it["name"].replace(" ", "_"), safe="_'")
        page = fetch(f"https://paldb.cc/en/{slug}")
        eff = effect_from_page(page) if page else None
        if eff:
            it["effect"] = eff
            done += 1
            print(f"  OK  {it['name']}: {eff[:90]}")
        else:
            missing += 1
            print(f"  --  {it['name']}: описание не найдено")
        time.sleep(args.sleep)
    (DATA / "items.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
    print(f"\n{done} effects written, {missing} missing → data/items.json")


if __name__ == "__main__":
    main()
