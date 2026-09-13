# geometric_edge, lipid_coldsplit: protbind6/protgeom8/protunion14 family comparison (2026-09-13)

Снимок на 2026-09-13. Все 14 лейблов — `geometric_edge_{mlp,attention}_protgeom_family_
neutral_normalized_bilinear_fusion_bilinear_norm_lcs[_esm3]*`, `--protein_descriptors=`
(нормализовано через DESCRIPTOR_CATALOG), под `--lipid_coldsplit`. Числа взяты из уже
сгенерированных `graphics/<label>/<label>.md` (`analysis/summarize_label.py`,
`analysis/full_label_report.py --split valid`) и `analysis/seed_variability_summary.py`
(новый в этой сессии, read-only, `metrics_summary.csv` only). Ничего не обучалось в
рамках сведения этой таблицы — все 14 лейблов уже были обучены на bigfoot заранее.

`sens std`/`spec std` — std sensitivity/specificity МЕЖДУ СИДАМИ, посчитано сначала
внутри каждой из 4 групп (наборов липидов), затем усреднено/медианизировано по
группам (не std по пулу всех 20 строк сразу) — показывает, насколько неустойчиво
обучение конкретного конфига от сида к сиду, отдельно от `gap` (который меряет
разрыв sens/spec ВНУТРИ одного прогона, а не изменчивость между прогонами).

| конфиг | test BA | test sens | test spec | gap mean | gap median | sens std | spec std | increment_prot | fit_chem_net_prot |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| attention protbind6 | 0.5201 | 0.4884 | 0.5518 | 0.5674 | 0.5734 | 0.2975 | 0.2830 | 0.016 | 0.724 |
| attention esm3+protbind6 | 0.5343 | 0.4146 | 0.6540 | 0.5242 | 0.5788 | 0.2755 | 0.2052 | 0.030 | 0.738 |
| mlp protbind6 | 0.5296 | 0.3576 | 0.7017 | 0.4501 | 0.5086 | 0.1886 | 0.1776 | 0.008 | 0.716 |
| mlp esm3+protbind6 | 0.5373 | 0.3424 | 0.7323 | 0.4798 | 0.4587 | 0.1686 | 0.1383 | 0.023 | 0.730 |
| mlp protbind6+prothid16 | 0.5255 | 0.3228 | 0.7282 | 0.6108 | 0.6014 | 0.2514 | 0.2415 | 0.014 | 0.722 |
| mlp protbind6+prothid32 | 0.5048 | 0.4248 | 0.5849 | 0.5024 | 0.5130 | 0.2906 | 0.2626 | 0.009 | 0.716 |
| mlp esm3+protbind6+prothid16 | 0.5720 | 0.4201 | 0.7238 | 0.4363 | 0.3908 | 0.2517 | 0.1774 | 0.011 | 0.719 |
| mlp esm3+protbind6+prothid32 | 0.5414 | 0.4939 | 0.5889 | 0.2914 | 0.2739 | 0.1191 | 0.1477 | 0.019 | 0.726 |
| attention esm3 (база, family-neutral-7) | 0.5283 | 0.4626 | 0.5939 | 0.3959 | 0.2230 | 0.2348 | 0.2020 | 0.025 | 0.732 |
| mlp esm3 (база, family-neutral-7) | 0.5530 | 0.3313 | 0.7747 | 0.4476 | 0.4864 | 0.1655 | 0.0931 | 0.013 | 0.721 |
| mlp esm3+protgeom8 | 0.5525 | 0.3787 | 0.7263 | 0.4057 | 0.3713 | 0.1966 | 0.1592 | 0.036 | 0.744 |
| mlp esm3+protunion14 | 0.5409 | 0.3326 | 0.7493 | 0.4829 | 0.4789 | 0.1741 | 0.1552 | 0.012 | 0.719 |
| mlp esm3+protunion14+prothid16 | 0.5604 | 0.4261 | 0.6947 | 0.4159 | 0.4348 | 0.2256 | 0.1816 | 0.024 | 0.731 |
| mlp esm3+protunion14+prothid32 | 0.5758 | 0.4516 | 0.6999 | 0.3797 | 0.3362 | 0.2193 | 0.1345 | 0.012 | 0.720 |

## Наблюдения

- Лучший test BA (пулом) — `mlp esm3+protunion14+prothid32` (0.5758), обгоняет базу
  (0.5530) и лучший из protbind6-линии (`esm3+protbind6+prothid16`, 0.5720).
- Лучший `increment_prot`/`fit_chem_net_prot` (сеть дальше всех от химии по
  внутрибелковому increment) — `mlp esm3+protgeom8` (0.036/0.744), не тот же
  конфиг, что лидирует по BA.
- Самый низкий `spec std` (самая устойчивая specificity между сидами) — база
  `mlp esm3` (0.0931), без каких-либо добавок дескрипторов.
- Ни один конфиг не лидирует одновременно по всем осям (BA / increment_prot /
  sens std / spec std) — компромисс, не доминирование.
- protbind6 (13 признаков) сам по себе ни разу не обгоняет базу по BA; выигрыш
  появляется только с добавлением esm3+prothid16/32 или переходом на protunion14.

## Чем посчитано

- `graphics/<label>/<label>.md` для всех 14 лейблов, каждый — `analysis/
  summarize_label.py` (Overall-таблица, `abs(sensitivity-specificity) gap` строка) +
  `analysis/full_label_report.py --split valid` (`mean AUC + increment, epoch 120`,
  `ranked INSIDE each protein, epoch 120` секции) — сгенерированы в этой сессии,
  прочитаны как есть, не пересчитывались повторно для этой таблицы.
- `sens std`/`spec std` — `analysis/seed_variability_summary.py <label>` (новый в
  этой сессии), read-only чтение `metrics_summary.csv`.
- Полный список признаков: `protbind6` = family-neutral-7 (`pocket_volume_per_sasa,
  pocket_elongation, pocket_flatness, buriedness_q50, apolar_sasa_share,
  aromatic_share, hydropathy_rim`) + `ev28_q10, aromatic_share_rim, depth_q10,
  hydropathy_core, ev14_q10, hydropathy_mean`; `protgeom8` = `pocket_extent,
  pocket_elongation, pocket_flatness, depth_q10, buriedness_q50, aromatic_share,
  hydropathy_core, hydropathy_rim`; `protunion14` = union обоих (14 = protbind6 +
  `pocket_extent`, единственное, чего не было в protbind6).
