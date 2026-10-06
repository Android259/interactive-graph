# Предсказание связывания белок-переносчик липидов (LTP) — липид

Модель решает бинарную задачу: связывает ли данный белок-переносчик липидов (LTP)
данный липид. Вход — пара (белок, липид), выход — два логита `[не связывает,
связывает]`. Главный вопрос проекта — обобщение на **новые липиды**: в тест уходят
липиды, которых модель не видела, а все белки остаются в обучении.

Что сейчас считается основным разрезом, метрикой и базовой конфигурацией:
[files/CURRENT_STATE.md](files/CURRENT_STATE.md).

## Данные

- **Таблица взаимодействий** — `data/Processed_Negative_Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv`
  (имя задано в `dataloader/dataset_source.py`): 10 920 строк, полная сетка 35 белков ×
  312 липидов, 658 позитивов. Семья белка — колонка `ProteinDomain`
  (CRAL-TRIO, START, GLTP, lipocalin, LBP_BPI_CETP, scp2, IP_trans, ML, OSBP).
  Источник позитивов: Titeca et al., 2023 —
  [files/reference/data_source.md](files/reference/data_source.md).
- **Белок**: структура и карман (`data/graphs/<белок>/`, `data/esm3_input/`), эмбеддинги
  ESM3 по остаткам (`data/embedding_ESM3*/`), дескрипторы кармана.
- **Липид**: SMILES (у части липидов — несколько кандидатов-изомеров), эмбеддинги
  MoLFormer (`data/lipid_SMILES_embedding_deterministic.*`), атомные графы
  (`data/lipid_graphs/`), сходство Tanimoto (`data/cache/Tanimoto_compact_*`).
- Подробный контракт файлов данных: [data/AGENTS.md](data/AGENTS.md).

## Схема пайплайна

```text
 исходные данные          предобработка (один раз)          кэши (один раз)
 ────────────────         ────────────────────────          ─────────────────
 таблица LTP×липид  ──►   preprocessing/*.py           ──►  data/cache/protein_graph_tensors.pt
 PDB белков               (эмбеддинги ESM3/MoLFormer,       data/cache/lipid_graph_tensors.pt
 SMILES липидов            графы, Tanimoto, кандидаты)      data/cache/lipid_SMILES_embedding_*.tensors.pt
                          data/build_*.py                   data/cache/pair_descriptor_cache_*.json
                                   │
                                   ▼
 обучение: training/new_train.py ── конфиг: arg_files/<семья>/<label>.md
   dataloader/Dataloader.py   разрез, сэмплинг негативов, сборка образцов
   architecture/*.py          энкодеры белка/липида, внимание, голова
   training/epoch_loop.py     эпохи, выбор чекпойнта по validation
   training/final_evaluation.py   тест → test_metrics/<family>/<label>/<набор>/*.txt
                                   │
                                   ▼
 таблица: results/tables/metrics_summary.csv  (одна строка на отчёт теста)
                                   │
                                   ▼
 анализ: analysis/*.py  → графики graphics/<family>/<label>/, разборы files/results/*.md
```

Кэши не обязательны: при их отсутствии загрузчик считает то же самое из исходных
файлов, только медленнее. Устаревший кэш (исходник изменился) отбрасывается
автоматически.

## Структура репозитория

| папка | что там |
|---|---|
| `training/` | точка входа `new_train.py`, разбор конфигурации, цикл обучения, тест |
| `architecture/` | модули модели (`interaction_classification.py` — верхний уровень) |
| `dataloader/` | `PLIDataset`: разрезы, сэмплинг, признаки, сборка образцов |
| `data/` | входные данные и скрипты построения кэшей |
| `preprocessing/` | офлайн-подготовка: эмбеддинги, графы, Tanimoto, проверки |
| `analysis/` | сборка таблицы метрик, графики; `baselines/` (Kron-RLS, GBM), `probes/` (разовые исследования), `tanimoto_groups/` |
| `arg_files/` | конфигурации запусков по семействам — [arg_files/README.md](arg_files/README.md) |
| `scripts/` | запуск локально и на кластерах — [scripts/README.md](scripts/README.md) |
| `tests/` | CPU-тесты (`pytest`) |
| `files/` | документы: справочники, результаты, предложения, статья — [files/INDEX.md](files/INDEX.md) |
| `results/tables/` | сводные таблицы метрик |
| `external/` | вендоренные внешние модели (MoLFormer, ProteinMPNN, RNA-BAnG) |

Генерируемые выходы (не исходники): `run/`, `test_metrics/`, `models/`,
`script_logs/`, `graphics/`, `testmode_outputs/`, `results/`.

У каждой папки с кодом есть `AGENTS.md` с подробным контрактом модуля.

## Окружение

Окружение conda описано в `scripts/cluster/cluster_env.yml` (Python, PyTorch с CUDA,
PyTorch Geometric, RDKit, pandas):

```bash
conda env create -f scripts/cluster/cluster_env.yml     # окружение Kalinin_project_LP
conda activate Kalinin_project_LP
```

На кластере без conda то же ставит `scripts/cluster/install_cluster_env.sh`.
Модели для пересчёта эмбеддингов (ESM3, MoLFormer) нужны только для предобработки —
[preprocessing/EXTERNAL_TOOLS.md](preprocessing/EXTERNAL_TOOLS.md).

## Первый запуск

Короткая проверка на CPU: одна эпоха, маленькая модель, всё пишется в
`testmode_outputs/`, настоящие таблицы не трогаются.

```bash
bash scripts/tools/test_run.sh test            # конфиг arg_files/smoke/test.md
```

Любая конфигурация, одна группа и один сид:

```bash
bash scripts/tools/test_run.sh ge_s15_prothid32_hid64_noreg START 0
```

Полная сетка (все отложенные наборы × 5 сидов), локально или на кластере:

```bash
bash scripts/run_local.sh ge_s15_prothid32_hid64_noreg
bash scripts/run_kraken.sh --graphics --summarize ge_s15_prothid32_hid64_noreg
```

Тесты:

```bash
python3 -m pytest tests/
```

## Где результаты и как читать таблицу

| путь | что |
|---|---|
| `script_logs/<family>/<label>*/<набор>/*.log` | лог прогона: эпохи (`valid epoch balanced_accuracy: …`), итоговый тест |
| `run/<family>/<label>/<набор>/train*/` | кривые TensorBoard (`epoch/train …`, `epoch/valid …`) |
| `test_metrics/<family>/<label>/<набор>/test_metrics_*.txt` | отчёт теста: конфигурация, сводка обучения, метрики, таблица по белкам |
| `results/tables/metrics_summary.csv` | все отчёты теста одной таблицей |

`<family>` — подпапка `arg_files/`, в которой лежит конфигурация (`geometric_edge`, `mlp`, …).
Метки без arg-файла попадают в `unsorted`. Правило в одном месте: `training/results_layout.py`.
`<набор>` — что отложено: `groups_species15`, `groups_PC`, `groups_START`, `random`, …

В `results/tables/metrics_summary.csv` одна строка — один прогон (label × набор × сид).
Ключевые колонки:

| колонка | что |
|---|---|
| `label`, `exclusion_set`, `seed` | какая конфигурация, что отложено, какой сид |
| `balanced_accuracy`, `sensitivity`, `specificity`, `F1`, `AUC` | **тестовые** метрики выбранного чекпойнта |
| `AUC_within_protein`, `AUC_within_protein_proteins` | AUC внутри каждого белка и по скольким белкам усреднено |
| `checkpoint_epoch`, `checkpoint_valid_balanced_accuracy` | какая эпоха выбрана и её validation |
| `number_of_parameters` | число обучаемых параметров |
| остальные | все флаги конфигурации, по колонке на флаг |

Как сравнивать: по тестовым метрикам в каждой отложенной группе, усредняя по сидам.
Нуль-модель на липидных разрезах — balanced accuracy 0.500. Validation служит только
для выбора чекпойнта.
