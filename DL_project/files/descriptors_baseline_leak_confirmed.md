# Дескрипторный baseline (architecture 2): утечка подтверждена, честной замены не существует

Снимок на 2026-09-11. Источники: `metrics_summary.csv`, `graphics/descriptors_head_family_neutral_lipprop*`,
`files/four_families_audit.md` §3.2, `files/signal_state.md` §8, `dataloader/pair_descriptors.py`,
`dataloader/protein_graph_builder.py`, `training/read_configuration.py`.

## TL;DR

`descriptors_no_extent_coarse_add_lipprop` — прежний канонический baseline для
descriptors-архитектуры (`files/four_families_audit.md` §3.2) — несёт утечку семейства
LBP_BPI_CETP напрямую (test BA 0.826 на этом семействе против 0.549 на остальных
шести, переживает поправку на chemistry-null). Попытки почистить его флагами
(`--no_pair_descriptor_extent`, `--pair_descriptor_pocket_shares_coarse`) ничего не
меняют в этом разрыве.

Собран честный кандидат — `descriptors_head_family_neutral_lipprop`
(`scripts/arg_files/descriptors_head_family_neutral_lipprop.md`), использующий те же
7 protein family-neutral дескрипторов, что и geometric_edge-архитектура, плюс 4
липидных (chain, unsaturation, hbond, heavy), через `--descriptor_names`
(DESCRIPTOR_CATALOG, всегда стандартизировано загрузчиком, в отличие от
`--pocket_descriptors`, который требует `--rnabang_frozen_node_adapter` для
нормализации — этот флаг нигде не стоит, так что `--pocket_descriptors`-путь кормит
сырые значения).

**Результат: честный вариант проигрывает chemistry-null модели напрямую.**

| label | net_AUC | null_AUC_k15 | margin |
|---|---|---|---|
| `descriptors_head_family_neutral_lipprop` | 0.529 | 0.596 | **−0.067** |
| `descriptors_head_family_neutral_lipprop_rankprot` (+ ranking loss) | 0.516 | 0.596 | **−0.080** |
| geometric_edge (architecture 1, для сравнения) | 0.602 | 0.545 | **+0.057** |

На pair-уровне то же самое: `net_AUC_pair` 0.512/0.496 против `null_AUC_pair_k15`
0.613 (margin −0.101/−0.117).

## Вывод

Прежний "хороший" BA (0.589) у descriptors-архитектуры был **полностью объяснён
утечкой семейства**, не реальным сигналом. Убрав утечку честными
(family-neutral, нормализованными) дескрипторами, архитектура не показывает вообще
никакого interaction-сигнала на double_coldsplit — она даже не бьёт тривиальный
kNN-lookup по химии липида. Попытка форсировать изучение взаимодействия через
`--rank_within_protein --loss_type=pairwise_rank` (rankprot) сделала только хуже.

**Architecture 2 (flat descriptors, `--descriptors_head`) на данный момент не имеет
рабочего baseline'а на double_coldsplit** — не "неподтверждённого", а буквально
не работающего лучше null-модели. Architecture 1 (geometric_edge) этот же бар
проходит (+0.057).

## Полный набор дескрипторов honest-кандидата и их утечка (η²)

**Липидные (утечка по классу липида, `analysis/lipid_descriptor_class_identity.py`,
`files/lipid_coldsplit_architecture_direction.md` §7f):**

| дескриптор | η² |
|---|---|
| Hydrogen-bond capacity (hbond) | 0.99 |
| Heavy atom count (heavy) | 0.92 |
| Acyl chain length (chain) | 0.43 |
| Degree of unsaturation (unsaturation) | 0.32 |

Все четыре статистически значимо (p=0.001) кодируют класс липида — это не проблема
для double_coldsplit (классы липидов там не исключаются), но было бы риском на
lipid_coldsplit.

**Протеиновые (утечка по семейству, `preprocessing/pocket_descriptor_identity_check.py`,
пересчитано напрямую 2026-09-11 — цифры из старой версии `files/pocket_shape_descriptors.md`
устарели, см. предупреждение ниже):**

| дескриптор | η² |
|---|---|
| Pocket flatness | 0.48 |
| Pocket volume per unit of solvent-accessible surface area | 0.41 |
| Share of apolar surface area | 0.40 |
| Median enclosure/buriedness of the lining residues | 0.32 |
| Share of aromatic residues | 0.30 |
| Average hydrophobicity at the pocket's rim/entrance | 0.28 |
| Pocket elongation | 0.19 |

Пол шума на 35 белках/9 семействах — 0.24. Все 7 — near/below floor, что и было
критерием отбора family-neutral набора (исключены 6 худших: pocket_sasa_share 0.85,
hydropathy_core 0.77, pocket_residue_share 0.71, pocket_extent 0.62, ev14_q50 0.59,
depth_q10 0.55).

**Null-модели для контекста:**
- Lipid-only null (kNN по 4 липидным дескрипторам, `analysis/null_model.py`): AUC 0.545
- Protein-only null (kNN по 7 protein family-neutral дескрипторам, блайнд к липиду):
  AUC 0.507 (на уровне случайности)
- Family-идентификационная точность по этому protein-набору: 51.4% (старый,
  более "утекающий" набор — 62.9%; потолок по ESM3-эмбеддингу — 94.3%)

**Предупреждение:** `files/pocket_shape_descriptors.md`'s раздел 5 даёт эти же η²
диапазонами (0.48–0.40, 0.32–0.28), но при точном пересчёте `pocket_elongation`
вышел за пределы заявленного диапазона (0.19 против заявленных 0.28-0.32) — документ,
похоже, устарел относительно текущего кода/данных; точная причина расхождения не
locate'на, но `preprocessing/pocket_descriptor_identity_check.py` считает вживую из
`coarse_graph_nodes.csv`/`pocketness.pdb`, так что его вывод свежее.

## geometric_edge (family-neutral) vs descriptors_head: чем отличается обработка дескрипторов, а не только граф

Оба используют один и тот же набор из 7 protein family-neutral имён
(`--protein_descriptors=...` у geometric_edge, `--descriptor_names=...` у
descriptors_head), но механизм принципиально разный:

1. **Broadcast на узлы графа vs единый вектор.** geometric_edge
   (`expand_named_protein_descriptors`, `architecture/protein_encoder.py`) копирует
   все 7 чисел НА КАЖДЫЙ узел (остаток) белкового графа как дополнительные
   признаки узла — они становятся частью представления каждого остатка отдельно.
   descriptors_head берёт один статический вектор на всю пару белок-липид, узлов
   и графа вообще нет.
2. **Липидная сторона.** У geometric_edge (в конфиге
   `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion`) нет
   флагов `--lipid_descriptors`/аналогов — липидная ветка остаётся на исходном
   механизме архитектуры (self-attention над токенами SMILES/chemical LM), не на
   4 плоских числах. У descriptors_head липид ТОЖЕ сведён к 4 числам
   (chain/unsaturation/hbond/heavy) — обе стороны одинаково "плоские".
3. **Что происходит с числами дальше.** У geometric_edge все 7 (плюс структура
   графа) проходят через `--protein_edge_mlp` (граф-слой над рёбрами — геометрические/
   пространственные связи между остатками) и self-attention, пулятся в один
   вектор, затем cross-attention с липидной веткой ДО слияния, затем
   `--bilinear_fusion` (настоящее билинейное произведение). У descriptors_head 11
   сырых чисел идут прямо в небольшой MLP без какой-либо структурной обработки,
   без attention, без билинейного слияния — просто конкатенация → MLP.
4. Протеиновая сторона geometric_edge всё ещё представлена ГРАФОМ остатков (просто
   без PLM-эмбеддингов, `--no_protein_embeddings`) — то есть архитектура сохраняет
   геометрию/связность белка, которой у descriptors_head нет вообще ни на одной
   стороне.

Разница объясняет, почему architecture 1 на тех же самых 7 дескрипторах даёт
положительный margin (+0.057), а architecture 2 — отрицательный (−0.067): не сами
числа отличаются, а то, что с ними делает архитектура вокруг.

## MolFormer lipid-embedding identity check, and real pair-descriptor η², 2026-09-11

### 1. MolFormer lipid embedding vs lipid class: identity check that never existed

Протеиновая сторона architecture 1 имеет identity-check
(`preprocessing/pocket_descriptor_identity_check.py`, ESM3-эмбеддинг как "чистый"
потолок identity: rho≈0.94, nearest-neighbour rate 94.3%). Липидная сторона (MolFormer
+ собственный self-attention проекта, `architecture/lipid_encoder.py`,
`--lipid_self_attention`) такого чекa не имела — `analysis/
lipid_descriptor_class_identity.py` покрывает только 13 ручных липидных дескрипторов,
не сам выученный MolFormer-эмбеддинг.

**Кэш проверен перед запуском**: `data/lipid_SMILES_embedding_deterministic.pkl` (и
его mmap-версия `dataloader/lipid_embedding_store.py`) — таблица, которую
дефолтный путь загрузчика (`--lipid_isomers` не установлен) реально читает
(`dataloader/Dataloader.py:279-295`), содержит 1226 записей, "каждый кандидат каждой
строки" (комментарий в коде). Прогон нового скрипта не нашёл ни одного отсутствующего
ключа на всех 283 липидных видах датасета — полное покрытие подтверждено, поэтому
это чистый анализ существующих данных, без forward pass через MolFormer.

Построен `preprocessing/lipid_embedding_identity_check.py` (зеркалит методологию
`pocket_descriptor_identity_check.py`, ось идентичности — липидный класс через
`analysis/feature_identity_check.species_class_map`). **Представление**: усреднение
768-мерного MolFormer per-token эмбеддинга по токенам (аналог усреднения ESM3 по
остаткам), затем усреднение по кандидатным структурам одного вида (тот же приём, что
`lipid_descriptor_class_identity.py`'s `candidate_matrix` использует для 13 ручных
дескрипторов) — итог: один 768-мерный вектор на липидный вид.

| метрика | значение | потолок/chance |
|---|---|---|
| eta²_joint (весь стандартизированный вектор vs класс) | **0.752** | арифметический пол (k-1)/(n-1) = 0.117 (34 класса / 283 вида) |
| Mantel rho (расстояние эмбеддинга vs one-hot(класс)) | **0.445**, p=0.001 | — |
| Nearest-neighbour shares class rate | **0.933**, p=0.001 | chance = 0.116 |

Явной непрерывной "чистой identity"-референции для липида (аналога ESM3) не
существует — идентичность вида к оси класса это и есть сам класс, поэтому Mantel тут
считается против one-hot(класс), а не против отдельного эмбеддинга, как на белковой
стороне. Nearest-neighbour rate (93.3%) почти совпадает с белковым ESM3-потолком
(94.3%) — MolFormer-эмбеддинг липида практически ЯВЛЯЕТСЯ отпечатком класса,
качественно так же сильно, как ESM3-эмбеддинг является отпечатком identity белка.

**Значение для проекта**: под `double_coldsplit` (где классы липидов НЕ исключаются)
это не проблема само по себе — то же самое верно и для ручных липидных дескрипторов
(hbond η²=0.99, heavy η²=0.92, см. таблицу выше). Но под `--lipid_coldsplit`, где
целые классы уходят из train, MolFormer-эмбеддинг несёт тот же риск "class
fingerprint", что и pocket_sasa_share (η²=0.85) нёс на белковой стороне — до сих
пор непроверенный для этой ветки архитектуры 1.

### 2. Реальный η² 10 pair-descriptor'ов `descriptors_pair_clean` против protein family

Кандидат `scripts/arg_files/descriptors_pair_clean.md` собран из
`PAIR_DESCRIPTOR_NAMES`-дескрипторов, каждый — произведение/min/ratio ОДНОГО
protein-side компонента (уже подтверждённого family-neutral-safe, η² 0.28-0.48) и
одного lipid-side компонента (class-независимого). Предыдущее расследование этой
сессии ВЫВЕЛО безопасность по построению, но никогда не ИЗМЕРЯЛО η² самого
вычисленного значения пары. Построен `analysis/pair_descriptor_family_eta2.py`:
берёт реальные (protein, lipid) пары из interaction table
(`dataloader.chemistry_prior.raw_feature_matrix`, `--zscore` — как в конфиге),
усредняет вычисленное значение по всем липидам, screened against одного белка (чтобы
перейти на ту же гранулярность — один номер на белок — что и белковая таблица), и
считает η² по 35 белкам / 9 семействам, тот же арифметический пол (k-1)/(n-1)=0.235.

| pair-descriptor | protein-side компонент (базовый η²) | η² по белку (это измерение) | above floor (0.235) |
|---|---|---|---|
| flatness_shape_match | pocket_flatness (0.48) | **0.481** | +0.246 |
| volume_fit | pocket_volume_per_sasa (0.41) | **0.409** | +0.174 |
| hbond_match | polar_share≈1−apolar_sasa_share (0.40) | **0.399** | +0.164 |
| buriedness_match | buriedness_q50 (0.32) | **0.316** | +0.081 |
| hbond_match_min | polar_share (0.40), bottleneck | **0.314** | +0.079 |
| aromatic_contact_min | aromatic_share (0.30), bottleneck | **0.303** | +0.067 |
| aromatic_contact | aromatic_share (0.30) | **0.301** | +0.066 |
| hydropathy_rim_match | hydropathy_rim (0.28) | **0.281** | +0.046 |
| tail_elongation_fit | pocket_elongation (0.19), ratio | **0.246** | +0.010 (на границе пола) |
| elongation_shape_match | pocket_elongation (0.19), product | **0.190** | **−0.045 (ниже пола)** |

**Ни один из 10 не превышает известный η² своего protein-side компонента** —
максимум (flatness_shape_match, 0.481) практически равен базовому pocket_flatness
(0.48), не выше. Умножение/min/ratio с независимой от семейства липидной величиной
может только разбавлять family-сигнал усреднением по разным липидам, не усиливать
его — что и наблюдается: у bottleneck-вариантов (hbond_match_min, aromatic_contact_
min) η² чуть НИЖЕ произведения (0.31/0.30 против базовых 0.40/0.30), у
elongation_shape_match (product) он падает ниже арифметического пола вовсе.
**Вывод "safe by construction" подтверждён прямым измерением**, ни один из 10
кандидатов не оказался более утекающим, чем ожидалось.

Для контекста рядом же измерен row-level η² (без усреднения по белку, пул всех
~9905 строк) — он почти везде ≈0.00 (продукты) или 0.07-0.15 (min/ratio-варианты) с
полом ≈0.0008 (9 семейств на тысячи строк вместо 35 белков); это НЕ то же измерение,
что запрошено (гранулярность другая, числа не сравнимы с белковой таблицей
напрямую), приведено только чтобы показать, что и на уровне отдельной строки
структура по семейству не появляется там, где её нет на уровне белка.

### чем посчитано

- MolFormer identity check: `preprocessing/lipid_embedding_identity_check.py`
  (новый), читает `data/lipid_SMILES_embedding_deterministic.pkl`/`.tensors.pt`,
  `data/interactions...csv`. Запуск: `scripts/env.sh python3 preprocessing/
  lipid_embedding_identity_check.py`.
- Pair-descriptor η²: `analysis/pair_descriptor_family_eta2.py` (новый), читает
  `dataloader.chemistry_prior.raw_feature_matrix` с `--zscore=True` (соответствует
  `scripts/arg_files/descriptors_pair_clean.md`). Запуск: `scripts/env.sh python3
  analysis/pair_descriptor_family_eta2.py`.
- Оба скрипта read-only: ничего не обучают, ни в какую общую таблицу не пишут.

## MolFormer-similarity null model vs lipid4 vs Tanimoto, 2026-09-11

Вопрос: даёт ли kNN-null-модель на похожести полного MolFormer-эмбеддинга (вместо 4
ручных дескрипторов lipid4 или Tanimoto по Morgan-фингерпринту) более сильный
(более высокий AUC) честный "пол" для double_coldsplit?

**Что построено.** `preprocessing/build_molformer_similarity_matrix.py` (новый) —
переиспользует загрузку эмбеддинга и per-species pooling из
`lipid_embedding_identity_check.py` (тот же 768-мерный вектор на вид, что и в
identity-check выше, среднее по токенам, затем по кандидатным структурам, полное
покрытие — 283 вида без пропусков), затем прогоняет через
`dataloader.chemistry_prior._standardised_similarity` (тот же 1/(1+euclidean)
после стандартизации столбцов, что `feature_similarity` уже применяет к каждому
именованному дескрипторному набору) и пишет `data/molformer_species_similarity_
matrix.npy` + `data/molformer_species_index.json`. `dataloader/chemistry_prior.py`
получил `molformer_species_similarity(data_dir)` (тот же контракт `(similarity,
index)`, что и `species_similarity` для Tanimoto), `analysis/null_model.py` —
новую ветку `--features=molformer` в `resolve_similarity` рядом с `tanimoto`.
Библиотека Tanimoto-совместимого компактного per-structure формата (uint8/255,
structure_index) НЕ переиспользована — MolFormer уже даёт один вектор на вид, там
нечего компактифицировать.

**Прогон.** Один и тот же протокол для всех трёх — `analysis/null_model.py
--split valid` (дефолт: 7 канонических семейств, seeds 0-4, `--share 0.8`,
`--ratio 2`, `--neighbours 5,15,40`), меняется только `--features`. Никакая сеть
не запускалась (`--scores` не передан) — это сравнение null-моделей самих с собой.

| similarity source | pooled null_AUC_k15 | median | std across seeds | std across families |
|---|---|---|---|---|
| lipid4 (chain,unsaturation,hbond,heavy) | 0.545 | 0.499 | 0.066 | 0.151 |
| tanimoto (Morgan fingerprint, дефолт) | 0.570 | 0.580 | 0.080 | 0.103 |
| molformer (768-мерный эмбеддинг) | 0.544 | 0.528 | 0.067 | 0.056 |

По семействам (null_AUC_k15):

| family | lipid4 | tanimoto | molformer |
|---|---|---|---|
| CRAL-TRIO | 0.483 | 0.453 | 0.562 |
| GLTP | 0.521 | 0.536 | 0.504 |
| IP_trans | 0.681 | 0.686 | 0.584 |
| LBP_BPI_CETP | **0.798** | 0.705 | 0.595 |
| START | 0.508 | 0.505 | 0.446 |
| lipocalin | 0.334 | 0.473 | 0.595 |
| scp2 | 0.488 | 0.629 | 0.525 |

**Вывод.** Пулировано MolFormer-null (0.544) практически совпадает с lipid4
(0.545) и чуть НИЖЕ Tanimoto (0.570) — разрыв между тремя (≤0.026) меньше
std across families любой из них (0.056–0.151), так что три способа статистически
неразличимы как единое число. MolFormer НЕ даёт более сильного пула-floor, чем уже
использовавшиеся lipid4/Tanimoto.

По отдельным семействам картина неоднородная, а не "MolFormer везде слабее/сильнее":
на известном family-leak семействе LBP_BPI_CETP (см. TL;DR выше, test BA 0.826 у
descriptors-baseline) MolFormer-null заметно НИЖЕ обоих (0.595 против lipid4 0.798,
tanimoto 0.705) — то есть 768-мерный эмбеддинг там СЛАБЕЕ ловит утечку семейства,
чем 4 ручных дескриптора или Morgan-фингерпринт. На CRAL-TRIO и lipocalin — наоборот,
MolFormer выше обоих (0.562/0.595 против 0.45-0.63). Ни один из трёх null-model'ей не
доминирует по всем семи семействам сразу.

Для честного "пола" double_coldsplit нет оснований менять lipid4/Tanimoto на
MolFormer-similarity целиком — пулированно они эквивалентны, а по семействам
MolFormer местами слабее именно на семействе, где утечка baseline'а больше всего
задокументирована (LBP_BPI_CETP). Если честный референс должен быть МАКСИМАЛЬНО
консервативным (наибольший null AUC на каждом отдельном семействе), то это не
единый источник похожести, а поточечный max(lipid4, tanimoto, molformer) по
семейству — эта комбинация здесь не строилась, только три исходных числа.

### чем посчитано (MolFormer null model)

- `preprocessing/build_molformer_similarity_matrix.py` (новый) — построение
  матрицы, запуск `scripts/env.sh python3 preprocessing/
  build_molformer_similarity_matrix.py` (283 вида, similarity range [0.011, 1.000]).
- `dataloader/chemistry_prior.py`'s `molformer_species_similarity` (новое) —
  читает написанные .npy/.json.
- `analysis/null_model.py --features=molformer|tanimoto|chain,unsaturation,hbond,heavy --split valid`
  (дефолтные `--share 0.8 --ratio 2 --neighbours 5,15,40`, k15 — колонка
  `null_AUC_k15` из блока "mean AUC"), три отдельных запуска, никакой сети
  (`--scores` не передавался). Read-only, ничего не обучает.
