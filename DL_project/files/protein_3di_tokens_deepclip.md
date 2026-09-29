# Токенизация кармана белка (аминокислоты + Foldseek 3Di) для DeepCLIP — `--deepclip_protein_tokens`

Снимок на 2026-09-29. Что установлено, чем сгенерировано, что изменено в коде. Обучение
НЕ запускалось, поэтому чисел качества здесь нет.

## 1. Установка Foldseek

Foldseek — это отдельный бинарник на C++, не Python-пакет. Ставится вне репозитория,
в git не попадает.

| что | значение |
|---|---|
| источник | официальная статическая сборка авторов: `https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz` |
| sha256 архива | `f886374e29ebbf03849cd9c4c8929be00904856dd271627d8c3043607e2af95a` |
| версия (`foldseek version`) | `463739e0014a1549a527de589102cde98f802f37` (коммит upstream) |
| куда распакован | `~/tools/foldseek/bin/foldseek` |
| требование к CPU | AVX2 (есть на этой машине; без AVX2 брать `foldseek-linux-sse2.tar.gz`) |

```bash
mkdir -p ~/tools && cd ~/tools
curl -sSL -o foldseek-linux-avx2.tar.gz https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz
sha256sum foldseek-linux-avx2.tar.gz      # сверить с таблицей
tar xzf foldseek-linux-avx2.tar.gz
~/tools/foldseek/bin/foldseek version     # 463739e0...
```

По ссылке `mmseqs.com` всегда лежит последняя сборка. Если хеш не совпадает, значит
версия другая, и 3Di-буквы могут отличаться. Тогда пересобрать CSV и сравнить с
закоммиченным.

## 2. Генерация `data/protein_3di.csv`

Скрипт — [preprocessing/build_foldseek_3di.py](../preprocessing/build_foldseek_3di.py).
Запускать в conda-окружении проекта:

```bash
conda activate Kalinin_project_LP
python3 preprocessing/build_foldseek_3di.py --foldseek ~/tools/foldseek/bin/foldseek
# 35 proteins -> data/protein_3di.csv (foldseek 463739e0...); 3Di letters used: ACDEFGHIKLMNPQRSTVWY
```

Что делает скрипт: `foldseek createdb` (`--chain-name-mode 0 --threads 1`) → `lndb` →
`convert2fasta` для аминокислотной и 3Di-баз. Для каждого белка результат сверяется
с графом.

- **Вход** — `data/graphs/<name>/pocketness.pdb`. Узлы `coarse_graph_nodes.csv` —
  ровно остатки этого файла. Файлы подкладываются во временную папку симлинками
  `<name>.pdb`, потому что Foldseek называет запись по имени файла.
- **Проверка** — аминокислотная строка Foldseek должна совпасть посимвольно с
  `residue_type` узлов (`RESIDUE_LETTERS`). При любом расхождении скрипт падает с
  именем белка, а не пишет сдвинутые буквы.
- **Выход** — одна строка на белок: `LTPProtein, residues, aa, three_di,
  foldseek_version`, по букве на узел графа в порядке узлов. 35 белков, 7843
  остатка, sha256 `09d43f05fe59e6af0ce8557adf51dd9ae389a6e25d7c233de41d5b32a414a4f4`.

**Найдено по дороге:** `data/esm3_input/<name>.pdb` устарел относительно графов (графы
пересобраны 2026-09-17, esm3_input — 2026-08-17). В нём меньше остатков, чем узлов:
GLTP 205/206, GM2A 162/193, HSDL2 273/275, LCN15 149/154. Поэтому вход — pocketness.pdb,
а не esm3_input. Это касается и `embedding_ESM3_v2` (`--use_esm3_v2_embeddings`),
который строится из esm3_input. Здесь это не исправлялось.

## 3. Токены

Модуль — [dataloader/protein_tokens.py](../dataloader/protein_tokens.py).

- **Токен = остаток кармана, в порядке цепи.** Остаток считается карманным так же, как в
  `ProteinGraphBuilder.protein_graph_tensors`: у любого атома боковой цепи флаг 1 в
  B-factor pocketness.pdb. Сопоставление с узлами идёт по (chain, resSeq, iCode), а не
  по позиции, поэтому спецслучай RBP4 (лишний атом N в конце файла) не нужен.
  Проверено: маска совпадает с маской загрузчика у всех 35 белков.
- **Алфавиты:** `aa` — 20 аминокислот, `3di` — 20 состояний 3Di. Можно одно из двух или
  `aa,3di`.
- **Разрыв цепи — канал, а не токен.** Флаг ставится, если остаток не сосед по цепи
  предыдущему карманному. Причина: карман в основном состоит из разрозненных остатков
  (медиана 33 остатка при 28 разрывах, максимум 107 у PITPNA). Отдельный gap-токен почти
  удвоил бы длину последовательности, и окно ширины 4–8 видело бы 2–4 остатка.
- **Ширина one-hot:** 20 × число алфавитов + 1 (канал разрыва), то есть 21 или 41.
- **Хранение:** целочисленные коды `[1, longest, 3]` на сэмпл (aa, 3di, break), паддинг
  -1, плюс `protein_token_count` `[1]`. `longest` — самый длинный карман среди белков
  таблицы, поэтому PyG и preassembled loader складывают сэмплы без изменений.

## 4. Как это входит в DeepCLIP

Код — [architecture/deepclip.py](../architecture/deepclip.py), метод `protein_summary`
и блок гейта.

1. Белковая башня той же формы, что липидная: Conv1d шириной `--deepclip_widths` (по
   `--deepclip_filters` на ширину, init `--deepclip_conv_init`, без bias) → ReLU →
   упакованный BiLSTM (`--deepclip_lstm`) → сумма направлений → среднее по остаткам
   кармана. Получается вектор `[batch, deepclip_lstm]`.
2. Этот вектор — вход существующего гейта, рядом с дескрипторами
   `--deepclip_protein_gate`, если они заданы. Гейт остаётся прежним: tanh,
   центрирование весов каналов по среднему, аддитивный bias, нулевая инициализация
   последнего слоя.
3. Поэтому в начале обучения модель **в точности** опубликованная DeepCLIP: логиты
   побитово равны модели без белка (это проверяется тестом). На первом шаге учится
   только последний слой гейта; со второго шага градиент доходит до башни.

Белок влияет только через взаимодействие с профилем липида: веса каналов на позицию и
сдвиг на белок. Отдельного белкового скора, который мог бы стать приором «на белок»,
нет.

Параметры при дефолтах DeepCLIP:

| конфиг | всего | башня | гейт |
|---|---|---|---|
| без белка | 1960 | — | — |
| `aa` или `3di` | 4137 | 1990 | 187 |
| `aa,3di` | 4737 | 2590 | 187 |

## 5. Флаг

```text
--deepclip --lipid_smiles_tokens --deepclip_protein_tokens=3di
```

- Требует `--deepclip`.
- Несовместим с `--deepclip_profile_weights`: пишет тот же вектор весов.
- Совместим с `--deepclip_protein_gate=...` (дескрипторы и башня подаются в гейт вместе)
  и с `--deepclip_gate_weight_decay`; валидация этого флага расширена на
  `deepclip_protein_tokens`.
- Для `3di` нужен `data/protein_3di.csv`. Для `aa` хватает графов.

Изменённые файлы:

- `training/read_configuration.py` — поле, парсер, валидация;
- `dataloader/Dataloader.py` — таблица токенов в `__init__`, поля сэмпла под `--deepclip`;
- `architecture/interaction_classification.py`, `training/forward_args.py` — проброс тензоров.

## 6. Тесты

`tests/test_protein_tokens.py`, 13 тестов:

- выбор кармана, флаг разрыва, iCode;
- проверки длины 3Di и отсутствующих остатков;
- паддинг таблицы и one-hot;
- флаг и валидация;
- старт = DeepCLIP побитово;
- независимость от длины паддинга;
- градиент в башню со второго шага;
- проброс в forward_args;
- preassembled loader совпадает с PyG.

```bash
LD_LIBRARY_PATH=$CONDA_PREFIX/lib python3 -m pytest tests/test_protein_tokens.py tests/test_deepclip.py
```

`LD_LIBRARY_PATH` нужен только при запуске python окружения без `conda activate`:
иначе rdkit не находит `GLIBCXX_3.4.31`.

Результаты:

- test_protein_tokens + test_deepclip + test_read_configuration +
  test_training_smoke_integration + test_pair_index_alignment + test_lipid_encoder:
  320 passed.
- Полный `tests/`: 616 passed, 10 failed. Все падения в модулях, которые не менялись:
  `test_balanced_batch_sampler` (1), `test_cluster_submitters` (3),
  `test_complete_lipid_candidate_sets` (6).

## 7. Оговорки

- Не обучалось. Ни одного arg-файла под флаг не создано.
- В режиме `--family_only` в семье 1–5 белков, и последовательность кармана однозначно
  называет белок. По сути это one-hot ID белка через гейт. Ожидать обобщения на новый
  белок оттуда нельзя; осмысленная проверка — многосемейный режим на
  `double_coldsplit`.
- Базовая DeepCLIP уже схлопывается в константу на ~10 позитивах
  ([deepclip_architecture_and_protein_conditioning.md](deepclip_architecture_and_protein_conditioning.md)
  §4). Белковый вход не решает проблему малых данных, он только даёт белку способ
  повлиять на профиль.
- `protein_summary` делает один `lengths.cpu()` на батч — одно чтение с устройства,
  которого на липидной стороне нет.
