#!/usr/bin/env python3
"""Build data/breeding.json from the paldb.cc parse (fetch_breeding.py).

Usage:
  python3 fetch_breeding.py > parsed.json   # or --html data/raw/paldb_breeding.html
  python3 build_breeding_json.py parsed.json

Validates every name against data/palworld_pals.csv (canonical 1.0 name list)
and refuses to write if any name mismatches.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FETCHED = "2026-07-14"

FORMULA = (
    "Every pal species has a hidden integer CombiRank. When two pals of "
    "opposite gender breed, the game computes target = floor((rank_parentA + "
    "rank_parentB + 1) / 2) and the child species is the pal in the generic "
    "breeding pool whose CombiRank is closest to that target. If two species "
    "are exactly equidistant from the target, the tie is broken by the lower "
    "internal paldex index (the pal that appears earlier in the game's "
    "internal species list wins). Parent order does not matter. Special "
    "combos override the formula entirely: a listed parent pair always "
    "produces its fixed child, and pals that only appear as special-combo "
    "children (elemental/regional variants, legendaries, and other excluded "
    "species) can never result from the rank formula."
)

def main(parsed_path):
    parsed = json.load(open(parsed_path))
    ranks, combos = parsed["combi_ranks"], parsed["special_combos"]

    canonical = {r["Name"] for r in
                 csv.DictReader(open(ROOT / "data" / "palworld_pals.csv"))}
    used = set(ranks) | {c[k] for c in combos
                         for k in ("parent_a", "parent_b", "child")}
    bad = used - canonical
    if bad:
        sys.exit(f"names not in canonical CSV, aborting: {sorted(bad)}")
    missing = canonical - set(ranks)

    self_pairs = [c for c in combos if c["parent_a"] == c["parent_b"]]
    cross = len(combos) - len(self_pairs)

    out = {
        "game_version": "1.0",
        "updated": FETCHED,
        "formula": FORMULA,
        "combi_ranks": dict(sorted(ranks.items())),
        "special_combos": combos,
        "same_species_note": ("breeding two pals of the same species always "
                              "yields that species"),
        "notes": [
            "Parents are order-insensitive: A+B and B+A give the same child.",
            "Breeding requires one male and one female parent; which parent "
            "is which gender does not affect the child species.",
            f"special_combos contains all {len(combos)} 'Breed Unique' rows "
            f"from paldb.cc for 1.0: {cross} fixed cross-species recipes plus "
            f"{len(self_pairs)} self-pair rows (X+X=X) marking the "
            "28 species obtainable in breeding ONLY by pairing two of the "
            "same species (legendaries, Slime/Cave Bat crossover pals, some "
            "variants).",
            "Elemental/regional variant pals and special-combo-only children "
            "are excluded from the generic rank pool: the formula can never "
            "produce them; use their special combo or same-species pairing.",
            "CombiRank range in 1.0 is 10 (Xenolord) to 3100 (the eleven "
            "crossover/Yakushima pals such as Green Slime and Cave Bat, "
            "which share rank 3100); Chikipi is 3080.",
            "Breeding combos were rebalanced in 1.0 vs early access; ranks "
            "here were scraped from paldb.cc after the 1.0 release and its "
            "pal list matches the 1.0 paldex (299 pals) exactly.",
        ],
        "gaps": [
            "Tie-break rule has conflicting documentation: palworld.wiki.gg "
            "says the lower internal index wins on exact CombiRank ties, "
            "while one 1.0-era aggregator claims ties resolve to the higher "
            "CombiRank; not independently verified in-game for 1.0.",
            "Eleven crossover pals share CombiRank 3100, so formula results "
            "among them depend entirely on the tie-break rule / their "
            "exclusion from the generic pool.",
            "paldb.cc does not print an explicit game-version stamp on the "
            "Breeding_Farm page; 1.0 provenance is inferred from its exact "
            "match with the 299-pal 1.0 paldex and 1.0-only species.",
        ],
        "sources": [
            {"url": "https://paldb.cc/en/Breeding_Farm",
             "what": ("full CombiRank table for all 299 pals ('Breed Combi' "
                      "tab) and all 164 special/unique breeding combinations "
                      "('Breed Unique' tab); raw HTML kept at "
                      "data/raw/paldb_breeding.html"),
             "fetched": FETCHED},
            {"url": "https://palworld.wiki.gg/wiki/Breeding",
             "what": ("exact formula wording child = floor((A + B + 1) / 2), "
                      "tie-break 'lowest index number is selected', gender "
                      "requirement, excluded/same-species-only pals"),
             "fetched": FETCHED},
            {"url": "https://palworld.ludbase.com/en/tools/breeding/",
             "what": ("1.0 confirmation of the floor((rankA + rankB + 1) / 2) "
                      "formula and of ~135 special override combinations"),
             "fetched": FETCHED},
            {"url": "https://advancecalchub.app/blog/palworld-breeding-guide-best-pals",
             "what": ("gender requirement and parent order-insensitivity "
                      "(pre-1.0 era page; used only for mechanics, not ranks)"),
             "fetched": FETCHED},
        ],
    }
    dest = ROOT / "data" / "breeding.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {dest}: {len(ranks)}/{len(canonical)} ranks "
          f"(missing: {sorted(missing) or 'none'}), {len(combos)} combos")


if __name__ == "__main__":
    main(sys.argv[1])
