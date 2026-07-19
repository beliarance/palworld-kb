#!/usr/bin/env python3
"""Добавляет swim_speed / swim_dash_speed в pals_combat.json для ПЛАВАТЕЛЬНЫХ маунтов.

Источник — страница пала на paldb.cc, блок статов:
  <div>SwimSpeed</div> ... <div>920</div>
  <div>SwimDashSpeed</div> ... <div>N</div>
SwimDashSpeed = спринт по воде верхом (аналог RideSprintSpeed). Собираем только
mount_type == "swim" (у сухопутных стат есть, но для езды не важен).

Запуск: python3 scripts/collectors/fetch_swim_speed.py
"""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0 (palworld-kb collector)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def stat(page, name):
    m = re.search(rf'<div>{name}</div>.*?<div>(\d+)</div>', page, re.S)
    return int(m.group(1)) if m else None


def main():
    combat = json.loads((DATA / "pals_combat.json").read_text())
    swim = [p for p in combat if p.get("mount_type") == "swim"]
    done = 0
    for p in swim:
        slug = urllib.parse.quote(p["name"].replace(" ", "_"), safe="_'")
        try:
            page = fetch(f"https://paldb.cc/en/{slug}")
        except Exception as e:
            print(f"  {p['name']}: fetch failed ({e})")
            continue
        ss, sd = stat(page, "SwimSpeed"), stat(page, "SwimDashSpeed")
        if ss:
            p["swim_speed"] = ss
        if sd:
            p["swim_dash_speed"] = sd
        done += 1
        print(f"  {p['name']}: swim={ss} dash={sd}")
        time.sleep(0.35)
    (DATA / "pals_combat.json").write_text(json.dumps(combat, ensure_ascii=False, indent=1))
    print(f"\n{done}/{len(swim)} плавательных маунтов → data/pals_combat.json")


if __name__ == "__main__":
    main()
