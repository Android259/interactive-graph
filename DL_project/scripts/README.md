# Скрипты запуска (`scripts/`)

Подробный контракт для сопровождения: [AGENTS.md](AGENTS.md). Здесь только «что
запускать, чтобы получить что».

Все команды запускаются из корня проекта. Конфигурация задаётся **голым именем**
файла из [arg_files/](../arg_files/) (без пути и `.md`); словарь сокращений в именах —
[arg_files/README.md](../arg_files/README.md).

## Что запускать

| задача | команда |
|---|---|
| один короткий прогон на этой машине (проверка, что всё работает) | `bash scripts/tools/test_run.sh test` |
| один прогон заданной конфигурации, одна группа, один сид | `bash scripts/tools/test_run.sh <label> <группа> <сид>` |
| сетка (все группы × сиды) на этой машине | `bash scripts/run_local.sh <label> [<label> ...]` |
| сетка на кластере Bigfoot / Kraken (GPU) / Kraken (CPU) | `bash scripts/run_bigfoot.sh <label>` / `run_kraken.sh` / `run_kraken_cpu.sh` |
| то же + графики и сводка по окончании | `bash scripts/run_kraken.sh --graphics --summarize <label>` |
| только часть групп или сидов | `--groups=START,GLTP`, `--no_groups=GLTP`, `--seeds=0,1,2` |
| следить за прогонами, забрать результаты, обновить таблицу | `bash scripts/wait_and_sync.sh` (кластеры), `bash scripts/wait_and_sync_local.sh` (локально) |
| остановить прогоны | `bash scripts/kill.sh <label>` (везде) или `--bigfoot` / `--kraken` / `--local` |
| сколько параметров у конфигурации (без обучения) | `bash scripts/tools/parameters.sh <label>` |
| графики по одной метке | `bash scripts/generate_config_graphics.sh <label>` |
| Kron-RLS / GBM baseline по метке | `python3 scripts/run_cron.py ...` / `python3 scripts/run_gbm.py ...` |

Все значения, которые обычно меняют (список групп, сиды по умолчанию, лимиты времени,
кластерные очереди), собраны в [settings.sh](settings.sh).

## Что где лежит

| папка | что внутри |
|---|---|
| `launch/` | общая реализация сетки для всех кластеров (`run_cluster.sh`, `submit_grid.sh`) и запуск одной задачи на узле |
| `lib/` | подключаемые библиотеки (`source`), сами не запускаются |
| `cluster/` | то, что выполняется на стороне кластера: очередь, cron-досылка, проверка окружения, `cluster_env.yml` |
| `tools/` | разовые команды: синхронизация, тестовый прогон, подсчёт параметров, профилирование |
| `submit/` | действующие нестандартные сабмиттеры (двухэтапный `structural_pretrain`) |

## Куда пишутся результаты

| путь | что |
|---|---|
| `script_logs/<family>/<label>_seeds*/<группа>/*.log` | лог каждой задачи (эпохи, итоговый тест) |
| `run/<family>/<label>/<набор>/train*/` | TensorBoard-кривые |
| `test_metrics/<family>/<label>/<набор>/test_metrics_*.txt` | отчёт теста: конфигурация, сводка обучения, метрики, таблица по белкам |
| `models/<family>/<label>/<набор>/seed<N>.pt` | веса (при `--save_model`) |
| `results/tables/metrics_summary.csv` | одна строка на каждый отчёт теста; пополняется автоматически |
| `graphics/<family>/<label>/` | графики и сводка `<label>.md` (при `--graphics --summarize`) |

`<family>` — подпапка `arg_files/`, в которой лежит конфигурация (`geometric_edge`, `mlp`, …).
Метки без arg-файла попадают в `unsorted`. Правило в одном месте: `training/results_layout.py`.
`<набор>` — имя отложенного набора: `groups_START`, `groups_species15`, `random`, …
Запуск с `--testmode` пишет всё это в `testmode_outputs/`, а настоящие таблицы не трогает.
