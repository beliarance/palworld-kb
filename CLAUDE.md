# Palworld 1.0 Knowledge Base

Локальная база знаний по игре **Palworld версии 1.0** (полный релиз 10 июля 2026).
Назначение: точно отвечать на игровые вопросы (роли палов, бридинг, стихии/каунтеры,
сборка команд, базостроение, хранение) и служить единым источником данных для будущего
CLI/веб-приложения.

## Структура

```
data/       — машиночитаемые данные (единый источник правды)
docs/       — человекочитаемые гайды (markdown)
scripts/    — query-инструмент, валидатор, сборщики данных
tests/      — unit-тесты query-слоя
web/        — локальный веб-интерфейс (SPA без зависимостей, читает data/*.json;
              запуск: python3 -m http.server 8842 → http://localhost:8842/web/).
              Автономная сборка: python3 scripts/build_standalone.py →
              web/palworld_kb_standalone.html (данные вшиты, открывается без сервера;
              пересобирать после изменения data/ или index.html)
```

Логика бридинга и конструктора баз продублирована в web/index.html (JS) и в
scripts/query.py / scripts/base_planner.py (Python) — при изменении править оба места.

Посторонние файлы в корне (Darktide_*, build_cheatsheet.js, node_modules, pg-1.jpg) —
от другого мини-проекта, к этой базе не относятся, не трогать.

## Данные и схемы (`data/`)

| Файл | Что внутри |
|---|---|
| `palworld_pals.csv` | 299 палов: `Number, Name, Element_1, Element_2, <12 work-колонок>, PaldbURL`. Work-уровни в 1.0 идут **1–8** (не 1–4 как в раннем доступе); пусто = пал не выполняет работу. |
| `pals_combat.json` | Массив 299 объектов: `name, paldeck_number, elements[], rarity, hp, melee_attack, shot_attack, defense, support, stamina, price, ride, mount_type (ground/flying/swim/null), movement{walk,run,sprint}, partner_skill{name,effect}, notable_drops[], role_tags[]`. |
| `type_chart.json` | 9 стихий; для каждой `strong_vs[]` и `weak_to[]`. Инвариант симметрии (A strong_vs B ⇔ B weak_to A) проверяется валидатором. |
| `bosses.json` | `tower_bosses[]` (9 башен 1.0) и `raid_bosses[]`: элементы, каунтер-элементы, уровни, тактика, флаг `preliminary`. |
| `breeding.json` | `formula` (текст), `combi_ranks{имя: ранг}`, `special_combos[{parent_a,parent_b,child}]`, `notes[]`, `gaps[]`, `sources[]`. Механика: обычный потомок = пал с рангом, ближайшим к `floor((rA+rB+1)/2)`; special combos переопределяют; одинаковые родители → тот же вид; дети special combos не выпадают из ранговой формулы. |
| `tier_lists.json` | `best_mounts_ground/flying/swim`, `best_fighters`, `best_for_fishing`, `best_base_workers_by_task{...}` — элементы `{name, note}`, лучшие первыми; `sources[]`. |
| `items.json` | `items[]`: `name, category, tech_level, recipe{station, materials{}}` или null, `obtained_from[]`, `notes`; у 84 аксессуаров также `effect` и `schematic_sources[]` (крафт 70 из них заперт за схемой «<Name> Schematic»: где падает + шанс + координаты фикс-точек Ancient Ruin; сборщик `collectors/fetch_accessory_effects.py`); плюс `stations[]`. Компоненты рецептов резолвятся по именам внутри же файла. |
| `expeditions.json` | Экспедиции: `unlock{}`, `mechanics{}`, `missions[{name, duration_hours, required_level, rewards[]}]`. Гайд — `docs/expeditions.md`. |
| `active_skills.json` | `skills[{name, element, power, cooldown_seconds, range, description, exclusive_to[], skill_fruit_exists}]` + `learnsets{имя: [{skill, level}]}`. |
| `passives.json` | `passives[{name, tier, effects, category, exclusive_source[], breedable}]` — полный список пассивок, включая вредные. |
| `pal_locations.json` | `pals{имя: {regions[], day_night, alpha_locations[], egg_types[], other_sources[], notes}}` — где найти/поймать каждого пала. |
| `resource_nodes.json` | `resources[{name, best_locations[{area, coordinates, node_count, notes}], base_recommendation, other_sources[]}]`. Гайд — `docs/resource_locations.md`. |
| `index.json` | **Денормализованный индекс — начинай поиск отсюда.** По каждому палу всё сразу (статы, работы, ранч-продукция, дропы, локации, ранг, теги partner skill) + обратные индексы: `inverted.ranch_produce{предмет: [палы]}`, `inverted.drops{предмет: [палы]}`, `inverted.work{задача: [[пал, ур]]}`, `inverted.partner_tags{fishing/capture/player_attack/...: [палы]}` и партийные роли `party:*` (weak_point:стихия, attack_type:стихия:active|mount, stack_atk/stack_speed:стихия, resist:стихия, player_atk, survival, weight/weight_cargo, capture_*, fishing_*, loot:стихия, detect/treasure_open/stealth/climate_*/terrain:sand — поле `party_roles` в карточке пала; списки отсортированы по силе эффекта); там же `base_support:*` — палы с базовыми баффами (+1 к навыку всех палов базы по каждой из 12 работ, ускорение яиц/инкубации, сохранение SAN/голода, буст урожая) и поле `base_support` в карточке пала. Генерируется: `python3 scripts/build_index.py` — **перезапускать после любого изменения data/**. |
| `skill_dps_meta.json` | Замеренный сообществом DPS активных скиллов против боссов (14 записей): `skill, element, dps_large, dps_small, multi_hit, acquire (exclusive/breeding/fruit/melee/learn), pal, note` + `guidance[]`, `sources[]`, `preliminary`. Реальный DPS по боссу зависит от мульти-хита и размера хитбокса — важнее голой power/cd. Используется пати-креатором (блок «Мета-скиллы»). Сборщик — вручную из гайдов 1.0. |
| `base_building.json` | Базостроение: 125 структур (tech, ancient-флаг, материалы, worker, power, energy_per_sec; `worker_req{tasks[], min_level}` у Ancient-зданий — двойные требования типа Kindling+Cooling; «Mine»/«Electric Mine»/«Ice Mine» — ловушки, не добыча), 56 блюд (nutrition/sanity/баффы/спойл), `pal_food_amount` 299/299 (аппетит 1–10), `rates` (яйцо 5 мин, 1 торт = 1 яйцо, таблицы скорости работы по уровням 1–10, механика уровней 9–10: Applied Handbook +1/конденсер/ауры). Полный индекс зданий paldb — `/en/Structures` (487 позиций, декор не собираем). |
| `regions.json` | 80 регионов карты → координаты метки (примерный центр). Используется `where` и планировщиком для подсказок «где ловить». Уровневые подзоны (`... [Lv. X-Y]`) маппятся отрезанием суффикса. |
| `merchants.json` | 38 магазинов торговцев: `shops{код: {merchant, currency, locations[{area, coordinates, level}], items[{name, price, qty?}]}}` (price=null = за золото по стандартной цене) + `pal_traders` (Pal Merchant / Black Marketeer — продают палов, с координатами). Валюты: Gold Coin, Battle Ticket (Arena), Dog Coin (Medal Merchant), Successful Bounty Token (PIDF Bounty Officer). Caravan_Shop_1–25 — караванщики 1.0, посещают базу игрока. Сборщик: `scripts/collectors/fetch_merchants.py`; строки «Sold by ...» в items.json генерируются им же (`--enrich-items`). |
| `raw/` | Сырые батчи парсинга paldb (история сборки pals_combat.json). |

**Канонические имена палов** — колонка `Name` в CSV. Все остальные файлы обязаны
использовать ровно эти написания (валидатор это проверяет).

## Гайды (`docs/`)

- `breeding_mechanics.md` — cake-рецепты, наследование пассивок, IV, Condenser (4/16/32/64 = 116 дублей до 4★), Mutation и Awakening (новое в 1.0), лучшие пассивки с цифрами.
- `boss_tower_counters.md` — таблица стихий, 9 башенных боссов 1.0 с каунтерами и тактикой, alpha/dungeon/raid-боссы.
- `base_setup.md` — лимиты базы, станции с материалами, стартовый самодостаточный сетап, раскладка рабочих.
- `guild_stash_and_storage.md` — гильдии, что шарится между базами (только Guild Chest), схема хранения.
- `expeditions.md` — экспедиции: станция, механика Firepower, миссии и награды.
- `resource_locations.md` — точки фарма ресурсов с координатами, мета-места под базы, World Tree.
- `base_locations.md` — топ-места под базы по стадиям (early/mid/late/endgame) + критерии выбора (ресурсы/рельеф/безопасность), лимит баз и специализация. PRELIMINARY 1.0.

## Как отвечать на вопросы

**Упоминая пала в ответе, всегда указывай его палдекс-номер в скобках:** `Anubis (#139)`.
Номер — колонка `Number` в CSV (`paldeck_number` в pals_combat.json).

Основной инструмент — `python3 scripts/query.py <команда>`:

```
pal <name>                    профиль пала
workers <task> [--element E]  лучшие рабочие (kindling, watering, planting, electricity,
                              handiwork, gathering, lumbering, mining, medicine, cooling,
                              transporting, farming)
mounts <ground|flying|swim>   маунты по скорости спринта
fighters [--element E]        бойцы по боевому скору
counter <element>             чем бить стихию + топ палов-контрпиков
boss <name>                   каунтер под босса/башню/рейд
breed <A> <B>                 результат скрещивания
breed-to <X> [--with A]       как получить пала X (special combos + ранговые пары)
breed-chain <start> <target> цепочка бридинга от одного родителя к виду (BFS) —
                              для переноса дроп-онли/эксклюзивного трейта на целевой вид
team <task>                   команда из 5 (fishing, combat, mining, lumbering,
                              production, ranch, transport, cake)
produce <item>                кто производит предмет (ранч/дропы/крафт) — через index.json
party <goal>                  пати из 5 под цель: combat (--element стихия бойца ИЛИ --vs враг;
                              --two-fighters = 2 бойца+3 ауры), openworld, catch,
                              fishing (--fish loot|pals: loot=ради ресурсов с Jelliette; pals=выуживать палов, Jelliette не нужна, вместо неё 2-й талант Solmora + быстрый маунт),
                              loot (--vs стихия жертв), eggs, explore (--biome cold|heat), xp (прокачка); --weightless (настройка мира «без веса»: убирает весовые ауры, добивает сустейном/атакой). Скиллы бойцов: производный ДПМ power×60/max(cd,5), ×2 к слабости; плюс блок мета-скиллов под босса из skill_dps_meta.json (замеренный DPS, мульти-хит).
                              Механика: дерётся 1 выпущенный пал, остальные — ауры
                              "While in party" (не стакаются) → дефолт 1 боец + 4 ауры
tiers <category>              тир-лист из tier_lists.json
item <name>                   предмет: категория, рецепт, станция, где достать
craft <name> [--qty N]        разложение крафта до сырых материалов (--flat без рекурсии)
drops <item>                  какие палы дропают предмет
skills <pal>                  ленсет активных скиллов пала + эксклюзивы
skill <name>                  детали активного скилла (элемент/урон/кд)
passive <name>                эффект пассивки, источник
where <pal>                   где найти/поймать пала (спавны, альфы, яйца)
resource <name>               лучшие места фарма ресурса (координаты)
```

Для вопросов про механики (как работает наследование, что такое Awakening, что шарится
между базами) — читать соответствующий гайд в `docs/`.

**Конструктор баз** — `python3 scripts/base_planner.py <preset> [опции]`:
пресеты `breeding | mine-craft | food | starter` (нефть — 1 экстрактор внутри mine-craft, работает без палов); опции `--slots N --tech N
--food self|shipped --workforce baseline|passives|max --roster top|easy --farms N --raw --lux
--metal ingot|refined|pal-metal|coralum|soralite|paloxite` (задаёт тир вместо --tech)
`--extra "Statue of Power:1,..."` (необязательные здания в смету).
`--roster top` — лучшие палы с альтернативой «проще достать»; `--roster easy` — наоборот.
У труднодоступных палов в выводе подсказка [где ловить] из pal_locations.
Выдаёт состав палов, здания со сметой материалов, заметки и явные допущения
(скорость ранча/плантаций — `--ranch-rate`, `--plant-yield`, `--cook-rate`; число брид-ферм — по умолчанию 1 (Ancient Hatchery инкубация ~10с, узкое место — разбор потомства; 2 для параллельных пар), `--farms N`; при Ancient Hatchery Braloha (ускорение кладки) авто-исключается — узкое место сортировка, а не скорость яиц (на медленной Breeding Farm остаётся); Broncherry Aqua/Grintale — ауры сбора яиц, носить в ПАТИ, не на базе; выработка Ancient Farm — `--ancient-farm-yield`, по умолчанию 1 (по игроку «быстрее ли плантации — сложно сказать»); еда — `--food-per-plot` (по умолчанию 80: 4 плантации кормят 50 палов). Число ферм/грядок режут yield-саппорты Lullu/Prunelia (от звёзд)). Торты — не линейные тиры: у каждого свой эффект/станция (Vegetable=2 яйца, Special=пассивки, Extravagant=мутация, Mushroom=статы) — пресет это поясняет.

## Проверка и тесты

```
python3 scripts/validate_data.py        # схемы, имена, симметрия type chart
python3 -m unittest discover tests      # тесты query-слоя
```

Запускать оба после любого изменения данных.

## Правила обновления данных

1. **Версия игры — 1.0 (июль 2026).** Не смешивать с данными раннего доступа без пометки.
2. Пометки в docs: `(pre-1.0 guide)` = данные EA-эпохи, не перепроверены под 1.0;
   `(PRELIMINARY 1.0)` = свежие данные 1.0, ещё стабилизируются. В JSON — поля
   `preliminary` / `notes` / `gaps`.
3. Каждое обновление данных фиксировать в `DATA_SOURCES.md`: источник (URL), что взято, дата.
4. **Ничего не выдумывать**: нет данных в источнике → `null` + пометка в `gaps`/`notes`.
5. Данные 1.0 ещё стабилизируются: при конфликте источников доверять более свежим,
   явно обновлённым под 1.0 (game8, paldb.cc, palworld.gg), а не EA-гайдам.
6. Скрипты сбора класть в `scripts/collectors/`, чтобы сбор был воспроизводим.
   При скрапинге: WebFetch режет страницы ~60k символов — пагинировать; JS-страницы
   брать через headless-браузер.
