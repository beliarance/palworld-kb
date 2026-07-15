#!/usr/bin/env python3
"""Собирает URL иконок предметов с paldb.cc в data/icons.json (карта "items").

Метод: страница-список https://paldb.cc/en/Items содержит ВСЕ предметы разом
в виде <a href="<slug>"><img loading="lazy" src="https://cdn.paldb.cc/...webp">.
Извлекаем пары slug -> icon URL из неё (1 запрос вместо ~1200).
Для слогов, которых на списке не оказалось, — fallback: тянем отдельные
страницы https://paldb.cc/en/<slug> (там иконка ищется по тому же паттерну —
ссылка предмета на самого себя), с паузой 0.25 c.

Имена берутся из data/raw/item_slugs.json (slug -> {name, category});
в icons.json пишутся только предметы, чьи имена есть в data/items.json.

Запуск: python3 scripts/collectors/fetch_item_icons.py [--verify N]
--verify N — проверить N случайных cdn-URL на HTTP 200.

NB: cdn.paldb.cc на части файлов включает hotlink-защиту по Referer —
без заголовка Referer: https://paldb.cc/ такие URL отдают 403,
с ним — 200. При использовании иконок в вебе (обычный <img>) браузер
не шлёт referer на чужой домен при referrerpolicy=no-referrer;
если иконка не грузится — проксировать или скачать локально.
"""

import argparse
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ICONS_PATH = ROOT / "data" / "icons.json"
SLUGS_PATH = ROOT / "data" / "raw" / "item_slugs.json"
ITEMS_PATH = ROOT / "data" / "items.json"
CACHE_PATH = ROOT / "data" / "raw" / "item_icon_urls.json"  # кэш slug -> url (резюмируемость)

LIST_URL = "https://paldb.cc/en/Items"
PAGE_URL = "https://paldb.cc/en/{slug}"
UA = "Mozilla/5.0 (compatible; Pal-KB icon collector; local research)"

# <a ... href="Slug"><img loading="lazy" src="https://cdn.paldb.cc/...webp"
PAIR_RE = re.compile(
    r'href="([^"/?#]+)"><img loading="lazy" '
    r'src="(https://cdn\.paldb\.cc/image/[^"]+\.webp)"'
)


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_pairs(html: str) -> dict:
    """Все пары slug -> icon URL со страницы (первое вхождение выигрывает)."""
    out = {}
    for slug, url in PAIR_RE.findall(html):
        out.setdefault(slug, url)
    return out


def icon_from_item_page(slug: str) -> str | None:
    """Иконка с индивидуальной страницы: ссылка предмета на самого себя."""
    html = http_get(PAGE_URL.format(slug=slug))
    pat = re.compile(
        r'href="%s"><img[^>]*src="(https://cdn\.paldb\.cc/image/[^"]+\.webp)"'
        % re.escape(slug)
    )
    m = pat.search(html)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", type=int, default=0, metavar="N",
                    help="проверить N случайных URL на HTTP 200")
    args = ap.parse_args()

    slugs = json.loads(SLUGS_PATH.read_text())          # slug -> {name, category}
    items = json.loads(ITEMS_PATH.read_text())["items"]
    item_names = {it["name"] for it in items}

    # Кэш (резюмируемость при fallback-обходе страниц)
    cache: dict = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text())

    missing = [s for s in slugs if s not in cache]
    if missing:
        print(f"Fetching listing page {LIST_URL} ...")
        listing = extract_pairs(http_get(LIST_URL))
        print(f"  listing has {len(listing)} slugs")
        for s in missing:
            if s in listing:
                cache[s] = listing[s]
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1))

    # Fallback: индивидуальные страницы
    missing = [s for s in slugs if s not in cache]
    if missing:
        print(f"Fallback: fetching {len(missing)} individual pages ...")
        for i, s in enumerate(missing, 1):
            try:
                url = icon_from_item_page(s)
            except Exception as e:
                print(f"  [{i}/{len(missing)}] {s}: ERROR {e}")
                url = None
            if url:
                cache[s] = url
            if i % 25 == 0 or i == len(missing):
                CACHE_PATH.write_text(
                    json.dumps(cache, ensure_ascii=False, indent=1))
                print(f"  [{i}/{len(missing)}] cached")
            time.sleep(0.25)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1))

    # slug -> name -> items map (только имена, существующие в items.json)
    items_map: dict = {}
    unmatched_names = set(item_names)
    for slug, meta in slugs.items():
        name = meta["name"]
        if name in item_names and slug in cache:
            items_map.setdefault(name, cache[slug])
            unmatched_names.discard(name)

    icons = json.loads(ICONS_PATH.read_text())
    icons["items"] = dict(sorted(items_map.items()))
    ICONS_PATH.write_text(
        json.dumps(icons, ensure_ascii=False, indent=1) + "\n")

    print(f"items.json names: {len(item_names)}; icons written: {len(items_map)}")
    if unmatched_names:
        print(f"WITHOUT icons ({len(unmatched_names)}): "
              f"{sorted(unmatched_names)[:50]}")

    if args.verify:
        sample = random.sample(sorted(items_map.items()),
                               min(args.verify, len(items_map)))
        ok = 0
        for name, url in sample:
            req = urllib.request.Request(
                url, method="HEAD",
                headers={"User-Agent": UA, "Referer": "https://paldb.cc/"})
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    status = r.status
            except Exception as e:
                status = f"ERR {e}"
            good = status == 200
            ok += good
            print(f"  {'OK ' if good else 'FAIL'} {status}  {name}  {url}")
            time.sleep(0.2)
        print(f"verify: {ok}/{len(sample)} HTTP 200")
        return 0 if ok == len(sample) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
