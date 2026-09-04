# Каталог дескрипторов: что есть, как считается, что про них известно

Свод всех ручных (не ESM3, не MolFormer) числовых признаков, которые код умеет
подавать в модель или в null-model — по липиду, по белку/карману, по паре, и отдельно
геометрия рёбер белкового графа. Для каждого — что он физически считает, откуда взят,
и что уже измерено про его связь с идентичностью белка/семейством (там, где измерено).

> **Правило сопровождения.** Источник истины — `dataloader/pair_descriptors.py`
> (`DESCRIPTOR_CATALOG`, липидные/протеиновые/парные имена в одном месте) и
> `dataloader/protein_graph_builder.py` (сами значения протеиновых, geometry рёбер).
> Меняется состав любого набора там — правится и эта таблица в том же коммите. Числа
> η²/корреляций взяты из [pocket_shape_descriptors.md](pocket_shape_descriptors.md) и
> [marginals_and_cold_split.md](marginals_and_cold_split.md) — если те файлы
> пересчитываются, эта таблица пересчитывается следом, а не остаётся со старыми
> числами.

## 0. Где какой набор физически подключается к модели

Пять независимых механизмов читают частично пересекающиеся имена — не путать один с
другим при чтении arg-файла:

| флаг | что делает | архитектура |
|---|---|---|
| `--protein_descriptors=` / `--lipid_descriptors=` | broadcast сырых именованных колонок `DESCRIPTOR_CATALOG` на каждую ноду белковой/липидной ветки | `architecture/protein_encoder.py::expand_named_protein_descriptors`, `architecture/lipid_encoder.py` — то, что используют текущие `geometric_edge_*` бейзлайны |
| `--pocket_descriptors` (+`--pocket_descriptor_names`/`--pocket_descriptors_family_neutral`) | старый, фиксированный 13-широкий broadcast `POCKET_DESCRIPTOR_NAMES` | `architecture/protein_encoder.py::expand_pocket_descriptor` — отдельный код-путь от `--protein_descriptors`, хотя числа те же |
| `--pair_descriptors` / `--descriptors_head` | self-attention голова над маленьким фиксированным набором токенов (aromatic_share, polar_share, extent, chain/unsaturation/hbond/heavy…) | `architecture/pair_descriptor_head.py::PairDescriptorHead` — отдельная архитектура, без белковой/липидной ветки вообще, не складывается с `bilinear_fusion` |
| `--two_pair_descriptors_paths` / `--good_descriptors` / `--bad_descriptors` | явный именованный признак из `DESCRIPTOR_CATALOG` (тот же каталог, что у `--protein_descriptors`) как отдельный вход | `architecture/named_descriptor_head.py::NamedDescriptorHead` |
| `--protein_edge_mlp` / `--protein_edge_attention` | геометрия рёбер белкового графа (раздел 5 ниже) | `architecture/protein_edge_geometry.py` — ортогонально всем четырём выше (рёбра, не ноды) |
| `--thematical_paths` (+`--geometric_descriptors=`/`--chemical_descriptors=`) | два именованных набора, каждый расщеплён на липидную/протеиновую сторону и принудительно перемножен (без skip-пути для сырых сторон) в один вектор группы, затем группы — друг с другом | `architecture/thematic_descriptor_head.py::ThematicDescriptorHead`/`ForcedInteraction` — третья sufficiency-test ветка, sibling `--descriptors_head`/`--two_pair_descriptors_paths`; полный разбор в [thematic_interaction_architecture.md](thematic_interaction_architecture.md) |

`analysis/null_model.py --features` читает тот же `DESCRIPTOR_CATALOG` независимо от
того, что подано в саму сеть — это отдельный, безобучаемый бейзлайн для сравнения.

## 1. Липидные дескрипторы (`LIPID_DESCRIPTOR_NAMES`, 13, `pair_descriptors.py:51`)

Все — из 2D RDKit-структуры (SMILES), без докинга и позы; мотивация — Lipovsky et al.,
Nature 2025 (см. модульный docstring `pair_descriptors.py`).

| имя | считает | функция |
|---|---|---|
| `chain` | число атомов C в самом длинном неароматическом нециклическом пути (длина ацильного хвоста) | `longest_acyl_chain` |
| `unsaturation` | число неароматических C=C двойных связей | `unsaturation_count` |
| `hbond` | RDKit доноры + акцепторы H-связи (прокси полярности головы) | `hbond_capacity` |
| `heavy` | число тяжёлых атомов (прокси объёма лиганда) | `heavy_atom_count` |
| `tail_count` | сколько ОТДЕЛЬНЫХ ацильных хвостов ≥ минимальной длины (не путать с `chain` — одно число на молекулу, а не на хвост) | `acyl_chain_count` |
| `npr1` | медианное по 10 ETKDG+MMFF конформерам PMI1/PMI3 — вытянутость 3D-формы, липидный аналог `pocket_elongation` | `npr1` (единственные два, требующие 3D-эмбеддинга конформера) |
| `npr2` | медианное PMI2/PMI3 — плоскостность, аналог `pocket_flatness` | `npr2` |
| `logp` | Crippen logP (октанол/вода) | `Descriptors.MolLogP` |
| `tpsa` | топологическая полярная площадь поверхности, Å² | `Descriptors.TPSA` |
| `molar_refractivity` | RDKit молярная рефракция — аналог `pocket_volume_per_sasa` для лиганда | `Descriptors.MolMR` |
| `rotatable_bond_count` | число вращаемых связей (абсолютное) | `rdMolDescriptors.CalcNumRotatableBonds` |
| `aromatic_ring_count` | число ароматических колец — аналог `aromatic_share` | `rdMolDescriptors.CalcNumAromaticRings` |
| `ring_count` | всего колец (ароматика + алифатика) | `rdMolDescriptors.CalcNumRings` |

**Что известно про идентичность.** Формальной Mantel/η²-проверки «дескриптор =
отпечаток класса/вида липида» для этого набора **не проводилось** — вся такая проверка
в проекте была сделана только для протеиновой стороны (раздел 2), потому что именно
холодный разрез по семейству белков — это ось, которую скрывает `--double_coldsplit`.
Единственная связанная находка: у `LBP_BPI_CETP` необъяснённая утечка на
`descriptors_path` (project memory `descriptors-path-fingerprint-leak`,
[signal_state.md §8](signal_state.md)) — среди неисключённых подозреваемых остаются
именно четыре липид-only токена `chain`/`unsaturation`/`hbond`/`heavy`, специфичные для
того, какие классы липидов исключены на этом семействе. Не доказано, флаг открыт.

## 2. Протеиновые/карманные дескрипторы (`PROTEIN_DESCRIPTOR_NAMES`, 15,
`pair_descriptors.py:115`, значения — `protein_graph_builder.py::pocket_descriptor`)

Считаются по остаткам кармана (`coarse_graph_nodes.csv`) и атомам кармана
(`pocketness.pdb`) — подробный разбор геометрии в
[pocket_shape_descriptors.md](pocket_shape_descriptors.md) §2–3.4. Единица измерения
семейственности — η² по 9 семействам на 35 белках; пол случайного числа при таком n —
**0.235** (не 0). Ниже — все 15, с флагом, входит ли имя в `--protein_descriptors=` у
текущих `geometric_edge_*_family_neutral*` бейзлайнов.

| имя | считает | η² (семья) | в family-neutral 7? |
|---|---|---|---|
| `pocket_sasa_share` | доля SASA кармана от SASA всего белка | **0.85** | нет — почти ярлык семейства |
| `hydropathy_core` | средняя гидропатия Кайт-Дулиттла в глубокой половине кармана | **0.77** | нет |
| `pocket_residue_share` | доля остатков белка, входящих в карман | **0.71** | нет |
| `pocket_extent` | размах вдоль главной оси кармана, Å (5–95 перцентиль) | **0.62** | нет |
| `ev14_q50` | медиана ev14 (закрытость) по остаткам кармана | **0.59** | нет |
| `depth_q10` | 10-й перцентиль voromqa-глубины — самые мелкие остатки кармана | **0.55** | нет |
| `pocket_flatness` | √λ2/√λ3 облака атомов кармана — щель против трубки | 0.48–0.40 | **да** |
| `pocket_volume_per_sasa` | Σ объём остатков / Σ SASA — гидравлический радиус | 0.48–0.40 | **да** |
| `apolar_sasa_share` | доля неполярной SASA кармана | 0.48–0.40 | **да** |
| `buriedness_q50` | медиана voromqa-закрытости остатков кармана | 0.32–0.28 | **да** |
| `aromatic_share` | доля Phe/Trp/Tyr среди остатков кармана | 0.32–0.28 | **да** |
| `pocket_elongation` | √λ1/√λ2 — трубка против чаши | 0.32–0.28 | **да** |
| `hydropathy_rim` | средняя гидропатия на устье (мелкая половина) кармана | 0.32–0.28 | **да** |
| `ev28_q10` | 10-й перцентиль ev28 по остаткам кармана | 0.134 | нет (отдельно, `rim_ev28`-вариант) |
| `aromatic_share_rim` | доля ароматики на устье кармана | 0.152 | нет (отдельно, `rim_ev28`-вариант) |

Family-neutral 7 = `pocket_volume_per_sasa, pocket_elongation, pocket_flatness,
buriedness_q50, apolar_sasa_share, aromatic_share, hydropathy_rim` — используются во
всех текущих `geometric_edge_*_family_neutral*` бейзлайнах. `ev28_q10`/
`aromatic_share_rim` — те же по η², но добавлены отдельным вариантом (`..._rim_ev28`,
[signal_state.md §10](signal_state.md)), не входят в дефолтные семь.

**Связь с реальной целью (не с семьёй), где измерялась** (`pocket_shape_descriptors.md`
§4, §4a — частная корреляция с длиной ацильной цепи/числом классов головных групп,
контроль на размер белка):

| дескриптор | цель | частная ρ | устойчиво по семьям? |
|---|---|---|---|
| `pocket_volume_per_sasa` | длина цепи | **−0.475** | нет — межсемейственный эффект, внутри семей знак меняется |
| `depth_q10` | длина цепи | −0.407 (pooled) | **да** — −0.434/−0.683 в двух отдельных семьях, тот же знак |
| `pocket_gyration`* | длина цепи | +0.443 | не проверено внутри семей |
| `pocket_extent` | длина цепи | +0.356 | не проверено |
| `hydropathy_core` | число классов голов | +0.403 | **да** — совпадает в CRAL-TRIO и lipocalin |
| `aromatic_share_rim` | число классов голов | +0.214 | да — CRAL-TRIO +0.312, lipocalin +0.220 |
| `ev28_q10` | число классов голов | −0.267 | нет — знак не устойчив |

\* `pocket_gyration` — исследовательский, не входит в 15 продакшн-имён (см. раздел 3).

**Вывод, который держит весь дизайн family-neutral отбора**: у `pocket_sasa_share` и
`pocket_residue_share` — САМАЯ высокая семейственность (0.85/0.71) И единственная
измеренная связь с длиной цепи среди старого набора — то есть предсказывает цепь ровно
то, что кодирует семью. `depth_q10` и `hydropathy_core` — противоположный случай:
выше пола (0.55/0.77), но проверены отдельно и держат один и тот же знак связи внутри
разных семейств, то есть несут что-то помимо ярлыка. Это ровно та пара, которую сейчас
пробуют `..._hydrocore_depthq10` arg-файлы — сознательно жертвуя family-neutrality ради
проверки, есть ли за ней реальный сигнал.

## 3. Исследовательские дескрипторы (не в продакшн-наборе, `pocket_shape_descriptors.md` §7)

18 чисел, которые `analysis/pocket_shape_vs_binding.py` считает из тех же файлов на
диске, но которые никогда не доходили до `POCKET_DESCRIPTOR_NAMES` — доступны только
скриптам анализа, не флагам обучения:

| дескриптор | η² | заметка |
|---|---|---|
| `ev28_q90` | 0.894 | насыщен у большинства белков (см. §3.5 pocket_shape_descriptors.md) |
| `pocket_gyration` | 0.789 | единственный размерный, физически связанный с длиной цепи (+0.443) — но второй по семейственности из всех 31 проверенных |
| `pocket_width` | 0.759 | ось v2 облака атомов кармана |
| `pocket_thickness` | 0.693 | ось v3 |
| `ev56_q10` | 0.653 | |
| `hydropathy_mean` | 0.611 | среднее по всему карману (core+rim не разделены) |
| `ev28_q50` | 0.609 | |
| `buriedness_q10` | 0.593 | |
| `depth_q50` | 0.561 | |
| `ev14_q90` | 0.559 | |
| `aromatic_share_core` | 0.490 | |
| `buriedness_q90` | 0.480 | |
| `depth_q90` | 0.352 | |
| `ev14_q10` | 0.238 | на самом полу, погранично |
| `ev56_q50`, `ev56_q90` | — | вырождены, насыщены у всех белков, η² не определён |

Только `ev14_q10` (0.238) вплотную подходит к порогу семейной нейтральности среди этих
18 — расширять family-neutral набор есть чем, но на 1 число, не на 18.

## 4. Производные протеиновые (`PROTEIN_DERIVED_DESCRIPTOR_NAMES`, 3,
`pair_descriptors.py:165`)

Читаются только `PairDescriptorHead` (`--pair_descriptors`), не broadcast-механизмом
раздела 0:

| имя | считает |
|---|---|
| `polar_share` | `1 − apolar_sasa_share` |
| `aromatic_share_coarse` | `aromatic_share`, забинованное в 3 квантильных бина (train-fit) |
| `polar_share_coarse` | `polar_share`, та же схема |

Отдельно `extent` в `DESCRIPTOR_CATALOG` — не сырой `pocket_extent`, а его train-fit
коарсенная, leak-safe версия, которую `PairDescriptorHead` и compat-механизм читают
вместо сырого значения на холодном сплите (`Dataloader.py`'s `coarse_extent`).

## 5. Парные дескрипторы (`PAIR_DESCRIPTOR_NAMES`, 11, `pair_descriptors.py:57`,
формулы — `pair_descriptor_value`)

Комбинируют одно липидное и одно протеиновое значение в одно число — «безобучаемая»
версия того, что self-attention `PairDescriptorHead` должен бы находить сам. Используются
и как признаки `analysis/null_model.py --features`, и как входы `NamedDescriptorHead`
(`--good_descriptors`/`--bad_descriptors`).

| имя | формула | что означает |
|---|---|---|
| `occupancy` | `relu(chain_length_Å − pocket_extent)` | превышение хвостом длины кармана (клэш), 0 если хвост короче |
| `chain_extent_gap` | `pocket_extent − chain_length_Å` (со знаком) | тот же зазор без обрезки — насколько карман длиннее/короче хвоста |
| `aromatic_contact` | `aromatic_share × unsaturation` | ароматика кармана встречает ненасыщенность хвоста (π-контакт) |
| `hbond_match` | `polar_share × hbond` | полярность кармана встречает H-донор/акцептор головы |
| `volume_fit` | `pocket_volume_per_sasa × heavy` | объёмная замкнутость кармана против объёма лиганда |
| `buriedness_match` | `buriedness_q50 × heavy` | закрытость кармана против объёма лиганда |
| `depth_bulk_match` | `depth_q10 × heavy` | мелкая часть кармана против объёма лиганда (НЕ сигнатура зазора, а произведение — единицы разные) |
| `hydropathy_chain_match` | `hydropathy_core × chain` | гидрофобность ядра против длины хвоста |
| `aromatic_contact_min` | `min(z(aromatic_share), z(unsaturation))` | bottleneck-версия `aromatic_contact` — узкое место, не среднее |
| `hbond_match_min` | `min(z(polar_share), z(hbond))` | bottleneck-версия `hbond_match` |
| `tail_elongation_fit` | `tail_count / max(pocket_elongation, 1.0)` | сколько отдельных хвостов форма кармана может вместить side-by-side |

**Что известно про утечку.** Прямая проверка была не для этого каталога целиком, а для
механизма `pair_descriptor_pocket_shares` (aromatic_share/polar_share и их coarse-версии,
раздел 4) на `descriptors_path`: `LBP_BPI_CETP` даёт test BA 0.796–0.826, не объяснённую
ни белко-слепой химией, ни pocket_extent (проверено раздельно, см.
[signal_state.md §8](signal_state.md)) — источник до сих пор не найден среди проверенных
каналов; `pocket_extent`, `pocket_shares` raw/split/coarse — все исключены измерением.
Для `lipocalin`, наоборот, `pocket_extent` — правдоподобный (η²-проверенный на прямое
разделение групп, p=0.0028) канал увеличения BA. Остальные 9 из 11 записей этого раздела
(occupancy, aromatic_contact, hbond_match, volume_fit, buriedness_match, depth_bulk_match,
hydropathy_chain_match, оба `_min`, `tail_elongation_fit`) отдельно на утечку **не
проверялись**.

## 6. Геометрия рёбер белкового графа (`architecture/protein_edge_geometry.py`)

Единственная категория здесь, которая не про химию — про голую геометрию упаковки
кармана, независимо от того, какой это остаток.

**Дефолтный путь (без `--protein_edge_mlp`/`--protein_edge_attention`)**: 3 сырых
скаляра Voronota-контакта на ребро — `distance`, `area` (площадь контакта), `boundary`
(длина границы контакта). Не SE(3)-инвариантны отдельно, но при этом абсолютны
(расстояние в Å, площадь в Å²) — не завязаны на выбор системы координат по построению,
раз это межатомные величины.

**Структурированный путь (`--protein_edge_mlp`/`--protein_edge_attention`,
`structured_edge_features`)**: 25-мерный SE(3)-инвариантный вектор на **направленное**
ребро (обе стороны строятся нативно, не зеркалированием — направление и кватернион
зависят от ориентации):

| компонент | размер | как считается |
|---|---|---|
| RBF-расстояние | 16 | гауссова экспансия `distance` (пересчитан из `frame_translation`, не взят из старого `edge_attr`) на 16 центров, 2–22 Å |
| локальное направление | 3 | единичный вектор `j − i` в локальной системе координат остатка `i` (поворот `Rᵢᵀ`) |
| относительный кватернион | 4 | ориентация `Rⱼ` относительно `Rᵢ` |
| `log1p(area)` | 1 | площадь контакта, та же величина, что в дефолтном пути, только сжатая log1p |
| `log1p(boundary/area)` | 1 | форма контакта (вытянутый против компактного), нормированная на почти-вырожденные контакты |

Источник рёбер (Voronota contact graph) и жёсткие фреймы (rotation+translation по Cα) —
общие для обоих путей; структурированный путь только переупаковывает те же 3 сырых
числа плюс геометрию фреймов в 25 инвариантных.

**Что известно про идентичность.** **Не измерялось.** В отличие от раздела 2 (где для
каждого протеинового дескриптора посчитан η² по семье, Mantel-тест против ESM3 и
nearest-neighbour-по-семье), для геометрии рёбер аналогичной проверки никто не делал —
ни для 3 сырых скаляров, ни для 25-мерного структурированного вектора. Это открытый
пробел: правдоподобно, что топология/степенное распределение контактного графа кармана
само по себе коррелирует с семейством (аналогично тому, как `pocket_gyration`/
`pocket_extent` коррелируют, раздел 2–3), но это не проверено ни в одну, ни в другую
сторону.

## 7. Базовые узловые признаки белка (`BASE_NODE_COLUMNS`/`EXTRA_NODE_COLUMNS`,
`protein_graph_builder.py:27-29`)

То, что реально лежит в `node` до broadcast любых дескрипторов разделов 2/4 сверху —
единственный канал, различающий строки внутри одного и того же кармана (broadcast
разделов 2/4 даёт всем нодам одного белка одно и то же число).

| колонка | считает | по умолчанию включена? |
|---|---|---|
| `residue_type` | ordinal-код аминокислоты 0–19 (Voronota алфавитный порядок `A R N D C Q E G H I L K M F P S T W Y V`), **сырое число**, не one-hot/embedding | да (`--no_protein_geometry` убирает) |
| `residue_sas_area` | SASA остатка | да |
| `residue_volume` | объём остатка (Voronoi-ячейка) | да |
| `residue_mean_ev28` | закрытость остатка (ev28) | только `--protein_extra_node_features` |
| `residue_mean_ev56` | закрытость остатка (ev56) | только `--protein_extra_node_features` |
| гидрофобность (Кайт-Дулиттл, по `residue_type`) | добавляется третьей к EXTRA | только `--protein_extra_node_features` |
| `residue_mean_buriedness` (`bury`) | закрытость остатка, отдельный тензор | только `--buryon` |

**Что известно про идентичность.** Не измерялось в том же смысле, что раздел 2 — это
per-residue величины (разные внутри одного белка), а не одно число на белок, поэтому
проверка «η² по семье»/Mantel против ESM3 (которая сравнивает облака ИЗ ОДНОГО ЧИСЛА НА
БЕЛОК) на них напрямую не ставилась. `residue_type` заведомо кодируется как сырой
ordinal-float, не как embedding/one-hot — архитектурный дефект, не измерение (см.
предложение (d) в обсуждении фич выше по треду: заменить на `nn.Embedding`).

## 8. Итоговый счёт `DESCRIPTOR_CATALOG`

`DESCRIPTOR_CATALOG = LIPID_DESCRIPTOR_NAMES(13) + ("extent",) +
PROTEIN_DESCRIPTOR_NAMES(15) + ("polar_share",) + PAIR_DESCRIPTOR_NAMES(11)` — 41
именованных токена всего, читаемых `--protein_descriptors`/`--lipid_descriptors`/
`--good_descriptors`/`--bad_descriptors`/`analysis/null_model.py --features` одним и тем
же `parse_descriptor_list`/`full_catalog_order` (`pair_descriptors.py`). Плюс 18
исследовательских протеиновых (раздел 3, не в каталоге, только `analysis/`-скрипты) и
геометрия рёбер (раздел 6, отдельный код-путь, не имена).
