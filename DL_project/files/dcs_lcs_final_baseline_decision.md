# DCS/LCS baseline decision for geometric_edge and descriptors (2026-09-12)

## Правило сопровождения

Снимок на 2026-09-12. Это не новое измерение с нуля — почти всё уже посчитано в
файлах, написанных в этой же сессии (`descriptors_baseline_leak_confirmed.md`,
`geometric_edge_descriptors_baseline_selection_results.md`,
`lcs_geometric_edge_best_candidate_recheck.md`, `lcs_descriptors_and_protgeom8_
baseline_results.md`), процитированных ниже без пересчёта. Новое здесь: (1)
код-проверка, какой путь подгрузки дескрипторов реально используют текущие
кандидаты; (2) честная per-family таблица для DCS-линии `geometric_edge_mlp
_..._bilinear_norm*`, которой раньше не было в одном месте (`analysis/
dcs_geometric_edge_bilinear_norm_family_ranking.py`, новый, read-only,
`metrics_summary.csv` only); (3) сведение всех четырёх ответов в одно решение.
Ничего не обучалось и не пересчитывалось forward-pass'ом — везде, где нужен
`full_label_report.py`/`checkpoint_scores.py` и он не был выполнен, это сказано
явно, а не подставлено число из другого лейбла.

## 0. Итог

| Вопрос | Ответ | Раздел |
|---|---|---|
| DCS-baseline, geometric_edge | `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm` (голая база) — остаётся рекомендацией. Ни один из 16 сиблингов не выигрывает по всем семьям сразу; лучший по пулу (`_edge_raw3`, BA 0.559 против 0.552) выигрывает на IP_trans (+2.21σ) и scp2 (+1.14σ), но ПРОИГРЫВАЕТ на GLTP (−1.72σ) — разнонаправленный эффект, не общее улучшение. AUC против хим. нуль-модели **не посчитан ни для одного** варианта этой линии (требует `full_label_report.py`, форвард-пасс, не выполнялся). | 2 |
| DCS-baseline, descriptors | **Нет варианта, который стоит называть "рабочим baseline"** — оба кандидата дефектны по-своему. Старый канонический (`descriptors_no_extent_coarse_add_lipprop`, BA 0.589) несёт подтверждённую утечку семейства LBP_BPI_CETP (0.826 vs 0.549 на остальных). Новый честный (`descriptors_head_family_neutral_lipprop`) **проигрывает химической нуль-модели** на AUC (0.529 vs 0.596, margin −0.067) и на test AUC_within_protein_pairs. Явное, документированное состояние "нет прошедшего бар baseline'а", не "нужно ещё поискать". | 3 |
| LCS-baseline, geometric_edge | **Нет единого победителя — три оси расходятся.** По честной метрике проекта (`AUC_within_protein_pairs`, надёжные наборы anionic/choline) — `advprot`-семейство, лучший вариант `esm3_advprot` (БЕЗ `--balanced_lipid_classes`). По train-valid GAP и по стабильности обучения (`collapse_fraction`) — `liphid32`/`liphid64`/голый baseline, с большим отрывом. `advprot`-семейство проводит 25-55% эпох в полном коллапсе на choline/phosphorus_free; `liphid32` почти никогда не коллапсирует, но на choline (надёжный блок, n≈12) даёт AUC 0.35-0.50 — на уровне/ниже случайного. | 4 |
| LCS-baseline, descriptors | **Нет единого лидера среди 4 вариантов**, тот же паттерн, что у geometric_edge: база проваливается на choline ниже случайного (0.415), `rankprot`/`tailtokens` чинят choline (0.61) ценой худшей стабильности из всех 8 разобранных lcs-конфигов (geometric_edge+descriptors) — `collapse_fraction` до 0.59; `protgeom8` чинит anionic (0.577), но не choline. | 5 |
| Путь подгрузки дескрипторов — есть ли ещё аргумент кроме z-score? | Да, два, оба уже задокументированы, не новые находки: (a) `descriptor_catalog.md` §0 прямо называет `--protein_descriptors=` тем, что "используют текущие geometric_edge_* бейзлайны", а `--pocket_descriptors` — "старым, отдельным код-путём"; (b) `--pocket_descriptors`' собственные буферы нормализации (`pocket_descriptor_mean/std` в `ProteinEncoder`) заполняются **только** под `--rnabang_frozen_node_adapter` (`training/new_train.py:96-99`, проверено напрямую) — если бы кто-то использовал `--pocket_descriptors` для broadcast'а на узлы графа БЕЗ этого флага, канал остался бы нестандартизованным (mean=0/std=1 identity). Ни один из 4 целевых кандидатов этого не делает (см. §1). | 1 |

## 1. Путь подгрузки дескрипторов — перепроверка

**Вопрос:** есть ли в `lipid_coldsplit_architecture_direction.md`,
`descriptor_catalog.md`, `geometric_edge_and_solo_next_architecture.md`,
`reference_baselines_metrics_proposal.md` аргумент за конкретный путь подгрузки
дескрипторов кроме "оба train-only z-score".

**Найдено, оба факта уже в files, не новые:**

1. `files/descriptor_catalog.md` §0 (таблица "где какой набор физически
   подключается", строки 24-25): `--protein_descriptors=`/`--lipid_descriptors=`
   — "broadcast сырых именованных колонок `DESCRIPTOR_CATALOG` на каждую ноду...
   — **то, что используют текущие `geometric_edge_*` бейзлайны**"; `--pocket_
   descriptors` (+`--pocket_descriptor_names`/`--pocket_descriptors_family_
   neutral`) — "старый, фиксированный 13-широкий broadcast... отдельный
   код-путь от `--protein_descriptors`, хотя числа те же". Это прямо отвечает
   "какой путь используют текущие лучшие бейзлайны" — не про нормализацию, а
   про то, что один путь описан как действующий, другой — как legacy.
2. `files/reference_baselines_metrics_proposal.md` (раздел "descriptors-
   architecture lcs adaptation proposal", п.2, и `files/descriptors_baseline_
   leak_confirmed.md` строки 20-23) дают именно нормализационный аргумент, но
   с конкретным механизмом, не общей фразой: `DESCRIPTOR_CATALOG`-путь
   (`--descriptor_names`/`--protein_descriptors`) ВСЕГДА стандартизуется
   загрузчиком; `--pocket_descriptors`' буферы нормализации заполняются
   **только** под `--rnabang_frozen_node_adapter`.

**Проверено напрямую в коде в этой сессии** (не просто процитировано):
`training/new_train.py:96-99`:
```python
if conf.rnabang_frozen_node_adapter:
    model.set_pocket_descriptor_normalization(train_dataset.pocket_descriptor_stats())
    model.set_rnabang_normalization(train_dataset.rnabang_normalization_stats())
```
`architecture/protein_encoder.py:195-200/445-459`: `pocket_descriptor_mean`/
`pocket_descriptor_std` — отдельные `register_buffer`, инициализированные
`torch.zeros`/`torch.ones`, заполняются РЕАЛЬНОЙ train-only статистикой ТОЛЬКО
вызовом `set_pocket_descriptor_normalization`, который вызывается ТОЛЬКО внутри
`if conf.rnabang_frozen_node_adapter` выше. Если флаг не стоит — буферы
остаются identity (mean=0, std=1), и `expand_pocket_descriptor` кормит сеть
СЫРЫМИ значениями под видом стандартизованных.

**Касается ли это наших 4 целевых кандидатов? Нет.**
- Оба geometric_edge-кандидата (dcs `..._bilinear_norm`, lcs `..._advprot` и
  все её соседи) используют `--protein_descriptors=pocket_volume_per_sasa,...`
  (см. arg-файлы, проверено grep'ом) — путь (a), всегда нормализован через
  `descriptor_catalog_input`, независимо от `rnabang_frozen_node_adapter`.
- Канонический descriptors-baseline (`descriptors_no_extent_coarse_add_
  lipprop`) использует `--pocket_descriptors` + `--pair_descriptors
  --pair_descriptor_pocket_shares_coarse`, но под `--descriptors_head` ветка
  `ProteinEncoder` (где живёт `pocket_descriptor_mean/std`) вообще не строится
  (`protein1` не создаётся — `training/read_configuration.py`, п. C в
  `reference_baselines_metrics_proposal.md`); реально читаемые из
  `pocket_descriptor` значения (`aromatic_share`, `1-apolar_sasa_share`) —
  ограниченные [0,1] доли, банding'уются `_coarse_band`, читаются СЫРЫМИ по
  дизайну (`architecture/pair_descriptor_head.py:254-267`, докстринг: "no
  standardisation needed"), не через `pocket_descriptor_mean/std`.
- Новые честные descriptors-кандидаты (`descriptors_head_family_neutral_
  lipprop*`, dcs и lcs) используют `--descriptor_names=` — путь (a).

Вывод: гейтинг на `--rnabang_frozen_node_adapter` — реальный, воспроизведённый
код-факт, но он не задевает ни один из 4 сравниваемых здесь бейзлайнов; он
касается гипотетической/другой конфигурации (`--pocket_descriptors` вместе с
полной архитектурой БЕЗ `--descriptors_head`, например `bbp_smd_fa_pocket_
desc_nps3mlp_...`, не входит в объём этого сравнения). Ничего сверх этих двух
пунктов в `geometric_edge_and_solo_next_architecture.md` и в `lipid_coldsplit_
architecture_direction.md` про путь подгрузки не нашлось (грепнуты все три
термина `pocket_descriptors`/`protein_descriptors=`/`descriptor_names=`+
`rnabang` — в первом файле 0 совпадений, во втором только уже процитированное
в §201/366, ссылающееся на этот же `descriptor_catalog.md`).

## 2. DCS-baseline, geometric_edge (two-branch/cross-attention)

**Линия:** `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
fusion_bilinear_norm*` — база + 16 обученных вариантов (2 из 19 запланированных,
`hid4`/`lipid_descriptors`, не имеют чекпойнтов вовсе, см. `reference_
baselines_metrics_proposal.md` "Chemistry-null comparison" раздел).

**AUC против нуль-модели — недоступен для всей линии.** Раздел "AUC vs
chemistry null model" в `graphics/<label>/<label>.md` пуст у всех 17 (частью
из-за устаревшего отчёта, частью `SKIP_AUC=1`, см. таблицу в `reference_
baselines_metrics_proposal.md`) — заполнение требует `full_label_report.py`
(форвард-пасс по чекпойнтам), не выполнено в этой сессии по прямому запрету
("никогда не запускать код, который грузит чекпойнт... по своей инициативе").
Плоская колонка `AUC` в `metrics_summary.csv` тоже пуста для всех 17 строк этой
линии — это старые прогоны, test report хранит только confusion-counts, AUC
физически негде взять без пересчёта по сырым скорам.

**Честная per-family таблица (test, `balanced_accuracy`/`|sensitivity −
specificity|`/GAP/`collapse_fraction`, усреднено по 5 сидам на семью, ЗАТЕМ по
7 семьям — не пул строк)**, `analysis/dcs_geometric_edge_bilinear_norm_family_
ranking.py`:

| вариант | BA (mean of per-family) | \|gap\| (mean of per-family) | train-valid GAP | collapse_fraction |
|---|---:|---:|---:|---:|
| `_edge_raw3` | **0.559** | 0.480 | 0.018 | 0.044 |
| `_pocketonly` | 0.556 | 0.543 | 0.056 | 0.048 |
| `_cross_forced` | 0.555 | 0.499 | 0.058 | 0.048 |
| `_ckpt30` | 0.553 | 0.632 | 0.045 | 0.073 |
| **(база)** | 0.552 | 0.586 | 0.061 | 0.075 |
| `_edge_orient_rbf6` | 0.549 | 0.614 | 0.025 | 0.043 |
| ... 9 остальных вариантов ... | 0.519-0.548 | 0.524-0.651 | 0.032-0.170 | 0.043-0.077 |
| `_node_bilinear` | 0.537 | 0.599 | **−0.062** | **0.232** |
| `_lipid_class` | 0.519 | 0.624 | **0.170** | 0.070 |

Полная таблица (17 строк) — вывод скрипта, не сокращена искусственно, здесь
приведены верхние/нижние по интересности строки.

**Разница пул-лучшего (`_edge_raw3`) с базой — разнонаправленная, не общее
улучшение.** Парная per-family проверка (тот же скрипт):

| семья | база BA | `_edge_raw3` BA | diff | combined SEM (5 сидов на плечо) | σ |
|---|---:|---:|---:|---:|---:|
| GLTP | 0.536 | 0.444 | −0.092 | 0.054 | **−1.72** |
| IP_trans | 0.574 | 0.664 | +0.090 | 0.041 | **+2.21** |
| scp2 | 0.568 | 0.609 | +0.041 | 0.036 | +1.14 |
| LBP_BPI_CETP | 0.580 | 0.617 | +0.037 | 0.066 | +0.57 |
| CRAL-TRIO/START/lipocalin | ~0.52-0.56 | ~0.51-0.55 | −0.009…−0.010 | 0.027-0.040 | −0.23…−0.36 |

`_edge_raw3` выигрывает на IP_trans (значимо, +2.21σ) и проигрывает на GLTP
(−1.72σ, тоже почти значимо) — пулированный выигрыш (+0.007 BA) — это разница
между выигрышем на одной семье и проигрышем на другой, не улучшение,
воспроизводящееся по всем семьям (правило проекта — не судить по пулу).

**Дополнительно, качественная находка по всей линии, не только у топ-кандидатов:**
sensitivity систематически ниже specificity на КАЖДОЙ семье у КАЖДОГО из 17
вариантов (например, база: sens 0.16-0.44, spec 0.68-0.90 на всех 7 семьях) —
вся линия смещена в сторону предсказания "нет", а не какой-то один вариант.
`|gap|` в диапазоне 0.48-0.65 у ВСЕХ 17 — устойчивый, не зависящий от конкретной
правки признак этой линии в целом.

**Явно дефектные варианты (исключить из рассмотрения, не спорный выбор):**
`_node_bilinear` (train-valid GAP отрицательный при `collapse_fraction`=0.232 —
почти четверть эпох в полном коллапсе), `_lipid_class` (GAP 0.170, втрое выше
остальных).

**Рекомендация.** Держать голую базу (`geometric_edge_mlp_protgeom_family_
neutral_normalized_bilinear_fusion_bilinear_norm`) как DCS-baseline для
geometric_edge — она "architecture of record" в проекте (`geometric_edge_
descriptors_baseline_selection_results.md` §5), ни один сиблинг не даёт выигрыш,
устойчивый по семьям, а не по пулу. **Оговорка**: AUC против нуль-модели ни для
базы, ни для одного сиблинга не посчитан — сравнение по BA/sens/spec/gap выше
не отвечает на вопрос "бьёт ли эта линия голую химию", только на вопрос "какой
вариант линии внутренне лучше других". Заполнение этого пробела требует
`full_label_report.py --label <label>` по 17 лейблам (форвард-пасс, не
выполнялось, список точных лейблов и причин пустоты — таблица в `reference_
baselines_metrics_proposal.md` раздел "Chemistry-null comparison, full
bilinear_fusion line").

## 3. DCS-baseline, descriptors

**Нет варианта, который стоит рекомендовать как "работающий baseline".**
Полностью установлено в `files/descriptors_baseline_leak_confirmed.md` (не
пересчитывалось здесь):

| label | net_AUC (valid) | null_AUC_k15 | margin | что не так |
|---|---:|---:|---:|---|
| `descriptors_no_extent_coarse_add_lipprop` (старый канонический) | — | — | — | test BA 0.826 на LBP_BPI_CETP против 0.549 на остальных шести — подтверждённая утечка семейства, не сигнал |
| `descriptors_head_family_neutral_lipprop` (честный, family-neutral-7 + 4 липидных, `--descriptor_names=`) | 0.529 | 0.596 | **−0.067** | проигрывает хим. нуль-модели |
| `_rankprot` (+ pairwise-rank loss) | 0.516 | 0.596 | **−0.080** | тоже проигрывает, хуже базы |
| `_heads1` (`--HEADS=1`) | 0.536 | 0.596 | **−0.060** | пулом неотличим от базы; по семьям остаточная утечка LBP_BPI_CETP БОЛЬШЕ, чем у базы (0.241 vs 0.143 по BA gap) |

По семьям (`geometric_edge_descriptors_baseline_selection_results.md` §2.3):
family-neutral набор сокращает разрыв LBP_BPI_CETP vs остальные BA примерно
вдвое (0.277→0.143 у базы) относительно старого утёкшего baseline, но не до
нуля — остаточная, не объяснённая химией утечка на этой семье (n=2 белка)
держится у всех трёх честных вариантов. `rankprot` дополнительно вызывает
коллапс sensitivity на 4 из 9 семей (`scp2` 0.047/0.929, `ML` 0.120/0.880,
`GLTP` 0.296/0.904, `START` 0.262/0.706 sens/spec) — качественно хуже, не
просто "ниже по среднему".

**Два конфига, которые могли бы ответить на "работают ли pair-дескрипторы
сами по себе" (`descriptors_pair_clean`, `descriptors_head_family_neutral_
lipprop_pair`) не обучились вообще** — `--zscore` не существует как флаг
обучения (`ValueError: Unknown parameter`, `training/read_configuration.py:
3226`), 0 строк в `metrics_summary.csv` у обоих. Это баг в arg-файле, не
отрицательный результат — вопрос остаётся открытым (`geometric_edge_
descriptors_baseline_selection_results.md` §1/§5).

**Рекомендация.** Если нужен ЛЮБОЙ baseline для будущих сравнений архитектуры 2
на dcs — использовать честный `descriptors_head_family_neutral_lipprop`
(база, не `_heads1`/`_rankprot`), явно документируя, что он **сам проигрывает
нуль-модели** (margin −0.067) — то есть это "пол", а не "работающая модель".
Не использовать `descriptors_no_extent_coarse_add_lipprop` как эталон для
сравнения архитектур — его BA 0.589 полностью объяснена утечкой одной семьи.

## 4. LCS-baseline, geometric_edge

Полностью разобрано в `files/lcs_geometric_edge_best_candidate_recheck.md`
(не пересчитывалось, только сверено). Три оси расходятся:

| ось | лучший | почему |
|---|---|---|
| (a) `AUC_within_protein[_pairs]` test, надёжные наборы (anionic n≥11, choline n≥9-15) | `advprot`-семейство, лучший — `esm3_advprot` (БЕЗ `--balanced_lipid_classes`): anionic 0.548 (n=16.4), choline 0.672 (n=14.8) | `liphid32`/`liphid64` на choline на уровне/ниже случайного (0.352/0.504) |
| (b) train-valid GAP | `advprot`-семейство, лучший `rankprot_advprot` (0.06/−0.01/0.06/0.03 по 4 наборам) | adversarial-механизм режет GAP в 2-10× относительно baseline/liphid32 |
| (c) increment над хим. нуль-моделью, in-sample (частично измерено, только для 5 из ~22 сравнимых лейблов) | сиблинги advprot едва отличимы от нуля (0.000-0.025) — нет прямых чисел для advprot/liphid32 самих (секция сгенерировалась пустой без ошибки) | пробел измерения, не вывод |
| (d) `collapse_fraction` (стабильность) | `liphid32`/`liphid64`/голый baseline (≤0.01 доли эпох) | ЛЮБОЙ вариант advprot — 25-55% эпох в полном коллапсе на choline/phosphorus_free |

`phosphorus_free`/`sphingolipids` посчитаны на 2-3.4 белковых блоках в среднем
у всех конфигов — по правилу проекта выводов по ним не делается, независимо
от того, какое число получилось.

**По зафиксированной метрике проекта** (`project_lcs_primary_metric`:
ранжировать по `AUC_within_protein`, не по пулу) **advprot-семейство обгоняет
liphid32 на главной метрике**, но заметно уступает ему по стабильности
обучения — оба свойства измерены, что важнее — решение пользователя (правило
проекта: не указывать пользователю, что приоритизировать). Официальный
`..._balanced_lipid_classes_advprot` не является лучшим внутри собственной
семьи — `esm3_advprot` (без `--balanced_lipid_classes`) обгоняет его на обоих
надёжных наборах при большем числе читаемых белковых блоков и с меньшим
коллапсом на phosphorus_free (0.075 против 0.542).

**Известный пробел**: `AUC_within_protein_pairs` (честная метрика) для
`liphid64` — все 20 строк `NaN` в `metrics_summary.csv` (проверено напрямую в
этой сессии). Единственное, что есть — грубая `AUC_within_protein` (среднее по
белкам, не по парам): anionic 0.463 (n=11.0), choline 0.504 (n=11.25),
phosphorus_free 0.550 (n=1.5, ненадёжно), sphingolipids 0.635 (n=2.0,
ненадёжно). Пересчёт пар-версии требует `analysis/cross_sampler_eval.py`
(форвард-пасс по чекпойнтам) — не выполнялся в этой сессии; точная команда
(если нужно заполнить пробел): `cross_sampler_eval.py --labels
geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64 --sets
anionic,choline,phosphorus_free,sphingolipids --seeds 0,1,2,3,4 --epochs 120`.

## 5. LCS-baseline, descriptors

Разобрано в `files/lcs_geometric_edge_best_candidate_recheck.md` §9 и `files/
lcs_descriptors_and_protgeom8_baseline_results.md` §2 (не пересчитывалось).
4 варианта `descriptors_head_family_neutral_lipprop_lcs*`, все с family-neutral-7
+ 4 липидных, разница только в лоссе/токенах:

| конфиг | anionic (n=14.6) | choline (n=14.0) | phosphorus_free (n=7.8) | sphingolipids (n=2.0, ненадёжно) | collapse (сред./макс.) |
|---|---:|---:|---:|---:|---:|
| база | 0.556 | **0.415** (ниже случайного) | 0.533 | 0.255 | 0.002 / 0.017 |
| `_rankprot` | 0.486 | **0.615** | 0.467 | 0.448 | **0.146 / 0.592** |
| `_tailtokens` | 0.512 | **0.608** | 0.441 | 0.397 | 0.023 / 0.141 |
| `_protgeom8` | **0.577** | 0.447 | 0.465 | 0.541 | 0.012 / 0.042 |

Тот же паттерн, что у geometric_edge: база проваливается на choline ниже
случайного (0.415, надёжный n=14) — белковая маргиналь "бесплатна" под lcs, и
база её не убирает. `rankprot`/`tailtokens` чинят именно этот провал (0.61)
ценой стабильности (`rankprot` — 59% эпох в коллапсе на худшем (набор, сид));
`protgeom8` чинит anionic, но не choline. Increment над нуль-моделью (§9.3 того
файла, in-sample, pair-level): база НИЖЕ нуль-модели на pair-уровне на всех
четырёх наборах — architecture 2 не бьёт даже kNN-lookup под lcs, тот же вывод,
что и под dcs (§3 выше).

**Рекомендация.** Нет единого лидера среди 4 — выбор зависит от того, какой из
двух проваленных наборов (choline vs anionic) важнее закрыть, и готов ли
пользователь платить 15%-ным средним коллапсом (`rankprot`) за choline-сигнал.
Если нужен один "менее сломанный по умолчанию" вариант — `_tailtokens` чинит
choline почти так же (0.608 vs 0.615), но с на порядок меньшим collapse_fraction
(0.023 против 0.146 средних, 0.141 против 0.592 максимальных) — это единственная
пара кандидатов, где один Парето-доминирует другой на близких по силе осях (a)
и (d) одновременно; и то не абсолютно, т.к. `_tailtokens` немного хуже anionic
(0.512 vs 0.486, разница в пределах шума).

## 6. Чем посчитано

- Путь подгрузки дескрипторов (§1): `files/descriptor_catalog.md` §0 (строки
  17-32), `files/reference_baselines_metrics_proposal.md` (раздел "descriptors-
  architecture lcs adaptation proposal", п.2), `files/descriptors_baseline_
  leak_confirmed.md` (строки 16-23) — прочитаны напрямую; код-проверка
  `training/new_train.py:85-107`, `architecture/protein_encoder.py:160-239/
  440-518`, `architecture/interaction_classification.py:137-154`,
  `architecture/pair_descriptor_head.py:104-267` — прочитаны и прослежены
  вручную (какая функция кем вызывается, при каком условии), не запускались.
  Arg-файлы geometric_edge dcs/lcs baseline и descriptors_head_family_neutral_
  lipprop* — прочитаны напрямую (`cat scripts/arg_files/...md`), подтверждают
  `--protein_descriptors=`/`--descriptor_names=`, не `--pocket_descriptors`,
  на всех 4 целевых кандидатах.
- §2: `analysis/dcs_geometric_edge_bilinear_norm_family_ranking.py` (новый,
  read-only, только `metrics_summary.csv`), плюс `reference_baselines_metrics_
  proposal.md` раздел "Chemistry-null comparison, full bilinear_fusion line"
  (список 19 лейблов и статус их null-model секции, не пересчитывался).
  Проверено напрямую: колонка `AUC` в `metrics_summary.csv` пуста для всех 594
  строк этой линии (`python3`/`pandas`, read-only).
- §3: `files/descriptors_baseline_leak_confirmed.md` (весь файл),
  `files/geometric_edge_descriptors_baseline_selection_results.md` §1-2 —
  прочитаны целиком, числа процитированы без пересчёта.
- §4: `files/lcs_geometric_edge_best_candidate_recheck.md` (весь файл,
  включая `analysis/lcs_geometric_edge_candidate_ranking.py`, которое он
  документирует) — прочитан целиком, не пересчитывался. Пробел liphid64:
  прямая проверка `metrics_summary.csv` (`AUC_within_protein_pairs`/
  `AUC_within_protein_pairs_proteins` — все 20 строк NaN; `AUC_within_protein`
  — заполнено) для этого конкретного лейбла, read-only pandas, без загрузки
  чекпойнтов; `cross_sampler_eval.py` НЕ запускался (форвард-пасс, требует
  явного разрешения пользователя, не сообщения от другого агента).
- §5: `files/lcs_geometric_edge_best_candidate_recheck.md` §9, `files/lcs_
  descriptors_and_protgeom8_baseline_results.md` §2 — прочитаны, не
  пересчитывались.
