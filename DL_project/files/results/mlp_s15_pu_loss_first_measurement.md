# PU-loss на MLP-линии species15: первое измерение, и баг, найденный по пути

Дата: 2026-09-30. Три варианта `--pu_loss` поверх лучшего MLP-baseline
(`mlp_s15_nomb_hid64`, test BA 0.876 ± 0.025, n=5) на `--lipid_species_coldsplit=0.15`:
единый ρ на 0.05 и на 0.1 скрытых позитивов среди unlabeled, и `--pu_rho_by_subclass`
(свой ρ на каждый подкласс липида, реализован этой же сессией) поверх 0.1. Все три —
первый живой прогон каждого из механизмов на этой линии.

## Баг, найденный и исправленный по дороге

`mlp_s15_nomb_hid64_pu01_subclass` упал на всех 5 сидах на первой же эпохе:

```
AttributeError: 'PreassembledBatch' object has no attribute 'pair_id'
```

Причина — в `dataloader/Dataloader.py`: тензор `_pair_id_tensor` строился только под
`--grab_loss` («без grab_loss он строился бы никем не используемым» — комментарий в
коде был буквально прав про единственного потребителя на момент, когда писался).
`--pu_rho_by_subclass` — второй потребитель (ищет подкласс строки по её `pair_id`,
`pu_prior_and_groups` в `training/new_train.py`), который это условие не предвидело.
Под `--descriptors --descriptor_mlp` данные грузятся через
`PreassembledBatch` (lean-loading путь, `dataloader/preassembled_loader.py`) —
именно там отсутствие `pair_id` и вылезало.

Исправление — расширить условие постройки тензора на обоих потребителей:

```python
self._pair_id_tensor = (
    torch.tensor(orig_indexes, dtype=torch.long).view(-1, 1)
    if self.config.grab_loss or getattr(self.config, "pu_rho_by_subclass", False)
    else None
)
```

Механизм сборки батча (`preassembled_loader.py::_batch`) уже был общим — трактует
`pair_id` как обычное graph-level поле и складывает его тем же способом, что и любой
другой атрибут, так что специальных правок под preassembly не понадобилось, только
условие постройки тензора. Проверено на всех 5 сидах после фикса — падений больше нет.
`tests/test_pair_index_alignment.py`, `tests/test_dataloader_lipid_graphs.py`,
`tests/test_grab_graph.py` (54 теста) проходят без изменений.

## Результат: все три варианта хуже cross-entropy, subclass — сильно хуже

Парно к базе `mlp_s15_nomb_hid64` (5 сидов, matched по seed):

| вариант | test BA | лучше сидов | test F1 | test sens | test spec |
|---|---:|---:|---:|---:|---:|
| `pu005` (ρ=0.05, единый) | −0.037 | **0/5** | −0.042 | −0.091 (0/5) | +0.017 (3/5) |
| `pu01` (ρ=0.1, единый) | −0.029 | 1/5 | −0.038 | −0.037 (0/5) | −0.021 (1/5) |
| `pu01_subclass` (ρ по подклассу) | **−0.196** | **0/5** | **−0.286** | **−0.464 (0/5)** | +0.073 (5/5) |

Абсолютные числа (mean ± std, n=5):

| | test BA | test F1 |
|---|---:|---:|
| база (cross-entropy) | 0.876 ± 0.055 | 0.827 ± 0.070 |
| pu005 | 0.839 ± 0.047 | 0.786 ± 0.061 |
| pu01 | 0.847 ± 0.038 | 0.789 ± 0.047 |
| pu01_subclass | **0.680 ± 0.037** | **0.542 ± 0.078** |

**Единый PU (pu005/pu01) уступает cross-entropy стабильно, но умеренно** — 0/5 и 1/5
лучше по BA, около −0.03…−0.04. Оба хуже в первую очередь за счёт sensitivity
(0/5 лучше на обоих), specificity почти не страдает — модель под PU становится
немного консервативнее, чем под cross-entropy, но не разваливается.

**Per-subclass PU — не умеренная деградация, а коллапс.** Sensitivity падает на
0.27–0.53 (против 0.5+ у базы) при специфичности 0.82–0.98 — модель на всех 5 сидах
систематически недооценивает позитивы. Это не случайность одного сида: паттерн
одинаковый на всех пяти (BA 0.62–0.71, sens 0.27–0.53, spec 0.82–0.98).

## Что известно о причине, а что нет

Посчитанные по подклассам ρ сильно неоднородны — на seed 0:
`FA=0.50, PC=0.48, PE=0.50` против `HexCer=0.26, Cer=0.25, TAG=0.25, LPC=0.28` — то
есть одни подклассы получают почти вдвое больший implied prior, чем другие. Сеть
одновременно решает 14 отдельных nnPU-целей (`_grouped_pu_loss`,
`architecture/loss.py`) с очень разными implied class-balance таргетами на 1614
строках — в среднем ~115 строк на группу, у части подклассов заметно меньше.

Частота nnPU-коррекции (диагностика `negative_risk < -beta`) у `pu01_subclass` НЕ
выше, чем у пулированного `pu01` — 12-17 срабатываний за эпоху на 379 group-batch'ей
(`pu01_subclass`) против 30-36 на 101 батчей (`pu01`), то есть по общему счёту реже,
не чаще. Значит объяснение «коррекция просто срабатывает намного чаще» не
подтверждается этим измерением — механизм коллапса sensitivity остаётся не до конца
объяснённым, нужно смотреть на что-то другое (например, как складываются градиенты
14 разных `positive_risk`-компонент, у каждой из которых свой вес и своя цель).

## Итог

На этой линии (mlp, `--lipid_species_coldsplit`, лучшая MLP-архитектура) PU-loss в
любом из трёх вариантов не улучшает cross-entropy — единый ρ понемногу хуже, ρ по
подклассу сильно хуже. Открытый вопрос из
[project_pu_loss_subclass_diversification_open](не файл проекта, а auto-memory) о
выборе рычага диверсификации (ρ на подкласс / вес в лоссе на подкласс / сэмплирование)
получил первую реальную точку: диверсификация именно через per-group ρ в текущей
реализации — плохой выбор на этом бенчмарке, не нейтральный.

## Чем посчитано

- `analysis/compare_labels.py <label> mlp_s15_nomb_hid64` (read-only,
  `metrics_summary.csv`) для каждого из трёх вариантов.
- `analysis/summarize_label.py <label>` для абсолютных чисел.
- Частота nnPU-коррекции — построчно из `script_logs/mlp_s15_nomb_hid64_pu01_seeds*/`
  и `script_logs/mlp_s15_nomb_hid64_pu01_subclass_seeds*/` (grep по `PU nnPU
  correction`).
- Код: `dataloader/Dataloader.py` (`_pair_id_tensor`, фикс этой сессии),
  `dataloader/preassembled_loader.py` (`PreassembledBatch`, `_batch`),
  `training/new_train.py` (`build_pu_subclass_priors`, `pu_prior_and_groups`),
  `architecture/loss.py` (`_grouped_pu_loss`).
- Аргфайлы: `arg_files/mlp_s15_nomb_hid64_pu{005,01,01_subclass}.md`.
