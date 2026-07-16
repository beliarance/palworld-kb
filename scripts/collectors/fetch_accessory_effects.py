#!/usr/bin/env python3
"""Собирает эффекты И источники аксессуаров с paldb.cc в items.json.

Пишет поля:
  effect             — из <meta property="og:description"> страницы предмета
  schematic_sources  — где падает схема "<Name> Schematic" (Treasure Box таблица
                       страницы схемы: сундук/данж + шанс, фикс-точки с координатами)
  drop_sources       — прямые источники самого предмета (если есть на его странице)

Крафт аксессуаров заперт за схемами (у предметов tech_level=None) — колонка
Schematic в Production. Запуск:
  python3 scripts/collectors/fetch_accessory_effects.py [--category accessory]
Не найденное честно пропускается (поле не пишется).
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


def treasure_sources(page, skip_name):
    """Источники из data-секции Treasure Box (заголовок card-title, не навигация)."""
    m = re.search(r'card-title[^>]*>\s*Treasure Box\s*</h5>(.*?)</table>', page, re.S)
    if not m:
        return []
    out = []
    # источник = второй <td> строки: <a>имя</a> + шанс ИЛИ ссылка на карту с координатами
    for sm in re.finditer(
            r'<td><a href="[^"]+">([^<]+)</a>\s*(?:([\d.]+%)|<a href="[^"]*pos=[^"]*">(?:<i[^>]*></i>)?([^<]+)</a>)?',
            m.group(1)):
        name, pct, coords = sm.group(1).strip(), sm.group(2), sm.group(3)
        if name == skip_name or name.endswith("Schematic"):
            continue  # первый td — сам предмет
        src = name + (f" ({pct})" if pct else "") + (f" — {coords.strip()}" if coords else "")
        if src not in out:
            out.append(src)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="accessory")
    ap.add_argument("--sleep", type=float, default=0.35)
    args = ap.parse_args()

    d = json.loads((DATA / "items.json").read_text())
    targets = [i for i in d["items"] if i.get("category") == args.category]
    done = missing = sch_n = 0
    for it in targets:
        slug = urllib.parse.quote(it["name"].replace(" ", "_"), safe="_'")
        page = fetch(f"https://paldb.cc/en/{slug}")
        eff = effect_from_page(page) if page else None
        if eff:
            it["effect"] = eff
            done += 1
        else:
            missing += 1
        if page:
            direct = treasure_sources(page, it["name"])
            if direct:
                it["drop_sources"] = direct
            if f"{it['name']} Schematic" in page:  # крафт заперт за схемой
                time.sleep(args.sleep)
                sp = fetch(f"https://paldb.cc/en/{urllib.parse.quote((it['name'] + ' Schematic').replace(' ', '_'), safe='_' + chr(39))}")
                if sp:
                    srcs = treasure_sources(sp, it["name"] + " Schematic")
                    if srcs:
                        it["schematic_sources"] = srcs
                        sch_n += 1
        print(f"  {it['name']}: eff={'+' if eff else '-'} схема={len(it.get('schematic_sources') or [])} дроп={len(it.get('drop_sources') or [])}")
        time.sleep(args.sleep)
    (DATA / "items.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
    print(f"\n{done} effects, {sch_n} schematic-источников, {missing} без описания → data/items.json")


if __name__ == "__main__":
    main()
