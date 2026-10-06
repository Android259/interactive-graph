# История дескрипторных моделей: `descriptors_*`, `descriptors_head`, `descriptor_mlp`

> **Правило сопровождения.** Хронология с итогом каждого шага. Заменяет исполненные
> планы «запуски `descriptors_head` на `species15`» и «подбор дескрипторов под
> `--descriptor_mlp`». Числа — из документов `results/`, на которые стоят ссылки.
> Новый шаг дописывается внизу.

Общее у всех: модель видит только ручные числовые дескрипторы липида, кармана и пары
(`--pair_descriptors --descriptor_names=...`, каталог —
[../reference/descriptor_catalog.md](../reference/descriptor_catalog.md)), без графов,
ESM3 и MoLFormer. Загрузка в этом режиме лёгкая: загрузчик не строит графы, а данные
целиком собираются на устройстве.

## 0. Коротко

| шаг | модель | итог |
|---|---|---|
| авг | `descriptors_*` (головы внимания над токенами-дескрипторами) | лучший канонический вариант держался на утечке семьи LBP_BPI_CETP |
| 11–13 сен | `dh_family_neutral_lipprop` (честный набор) | на `dcs` 0.555, почти всё — одна семья; на `lcs` нет лидера |
| 29 сен | `dh_s15_*` на `species15` | голова не подгоняет даже train (0.51): узкое место — сама голова |
| 30 сен | `--descriptor_mlp` (простой MLP) | train 0.87; лучший `mlp_s15_nomb_hid64` 0.876 — на уровне планки 0.871 |
| 30 сен – 6 окт | архитектурная сетка, абляции, PU-loss | ничего не лучше базы; обе стороны (липид и белок) нужны |

## 1. `descriptors_*` (август)

- Канонический `descriptors_no_extent_coarse_add_lipprop` на двустороннем разрезе:
  BA 0.589, но 0.826 на LBP_BPI_CETP против 0.549 на остальных шести. Это утечка семьи,
  и она переживает поправку на химическую нуль-модель. Почистить флагами не удалось.
  [descriptors_baseline_leak_confirmed](../results/descriptors_baseline_leak_confirmed.md).
- Честная замена: `dh_family_neutral_lipprop` — 7 белковых дескрипторов,
  не выдающих семью, плюс 4 липидных (chain, unsaturation, hbond, heavy) через
  `--descriptor_names`.

## 2. `descriptors_head` на `dcs` и `lcs` (11–13 сентября)

- `dcs`, 7 семей × 5 сидов: BA 0.555 ± 0.013. LBP_BPI_CETP 0.677, остальные
  0.509–0.564. Порог систематически не на месте: средний разъезд |sens−spec| 0.39.
  [mlp_baseline_lcs_dcs](../results/mlp_baseline_lcs_dcs.md),
  [lbp_bpi_cetp_family_identifiability](../results/lbp_bpi_cetp_family_identifiability.md).
- `lcs`: база проваливается на `choline` ниже случайного (0.415); `rankprot` и
  `tailtokens` чинят `choline` (0.61) ценой стабильности. Единого лидера нет.
  [lcs_descriptors_head_family_comparison](../results/lcs_descriptors_head_family_comparison.md).

## 3. `descriptors_head` на `species15` (29 сентября)

- Добавлен `--marginal_balance_weight`: веса строк подгоняются так, что доля позитивов
  одинакова внутри каждого белка, класса липида и конкретного липида. Тогда эти
  одиночные «склонности» не несут информации о метке.
- Сетка `dh_s15_mbw*` (11 меток) и лестница дескрипторов `_d11…_d34`, отобранных
  жадно под логистическую регрессию.
- **Итог: узкое место — голова.** На тех же 11 входах: голова проекта train 0.51 /
  test 0.535; обычный MLP 64×64 — test 0.853; GBM — 0.837. Голова не может подогнаться
  даже под train из-за того, как она вкладывает каждый дескриптор
  (`Linear(1, dim)` на скаляр). [descriptors_head_bottleneck](../results/descriptors_head_bottleneck.md).

## 4. `--descriptor_mlp` на `species15` (30 сентября – 6 октября)

- На тех же дескрипторах `_d11…_d14` MLP подгоняет train 0.87 против 0.51 у головы,
  test 0.69–0.74 против 0.50–0.54
  ([descriptor_mlp_recheck_and_tuning](../results/descriptor_mlp_recheck_and_tuning.md)).
  Оговорка: эти прогоны унаследовали `--negatives_per_positive=5`, а планка считалась
  при 2, так что F1 несравним. Все `mlp_s15_*` потом переведены на 2.
- Лестница d11…d34 на `mlp_s15_nomb_hid32_m8` прогнана (`mlp_s15_nomb_hid32_m8_d*`),
  но её итог отдельно не разобран. Базой линии служит полный набор из 70 дескрипторов:
  **`mlp_s15_nomb_hid64` — BA 0.876 ± 0.025** при планке 0.871.
- Архитектурная сетка на нём, 14 вариантов (длина обучения, ширина, глубина, dropout,
  активация): ни один не лучше базы на 4–5 сидах из 5; `gelu` резко хуже (−0.10).
  [mlp_s15_architecture_sweep](../results/mlp_s15_architecture_sweep.md).
- Абляция 70 входов: обнуление липидных (22) или белковых и парных (48) стоит по
  −0.28 BA, то есть нужны обе стороны. Самый важный одиночный вход — `logp`.
  [mlp_s15_ablation_70_inputs](../results/mlp_s15_ablation_70_inputs.md).
- PU-loss (доля скрытых позитивов 0.05 / 0.1): 0.839 / 0.847, ниже планки. Вариант
  с ρ по подклассам сначала падал на первой эпохе; баг найден и исправлен.
  [mlp_s15_pu_loss_first_measurement](../results/mlp_s15_pu_loss_first_measurement.md).

## 5. MLP на `lipid_subclass` (октябрь)

- 17 дескрипторов (`mlp_sub_pb6`) против головы: BA 0.625 против 0.637.
  Набор `keep5` (5 карманных дескрипторов, отобраны абляцией) — 0.648, но у него AUC
  внутри белка ровно 0.500: без липидных входов модель не может ранжировать липиды
  одного белка.
  [mlp_vs_head_subclass_and_feature_ablation](../results/mlp_vs_head_subclass_and_feature_ablation.md),
  [mlp_all70_subclass_ablation](../results/mlp_all70_subclass_ablation.md),
  [keep5_all6_network_knn_kronrls_subclass](../results/keep5_all6_network_knn_kronrls_subclass.md).

## 6. Что из планов не сделано

- Второй раунд подбора дескрипторов для MLP: настоящий жадный шаг от лучшей точки
  лестницы (обучить → измерить → добавить). Не запускался: десятки прогонов на шаг.
- Подать `tail_double_bond_position` вместе с флагом «насыщенный» и дать хвостовым
  дескрипторам обходной канал мимо сжатия
  ([../proposals/species15_information_above_protein_subclass.md](../proposals/species15_information_above_protein_subclass.md) §7).
