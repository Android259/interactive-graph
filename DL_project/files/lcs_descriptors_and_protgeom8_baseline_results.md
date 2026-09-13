# 8 новых `--lipid_coldsplit` конфигов: `descriptors_head` впервые под lcs, `protgeom8`/`protfull` поверх текущего лучшего baseline

> **Пометка 2026-09-12**: "текущий лучший baseline"/"текущего лучшего lcs-baseline с
> advprot" (заголовок, §0 п.2, §3.1) устарело как безусловная формулировка —
> `advprot` обгоняет `liphid32` на честной метрике (`AUC_within_protein`), но заметно
> уступает ему по стабильности обучения (`collapse_fraction`), и есть непроверенный
> здесь третий кандидат (`esm3_advprot`, без `--balanced_lipid_classes`), который
> обгоняет "официальный" `advprot` на обоих надёжных наборах. Подробности:
> [lcs_geometric_edge_best_candidate_recheck.md](lcs_geometric_edge_best_candidate_recheck.md).
> Числа `protgeom8`/`protfull` в этом файле не переоцениваются — они остаются верными
> относительно того baseline, с которым сравнивались.

## Правило сопровождения

Снимок на 2026-09-12. Все числа — из `metrics_summary.csv` (8 лейблов, 20 строк
каждый = 4 набора липидов × 5 сидов, свежий батч с bigfoot, ни одного краша).
Агрегаты по группам/сидам посчитаны `analysis/lcs_new_configs_summary.py`
(новый скрипт, читает только `metrics_summary.csv`, ничего не обучает и не
грузит чекпойнты — см. «чем посчитано»). Для трёх лейблов сравнения
(`..._lcs_esm3_balanced_lipid_classes_advprot`, `..._lcs_balanced_lipid_classes_advprot`,
`geometric_edge_mlp_protgeom_full_lcs`) готовые `graphics/<label>/<label>.md` уже
существовали — взяты оттуда и не пересчитывались.

**Первичная метрика — `AUC_within_protein_pairs` на test, по каждому вынесенному
набору отдельно.** Пулированные BA/AUC на `--lipid_coldsplit` выигрываются
белковой маргиналью (все белки остаются в train) — правило и измерение в
[lipid_coldsplit_architecture_direction.md](lipid_coldsplit_architecture_direction.md),
врезка «ПРАВИЛО» и §7j. SEM = std/√5 по группе; combined SEM = квадратичная
сумма двух SEM. Арифметика — в самом `analysis/lcs_new_configs_summary.py`
(`mean`/`sem`), не вручную.

## 0. Итог

| Вопрос | Ответ | Раздел |
|---|---|---|
| Что вообще прогнано? | 4 варианта `descriptors_head` под lcs (первые в проекте вообще) + 4 варианта `geometric_edge_mlp` (`protgeom8`/`protfull` × `esm3`/без esm3) поверх текущего лучшего lcs-baseline с `advprot`. Все 8×20=160 строк, 0 крашей, 120/120 эпох у каждого прогона. | 1 |
| `descriptors_head` под lcs — работает ли вообще? | Нет единого ответа «да»/«нет»: у каждого из 4 вариантов значимо (>2σ от 0.5) отличается от шанса **ровно один** набор из четырёх, и знак не всегда положительный. `base` и `tailtokens` **значимо НИЖЕ** шанса на `sphingolipids` (−2.85σ и −2.43σ) — ранжирование хуже случайного, не просто неинформативное. `protgeom8` даёт единственный уверенно положительный результат линии — `anionic` 0.577±0.019 (+4.05σ). | 2 |
| Какой из 4 вариантов `descriptors_head` лучше? | Нет единого лидера по всем наборам. `protgeom8` — лучший на `anionic`; `rankprot`/`tailtokens` — единственные, кто вообще подбирается к внутрибелковому сигналу на `choline` (0.61–0.64 по средней-по-белкам версии против null-модельного ориентира 0.331, см. §2.3); `base` и `tailtokens` проваливаются на `sphingolipids`. | 2 |
| `protgeom8`/`protfull` поверх лучшего baseline — бьют ли baseline? | **Нет, ни один из 4.** Все дельты к своему baseline (esm3 или no-esm3) в пределах ±1.8 combined SEM на всех 4 наборах — ни одна не проходит 2σ. | 3 |
| `protgeom8` vs `protfull` — какой лучше? | **Не различимы.** 8 прямых сравнений (4 набора × 2 esm3-плеча) — все в пределах ±1.8σ, ни одно не значимо. Единственный намёк — `anionic` в no-esm3-плече, `protfull` выше `protgeom8` на 1.80σ (не 2σ). | 4 |
| Подтверждает это старое опровержение `protgeom8` из §7.1? | **Да, и на существенно более сильном baseline.** §7.1 (`lipid_coldsplit_architecture_direction.md`) опроверг `protgeom8` на голом `lcs_esm3` (без bilinear-стека/advprot/balanced_lipid_classes) — там тоже плоско. Теперь то же самое измерено поверх `advprot + balanced_lipid_classes + bilinear_norm` — снова плоско, на всех 4 наборах и в обоих esm3-плечах. Два независимых baseline'а, один и тот же результат. | 3 |
| Патология сидов, как у `geometric_edge_mlp_protgeom_full_lcs` (6/20)? | **Нет ни у одного из 8.** Максимальный test loss по всем 160 новым строкам — 1.12 (у `descriptors_head_lcs_rankprot`, `sphingolipids`); у `protgeom_full_lcs` — до 243.6 (в 217 раз больше). `nan_epoch_count`=0 везде. Есть отдельная, более мягкая нестабильность — см. §5. | 5 |
| Что-то новое про пулированные sens/spec как ловушку? | Да: `geometric_edge_mlp_..._esm3_..._advprot_protfull` даёт пулом sens=0.516/spec=0.510 (гэп 0.006 — почти идеальный баланс), а по группам — `anionic` 0.86/0.17 и `phosphorus_free` 0.13/0.82: противоположные перекосы по группам взаимно гасятся в пуле. Ровно то, против чего предостерегает правило проекта «не судить по пулу». | 3 |

## 1. Что прогнано и чем отличается от плана

### 1.1 `descriptors_head` (план A-G, `reference_baselines_metrics_proposal.md` §3)

| лейбл | что меняет относительно базы (A+B уже в базе) | параметров |
|---|---|---|
| `descriptors_head_family_neutral_lipprop_lcs` | база: `--lipid_coldsplit` (A) + `--balanced_lipid_classes` (B), `descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim` | 1066 |
| `..._rankprot` | + `--loss_type=pairwise_rank --rank_within_protein --batch=32` (план D) | 1066 |
| `..._tailtokens` | `hbond,heavy` → `tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_length_asymmetry` (план E) | 1082 |
| `..._protgeom8` | протеиновые токены в `descriptor_names`: `pocket_volume_per_sasa,...,hydropathy_rim` (family-neutral 7 минус то, что попало в лист) → `pocket_extent,...,depth_q10,...,hydropathy_core,...` (protgeom8, план F) | 1074 |

Все четыре подтверждены полем `descriptor_names`/`protein_descriptors` в
`metrics_summary.csv` — у `descriptors_head` протеиновые дескрипторы идут
ВНУТРИ `descriptor_names` (`protein_descriptors` пуст), в отличие от
`geometric_edge_mlp`, где это отдельный флаг. Все четыре имеют
`adversarial_grl=0` — план C (`descriptors_head` физически не строит
`protein1`/`lipid1`, GRL кидает `ValueError`) подтверждён самим фактом, что
эти прогоны вообще стартовали с `adversarial_grl` не включённым.

Сравнивать эти 4 не с чем: это первые прогоны `descriptors_head` под
`--lipid_coldsplit` в проекте вообще (`reference_baselines_metrics_proposal.md`
§3, вводная часть).

### 1.2 `geometric_edge_mlp` `protgeom8`/`protfull` (план F, тот же файл)

Оба поверх `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_{esm3_,}balanced_lipid_classes_advprot` (27 544 / 27 384 параметра), меняя **только** `--protein_descriptors=`:

| лейбл | `--protein_descriptors=` | параметров |
|---|---|---|
| baseline esm3 | 7 family-neutral (`pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim`) | 27 544 |
| baseline no-esm3 | то же | 27 384 |
| `..._esm3_..._protgeom8` | 8 имён: `pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim` | 27 560 |
| `..._protgeom8` (no-esm3) | то же | 27 400 |
| `..._esm3_..._protfull` | все 15 `PROTEIN_DESCRIPTOR_NAMES` | 27 672 |
| `..._protfull` (no-esm3) | то же | 27 512 |

Разница в числе параметров (16–288) — ровно от разницы в длине входного
вектора дескрипторов, ничего архитектурного не поменялось. Все 4 сохраняют
`adversarial_grl=1, adv_lipid=0, adv_protein=1, balanced_lipid_classes=1` —
то есть отличаются от своего baseline буквально одной строкой флага.

## 2. `descriptors_head` под lcs: честная картина, без опоры на что-либо

`descriptors_head` — сильно урезанная архитектура: она не строит
протеиновый/липидный GATv2-энкодер, ESM3-проекцию и cross-attention вообще;
всё, что видит модель, — это self-attention (`NamedDescriptorHead`) над
списком именованных скалярных дескрипторов (липидных + протеиновых карманных)
и маленький классификатор поверх (`training/read_configuration.py:542-557`,
1066–1082 параметров — на два порядка меньше `geometric_edge_mlp`).

### 2.1 `AUC_within_protein_pairs`, test, по наборам (mean ± SEM, n=5 сидов)

| набор | `base` | `rankprot` | `tailtokens` | `protgeom8` |
|---|---|---|---|---|
| anionic | 0.5557 ± 0.0269 (**+2.07σ**) | 0.4855 ± 0.0221 (−0.66σ) | 0.5123 ± 0.0124 (+0.99σ) | **0.5766 ± 0.0189 (+4.05σ)** |
| choline | 0.4149 ± 0.0441 (−1.93σ) | 0.6146 ± 0.0634 (+1.81σ) | **0.6084 ± 0.0457 (+2.37σ)** | 0.4466 ± 0.0485 (−1.10σ) |
| phosphorus_free | 0.5331 ± 0.0959 (0.34σ) | 0.4672 ± 0.0313 (−1.05σ) | 0.4407 ± 0.0405 (−1.46σ) | 0.4646 ± 0.0494 (−0.72σ) |
| sphingolipids | **0.2551 ± 0.0860 (−2.85σ)** | 0.4482 ± 0.0731 (−0.71σ) | **0.3966 ± 0.0426 (−2.43σ)** | 0.5410 ± 0.0889 (0.46σ) |
| ALL (пул 4×5) | 0.4397 ± 0.0420 | 0.5039 ± 0.0282 | 0.4895 ± 0.0252 | 0.5072 ± 0.0289 |

σ считается против шанса (0.5), не против честной нуль-модели (для
`descriptors_head` под lcs нуль-модель `analysis/lipid_coldsplit_null_model.py`
в этом раунде не пересчитывалась — не запускалась намеренно, см. правила
задания). n=5 — слабая статистика, и `sphingolipids`/`phosphorus_free` дают
всего 1.8–2.0 читаемых белковых блока в среднем (колонка «proteins_averaged»
у пары AUC надёжнее — 7.8/14 «contributing», см. таблицу ниже), так что числа
по этим двум наборам разрежены сильнее, чем по `anionic`/`choline`.

**Ни один из 4 вариантов не выигрывает уверенно на всех наборах, и у двух
(`base`, `tailtokens`) есть значимый провал НИЖЕ шанса на `sphingolipids`** —
ранжирование там систематически (по 5 сидам, std 0.086/0.043) ставит
отрицательный липид выше положительного, а не просто «не знает». `rankprot`
и `protgeom8` на этом же наборе плоские (не отрицательные), так что провал не
общий для архитектуры, а зависит от конкретного набора дескрипторов/лосса —
причина не установлена этим разбором (не гадаю, откуда конкретно берётся
знак).

### 2.2 Контекст: пулированные BA/sens/spec/loss и стабильность

| | anionic BA | anionic sens/spec | choline BA | choline sens/spec | phosphorus_free BA | phosphorus_free sens/spec | sphingolipids BA | sphingolipids sens/spec |
|---|---|---|---|---|---|---|---|---|
| base | 0.6054±0.0224 | 0.735/0.475 | 0.5377±0.0240 | 0.568/0.508 | 0.4774±0.0363 | 0.232/0.722 | 0.4567±0.0156 | 0.406/0.507 |
| rankprot | 0.5030±0.0319 | 0.366/0.640 | 0.5538±0.0167 | 0.503/0.605 | 0.5357±0.0219 | 0.439/0.633 | 0.6395±0.0290 | 0.430/0.849 |
| tailtokens | 0.6379±0.0141 | 0.705/0.571 | 0.5410±0.0141 | 0.611/0.471 | 0.4758±0.0194 | 0.413/0.539 | 0.5088±0.0183 | 0.515/0.502 |
| protgeom8 | 0.6272±0.0129 | 0.746/0.508 | 0.5094±0.0211 | 0.501/0.518 | 0.5031±0.0144 | 0.361/0.645 | 0.5193±0.0374 | 0.673/0.366 |

Гэп |sens−spec| пулом: base 0.068, rankprot 0.247, tailtokens 0.040,
protgeom8 0.061 — **`rankprot` даёт самый большой пулированный гэп**, что
для ранжирующего лосса ожидаемо (порог 0.5 не то, что он оптимизирует, см.
`lipid_coldsplit_architecture_direction.md` §7n).

**Стабильность (per-seed, `sensitivity`/`specificity`/`loss`/`converged`,
`analysis/lcs_new_configs_summary.py --per-seed`):**

- Нет ни одного NaN-эпизода и ни одного взрыва loss ни у одного из 4×20=80
  прогонов: test loss в диапазоне 0.61–1.12 (максимум — `rankprot`,
  `sphingolipids`, seed2, 1.12), везде 120/120 эпох.
- Есть частые (но НЕ катастрофические) коллапсы sens/spec к 0/~1 на
  отдельных сидах маленьких наборов: `base` phosphorus_free seed1/4
  (sens=0.00, spec=0.98–1.00), `sphingolipids` seed1 (sens=0.00, spec=1.00);
  `protgeom8` choline seed3/4 (sens=0.99/spec=0.00 и наоборот),
  `phosphorus_free` seed4 (sens=0.00); `tailtokens` sphingolipids seed1/2
  (0/1 и 1/0 — противоположные коллапсы гасят друг друга в среднем). Ни один
  из этих коллапсов не сопровождается ростом loss — это похоже на
  нестабильность порога у крошечной (1066–1082 параметра) модели на
  крошечных тестовых блоках (61–88 строк на набор), а не на расходящееся
  обучение, как у `geometric_edge_mlp_protgeom_full_lcs` (§5).
- `collapse_epoch_count` (доля ВАЛИДАЦИОННЫХ эпох с полным коллапсом класса
  во время обучения, не тест) низкий у `base`/`tailtokens`/`protgeom8`
  (максимум 1–17 эпох из 120), заметно выше у `rankprot` (до 51–71 из 120 на
  `anionic`/`choline`) — ранжирующий лосс чаще проходит через
  полностью-однокарассовые валидационные эпохи по пути, что согласуется с
  его большим пулированным гэпом выше.

### 2.3 `choline`/`phosphorus_free` — единственные наборы, где стоит сверяться с честной нуль-моделью

`lipid_coldsplit_architecture_direction.md` §7j уже посчитал два
chemistry-blind (без модели вообще) соперника на **том же самом**
`--balanced_lipid_classes`-сплите (архитектурно-независимая величина: сплит
строится из химии и флага, не из энкодера) — `within_protein`: `choline`
0.331, `phosphorus_free`0.406, `anionic` 0.745, `sphingolipids` 0.483 (метрика
там — среднее по белкам, не парная, но того же семейства, что и «AUC
in-protein (per-protein mean)» в таблице ниже).

| набор | `within_protein`-соперник (без модели) | `base` (per-protein mean) | `rankprot` | `tailtokens` | `protgeom8` |
|---|---|---|---|---|---|
| anionic | **0.745** | 0.545 | 0.492 | 0.543 | 0.575 |
| choline | 0.331 | 0.371 | **0.639** | **0.581** | 0.431 |
| phosphorus_free | 0.406 | 0.518 (n≈1.8 белка/сид, шумно) | 0.419 | 0.334 | 0.500 |
| sphingolipids | 0.483 | 0.240 | 0.492 | 0.438 | 0.517 |

**На `anionic` ни один вариант `descriptors_head` не приближается к
chemistry-blind сопернику (0.745)** — то же самое, что уже нашли для
`geometric_edge_mlp` на этом наборе (§7j: сеть 0.706 против 0.745). **На
`choline` `rankprot` и `tailtokens` заметно ВЫШЕ соперника** (0.639 и 0.581
против 0.331) — это тот же качественный эффект, что `lipid_coldsplit_
architecture_direction.md` §7n/§7p уже задокументировал для `geometric_edge_
mlp` (`choline` — набор, где различать надо по ацильной цепи, и она
переносится через разрез), только здесь он воспроизводится на архитектуре,
у которой в принципе нет обучаемого протеинового/липидного энкодера —
довод, что эффект держится на уровне лосса/сэмплирования, а не конкретной
ветки представления.

## 3. `geometric_edge_mlp`: `protgeom8`/`protfull` поверх лучшего baseline

### 3.1 `AUC_within_protein_pairs`, test, дельты к своему baseline (esm3 или no-esm3) в combined SEM

| набор | baseline esm3 | `protgeom8` esm3 | Δ | `protfull` esm3 | Δ |
|---|---|---|---|---|---|
| anionic | 0.4849±0.0202 | 0.5055±0.0248 | +0.021 (0.64σ) | 0.4824±0.0230 | −0.003 (0.08σ) |
| choline | 0.6041±0.0190 | 0.6027±0.0289 | −0.001 (0.04σ) | 0.6045±0.0240 | +0.000 (0.01σ) |
| phosphorus_free | 0.6182±0.0525 | 0.6138±0.0669 | −0.004 (0.05σ) | 0.5883±0.0652 | −0.030 (0.36σ) |
| sphingolipids | 0.4906±0.0742 | 0.4654±0.0830 | −0.025 (0.23σ) | 0.4909±0.0818 | +0.000 (0.00σ) |

| набор | baseline no-esm3 | `protgeom8` no-esm3 | Δ | `protfull` no-esm3 | Δ |
|---|---|---|---|---|---|
| anionic | 0.5146±0.0215 | 0.4594±0.0262 | −0.055 (1.63σ) | 0.5268±0.0268 | +0.012 (0.35σ) |
| choline | 0.6008±0.0473 | 0.6028±0.0310 | +0.002 (0.04σ) | 0.5642±0.0252 | −0.037 (0.68σ) |
| phosphorus_free | 0.6887±0.0543 | 0.5721±0.0500 | −0.117 (1.58σ) | 0.6295±0.0352 | −0.059 (0.92σ) |
| sphingolipids | 0.4261±0.0561 | 0.3923±0.0414 | −0.034 (0.48σ) | 0.4140±0.0645 | −0.012 (0.14σ) |

**Ни одна из 8 ячеек не проходит 2σ.** Наибольшие (но всё ещё не значимые)
дельты — обе отрицательные, обе у `protgeom8` в no-esm3-плече: `anionic`
−1.63σ и `phosphorus_free` −1.58σ. Это ровно те два набора, для которых план
F (`reference_baselines_metrics_proposal.md`) обосновывал `protgeom8` —
измеренная связь `depth_q10`/`hydropathy_core` с длиной цепи и числом
головных классов. Наблюдаемое направление (в минус, хоть и не значимо) не
подтверждает этот механизм на данном (уже гораздо более сильном, чем в
§7.1) baseline.

**Это подтверждает §7.1 на новом baseline.** Опровержение `protgeom8` в
`lipid_coldsplit_architecture_direction.md` §7.1/§7i было получено на голом
`lcs_esm3` (0.5525 против 0.5530 baseline, без bilinear-стека/`advprot`/
`balanced_lipid_classes`). Здесь то же сравнение — на несравнимо более
сильном baseline (`advprot` + `balanced_lipid_classes` + `bilinear_norm`) — и
результат тот же: плоско на всех 4 наборах, в обоих esm3-плечах. Два разных
baseline'а, одна и та же картина.

### 3.2 Sens/spec: известный перекос advprot, местами усиленный

Пулированные (по всем 4 наборам) sens/spec:

| | sens | spec | гэп |
|---|---|---|---|
| baseline esm3 | 0.4154 | 0.6123 | 0.197 |
| baseline no-esm3 | 0.4590 | 0.5421 | 0.083 |
| `protgeom8` esm3 | 0.5834 | 0.4395 | 0.144 |
| `protgeom8` no-esm3 | 0.5648 | 0.4309 | 0.134 |
| `protfull` esm3 | 0.5159 | 0.5101 | **0.006** |
| `protfull` no-esm3 | 0.5267 | 0.4649 | 0.062 |

`protfull` esm3 выглядит пулом почти идеально сбалансированным (гэп 0.006) —
**но это артефакт усреднения по группам с противоположным перекосом**, не
реальный баланс:

| набор | `protfull` esm3 sens/spec |
|---|---|
| anionic | 0.862 / 0.165 (крен в sens) |
| choline | 0.721 / 0.416 (крен в sens) |
| phosphorus_free | **0.129 / 0.820** (крен в spec — противоположный знак) |
| sphingolipids | 0.352 / 0.639 (крен в spec) |

Ровно то, о чём предупреждает правило проекта «не судить по одной
сбалансированной BA/sens/spec»: пулированный почти-ноль-гэп получается из
двух пар групп, каждая из которых сильно однобока в свою сторону, и они
взаимно гасятся при усреднении по 20 строкам разного размера.

На `anionic` перекос в сторону sensitivity **сильнее**, чем у обоих
baseline'ов, во всех 4 новых вариантах: baseline esm3 0.763/0.293, baseline
no-esm3 0.591/0.418, а `protgeom8`/`protfull` × esm3/no-esm3 дают
0.85–0.99 sens против 0.02–0.19 spec — по сути полный коллапс в сторону
«да» на большинстве сидов именно на этом наборе (см. per-seed данные в §5).
`AUC_within_protein_pairs` при этом на `anionic` не проседает (§3.1) —
то есть непрерывный скор всё ещё что-то ранжирует, а вот порог 0.5 уезжает
к «почти всегда да» сильнее, чем у baseline.

## 4. `protgeom8` vs `protfull` напрямую

8 сравнений (4 набора × 2 esm3-плеча), из таблиц §3.1:

| набор | esm3: `protgeom8`−`protfull` | no-esm3: `protgeom8`−`protfull` |
|---|---|---|
| anionic | +0.023 (0.68σ) | **−0.067 (1.80σ)** |
| choline | −0.002 (0.05σ) | +0.039 (0.97σ) |
| phosphorus_free | +0.026 (0.27σ) | −0.057 (0.94σ) |
| sphingolipids | −0.026 (0.22σ) | −0.022 (0.28σ)|

**Ни одна ячейка не значима.** Единственная, что приближается к 2σ, —
`anionic` в no-esm3-плече, где `protfull` (15 признаков, менее обоснованная
идея) опережает `protgeom8` (8 признаков, обоснованный план F) на 1.80σ —
не 2σ, но если выбирать между двумя, эмпирика (в той мере, в какой её можно
доверять при 1.8σ) не на стороне более обоснованного набора. На всех
остальных 7 ячейках разницы нет вовсе.

## 5. Нестабильность по сидам: сравнение всех 8 с известной патологией `protgeom_full_lcs`

Известная точка отсчёта (`geometric_edge_descriptors_baseline_selection_results.md`
§4.2, старый конфаунд-прогон, НЕ входит в 8 новых): 6 из 20 прогонов дают
патологический коллапс (sens/spec к 0/1 **и** test loss до 244× нормы **и**
пометка `converged=1` — «пайплайн отметил незавершённую сходимость» уже во
время обучения, не только в тесте).

**Ни один из 8 новых конфигов не воспроизводит эту патологию.** По всем
160 новым строкам:

| | test loss (max) | nan_epoch_count (max) | epochs_completed |
|---|---|---|---|
| 8 новых лейблов, пулом | 1.12 | 0 | 120/120 везде |
| `geometric_edge_mlp_protgeom_full_lcs` (для сравнения) | 243.58 | 0 | 120/120 |

Есть более мягкая, отдельная форма нестабильности, которая присутствует у
ОБОИХ baseline'ов ещё до какого-либо изменения дескрипторов (то есть это
свойство механизма `advprot`, не новых конфигов):

- `collapse_epoch_count` (валидационные эпохи, где весь батч предсказан
  одним классом, во время обучения) доходит до 88–101 из 120 на
  `choline`/`phosphorus_free` **уже у обоих baseline'ов** (esm3: 49.6/69 и
  65.0/89 mean/max; no-esm3: 53.4/101 и 40.4/69) — и остаётся в том же
  порядке величины у `protgeom8`/`protfull` (51.4/82 … 58.4/88). То есть
  замена дескрипторов не создаёт эту нестабильность, а наследует уже
  измеренную (документирована для advprot ранее в `geometric_edge_and_
  solo_next_architecture.md` §2.4 по словам самого§0-ответа выше).
- На `anionic` все 4 новых варианта показывают сильный per-seed крен sens/spec
  (см. §3.2) — не коллапс в статистическом смысле (`AUC_within_protein_pairs`
  не падает), а сдвиг решающего порога, заметно сильнее, чем у baseline'ов.
- `descriptors_head`'вские 4 варианта показывают отдельные почти-полные
  коллапсы sens/spec на индивидуальных сидах маленьких наборов (§2.2) без
  сопутствующего роста loss — не тот же механизм, что у
  `protgeom_full_lcs` (там loss рос вместе с коллапсом).

**Итог по стабильности:** ни у одного из 8 новых конфигов нет признаков
расходящегося обучения (loss/NaN). Есть унаследованная (не новая) высокая
доля коллапс-эпох на `choline`/`phosphorus_free` под `advprot`, и есть
per-seed чувствительность порога — оба эффекта присутствуют у baseline'ов
тоже, не введены новыми дескрипторами.

## Чем посчитано

- `metrics_summary.csv` — 8 новых лейблов (по 20 строк каждый) +
  `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
  bilinear_norm_lcs_{esm3_,}balanced_lipid_classes_advprot` +
  `geometric_edge_mlp_protgeom_full_lcs` (все существующие, по 20 строк).
  Ни один чекпойнт не читался, ничего не обучалось.
- [analysis/lcs_new_configs_summary.py](../analysis/lcs_new_configs_summary.py) —
  новый скрипт, только чтение `metrics_summary.csv` (переиспользует
  `latest_rows_for_label`/`numeric`/`read_table_rows` из `analysis/
  compare_labels.py`). Считает per-group mean/SEM для
  `AUC_within_protein_pairs` (+ per-protein-mean версия и обе колонки числа
  участвующих белков), пулированные BA/sens/spec/AUC/loss, и блок
  стабильности (`converged`, `collapse_epoch_count`, `nan_epoch_count`,
  `run_status`, test loss). Вызовы:
  ```
  python3 analysis/lcs_new_configs_summary.py <8 новых лейблов>
  python3 analysis/lcs_new_configs_summary.py --per-seed <8 новых лейблов>
  python3 analysis/lcs_new_configs_summary.py <2 baseline + protgeom_full_lcs>
  ```
- `graphics/geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
  fusion_bilinear_norm_lcs_{esm3_,}balanced_lipid_classes_advprot/*.md`,
  `graphics/geometric_edge_mlp_protgeom_full_lcs/*.md` — уже сгенерированы
  (`analysis/summarize_label.py`, TEST split), использованы как есть для
  трёх лейблов сравнения; не пересчитывались. У всех трёх раздел «AUC vs
  chemistry null model» пуст/падает (`split reproduced here does not match
  the scored rows`) — тот же известный баг реконструкции сплита, не
  относящийся к этому разбору.
- `files/lipid_coldsplit_architecture_direction.md` §7j — chemistry-blind
  null-модельные числа (`lipid_only`, `within_protein`) для того же
  `--balanced_lipid_classes`-сплита, процитированы, не пересчитаны (сплит
  архитектурно-независим, поэтому применим к `descriptors_head` тоже).
- `files/geometric_edge_descriptors_baseline_selection_results.md` §4.2 —
  определение патологии (6/20 у `protgeom_full_lcs`), процитировано для
  сравнения масштаба в §5.
- `files/reference_baselines_metrics_proposal.md` §3 — план A-G для
  `descriptors_head`, сверен построчно с полями `metrics_summary.csv`
  (`descriptor_names`, `loss_type`, `rank_within_protein`, `batch`,
  `adversarial_grl`) в §1.1 этого файла.
- `feature_contributions.csv` — проверено (`grep`/построчный поиск), ни для
  одного из 8 новых лейблов строк нет — не релевантно этому разбору.
- Код: `training/read_configuration.py:542-557` (что строит `descriptors_head`),
  `training/run_metrics.py:251-265` (`nan_epoch_count`/`collapse_epoch_count`/
  `converged` — точные определения).
