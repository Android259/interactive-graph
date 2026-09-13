# Разбор 33 прогонов (2026-09-11): что из предложений подтвердилось для geometric_edge и descriptors

> **Пометка 2026-09-12**: везде ниже, где `..._lcs_esm3_balanced_lipid_classes_advprot`
> называется "текущим лучшим lcs-baseline/кандидатом" (§0 п.6, §4, §5) — это устарело.
> Честное трёхосевое сравнение (`AUC_within_protein`, train-valid GAP,
> `collapse_fraction`) с `liphid32` и другими сиблингами `advprot` — в
> [lcs_geometric_edge_best_candidate_recheck.md](lcs_geometric_edge_best_candidate_recheck.md).
> Числа этого файла не переписаны, только помечены как неполные без того сравнения.

## Правило сопровождения

Снимок на 2026-09-12. Разбираются 7 конфигов (script_logs `*_seeds01234`/`*_lipidsets`,
все завершились 2026-09-11), которые должны были проверить предложения из
`files/geometric_edge_and_solo_next_architecture.md`,
`files/descriptors_baseline_leak_confirmed.md`,
`files/reference_baselines_metrics_proposal.md` и `files/lipid_coldsplit_architecture_direction.md`
(§7.1/§7i/§7j/§7n/§8). Числа взяты из `metrics_summary.csv`, свежесгенерированных
`graphics/<label>/<label>.md` и сырых `script_logs/*/*.log`; ничего не обучалось,
ни один чекпойнт не грузился. `files/interaction_embedding_design.md`,
`files/solo_family_report.md`, `files/structural_pretrain_family_diagnosis.md`
прочитаны, но ни один из 7 конфигов их не проверяет (все три — про линию `solo`/
`structural_pretrain_family`, которой в этой партии нет) — не разбираются ниже.

**Первая находка, которая должна была быть очевидна из названий конфигов, но не была
оговорена в задании: из 7 конфигов только ОДИН (`geometric_edge_mlp_protgeom_full_lcs`)
реально прогнан под `--lipid_coldsplit`.** Остальные шесть (все пять `descriptors_*` и
`geometric_edge_attention_..._bilinear_fusion`) стоят на `--double_coldsplit=1`
(протеиновая ось, exclusion_set = семейство белка), проверено по колонкам
`lipid_coldsplit`/`double_coldsplit`/`exclusion_set` в `metrics_summary.csv` (§0 в
разделе "чем посчитано"). Это отдельная, официально отложенная ось (`project_lipid_
coldsplit_primary` в памяти проекта), но именно на ней стоит вся ветка про утечку
дескрипторного baseline (`descriptors_baseline_leak_confirmed.md`) — поэтому она
разбирается ниже как есть, с явной пометкой "double_coldsplit", а не подгоняется под
рамку "липидный колдсплит".

## 0. Итог

| # | Вопрос | Ответ | Раздел |
|---|---|---|---|
| 1 | Все ли 7 конфигов вообще обучились? | Нет. 2 из 7 (`descriptors_pair_clean`, `descriptors_head_family_neutral_lipprop_pair`) упали на разборе конфига до первой эпохи на ВСЕХ семьях и сидах — `--zscore` не существует как флаг обучения, это флаг только у `analysis/*.py`-скриптов. 0 строк в `metrics_summary.csv`, 0 обученных эпох. | 1 |
| 2 | На какой оси реально прогнаны остальные 6? | 5 `descriptors_*` + 1 `geometric_edge_attention_*` — на `--double_coldsplit` (протеин); 1 `geometric_edge_mlp_protgeom_full_lcs` — на `--lipid_coldsplit`. | см. врезку выше |
| 3 | Какой из 3 выживших descriptors-вариантов лучший? | Ни один не бьёт химическую нуль-модель (валид-сплит). `heads1` ≈ `base` (эффекта нет, ни пулом, ни по семьям). `rankprot` хуже `base` и вызывает коллапс sensitivity на 4 из 9 семей. | 2 |
| 4 | Держится ли утечка LBP_BPI_CETP после честных (family-neutral) дескрипторов? | Уменьшается (BA 0.826→0.68-0.78), но не исчезает и не объясняется химией нацело — сеть по-прежнему обходит нуль-модель именно на этой семье во всех трёх вариантах. `heads1` уменьшает утечку МЕНЬШЕ, чем `base`, при равном отсутствии среднего эффекта. | 2.3 |
| 5 | mlp vs attention для geometric_edge (double_coldsplit)? | На честной тест-метрике (BA по семьям) — практически ничья (0.564 vs 0.566, 7 семей). На валид-сплитовой нуль-модельной поправке — mlp впереди (+0.057 против +0.018 у margin к нулю), но это тот же исторический результат "mlp > attention", уже виденный на lcs-ветке `_bilinear_norm_lcs_esm3`, не новое открытие. Обе линии унаследовали известную нестабильность "bare"-конфигурации (`--bilinear_fusion` без `--bilinear_pooled_norm`) — лосс взрывается на части сидов у ОБЕИХ (mlp тоже, до 93×, не только attention). | 3 |
| 6 | Что показал единственный lcs-прогон (`geometric_edge_mlp_protgeom_full_lcs`)? | Он одновременно меняет 3 переменные относительно текущего лучшего lcs-baseline (`..._lcs_esm3_balanced_lipid_classes_advprot`): снимает ESM3, меняет 7 family-neutral дескрипторов на 15 "полных", и `--balanced_lipid_classes` заменяет на `--balanced_proteins` — то есть НЕ является чистой проверкой ни одного предложения по отдельности. Вдобавок 6 из 20 прогонов (сид×набор) показывают патологический коллапс (sens/spec к 0/1, лосс до 244× нормы, флаг `converged=1`, т.е. пайплайн сам отметил незавершённую сходимость). | 4 |
| 7 | Появился ли новый рабочий baseline? | Нет ни для одной архитектры. Для descriptors — по-прежнему нет конфигурации, бьющей нуль-модель (что и предсказывал `descriptors_baseline_leak_confirmed.md`); 2 самых интересных кандидата (`pair`, `pair_clean`) остались непроверенными из-за бага. Для geometric_edge — mlp остаётся architecture of record, но эта партия прогонов не добавляет к этому ничего решающего: attention-бейзлайн не бьёт mlp ни на одной честной тест-метрике настолько, чтобы это отличалось от нуля, и не проигрывает тоже. | 5 |

## 1. Два конфига не обучились: `--zscore` не существует как флаг training

`scripts/arg_files/descriptors_pair_clean.md` и `scripts/arg_files/descriptors_head_family_neutral_lipprop_pair.md`
оба содержат строку `--zscore`. Она реально существует — но только как флаг
`argparse` в `analysis/null_model.py`, `analysis/full_label_report.py`,
`analysis/feature_identity_check.py`, `analysis/interaction_increment.py`,
`analysis/rank_pair_descriptors.py`, `analysis/lipid_coldsplit_null_model.py`,
`analysis/pair_descriptor_family_eta2.py` — все read-only анализные скрипты,
не `training/read_configuration.py`. У обучающего парсера такого параметра нет:

```
ValueError: Unknown parameter: --zscore
  (training/read_configuration.py:3226, read_named_configuration)
```

Ошибка воспроизведена во ВСЕХ проверенных логах обоих конфигов (все 9 семей ×
5 сидов у каждого — проверено выборочно по CRAL-TRIO/START/LBP_BPI_CETP/OSBP/ML для
`descriptors_pair_clean`, идентичный traceback у `descriptors_head_family_neutral_
lipprop_pair`). Ни один прогон обоих конфигов не дошёл до первой эпохи. Как
следствие: `metrics_summary.csv` не содержит ни одной строки с этими лейблами,
`graphics/descriptors_pair_clean/*.md` и `graphics/descriptors_head_family_neutral_
lipprop_pair/*.md` содержат только текст ошибки.

**Значение для проекта.** Это два конфига, которые по замыслу должны были проверить
самое интересное в этой партии: `pair_clean` — несут ли 10 "чистых" pair-дескрипторов
(`aromatic_contact`, `hbond_match`, `volume_fit`, ... — `PAIR_DESCRIPTOR_NAMES`) сигнал
сами по себе, без сырых protein/lipid признаков; `pair` — работает ли комбинация всех
21 признака (4 липидных + 7 протеиновых + 10 парных) вместе. Оба вопроса остаются
полностью непроверенными, не "опровергнутыми" — это баг в arg-файле, а не результат.
Правка — убрать `--zscore` из обоих arg-файлов (сами `--descriptor_names` уже проходят
через `DESCRIPTOR_CATALOG`, которое `training/read_configuration.py`/`dataloader/
pair_descriptors.py` всегда стандартизует само, независимо от какого-либо флага — см.
`descriptors_baseline_leak_confirmed.md`'s собственное описание пути `--descriptor_names`).

## 2. Descriptors architecture, double_coldsplit: 3 выживших конфига, ни один не бьёт нуль-модель

Три сохранившихся варианта — `descriptors_head_family_neutral_lipprop` (база, 35
строк/7 семей), `_heads1` (`--HEADS=1` вместо дефолтных 8 в self-attention над
дескрипторными токенами `NamedDescriptorHead`, 45 строк/9 семей), `_rankprot`
(`--loss_type=pairwise_rank --rank_within_protein`, 45 строк/9 семей). Общий набор
признаков (11): `chain,unsaturation,hbond,heavy` (липид) +
`pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,
apolar_sasa_share,aromatic_share,hydropathy_rim` (protein family-neutral, те же 7,
что у geometric_edge).

### 2.1 Пулированный margin против химической нуль-модели (VALID-сплит — не test)

`analysis/full_label_report.py` по умолчанию считает раздел "AUC vs chemistry null
model" на `--split valid` (сам скрипт: `choices=("valid","test","both")`, default
`"valid"`), и во всех проверенных отчётах в заголовке стоит буквально
`########## split = valid ##########`. Значит следующая таблица — это ВАЛИДАЦИЯ,
не тест; тестовые числа — в §2.2/§2.3 ниже, они первичны по правилу проекта.

| конфиг | net_AUC (valid) | null_AUC_k15 (valid) | margin | net_AUC_pair | null_AUC_pair_k15 | margin_pair |
|---|---|---|---|---|---|---|
| `descriptors_no_extent_coarse_add_lipprop` (старый утёкший baseline, для контекста) | — | — | — | — | — | — |
| `descriptors_head_family_neutral_lipprop` (база) | 0.529 | 0.596 | **−0.067** | 0.512 | 0.613 | **−0.101** |
| `_heads1` | 0.536 | 0.596 | **−0.060** | 0.515 | 0.614 | **−0.099** |
| `_rankprot` | 0.516 | 0.596 | **−0.080** | 0.496 | 0.613 | **−0.117** |
| geometric_edge (mlp, для сравнения, тот же 7-family набор) | 0.602 | 0.545 | **+0.057** | 0.569 | 0.595 | −0.026 |

Все три descriptors-варианта остаются ниже нуль-модели; `heads1` минимально лучше
базы (+0.007), `rankprot` — хуже базы (−0.013). Разброс между тремя (≤0.02) меньше
`std across families` любого из них (0.10-0.15) — различие не читается как факт, а
не как случайность.

### 2.2 Тест-сплит, честная метрика (`AUC_within_protein_pairs`, семь общих семей)

Пулированное значение из `summarize_label.py` (тест, все строки лейбла):

| конфиг | test BA (пул) | test AUC_within_protein_pairs (пул) | n строк |
|---|---|---|---|
| `descriptors_head_family_neutral_lipprop` | 0.5545 | 0.5857 | 35 (7 семей) |
| `_heads1` | 0.5492 | 0.5928 | 45 (9 семей) |
| `_rankprot` | 0.5371 | 0.5330 | 45 (9 семей) |

`heads1` даёт тот же вывод, что и на валид-сплите: неотличим от базы. `rankprot`
хуже на тесте так же, как и на валиде — направление совпадает между двумя сплитами
в обе стороны, это не артефакт выбора сплита.

### 2.3 По семьям: утечка LBP_BPI_CETP уменьшена, но не закрыта

Test BA и `AUC_within_protein_pairs` по 7 общим семьям (без ML/OSBP, которых у базы
ещё нет):

| семья | старый утёкший baseline (test BA) | база (test BA / pairs AUC) | heads1 (test BA / pairs AUC) | rankprot (test BA / pairs AUC) |
|---|---|---|---|---|
| LBP_BPI_CETP | **0.826** | 0.677 / 0.849 | 0.776 / 0.871 | 0.702 / 0.703 |
| остальные 6 (среднее BA) | 0.549 | 0.534 | 0.536 | 0.527 |
| разрыв LBP_BPI_CETP − остальные (BA) | 0.277 | 0.143 | 0.241 | 0.175 |
| разрыв LBP_BPI_CETP − остальные (pairs AUC) | — | 0.307 | 0.334 | 0.194 |

Family-neutral набор сокращает разрыв BA примерно вдвое (0.277 → 0.143) относительно
старого утёкшего baseline — но не до нуля, и по `AUC_within_protein_pairs` сеть на
LBP_BPI_CETP по-прежнему обходит валид-сплитовую нуль-модель (net=0.732/0.753/0.676
против chem=0.634 на этой семье во всех трёх вариантах — см. таблицы `по семьям` в
самих `.md`-отчётах, §"чем посчитано"). То есть остаточный, необъяснённый химией сигнал
на этой семье (n=2 белка) держится при любом из трёх испытанных лоссов/ширин
attention-головы. `heads1` НЕ уменьшает этот разрыв — по обеим метрикам он у него
БОЛЬШЕ, чем у базы (0.241 против 0.143 по BA, 0.334 против 0.307 по pairs AUC),
хотя пулированный эффект `heads1` заявлен как "нулевой" (§2.1/2.2) — то есть
увеличение ширины per-head (`--HEADS=1` при `hiddim=8` даёт 8 измерений на голову
вместо 1 в self-attention над дескрипторными токенами) не помогает генерализации, но
даёт чуть больше свободы подогнаться именно под эту маленькую семью. n=2 белка,
экстраполировать нельзя, но направление воспроизводится на двух независимых метриках
(BA и pairs AUC).

**`rankprot` вызывает коллапс sensitivity на 4 из 9 семей, а не просто "хуже".**
Test sensitivity/specificity: `scp2` 0.047/0.929, `ML` 0.120/0.880, `GLTP` 0.296/0.904,
`START` 0.262/0.706 — модель почти всегда предсказывает отрицательный класс на этих
четырёх семьях. Это качественно ДРУГОЕ поведение, чем эффект `rankprot` на
geometric_edge под lipid_coldsplit (там `rankprot` убирал белковую маргиналь и
поднимал внутрибелковый AUC при падении пулированной BA, без такого тотального
коллапса sensitivity, см. `lipid_coldsplit_architecture_direction.md` §7n) —
перенос вывода "rankprot полезен" с одной архитектуры/оси на другую не подтверждён,
здесь он скорее вреден.

## 3. geometric_edge mlp vs attention, double_coldsplit (bare `--bilinear_fusion` baseline)

`geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion` (без
суффикса `_bilinear_norm`, 45 строк/9 семей — впервые прогнан на ML/OSBP) — прямой
аналог уже существующего `geometric_edge_mlp_protgeom_family_neutral_normalized_
bilinear_fusion` (35 строк/7 семей, старый, без ML/OSBP). Единственная разница в
arg-файлах — `--protein_edge_attention` вместо `--protein_edge_mlp`.

### 3.1 Тест BA по 7 общим семьям — практически ничья

| семья | mlp (test BA) | attention (test BA) |
|---|---|---|
| CRAL-TRIO | 0.5645 | 0.5551 |
| GLTP | 0.4800 | 0.5040 |
| IP_trans | 0.5742 | 0.5531 |
| LBP_BPI_CETP | 0.6358 | 0.6272 |
| START | 0.4912 | 0.5279 |
| lipocalin | 0.6375 | 0.6597 |
| scp2 | 0.5647 | 0.5382 |
| **среднее по 7 семьям** | **0.5640** | **0.5665** |

По BA разницы нет. Но под равным BA прячутся разные профили sensitivity/specificity
(правило проекта — не судить по одной BA):

| семья | mlp sens/spec | attention sens/spec |
|---|---|---|
| CRAL-TRIO | 0.722/0.407 | 0.546/0.564 |
| GLTP | 0.632/0.328 | 0.544/0.464 |
| IP_trans | 0.574/0.575 (сбалансировано) | **0.391/0.715** (сильный крен в spec) |
| LBP_BPI_CETP | 0.565/0.706 | 0.557/0.698 |
| START | 0.526/0.456 | **0.674/0.382** (крен в sens) |
| lipocalin | 0.728/0.547 | 0.756/0.564 |
| scp2 | 0.753/0.377 (крен в sens) | 0.482/0.594 (лёгкий крен в spec) |

mlp почти везде смещён в сторону sensitivity (предсказывает "да" чаще), attention —
непостоянно, где-то в spec (IP_trans, scp2), где-то в sens (START) — то есть за
одинаковой средней BA стоят два разных, не просто более мягких/жёстких, а
качественно разных по знаку смещения решающих правила.

### 3.2 Валид-сплитовая нуль-модельная поправка — mlp впереди, но это старый результат

| | net_AUC (valid, 7 семей) | null_AUC_k15 | margin | net_AUC_prot (within-protein) |
|---|---|---|---|---|
| mlp (существующий) | 0.602 | 0.545 | **+0.057** | 0.591 |
| attention (новый) | 0.563 | 0.545 | **+0.018** | 0.557 |

Направление ("mlp > attention") совпадает с уже зафиксированным в
`lipid_coldsplit_architecture_direction.md` §7i выводом на СОВСЕМ другой ветке
(`attention_lcs_esm3` против `lcs_esm3`, там разрыв −0.062/1.5σ по другой метрике,
lipid_coldsplit) — то есть этот прогон не открывает новый факт, а воспроизводит уже
известный на ещё одной паре конфигов. Within-protein разрыв (0.591 vs 0.557) в
основном идёт с двух семей: `lipocalin` (mlp 0.730 vs attention 0.571, самый большой
единичный разрыв +0.159) и `LBP_BPI_CETP` (0.737 vs 0.667, +0.070) — обе с малым
числом белковых блоков (5 и 2 соответственно), так что 1-2 сида/белка могут решать
исход.

### 3.3 Обе линии унаследовали известную нестабильность "bare"-конфигурации

И mlp (существующий, 35 строк), и attention (новый, 45 строк) стоят на "bare"
варианте `--bilinear_fusion` — БЕЗ `--bilinear_pooled_norm`, который есть у
параллельной, уже стабильной линии `..._bilinear_fusion_bilinear_norm*`. Тестовый
лосс взрывается на части сидов у ОБЕИХ: mlp — до 92.96 (LBP_BPI_CETP, сид 4), 40.33
(IP_trans, сид 4); attention — до 278.91 (LBP_BPI_CETP, сид 0), 28.11 (ML, сид 1).
Это не специфично для attention и не новая проблема — уже стабильная
`_bilinear_norm`-линия (существующая, 35 строк/7 семей у каждого варианта, max test
loss 1.25–1.55) существует именно потому, что кто-то уже чинил эту нестабильность
добавлением нормировки; она просто не была применена в этих двух "bare"-конфигах.
На стабильной `_bilinear_norm`-линии разница mlp/attention по пулированной test BA
меньше (0.5525 vs 0.5428, Δ=0.01) — тот же знак, меньше по величине, без взрывов
лосса — но её собственный раздел нуль-модели помечен как сломанный/устаревший
(`reference_baselines_metrics_proposal.md`, раздел "Chemistry-null comparison, full
bilinear_fusion line") и требует повторного запуска `full_label_report.py`, который
не выполнялся в рамках этого разбора (форвард-пасс по чекпойнтам, инициативный запуск
запрещён).

## 4. Единственный lipid_coldsplit-прогон: `geometric_edge_mlp_protgeom_full_lcs`

Arg-файл (`scripts/arg_files/geometric_edge_mlp_protgeom_full_lcs.md`) относительно
текущего лучшего lcs-baseline `..._bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot`
меняет ОДНОВРЕМЕННО три вещи:

1. `--no_protein_embeddings` — снимает ESM3 (баз. линия его держит, суффикс `_esm3`);
2. `--protein_descriptors=` — 15 "полных" карманных признаков вместо 7 family-neutral
   (проверка предложения §7.1 из `lipid_coldsplit_architecture_direction.md`);
3. `--balanced_proteins` вместо `--balanced_lipid_classes` — использует СТАРЫЙ
   протеин-балансирующий сэмплер, который §7.4/§8.6 того же файла уже определили как
   уступающий на внутрибелковой метрике (−0.07 на двух читаемых наборах).

При этом сохраняется `--adversarial_grl --no_adv_lipid` (advprot-механизм). Ни один
из прочитанных 7 файлов-предложений не описывает именно эту комбинацию как отдельную,
намеренную гипотезу — единственное упоминание этого arg-файла в источниках
(`lipid_coldsplit_architecture_direction.md`, конец файла) констатирует, что он
"собран БЕЗ какой-либо балансировки по классу липида — ни старой, ни новой [весовой,
не реализованной]", то есть похоже на конфиг, собранный до/независимо от находок
§7.4/§7j/§7n о важности `--balanced_lipid_classes`, а не после них.

### 4.1 Результат: не отличим от текущего лучшего baseline при огромном разбросе по сидам

`AUC_within_protein_pairs`, тест, по вынесенным наборам липидов (первичная метрика):

| набор | `geometric_edge_mlp_protgeom_full_lcs` (этот прогон) | `..._balanced_lipid_classes_advprot` (текущий лучший, для сравнения) | белковых блоков (этот прогон) |
|---|---|---|---|
| anionic | 0.522 | 0.485 ± 0.020 | 15-17 |
| choline | 0.574 | **0.604 ± 0.019** | 14 |
| phosphorus_free | 0.621 | 0.618 ± 0.052 | 8-13 |
| sphingolipids | 0.468 | 0.491 ± 0.074 | 2-3 |

Все четыре разницы (±0.02...−0.03) лежат внутри типичного разброса по 5 сидам,
видного в самой таблице ("текущий лучший" колонка, ±SEM 0.02-0.07). Три
одновременных изменения (§4, пункты 1-3) не сдвинули результат ни в одну сторону
настолько, чтобы отличить эффект одного изменения от другого — эта партия НЕ
проверяет предложение §7.1 (полный набор дескрипторов) отдельно от двух остальных
изменений. Прямое сравнение с химической нуль-моделью для ЭТОГО прогона недоступно:
`full_label_report.py --label geometric_edge_mlp_protgeom_full_lcs` завершается
ошибкой `sphingolipids/seed0: split reproduced here does not match the scored rows`
(текст ошибки взят из самого `graphics/.../....md`, скрипт не перезапускался).

### 4.2 Нестабильность по сидам — сильнее, чем у известного advprot-бейзлайна

6 из 20 запусков (набор×сид) показывают патологические профили и/или пометку
`converged=0` не проставлена как надёжная (колонка `converged=1` у пайплайна
означает явно отмеченную несходимость):

| набор | сид | sens | spec | test loss | `converged` |
|---|---|---|---|---|---|
| anionic | 0 | 0.925 | 0.079 | 33.4 | 1 |
| anionic | 1 | 0.763 | 0.305 | 127.6 | 0 |
| anionic | 2 | 0.000 | 1.000 | 15.6 | 0 |
| anionic | 3 | 0.957 | 0.033 | 243.6 | **1** |
| choline | 1 | 0.928 | 0.132 | — | 0 |
| choline | 3 | 0.144 | 0.964 | 21.7 | 0 |

На `anionic` из 5 сидов три (0,2,3) практически полностью коллапсируют в один класс
(предсказывают почти всегда "да" или почти всегда "нет"), два сида (0 и 3) пайплайн
сам отмечает как несошедшиеся. Это заметно хуже той степени нестабильности, что уже
задокументирована для advprot-механизма на устоявшемся lcs-baseline (`geometric_edge_
and_solo_next_architecture.md` §2.4: train BA падает до 0.582, но без коллапса
sens/spec к 0/1 и без пометок `converged=1`). Разброс std по сидам в самих таблицах
`summarize_label.py` (например `anionic` test sensitivity std=0.394, specificity
std=0.387) уже отражает эту нестабильность, но её масштаб виден только по сырым
строкам, не по агрегату.

**Вывод по этому прогону.** Он не подтверждает и не опровергает предложение §7.1
(полный набор дескрипторов) изолированно — конфаунд с ESM3 и с типом
балансировки, плюс нестабильность обучения на нескольких сидах, делают
единственное число (пул по 5 сидам) ненадёжным индикатором того, какое из трёх
одновременных изменений отвечает за результат.

## 5. Новый baseline: не появился ни для одной архитектуры

**Descriptors.** Ни один из 5 фактически обученных вариантов (база, heads1, rankprot
— double_coldsplit; pair/pair_clean не обучились вовсе) не бьёт химическую
нуль-модель ни на валид-, ни на тест-сплите. `descriptors_baseline_leak_confirmed.md`
предсказывал именно это для базы и rankprot — подтвердилось; для heads1 (не
разобранного в том файле) вывод тот же: пулом эффекта нет, а по семье с
известной утечкой (LBP_BPI_CETP) эффект даже отрицательный (утечка чуть выросла
относительно базы, не сократилась). Самый интересный нерешённый вопрос —
работают ли "чистые" pair-дескрипторы (`pair_clean`) или их полная комбинация
(`pair`) — остаётся открытым из-за бага `--zscore` (§1), не из-за отрицательного
результата.

**geometric_edge.** mlp остаётся впереди attention там, где раньше уже было
измерено (валид-сплитовая нуль-модельная поправка, within-protein AUC), но на
честной тест-BA по семьям разницы практически нет (0.564 vs 0.566), и обе линии
несут не related to attention/mlp нестабильность "bare"-конфигурации. Для
lipid_coldsplit единственный прогон этой партии не даёт чистого сравнения ни с чем
из-за трёхфакторного конфаунда и нестабильности обучения — текущий лучший
lcs-baseline (`..._bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot`) остаётся
таковым без изменений по итогам этой партии.

## Чем посчитано

- Классификация double_coldsplit/lipid_coldsplit для всех 7 лейблов и подсчёт строк:
  `python3`/`pandas` над `metrics_summary.csv`, группировка по `label`, колонки
  `lipid_coldsplit`, `double_coldsplit`, `exclusion_set`, `seed` (read-only).
- Тест-метрики по семьям/наборам (BA, sensitivity, specificity, `AUC_within_protein`,
  `AUC_within_protein_pairs`) — те же колонки `metrics_summary.csv`, а также готовые
  агрегаты в `graphics/descriptors_head_family_neutral_lipprop/*.md`,
  `graphics/descriptors_head_family_neutral_lipprop_heads1/*.md`,
  `graphics/descriptors_head_family_neutral_lipprop_rankprot/*.md`,
  `graphics/geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_
  fusion/*.md`, `graphics/geometric_edge_mlp_protgeom_full_lcs/*.md`
  (`analysis/summarize_label.py`, уже сгенерировано, не пересчитывалось).
- Валид-сплитовая нуль-модельная таблица ("AUC vs chemistry null model") — та же
  секция тех же `.md`-файлов (`analysis/full_label_report.py`, дефолт `--split
  valid`, подтверждено грепом заголовка `########## split = valid ##########` и
  чтением `analysis/full_label_report.py:177` `add_argument("--split",
  default="valid", ...)`); для `geometric_edge_mlp_protgeom_family_neutral_
  normalized_bilinear_fusion` (существующий mlp bare baseline) числа взяты из уже
  готового `graphics/.../....md`, не пересчитывались.
- Существующий lcs-baseline (`..._balanced_lipid_classes_advprot`) и вся история
  предложений §7 — процитировано из `files/lipid_coldsplit_architecture_direction.md`
  (§7.1, §7a, §7i, §7j, §7k, §7n, финальный раздел "Предложенная альтернатива
  --balanced_lipid_classes"), не пересчитывалось заново.
- Причина падения `descriptors_pair_clean`/`descriptors_head_family_neutral_lipprop_
  pair`: чтение `script_logs/descriptors_pair_clean_seeds01234/{CRAL-TRIO,START,
  LBP_BPI_CETP,OSBP,ML}/*.log` и `script_logs/descriptors_head_family_neutral_
  lipprop_pair_seeds01234/START/*.log` (traceback), `grep -rn "\-\-zscore"
  analysis/ dataloader/ training/ scripts/` (подтверждает: флаг существует только в
  `analysis/*.py`), `training/read_configuration.py:3226` (место, где кидается
  `ValueError: Unknown parameter`), сверка arg-файлов `scripts/arg_files/
  descriptors_pair_clean.md` / `descriptors_head_family_neutral_lipprop_pair.md`.
- Диагностика "bare" vs "`_bilinear_norm`" нестабильности: `diff` между
  `scripts/arg_files/geometric_edge_{mlp,attention}_protgeom_family_neutral_
  normalized_bilinear_fusion.md` и их `_bilinear_norm`-версиями; `metrics_summary.csv`
  колонка `loss` (`max()`/сортировка) для всех четырёх лейблов (mlp bare, attention
  bare, mlp `_bilinear_norm`, attention `_bilinear_norm`).
- Сырые per-seed профили нестабильности `geometric_edge_mlp_protgeom_full_lcs` и
  `geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion`:
  прямой листинг строк `metrics_summary.csv` по этим двум лейблам (`sensitivity`,
  `specificity`, `loss`, `converged`), без агрегации.
- Контекст по `--HEADS`/`NamedDescriptorHead`: `grep -n "HEADS" architecture/*.py
  training/read_configuration.py`, `architecture/named_descriptor_head.py:65`.
- Ничего не обучалось, ни один чекпойнт не загружался, кластер не трогался.
