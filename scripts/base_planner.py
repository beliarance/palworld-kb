#!/usr/bin/env python3
"""Конструктор баз Palworld 1.0.

  python3 scripts/base_planner.py breeding  --slots 50 --tech 76
  python3 scripts/base_planner.py mine-craft --slots 50 --tech 60 --food self

Пресеты: breeding, mine-craft, food, starter.
Опции:
  --slots N            рабочих слотов на базе (по умолчанию 50)
  --tech N             доступный уровень технологий (по умолчанию 60) — здания выбираются по нему
  --food self|shipped  кормовой модуль на месте / еда привозная (по умолчанию self)
  --workforce baseline|passives|max   Work Speed рабочих: 70 (дикие) / 154 (+пассивки) / 192 (макс-стек);
                                      база WS 70 растёт от пассивок (Artisan/Serious) и еды
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

    def food_ws(self):
        """Бонус Work Speed от кормёжки базы buff-едой (флэт +N к WS)."""
        if self.args.food_buff <= 0:
            return 0
        # доступность buff-блюда по tech: Salad (+30) с tech 25; ниже — нет буфф-еды
        if self.args.tech >= (self.structs.get("Tomato Plantation", {}).get("tech_level") or 25):
            return self.args.food_buff
        return 0

    def q(self):
        """Эффективный множитель работы = (база 70 × пассивки + бонус еды)/70 × звёзды × ресёрч.
        Звёзды (конденсер): 4★ = +1 ур. работы (ур.8→9 ≈ ×1.68 крафт/×1.41 поле, среднее ×1.55).
        Ресёрч (Pal Labor Research Lab, макс): Work Speed +45% на большинстве работ (×1.45).
        Оговорка: у Gathering/Transporting/Farming ресёрча нет — для ранча/сбора реальный буст меньше."""
        star = 1.55 if self.args.stars else 1.0
        research = 1.45 if self.args.research else 1.0
        return (70 * QUALITY[self.args.workforce] + self.food_ws()) / 70 * star * research

    def garden_mult(self):
        """Множитель садовой тройки = q() × суитабилити-саппорты (Petallia +1 Planting,
        Amione +1 Watering — в брид-пресете; +1 к уровню работы всех палов базы ≈ ×1.35)."""
        return self.q() * 1.35

    def ranch_mult(self):
        """Множитель ранча = q() (звёзды/пассивки/ресёрч) × бонус Ranch Master/handbook.
        Ranch Master (+2 Farming) и Applied Technique Handbook (+1) поднимают уровень Farming
        → выше выработка. При палах с пассивками/max закладываем, что ранч-палы их несут (×1.5)."""
        rm = 1.5 if self.args.workforce != "baseline" else 1.0
        return self.q() * rm

    def plant_yield_eff(self):
        """Выработка грядки/час с учётом ресёрча и yield-саппортов базы.
        Lullu (crop growth) и Prunelia (harvest) — ПАРТНЁРСКИЕ скиллы, их сила растёт от ЗВЁЗД
        конденсации: диапазоны +50~70% / +18~35% = 0★…4★. Тумблер 4★ → верх, иначе низ."""
        growth = 1.70 if self.args.stars else 1.50   # Lullu crop growth +70% (4★) / +50% (0★)
        yld = 1.35 if self.args.stars else 1.18      # Prunelia harvest +35% (4★) / +18% (0★)
        return self.args.plant_yield * growth * yld * (1.5 if self.args.research else 1.0)

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
        springs = max(1, math.ceil(slots / 25))  # SAN падает медленно и восстанавливается быстро; палы ротируются
        self.add(spring, springs)
        self.assumptions.append(f"{spring} x{springs}: ~1 на 25 палов (SAN падает медленно, палы по очереди) — подстрой по факту SAN")
        self.add("Feed Box", max(2, slots // 20))
        self.add("Palbox", 1)
        med = self.best(["Medieval Medicine Workbench", "Medicine Workbench", "Electric Medicine Workbench"])
        self.add(med, 1)
        clinic = self.best(["Clinic", "Ancient Clinic"])
        if clinic:
            self.add(clinic, 1)
        # медика по возможности вешаем на саппорт-пала с навыком Medicine (Petallia/Mycora/Lullu)
        if not self.try_dual("Medicine", 3, "медик"):
            self.hire_best("Medicine", 1, 1, "медик (лечит/варит меды)")

    def power(self, heavy=False):
        gen = self.best(["Human-Powered Generator", "Power Generator", "Large Power Generator", "Ancient Power Generator"])
        n = 2 if heavy else 1
        self.add(gen, n)
        if gen != "Human-Powered Generator":
            # первого электрика по возможности вешаем на саппорта (Dynamoff Elec 6)
            got = self.try_dual("Generating_Electricity", 4, "электрик") if n >= 1 else False
            if n - (1 if got else 0) > 0:
                self.hire_best("Generating_Electricity", 6, n - (1 if got else 0), "электрик")
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
        # рабочие палы с навыком Transporting сами таскают выхлоп в простое — выделенных нужно немного
        n = max(1, math.ceil(prod / 8))
        best, bi = None, None
        for nm, lv in self.idx["inverted"]["work"].get("Transporting", []):
            p = self.idx["pals"][nm]
            # гружёные ходят ШАГОМ (подтверждено игроком)
            score = self.TRANS_CAP[lv] * (p.get("walk") or 0)
            if not best or score > bi["score"]:
                best, bi = nm, {"score": score, "cap": self.TRANS_CAP[lv], "run": p.get("run"), "walk": p.get("walk")}
        self.hire(best, n, f"транспорт: несёт {bi['cap']}, шаг(гружён) {bi['walk']} / бег {bi['run']} "
                           f"(пропускная {bi['score']//1000}k) — добивка к самовывозу")
        self.assumptions.append(f"Транспорт: {n} выделенных на {prod} зданий (1 на ~8). "
                                f"Большинство рабочих палов с навыком Transporting сами носят выхлоп в простое, "
                                f"поэтому выделенных нужно мало — крути, если сундуки далеко от станций")

    def add_plantations(self, plants_n, PLANTS):
        """Ставит плантации; на tech 78+ Ancient Farm заменяет все раздельные (растит любые культуры)."""
        total = sum(plants_n.values())
        if self.args.tech >= 78 and "Ancient Farm" in self.structs and total:
            # древние фермы вместо плантаций, по-культурно: Ancient Farm (Tomato) x2 и т.д.
            n_af = 0
            for crop, n in plants_n.items():
                k = max(1, math.ceil(n / self.args.ancient_farm_yield))
                self.add(f"Ancient Farm ({crop})", k)
                n_af += k
            note = (f"Ancient Farm x{n_af} (по культурам) вместо раздельных плантаций: компактнее, "
                    "4 места, Watering+Planting+Gathering 6+")
            note += (f". Принято ×{self.args.ancient_farm_yield:g} к выработке (калибровка по игроку: "
                     "4 древние фермы кормят 50 палов с избытком; точной цифры в данных нет — --ancient-farm-yield)")
            self.notes.append(note)
            return total
        else:
            for crop, n in plants_n.items():
                pl = self.best([PLANTS[crop]])
                if pl:
                    self.add(pl, n)
        return total

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

    def try_dual(self, task, min_level, label):
        """Навесить вторую роль на уже нанятого саппорт-пала, если у него есть нужный навык.
        Аура работает «while at base», так что саппорт может параллельно работать. Экономит слот."""
        for i, (sp, cnt, role) in enumerate(self.pals):
            if role.startswith("саппорт") and " + " not in role:
                lv = (self.idx["pals"].get(sp) or {}).get("work", {}).get(task, 0)
                if lv >= min_level:
                    self.pals[i] = (sp, cnt, f"{role}  + {label} ({task} {lv})")
                    return True
        return False

    def support_core(self, kinds):
        """Саппорт-палы с базовыми аурами (виды уникальны — альтернатив нет, даём где ловить)."""
        tags = self.idx["inverted"]["partner_tags"]
        for kind, why in kinds:
            for n in tags.get("base_support:" + kind, [])[:1]:
                hint = self.catch_hint(n)
                self.hire(n, 1, f"саппорт: {why}" + (f"  [{hint}]" if hint else ""))

    def roster_appetite(self):
        """Суммарный аппетит уже нанятых палов = Σ count × FoodAmount (стат «сколько еды надо»)."""
        fa = self.bb["pal_food_amount"]
        return sum(c * (fa.get(sp) or 5) for sp, c, _ in self.pals)

    def food_module(self, roster_slots, share_crew=False):
        """Кормовой модуль. Возвращает число кормовых грядок.
        share_crew=True: грядки обслуживает общая тройка базы (не нанимаем свою — брид/еда-базы,
        где Planting/Watering/Gathering-палы уже есть и покрывают ВСЕ плантации)."""
        # спрос = сумма FoodAmount реального ростера (крупные палы едят больше мелких).
        # точной скорости голода в данных нет (gap) — food_per_plot = «аппетит-единиц на грядку»
        appetite = self.roster_appetite()
        # добивка на ещё не нанятых (транспорт/тройка/повар) ~ средний аппетит
        appetite += max(0, roster_slots - sum(c for _, c, _ in self.pals)) * 4.6
        per_plot = self.args.food_per_plot * (1.5 if self.args.research else 1.0)
        plots = max(2, math.ceil(appetite / per_plot))
        salad_ok = self.args.tech >= (self.structs.get("Tomato Plantation", {}).get("tech_level") or 99)
        food_plants = {}
        if salad_ok:
            pairs = max(1, -(-plots // 2))  # ceil: не недокармливаем
            food_plants = {"Tomato": pairs, "Lettuce": pairs}
            self.add_plantations(food_plants, {"Tomato": "Tomato Plantation", "Lettuce": "Lettuce Plantation"})
            station = self.best(["Cooking Pot", "Electric Kitchen", "Large-Scale Stone Oven", "Ancient Kitchen"])
            self.add(station, 1)
            self.hire_best("Kindling", 3, 1, "ЕДА: повар салатов")
            af = self.args.tech >= 78 and "Ancient Farm" in self.structs
            per = max(1, math.ceil(pairs / self.args.ancient_farm_yield)) if af else pairs
            self.notes.append(f"ЕДА (self): Salad — {per}x Tomato + {per}x Lettuce "
                              f"({'Ancient Farm' if af else 'плантаций'}), повар на {station}")
        else:
            food_plants = {"Red Berries": plots}
            self.add_plantations(food_plants, {"Red Berries": "Berry Plantation"})
            self.add("Campfire", 1)
            self.hire_best("Kindling", 2, 1, "ЕДА: жарка ягод")
            self.notes.append(f"ЕДА (self): Baked Berries — {plots}x Berry Plantation (апгрейд до Salad на tech 25)")
        n = sum(food_plants.values())
        if not share_crew:
            crew = max(1, math.ceil(n / (self.args.plants_per_worker * self.q())))
            self.hire_best("Planting", 3, crew, "ЕДА: посадка")
            self.hire_best("Watering", 3, crew, "ЕДА: полив")
            # Gathering палов не берём: собранное подхватывают при простое (авто-сбор)
        else:
            self.notes.append("Кормовые грядки обслуживает общая тройка базы (отдельные рабочие не нужны)")
        self.assumptions.append(
            f"Еда: спрос {appetite:.0f} аппетит-единиц (Σ FoodAmount ростера) → {n} грядок "
            f"(~{self.args.food_per_plot}/грядку; скорости голода в данных нет — --food-per-plot). Salad держит долго")
        return n

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
        rr = a.ranch_rate * self.ranch_mult()
        ranch = {ranch_map[p][0]: math.ceil(v / rr) for p, v in ranch_prod.items()}
        plants_n = {c: math.ceil(v / self.plant_yield_eff()) for c, v in plants.items()}
        trio = 3 * math.ceil(sum(plants_n.values()) / (a.plants_per_worker * self.garden_mult())) if plants_n else 0
        ops = cakes_h + sum(crafts.values()) - crafts.get("Flour", 0)
        cooks = max(1, math.ceil(ops / (a.cook_rate * self.q())))
        mills = max(1, math.ceil(crafts.get("Flour", 0) / 60)) if crafts.get("Flour") else 0
        heads = 2 * farms + sum(ranch.values()) + trio + cooks + mills
        return {"cakes_h": cakes_h, "eggs_h": cakes_h * eggs_per_cake, "ranch": ranch,
                "ranch_prod": ranch_prod, "plants_n": plants_n, "PLANTS": PLANTS,
                "imports": imports, "trio": trio, "cooks": cooks, "mills": mills, "heads": heads}

    def _breeding_build(self, farms):
        """Полностью строит брид-базу на `farms` ферм. Возвращает суммарное число палов.
        Вызывается решателем несколько раз — каждый раз с чистого листа."""
        a = self.args
        self.buildings, self.pals, self.notes, self.assumptions = {}, [], [], []
        hatchery = a.tech >= 76 and "Ancient Hatchery" in self.structs
        farm_name = "Ancient Hatchery" if hatchery else "Breeding Farm"
        line = self.breeding_staff_for(farms)

        support_kinds = [("base_defense", "ПВО базы от рейдов")]
        if a.braloha:
            support_kinds.insert(0, ("egg_speed", "яйца +20~50%"))
        if a.incubation > 0:
            support_kinds.append(("incubation", "инкубация -20~40%"))
        else:
            self.notes.append("Инкубация мгновенная (настройка мира = 0): инкубаторы и Dynamoff не нужны — слот сэкономлен")
        self.support_core(support_kinds + [("crop_growth", "рост культур +50~70%"), ("crop_yield", "урожай +18~35%"),
                           ("sanity_save", "SAN базы -10~15% утечка"),
                           ("suitability:Watering", "+1 Watering всем (Amione)"),
                           ("suitability:Planting", "+1 Planting всем (Petallia)"),
                           ("suitability:Gathering", "+1 Gathering всем (Clovee) — тройка"),
                           ("suitability:Farming", "+1 Farming всем (Cinnamoth) — ранч")])
        self.hire("Woolipop Terra", 1, "саппорт: голод базы -15~25% + Caramel Cotton Candy на ранче")

        self.add(farm_name, farms)
        self.hire("(пары родителей)", 2 * farms, f"в {farm_name} x{farms}")
        rm = self.idx["inverted"]["ranch_produce"]
        for sp, n in line["ranch"].items():
            prod = next((p for p in line["ranch_prod"] if rm[p][0] == sp), "?")
            self.hire(sp, n, f"ранч: {prod} ({line['ranch_prod'].get(prod, 0):.0f}/час)")
        self.add("Ranch", math.ceil(sum(line["ranch"].values()) / 4))
        self.add_plantations(line["plants_n"], line["PLANTS"])
        for name, per_h in line["imports"].items():
            self.notes.append(f"⚠ привозное для торта «{a.cake}»: {name} x{per_h:.0f}/час")
        if line["mills"]:
            self.add("Mill", line["mills"])
            self.hire_best("Watering", 4, line["mills"], "мельница")
        cake_station = (self.items.get(a.cake, {}).get("recipe") or {}).get("station")
        kitchen = cake_station if cake_station in self.structs and             (self.structs[cake_station]["tech_level"] or 0) <= a.tech else             self.best(["Cooking Pot", "Electric Kitchen", "Large-Scale Stone Oven", "Ancient Kitchen"])
        self.add(kitchen, line["cooks"])
        self.hire_best("Kindling", 4, line["cooks"], f"повар тортов ({a.cake})")
        # кормовые грядки ставим до тройки, чтобы ОДНА тройка покрыла и торт, и салат
        food_plots = self.food_module(a.slots, share_crew=True) if a.food == "self" else 0
        if a.food != "self":
            self.notes.append("Еда привозная (--food shipped): вози Salad/Pizza guild chest'ом")
        cake_plots = sum(line["plants_n"].values())
        n_trio = max(1, math.ceil((cake_plots + food_plots) / (a.plants_per_worker * self.garden_mult())))
        self.hire_best("Planting", 3, n_trio, f"посадка (все {cake_plots + food_plots} грядок)")
        self.hire_best("Watering", 3, n_trio, "полив (все грядки)")
        self.hire_best("Gathering", 3, n_trio, "сбор (все грядки)")
        self.hire_transport()
        if a.incubation > 0 and not hatchery:
            inc = self.best(["Egg Incubator", "Electric Egg Incubator", "Large Egg Incubator",
                             "Large-Scale Electric Egg Incubator"])
            if inc:
                import re as _re
                m = _re.search(r"(\d+)\s*egg", self.structs[inc].get("capacity") or "")
                cap = int(m.group(1)) if m else 1
                n_inc = max(1, min(math.ceil(farms * 2 * a.incubation / cap), 12))
                self.add(inc, n_inc)
                self.assumptions.append(f"Инкубаторы: {n_inc} = фермы x2 x мир {a.incubation} / вместимость {cap} "
                                        "(точное время инкубации по типам яиц в данных нет)")
        self.infra(a.slots)
        if hatchery or (kitchen and self.structs.get(kitchen, {}).get("power")):
            self.power(heavy=hatchery)

        self._breed_summary = (farm_name, hatchery, line)
        return sum(c for _, c, _ in self.pals)

    def preset_breeding(self):
        a = self.args
        # решатель: максимум ферм, чей ПОЛНЫЙ план (с транспортом/едой/саппортом) влезает в слоты
        if a.farms:
            self._breeding_build(a.farms)
            farms = a.farms
        else:
            farms = 1
            self._breeding_build(1)
            while farms < 40:
                if self._breeding_build(farms + 1) <= a.slots:
                    farms += 1
                else:
                    self._breeding_build(farms)  # откат к последнему влезающему
                    break
        farm_name, hatchery, line = self._breed_summary
        self.notes.append(f"{farm_name} x{farms}: ~{line['eggs_h']:.0f} яиц/час = {line['eggs_h']*24:.0f}/сутки, тортов {line['cakes_h']:.0f}/час "
                          + (f"— линия рассчитана под буст Braloha x{a.egg_boost}" if a.braloha
                             else f"— без Braloha (x{a.egg_boost}), яйца на базовой скорости")
                          + (" (авто-инкубация, 10 слотов яиц)" if hatchery else ""))
        if hatchery:
            self.notes.append("⚠ Ancient Hatchery: скорость производства яиц принята как у обычной фермы "
                              f"({a.egg_interval or 5} мин/яйцо). Гайды говорят про '~10 сек/цикл' (PRELIMINARY) — "
                              "если это про кладку, а не инкубацию, спрос на торты кратно выше. "
                              "Замерь в игре и задай --egg-interval")
        self.notes.append(
            "Торты — НЕ линейные тиры, у каждого свой эффект и станция (выбирай под цель батча): "
            "Cake — базовый (Cooking Pot); Mushroom Cake — рост статов/IV; "
            "Vegetable Cake — 2 ЯЙЦА за цикл, объём (Electric Kitchen, Tomato+Lettuce); "
            "Extravagant Vegetable Cake — шанс МУТАЦИИ + статы (Large-Scale Stone Oven); "
            "Special Cake — стак ПАССИВОК потомству (Ancient Kitchen). "
            "Напр. Vegetable даёт 2 яйца, чего Special НЕ даёт — они ситуативны, а не «лучше/хуже»")
        self.notes.append(f"Потолок {farms} ферм для {a.slots} слотов при этих настройках "
                          f"(еда {a.food}, рабочие {a.workforce}); больше = вторая брид-база или --food shipped")
        self.notes.append("В пати при сборе яиц: Broncherry Aqua (45~55% альфа-яйца) + Grintale (50~75% лишнее яйцо)")
        self.assumptions.append(
            f"Грядки: {a.plant_yield}/час × yield-саппорты (партнёрки, СИЛА ОТ ЗВЁЗД): Lullu рост "
            f"×{1.70 if a.stars else 1.50:g} + Prunelia урожай ×{1.35 if a.stars else 1.18:g} "
            f"({'4★' if a.stars else '0★'})" + (" × ресёрч +50%" if a.research else "") + " → меньше грядок")
        self.assumptions.append(f"Ранч: {a.ranch_rate} дропов/час x качество (звёзды --stars, пассивки --workforce, "
                                f"ресёрч; при пассивках +Ranch Master +2 Farming/handbook ×1.5); "
                                f"кухня: {a.cook_rate} тортов/час на повара (--cook-rate); "
                                f"яйцо {a.egg_interval or 5} мин x буст {a.egg_boost} "
                                f"({'Braloha в составе' if a.braloha else 'без Braloha, --no-braloha'}; --egg-interval/--egg-boost)")

    def preset_mine_craft(self):
        a = self.args
        # самообеспечение сырьём: placeable-станции добычи (по 1 на базу)
        sites = []
        # ВНИМАНИЕ: "Mine"/"Electric Mine"/"Ice Mine" — ловушки (Defenses), не добыча!
        # в игре можно поставить по 1 КАЖДОГО типа — добавляем все доступные по tech
        # семьи с одинаковым продуктом — только лучшая (Ore I/II дают одно и то же);
        # Logging I (Wood) и II (Hardwood) — разные продукты, обе
        synthesizer = a.tech >= 78 and "Ancient Material Synthesizer" in self.structs
        if synthesizer:
            # синтезайзер производит ЛЮБОЙ материал (дерево/руды) — заменяет ВСЕ шахты.
            # Один продукт за раз: переключай, что нужно; лимит 1 на базу
            self.add("Ancient Material Synthesizer", 1)
            self.hire_best("Mining", 6, 1, "Ancient Material Synthesizer (любой материал, 1 пал)")
            self.notes.append("Ancient Material Synthesizer (tech 78) заменяет ВСЕ шахты/лесопилки: "
                              "производит любой вид дерева/руды, но ОДИН выбранный за раз — переключай продукт. "
                              "Нужен параллельный поток нескольких руд — доставь конкретные шахты через «+ здание»")
        else:
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
        ext = self.best(["Crude Oil Extractor", "High-Pressure Crude Oil Extractor"])
        if ext:
            self.add(ext, 1)
            self.notes.append(f"{ext}: работает БЕЗ палов, только электричество "
                              f"({self.structs[ext].get('energy_per_sec')}/с)"
                              + ("; ставится в любой точке" if "High-Pressure" in ext else "; нужна нефтяная точка"))
        if sites:
            self.notes.append(f"Добыча ({len(sites)} станций, по 1 на базу): {', '.join(sites)}")
        self.support_core([("suitability:Mining", "+1 Mining всем (Tetroise)"),
                           ("base_defense", "ПВО базы от рейдов (Panthalus)"),
                           ("suitability:Handiwork", "+1 Handiwork всем (Ribbuny)"),
                           ("suitability:Transporting", "+1 Transport всем (Wumpo)"),
                           ("suitability:Kindling", "+1 Kindling всем (Katress Ignis) — печи/плавка"),
                           ("sanity_save", "SAN базы (Shroomer Noct)")])
        mining_sites = [x for x in sites if self.structs[x].get("workers") == "Mining"]
        lumber_sites = [x for x in sites if self.structs[x].get("workers") == "Lumbering"]
        # у станций до worker_slots мест (обычно 3); --per-station задаёт, сколько занять
        def staff(site_list, task, min_lv, label):
            for site in site_list:
                slots = self.structs[site].get("worker_slots") or 1
                n = max(1, min(self.args.per_station, slots))
                self.hire_best(task, min_lv, n, f"{label}: {site} ({n}/{slots} мест)")
        staff(mining_sites, "Mining", 6, "добыча")
        staff(lumber_sites, "Lumbering", 5, "лесопилка")
        if sites:
            self.notes.append(f"Добыча: {self.args.per_station} пал(ов) на станцию (--per-station, у шахт до 3 мест — "
                              "больше палов = быстрее добыча на станции). 1 = все станции работают, но не на макс. скорости")
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
        # крафт-ранч: пал-материалы для компонентов (Computer/AI Core/Cement/Coolant).
        # Flame/Electric Organ — узкое место под Computer, поэтому по 2; Pal Oil тоже x2.
        if a.tech >= 45:
            producers = [("Flambelle", 2, "Flame Organ (Computer, Carbon Fiber, Bio Battery) — x2, узкое место"),
                         ("Sparkit", 2, "Electric Organ (Computer, AI Core, Bio Battery) — x2, узкое место"),
                         ("Dumud Gild", 2, "High Quality Pal Oil — Farming 4, x4 к скорости Dumud (Polymer, Circuit Board) — x2"),
                         ("Depresso", 1, "Venom Gland 🌙 ночной, работает 24/7 (AI Core, Solvent, Thermal Core)"),
                         ("Kelpsea", 1, "Aquatic Pal Fluids (Cement, Cryogenic Coolant)"),
                         ("Foxcicle", 1, "Ice Organ — Farming 3 (Cryogenic Coolant)")]
        else:
            producers = [("Surfent", 1, "Leather (броня)"), ("Cremis", 1, "Wool (Cloth)"),
                         ("Sootseer", 1, "Bone 🌙 ночной, Farming 2 (Cement)"),
                         ("Kelpsea", 1, "Aquatic Pal Fluids (Cement)"), ("Foxcicle", 1, "Ice Organ — Farming 3 (Coolant)")]
        for sp, cnt, why in producers:
            self.hire(sp, cnt, f"крафт-ранч: {why}")
        self.add("Ranch", -(-sum(c for _, c, _ in producers) // 4))
        self.notes.append("Крафт-ранч: пал-материалы на месте. Flame/Electric Organ и Pal Oil — по 2 пала "
                          "(узкое место под Computer/Polymer); при нехватке добавь ещё. 🌙 = ночной, работает без сна; "
                          "ДОПУЩЕНИЕ: скорость ранча ~ уровню Farming")
        self.hire("Ribbuny Botan", 1, "оружейный верстак (+200~400% на нём)")
        self.hire("Anubis", 2, "верстаки (Handiwork 6) — пара с Sekhmet")
        self.hire("Sekhmet", 1, "буст Anubis +20~40% и себе +30~60% на верстаках")
        self.hire_transport()
        if a.spoilage:
            cool = self.best(["Cooler Box", "Refrigerator"])
            if cool:
                self.add(cool, 1)
                self.hire_best("Cooling", 3, 1, "холодильник (замедляет порчу)")
        else:
            self.notes.append("Порча выключена (настройка мира): холодильник и Cooling-пал не нужны — "
                              "хватает Feed Box; слот и Ice-пал сэкономлены")
        if a.food == "self":
            self.food_module(a.slots)  # сам нанимает лёгкую бригаду (посадка+полив)
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

        plants_n = {}
        for crop, per_h in need_plants.items():
            if self.best([PLANTS[crop]]) or (a.tech >= 78 and "Ancient Farm" in self.structs):
                plants_n[crop] = math.ceil(per_h / self.plant_yield_eff())
            else:
                imports[crop] = imports.get(crop, 0) + per_h
        total_pl = self.add_plantations(plants_n, PLANTS)
        if total_pl:
            self.plant_crew(total_pl)
            self.support_core([("crop_growth", "Lullu"), ("crop_yield", "Prunelia"),
                               ("suitability:Planting", "+1 Planting"), ("suitability:Watering", "+1 Watering")])
        for prod, per_h in need_ranch.items():
            sp = ranch_map[prod][0]
            self.hire(sp, math.ceil(per_h / (a.ranch_rate * self.ranch_mult())), f"ранч: {prod} ({per_h:.0f}/час)")
        if need_ranch:
            ranchers = sum(math.ceil(v / (a.ranch_rate * self.ranch_mult())) for v in need_ranch.values())
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
        fw = self.food_ws()
        parts = [f"{a.workforce}"]
        if fw:
            parts.append(f"еда +{fw:.0f}")
        if a.stars:
            parts.append("4★ ×1.55")
        if a.research:
            parts.append("ресёрч ×1.45")
        ws_txt = f"Work Speed {int(70 * self.q())} ({', '.join(parts)})"
        print(f"═══ База: {a.preset}  |  слоты {a.slots}  |  tech {a.tech}  |  еда: {a.food}  |  {ws_txt} ═══\n")
        if a.stars:
            self.notes.append("Рабочие 4★: +1 ур. работы (≈×1.55). Цена: 116 дублей вида на каждого пала — "
                              "оправдано для постоянного ядра базы, не для одноразовых")
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
            # «Ancient Farm (Tomato)» — материалы/tech берём у базового здания
            s = self.structs.get(b) or self.structs.get(b.split(" (")[0], {})
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
    ap.add_argument("--no-spoilage", dest="spoilage", action="store_false",
                    help="настройка мира «еда не портится»: без холодильника и Cooling-пала, хватит Feed Box")
    ap.add_argument("--research", action="store_true",
                    help="макс ресёрч Pal Labor Research Lab (account-wide): Work Speed +45%, урожай +50% — меньше рабочих/грядок")
    ap.add_argument("--stars", action="store_true",
                    help="рабочие сконденсированы до 4★ (+1 ур. работы ≈ ×1.55 скорости; цена — 116 дублей на пала)")
    ap.add_argument("--ancient-farm-yield", type=float, default=3,
                    help="во сколько раз Ancient Farm производительнее обычной грядки (дефолт 3 — калибровка по игроку: "
                         "4 древние фермы кормят базу 50 палов с избытком; точной выработки в данных нет)")
    ap.add_argument("--food-buff", type=float, default=30,
                    help="бонус Work Speed от кормёжки buff-едой: Salad +30 (по умолч.), Minestrone +40, 0 = без буффа")
    ap.add_argument("--food-per-plot", type=float, default=110,
                    help="аппетит-единиц (Σ FoodAmount), которые кормит одна грядка (дефолт 110 — калибровка по игроку: "
                         "6 грядок Tomato/Lettuce = сильный перебор еды; абсолютной скорости голода в данных нет)")
    ap.add_argument("--per-station", type=int, default=1,
                    help="(mine-craft) палов на добывающую станцию 1..3 (у шахт 3 места; больше = быстрее добыча)")
    ap.add_argument("--cake", default="Cake",
                    choices=["Cake", "Mushroom Cake", "Vegetable Cake", "Extravagant Vegetable Cake", "Special Cake"],
                    help="(breeding) какой торт производить (Vegetable = 2 яйца за цикл)")
    ap.add_argument("--incubation", type=float, default=1,
                    help="(breeding) множитель скорости инкубации из настроек МИРА: 0 = мгновенно (без инкубаторов и Dynamoff)")
    ap.add_argument("--no-braloha", dest="braloha", action="store_false",
                    help="(breeding) без Braloha: убрать её из состава и считать яйца без буста +20~50%%")
    ap.add_argument("--egg-boost", type=float, default=None,
                    help="(breeding) переопределить множитель тортовой линии вручную "
                         "(по умолчанию 1.35 с Braloha, 1.0 без неё)")
    ap.add_argument("--ranch-rate", type=float, default=12, help="дропов/час на ранч-пала (ДОПУЩЕНИЕ)")
    ap.add_argument("--plant-yield", type=float, default=60, help="единиц урожая/час с плантации (ДОПУЩЕНИЕ)")
    ap.add_argument("--cook-rate", type=float, default=30, help="тортов/час на повара (ДОПУЩЕНИЕ)")
    ap.add_argument("--plants-per-worker", type=float, default=3, help="плантаций на 1 троицу рабочих при baseline")
    args = ap.parse_args()
    if args.egg_boost is None:
        # Braloha egg speed +20~50% — партнёрка, растёт от звёзд: 4★ = +50% (×1.5), 0★ = +20% (×1.2)
        args.egg_boost = (1.5 if args.stars else 1.2) if args.braloha else 1.0
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
