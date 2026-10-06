# Конфигурации запусков (`arg_files/`)

Один файл = одна конфигурация. Имя файла без `.md` — это **label** запуска: под ним
лежат `run/<family>/<label>/`, `test_metrics/<family>/<label>/`, `models/<family>/<label>/` и строки
`results/tables/metrics_summary.csv`. Поэтому переименование файла создаёт новую
конфигурацию, а не правит старую.

Строки, начинающиеся с `--`, передаются в `training/new_train.py` как флаги
(разбор: `training/read_configuration.py`). Остальные строки — комментарии.
Строка с отступом сразу после `--flag=...` продолжает длинное значение
(`scripts/lib/args_file_lib.sh`).

## Раскладка

Та же подпапка — уровень во всех папках результатов: `run/<семейство>/<label>/`,
`test_metrics/…`, `models/…`, `script_logs/…`, `graphics/…`. Перенос конфигурации в другую
подпапку меняет, куда пишутся её новые результаты; старые переносятся
`python3 scripts/tools/migrate_results_to_families.py --apply`.

| подпапка | что внутри | основные флаги |
|---|---|---|
| `geometric_edge/` | `geometric_edge_*`, `ge_*`: белковый граф с геометрией рёбер + bilinear fusion | `--protein_edge_mlp` / `--protein_edge_attention`, `--bilinear_fusion` |
| `mlp/` | `mlp_*`: MLP по каталогу дескрипторов, без графов и эмбеддингов | `--pair_descriptors --descriptor_mlp --descriptor_names=...` |
| `descriptors/` | `descriptors_*`, `dh_*`, `GBdescriptors_*`: дескрипторные головы | `--descriptors_head`, `--pair_descriptors` |
| `deepclip/` | `deepclip_*`: CNN+LSTM по токенам SMILES липида | `--deepclip --lipid_smiles_tokens` |
| `thematical/` | `thematical_*`: раздельные геометрический/химический пути | `--thematical_paths` |
| `structural_pretrain/` | предобучение белкового энкодера | `--structural_pretrain` |
| `bbp/` | исходная attention-архитектура (GAT + cross-attention) | `--balanced_batches --balanced_proteins` |
| `archive/` | июльские переборы гиперпараметров первой модели (lr, wd, dropout, h16/h32, `no_post_sa`, `nps3mlp`, …) | — |
| `smoke/` | `test.md`, `_smoketest_2paths.md`: служебные конфиги для проверки | `--testmode`, `--ep=1` |

Скрипты запуска принимают **голое имя** (`ge_s15_prothid32_hid64_noreg`) и сами
находят файл в подпапке. Имена уникальны по всему дереву: если одно имя окажется в двух
подпапках, запуск остановится с ошибкой.

## Словарь сокращений в именах

Имена собраны из кусков, разделённых `_`. Значение куска сверено с флагами внутри
файлов. Если кусок не найден ниже, смотрите сам файл: в нём есть флаги, а часто и
комментарий с обоснованием.

### Разрез данных (что уходит в valid/test)

| кусок | флаг | смысл |
|---|---|---|
| *(нет)* | `--excluded_groups=<семья>` (ставит лаунчер) | отложена одна белковая семья |
| `cs` | `--cold_split` | белковый колдсплит (старый) |
| `pcs` | — | то же, «protein cold split», в старых именах |
| `dcs` | `--double_coldsplit` | двусторонний: отложены и белки, и химия |
| `lcs` | `--lipid_coldsplit` | отложен химический набор липидов, все белки в train |
| `mcs` | `--mixed_coldsplit` | смешанный колдсплит |
| `s15`, `species15` | `--lipid_species_coldsplit=0.15` | отложено 15% конкретных видов липидов (по сиду) |
| `sub`, `subclass` | `--lipid_subclass=...` | отложен подкласс липидов из статьи (PC, PA, …) |
| `iso56` … `iso85` | `--lipid_isolation=0.56` … | изолированный по Tanimoto блок липидов |
| `rand` | `--random_split` (метка лаунчера) | случайный сплит строк, ничего не отложено |

### Сэмплинг и баланс

| кусок | флаг |
|---|---|
| `bbp` | `--balanced_batches --balanced_proteins` |
| `balanced_lipid_classes` | `--balanced_lipid_classes` |
| `lipprop` | `--lipid_propensity_weight` |
| `mbw` / `nomb` | `--marginal_balance_weight` включён / выключен |
| `hnm` | `--hard_negative_mining` |
| `rotneg` | `--rotate_train_negatives` |
| `npp5`, `npp6` | `--negatives_per_positive=5` / `6` |
| `frstcand` | `--lipid_first_fragment_only` (первый кандидат-изомер) |
| `dro` | `--group_dro` |

### Архитектура

| кусок | флаг |
|---|---|
| `fa` | `--fast_attention` |
| `nps` | `--protein_disable_post_sa_mlp --lipid_disable_post_sa_mlp` (no post-SA MLP) |
| `nps3mlp`, `3mlp` | `nps` + `--third_layers_in_mlps` |
| `gm` / `add` / `ap`, `attnpool` | `--pool_type="gem"` / `"add"` / `--attention_pooling` |
| `swe` | `--swe_pooling` |
| `bilinear_fusion`, `bilinear_norm` | `--bilinear_fusion`, `--bilinear_pooled_norm` |
| `edge_mlp`, `edge_attention` | `--protein_edge_mlp`, `--protein_edge_attention` |
| `rbf6`, `rbf32` | `--protein_edge_rbf_count=6` / `32` |
| `gt` | `--geometric_transformer` |
| `bng` | RNA-BAnG-эмбеддинги белка (`--rnabang_*`) |
| `esmif1` | `--esmif1_replace_esm3` |
| `esm3` | эмбеддинги ESM3 остаются включены (без `--no_protein_embeddings`) |
| `doubleattn` | `--double_attention` |
| `3rd_head` | `--pair_descriptors --pocket_descriptors` поверх attention-модели (третий вход головы) |
| `ffngate` | `--sparsity_gate_ffn` (структурная разреженность) |

### Размеры и регуляризация

| кусок | флаг |
|---|---|
| `hidN` | `--hiddim=N` |
| `prothidN`, `liphidN` | `--protein_hiddim=N`, `--lipid_hiddim=N` |
| `plmN` | `--plm_compression_dim=N` |
| `mN` | `--m=N` |
| `dptN` | `--dropout=0.N` (`dpt01` = 0.1, `dpt0` = 0) |
| `wd001`, `wd0001`, `wd0` | `--weight_decay=0.01` / `0.001` / `0` |
| `nwd` | без `--weight_decay` (то есть значение по умолчанию) |
| `noreg` | `--dropout=0.0` и почти нулевой `--weight_decay` |
| `lre-5` | `--lr=1e-5` |
| `epN` | `--ep=N` |
| `batchN` | `--batch=N` |
| `ckpt30` | `--checkpoint_window=30` |
| `aucsel` | `--checkpoint_selection_metric=auc` |

### Функция потерь и адверсарии

| кусок | флаг |
|---|---|
| `GRL`, `grl`, `adv` | `--adversarial_grl` |
| `advprot` | `--adversarial_grl --no_adv_lipid` (адверсарий только на белковой стороне) |
| `dp` | `--adv_deep` |
| `rmpft` | `--adv_lambda_ramp_by_fit` |
| `dann` | `--dann_family` |
| `chemadv` | `--chem_adversary` |
| `puNNN` | `--pu_loss --pu_unlabeled_positive_fraction=0.NNN` (`pu005` = 0.05) |
| `softpluscap3` | `--pu_loss_cap=3` |
| `rank`, `rankprot` | `--loss_type=pairwise_rank`, `rankprot` = `+ --rank_within_protein` |

### Наборы дескрипторов

Числа в именах наборов — это сколько дескрипторов в наборе. Точный список задан флагом
`--protein_descriptors=` / `--descriptor_names=` внутри файла, а описание каждого
дескриптора — в `files/reference/descriptor_catalog.md`.

| кусок | смысл |
|---|---|
| `protgeom`, `protgeom8` | геометрия кармана (объём/SASA, вытянутость, сплюснутость, …) |
| `protbind6`, `pb6` | базовый набор + 6 белковых дескрипторов (`ev28_q10`, `aromatic_share_rim`, `depth_q10`, `hydropathy_core`, `ev14_q10`, `hydropathy_mean`) |
| `protunion14` | объединение двух предыдущих наборов: 14 белковых дескрипторов |
| `pocketchem4`, `lipcron4` | 4 химических дескриптора кармана, 4 липидных дескриптора из Kron-RLS-отбора |
| `family_neutral`, `normalized` | набор без дескрипторов, выдающих белковую семью, нормированный по train |
| `coarse` | дескрипторы на огрублённом графе остатков |
| `lambdasqrt` | формы кармана через `√λ` вместо percentile span |
| `lipvol` | экспериментальный объём липида |
| `all70`, `dNN` | все 70 дескрипторов / первые NN по рангу |
| `keep5`, `all6`, `pair3`, `pocket3` | 5 отобранных по абляции; `+ 3 парных + 3 карманных`; только 3 парных / 3 карманных |
| `drop_<имя>` | абляция: этот дескриптор убран |
| `GB` | `--good_descriptors` / `--bad_descriptors` |
| `rim`, `core` | дескриптор посчитан на краю / в ядре кармана |
| `ev14`, `ev28`, `ev56`, `q10`, `q50` | окрестности 14/28/56 Å и квантили 10%/50% (имена дескрипторов) |

### DeepCLIP

| кусок | флаг |
|---|---|
| `fN` | `--deepclip_filters=N` |
| `normal`, `const` | `--deepclip_conv_init` |
| `mean`, `sum` | `--deepclip_readout` |
| `cral_trio`, `gltp`, `start` | `--family_only=<семья>` |
| `protein_gate` | `--deepclip_protein_gate=...` |
| `gatewd`, `smallgate` | `--deepclip_gate_weight_decay`, `--deepclip_gate_hidden=3` |
| `warm` | контроль без белкового гейта (только липид), пара к `*_protein_gate` |
| `pa`, `pg`, `sugar_phospho` | `--lipid_subclass=PA` / `PG` / … |

### Служебное

| кусок | флаг |
|---|---|
| `smd` | `--save_model_in_dynamics` |
| `cs` в конце (`bf_*_cs`) | `--cold_split` |
