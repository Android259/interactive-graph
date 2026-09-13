# Пересмотр "лучшего lcs-кандидата" для geometric_edge: advprot vs liphid32 vs остальные

## Правило сопровождения

Снимок на 2026-09-12. Числа взяты из `metrics_summary.csv` (через новый скрипт
`analysis/lcs_geometric_edge_candidate_ranking.py`, read-only), из уже
сгенерированных `graphics/<label>/<label>.md` (null-model секции, часть которых
почищена сегодня фиксом `analysis/null_model.py`/`analysis/interaction_increment.py`
для `--lipid_coldsplit`), и из `training/run_metrics.py` (точные определения
`collapse_fraction`/`converged`). Ничего не обучалось, ни один чекпойнт не
загружался и не пересчитывался; `generate_label_report.sh`/`full_label_report.py`
не запускались в этой сессии.

## 0. Итог

| Вопрос | Ответ | Раздел |
|---|---|---|
| `advprot` — это "текущий лучший lcs-кандидат", как написано в нескольких `files/*.md`? | Формулировка устарела и вводит в заблуждение — правильнее "лучший по одной оси, худший по другой, и не единственный кандидат в своей категории". На честной метрике проекта (`AUC_within_protein`) `advprot`-семейство обгоняет `liphid32` именно на единственном наборе с надёжным сигналом (`choline`); но `advprot` при этом ощутимо менее стабилен при обучении (`collapse_fraction` 0.27 против 0.005 у `liphid32`). | 3, 6, 7 |
| Прав ли пользователь, что `liphid32` лучше `advprot`? | И да, и нет — зависит от оси. По train-valid GAP и по `collapse_fraction` (стабильность) — да, заметно лучше. По `AUC_within_protein`/`_pairs` (главная метрика проекта по зафиксированному правилу) — нет: на двух надёжных блоках (`anionic` n≈12-17 белков, `choline` n≈9-15) `liphid32` даёт 0.464/0.352 (на уровне случайного или ХУЖЕ него), `advprot`-семейство — 0.47-0.55/0.53-0.67 (`choline` заметно выше случайного). | 3, 7 |
| Есть ли конфиг лучше обоих? | `..._lcs_esm3_advprot` (тот же adversarial-механизм, БЕЗ `--balanced_lipid_classes`) даёt самый высокий `AUC_within_protein_pairs` на обоих надёжных блоках (anionic 0.548, choline 0.672, на 16.4/14.8 белках — больше, чем у любого другого конфига) и заметно меньший коллапс на `phosphorus_free` (0.075 против 0.54 у "официального" `advprot`), но платит более широким GAP (0.11-0.26 против 0.00-0.10). Не был назван "лучшим" ни в одном файле — вероятно, потому что появился раньше `--balanced_lipid_classes` и не пересравнивался после. | 3, 4, 7 |
| Что показывает increment над хим. нуль-моделью (эпoch 120, in-sample)? | Посчитан только для 5 из ~20 сравнимых лейблов (`advprot_protfull`×2, `advprot_protgeom8`×2, `rankprot`) — для `advprot` и `liphid32` САМИХ секция в `graphics/.../*.md` сегодня сгенерировалась ПУСТОЙ (заголовок есть, таблицы нет, ошибки тоже нет — не то же самое, что уже известный баг `ValueError`). Там, где число есть, increment_prot (внутрибелковый) везде мал (0.000-0.025), максимален на `sphingolipids` — то есть даже "рабочие" сиблинги advprot едва отличимы от химии внутри белка на строгой in-sample метрике. | 5 |
| Что с 4 вариантами `descriptors_head_family_neutral_lipprop_lcs`? | Все четыре ощутимо хуже стабильностью, чем geometric_edge-семейство: `rankprot` даёт коллапс 15% эпох (макс. 59%) и провал `AUC_within_protein_pairs` на `choline` не наблюдается — то есть `rankprot`/`tailtokens` чинят `choline` (0.61) там, где база коллапсирует НИЖЕ случайного (0.415), тот же паттерн, что у geometric_edge. `protgeom8` не даёт устойчивого выигрыша ни на одной честной метрике. | 9 |
| Где в `files/*.md` `advprot` назван "текущим лучшим" и это надо пометить? | `geometric_edge_descriptors_baseline_selection_results.md` (3 места), `lcs_descriptors_and_protgeom8_baseline_results.md` (несколько мест), `reference_baselines_metrics_proposal.md` (§ "Третий пробел"). Добавлены короткие датированные пометки-указатели на этот файл, старые числа не тронуты. | 10 |

## 1. Что такое "утечка" и "нормализация" здесь на самом деле

Вопрос был: почему нужно требовать "тот же набор признаков и способ нормализации"
для честного сравнения — и это не про `--protein_descriptors` vs `--pocket_descriptors`
(оба train-only, см. предыдущее расследование в задании).

Ответ найден в `files/lipid_coldsplit_architecture_direction.md` §4 и §7f, и он про
ДВЕ разные вещи, которые обе называют "утечкой", но с разных сторон:

1. **Белковая сторона, под lcs — НЕ утечка.** `Dataloader.py:1454-1459`: под
   `--lipid_coldsplit` откладывается только химия, все 35 белков остаются в train.
   Значит η²-по-СЕМЬЕ (критерий, которым отобран family-neutral-7) тут не защищает
   ни от какой реально отложенной оси — белковую ось никто не выносит. Это объясняет,
   почему в §7.1 подмена family-neutral-7 на protgeom8 (более "утекающий" по семье
   набор из 8 дескрипторов) не изменила результат: искать здесь нечего.
2. **Липидная сторона — вот где утечка реальна.** §7f: аудит всех 13 именованных
   липидных дескрипторов (`hbond`, `tpsa`, `heavy`, `chain`, ...) против оси "класс
   головной группы" (34 класса) даёт η² от 0.29 до 0.99 — то есть каждый из них почти
   полностью предсказывает класс липида. Позже (`descriptors_baseline_leak_confirmed.md`,
   раздел про MolFormer) то же самое измерено и для самого векторного представления
   липида: усреднённый по токенам MolFormer-эмбеддинг имеет η²=0.752 против класса и
   nearest-neighbour-same-class rate 93.3% — практически ЯВЛЯЕТСЯ отпечатком класса,
   качественно как ESM3 являлся отпечатком identity белка на белковой стороне.

**Следствие для того, какие конфиги вообще можно класть в одну таблицу.** Все
кандидаты, которые здесь сравниваются (`advprot`, `liphid32/64`, `rankprot`,
`heads2/4`, `lam025/05/2`, `cross_forced`, `node_bilinear`, обычный `baseline`) —
используют липидную ветку в её исходном виде: `torch.nn.Linear(768, hiddim)` над
MolFormer-эмбеддингом, БЕЗ `--lipid_descriptors`/`--lipid_graph_isomers`. Значит риск
утечки класса через липидную сторону у них у ВСЕХ ОДИНАКОВЫЙ (тот же MolFormer,
та же проекция) — это не ось, по которой они отличаются друг от друга, и не мешает
их сравнивать между собой. Два кандидата, где липидная утечка реально варьируется
(`lipdesc` — явные дескрипторы класса; `lipgraph` — химический граф), уже были
измерены и закрыты как хуже базы (`lipid_coldsplit_architecture_direction.md` §7k) —
они не переоцениваются здесь заново.

**Ось, которая реально варьируется между сравниваемыми конфигами и требует
разделения** — набор `--protein_descriptors=`:

| набор | входит в | строка (из `metrics_summary.csv`) |
|---|---|---|
| family-neutral-7 | `advprot`, `liphid32/64`, `rankprot`, `heads2/4`, `lam*`, `cross_forced`, `node_bilinear`, `headchain`, `rankprot_advprot`, `lipdesc`, `lipgraph`, обычный baseline, `esm3`, `attention` | `pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim` |
| protgeom8 (8 полей, включая `depth_q10`/`hydropathy_core`) | `advprot_protgeom8` (× esm3/no-esm3), `esm3_protgeom8` | `pocket_extent,pocket_elongation,pocket_flatness,depth_q10,buriedness_q50,aromatic_share,hydropathy_core,hydropathy_rim` |
| protfull (15 полей) | `advprot_protfull` (× esm3/no-esm3) | `pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim` |

Плюс `geometric_edge_mlp_protgeom_full_lcs` меняет ОДНОВРЕМЕННО набор дескрипторов
(protfull), esm3 (снят) и балансировку (`--balanced_proteins` вместо
`--balanced_lipid_classes`), И идёт с `bilinear_pooled_norm=0` — три конфаунда плюс
условие (b) не выполнено. Уже разобран и признан неинформативным в
`files/geometric_edge_descriptors_baseline_selection_results.md` §4 (шесть коллапс-
прогонов из 20); здесь не пересчитывается, только подтверждается его исключение.

**Вывод: 22 лейбла (family-neutral-7 + `bilinear_fusion=1` + `bilinear_pooled_norm=1`)
образуют одну честную группу сравнения "одинаковый вход/нормализация".** Именно её
и сравнивает раздел 3-7 ниже. `protgeom8`/`protfull`-варианты `advprot` — вторая,
отдельная группа (раздел 8): они отвечают на вопрос "важен ли САМ набор дескрипторов",
не "какая надстройка над advprot лучше".

## 2. Полный список lcs-лейблов geometric_edge с `--bilinear_fusion`

`grep -l lipid_coldsplit scripts/arg_files/geometric_edge*.md` даёт 34 arg-файла; 29
из них имеют завершённые строки в `metrics_summary.csv` (20 строк = 4 набора × 5
сидов у каждого, кроме `rankprot` — 21, вероятно один повторный сид). Не запущены:
`advprot_lambda05`, `advprot_lambda2`, `advprot_batch64`, `advprot_ckpt` (0 строк —
похоже, дубли/переименования уже запущенных `lam05`/`lam2`).

## 3. Ось (a): честная тест-метрика, `AUC_within_protein` по набору

Колонка `AUC_within_protein_pairs` появилась в проекте только 2026-09-08 (после
запуска `liphid32/64`, `lipdesc`, `lipgraph`, `baseline`, `esm3`, `hid64`,
`attention`) — у этих лейблов её нет, есть только более грубый (и по построению
более шумный на малых блоках) `AUC_within_protein` — среднее ПО БЕЛКАМ, требует ≥6
строк и оба класса на белок. Ниже — обе версии не смешиваются молча: колонка
"n белков" показывает, на скольких блоках вообще считалось число, и это главное, на
что нужно смотреть перед тем как доверять цифре.

| конфиг | anionic (n≈12-17) | choline (n≈9-15) | phosphorus_free (n≈2-13) | sphingolipids (n≈2-3.4) |
|---|---|---|---|---|
| baseline (`esm3_balanced_lipid_classes`) | нет данных (лейбл старше метрики; доп. пересчёт офлайн дал 0.460, `lipid_coldsplit_architecture_direction.md` §7j) | нет данных (офлайн: 0.457) | нет данных | нет данных |
| `liphid32` | **0.464** (n=11.7) | **0.352** (n=12.0) | 0.692 (n=**1.75**, ненадёжно) | 0.793 (n=**2**, ненадёжно) |
| `liphid64` | 0.463 (n=11.0) | 0.504 (n=11.25) | 0.550 (n=1.5) | 0.635 (n=2) |
| `esm3_advprot` (БЕЗ balanced_lipid_classes) | **0.548** (n=16.4) | **0.672** (n=14.8) | 0.437 (n=12.2) | 0.498 (n=3.4) |
| `esm3_balanced_lipid_classes_advprot` ("официальный") | 0.485 (n=14.6) | 0.604 (n=14.0) | 0.618 (n=7.8) | 0.491 (n=2.0) |
| `balanced_lipid_classes_advprot` (без esm3) | 0.515 (n=14.6) | 0.601 (n=14.0) | 0.689 (n=7.8) | 0.426 (n=2.0) |
| `rankprot` (без advprot) | 0.492 (n=11.6) | 0.602 (n=11.0) | 0.636 (n=10.0) | 0.535 (n=2.0) |
| `rankprot_advprot` | 0.527 (n=14.6) | **0.641** (n=14.0) | 0.575 (n=7.8) | 0.444 (n=2.0) |
| heads2/heads4/lam025/lam05/lam2/cross_forced/node_bilinear/headchain (8 конфигов) | 0.470-0.537 | 0.537-0.628 | 0.543-0.647 | 0.414-0.625 | — все внутри разброса `advprot`, ни один не выигрывает >1-2 SEM (`analysis/lcs_geometric_edge_candidate_ranking.py`) |

**На двух надёжных блоках (anionic n≥11, choline n≥9-15) картина однозначная:**
`liphid32`/`liphid64` — на уровне случайного или НИЖЕ него на `choline` (0.352/0.504);
любой вариант `advprot`-семьи — заметно выше случайного на `choline` (0.60-0.67), на
`anionic` — у случайного или чуть выше (0.47-0.55). `phosphorus_free`/`sphingolipids`
у ВСЕХ конфигов посчитаны на 2-3.4 белковых блоках в среднем — про них нельзя делать
выводов вообще, независимо от того, какое число получилось (правило проекта:
`AUC_within_protein_proteins` рядом с числом, не одно число).

**`_esm3_advprot`** (тот же adversarial-механизм, но БЕЗ `--balanced_lipid_classes`)
даёт самые высокие числа на обоих надёжных блоках при этом на БОЛЬШЕМ числе белков
(16.4/14.8 против 14.6/14.0 у "официального" конфига) — не был отдельно
сопоставлен с `liphid32` ни в одном существующем файле.

## 4. Ось (b): GAP train-valid по набору

`mean_train_valid_gap`, усреднено по эпохам обучения и по 5 сидам:

| конфиг | anionic | choline | phosphorus_free | sphingolipids |
|---|---|---|---|---|
| baseline (`esm3_balanced_lipid_classes`) | 0.164 | **0.393** | 0.291 | 0.332 |
| `liphid32` | 0.161 | 0.384 | 0.306 | 0.272 |
| `liphid64` | 0.177 | 0.360 | 0.285 | 0.319 |
| `esm3_advprot` | 0.169 | 0.106 | 0.260 | 0.103 |
| `esm3_balanced_lipid_classes_advprot` | **0.097** | **0.001** | **0.088** | **0.069** |
| `rankprot` | 0.135 | 0.099 | 0.193 | 0.194 |
| `rankprot_advprot` | **0.062** | **-0.009** | **0.060** | **0.031** |

**Однозначный и чистый результат: любой вариант с `--adversarial_grl --no_adv_lipid`
(advprot-механизм) режет train-valid GAP в 2-10 раз относительно baseline/`liphid32`
на ВСЕХ четырёх наборах.** Это прямое, некосвенное свидетельство того, зачем
adversarial-голова вообще была предложена (§7l пункта 2
`lipid_coldsplit_architecture_direction.md`: "разворот градиента делает белковую
ветку индивидуально неинформативной") — она заметно снижает переобучение сети на
идентичности белка, а не просто топчется на месте. `liphid32`/`liphid64` эту причину
overfitting не трогают вообще и остаются на уровне baseline.

## 5. Ось (c): increment над химической нуль-моделью, epoch 120, in-sample

Раздел "AUC vs chemistry null model" сегодня почищен фиксом `null_model.py`/
`interaction_increment.py`, но реально непустой РОВНО для 5 из ~22 сравнимых
лейблов: `advprot_protfull` (esm3 и no-esm3), `advprot_protgeom8` (esm3 и no-esm3),
`rankprot`. **Для `advprot` и `liphid32` САМИХ, а также для `rankprot_advprot`,
секция сгенерировалась today пустой — заголовок есть, таблицы нет, и это НЕ уже
известная ошибка `ValueError: split reproduced here does not match` (для остальных
9 непроверенных лейблов — heads2/4, lam*, cross_forced, node_bilinear, headchain,
liphid64, baseline — именно эта ошибка и стоит). Разница между "пусто без ошибки" и
"явная ошибка" не диагностирована в этой сессии (не запускался `full_label_report.py`
заново, как и просил пользователь) — это отдельный технический пробел, а не число.**

Там, где число есть (`chem_prot`/`net_prot` — химия/сеть по логрегрессии внутри
белка, `increment_prot` = разница, **in-sample, верхняя граница, не held-out**):

| конфиг | anionic increment_prot | choline | phosphorus_free | sphingolipids |
|---|---|---|---|---|
| `rankprot` | -0.003 | +0.002 | +0.005 | **+0.014** |
| `advprot_protfull` (esm3) | +0.001 | +0.001 | +0.002 | **+0.025** |
| `advprot_protfull` (no esm3) | +0.001 | +0.001 | +0.001 | +0.017 |
| `advprot_protgeom8` (esm3) | -0.000 | +0.002 | -0.001 | +0.013 |
| `advprot_protgeom8` (no esm3) | +0.001 | +0.002 | +0.001 | +0.015 |

Все пять — крошечные (0.000-0.025), `sphingolipids` систематически выше остальных
(но это блок из 2-3 белков — см. §3). На этой строгой in-sample метрике даже
"рабочие" сиблинги `advprot` едва отличимы от химии внутри белка на трёх из четырёх
наборов. Прямых чисел для `advprot`/`liphid32` самих нет (см. выше) — сравнить их
между собой по этой оси сейчас нельзя, только по осям (a) и (b)/(d).

## 6. Ось (d): стабильность обучения — `collapse_fraction` / `converged`

Точное определение (`training/run_metrics.py:259-265`): `collapse_fraction` — доля
ЭПОХ обучения, на которых предсказания сети на VALID-сплите целиком одного класса
(`predicted_positive == 0` или `predicted_negative == 0`); `converged` — последние 3
valid BA отличаются друг от друга не больше чем на 0.01.

| конфиг | anionic | choline | phosphorus_free | sphingolipids |
|---|---|---|---|---|
| baseline | 0.010 | 0.005 | 0.007 | 0.008 |
| `liphid32` | 0.003 | 0.007 | 0.003 | 0.008 |
| `liphid64` | 0.005 | 0.003 | 0.002 | 0.005 |
| `esm3_advprot` | 0.040 | 0.342 | 0.075 | 0.037 |
| `esm3_balanced_lipid_classes_advprot` | 0.075 | **0.413** | **0.542** | 0.040 |
| `rankprot` | — (пул по лейблу 0.103) |||
| `rankprot_advprot` | 0.258 | 0.558 | 0.200 | 0.242 |

**Это ровно обратная картина оси (b).** `liphid32`/`liphid64`/baseline почти никогда
не коллапсируют во время обучения (≤0.01 доли эпох); ЛЮБОЙ вариант `advprot`
проводит 25-55% эпох обучения с полностью коллапсированными valid-предсказаниями на
`choline` и (для "официального" конфига) на `phosphorus_free`. По отдельным сидам
"официального" `advprot` на `phosphorus_free` — коллапс sensitivity к 0.00-0.065 у
ВСЕХ пяти сидов на тесте (пример: seed2 sens=0.000, spec=1.000). При этом
`AUC_within_protein_pairs` на этом же наборе у `advprot` равен 0.618 (§3) — то есть
ранжирование внутри белка остаётся содержательным даже там, где точечный классификатор
при пороге 0.5 коллапсирует в "всегда нет"; AUC порогонезависим, BA — нет (уже
установленное в проекте различие, `signal_state.md` §6.2).

## 7. Синтез: три оси расходятся, и это содержательный результат

| ось | что лучше | почему |
|---|---|---|
| (a) `AUC_within_protein[_pairs]`, `choline`/`anionic` (надёжные блоки) | `advprot`-семья, лучший — `esm3_advprot` (без balanced_lipid_classes) | `liphid32` на `choline` на уровне/ниже случайного (0.352-0.504); `advprot`-семья — 0.53-0.67 |
| (b) train-valid GAP | `advprot`-семья, лучший — `rankprot_advprot` (0.06/-0.01/0.06/0.03) | adversarial-механизм режет GAP в 2-10× относительно baseline/`liphid32`; `liphid32` не трогает эту причину переобучения вообще |
| (c) increment над химией, in-sample (частично измерено) | сиблинги `advprot` (protfull/protgeom8/rankprot) едва отличимы от нуля | нет прямых чисел для `advprot`/`liphid32` самих — пробел измерения, не вывод |
| (d) `collapse_fraction` (стабильность обучения) | `liphid32`/`liphid64`/baseline | `advprot`-семья проводит 25-55% эпох в коллапсе на `choline`/`phosphorus_free`, `rankprot_advprot` — тоже (20-56%) |

По зафиксированному правилу проекта (`project_lcs_primary_metric`: ранжировать по
`AUC_within_protein`, не по пулу) и по конвенции `reference_baselines_metrics_proposal.md`
§4 (GAP — диагностика, не заголовок; BA-коллапс на пороге 0.5 не то же самое, что
провал AUC) — **на метрике, которую проект называет главной, `advprot`-семья
обгоняет `liphid32`, а не наоборот.** Одновременно верно, что `liphid32` ведёт себя
кардинально стабильнее во время обучения, и это реальный, измеренный недостаток
`advprot`, а не придирка. Какой из двух критериев важнее для дальнейшей работы
(надёжная метрика ранжирования против предсказуемости обучения и лёгкости выбора
чекпойнта) — решение пользователя, оба свойства измерены выше по отдельности.

Дополнительно: `esm3_advprot` (без `--balanced_lipid_classes`) не хуже "официального"
`advprot` ни на одной оси, кроме GAP (0.11-0.26 против 0.00-0.10), и лучше него на
`choline`/`anionic` (оси a) и на `collapse_fraction` `phosphorus_free` (0.075 против
0.542) — стоит по крайней мере иметь в виду как альтернативный кандидат, не
рассмотренный ни в одном из существующих файлов как отдельный от "официального".

## 8. Другой набор протеиновых дескрипторов (protgeom8/protfull) поверх `advprot`

Уже разобрано в `files/lcs_descriptors_and_protgeom8_baseline_results.md` §3 — здесь
только сверка через новый скрипт, без противоречий: все 4 варианта (esm3/no-esm3 ×
protgeom8/protfull) дают `AUC_within_protein_pairs` в диапазоне 0.39-0.63, то есть
внутри разброса самого `advprot` на family-neutral-7 (0.43-0.69) — ни один набор
дескрипторов не выигрывает и не проигрывает достаточно, чтобы отличить эффект от
шума. Подтверждает вывод §7.1 `lipid_coldsplit_architecture_direction.md` "protgeom8
не помогает" на другом (более сильном, с advprot) baseline.

## 9. Четыре варианта `descriptors_head_family_neutral_lipprop_lcs` (architecture 2)

Отдельная архитектура (`--descriptors_head`, плоские дескрипторы, без графа и без
cross-attention) — не смешивается с geometric_edge выше, сравнивается только сама
с собой. `--protein_descriptors` тот же family-neutral-7 + 4 липидных (chain,
unsaturation, hbond, heavy) во всех четырёх (см. `files/descriptors_baseline_leak_confirmed.md`
про то, что architecture 2 в принципе не бьёт нуль-модель на double_coldsplit —
здесь другой сплит, lipid_coldsplit, проверяется заново).

### 9.1 Честная тест-метрика, `AUC_within_protein_pairs`

| конфиг | anionic (n=14.6) | choline (n=14.0) | phosphorus_free (n=7.8) | sphingolipids (n=2.0, ненадёжно) |
|---|---|---|---|---|
| база (`..._lcs`) | 0.556 | **0.415** (ниже случайного) | 0.533 | 0.255 |
| `_rankprot` | 0.486 | **0.615** | 0.467 | 0.448 |
| `_tailtokens` | 0.512 | **0.608** | 0.441 | 0.397 |
| `_protgeom8` | **0.577** | 0.447 | 0.465 | 0.541 |

**Тот же паттерн, что у geometric_edge:** база проваливается на `choline` НИЖЕ
случайного (0.415, надёжный n=14) — рассуждение о "белковой маргинали, которая
бесплатна под lcs" (`lipid_coldsplit_architecture_direction.md` §7j) применимо и к
architecture 2. `rankprot`/`tailtokens` чинят именно этот провал (0.61), но не
трогают `anionic` (0.49-0.51, у случайного); `protgeom8` — противоположный эффект:
лучший `anionic` (0.577), но не чинит `choline` (0.447, всё ещё ниже случайного).

### 9.2 GAP, коллапс, сходимость

| конфиг | GAP (choline / phosphorus_free / sphingolipids) | `collapse_fraction` (сред./макс.) | `converged`=1 доля |
|---|---|---|---|
| база | 0.157 / 0.220 / 0.303 | 0.002 / 0.017 | 10/20 |
| `_rankprot` | -0.018 / -0.050 / -0.099 | **0.146 / 0.592** | 4/20 |
| `_tailtokens` | 0.155 / 0.224 / 0.271 | 0.023 / 0.141 | 7/20 |
| `_protgeom8` | 0.202 / 0.170 / 0.238 | 0.012 / 0.042 | 5/20 |

`rankprot` здесь ведёт себя заметно менее стабильно, чем на geometric_edge:
`collapse_fraction` до 59% эпох на одном (набор, сид), а GAP уходит в ОТРИЦАТЕЛЬНУЮ
область на 3 из 4 наборов (valid BA выше train BA в среднем) — правдоподобное
объяснение: `--loss_type=pairwise_rank` не оптимизирует напрямую ту BA, которую
печатает лог (то же уже отмечено для geometric_edge в §4 выше), так что GAP по BA
здесь не читает то, что модель реально минимизирует.

### 9.3 Increment над нуль-моделью (in-sample, pair-level, epoch 120)

Секция для architecture 2 не имеет `_prot`-разбивки (нет графа/белковых узлов),
только `chem_pair`/`net_pair`:

| конфиг | anionic (chem/net) | choline | phosphorus_free | sphingolipids |
|---|---|---|---|---|
| база | 0.530/0.491 | 0.552/0.447 | 0.509/0.488 | 0.556/0.419 |
| `_rankprot` | 0.530/0.474 | 0.552/**0.580** | 0.509/0.513 | 0.556/0.376 |
| `_tailtokens` | 0.535/0.529 | 0.541/0.507 | 0.543/0.517 | 0.480/0.352 |
| `_protgeom8` | 0.512/**0.524** | 0.540/0.421 | 0.521/**0.538** | 0.446/0.419 |

База ниже нуль-модели на pair-уровне на ВСЕХ четырёх наборах — согласуется с
`descriptors_baseline_leak_confirmed.md` ("architecture 2 не бьёт даже kNN-lookup").
`rankprot` чинит именно `choline` (0.580>0.552), `protgeom8` — `anionic` и
`phosphorus_free`, но не одновременно ни один вариант не чинит все четыре.

**Вывод по architecture 2:** нет единого победителя среди 4 вариантов — как и у
geometric_edge, разные правки чинят разные наборы, и ни одна не доминирует по всем
трём осям (метрика/GAP/стабильность) сразу. `rankprot` даёт лучший choline-сигнал
ценой худшей стабильности обучения из всех восьми (geometric_edge+descriptors_head)
конфигов, разобранных в этом файле.

## 10. Устаревшие упоминания "`advprot` = текущий лучший" — куда добавлены пометки

Числа НЕ переписаны (конвенция проекта — не молчаливая правка задним числом), в
каждый файл добавлена короткая датированная пометка со ссылкой на этот файл:

| файл | место | что было заявлено |
|---|---|---|
| `files/geometric_edge_descriptors_baseline_selection_results.md` | §0 п.6, §4 (заголовок и §4.1/4.2), §5 | "текущий лучший lcs-baseline" / "текущий лучший lcs-кандидат" применительно к `..._balanced_lipid_classes_advprot`, без сравнения с `liphid32` |
| `files/lcs_descriptors_and_protgeom8_baseline_results.md` | §0 п.2, §3.1 (интро) | "текущего лучшего lcs-baseline с advprot" как данность, без альтернатив |
| `files/reference_baselines_metrics_proposal.md` | §5 ("Третий пробел") | "текущем лучшем кандидате (`_advprot`)" |

## чем посчитано

- `analysis/lcs_geometric_edge_candidate_ranking.py` (новый, read-only) — читает
  `metrics_summary.csv`, фильтрует по `bilinear_fusion=1`/`bilinear_pooled_norm=1`/
  точному совпадению строки `protein_descriptors`, агрегирует
  `AUC_within_protein[_pairs]`, sensitivity/specificity/BA, `mean_train_valid_gap`
  по (label, exclusion_set) со SEM по 5 сидам. Запуск:
  `python3 analysis/lcs_geometric_edge_candidate_ranking.py`.
- `training/run_metrics.py:259-265` — точные определения `collapse_fraction`
  (доля эпох с `predicted_positive==0` или `predicted_negative==0` на valid) и
  `converged` (последние 3 valid BA в пределах 0.01).
- Null-model/increment числа (§5, §9.3) — прямое чтение уже сгенерированных
  `graphics/<label>/<label>.md`, секция "AUC vs chemistry null model, in-sample
  increment" (`analysis/full_label_report.py`/`analysis/interaction_increment.py`,
  `--split valid`, epoch 120). Не пересчитывались; для лейблов, где секция пуста или
  падает с `ValueError`, число явно помечено как отсутствующее, а не подставлено
  из другого конфига.
- Утечка/нормализация (§1) — прочитаны целиком `files/lipid_coldsplit_architecture_direction.md`
  §4, §7f и `files/descriptors_baseline_leak_confirmed.md` (раздел про MolFormer
  identity check), ссылки на строки кода даны в тех файлах, здесь не
  переизмерялись.
- Список лейблов (§2) — `grep -l lipid_coldsplit scripts/arg_files/geometric_edge*.md`
  пересечено с `grep -l bilinear_fusion`, дальше сверено с фактическими строками
  `metrics_summary.csv` через `analysis/lcs_geometric_edge_candidate_ranking.py`.
- Ничего не обучалось, ни один чекпойнт не загружался,
  `scripts/lib/generate_label_report.sh`/`full_label_report.py`/`checkpoint_scores.py`
  не запускались в этой сессии.
