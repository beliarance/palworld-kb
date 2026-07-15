#!/usr/bin/env python3
"""Собирает автономный web/palworld_kb_standalone.html — один файл со вшитыми данными.

Открывается двойным кликом на любой машине (Windows/Mac/Linux), без сервера и Python.
Перезапускать после изменения data/ или web/index.html:
    python3 scripts/build_standalone.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# те же ключи, что DATA_FILES в web/index.html
FILES = {
    "combat": "pals_combat.json", "chart": "type_chart.json", "bosses": "bosses.json",
    "breeding": "breeding.json", "tiers": "tier_lists.json", "items": "items.json",
    "exp": "expeditions.json", "skills": "active_skills.json", "passives": "passives.json",
    "loc": "pal_locations.json", "res": "resource_nodes.json", "idx": "index.json",
    "bb": "base_building.json", "regions": "regions.json",
}


def js_safe(s):
    # чтобы </script> внутри данных не разорвал тег
    return s.replace("</", "<\\/")


def main():
    payload = {k: json.loads((DATA / f).read_text()) for k, f in FILES.items()}
    csv_text = (DATA / "palworld_pals.csv").read_text()
    blob = ("<script>window.EMBEDDED_DATA=" + js_safe(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
            + ";window.EMBEDDED_CSV=" + js_safe(json.dumps(csv_text, ensure_ascii=False)) + ";</script>")
    html = (ROOT / "web" / "index.html").read_text()
    marker = "<script>\n\"use strict\";"
    assert marker in html, "не нашёл главный <script> в web/index.html"
    out = html.replace(marker, blob + "\n" + marker)
    dest = ROOT / "web" / "palworld_kb_standalone.html"
    dest.write_text(out)
    print(f"{dest} — {dest.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
