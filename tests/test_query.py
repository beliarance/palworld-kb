"""Тесты ключевых функций query-слоя. Запуск: python3 -m unittest discover tests"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import query  # noqa: E402


class TestDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = query.load_db()

    def test_loads_all_pals(self):
        self.assertEqual(len(self.db), 299)

    def test_merge_has_both_sides(self):
        anubis = self.db["Anubis"]
        self.assertIn("Ground", anubis["elements"])          # from CSV
        self.assertGreaterEqual(anubis["work"]["Handiwork"], 4)  # CSV work
        self.assertIsInstance(anubis["hp"], int)             # from combat JSON

    def test_find_pal_case_insensitive(self):
        self.assertEqual(query.find_pal(self.db, "anubis")["name"], "Anubis")

    def test_rank_workers_sorted_desc(self):
        col, pals = query.rank_workers(self.db, "mining")
        levels = [p["work"][col] for p in pals]
        self.assertEqual(levels, sorted(levels, reverse=True))
        self.assertTrue(all(v >= 1 for v in levels))


class TestTypeChart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "data" / "type_chart.json") as f:
            cls.chart = json.load(f)["chart"]

    def test_electric_countered_by_ground(self):
        self.assertIn("Ground", query.counters_for(self.chart, "electric"))

    def test_symmetry(self):
        for el, node in self.chart.items():
            for target in node["strong_vs"]:
                self.assertIn(el, self.chart[target]["weak_to"],
                              f"{el} strong_vs {target} but no inverse weak_to")


@unittest.skipUnless((ROOT / "data" / "breeding.json").exists(), "breeding.json not collected yet")
class TestBreeding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ROOT / "data" / "breeding.json") as f:
            cls.br = json.load(f)

    def test_same_species(self):
        child, _ = query.breed_child(self.br, "Anubis", "Anubis")
        self.assertEqual(child, "Anubis")

    def test_special_combo_overrides(self):
        combo = self.br["special_combos"][0]
        child, why = query.breed_child(self.br, combo["parent_a"], combo["parent_b"])
        self.assertEqual(child, combo["child"])
        self.assertIn("special", why)

    def test_rank_formula_returns_known_pal(self):
        ranks = self.br["combi_ranks"]
        names = sorted(ranks)
        if len(names) >= 2:
            child, _ = query.breed_child(self.br, names[0], names[1])
            self.assertIn(child, ranks)


if __name__ == "__main__":
    unittest.main()
