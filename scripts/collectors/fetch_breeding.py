#!/usr/bin/env python3
"""Fetch and parse Palworld 1.0 breeding data from paldb.cc.

Fetches https://paldb.cc/en/Breeding_Farm (server-side rendered) and parses:
  - "Breed Combi" tab  -> CombiRank per pal
  - "Breed Unique" tab -> special (fixed) breeding combinations

Usage:
  python3 fetch_breeding.py [--html PATH]   # use a saved HTML dump instead of fetching
Outputs JSON to stdout: {"combi_ranks": {...}, "special_combos": [...]}
Raw HTML is cached at data/raw/paldb_breeding.html when fetched.
"""
import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

URL = "https://paldb.cc/en/Breeding_Farm"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "paldb_breeding.html"


def fetch() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(html)
    return html


class TableGrabber(HTMLParser):
    """Collect rows of every <table> as lists of cell texts (anchors joined)."""

    def __init__(self):
        super().__init__()
        self.tables = []          # list of list-of-rows; row = list of cells
        self.anchor_tables = []   # same shape, cell = list of <a> texts
        self._rows = None
        self._arows = None
        self._cells = None
        self._acells = None
        self._buf = None
        self._abuf = None
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._rows, self._arows = [], []
        elif tag == "tr" and self._rows is not None:
            self._cells, self._acells = [], []
        elif tag in ("td", "th") and self._cells is not None:
            self._buf, self._acells_cur = [], []
        elif tag == "a" and self._buf is not None:
            self._in_a = True
            self._abuf = []

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            self._in_a = False
            if self._abuf:
                self._acells_cur.append("".join(self._abuf).strip())
            self._abuf = None
        elif tag in ("td", "th") and self._buf is not None:
            self._cells.append("".join(self._buf).strip())
            self._acells.append(self._acells_cur)
            self._buf = None
        elif tag == "tr" and self._cells is not None:
            self._rows.append(self._cells)
            self._arows.append(self._acells)
            self._cells = self._acells = None
        elif tag == "table" and self._rows is not None:
            self.tables.append(self._rows)
            self.anchor_tables.append(self._arows)
            self._rows = self._arows = None

    def handle_data(self, data):
        if self._buf is not None:
            self._buf.append(data)
        if self._abuf is not None:
            self._abuf.append(data)


def split_tabs(html: str) -> dict:
    """Return {tab_id: html_chunk} for the page's tab panes."""
    chunks = {}
    for m in re.finditer(r'<div id="(\w+)" class="tab-pane[^"]*">', html):
        start = m.end()
        nxt = re.search(r'<div id="\w+" class="tab-pane', html[start:])
        end = start + nxt.start() if nxt else len(html)
        chunks[m.group(1)] = html[start:end]
    return chunks


def parse(html: str):
    tabs = split_tabs(html)
    combi_ranks, special = {}, []

    grab = TableGrabber()
    grab.feed(tabs.get("BreedCombi", ""))
    for table in grab.tables:
        header = [c.lower() for c in table[0]] if table else []
        if not any("combirank" in c for c in header):
            continue
        for row in table[1:]:
            if len(row) >= 2 and re.fullmatch(r"\d+", row[1]):
                combi_ranks[row[0].strip()] = int(row[1])

    grab = TableGrabber()
    grab.feed(tabs.get("BreedUnique", ""))
    for table in grab.anchor_tables:
        for row in table[1:] if table else []:
            # column 1 anchors: [parentA, parentB]; column 2 anchors: [child]
            if len(row) == 2 and len(row[0]) == 2 and len(row[1]) == 1:
                special.append({"parent_a": row[0][0], "parent_b": row[0][1],
                                "child": row[1][0]})
    return combi_ranks, special


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="parse a saved HTML file instead of fetching")
    args = ap.parse_args()
    html = Path(args.html).read_text() if args.html else fetch()
    ranks, special = parse(html)
    json.dump({"combi_ranks": ranks, "special_combos": special},
              sys.stdout, indent=2, ensure_ascii=False)
    print(f"\nparsed {len(ranks)} ranks, {len(special)} special combos",
          file=sys.stderr)


if __name__ == "__main__":
    main()
