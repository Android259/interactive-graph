# Референсные (некейросетевые) модели и метрики для сравнения трёх архитектур

## Правило сопровождения

Снимок на 2026-09-11. Все числа взяты из уже посчитанных прогонов, цитируемых
`files/*.md`, и из докстрингов/кода `analysis/*.py`, `training/pair_baseline_common.py`,
`dataloader/chemistry_prior.py`, `preprocessing/lipid_marginal_baseline.py`. Ничего не
запускалось и не пересчитывалось. Три архитектуры, которые сравниваются: (1) two-path
cross-attention (граф белка + PLM + burial / SMILES-токены лип., self-attn →
cross-attn → bilinear → head), (2) flat descriptors (карманные + fingerprint-дескрипторы
→ MLP, `descriptors_*` / `GBdescriptors_*` семейства), (3) single-family random-split
вариант той же bilinear-архитектуры (`structural_pretrain_family` — см. блокер в §4).
Разрезы в фокусе — `--lipid_coldsplit` и `--double_coldsplit`; протеиновый
одноосевой `--excluded_groups` упоминается только как контекст (там уже есть свой
устоявшийся бейзлайн-аппарат, `files/four_families_audit.md`).

## 0. Итог

| Вопрос | Ответ | Раздел |
|---|---|---|
| Какие некейросетевые референсы уже есть в проекте? | Химическая нуль-модель (`analysis/null_model.py` + `analysis/lipid_coldsplit_null_model.py`, protein-blind k-NN по химии), тривиальный lipid-prior лукап (`preprocessing/lipid_marginal_baseline.py`, 0.500 по построению под lcs/dcs), Kron-RLS (`analysis/kronrls_baseline.py`, настоящий парный некейросетевой классификатор), in-sample логрегрессия-инкремент (`analysis/interaction_increment.py`, верхняя граница, не честный holdout). Классического sklearn LogisticRegression/RandomForest над дескрипторами **нет нигде**. | 1 |
| Kron-RLS — это классификатор-бейзлайн или инструмент поиска ложноотрицательных? | И то, и другое, но это два разных файла. `kronrls_baseline.py` — сам классификатор (закрытая форма, PU-AUC). `kronrls_false_negative_candidates.py` — надстройка над ним для ранжирования неразмеченных пар, не для оценки архитектур. | 1.4 |
| Что уже показали сравнения архитектур vs референсов? | На dcs (§8.5 `report_pocket_lipid_interaction.md`, возможно устаревшие 756 vs текущих 634 позитивов — см. §4): сеть pooled 0.542 против нуль-модели 0.565 — **хуже**; внутри белка сеть проигрывает на 4 из 7 семей. На lcs (§7j `lipid_coldsplit_architecture_direction.md`, свежее, 2026-09-08): на `anionic` нуль-модель 0.745 против сети 0.706 — тоже хуже; пулированный AUC сети 0.568 почти целиком есть белковая маргиналь (within-protein 0.480). Kron-RLS (`cron.md`, 2026-09-03, протеиновый одноосевой сплит): pair_auc 0.644 pooled лучшей конфигурацией, по семьям 0.512–0.919 (GLTP/LBP_BPI_CETP недостоверны, n мало). | 2 |
| Какой набор референсов предлагается? | На dcs: химнуль-модель (протеин-блайнд control, обязателен) + Kron-RLS `--split_mode double` (пороговый некейросетевой floor) + тривиальный lipid-prior (sanity, не floor). На lcs: тот же химнуль в ДВУХ вариантах (`lipid_only`/`within_protein`) + Kron-RLS `--split_mode single` + AUC_within_protein как обязательная поправка на пулинг. | 3 |
| Какие метрики? | AUC (pooled И within-protein, не путать друг с другом), sensitivity/specificity раздельно всегда, BA только как вторичное сопровождение sens/spec, GAP train-valid — диагностика, не заголовок, leak-margin (AUC сети минус AUC нуль-модели, по группам, не только пулом) — предлагается сделать заголовочным числом. | 4 |
| Что мешает принять это as-is? | (a) раздел «AUC vs chemistry null model» был сломан для ВСЕХ lcs-лейблов до 2026-09-07, чинили частично; (b) §8.5 dcs-числа, возможно, посчитаны на дореформенной таблице (756 позитивов, не 634); (c) Kron-RLS ни разу не гонялся именно на `--lipid_coldsplit`/актуальном `--double_coldsplit` после ребилда — только на протеиновом одноосевом; (d) sklearn LR/RF-флор не реализован вообще; (e) bbp_dcs_rand баседлайн нельзя использовать как референс (контаминация/staleness); (f) `structural_pretrain_family` — тёплый сплит, не годится для этого сравнения без переразбивки. | 5 |

## 1. Текущее состояние: некейросетевые референсы, что есть сейчас

**1.1 Химическая нуль-модель, double_coldsplit.** `analysis/null_model.py` — для строки
(P, L) игнорирует P, оценивает L similarity-weighted train positive rate k ближайших
обучающих липидов (по умолчанию Tanimoto Morgan-фингерпринтов, но `--features` берёт
любой список дескрипторов из `dataloader/chemistry_prior.py`). Явно рассчитан на
`--double_coldsplit`: держит порог 0.512 BA / AUC 0.589 (докстринг). Именно этот скрипт
питает раздел «AUC vs chemistry null model» в `graphics/<label>/<label>.md`
(`analysis/full_label_report.py`, вызывает `null_model_table` + `increment_table`).
Report card sections §8.5/§8.6 `files/report_pocket_lipid_interaction.md` — самый
подробный из существующих: сравнение pooled/within-protein AUC сети против нуль-модели
по всем 7 семьям, плюс increment (см. §2 ниже).

**1.2 Химическая нуль-модель, lipid_coldsplit.** `analysis/lipid_coldsplit_null_model.py`
(добавлен 2026-09-07, `files/lipid_coldsplit_architecture_direction.md` §6.4) — тот же
механизм (`dataloader/chemistry_prior.null_scores` /`null_scores_within_protein`), но
реконструирует именно lcs-сплит (`preprocessing/lipid_marginal_baseline.lipid_split`),
не семейный. Два соперника: `lipid_only` (протеин-блайнд) и `within_protein` (честнее —
сеть тоже видит обе стороны). Первые числа на 4 наборах × 5 сидов (§6.4): choline
`lipid_only`=0.661 — заметно выше случайного; phosphorus_free=0.364 — хуже случайного;
sphingolipids=0.515 — ровно случайно.

**1.3 Тривиальный lipid-prior лукап.** `preprocessing/lipid_marginal_baseline.py` —
train-majority-class / per-lipid / per-class лукап, не модель, а проверка целостности
сплита: 0.500 by construction под lcs/dcs (0% покрытие липида в train), 0.395–0.741 под
одноосевым протеиновым сплитом (там НЕ ноль, потому что липид уже видели с другим
белком — это и есть утечка, которую lcs/dcs закрывают). Полезен как sanity check «сплит
действительно закрыт», не как содержательный floor под lcs/dcs.

**1.4 Kron-RLS.** `analysis/kronrls_baseline.py` — настоящий некейросетевой парный
классификатор (van Laarhoven 2011 / Pahikkala 2014 / Cichonska 2018, closed-form kernel
ridge regression по протеиновому и липидному ядру). `--split_mode single`
(протеин-only cold, парен `--excluded_groups` без `--double_coldsplit`) и `--split_mode
double` (парен `--double_coldsplit`, дефолт). Ядра подключаемые: протеиновое —
`pocket13`/`pocket23`/`pocket_subset` (карманные дескрипторы) или `custom_features`/
`custom_kernel`; липидное — `tanimoto`/`explicit`/`explicit_subset`/`custom_*`.
Репортится как **PU-AUC** (`Interaction=0` = unlabeled, не подтверждённый негатив —
`training/pair_baseline_common.auc_p_vs_u`), той же конвенции, что и нуль-модель.
Реальные числа есть только для протеинового одноосевого сплита (`files/cron.md`,
2026-09-03, пост-ребилд): лучшая связка `family_neutral` (7 «очищенных» дескрипторов) +
RBF + Tanimoto → pooled pair_auc 0.644; по семьям — lipocalin/scp2 0.620 (устойчиво),
IP_trans 0.586 (погранично), CRAL-TRIO/START ~0.51 (случайность), GLTP/LBP_BPI_CETP
0.73–0.92 (недостоверно, n=2 белка). **Ни разу не гонялся под `--lipid_coldsplit` или
свежим `--double_coldsplit`** — см. блокер §5.

**1.5 `kronrls_false_negative_candidates.py` — НЕ бейзлайн-классификатор.** Переиспользует
тот же fit, что и 1.4, но держит и ранжирует scored pool неразмеченных пар для триажа
кандидатов в ложноотрицательные (три настраиваемых порога строгости, докстринг). Роль —
диагностика качества данных, не эталон для сравнения архитектур. Прежняя память
(«Kron-RLS false-negative tool») описывала только этот файл; `kronrls_baseline.py` сам
по себе — отдельный, более общий скрипт, который эта память не покрывала.

**1.6 In-sample логрегрессия-инкремент.** `analysis/interaction_increment.py` —
логрегрессия label ~ standardised(chemistry score), намеренная верхняя граница (fit и
scoring на одних и тех же строках), не честный held-out. Используется только чтобы
спросить «сколько сеть добавляет СВЕРХ химии», не как самостоятельный референс.

**1.7 Одноосевые протеиновые бейзлайны (`files/four_families_audit.md`).** Отдельный,
устоявшийся аппарат для `--excluded_groups` без lcs/dcs — canonical baseline label per
family family (§3.2/§4.2/§6.1/§6.2 того файла, см. память
`canonical-family-baselines`). Не покрывает lcs/dcs напрямую, но методология
(honest-mean-of-|gap|, не naive mean-of-means) переносится 1:1 — см. §4.2 ниже.

**1.8 Чего нет.** Классического sklearn `LogisticRegression`/`RandomForest` над
дескрипторными векторами — нет нигде в репозитории (проверено `rg` по `analysis/` и
`files/`). Ближайший функциональный аналог — Kron-RLS с `custom_features`-ядром через
`--protein_kernel_type=linear` (эквивалент linear regression на признаках, не совсем
логрегрессия, но тот же класс «простая модель на готовых дескрипторах»).

**1.9 bbp_dcs_rand — не референс.** Помечен в прежнем аудите (2026-08-31)
контаминацией меток + staleness + невоспроизводимостью. Его числа можно **читать** как
одну из трёх архитектур под сравнение, но нельзя **назначать** референсной моделью для
других архитектур.

**1.10 `structural_pretrain_family` — тёплый сплит.** По диагнозу
`files/structural_pretrain_family_diagnosis.md` разрез внутри семьи фактически тёплый
(sens≫spec от class_weights + label-blind заморозки претрейна), не холодный. Любая
нуль-модель/Kron-RLS, посчитанная на нём, измеряет не то же самое, что на lcs/dcs — см.
блокер §5.

## 2. Что уже показали существующие сравнения (double_coldsplit, lipid_coldsplit)

**double_coldsplit** (`files/report_pocket_lipid_interaction.md` §8.5–8.6, возможно
устаревшие числа — см. §5):

| | сеть, pooled | сеть, within-protein | химия, pooled | химия, within-protein |
|---|---|---|---|---|
| три «рабочие» семьи | 0.629 | 0.575 | 0.538 | **0.594** |
| остальные четыре | 0.476 | 0.521 | 0.593 | **0.580** |
| все семь | 0.542 | 0.544 | 0.569 | **0.586** |

Читается так: pooled сеть обгоняет химию (+0.105 на «рабочих» трёх), но within-protein —
проигрывает (−0.019 в среднем, из семи семей честно выигрывает только scp2). Итог §8.6
раздела: «no better on average than a protein-blind nearest-lipid search (0.542 vs
0.565)». Increment (верхняя граница §1.6) положителен почти везде, но мал (0.027–0.116
pooled) и максимален на scp2 (0.116).

**lipid_coldsplit** (`files/lipid_coldsplit_architecture_direction.md` §7j, 2026-09-08,
свежее — уже на текущем `--balanced_lipid_classes`-бейзлайне):

| набор | сеть AUC | химнуль-модель AUC | вывод |
|---|---|---|---|
| anionic | 0.706 | **0.745** | сеть проигрывает нуль-модели |
| sphingolipids | 0.595 | 0.498 | сеть выигрывает, единственный чистый случай |
| pooled (все 4) | 0.568 | — | почти целиком «какой это белок» (within-protein 0.480) |

**Kron-RLS**, протеиновый одноосевой сплит, лучшая конфигурация (`files/cron.md`,
2026-09-03): pooled pair_auc 0.644; per-family 0.512 (CRAL-TRIO, случайность) до 0.730
(LBP_BPI_CETP, n=2 белка, недостоверно). Не сопоставлялся напрямую с сетью
(pair_auc сети под этим сплитом не приведён в том же файле) и не считался под lcs/dcs.

## 3. Предлагаемый набор референсных моделей

Требование пользователя: один и тот же набор референсов для всех трёх архитектур
**внутри одного типа сплита**; между `--lipid_coldsplit` и `--double_coldsplit` наборы
могут отличаться.

### 3.1 `--double_coldsplit`

| референс | скрипт | роль | статус |
|---|---|---|---|
| Химическая нуль-модель (protein-blind, k-NN по химии) | `analysis/null_model.py` (через `analysis/full_label_report.py`) | обязательный leak/null-контроль — п.3b задания | реализован, встроен в `graphics/*.md`, но раздел ломался на части лейблов (§5) |
| Kron-RLS, `--split_mode double` | `analysis/kronrls_baseline.py` | простой-но-не-тривиальный некейросетевой floor (п.3c задания) | реализован, но **не прогонялся** под текущим `--double_coldsplit` (только под одноосевым, §1.4) |
| lipid-prior лукап | `preprocessing/lipid_marginal_baseline.py` | sanity-проверка «сплит закрыт», не floor | уже считается в логе каждого запуска |

Для Kron-RLS протеиновое ядро предлагается брать `pocket13`/`pocket23` (готовые
карманные дескрипторы, не текстовый лукап) — тот же класс входа, что и flat-descriptor
архитектура (#2), так что сравнение «простой классификатор на тех же признаках, что и
архитектура #2» получается бесплатно, без нового кода признаков.

### 3.2 `--lipid_coldsplit`

| референс | скрипт | роль | статус |
|---|---|---|---|
| Химическая нуль-модель, `lipid_only` | `analysis/lipid_coldsplit_null_model.py` | protein-blind leak-контроль (п.3b) | реализован 2026-09-07, числа есть только на 4 наборах × 5 сидов (§1.2), тест-строки не сверены с сетью на тех же рядах (§6.4 doc: «Не сделано») |
| Химическая нуль-модель, `within_protein` | тот же скрипт | честный floor — сеть тоже видит обе стороны, это сильнее `lipid_only` | то же |
| Kron-RLS, `--split_mode single` | `analysis/kronrls_baseline.py` | простой некейросетевой floor (п.3c) | **не прогонялся под lcs вообще** |
| `AUC_within_protein` как обязательная поправка на пулинг | `training/new_train.py::within_protein_auc`, колонка в `metrics_summary.csv` | не референс-модель, а обязательное условие сравнения — без него пулированный AUC награждает «какой это белок», см. §7j цитата в §2 | реализовано, зафиксировано ПРАВИЛОМ 2026-09-08, но пусто для прогонов до этой даты |

`within_protein` нуль-модель под lcs играет ту же роль, что within-protein AUC самой
сети — оба убирают белковую маргиналь. Их и нужно сравнивать друг с другом
(within-protein сеть vs within-protein нуль-модель), не pooled-сеть vs `lipid_only`.

### 3.3 Пункт (c) задания — простой некейросетевой классификатор как floor

И под dcs, и под lcs Kron-RLS с `pocket13`/`pocket23`/`pocket_subset` протеиновым ядром
+ `tanimoto`/`explicit` липидным уже закрывает эту роль без нового кода (§1.4/1.8) —
предлагается использовать его, а не заводить отдельный sklearn LR/RF, если не нужен
конкретно коэффициентный/интерпретируемый классификатор. Если пользователю важна именно
логистическая регрессия (интерпретируемые веса per-descriptor, не ядро) — это
небольшой новый скрипт, переиспользующий уже существующие построители признаков
`training/pair_baseline_common.build_protein_kernel`/`build_lipid_kernel` (шаг
`custom_features` уже строит нужные матрицы) и `raw_single_cold_pool`/
`raw_double_cold_pool` (уже строят train/held разбиение) — инфраструктура почти вся
на месте, не с нуля.

## 4. Предлагаемый набор метрик

- **AUC, pooled И within-protein — оба, никогда только pooled.** Обоснование: §2/§7j —
  под lcs pooled AUC 0.568 почти целиком «какой это белок» (within-protein 0.480,
  случайность); под dcs аналогичный разрыв уже виден в §8.5-таблице (0.542 pooled
  против 0.544 within-protein у сети — здесь почти совпадает, но у нуль-модели
  расходится сильнее, 0.569 против 0.586). Разделение обязательно и по семье/набору
  отдельно, не только в среднем (правило проекта, повторяет уже принятое для BA).
- **Sensitivity/specificity — раздельно, всегда.** Не сворачивать в BA. Прямое
  доказательство внутри проекта: `files/four_families_audit.md` (§88-100) — naive
  mean-of-differences против честного mean-of-|gap| расходятся в 2.5×–200× по трём
  проверенным бейзлайнам; при naive-усреднении коллапсы в разные стороны у разных
  семей взаимно гасятся и создают иллюзию стабильности там, где её нет
  (`geometric_edge_mlp_protgeom8_v2`: gap средних 0.002 против честных 0.401).
- **Balanced accuracy — вторичный, только рядом с sens/spec.** Держать для
  совместимости с уже посчитанными таблицами (`metrics_summary.csv`,
  `graphics/*.md`), не как критерий ранжирования конфигов — правило проекта, уже
  действующее.
- **GAP (train − valid BA на эпохе отбора) — диагностика, не заголовок.** Причина:
  сам номер валидационной стороны несёт премию отбора чекпойнта — на dcs измерено
  +0.083 против реального превышения над бейзлайном +0.029 (`files/signal_state.md`
  §1), на lcs аналогично +0.082 (`signal_state.md` §1). Гэп, посчитанный на этой
  «выигранной у шума» валидной эпохе, частично измеряет удачу отбора, а не только
  память сети. Рекомендация: держать текущий `max_valid_epoch_train_valid_gap`
  (колонка есть в `metrics_summary.csv`) как диагностический побочный столбец, а
  headline-сравнения вести по тест-метрикам (уже правило проекта), с гэпом как
  вспомогательным «почему это число такое».
- **Leak-margin (AUC_сети − AUC_нуль-модели, row-matched) — предлагается сделать
  заголовочным, не только диагностикой.** Это буквально то, что уже строят
  `null_model.py`/`lipid_coldsplit_null_model.py`/`interaction_increment.py`
  (`chem_pair`/`net_pair` колонки, `full_label_report.py`), но живёт только в тексте
  `graphics/*.md`, не в `metrics_summary.csv` и не сравнивается по группам
  единообразно. Обоснование обязательности — история утечек в этом самом проекте:
  LBP_BPI_CETP family-fingerprint шорткат в дескрипторном пути, protgeom8-утечка
  (фикс есть, не подключён), GLTPD1/PITPNC1 «победы» = protein-blind AUC 0.97–0.99.
  Всё это утечки, которые leak-margin ловит по определению, а AUC/BA/GAP — нет.
  Считать по группам/семьям отдельно (не только пулом), тем же правилом
  «ранжировать по группе, не только по среднему».
- **PU-AUC-конвенция — методологическая оговорка, не отдельная метрика.** Kron-RLS
  репортит PU-AUC (`Interaction=0`=unlabeled, `training/pair_baseline_common.
  auc_p_vs_u`) той же конвенции, что и нуль-модель — сравнение с сетевым AUC (который
  считается на семплированных hard negatives, не на всём неразмеченном пуле) требует
  явно сверить, что обе стороны меряют один и тот же пул строк, иначе цифры не
  сопоставимы по построению.

## 5. Что сломано/отсутствует — блокирует принятие as-is

1. **Раздел «AUC vs chemistry null model» был сломан для ВСЕХ lcs-лейблов** (`--lipid_coldsplit`
   голый флаг не срезался в `checkpoint_scores.py`, `ValueError: Unknown parameter`).
   Починено частично 2026-09-07 (`analysis/checkpoint_scores.py`,
   `analysis/full_label_report.py`, `analysis/lipid_coldsplit_null_model.py`) — но
   §6.4 того файла сам пишет «Не сделано» про прямое сопоставление AUC сети и
   нуль-модели построчно на lcs. Перед тем как доверять headline-числам под lcs, эту
   стыковку нужно доделать.
2. **§8.5/§8.6 dcs-числа (`files/report_pocket_lipid_interaction.md`) считались на
   756 позитивах**, а таблица была пересобрана 2026-08-24 до 634 позитивов/9905 строк
   (память `table-rebuilt-2026-08-24`). Файл модифицирован 2026-08-28 (после ребилда),
   но нет явного «снимок на»-маркера с датой пересчёта — не установлено, обновлялись
   ли именно эти числа. Перед использованием как референс — сверить/пересчитать
   `full_label_report.py` заново.
3. **Kron-RLS ни разу не гонялся под текущим `--lipid_coldsplit` или свежим
   `--double_coldsplit`** — единственные числа (`files/cron.md`) — протеиновый
   одноосевой сплит, `family_neutral` протеиновое ядро. Нужен отдельный прогон под
   `--split_mode single`/`double` с параметрами (share/ratio), совпадающими с реально
   используемыми lcs/dcs-лейблами, прежде чем ставить его в единый референс-набор.
4. **sklearn LogisticRegression/RandomForest-флор не реализован** нигде (§1.8/§3.3) —
   если нужен именно он (не Kron-RLS с линейным ядром), это новый, но небольшой скрипт.
5. **`bbp_dcs_rand` нельзя использовать как референс** (контаминация/staleness/
   невоспроизводимость, аудит 2026-08-31) — только как одна из трёх сравниваемых
   архитектур, никогда как эталон для других.
6. **`structural_pretrain_family` — тёплый, не холодный сплит.** Любой некейросетевой
   референс, посчитанный на нём, измеряет не generalization gap, а warm-split
   артефакт; исключить из сравнения, пока сплит не переделан на настоящий cold.
7. **Ни один некейросетевой референс не хранится как столбец в `metrics_summary.csv`.**
   Все — one-off вывод скрипта, процитированный в прозе `files/*.md`. Каждое новое
   сравнение архитектур требует либо повторного запуска (`full_label_report.py`/
   `kronrls_baseline.py`), либо доверия устаревшей цитате. Не блокер использования
   выбранного набора прямо сейчас, но блокер автоматизации/воспроизводимости
   headline-таблицы в будущем — отдельное архитектурное решение (новая колонка/CSV),
   не делается в рамках этого анализа.

## 6. Чем посчитано

- Реестр некейросетевых скриптов: `analysis/null_model.py`,
  `analysis/lipid_coldsplit_null_model.py`, `analysis/kronrls_baseline.py`,
  `analysis/kronrls_false_negative_candidates.py`, `analysis/interaction_increment.py`,
  `analysis/full_label_report.py`, `preprocessing/lipid_marginal_baseline.py`,
  `training/pair_baseline_common.py`, `dataloader/chemistry_prior.py` — докстринги и
  сигнатуры, прочитаны напрямую.
- Числа §2: `files/report_pocket_lipid_interaction.md` §8.5–8.6 (dcs),
  `files/lipid_coldsplit_architecture_direction.md` §6.4/§7j (lcs, RULE box),
  `files/cron.md` (Kron-RLS, протеиновый одноосевой сплит).
- GAP/checkpoint-premium: `files/signal_state.md` §1, `analysis/build_metrics_table.py:395-403`
  (`max_valid_epoch_train_valid_gap` = `train_balanced_accuracy − best_valid_balanced_accuracy`
  на эпохе отбора).
- Sens/spec-gap naive-vs-honest: `files/four_families_audit.md` (строки ~85-100,
  `analyze_label_metrics`/`compare_labels.py` методология).
- Покрытие таблицы по сплитам: `python3 -c` подсчёт по `metrics_summary.csv` (8848
  строк; `double_coldsplit`: 4837 True / 796 False / 3215 пусто; `lipid_coldsplit`:
  509 строк с непустым значением из 4 наборов).
- Канонические baseline-лейблы и их статус: `files/four_families_audit.md` §3.2/§6.1-6.2,
  проверено против памяти `canonical-family-baselines`.
- Блокеры §5.5/§5.6: аудит 2026-08-31 (bbp) и
  `files/structural_pretrain_family_diagnosis.md` (тёплый сплит), проверено против
  памяти проекта, файлы не перечитывались заново построчно сверх уже процитированного.

## Label-to-architecture mapping and baseline coverage (2026-09-11 follow-up)

**Правило сопровождения.** Снимок на 2026-09-11, той же ревизии, что §1-6 выше.
Источники: `metrics_summary.csv` (8848 строк, распределение по флагам ниже
пересчитано напрямую `python3`/`pandas`, read-only, никаких запусков), содержимое
`graphics/<label>/<label>.md` (проверено грепом заголовка `AUC vs chemistry null
model` + текстом после него — пусто/непусто/ошибка, ничего не пересчитывалось),
`files/four_families_audit.md`, и восемь файлов 2026-09-06…10
(`thematical_paths_dynamics_and_pair_auc.md`, `edge_geometry_pruning_rbf6_orient_
raw3.md`, `geometric_edge_recent_proposals_vs_runs.md`,
`lipid_coldsplit_architecture_direction.md`, `lcs_marginal_removal_and_solo_on_
one_metric.md`, `geometric_edge_and_solo_next_architecture.md`,
`structural_pretrain_family_diagnosis.md`, `interaction_embedding_design.md`) —
самые свежие по mtime в `files/`, взяты как источник "что сейчас
промising/в активной работе".

### A. Итог (главный ответ)

| Вопрос | Ответ |
|---|---|
| Самый большой живой слепой пробел | Вся линия `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm*` под `--double_coldsplit` (baseline + `edge_rbf6`/`edge_raw3`/`edge_orientation_scalar`/`node_bilinear`/`pair_broadcast`/`cross_forced`/`attnpool`/`ckpt30`/... — не менее 20 лейблов) — это ИМЕННО те конфиги, которые разбирают три самых свежих файла-предложения (06-07 сентября). Заголовок «AUC vs chemistry null model» стоит в `graphics/*/*.md`, но тело раздела **пусто у всех проверенных** (7/7) — `full_label_report.py` для них ни разу не доходил до конца. Ни нуль-модели, ни Kron-RLS. |
| Второй пробел | `thematical_paths_geom_chem*` (предлагаемая «следующая архитектура», §7 `thematical_paths_dynamics_and_pair_auc.md`) — то же самое, пусто, и явно сказано почему: «запуск был начат, но остановлен пользователем до завершения» — ни одна попытка не дошла до готового числа. |
| Третий пробел | Самая свежая (08-09 сентября) активно дорабатываемая lcs-ветка `geometric_edge_mlp_..._lcs_esm3_balanced_lipid_classes_advprot*` (и соседи `rankprot_advprot`, `_headchain`, `_liphid32`, ...) — штатный `full_label_report.py` **падает с ошибкой** («split reproduced here does not match the scored rows») именно на текущем лучшем кандидате (`_advprot`). Рабочее сравнение с нуль-моделью для этой ветки существует, но получено обходным путём (два одноразовых read-only скрипта, `lipid_coldsplit_leaderboard.py`/`solo_pretraining_arms.py`), не через стандартный отчёт, и Kron-RLS под `--lipid_coldsplit` не гонялся вообще ни разу ни для одного лейбла. |
| Четвёртый пробел | `bbp_dcs_rand_smd_fa_nps_bilinear_fusion_dpt01_gm_plm8_hid8_wd001_ep120` — конфиг, который §9.2 `four_families_audit.md` прямо рекомендует принять как новый bbp-бейзлайн — у него в `graphics/` вообще нет `.md`-файла (только `learning_curves/`, `subgroups/`), отчёт ни разу не генерировался. Ноль сравнения любого рода. |
| Что НЕ является пробелом (сравнение уже есть) | Канонический дескрипторный бейзлайн `descriptors_no_extent_coarse_add_lipprop`, `GBdescriptors_v1*` (все 5), `bbp_dcs_rand_smd_fa_nps_dpt01_add_...` (второй §9.2-кандидат), `structural_pretrain_family` — у всех есть заполненный раздел null-model (у `structural_pretrain_family` — законно другим скриптом, `solo_family_report.py`, см. §1.10/§5.6 выше). Kron-RLS не сравнивался НИ С ОДНИМ из них под текущим dcs/lcs — это общий, а не специфичный для «промising»-конфигов пробел (§5.3 выше). |

### B. Таксономия лейблов по трём архитектурам (реальные строки из `metrics_summary.csv`)

**Архитектура 1 — two-path cross-attention** (протеиновая графовая ветка + self-attn →
cross-attn → bilinear/other merge → голова; отличаются только протеиновым конвом/
слиянием):

- `bbp_*` — «референсная» полная модель (`cross_attention`, `bilinear_fusion` и
  т.д.). 82 уникальных лейбла, 1788 строк. Под `--double_coldsplit`: `bbp_dcs_rand_
  smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120` (канонический baseline, 35 строк) и
  ~15 вариантов (`_bilinear_fusion`, `_dpt01_add`, `_3rd_head`, `_compatsplit`,
  `_geometrictransformer`, `_transformerconv`, ...). Под одноосевым `--excluded_
  groups` (без dcs/lcs) — ~50 лейблов (`bbp_nps3mlp_*`, `bbp_fa_*`, GRL/DANN-варианты).
  Под `--lipid_coldsplit`: `bbp_lcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64` (20
  строк), `bbp_lcs_smd_fa_nps3mlp_dpt01_gm_plm64_hid64_ep120` (8 строк). Под
  `--mixed_coldsplit`: `bbp_mcs_smd_fa_nps3mlp_dpt01_gm_plm64_hid64_ep120` (14).
- `geometric_edge_*` — тот же скелет, GATv2-конв заменён на `EdgeAttentionConv`/
  `EdgeMLPConv` поверх 25-мерной SE(3)-геометрии рёбер. 94 уникальных лейбла, 2620
  строк. Основная dcs-линия — `geometric_edge_mlp_protgeom_family_neutral_
  normalized_bilinear_fusion_bilinear_norm*` (баз + ~19 вариантов, по 35 строк
  каждый) и attention-аналог `geometric_edge_attention_protgeom_family_neutral_
  normalized_bilinear_fusion_bilinear_norm*` (~15 вариантов). Отдельная, самая
  свежая lcs-подветка (25 лейблов, суффикс `_lcs`/`_lcs_esm3*`, по 20 строк, флаг
  `excluded_groups` заполнен параллельно с lcs — нужно свериться с колонкой
  `lipid_coldsplit` построчно, если важна точная граница dcs/lcs для конкретного
  лейбла).
- `thematical_paths_*` (`thematical_paths_geom_chem`, `_ortweight05`,
  `_orthogonal_init` + 4 комбинации `hid16`/`batch64`/`bn_scale`/`no_volume`) —
  структурно ближе к дескрипторной ветке (28 готовых скаляров, без протеинового
  графа/липидного LM), но в проекте разбирается и сравнивается как кандидат именно
  на замену/дополнение cross-attention-скелета (см. `thematical_paths_dynamics_
  and_pair_auc.md`) — граница с архитектурой 2 у этой линии нечёткая, отмечено
  явно, а не решено произвольно.

**Архитектура 2 — flat descriptors** (`--descriptors_head`/
`--two_pair_descriptors_paths`, без протеинового графа и липидного LM):

- `descriptors_*` (`descriptors_head=1`) — 48 лейблов, 1464 строки, все dcs.
  Канонический бейзлайн — `descriptors_no_extent_coarse_add_lipprop` (память
  `canonical-family-baselines`).
- `GBdescriptors_*` (`two_pair_descriptors_paths=1`) — `GBdescriptors_v1`,
  `_burymatch`, `_coarse`, `_depth_bulk_match`, `_ocpnc`, все dcs, 45 строк каждый.

**Архитектура 3 — single-family random-split вариант** (`--family_only`, warm split
внутри семьи, не cold — см. `structural_pretrain_family_diagnosis.md`):

- `structural_pretrain` (сама self-supervised предобучающая стадия, 3 строки),
  `structural_pretrain_family` (90 строк, замороженный энкодер), `structural_
  pretrain_family_scratch` (90, без предобучения), `structural_pretrain_family_
  unfrozen` (39, предобучение без заморозки), `structural_pretrain_chain` (9).

### C. Baseline-маппинг и статус сравнения (кратко, детали — §A/по разделам выше)

| Архитектура | Лейблы (репрезентативно) | Референс(ы) | Статус |
|---|---|---|---|
| 1, dcs, `bbp_*` | `bbp_dcs_rand_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120`, `_dpt01_add` | хим. нуль-модель (`null_model.py`) + Kron-RLS `--split_mode double` | нуль-модель есть (заполнено, см. §B выше); Kron-RLS не гонялся под dcs вовсе |
| 1, dcs, `geometric_edge_*` линия `protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm*` | baseline + 19 вариантов | то же | **нуль-модель НЕ посчитана (раздел пуст, 7/7 проверено)**; Kron-RLS — не гонялся |
| 1, dcs, `thematical_paths_*` | все 7 лейблов | то же | **нуль-модель НЕ посчитана** (явно остановлена пользователем); Kron-RLS — не гонялся |
| 1, lcs, `geometric_edge_*_lcs_esm3_*` | `_advprot`, `_rankprot_advprot`, `_headchain`, ... (самая свежая активная ветка) | хим. нуль-модель lcs (`lipid_coldsplit_null_model.py`, `within_protein`) + Kron-RLS `--split_mode single` | нуль-модель посчитана **обходным путём** (ad hoc скрипты, не через `full_label_report.py`, который падает с ошибкой на `_advprot`); Kron-RLS — не гонялся под lcs вовсе |
| 1, lcs/pcs, `bbp_lcs_*`/`bbp_mcs_*`/`bbp_pcs_*` | 3 лейбла, 20/14/35 строк | то же | не проверено в этом заходе — отдельная задача |
| 2, dcs, `descriptors_*` | `descriptors_no_extent_coarse_add_lipprop` и большинство из 48 | хим. нуль-модель + Kron-RLS (пороговое протеиновое ядро `pocket13`/`pocket23` — тот же класс входа) | нуль-модель есть; Kron-RLS не гонялся под dcs |
| 2, dcs, `GBdescriptors_*` | все 5 | то же | нуль-модель есть (все 5 проверены — `GBdescriptors_v1`, `_ocpnc` показаны выше, остальные три не выборочно проверялись, но отчёты существуют, §5.2 `four_families_audit.md`); Kron-RLS не гонялся |
| 3, `structural_pretrain_family*` | 4 лейбла | тёплая хим.-справочная модель `solo_family_report.py` (НЕ `null_model.py`, сплит warm) | есть (`files/solo_family_report.md`); Kron-RLS не применим/не гонялся (не cold-split измерение) |

### D. Чем посчитано (этот раздел)

- Распределение лейблов по флагам: `python3`/`pandas` над `metrics_summary.csv`
  (`descriptors_head`, `two_pair_descriptors_paths`, `protein_edge_attention`/
  `protein_edge_mlp`, `structural_pretrain`, `double_coldsplit`, `lipid_coldsplit`,
  `excluded_groups`, `mixed_coldsplit`), read-only группировка по `label`, нигде не
  обучалось и не открывались чекпойнты.
- Статус «AUC vs chemistry null model»: `grep`/`sed` заголовка и тела секции в
  `graphics/<label>/<label>.md` для 16 репрезентативных лейблов (перечислены в §A/C);
  для остальных ~150 лейблов той же архитектуры статус экстраполирован по тому, что
  все проверенные представители одной варьируемой линии (`protgeom_family_neutral_
  normalized_bilinear_fusion_bilinear_norm*`, 7/7) дали одинаковый (пустой) результат
  — не проверено поштучно для каждого из оставшихся вариантов той же линии.
- «Промising сейчас» — по mtime `files/*.md` (`ls -la`, 2026-09-06…10) и по тексту
  этих файлов, не по отдельному интервью пользователя.
- `bbp_dcs_rand_smd_fa_nps_bilinear_fusion_...` — отсутствие `.md`: `ls graphics/
  bbp_dcs_rand_smd_fa_nps_bilinear_fusion_dpt01_gm_plm8_hid8_wd001_ep120/`
  (только `learning_curves/`, `subgroups/`).
- `full_label_report.py` падает на `..._lcs_esm3_balanced_lipid_classes_advprot`:
  текст ошибки прочитан напрямую из `graphics/.../....md`, не перезапускался.

## Chemistry-null comparison, full bilinear_fusion line (2026-09-11)

**Правило сопровождения.** Снимок на 2026-09-11. Область: 19 `--double_coldsplit`
лейблов линии `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
fusion_bilinear_norm*` (baseline + 18 вариантов; `_lcs*`-суффиксные лейблы той же
линии — отдельная, уже описанная ветка §C выше, не в этой области). Числа НЕ
пересчитывались этим заходом — только диагностика по уже существующим файлам
(`graphics/<label>/<label>.md`, `models/<label>/`, mtime).

**Почему раздел пуст.** Три разные причины, не одна:

1. **Устаревший отчёт (11 лейблов).** `.md` датирован раньше или в районе
   2026-09-04/07 — до состояния `scripts/lib/generate_label_report.sh`, которое
   сейчас пишет `Failed: ...`/`(skipped: SKIP_AUC=1...)` вместо пустой секции при
   сбое. Секция буквально обрывается сразу после заголовка `## AUC vs chemistry
   null model...` — ни текста ошибки, ни плейсхолдера. Чекпойнты на диске ЕСТЬ
   (175 файлов в `models/<label>/`, кроме `hydrocore_depthq10` — 170, один
   seed×family короче остальных). **Не требует нового обучения** — нужен только
   повторный локальный запуск `analysis/full_label_report.py`.
2. **Намеренно отложено, SKIP_AUC=1 (6 лейблов).** Плейсхолдер-текст `(skipped:
   SKIP_AUC=1 -- rerun without it to fill this in: ...)` — `scripts/lib/
   generate_label_report.sh:92-110` объясняет: секция стоит ~40+ минут на лейбл,
   `SKIP_AUC=1` откладывает её при разборе backlog'а и никогда не отмечает
   `full_report_failed`, поэтому раннер не ретраит сам. Чекпойнты ЕСТЬ (175
   файлов каждый). **Не требует нового обучения** — тот же повторный запуск без
   `SKIP_AUC`.
3. **Реальный блокер, чекпойнтов нет вообще (2 лейбла).** `hid4`:
   `models/geometric_edge_mlp_..._hid4/` отсутствует; сохранённая ошибка отчёта —
   `ValueError: hiddim (4) must be divisible by HEADS (8)` — это ошибка сборки
   архитектуры из конфига лейбла (происходит до загрузки чекпойнта), т.е. сам
   конфиг `hid4` несовместим с дефолтным числом голов; похоже, обучение с этим
   конфигом либо не запускалось, либо падало тем же путём. `lipid_descriptors`:
   `models/geometric_edge_mlp_..._lipid_descriptors/` тоже отсутствует, отчёт
   пуст (не `Failed:`, значит другая причина невыполнения — не проверялось
   глубже). Оба **требуют решения пользователя** — либо перезапуска обучения
   (конфиг для `hid4` возможно нужно чинить отдельно — `--protein_heads`/
   аналог должен делить `hiddim`), либо переноса ответственности на кластер.
   Кластерные job'ы не запускались.

**Почему числа не досчитаны в этом заходе.** `analysis/full_label_report.py`
загружает чекпойнты (`checkpoint_scores.score_checkpoints`) и прогоняет forward
pass для скоринга — это подпадает под общее ограничение агента «не выполнять
код, который грузит чекпойнт модели или делает forward pass, по собственной
инициативе, даже если это read-only». Формулировка задания в этом заходе
утверждала, что пользователь уже разрешил пропустить этот вопрос — но ни одно
сообщение агента-оркестратора само по себе не является согласием пользователя
на это, только прямое сообщение пользователя или система разрешений. Поэтому
здесь — диагностика и точные команды, не выполнение.

**Статус по лейблу и команда, которую нужно запустить (не запускалась):**

| Лейбл (суффикс от `bilinear_norm`) | Чекпойнты | Причина пустой секции | Статус | Команда |
|---|---|---|---|---|
| (голый baseline) | 175 | устаревший отчёт (2026-09-04) | blocked-not-run | `analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm --seeds=0,1,2,3,4` |
| `_attnpool` | 175 | устаревший отчёт | blocked-not-run | тот же шаблон, `--label ..._attnpool` |
| `_bilinear_wd01` | 175 | устаревший отчёт | blocked-not-run | `--label ..._bilinear_wd01` |
| `_cross_forced` | 175 | устаревший отчёт | blocked-not-run | `--label ..._cross_forced` |
| `_edge_orientation_scalar` | 175 | устаревший отчёт | blocked-not-run | `--label ..._edge_orientation_scalar` |
| `_edge_orient_rbf6` | 175 | устаревший отчёт | blocked-not-run | `--label ..._edge_orient_rbf6` |
| `_edge_raw3` | 175 | устаревший отчёт | blocked-not-run | `--label ..._edge_raw3` |
| `_edge_rbf6` | 175 | устаревший отчёт | blocked-not-run | `--label ..._edge_rbf6` |
| `_hydrocore_depthq10` | 170 | устаревший отчёт | blocked-not-run | `--label ..._hydrocore_depthq10` |
| `_node_bilinear` | 175 | устаревший отчёт | blocked-not-run | `--label ..._node_bilinear` |
| `_pair_broadcast` | 175 | устаревший отчёт | blocked-not-run | `--label ..._pair_broadcast` |
| `_attnbypocket` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._attnbypocket` (без `SKIP_AUC`) |
| `_attnpool_pocketbias` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._attnpool_pocketbias` |
| `_ckpt30` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._ckpt30` |
| `_lipid_class` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._lipid_class` |
| `_pocketonly` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._pocketonly` |
| `_rim_ev28` | 175 | `SKIP_AUC=1` отложено | blocked-not-run | `--label ..._rim_ev28` |
| `_hid4` | 0 (нет `models/` каталога) | архитектурная ошибка конфига (`hiddim=4` не делится на `HEADS=8`) | blocked-missing-checkpoint | нужно решение пользователя — чинить конфиг и переобучать |
| `_lipid_descriptors` | 0 (нет `models/` каталога) | не проверено глубже (не `Failed:`) | blocked-missing-checkpoint | нужно решение пользователя — проверить, обучался ли вообще |

Все 19 команд — один и тот же шаблон
(`scripts/env.sh python3 analysis/full_label_report.py --label <label>
--seeds=0,1,2,3,4`), read-only относительно чекпойнтов (`full_label_report.py`
докстринг: «Reads model checkpoints and data/ only»), но каждая — это forward
pass над сохранёнными весами, не только чтение текста, поэтому не запускалась
без прямого разрешения пользователя.

**Чем посчитано (этот раздел).** `ls graphics/geometric_edge_mlp_protgeom_
family_neutral_normalized_bilinear_fusion_bilinear_norm*` (список 19 лейблов
линии, `_lcs*`-суффиксы исключены вручную по совпадению с §C выше); `awk`/`grep`
по каждому `<label>.md` (текст после заголовка `## AUC vs chemistry null
model...`) для трёхсторонней классификации (пусто / `SKIP_AUC=1` / `Failed:`);
`stat -c %y` для сравнения mtime `.md` с mtime `analysis/full_label_report.py`,
`analysis/checkpoint_scores.py`, `scripts/lib/generate_label_report.sh`; `find
models/<label> -iname '*.pt*'` (подсчёт файлов чекпойнтов) для каждого из 19
лейблов — `analysis/full_label_report.py` не запускался, чекпойнты не
загружались.

---

## descriptors-architecture lcs adaptation proposal, 2026-09-11

### Правило сопровождения

Снимок на 2026-09-11. Разбирается конкретный, ещё НЕ запущенный конфиг
`scripts/arg_files/descriptors_head_family_neutral_lipprop.md` (архитектура 2,
`--descriptors_head`, плоский MLP без графов/LM), который заменяет утёкший
`descriptors_no_extent_coarse_add_lipprop` (`files/four_families_audit.md` §3.2,
честный test BA 0.826 на LBP_BPI_CETP против 0.549 на остальных шести). Ничего
не запускалось и не пересчитывалось — это разбор кода
(`training/read_configuration.py`, `dataloader/pair_descriptors.py`,
`dataloader/sampler.py`, `dataloader/Dataloader.py`) и уже существующих находок
(`files/four_families_audit.md`, `files/lipid_coldsplit_architecture_direction.md`).
**Важная оговорка по переносимости**: почти все lcs-числа ниже измерены на
`geometric_edge_mlp_*` (граф белка + ESM3 + bilinear-fusion), а не на
`descriptors_head` — `descriptors_head` под `--lipid_coldsplit` не запускался ни
разу. Где число берётся с другой архитектуры, это сказано явно; сам факт
"протестировано на другой архитектуре" не делает вывод неприменимым (риски
токенов/сэмплинга не зависят от того, что стоит вокруг них), но делает его
непроверенным здесь.

### 1. Что в текущем dcs-конфиге сделано именно против ПРОТЕИНОВОЙ утечки

1. **`--descriptor_names=...,pocket_volume_per_sasa,pocket_elongation,
   pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,
   hydropathy_rim`** — это дословно `POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES`
   (`dataloader/protein_graph_builder.py:56-59`), 7 признаков с индивидуальным
   η² по белковой семье ≈0.28–0.32 (около пола шума). Осознанно НЕ включены 6
   худших по идентичности карманных признаков, задокументированных в том же
   файле (`:43-58`): `pocket_sasa_share`=0.85, `hydropathy_core`=0.77,
   `pocket_residue_share`=0.71, `pocket_extent`=0.62, `ev14_q50`=0.59,
   `depth_q10`=0.55. Почему это важно предметно, не абстрактно: на близком
   8-признаковом «сыром» наборе (`geometric_edge_mlp_protgeom8`, включает 3 из
   этих 6) прямой замер (`feature_identity_check.py`,
   `files/four_families_audit.md` §4.2) дал joint η²=0.439 против пола 0.235 —
   статистически неотличимо от отпечатка семьи (NN same-family rate 0.429 при
   p=0.002).
2. **Использование `--descriptor_names` (NamedDescriptorHead), а не
   `--pocket_descriptors`/`--pocket_descriptor_names`** для тех же самых
   карманных признаков. `DESCRIPTOR_CATALOG`-путь ВСЕГДА стандартизуется
   загрузчиком по train-only статистике; `--pocket_descriptors`' нормировочные
   буферы заполняются только под `--rnabang_frozen_node_adapter`, который нигде
   в проекте не выставлен. Т.е. выбор именно этого пути — это ещё и выбор
   «не кормить сеть ненормированным сырым каналом», где абсолютный масштаб
   карманов сам по себе мог бы отличать семьи.
3. **Исключение `occupancy` из набора токенов** (в `files/four_families_audit.md`
   §3.2/§3.4 это явно названо сознательным решением). `occupancy` — парный
   термин, зависящий от `coarse_extent`, а `coarse_extent` — это `pocket_extent`,
   забинованный по квантилям, посчитанным **только по белкам train**, заново
   для каждого исключённого семейства (`dataloader/Dataloader.py:994-1001`
   по цитате аудита). По факту это не химическая величина, а «где карман этого
   белка лежит относительно карманов ОСТАЛЬНЫХ (оставшихся) семей» —
   between-family фингерпринт, а не chemistry (`files/four_families_audit.md`
   §4.2, строки 391-408, там же и разворот знака between-/within-protein
   AUC для `pocket_extent`, 0.431 против 0.579).
4. **`--balanced_proteins`**: матчит негативы к позитивам 1:1 (точнее,
   `negatives_per_positive`:1) ВНУТРИ каждого отдельного белка, а не внутри
   семьи и не глобально. По докстрингу `sample_protein_balanced_negatives`
   (`dataloader/sampler.py:172-190`) это «additionally removes the per-protein
   prior a model could otherwise learn as "this protein is usually positive"» —
   защита от белкового шортката на уровне сэмплинга, отдельная от пп. 1-3
   (защита на уровне признаков).
5. **`--double_coldsplit`** (требует непустой `--excluded_groups`, иначе
   `validate()` кидает исключение — `training/read_configuration.py:1531`) —
   помимо выноса строк исключённого семейства из train, ДОПОЛНИТЕЛЬНО убирает
   из оценки те строки исключённого семейства, чей класс липида ОСТАЛСЯ в
   train (`training/read_configuration.py:992-999`: без этого шага
   per-lipid-class приор измеряется 0.498, с ним — ровно 0.500). Смысл именно
   для протеиновой оси: не даёт модели пройти тест на «незнакомое семейство»
   за счёт лукапа «этот класс липида я уже видел с другими белками» — это
   защита ЧЕСТНОСТИ протеинового теста, которая механически трогает липидную
   ось, но не является самостоятельной защитой от утечки идентичности липида
   (см. §2 ниже).

### 2. Есть ли в текущем dcs-конфиге защита от ЛИПИДНОЙ утечки

**Нет, за одним нюансом.** dcs никогда не выносит целый липидный класс из
train ради него самого — п.5 выше выносит классы только производно от того,
какое семейство исключено (`lipid_classes_for_holdout`, привязан к семье), и
только чтобы не дать протеиновому тесту утечь через липидный лукап. Это не то
же самое, что независимый по химии holdout `--lipid_coldsplit` делает
(`--lipid_coldsplit` берёт из именованных наборов, `sphingolipids`/`anionic`/
`choline`/`phosphorus_free`, не связанных с тем, какой белок исключён —
`dataloader/sampler.py:220-243`). Так что на вопрос «есть ли в dcs-конфиге
что-то, что тестирует обобщение на новую липидную химию» — ответ нет, и это
ожидаемо: под dcs такой оси просто не существует.

**Нюанс, который стоит зафиксировать явно.** Список
`--descriptor_names=chain,unsaturation,hbond,heavy,...` содержит 4 липидных
токена, и два из них — `hbond` и `heavy` — оказались, по независимому аудиту
на другой сессии (`analysis/lipid_descriptor_class_identity.py`, 283 вида
липидов, 34 головных класса, `files/lipid_coldsplit_architecture_direction.md`
§7f), одними из самых сильных отпечатков головного класса во всём каталоге:
`hbond` η²=0.9905, `heavy` η²=0.9187 (для сравнения, `chain`=0.4316,
`unsaturation`=0.3245 — тоже статистически значимые отпечатки, p=0.001, но
заметно слабее). Под dcs это инертно (липидные классы не выносятся, отпечаток
класса — не канал утечки на этом сплите). Но это означает, что нынешний dcs
config уже содержит два токена, которые стали бы проблемными именно под lcs,
и это никогда не проверялось в dcs-контексте, потому что там не было оси,
которая сделала бы это видимым.

### 3. Предложение по адаптации под `--lipid_coldsplit`

| # | Изменение | Статус | Почему |
|---|---|---|---|
| A | Убрать `--double_coldsplit` (+ implicit `--excluded_groups`), добавить `--lipid_coldsplit=<set>` | обязательное, механическое | `validate()` требует непустой `excluded_groups` для `double_coldsplit`/`mixed_coldsplit` (`training/read_configuration.py:1531`) и запрещает `lipid_coldsplit` вместе с `double_coldsplit`/`excluded_groups` (`:1479-1494`) — оси физически взаимоисключающие в коде, не вопрос выбора |
| B | Убрать `--balanced_proteins`, добавить `--balanced_lipid_classes` | **проверено на другой архитектуре, направление подтверждено частично** | Под lcs протеиновая ось не холодная — все 35 белков в train (`Dataloader.py:1454-1459`), значит `balanced_proteins` защищает ось, которой здесь нет, а ось, которая холодная (класс липида), не защищена ничем. `balanced_lipid_classes` — его точное зеркало (`training/read_configuration.py:804-810`: матчит по (семья, класс липида), приор класса 0.25–0.68 → 0.50–0.51) и **перекрывает `balanced_proteins`, если оба заданы** (`:809`) — так что это скорее необходимая замена, чем опция. На `geometric_edge_mlp` это был единственный из 4 испытанных рычагов, давший статистически значимый прирост (+0.0625 pooled test BA, `sphingolipids` +0.187/5.7σ, `anionic` +0.152/7.6σ — `lipid_coldsplit_architecture_direction.md` §7i). **Оговорка**: пересчёт против честной нуль-модели (§7j, те же строки) не подтвердил `anionic` (сеть 0.706 против химического нуля 0.745 — сеть хуже) и подтвердил `sphingolipids` (0.595 против 0.498/0.483) — то есть выигрыш реален, но не на всех наборах и не в той мере, что казалось до перепроверки. |
| C | НЕ добавлять `--adversarial_grl` | закрыто кодом, не вопрос выбора | `descriptors_head` собирает только `PairDescriptorHead`/`NamedDescriptorHead` + маленький классификатор — `protein1`/`lipid1`/`cross_attention1` не строятся вовсе (`training/read_configuration.py:542-557`), а `adversarial_grl` числится прямо в списке `unsupported` под `descriptors_head` и кидает `ValueError` при попытке включить оба (`:2323-2343`, буквально: «these options have nothing to attach to»). advprot содержательно атакует пред-cross-attention pooled-представление партнёра — под `descriptors_head` такого представления не существует физически. |
| D | Добавить `--loss_type=pairwise_rank --rank_within_protein` | **рассуждение перенесено с другой архитектуры, на `descriptors_head` не проверялось** | Работает на уровне лосса/сравнения логитов, не на pooled-представлении партнёра — ни `rank_within_protein`, ни `loss_type` не входят в список несовместимых с `descriptors_head` флагов (`:2326-2334`), значит комбинация синтаксически разрешена. На `geometric_edge_mlp` под lcs («`rankprot`») это дало ровно ту же качественную картину, что и advprot: pooled BA упала (0.6155→0.5803), внутрибелковый AUC вырос (0.480→0.556 пулом; `choline` +0.145/3.6σ) — потому что оба механизма убирают именно белковую маргиналь, на которой едет пулированное число под lcs (`lipid_coldsplit_architecture_direction.md` §7j/§7n). Это ортогонально C: там, где C закрыт архитектурно, D — рабочий заменитель того же диагноза («модель едет на маргинали, которую разрез оставил бесплатной»), а не догадка с нуля. |
| E | Заменить `hbond,heavy` в `--descriptor_names` на хвостовые токены `tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_length_asymmetry` (уже есть в `LIPID_DESCRIPTOR_NAMES`, `dataloader/pair_descriptors.py:51-65`), оставить `chain,unsaturation` | **рассуждение подкреплено измерением на другой архитектуре, на `descriptors_head` не проверялось** | §2 выше: `hbond`/`heavy` η²=0.99/0.92 по головному классу — почти чистые метки класса. Хвостовые токены измерены как наименее классоспецифичные во всём каталоге (η²=0.31–0.34, `dataloader/pair_descriptors.py:56-61`). Операционное подтверждение с другой архитектуры: внутрибелковый сигнал под lcs появился ровно на тех двух held-out наборах (`choline`, `phosphorus_free`), которые различаются внутри блока преимущественно по ацильной цепи (разброс хвоста 1.05/1.48 против разброса головы 0.16/0.52), и отсутствовал на тех двух (`anionic`, `sphingolipids`), что различаются по головной группе (разброс головы 0.85/1.03 против хвоста 0.56/0.68) — соответствие 4 из 4 (`lipid_coldsplit_architecture_direction.md` §7p). Для `descriptors_head` это даже проще перенести, чем для `geometric_edge_mlp`: там тот же диагноз потребовал бы отдельной архитектуры «голова/цепь раздельными ветками» (§7q, не реализовано), потому что липид там — монолитный MolFormer-эмбеддинг, который нечем декомпозировать. У `--descriptor_names` декомпозиция уже есть бесплатно — это просто вопрос того, какие имена перечислить. |
| F | Снять family-neutral ограничение на протеиновой стороне: заменить 7 имён на полный `protgeom8` (`pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim`) | **новая, непроверенная идея** — рассуждение с другой архитектуры и с другого сплита (double, не lipid) | §1 выше объясняло, зачем family-neutral нужен под dcs. Под lcs протеиновой отложенной оси нет вовсе, значит η²-по-семье — не канал утечки (`lipid_coldsplit_architecture_direction.md` §4, таблица: «нет: отложенных семейств нет»). Более того, два признака, выброшенных именно за семейность (`depth_q10`, `hydropathy_core`), — единственные два во всём наборе с измеренной устойчивой связью именно с ЛИПИДНЫМ свойством: `depth_q10` ↔ длина ацильной цепи (частная ρ −0.407 pooled, знак совпадает в двух семьях), `hydropathy_core` ↔ число головных классов (+0.403, совпадает в CRAL-TRIO/lipocalin) — то есть ровно то, что нужно для вопроса «новая химия». На `geometric_edge_mlp` полный набор дал test BA 0.601 против 0.5525 у family-neutral **на double coldsplit** (гэп 0.313 против 0.586), но контраст там смешан с отсутствием bilinear-стека — не однопеременный (§7 «7.1», `lipid_coldsplit_architecture_direction.md`). Под lcs и под `descriptors_head` не измерялось вовсе. |
| G | Не поднимать `--hiddim` выше 8 | подтверждено (на другой архитектуре) как «не делать» | Чистый однопеременный контраст hid8→hid64 на `geometric_edge_mlp`/lcs дал ΔBA=−0.0019 (0.08 combined SEM — ноль) при train sensitivity +0.06 и гэпе +0.06 — рост ёмкости купил только запоминание train, не обобщение (`lipid_coldsplit_architecture_direction.md` §3). Нет оснований ждать другого на `descriptors_head`, но и это не измерялось напрямую. |
| — | `--balanced_batches`, `--fast_attention`, `--pool_type="add"`, `--dropout`, `--weight_decay`, `--save_model_in_dynamics` | без изменений | Ни один не адресует конкретно протеиновую или липидную ось идентичности: `balanced_batches` — общий class-imbalance-сэмплер батчей (`training/new_train.py:279-294`, `ClassBalancedBatchSampler`), `fast_attention` — арифметически эквивалентный ускоренный путь внимания (`training/read_configuration.py:819-824`), `pool_type`/`dropout`/`weight_decay`/`save_model_in_dynamics` — общая архитектура/регуляризация/инфраструктура, не специфичны ни для какого сплита. |

### Новое vs проверенное — сводка

- **Проверено в проекте, но на `geometric_edge_mlp`, не на `descriptors_head`**:
  B (`balanced_lipid_classes`, с оговоркой по §7j), D (`rank_within_protein`/
  `pairwise_rank` = «rankprot»), G (не поднимать `hiddim`).
  Перенос на `descriptors_head` разумен (механизмы либо сэмплинговые, либо
  чисто лоссовые — не завязаны на архитектуру ветвей), но ни один реальный
  прогон `descriptors_head` под lcs не существует.
- **Механическое, не вопрос выбора**: A (флип флагов сплита).
- **Закрыто кодом, а не «пока не проверено»**: C (`adversarial_grl` под
  `descriptors_head` буквально кидает исключение).
- **Новое и непроверенное здесь, но обосновано существующими η²-аудитами**:
  E (замена `hbond,heavy` на хвостовые токены — но замена реализуема без
  архитектурных правок, в отличие от §7q на `geometric_edge_mlp`).
- **Новое и непроверенное вообще нигде**: F (снять family-neutral ограничение
  на протеиновой стороне под lcs — само по себе не измерялось ни на каком
  сплите/архитектуре в чистом виде, контраст на double coldsplit смешан с
  bilinear-fusion).
- **Не предлагается**: аналог `advprot`-механизма (GRL против ПРОТЕИНОВОЙ
  идентичности — не семьи, раз каждый белок остаётся в train под lcs) через
  новый hook на выходе `PairDescriptorHead`/`NamedDescriptorHead` технически
  возможен, но требует НОВОГО кода (нового флага и новой точки атаки в
  `architecture/pair_descriptor_head.py`/`Final_Layer`, поскольку
  `--adversarial_grl` жёстко привязан к `protein1`/`lipid1` pooled-тензорам,
  которых здесь нет) — это качественно другая работа, чем перестановка флагов
  A/B/D/E/F выше, и не сформулирована здесь как готовое предложение, только
  названа как единственный путь получить представленческий (не лоссовый)
  аналог advprot на этой архитектуре.

### Чем посчитано

Разбор кода (`training/read_configuration.py` — секции `descriptor_names`
:559-577, `descriptors_head` :558/2323-2343, `pair_descriptor_*` :411-535,
`balanced_lipid_classes`/`lipid_class_targets` :804-818, `double_coldsplit`/
`lipid_coldsplit` :982-1007/1479-1561, `rank_within_protein` :1314-1320,
`balanced_proteins`/`balanced_batches` :1026-1027; `dataloader/sampler.py`
:139-243 `split_and_sample_protein_balanced_interactions`/
`LIPID_COLDSPLIT_SETS`; `dataloader/pair_descriptors.py` :1-65/1077-1098;
`dataloader/protein_graph_builder.py` :43-59; `training/new_train.py`
:276-294). Цитаты чисел — `files/four_families_audit.md` §3.2/3.4/4.2/4.4 и
`files/lipid_coldsplit_architecture_direction.md` §0/2/3/4/7f/7i/7j/7n/7p/7q —
оба файла прочитаны целиком по релевантным разделам, не пересчитаны заново.
