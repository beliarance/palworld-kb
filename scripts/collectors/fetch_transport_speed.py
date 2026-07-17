#!/usr/bin/env python3
"""Добавляет стат `transport_speed` в pals_combat.json со страницы paldb.cc/en/Transporting.

Transport Speed — отдельный от Run Speed стат: скорость пала при ПЕРЕНОСКЕ груза на базе.
Уровень Transporting = сколько несёт за раз (carry), скорость переноски = отдельно.
Таблица paldb: строка пала = `<a href="Name">Name</a> ... <td>LEVEL<td>RUN<td>TRANSPORT_SPEED<tr>`.

Запуск: python3 scripts/collectors/fetch_transport_speed.py
Не найденное честно пропускается (поле не пишется).
"""

import html as htmllib
import json
import re
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0 (palworld-kb collector)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(page):
    """{имя пала: {level, run, transport_speed}} из таблицы Transporting."""
    out = {}
    # строка: href="Name"> [<img>] Name </a> [<img icons>]* <td>LVL<td>RUN<td>TS<tr>
    pat = re.compile(
        r'href="[^"]+"[^>]*>(?:<img[^>]*>)?\s*([^<]+?)\s*</a>'
        r'(?:\s*<img[^>]*>)*\s*<td>(\d+)<td>(\d+)<td>(\d+)<tr>')
    for m in pat.finditer(page):
        name = htmllib.unescape(m.group(1)).strip()
        out[name] = {"level": int(m.group(2)), "run": int(m.group(3)),
                     "transport_speed": int(m.group(4))}
    return out


def main():
    page = fetch("https://paldb.cc/en/Transporting")
    table = parse(page)
    combat = json.loads((DATA / "pals_combat.json").read_text())
    by = {p["name"]: p for p in combat}
    added = missing = 0
    unmatched = []
    for name, row in table.items():
        p = by.get(name)
        if not p:
            unmatched.append(name)
            continue
        p["transport_speed"] = row["transport_speed"]
        added += 1
    for p in combat:  # у нетранспортных палов стата нет — оставляем null, чтобы явно
        p.setdefault("transport_speed", None)
    (DATA / "pals_combat.json").write_text(json.dumps(combat, ensure_ascii=False, indent=1))
    print(f"transport_speed: записано {added}, в таблице {len(table)} строк")
    if unmatched:
        print(f"не сматчено ({len(unmatched)}): {', '.join(unmatched[:15])}")


if __name__ == "__main__":
    main()
