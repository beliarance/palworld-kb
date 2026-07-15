#!/usr/bin/env python3
"""Конструктор баз Palworld 1.0.

  python3 scripts/base_planner.py breeding  --slots 50 --tech 76
  python3 scripts/base_planner.py mine-craft --slots 50 --tech 60 --food self

Пресеты: breeding, mine-craft, food, starter.
Опции:
  --slots N            рабочих слотов на базе (по умолчанию 50)
  --tech N             доступный уровень технологий (по умолчанию 60) — здания выбираются по нему
  --food self|shipped  кормовой модуль на месте / еда привозная (по умолчанию self)
  --workforce baseline|passives|max   качество рабочих: дикие ×1.0 / бридовые ×2.2 / 4-пассивки ×2.75
  --farms N            (breeding) фиксировать число брид-ферм вместо авто
  --raw                смету материалов развернуть до сырья (по items.json)

Числа из data/base_building.json (paldb 1.0). Величины, которых нет в данных
(скорость дропа с ранча, циклы плантаций, абсолютная скорость голода), — явные
ДОПУЩЕНИЯ с флагами для подстройки; печатаются в конце.
"""

import argparse
import json
import math
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# скорость работы по уровню навыка 1-10 (paldb, work_speed_by_level)
CRAFT_SPEED = [50, 80, 140, 240, 400, 680, 1100, 1900, 3200, 5400]
FIELD_SPEED = [50, 70, 100, 140, 190, 260, 370, 510, 720, 1000]
QUALITY = {"baseline": 1.0, "passives": 2.2, "max": 2.75}

# доступный металл -> потолок tech (по печам: следующая печь минус 1)
METALS = {
    "ingot": 33,        # Primitive Furnace (10) ... до Improved (34)
    "refined": 43,      # Improved Furnace (34) ... до Electric (44)
    "pal-metal": 57,    # Electric Furnace (44) ... до Gigantic (58)
    "coralum": 65,      # Gigantic Furnace (58) ... до Ancient (66)
    "soralite": 73,     # Ancient Furnace (66), Soralite Ingot tech 66
    "paloxite": 99,     # Paloxite Ingot tech 74+, весь Ancient-тир
}


def load(name):
    with open(DATA / name) as f:
        return json.load(f)


class Planner:
    def __init__(self, args):
        self.args = args
        self.bb = load("base_building.json")
        self.idx = load("index.json")
        self.items = {i["name"]: i for i in load("items.json")["items"]}
        self.structs = {s["name"]: s for s in self.bb["structures"]}
        try:
            self.regions = load("regions.json")["regions"]
        except FileNotFoundError:
            self.regions = {}
        self.buildings = {}   # name -> count
        self.pals = []        # (species, count, role)
        self.assumptions = []
        self.notes = []

    # ---------- выбор зданий по tech ----------
    def best(self, candidates):
        """Лучшее доступное здание из списка (кандидаты от худшего к лучшему)."""
        avail = [c for c in candidates if c in self.structs
                 and (self.structs[c]["tech_level"] or 0) <= self.args.tech]
        return avail[-1] if avail else None

    def add(self, name, count=1):
        if name and count > 0:
            self.buildings[name] = self.buildings.get(name, 0) + count

    def hire(self, species, count, role):
        if count > 0:
            self.pals.append((species, math.ceil(count), role))

    def q(self):
        return QUALITY[self.args.workforce]

    # ---------- общие модули ----------
    def infra(self, slots):
        # кровати/источники: не гонимся за Ancient-тиром — цена/польза (--lux включает топ)
        beds = ["Straw Pal Bed", "Fluffy Pal Bed", "Large Pal Bed", "Pal Pod", "Ancient Pal Pod"]
        springs = ["Hot Spring", "High Quality Hot Spring", "Ancient Hot Spring"]
        if not self.args.lux:
            beds, springs = beds[:2], springs[:2]
        bed = self.best(beds)
        self.add(bed, slots)
        spring = self.best(springs)
        springs = math.ceil(slots / 6)  # вместимость 1-2 пала; ~1 на 6 палов очереди
        self.add(spring, springs)
        self.assumptions.append(f"{spring} x{springs}: ~1 источник на 6 палов (вместимость 1-2, очередь) — подстрой по факту SAN")
        self.add("Feed Box", max(2, slots // 20))
        self.add("Palbox", 1)
        med = self.best(["Medieval Medicine Workbench", "Medicine Workbench", "Electric Medicine Workbench"])
        self.add(med, 1)
        clinic = self.best(["Clinic", "Ancient Clinic"])
        if clinic:
            self.add(clinic, 1)
        self.hire_best("Medicine", 1, 1, "медик (лечит/варит меды)")

    def power(self, heavy=False):
        gen = self.best(["Human-Powered Generator", "Power Generator", "Large Power Generator", "Ancient Power Generator"])
        n = 2 if heavy else 1
        self.add(gen, n)
        if gen != "Human-Powered Generator":
            self.hire_best("Generating_Electricity", 6, n, "электрик")
        acc = self.best(["Accumulator"])
        if acc and heavy:
            self.add(acc, 2)

    def easy_to_get(self, name):
        """Пал ловится в диких зонах вне эндгейма (не World Tree/Sunreach, не бридинг-only)."""
        p = self.idx["pals"].get(name) or {}
        regions = [r for r in (p.get("regions") or [])
                   if not any(z in r for z in ("World Tree", "Sunreach"))]
        return bool(regions)

    def catch_hint(self, name):
        p = self.idx["pals"].get(name) or {}
        regs = [r for r in (p.get("regions") or []) if "World Tree" not in r]
        if regs:
            import re
            base = re.sub(r"\s*\[Lv\.[^\]]*\]$", "", regs[0]).strip()
            c = self.regions.get(regs[0]) or self.regions.get(base)
            return f"ловится: {regs[0]}" + (f" ({c[0]}, {c[1]})" if c else "")
        if p.get("alpha"):
            # у альф координаты уже в строке; для данжевых — вход не документирован
            return f"альфа: {p['alpha'][0].split(' - ')[-1]}"
        via = p.get("get_via") or []
        return via[-1] if via else ""

    TRANS_CAP = {1: 2, 2: 5, 3: 10, 4: 20, 5: 40, 6: 70, 7: 120, 8: 200, 9: 320, 10: 500}

    def hire_transport(self):
        """Транспортники: число от производящих зданий, вид — по пропускной способности (несёт x бег)."""
        prod = sum(c for n, c in self.buildings.items()
                   if (self.structs.get(n, {}).get("workers")
                       or any(k in n for k in ("Plantation", "Ranch", "Mill", "Kitchen", "Furnace",
                                               "Workbench", "Assembly", "Pit", "Site", "Mine", "Quarry", "Farm", "Pot", "Oven"))))
        n = max(2, math.ceil(prod / 3.5))
        best, bi = None, None
        for nm, lv in self.idx["inverted"]["work"].get("Transporting", []):
            p = self.idx["pals"][nm]
            # гружёные ходят ШАГОМ (подтверждено игроком)
            score = self.TRANS_CAP[lv] * (p.get("walk") or 0)
            if not best or score > bi["score"]:
                best, bi = nm, {"score": score, "cap": self.TRANS_CAP[lv], "run": p.get("run"), "walk": p.get("walk")}
        self.hire(best, n, f"транспорт: несёт {bi['cap']}, шаг(гружён) {bi['walk']} / бег {bi['run']} "
                           f"(пропускная {bi['score']//1000}k) — 1 на ~3.5 здания")
        self.assumptions.append(f"Транспорт: {n} палов на {prod} производящих зданий (1 на ~3.5); "
                                f"гружёные ходят шагом (подтверждено игроком)")

    def hire_best(self, task, min_level, count, role):
        """Нанять лучшего по задаче; в роли указать альтернативу попроще (--roster easy меняет их местами)."""
        ranked = self.idx["inverted"]["work"].get(task, [])
        if not ranked:
            return
        top = next((n for n, lv in ranked if lv >= min_level), ranked[0][0])
        easy = next((n for n, lv in ranked if lv >= min_level and self.easy_to_get(n)), None) \
            or next((n for n, lv in ranked if self.easy_to_get(n)), top)
        lv = dict(ranked)
        primary, alt = (easy, top) if self.args.roster == "easy" else (top, easy)
        note = f"{role} ({task} {lv[primary]})"
        if alt != primary:
            tag = "топ" if self.args.roster == "easy" else "проще достать"
            num = (self.idx["pals"].get(alt) or {}).get("number")
            note += f"  | {tag}: {alt}" + (f" (#{num}, {task} {lv[alt]})" if num else "")
        if not self.easy_to_get(primary):
            hint = self.catch_hint(primary)
            if hint:
                note += f"  [{hint}]"
        self.hire(primary, count, note)

    def support_core(self, kinds):
        """Саппорт-палы с базовыми аурами (виды уникальны — альтернатив нет, даём где ловить)."""
        tags = self.idx["inverted"]["partner_tags"]
        for kind, why in kinds:
            for n in tags.get("base_support:" + kind, [])[:1]:
                hint = self.catch_hint(n)
                self.hire(n, 1, f"саппорт: {why}" + (f"  [{hint}]" if hint else ""))

    def food_module(self, roster_slots):
        """Кормовой модуль: салаты (томат+латук) или ягоды на низком tech."""
        appetite = 5.0  # средний FoodAmount по типичному ростеру
        fa = self.bb["pal_food_amount"]
        avg = sum(v for v in fa.values() if v) / max(1, len([v for v in fa.values() if v]))
        demand = roster_slots * avg  # в FoodAmount-единицах
        salad_ok = self.args.tech >= (self.structs.get("Tomato Plantation", {}).get("tech_level") or 99)
        if salad_ok:
            station = self.best(["Cooking Pot", "Electric Kitchen", "Large-Scale Stone Oven", "Ancient Kitchen"])
            plant_pairs = max(1, math.ceil(demand / (self.args.plant_yield * 1.5)))
            self.add("Tomato Plantation", plant_pairs)
            self.add("Lettuce Plantation", plant_pairs)
            self.add(station, 1)
            self.hire_best("Kindling", 3, 1, "ЕДА: повар салатов")
            n_trio = math.ceil(plant_pairs * 2 / (self.args.plants_per_worker * self.q()))
            self.hire_best("Planting", 3, n_trio, "ЕДА: посадка томатов/латука")
            self.hire_best("Watering", 3, n_trio, "ЕДА: полив томатов/латука")
            self.hire_best("Gathering", 3, n_trio, "ЕДА: сбор томатов/латука")
            self.notes.append(f"ЕДА (self): Salad (сытость 84, SAN +11, work speed +30 на 600с) — "
                              f"{plant_pairs}x Tomato + {plant_pairs}x Lettuce Plantation, повар на {station}")
        else:
            n = max(2, math.ceil(demand / self.args.plant_yield))
            self.add("Berry Plantation", n)
            self.add("Campfire", 1)
            self.hire_best("Kindling", 2, 1, "ЕДА: жарка ягод")
            self.hire_best("Planting", 2, 1, "ЕДА: ягодные плантации")
            self.hire_best("Watering", 2, 1, "ЕДА: полив ягод")
            self.notes.append(f"ЕДА (self): Baked Berries ({n}x Berry Plantation; низкий tech — "
                              f"апгрейдись до Salad при tech 25)")
        self.assumptions.append(
            f"Спрос на еду: {roster_slots} палов x средний аппетит {avg:.1f} = {demand:.0f} FoodAmount-ед.; "
            f"выработка плантации принята {self.args.plant_yield}/час (--plant-yield)")

    def plant_crew(self, plantations):
        """Штат на N плантаций: посадка+полив+сбор."""
        per = self.args.plants_per_worker * self.q()
        n = math.ceil(plantations / per)
        self.hire_best("Planting", 3, n, "посадка")
        self.hire_best("Watering", 3, n, "полив")
        self.hire_best("Gathering", 3, n, "сбор")
        self.assumptions.append(
            f"Штат плантаций: 1 троица (посадка/полив/сбор) на {per:.0f} плантаций "
            f"(--plants-per-worker {self.args.plants_per_worker} x качество {self.q()})")
        return 3 * n

    # ---------- пресеты ----------
    def breeding_staff_for(self, farms):
        """Подсчёт голов тортовой линии на `farms` ферм (без найма). Возвращает словарь."""
        a = self.args
        interval = a.egg_interval or self.bb["rates"]["breeding_egg_interval_minutes"]
        cakes_h = farms * 60 / interval * a.egg_boost
        cake = a.cake
        eggs_per_cake = 2 if cake == "Vegetable Cake" else 1
        # цепочка по рецепту выбранного торта (как в food-пресете)
        PLANTS = {"Red Berries": "Berry Plantation", "Wheat": "Wheat Plantation",
                  "Tomato": "Tomato Plantation", "Lettuce": "Lettuce Plantation",
                  "Potato": "Potato Plantation", "Carrot": "Carrot Plantation", "Onion": "Onion Plantation"}
        ranch_map = self.idx["inverted"]["ranch_produce"]
        plants, ranch_prod, imports, crafts = {}, {}, {}, {}

        def expand(name, per_hour, depth=0):
            if name in PLANTS:
                plants[name] = plants.get(name, 0) + per_hour
            elif name in ranch_map:
                ranch_prod[name] = ranch_prod.get(name, 0) + per_hour
            elif depth < 5 and self.items.get(name, {}).get("recipe"):
                crafts[name] = crafts.get(name, 0) + per_hour
                for m, q in self.items[name]["recipe"]["materials"].items():
                    expand(m, q * per_hour, depth + 1)
            else:
                imports[name] = imports.get(name, 0) + per_hour

        for m, q in (self.items.get(cake, {}).get("recipe") or {"materials": {}})["materials"].items():
            expand(m, q * cakes_h)
        rr = a.ranch_rate * self.q()
        ranch = {ranch_map[p][0]: math.ceil(v / rr) for p, v in ranch_prod.items()}
        plants_n = {c: math.ceil(v / a.plant_yield) for c, v in plants.items()}
        trio = 3 * math.ceil(sum(plants_n.values()) / (a.plants_per_worker * self.q())) if plants_n else 0
        ops = cakes_h + sum(crafts.values()) - crafts.get("Flour", 0)
        cooks = max(1, math.ceil(ops / (a.cook_rate * self.q())))
        mills = max(1, math.ceil(crafts.get("Flour", 0) / 60)) if crafts.get("Flour") else 0
        heads = 2 * farms + sum(ranch.values()) + trio + cooks + mills
        return {"cakes_h": cakes_h, "eggs_h": cakes_h * eggs_per_cake, "ranch": ranch,
                "ranch_prod": ranch_prod, "plants_n": plants_n, "PLANTS": PLANTS,
                "imports": imports, "trio": trio, "cooks": cooks, "mills": mills, "heads": heads}

    def preset_breeding(self):
        a = self.args
        hatchery = a.tech >= 76 and "Ancient Hatchery" in self.structs
        farm_name = "Ancient Hatchery" if hatchery else "Breeding Farm"
        overhead = 8 + 1 + 2 + 2  # саппорт 8 + медик + транспорт 2 + электрики/прочее
        food_slots = 4 if a.food == "self" else 0
        budget = a.slots - overhead - food_slots
        # решатель: максимум ферм, чья линия влезает в бюджет слотов
        farms = a.farms
        if not farms:
            farms = 1
            while farms < 40 and self.breeding_staff_for(farms + 1)["heads"] <= budget:
                farms += 1
        line = self.breeding_staff_for(farms)

        support_kinds = [("egg_speed", "яйца +20~50%"), ("base_defense", "ПВО базы от рейдов")]
        if a.incubation > 0:
            support_kinds.append(("incubation", "инкубация -20~40%"))
        else:
            self.notes.append("Инкубация мгновенная (настройка мира = 0): инкубаторы и Dynamoff не нужны — слот сэкономлен")
        self.support_core(support_kinds + [("crop_growth", "рост культур +50~70%"), ("crop_yield", "урожай +18~35%"),
                           ("sanity_save", "SAN базы -10~15% утечка"),
                           ("suitability:Watering", "+1 Watering всем"),
                           ("suitability:Planting", "+1 Planting всем")])
        self.hire("Woolipop Terra", 1, "саппорт: голод базы -15~25% + Caramel Cotton Candy на ранче")

        self.add(farm_name, farms)
        self.hire("(пары родителей)", 2 * farms, f"в {farm_name} x{farms}")
        rm = self.idx["inverted"]["ranch_produce"]
        for sp, n in line["ranch"].items():
            prod = next((p for p in line["ranch_prod"] if rm[p][0] == sp), "?")
            self.hire(sp, n, f"ранч: {prod} ({line['ranch_prod'].get(prod, 0):.0f}/час)")
        self.add("Ranch", math.ceil(sum(line["ranch"].values()) / 4))
        for crop, n in line["plants_n"].items():
            pl = self.best([line["PLANTS"][crop]])
            if pl:
                self.add(pl, n)
        for name, per_h in line["imports"].items():
            self.notes.append(f"⚠ привозное для торта «{a.cake}»: {name} x{per_h:.0f}/час")
        if line["mills"]:
            self.add("Mill", line["mills"])
            self.hire_best("Watering", 4, line["mills"], "мельница")
        cake_station = (self.items.get(a.cake, {}).get("recipe") or {}).get("station")
        kitchen = cake_station if cake_station in self.structs and             (self.structs[cake_station]["tech_level"] or 0) <= a.tech else             self.best(["Cooking Pot", "Electric Kitchen", "Large-Scale Stone Oven", "Ancient Kitchen"])
        self.add(kitchen, line["cooks"])
        self.hire_best("Kindling", 4, line["cooks"], f"повар тортов ({a.cake})")
        n_trio = line["trio"] // 3
        self.hire_best("Planting", 3, n_trio, "посадка")
        self.hire_best("Watering", 3, n_trio, "полив")
        self.hire_best("Gathering", 3, n_trio, "сбор")
        self.hire_transport()
        if a.incubation > 0 and not hatchery:
            inc = self.best(["Egg Incubator", "Electric Egg Incubator", "Large Egg Incubator",
                             "Large-Scale Electric Egg Incubator"])
            if inc:
                n_inc = min(math.ceil(farms * 2 * a.incubation), 12)
                self.add(inc, n_inc)
                self.assumptions.append(f"Инкубаторы: {n_inc} = фермы x2 x множитель мира {a.incubation} "
                                        "(точное время инкубации по типам яиц в данных нет)")
        if a.food == "self":
            self.food_module(a.slots)
        else:
            self.notes.append("Еда привозная (--food shipped): вози Salad/Pizza guild chest'ом")
        self.infra(a.slots)
        if hatchery or (kitchen and self.structs.get(kitchen, {}).get("power")):
            self.power(heavy=hatchery)

        self.notes.append(f"{farm_name} x{farms}: ~{line['eggs_h']:.0f} яиц/час = {line['eggs_h']*24:.0f}/сутки, тортов {line['cakes_h']:.0f}/час "
                          f"при полном снабжении тортами (x буст {a.egg_boost} (1.0 = торты лимитируют, Braloha без простоев))"
                          + (" (авто-инкубация, 10 слотов яиц)" if hatchery else ""))
        if hatchery:
            self.notes.append("⚠ Ancient Hatchery: скорость производства яиц принята как у обычной фермы "
                              f"({a.egg_interval or 5} мин/яйцо). Гайды говорят про '~10 сек/цикл' (PRELIMINARY) — "
                              "если это про кладку, а не инкубацию, спрос на торты кратно выше. "
                              "Замерь в игре и задай --egg-interval")
        self.notes.append("Vegetable Cake удваивает яйца за цикл; Special Cake — для стакания пассивок")
        m = self.breeding_staff_for(farms + 1)["heads"] - line["heads"]
        self.notes.append(f"Масштабирование: +1 ферма = +12 яиц/час, но +{m} голов персонала — "
                          f"на этой базе потолок {farms} ферм; больше = вторая брид-база")
        self.notes.append("В пати при сборе яиц: Broncherry Aqua (45~55% альфа-яйца) + Grintale (50~75% лишнее яйцо)")
        self.assumptions.append(f"Ранч: {a.ranch_rate} дропов/час на пала (--ranch-rate) x качество; "
                                f"кухня: {a.cook_rate} тортов/час на повара (--cook-rate); "
                                f"яйцо {a.egg_interval or 5} мин x буст Braloha {a.egg_boost} (--egg-interval/--egg-boost)")

    def preset_mine_craft(self):
        a = self.args
        # самообеспечение сырьём: placeable-станции добычи (по 1 на базу)
        sites = []
        # ВНИМАНИЕ: "Mine"/"Electric Mine"/"Ice Mine" — ловушки (Defenses), не добыча!
        # в игре можно поставить по 1 КАЖДОГО типа — добавляем все доступные по tech
        # семьи с одинаковым продуктом — только лучшая (Ore I/II дают одно и то же);
        # Logging I (Wood) и II (Hardwood) — разные продукты, обе
        SITE_FAMS = [["Stone Pit"], ["Logging Site"], ["Logging Site II"],
                     ["Ore Mining Site", "Ore Mining Site II"],
                     ["Coal Mine"], ["Sulfur Mine"], ["Pure Quartz Quarry"],
                     ["Hexolite Quartz Mine"], ["Soralite Quarry"]]
        for fam in SITE_FAMS:
            m = self.best(fam)
            if m:
                self.add(m, 1)
                sites.append(m)
        if self.best(["Ore Mining Site", "Ore Mining Site II"]) == "Ore Mining Site II":
            self.notes.append("Ore Mining Site I даёт ту же руду — можно доставить для второго потока, если есть слоты")
        if a.tech >= 78 and "Ancient Material Synthesizer" in self.structs:
            self.add("Ancient Material Synthesizer", 1)
            self.hire_best("Mining", 6, 1, "Ancient Material Synthesizer (производит ВСЕ виды дерева и руды, 1 пал)")
            self.notes.append("Ancient Material Synthesizer (tech 78): все виды дерева/руды с одного здания — "
                              "потенциально заменяет отдельные шахты (что именно покрывает — проверь в игре)")
        ext = self.best(["Crude Oil Extractor", "High-Pressure Crude Oil Extractor"])
        if ext:
            self.add(ext, 1)
            self.notes.append(f"{ext}: работает БЕЗ палов, только электричество "
                              f"({self.structs[ext].get('energy_per_sec')}/с)"
                              + ("; ставится в любой точке" if "High-Pressure" in ext else "; нужна нефтяная точка"))
        self.notes.append(f"Добыча ({len(sites)} станций, по 1 на базу): {', '.join(sites)}")
        self.support_core([("suitability:Mining", "+1 Mining всем (Tetroise)"),
                           ("base_defense", "ПВО базы от рейдов (Panthalus)"),
                           ("suitability:Handiwork", "+1 Handiwork всем (Ribbuny)"),
                           ("suitability:Transporting", "+1 Transport всем (Wumpo)"),
                           ("sanity_save", "SAN базы (Shroomer Noct)")])
        mining_sites = [x for x in sites if self.structs[x].get("workers") == "Mining"]
        hand_sites = [x for x in sites if x not in mining_sites]
        if hand_sites:
            self.hire_best("Handiwork", 5, max(1, round(len(hand_sites) * 0.8 / self.q())),
                           f"добыча (Handiwork): {'/'.join(hand_sites)}")
        if mining_sites:
            self.hire_best("Mining", 6, max(1, round(len(mining_sites) * 0.8 / self.q())),
                           f"добыча (Mining): {'/'.join(mining_sites)}")
        self.hire_best("Mining", 6, max(1, round(2 / self.q())), "шахтёр (рудные точки на базе, если есть)")
        furn = self.best(["Primitive Furnace", "Improved Furnace", "Electric Furnace", "Gigantic Furnace", "Ancient Furnace"])
        self.add(furn, 2)
        self.hire_best("Kindling", 6, 2, "печи")
        if a.tech >= 67 and "Ancient Workbench" in self.structs:
            self.add("Ancient Workbench", 2)
            self.hire_best("Medicine", 6, 1, "Ancient Workbench (требует Handiwork И Medicine 6+)")
            self.notes.append("Ancient Workbench (tech 67, 2000⚡/с) x2: крафтит ВСЁ включая материалы "
                              "(Polymer/Computer/AI Core) — заменяет production/weapon/sphere линии. "
                              "Требует палов с Handiwork И Medicine Production 6+ (Handiwork-ядро уже в составе)")
        else:
            self.add(self.best(["Production Assembly Line", "Production Assembly Line II", "Advanced Workshop"]), 1)
            for fam in [["Weapon Workbench", "Weapon Assembly Line", "Weapon Assembly Line II", "Advanced Weapon Assembly Line"],
                        ["Sphere Workbench", "Sphere Assembly Line", "Sphere Assembly Line II", "Advanced Sphere Assembly Line"]]:
                s = self.best(fam)
                if s:
                    self.add(s, 1)
        n_hands = max(4, round(10 / self.q()))
        self.hire_best("Handiwork", 6, n_hands, "сборочные линии/верстаки")
        # крафт-ранч: пал-материалы для компонентов (Computer/AI Core/Cement/Coolant)
        if a.tech >= 45:
            producers = [("Flambelle", "Flame Organ (Computer, Carbon Fiber, Bio Battery)"),
                         ("Sparkit", "Electric Organ (Computer, AI Core, Bio Battery)"),
                         ("Depresso", "Venom Gland 🌙 ночной, работает 24/7 (AI Core, Solvent, Thermal Core)"),
                         ("Dumud Gild", "High Quality Pal Oil — Farming 4, x4 к скорости Dumud (Polymer, Circuit Board)"),
                         ("Kelpsea", "Aquatic Pal Fluids (Cement, Cryogenic Coolant)"),
                         ("Foxcicle", "Ice Organ — Farming 3 (Cryogenic Coolant)")]
        else:
            producers = [("Surfent", "Leather (броня)"), ("Cremis", "Wool (Cloth)"),
                         ("Sootseer", "Bone 🌙 ночной, Farming 2 (Cement)"),
                         ("Kelpsea", "Aquatic Pal Fluids (Cement)"), ("Foxcicle", "Ice Organ — Farming 3 (Coolant)")]
        for sp, why in producers:
            self.hire(sp, 1, f"крафт-ранч: {why}")
        self.add("Ranch", -(-len(producers) // 4))
        self.notes.append("Крафт-ранч: пал-материалы для компонентов на месте; масштабируй +1 пала на узкое место "
                          "(обычно Flame/Electric Organ под Computer). 🌙 = ночной, работает без сна; "
                          "ДОПУЩЕНИЕ: скорость ранча ~ уровню Farming")
        self.hire("Ribbuny Botan", 1, "оружейный верстак (+200~400% на нём)")
        self.hire("Anubis", 2, "верстаки (Handiwork 6) — пара с Sekhmet")
        self.hire("Sekhmet", 1, "буст Anubis +20~40% и себе +30~60% на верстаках")
        self.hire_transport()
        cool = self.best(["Cooler Box", "Refrigerator"])
        if cool:
            self.add(cool, 1)
            self.hire_best("Cooling", 3, 1, "холодильник")
        if a.food == "self":
            self.food_module(a.slots)
            self.plant_crew(self.buildings.get("Tomato Plantation", 0) + self.buildings.get("Lettuce Plantation", 0)
                            + self.buildings.get("Berry Plantation", 0))
        self.infra(a.slots)
        self.power(heavy=True)
        self.notes.append("Placeable-шахты лимитированы 1 шт каждого типа на базу — потому майнинг+крафт на одной базе эффективнее")

    def preset_food(self):
        """Еда-хаб под конкретное блюдо: --dish "Pizza" --dish-rate 30 (блюд/час)."""
        a = self.args
        dish = a.dish or "Salad"
        foods = {f["name"]: f for f in self.bb["foods"]}
        fd = foods.get(dish)
        it = self.items.get(dish)
        if not fd or not it or not it.get("recipe"):
            sys.exit(f"Блюдо '{dish}' не найдено или без рецепта. Варианты: " +
                     ", ".join(sorted(n for n, f in foods.items()
                                      if f.get("category") in ("meal", "base_buff", "combat", "breeding")
                                      and self.items.get(n, {}).get("recipe"))))
        rate = a.dish_rate
        buffs = ", ".join(fd.get("buffs") or []) or "без баффов"
        self.notes.append(f"Блюдо: {dish} [{fd.get('category')}] — сытость {fd.get('nutrition')}, "
                          f"SAN +{fd.get('sanity')}, {buffs}; цель {rate} блюд/час")

        PLANTS = {"Red Berries": "Berry Plantation", "Wheat": "Wheat Plantation",
                  "Tomato": "Tomato Plantation", "Lettuce": "Lettuce Plantation",
                  "Potato": "Potato Plantation", "Carrot": "Carrot Plantation", "Onion": "Onion Plantation"}
        ranch_map = self.idx["inverted"]["ranch_produce"]
        need_plants, need_ranch, imports, crafts = {}, {}, {}, {}

        def expand(name, per_hour, depth=0):
            if name in PLANTS:
                need_plants[name] = need_plants.get(name, 0) + per_hour
            elif name in ranch_map:
                need_ranch[name] = need_ranch.get(name, 0) + per_hour
            elif depth < 5 and self.items.get(name, {}).get("recipe"):
                r = self.items[name]["recipe"]
                crafts[name] = crafts.get(name, 0) + per_hour
                for m, q in r["materials"].items():
                    expand(m, q * per_hour, depth + 1)
            else:
                imports[name] = imports.get(name, 0) + per_hour

        for m, q in it["recipe"]["materials"].items():
            expand(m, q * rate)

        for crop, per_h in need_plants.items():
            n = math.ceil(per_h / a.plant_yield)
            pl = self.best([PLANTS[crop]])
            if pl:
                self.add(pl, n)
            else:
                imports[crop] = imports.get(crop, 0) + per_h
        total_pl = sum(self.buildings.get(p, 0) for p in PLANTS.values())
        if total_pl:
            self.plant_crew(total_pl)
            self.support_core([("crop_growth", "Lullu"), ("crop_yield", "Prunelia"),
                               ("suitability:Planting", "+1 Planting"), ("suitability:Watering", "+1 Watering")])
        for prod, per_h in need_ranch.items():
            sp = ranch_map[prod][0]
            self.hire(sp, math.ceil(per_h / (a.ranch_rate * self.q())), f"ранч: {prod} ({per_h:.0f}/час)")
        if need_ranch:
            ranchers = sum(math.ceil(v / (a.ranch_rate * self.q())) for v in need_ranch.values())
            self.add("Ranch", math.ceil(ranchers / 4))
            self.support_core([("suitability:Farming", "+1 Farming всем")])
        if "Wheat" in need_plants or "Flour" in crafts:
            self.add("Mill", max(1, math.ceil(crafts.get("Flour", 0) / 60)))
            self.hire_best("Watering", 4, 1, "мельница")
        station = it["recipe"].get("station")
        if station and station in self.structs:
            ops = sum(crafts.values()) + rate
            n_k = max(1, math.ceil(ops / (a.cook_rate * self.q())))
            self.add(station, n_k)
            self.hire_best("Kindling", 4, n_k, f"повар ({dish} + полуфабрикаты, {ops:.0f} операций/час)")
        for name, per_h in imports.items():
            self.notes.append(f"⚠ привозной ингредиент: {name} x{per_h:.0f}/час (охота/рыбалка/закупка — плантации нет)")
        for name, per_h in crafts.items():
            self.notes.append(f"полуфабрикат: {name} x{per_h:.0f}/час (крафтится на месте)")
        self.hire_transport()
        self.infra(a.slots)
        if self.structs.get(station, {}).get("power"):
            self.power(False)
        self.assumptions.append(f"{a.dish_rate} блюд/час (--dish-rate); плантация {a.plant_yield}/час; "
                                f"ранч {a.ranch_rate}/час; кухня {a.cook_rate} операций/час на повара")

    def preset_starter(self):
        self.args.tech = min(self.args.tech, 20)
        for s, n in [("Palbox", 1), ("Wooden Chest", 3), ("Feed Box", 1), ("Ranch", 1),
                     ("Berry Plantation", 2), ("Wheat Plantation", 1), ("Mill", 1),
                     ("Primitive Furnace", 1), ("Cooking Pot", 1), ("Human-Powered Generator", 1),
                     ("Hot Spring", 2), ("Straw Pal Bed", 15)]:
            if s in self.structs:
                self.add(s, n)
        self.hire("Chikipi", 1, "ранч: яйца"); self.hire("Mozzarina", 1, "ранч: молоко")
        self.hire_best("Kindling", 2, 1, "печь/готовка")
        self.hire_best("Handiwork", 2, 2, "верстаки")
        self.plant_crew(3)
        self.hire_best("Transporting", 2, 2, "переноска")
        self.notes.append("Стартовый сетап из docs/base_setup.md, ~15 палов")

    # ---------- вывод ----------
    def report(self):
        a = self.args
        total_pals = sum(c for _, c, _ in self.pals)
        print(f"═══ База: {a.preset}  |  слоты {a.slots}  |  tech {a.tech}  |  еда: {a.food}  |  рабочие: {a.workforce} (x{self.q()}) ═══\n")
        print("ПАЛЫ".ljust(60) + f"[{total_pals}/{a.slots} слотов]")
        num = lambda s: (self.idx["pals"].get(s) or {}).get("number")
        for sp, c, role in self.pals:
            label = sp + (f" (#{num(sp)})" if num(sp) else "")
            print(f"  {c:>2}x {label:<26} — {role}")
        if total_pals > a.slots:
            print(f"  !! перебор на {total_pals - a.slots} слотов — уменьши --farms или подними --workforce")
        else:
            print(f"  свободно: {a.slots - total_pals} слотов (докинь ферм/рабочих)")
        print("\nЗДАНИЯ И СМЕТА")
        bill = {}
        for b, c in sorted(self.buildings.items()):
            s = self.structs.get(b, {})
            mats = s.get("materials") or {}
            for m, q_ in mats.items():
                bill[m] = bill.get(m, 0) + q_ * c
            mat_s = ", ".join(f"{m} x{q_ * c}" for m, q_ in mats.items())
            pw = " ⚡" if s.get("power") else ""
            print(f"  {c:>2}x {b:<28} (tech {s.get('tech_level', '?')}){pw}  {mat_s}")
        print("\n  ИТОГО материалов:")
        if a.raw:
            raw = {}
            def expand(m, q_, d=0):
                it = self.items.get(m)
                r = it.get("recipe") if it else None
                if r and d < 5:
                    for mm, qq in r["materials"].items():
                        expand(mm, qq * q_, d + 1)
                else:
                    raw[m] = raw.get(m, 0) + q_
            for m, q_ in bill.items():
                expand(m, q_)
            for m, q_ in sorted(raw.items()):
                print(f"    {m}: {q_}")
        else:
            for m, q_ in sorted(bill.items()):
                print(f"    {m}: {q_}   (--raw развернёт до сырья)")
        if self.notes:
            print("\nЗАМЕТКИ")
            for x in self.notes:
                print(f"  • {x}")
        if self.assumptions:
            print("\nДОПУЩЕНИЯ (нет в данных — подстрой флагами)")
            for x in self.assumptions:
                print(f"  ~ {x}")


def main():
    ap = argparse.ArgumentParser(description="Palworld 1.0 base planner")
    ap.add_argument("preset", choices=["breeding", "mine-craft", "food", "starter"])
    ap.add_argument("--slots", type=int, default=50)
    ap.add_argument("--tech", type=int, default=60)
    ap.add_argument("--food", choices=["self", "shipped"], default="self")
    ap.add_argument("--workforce", choices=list(QUALITY), default="baseline")
    ap.add_argument("--farms", type=int, default=None)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--lux", action="store_true", help="топовые кровати/источники (дорогой Ancient-тир)")
    ap.add_argument("--roster", choices=["top", "easy"], default="top",
                    help="top: лучшие палы (+альтернатива попроще); easy: лучшие из легко ловимых (+топ в скобках)")
    ap.add_argument("--metal", choices=list(METALS),
                    help="доступный металл вместо --tech: ingot|refined|pal-metal|coralum|soralite|paloxite")
    ap.add_argument("--extra", default="",
                    help="доп. здания: 'Statue of Power:1,Pal Essence Condenser:1'")
    ap.add_argument("--dish", help="(food) целевое блюдо, например 'Pizza' или 'Cake'")
    ap.add_argument("--dish-rate", type=float, default=30, help="(food) блюд/час")
    ap.add_argument("--egg-interval", type=float, default=None,
                    help="(breeding) минут на яйцо (по умолчанию 5 из данных; для хатчери замерь в игре)")
    ap.add_argument("--cake", default="Cake",
                    choices=["Cake", "Mushroom Cake", "Vegetable Cake", "Extravagant Vegetable Cake", "Special Cake"],
                    help="(breeding) какой торт производить (Vegetable = 2 яйца за цикл)")
    ap.add_argument("--incubation", type=float, default=1,
                    help="(breeding) множитель скорости инкубации из настроек МИРА: 0 = мгновенно (без инкубаторов и Dynamoff)")
    ap.add_argument("--egg-boost", type=float, default=1.0,
                    help="(breeding) 1.0 = тортовая линия под базовую скорость (Braloha лишь убирает простои); "
                         "1.35-1.5 = линия под реализованный буст Braloha (яйца +20~50%%)")
    ap.add_argument("--ranch-rate", type=float, default=12, help="дропов/час на ранч-пала (ДОПУЩЕНИЕ)")
    ap.add_argument("--plant-yield", type=float, default=60, help="единиц урожая/час с плантации (ДОПУЩЕНИЕ)")
    ap.add_argument("--cook-rate", type=float, default=30, help="тортов/час на повара (ДОПУЩЕНИЕ)")
    ap.add_argument("--plants-per-worker", type=float, default=3, help="плантаций на 1 троицу рабочих при baseline")
    args = ap.parse_args()
    if args.metal:
        args.tech = METALS[args.metal]
    pl = Planner(args)
    {"breeding": pl.preset_breeding, "mine-craft": pl.preset_mine_craft,
     "food": pl.preset_food, "starter": pl.preset_starter}[args.preset]()
    if args.metal:
        pl.notes.append(f"Тир зданий по металлу '{args.metal}' -> tech <= {args.tech}")
    for chunk in filter(None, args.extra.split(",")):
        name, _, qty = chunk.partition(":")
        name = name.strip()
        hit = next((s for s in pl.structs if s.lower() == name.lower()), None)
        if hit:
            pl.add(hit, int(qty or 1))
            pl.notes.append(f"Доп. здание по запросу: {hit} x{qty or 1}")
        else:
            pl.notes.append(f"!! Доп. здание '{name}' не найдено в base_building.json")
    pl.report()


if __name__ == "__main__":
    main()
