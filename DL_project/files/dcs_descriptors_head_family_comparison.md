# descriptors_head (одноветочная архитектура), double_coldsplit: вся линия (2026-09-13)

Снимок на 2026-09-13. Все 49 лейблов — `descriptors_*` под `--descriptors_head`
(плоские дескрипторы, self-attention над именованными токенами, без графа/GATv2 ни
на одной стороне, без bilinear_fusion — архитектурно одноветочная, в отличие от
geometric_edge). Цифры взяты напрямую из `metrics_summary.csv`
(`analysis/seed_variability_summary.py`, read-only, без графиков/пересчёта
нуль-модели). Без фильтров — весь ряд как есть.

**Осторожно с `descriptors_no_extent_coarse_add_lipprop`** (строка ниже) — это старый
канонический baseline с подтверждённой утечкой семейства LBP_BPI_CETP (test BA 0.826
на этой семье против 0.549 на остальных шести, `files/descriptors_baseline_leak_
confirmed.md`) — его пулированный BA (0.5887) не читается как реальный сигнал.

| конфиг | test BA | test sens | test spec | gap mean | gap median | sens std | spec std | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| descriptors_1head_coarse | 0.5705 | 0.6021 | 0.5389 | 0.3433 | 0.2647 | 0.2114 | 0.2308 | 35 |
| descriptors_2heads_coarse | 0.5725 | 0.5944 | 0.5506 | 0.3390 | 0.2866 | 0.2235 | 0.2282 | 35 |
| descriptors_2paths | 0.5447 | 0.5141 | 0.5754 | 0.5470 | 0.5236 | 0.3484 | 0.3123 | 35 |
| descriptors_2paths_4heads | 0.5634 | 0.5890 | 0.5379 | 0.4473 | 0.4000 | 0.2686 | 0.2618 | 35 |
| descriptors_2paths_extent | 0.5559 | 0.6261 | 0.4857 | 0.4201 | 0.4197 | 0.2116 | 0.2253 | 35 |
| descriptors_2paths_extent_protgeom | 0.5648 | 0.5653 | 0.5644 | 0.3987 | 0.3515 | 0.2569 | 0.1957 | 35 |
| descriptors_2paths_protgeom | 0.5645 | 0.4962 | 0.6328 | 0.3599 | 0.3362 | 0.1956 | 0.1800 | 35 |
| descriptors_3heads_coarse | 0.5749 | 0.6239 | 0.5258 | 0.3162 | 0.2381 | 0.1826 | 0.1915 | 35 |
| descriptors_coarse | 0.5805 | 0.5994 | 0.5616 | 0.3193 | 0.2800 | 0.2138 | 0.1947 | 35 |
| descriptors_coarse_buriedness_match | 0.5846 | 0.6031 | 0.5661 | 0.4038 | 0.3750 | 0.2401 | 0.2435 | 35 |
| descriptors_coarse_hbond_match | 0.5818 | 0.5735 | 0.5901 | 0.3983 | 0.3529 | 0.2394 | 0.2421 | 35 |
| descriptors_coarse_hydrocore | 0.5839 | 0.5731 | 0.5947 | 0.2990 | 0.2313 | 0.1937 | 0.1857 | 35 |
| descriptors_coarse_pocket_elongation | 0.5760 | 0.6085 | 0.5435 | 0.3723 | 0.2800 | 0.2203 | 0.2098 | 35 |
| descriptors_coarse_tail_elongation_fit | 0.5768 | 0.5804 | 0.5733 | 0.2936 | 0.2353 | 0.1726 | 0.1789 | 35 |
| descriptors_head_family_neutral_lipprop | 0.5545 | 0.6236 | 0.4854 | 0.3901 | 0.2469 | 0.2203 | 0.2328 | 35 |
| descriptors_head_family_neutral_lipprop_heads1 | 0.5492 | 0.5678 | 0.5306 | 0.3368 | 0.2118 | 0.2034 | 0.1535 | 45 |
| descriptors_head_family_neutral_lipprop_pair | 0.5537 | 0.5772 | 0.5301 | 0.4451 | 0.3200 | 0.2696 | 0.2889 | 35 |
| descriptors_head_family_neutral_lipprop_rankprot | 0.5371 | 0.4198 | 0.6544 | 0.6823 | 0.7854 | 0.3211 | 0.2970 | 45 |
| descriptors_lipprop | 0.5646 | 0.6002 | 0.5290 | 0.4026 | 0.3529 | 0.2199 | 0.2417 | 35 |
| descriptors_mlp_coarse | 0.5609 | 0.5469 | 0.5750 | 0.2711 | 0.1869 | 0.1699 | 0.1565 | 35 |
| descriptors_No_extent | 0.6064 | 0.5770 | 0.6359 | 0.2771 | 0.2017 | 0.1885 | 0.1526 | 35 |
| descriptors_no_extent_coarse | 0.6008 | 0.5810 | 0.6206 | 0.2455 | 0.1796 | 0.1784 | 0.1447 | 35 |
| descriptors_no_extent_coarse_add_dpt005 | 0.5791 | 0.5649 | 0.5934 | 0.3477 | 0.3452 | 0.2378 | 0.2027 | 35 |
| descriptors_no_extent_coarse_add_hid16 | 0.5784 | 0.5832 | 0.5735 | 0.2505 | 0.2059 | 0.1568 | 0.1510 | 35 |
| descriptors_no_extent_coarse_add_hid24 | 0.5697 | 0.5309 | 0.6085 | 0.2646 | 0.2000 | 0.1665 | 0.1486 | 35 |
| descriptors_no_extent_coarse_add_hid32 | 0.5829 | 0.5702 | 0.5955 | 0.2707 | 0.1512 | 0.1845 | 0.1422 | 35 |
| descriptors_no_extent_coarse_add_lipprop (утёкший, см. предупреждение) | 0.5887 | 0.5686 | 0.6087 | 0.2325 | 0.2400 | 0.1528 | 0.1541 | 35 |
| descriptors_no_extent_coarse_add_lipprop_dpt005 | 0.5626 | 0.5502 | 0.5749 | 0.4010 | 0.4033 | 0.2634 | 0.2532 | 35 |
| descriptors_no_extent_coarse_add_lipprop_extent | 0.5374 | 0.3900 | 0.6848 | 0.4094 | 0.3711 | 0.3194 | 0.2130 | 10 |
| descriptors_no_extent_coarse_add_lipprop_family_neutral | 0.5426 | 0.5613 | 0.5239 | 0.3776 | 0.3837 | 0.0977 | 0.1390 | 10 |
| descriptors_no_extent_coarse_add_lipprop_hid2 | 0.5222 | 0.5644 | 0.4799 | 0.7199 | 0.8299 | 0.4121 | 0.4254 | 35 |
| descriptors_no_extent_coarse_add_lipprop_hid4 | 0.5556 | 0.6344 | 0.4768 | 0.4941 | 0.4348 | 0.3067 | 0.3315 | 35 |
| descriptors_no_extent_coarse_add_lipprop_lr0005 | 0.5905 | 0.5805 | 0.6005 | 0.2582 | 0.2239 | 0.1693 | 0.1547 | 35 |
| descriptors_no_extent_coarse_add_lipprop_lr001 | 0.6083 | 0.6689 | 0.5477 | 0.2956 | 0.2400 | 0.1928 | 0.1606 | 35 |
| descriptors_no_extent_coarse_add_lipprop_lr005 | 0.5835 | 0.7168 | 0.4501 | 0.4653 | 0.4006 | 0.2032 | 0.2323 | 35 |
| descriptors_no_extent_coarse_add_lipprop_rankprot | 0.5427 | 0.6625 | 0.4228 | 0.6743 | 0.8603 | 0.3752 | 0.3671 | 34 |
| descriptors_no_extent_coarse_add_no_chain_lipprop | 0.5439 | 0.4509 | 0.6368 | 0.4390 | 0.3824 | 0.3092 | 0.2313 | 35 |
| descriptors_no_extent_coarse_flatten | 0.5488 | 0.4527 | 0.6449 | 0.3637 | 0.2000 | 0.2600 | 0.1941 | 35 |
| descriptors_no_extent_coarse_pool_add | 0.5925 | 0.6001 | 0.5849 | 0.2375 | 0.1776 | 0.1553 | 0.1336 | 35 |
| descriptors_no_extent_coarse_pool_addmax | 0.5866 | 0.5615 | 0.6117 | 0.2551 | 0.1334 | 0.1477 | 0.1284 | 35 |
| descriptors_no_extent_coarse_pool_gem | 0.6004 | 0.5802 | 0.6206 | 0.2457 | 0.1796 | 0.1826 | 0.1402 | 35 |
| descriptors_no_extent_coarse_pool_max | 0.5832 | 0.5774 | 0.5890 | 0.3888 | 0.2112 | 0.2389 | 0.2088 | 35 |
| descriptors_pair_clean | 0.5629 | 0.5588 | 0.5670 | 0.4602 | 0.4118 | 0.2796 | 0.2363 | 35 |
| descriptors_pair_only | 0.5461 | 0.5745 | 0.5178 | 0.5201 | 0.4861 | 0.3150 | 0.2475 | 35 |
| descriptors_pair_only_rankprot | 0.5122 | 0.5790 | 0.4454 | 0.7548 | 0.8343 | 0.4314 | 0.4306 | 34 |
| descriptors_path | 0.5756 | 0.5752 | 0.5759 | 0.3112 | 0.2528 | 0.1759 | 0.1758 | 35 |
| descriptors_path_v2 | 0.5720 | 0.5549 | 0.5892 | 0.5696 | 0.5930 | 0.1852 | 0.1869 | 35 |
| descriptors_shares_coarse | 0.5789 | 0.5235 | 0.6343 | 0.3260 | 0.2800 | 0.1652 | 0.1559 | 35 |
| descriptors_v2_lipprop | 0.5813 | 0.5447 | 0.6178 | 0.4368 | 0.4118 | 0.2486 | 0.2331 | 35 |

## Наблюдения

- Лучший test BA пулом — `descriptors_No_extent` (0.6064) и
  `descriptors_no_extent_coarse_add_lipprop_lr001` (0.6083), оба заметно выше всей
  geometric_edge `_bilinear_norm` линии (макс. там 0.5594) — но у второго нет
  проверки на утечку семьи (та же архитектурная ветка, что у подтверждённо
  утёкшего `..._add_lipprop`, не проверялась отдельно).
- Самый низкий gap (наиболее сбалансированный sens/spec) —
  `descriptors_no_extent_coarse_add_lipprop` (0.2325) — именно утёкший baseline;
  среди НЕ вызывающих подозрений — `descriptors_no_extent_coarse_pool_add` (0.2375).
- Самый низкий spec std — `descriptors_no_extent_coarse_pool_addmax` (0.1284).
- `rankprot`-варианты (`descriptors_head_family_neutral_lipprop_rankprot`,
  `descriptors_no_extent_coarse_add_lipprop_rankprot`, `descriptors_pair_only_
  rankprot`) — худшие по gap (0.67-0.75) и по обоим std из всей таблицы, тот же
  паттерн, что и в LCS-версии этой архитектуры.
- Два лейбла (`..._extent`, `..._family_neutral`) прогнаны только на 2 семьях
  (n=10, 2 группы) — недостаточно для выводов, оставлены для полноты списка.

## Фильтр: нормализованный вход + gap <= 0.5, по убыванию BA (2026-09-13)

"Нормализованный вход" = `--descriptor_names=` (DESCRIPTOR_CATALOG, всегда
train-only z-score) вместо `--pocket_descriptors` (старый путь, без нормализации
вообще). Из 49 лейблов только 20 используют `--descriptor_names=` (проверено прямым
grep по `scripts/arg_files/*.md`, не по названию — имя "no_extent_coarse" не
предсказывает путь надёжно: `..._add_dpt005`/`..._add_lipprop_dpt005`/
`..._add_no_chain_lipprop` нормализованы, несмотря на название). Из этих 20 ещё 3
отсеиваются по gap > 0.5 (`rankprot` 0.68, `pair_only` 0.52, `pair_only_rankprot`
0.75) — остаётся 17:

| конфиг | test BA | test sens | test spec | gap mean | gap median | sens std | spec std |
|---|---:|---:|---:|---:|---:|---:|---:|
| descriptors_coarse_buriedness_match | 0.5846 | 0.6031 | 0.5661 | 0.4038 | 0.3750 | 0.2401 | 0.2435 |
| descriptors_coarse_hydrocore | 0.5839 | 0.5731 | 0.5947 | 0.2990 | 0.2313 | 0.1937 | 0.1857 |
| descriptors_coarse_hbond_match | 0.5818 | 0.5735 | 0.5901 | 0.3983 | 0.3529 | 0.2394 | 0.2421 |
| descriptors_coarse | 0.5805 | 0.5994 | 0.5616 | 0.3193 | 0.2800 | 0.2138 | 0.1947 |
| descriptors_no_extent_coarse_add_dpt005 | 0.5791 | 0.5649 | 0.5934 | 0.3477 | 0.3452 | 0.2378 | 0.2027 |
| descriptors_coarse_tail_elongation_fit | 0.5768 | 0.5804 | 0.5733 | 0.2936 | 0.2353 | 0.1726 | 0.1789 |
| descriptors_coarse_pocket_elongation | 0.5760 | 0.6085 | 0.5435 | 0.3723 | 0.2800 | 0.2203 | 0.2098 |
| descriptors_3heads_coarse | 0.5749 | 0.6239 | 0.5258 | 0.3162 | 0.2381 | 0.1826 | 0.1915 |
| descriptors_2heads_coarse | 0.5725 | 0.5944 | 0.5506 | 0.3390 | 0.2866 | 0.2235 | 0.2282 |
| descriptors_1head_coarse | 0.5705 | 0.6021 | 0.5389 | 0.3433 | 0.2647 | 0.2114 | 0.2308 |
| descriptors_pair_clean | 0.5629 | 0.5588 | 0.5670 | 0.4602 | 0.4118 | 0.2796 | 0.2363 |
| descriptors_no_extent_coarse_add_lipprop_dpt005 | 0.5626 | 0.5502 | 0.5749 | 0.4010 | 0.4033 | 0.2634 | 0.2532 |
| descriptors_mlp_coarse | 0.5609 | 0.5469 | 0.5750 | 0.2711 | 0.1869 | 0.1699 | 0.1565 |
| descriptors_head_family_neutral_lipprop | 0.5545 | 0.6236 | 0.4854 | 0.3901 | 0.2469 | 0.2203 | 0.2328 |
| descriptors_head_family_neutral_lipprop_pair | 0.5537 | 0.5772 | 0.5301 | 0.4451 | 0.3200 | 0.2696 | 0.2889 |
| descriptors_head_family_neutral_lipprop_heads1 | 0.5492 | 0.5678 | 0.5306 | 0.3368 | 0.2118 | 0.2034 | 0.1535 |
| descriptors_no_extent_coarse_add_no_chain_lipprop | 0.5439 | 0.4509 | 0.6368 | 0.4390 | 0.3824 | 0.3092 | 0.2313 |

Заметно: весь верхний блок (`descriptors_coarse*`, 8 из топ-10) не совпадает с
подтверждённо утёкшим `descriptors_no_extent_coarse_add_lipprop` (которое здесь
отсутствует вовсе — оно на RAW-пути, `--pocket_descriptors`, отфильтровано этим
условием) — лидер этого честного списка (`coarse_buriedness_match`, 0.5846) не
проверялся отдельно на утечку семьи, это не то же самое, что "подтверждён чистым".

## Чем посчитано

`analysis/seed_variability_summary.py <label> ...` (read-only, `metrics_summary.csv`)
по всем 49 лейблам одним вызовом; классификация NORM/RAW — `grep -q
"descriptor_names="` против `scripts/arg_files/<label>.md` напрямую, не по имени.
