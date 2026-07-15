# Источники данных

Версия игры: **Palworld 1.0** (релиз 10 июля 2026). Дата актуализации базы: **2026-07-14**.

Пометки: `(pre-1.0 guide)` — данные Early-Access-эпохи, не перепроверены под 1.0;
`(PRELIMINARY 1.0)` — данные 1.0, ещё стабилизируются.

## data/palworld_pals.csv — работы палов (собрано 2026-07-14)

- **paldb.cc** — списки палов и work suitability по каждому палу (парсер: `scripts/collectors/parse_pals.py`).
- Work-уровни 1–8 соответствуют шкале 1.0.

## data/pals_combat.json — боевые статы, маунты, partner skills (собрано 2026-07-14)

- **paldb.cc** — статы (HP/ATK/DEF), movement, partner skills, дропы; собрано батчами
  (`data/raw/_raw_batch*.json`, сборка: `scripts/collectors/_build_combat.py`).

## data/type_chart.json — таблица стихий (2026-07-14)

- Первичный черновик: `docs/boss_tower_counters.md` (компиляция game8.co, nexttier.pro,
  thepalprofessor.com, palworld.fandom.com).
- Верифицировано 2026-07-14 по двум независимым актуальным источникам (Dexerto — полная
  таблица; xgamingserver, статья от 2026-06-08): все 9 элементов совпали, правок не
  потребовалось (`verified: true`, URL в `sources` файла).

## data/bosses.json — башенные и рейдовые боссы (2026-07-14)

- Выжимка из `docs/boss_tower_counters.md` §2–§3, §7. Боссы 8–9 (Shaolong, Astralym)
  и часть рейдов — `(PRELIMINARY 1.0)` (флаг `preliminary: true` в записях).

## data/breeding.json — combi ranks и special combos (собрано 2026-07-14)

- **paldb.cc/en/Breeding_Farm** — полная таблица CombiRank (299/299 палов) и все 164
  unique-комбо (136 кросс-видовых + 28 self-pair «только одинаковой парой»). Версия 1.0
  подтверждена косвенно: список совпадает с палдексом 1.0 включая 1.0-only виды.
  Сырой дамп: `data/raw/paldb_breeding.html`; скрипты:
  `scripts/collectors/fetch_breeding.py`, `scripts/collectors/build_breeding_json.py`.
- **palworld.wiki.gg/wiki/Breeding** — формула `floor((A+B+1)/2)`, тайбрейк, требование пола.
- **palworld.ludbase.com** — подтверждение формулы и числа special-комбо под 1.0.
- Пробелы (см. `gaps` в файле): точный тайбрейк при равных рангах документирован
  противоречиво; 11 кроссовер-палов делят ранг 3100.

## data/tier_lists.json — тир-листы по ролям (собрано 2026-07-14)

- **palworld.gg** — тир-листы combat / flying mounts / ground mounts / base work
  (скрапинг: `scripts/collectors/fetch_tier_pages.sh`, `parse_palworld_gg.py`).
- **nexttier.pro**, **thebiglead.com** — скорости маунтов; **palworldzone.com** — пловцы;
  **oslink.io** — бойцы 1.0; **4netplayers.com**, mobalytics (сводка) — рыбалка 1.0.
- Все 89 записей сверены с CSV (0 несоответствий), work-уровни в заметках проверены
  программно. **pindrop.gg отброшен** (ещё pre-1.0 ростер); game8/fandom/wiki.gg были
  недоступны из-за бот-защиты — заменены источниками выше.
- Ни одна категория не взята из EA-эпохи (включая рыбалку — фича 1.0).

## data/expeditions.json + docs/expeditions.md — экспедиции (собрано 2026-07-14)

- **palpedia.net/expeditions** (сайт на v1.0.0) — все 18 миссий с полными пулами наград
  (279 строк с количеством и шансами); скрапинг: `scripts/collectors/parse_expeditions.py`,
  `build_expeditions_json.py`; сырой парс: `data/raw/expeditions_palpedia_raw.json`.
- **palworld.wiki.gg** (Expeditions, Pal_Expedition_Station) — механика, формула Firepower
  = (ATK + DEF + HP/5) × ранг-конденсации², стоимость станции.
- **xgamingserver** — патч-ноуты 1.0 (экспедиции расширены на Sunreach и World Tree).
- Пробелы: точная кривая скейлинга наград от избытка firepower; влияние трейтов (в `gaps`).

## data/active_skills.json — активные скиллы (собрано 2026-07-14)

- **paldb.cc/en/Active_Skills** — 328 скиллов, все с элементом/уроном/кулдауном
  (сырой HTML: `data/raw/paldb_active_skills.html`).
- **paldb.cc/en/<PalName>** — ленсеты 298/299 палов (у Astralym секция пуста — босс-пал).
  Скрипты: `scripts/collectors/fetch_skills.py`, `build_active_skills.py`.
- 157 эксклюзивов замаплены на палов; 46 внутренних boss-only записей исключены,
  10 дублей смержены (задокументировано в `notes` файла).

## data/resource_nodes.json + docs/resource_locations.md — ресурсы на карте (собрано 2026-07-14)

- 16 ресурсов (Ore, Coal, Quartz, Sulfur, Paldium, Crude Oil, Chromite, Hexolite,
  Paloxite, Radiant Gems, Soralite и др.), 47 локаций с координатами (x, y).
- Источники (18 в `sources` файла): nexttier.pro (базы 1.0, oil rigs), shockbyte (уголь),
  scalacube (руда/нефть), thegamer (skill fruits), vgtimes + bisecthosting (World Tree /
  Sunreach 1.0), nodecraft/holy.gg (сера, Chromite/Hexolite).
- Пробелы: у интерьера World Tree нет числовых координат (своя суб-карта); два конфликта
  координат помечены, а не разрешены (в `gaps`).

## data/items.json — база предметов (собрано 2026-07-14)

- **paldb.cc** (датасет v1.0.0 от 2026-07-10, дата релиза игры) — категории-индексы
  (Material, Ingredient, Consumable, Weapon, Armor, Accessory, Ammo, Sphere, Key_Items,
  Glider), 1269 карточек предметов (рецепты, дропы, торговцы, сундуки),
  paldb.cc/en/Technologies (tech-уровни). Скрипты: `scripts/collectors/fetch_items.py`,
  `parse_items.py`; сырые данные: `data/raw/item_slugs.json`, `item_meta.json`.
- 1195 предметов, 662 полных рецепта (цепочки компонентов полностью замкнуты),
  31 станция с tech-уровнями. `recipe.station` = станция минимального тира,
  альтернативы и размер партии — в notes предмета.
- 34 рецепта без станции на paldb (схематик/ивент-крафты, кроссовер-оружие) — оставлены
  null с пояснением в notes каждого; ~100 предметов без рецепта и источника (косметика
  из магазинов) перечислены в `gaps`.

## data/passives.json — пассивки (собрано 2026-07-14)

- **paldb.cc/en/Passive_Skills** — все 114 пассивок 1.0, тир-шкала −3..+5 (5 = новый
  золотой «World Tree»-тир); 109/114 с точными цифрами. Скрипты:
  `scripts/collectors/fetch_passives.py`, `fetch_passives_palworldgg.py`, `build_passives_json.py`.
- **palworld.gg/passive-skills** — кросс-чек (54 пересечения, 0 числовых конфликтов).
- Конфликты с docs/breeding_mechanics.md зафиксированы в `notes` файла: Emperor/Lord-пассивки
  в 1.0 дают +30% (в EA было +20%); Eternal Engine описан иначе. Пробелы: имена
  mutation-эксклюзивных пассивок не подтверждены (вероятно — 7 тир-5 «World Tree»-пассивок).

## data/pal_locations.json — где найти/поймать палов (собрано 2026-07-14)

- **paldb.cc** — 299 карточек палов + внутриигровые данные распределения спавнов
  (`DT_PaldexDistributionData.json`, ~19 МБ точек день/ночь, спроецированы на 68 именованных
  регионов 1.0 включая Sakurajima, Feybreak, Sky Islands, World Tree). Скрипты:
  `scripts/collectors/fetch_locations.py`, `fetch_paldex_distribution.py`,
  `build_locations_json.py`; промежуточные данные в `data/raw/`.
- Покрытие: дикие спавны 276/299 (в среднем ~4 региона на пала, по доле точек спавна);
  альфа-боссы с координатами 207/299; яйца 298/299; день/ночь 274/299 (12 ночных — список
  совпадает с известным поведением игры). 23 пала без дикого спавна — у каждого указан
  реальный способ получения (бридинг-комбо, рейд-яйцо, альфа).
- Websearch-факты: 11 Terraria-палов живут в данже Sealed Realm of Terraria; Astralym
  недоступен для получения (стори-босс).
- Пробелы: ассортимент торговцев/Black Marketeer не покрыт; имена регионов —
  аппроксимация «ближайшая метка».

## data/base_building.json — базостроение для конструктора баз (собрано 2026-07-14/15)

- **paldb.cc** (server-rendered, curl + regex-парсинг):
  - 58 страниц построек (категории Pal / Food / часть Production / Storage /
    Infrastructure) — tech level, флаг ancient tech (`Special_` в tech id), материалы
    (кросс-проверены против таблицы Materials/Product/Schematic — 0 расхождений),
    энергопотребление (`Energy X Per Sec`), Worker Max, описания.
  - **2026-07-15, дозаполнение до 125 структур**: изначальный сбор пропустил печи,
    верстаки, сборочные линии и всю категорию Lumbering/Mining. Полный список найден
    через индекс `/en/Structures` (487 зданий, декор/стены не собираем): +26 крафт-станций,
    +4 добывающих, +41 функциональное (шахты Coal/Sulfur/Quartz/Hexolite/Soralite,
    High-Pressure Oil Extractor, Guild Chest, пруды, алтарь, ресайклеры, сундуки).
    `worker_req` (Kindling+Cooling у Ancient Furnace и т.п.) — из описаний;
    min_level 6+ со слов игрока (PRELIMINARY). «Mine»/«Electric/Ice Mine» — ловушки.
    Две мои промежуточные ошибки зафиксированы и исправлены: «шахт нет» (промах по
    слагам) и заметка про Coal Mine в resource_nodes.
  - 56 страниц еды — Nutrition / SAN / Corruption (таймер порчи) / ворк-спид бафф;
    эффекты всех 5 тортов подтверждены текстами предметов 1.0.
  - 299 страниц палов — `FoodAmount` (аппетит, шкала 1–10, фактические значения 1–9) и
    `FullStomachDecreaseRate` (у всех = 1.0 в 1.0).
  - 12 страниц Work Suitability (`/en/Kindling` … `/en/Farming`) — точные таблицы
    work-speed по уровням 1–10, DropNumRate (Gathering ×1…×5.5), DamageRate
    (Lumbering/Mining), грузоподъёмность (Transporting), список исследований Research Lab.
- Веб-гайды 1.0 (nodecraft, palmods.gg, allthings.how, xgamingserver, neonlightsmedia):
  механика уровней пригодности 9–10 (Applied Handbook +1/книга per-pal, конденсация
  +1/звезда, партнёрские ауры +1 base-wide, пассивки), бридинг (5 мин/яйцо, 1 торт = 1 яйцо,
  Ancient Hatchery ~10 сек/цикл + 10 слотов, preliminary), инкубаторы (1/1/10/10 яиц),
  санити (Hot Spring rate 0.5), голод (пассивки ±10–20%, слайдер PalStomachDecreaceRate).
  Полный список URL — в `sources[]` внутри файла.
- Скрипты: `scripts/collectors/fetch_base_building.py` (сбор+парсинг, кэш страниц),
  `build_base_building.py` (сборка итогового JSON).
- Пробелы (в `gaps[]`): урожай грядок за цикл и абсолютные тайминги роста; базовая скорость
  голода/санити в ед./сек; точные множители скорости инкубаторов.
- Расхождение: paldb 1.0 даёт Pal Expedition Station tech 22 (Wooden Board 10, Stone 100,
  Paldium 20) против tech 15 в `expeditions.json` — требует перепроверки expeditions.json.

## Точечные правки по игровому опыту

- **2026-07-14, Coralum Ore через сальвадж-магниты** — сообщено пользователем из игры,
  подтверждено по paldb.cc/en/Powerful_Fishing_Magnet (лут-таблица сальваджа: Coralum Ore
  x1–2, 30%). Внесено в `items.json` (Coralum Ore, оба магнита) и `resource_nodes.json`.

## data/regions.json — координаты регионов карты (2026-07-15)

- Производное от `data/raw/paldb_region_labels.json` (метки регионов paldb с ipos):
  80 регионов → (x, y) центра метки. Покрывает 66/77 регионов из pal_locations
  (+ уровневые подзоны через отрезание суффикса `[Lv. X-Y]`). Входы в данжи
  для данжевых альфа-боссов не документированы — пробел.

## data/icons.json — карта "items" (иконки предметов, 2026-07-15)

- https://paldb.cc/en/Items (страница-список всех предметов): пары slug → cdn-URL иконки
  извлечены одним запросом (`scripts/collectors/fetch_item_icons.py`,
  кэш — `data/raw/item_icon_urls.json`). Покрытие 1195/1195 имён из items.json.
  4 предмета (Mythical Wooden Board, Potage, Sunreach Rapid-Fire/Single-Shot Ammo)
  на самом paldb имеют плейсхолдер `T_icon_unknown.webp` — оставлен как есть.
  NB: часть файлов cdn.paldb.cc отдаёт 403 без заголовка `Referer: https://paldb.cc/`.

## data/merchants.json — торговцы и магазины (2026-07-15)

- **paldb.cc/en/Merchant** — все 587 листингов «Wandering Merchant» (предмет → код
  магазина), 38 магазинов. **paldb.cc/en/<Shop_Code>** (38 страниц) — ассортимент,
  цены и валюта каждого магазина (пустая колонка цены = продажа за Gold Coin по
  стандартной цене предмета). **paldb.cc/en/Caravan_Merchant** + 23 страницы NPC —
  имена караванных торговцев 1.0 → коды Caravan_Shop_1–25 (посещают базу игрока).
  **paldb.cc/js/map_data_en.js** — точные координаты маркеров торговцев на карте:
  Wandering Merchant (4 поселения, href=Village_Shop_1), Duneshelter (Desert_Shop_1/2),
  Fisherman's Point (Volcano_Shop_1/2), Arena Merchant (631,16) = Arena_Shop_1
  (Battle Ticket), Medal Merchant (4 церкви) = Medal_Shop_1 (Dog Coin), PIDF Bounty
  Officer (3 поселения) = Bounty_Shop_1 (Successful Bounty Token); там же Pal
  Merchant / Black Marketeer (продают палов → `pal_traders`).
  Скрипт: `scripts/collectors/fetch_merchants.py` (резюмируемый, кэш страниц).
- В `items.json` 228 плейсхолдеров «Sold by merchants (N shop listings)» заменены на
  конкретные строки «Sold by <торговец> (<цена/валюта>) - <локация (координаты)>».
- Пробелы: Vagrant_Trader_1_1/2/3 — личность/локация не документированы (в т.ч.
  websearch 2026-07-15 ничего не дал); Wander_Shop_1 (случайный бродячий торговец) и
  Dungeon_Shop_01 (в данжах) фиксированных координат не имеют by design.

## docs/ — гайды (компиляции, собраны 2026-07-14)

- `breeding_mechanics.md` — game8.co (cake, инхерит пассивок, condenser, IV, пассивки),
  xgamingserver.com и hostedgg.com (Mutation/Awakening 1.0), palworld.fandom.com.
  Полный список URL — внизу самого файла.
- `boss_tower_counters.md` — game8.co, nexttier.pro, thepalprofessor.com,
  palworld.fandom.com, allthings.how.
- `base_setup.md` — palworld.wiki.gg (крафт-косты, Feybreak-эпоха → `(pre-1.0 guide)`).
- `guild_stash_and_storage.md` — компиляция wiki/гайдов Feybreak-эпохи, помечено где не перепроверено.

## Правила добавления записей

При каждом обновлении данных добавлять сюда (или в `sources[]` внутри JSON): URL источника,
что именно взято, дату получения. Не выдумывать значения: нет данных → null + запись в `gaps`.
