# Feature mapping: 17 дескрипторов `mlp_sub_pb6` / `descriptors_head_..._protbind6`

Набор из `--descriptor_names=` в `scripts/arg_files/mlp_sub_pb6*.md` и в
`descriptors_head_family_neutral_lipprop_lcs_protbind6*.md` (одинаковый в обоих). Для каждого
имени: что измеряет, откуда берётся, как считается, как доходит до сети. Общий каталог (все
имена, не только эти 17) — [descriptor_catalog.md](descriptor_catalog.md); здесь только то,
что реально подаётся в эти модели.

Источник истины: `dataloader/pair_descriptors.py` (имена, липидные формулы),
`dataloader/protein_graph_builder.py` (значения кармана), `dataloader/Dataloader.py`
(сборка и стандартизация), `architecture/descriptor_mlp_head.py` (mlp).

## 1. Состав: 4 липидных + 13 карманных

Порядок как в arg-файле. Все 17 — скаляры, все берутся из каталога `DESCRIPTOR_CATALOG` по
имени; ничего, кроме них, mlp не видит (`descriptor_catalog_only`: липидная сторона пустой
`Data()`, ESM3/MolFormer/графы не читаются).

| # | имя | сторона | что физически |
|---|---|---|---|
| 1 | `chain` | липид | длина ацильного хвоста |
| 2 | `unsaturation` | липид | число C=C в молекуле |
| 3 | `hbond` | липид | способность головы к H-связям |
| 4 | `heavy` | липид | размер молекулы |
| 5 | `pocket_volume_per_sasa` | карман | «узость» кармана |
| 6 | `pocket_elongation` | карман | трубка vs чаша |
| 7 | `pocket_flatness` | карман | щель vs трубка |
| 8 | `buriedness_q50` | карман | типичная погружённость остатков |
| 9 | `apolar_sasa_share` | карман | доля неполярной поверхности |
| 10 | `aromatic_share` | карман | доля ароматических остатков |
| 11 | `hydropathy_rim` | карман | гидрофобность устья |
| 12 | `ev28_q10` | карман | закрытость (нижний дециль) по ev28 |
| 13 | `aromatic_share_rim` | карман | ароматика в устье |
| 14 | `depth_q10` | карман | мелкий дециль глубины |
| 15 | `hydropathy_core` | карман | гидрофобность глубины |
| 16 | `ev14_q10` | карман | закрытость (нижний дециль) по ev14 |
| 17 | `hydropathy_mean` | карман | гидрофобность всего кармана |

Пункты 5–11 — это `POCKET_DESCRIPTOR_FAMILY_NEUTRAL_NAMES`; 12–17 добавлены поверх
(«protbind6» = эти шесть).

## 2. Липидные: определение и реализация

Считаются из 2D-структуры (RDKit по SMILES), без докинга и без 3D. Функции в
`pair_descriptors.py`.

| имя | формула | функция | пропуск |
|---|---|---|---|
| `chain` | атомы C в самом длинном неароматическом ациклическом пути; головы, кольца, сахара выпадают | `longest_acyl_chain` | `None`, если SMILES не парсится или нет подходящего C |
| `unsaturation` | число неароматических связей C=C | `unsaturation_count` | `None` при непарсящемся SMILES |
| `hbond` | `NumHDonors + NumHAcceptors` | `hbond_capacity` | `None` |
| `heavy` | число тяжёлых атомов | `heavy_atom_count` | `None` |

Важные детали:
- `hbond` и `heavy` — прокси: поза не известна, измеряется свойство молекулы, а не контакт
  (см. docstring модуля).
- `heavy` в кэше хранится под именем `heavy_atoms`
  (`chemistry_prior._CACHE_MEASURE_ALIAS`).
- Один ряд таблицы может иметь несколько кандидатных SMILES (спектроскопическая
  неоднозначность). В нейросетевом пути значения идут **по кандидатам** (ragged,
  `raw_values[...] = (values, True)` в `Dataloader.py`), на уровне вида липида
  (`chemistry_prior._lipid_descriptor_table`) — **среднее по кандидатам**, каждый кандидат с
  равным весом.

## 3. Карманные: определение и реализация

Все значения одной функцией `pocket_descriptor()` (`protein_graph_builder.py:227`) из двух
артефактов белка: таблицы остатков `coarse_graph_nodes.csv` (колонки `residue_*`) и атомов
кармана `pocketness.pdb`. Остатки кармана — маска `pocket`; `core` = остатки с
`residue_mean_buriedness ≥ медианы по карману`, `rim` = остальные (медиана внутри
кармана, не фиксированный порог).

| имя | формула | исходные колонки |
|---|---|---|
| `pocket_volume_per_sasa` | Σ`residue_volume` / Σ`residue_sas_area` по остаткам кармана | `residue_volume`, `residue_sas_area` |
| `pocket_elongation` | span₀ / span₁, где span_k — 5–95-перцентильный размах проекции атомов кармана на k-ю главную ось (PCA) | `pocketness.pdb` |
| `pocket_flatness` | span₁ / span₂ (те же оси) | `pocketness.pdb` |
| `buriedness_q50` | медиана `residue_mean_buriedness` | `residue_mean_buriedness` |
| `apolar_sasa_share` | Σ`sas_area` остатков с гидропатией > 0 / Σ`sas_area` кармана | `residue_type`, `residue_sas_area` |
| `aromatic_share` | доля остатков кармана типа Phe/Trp/Tyr (коды 13, 17, 18) | `residue_type` |
| `hydropathy_rim` | средняя гидропатия Кайта–Дулиттла по `rim` | `residue_type` |
| `ev28_q10` | 10-й перцентиль `residue_mean_ev28` | `residue_mean_ev28` |
| `aromatic_share_rim` | доля ароматических среди `rim` | `residue_type` |
| `depth_q10` | 10-й перцентиль `residue_mean_voromqa_depth` | `residue_mean_voromqa_depth` |
| `hydropathy_core` | средняя гидропатия по `core` | `residue_type` |
| `ev14_q10` | 10-й перцентиль `residue_mean_ev14` | `residue_mean_ev14` |
| `hydropathy_mean` | средняя гидропатия по всему карману (без разбиения на core/rim) | `residue_type` |

Детали:
- Гидропатия — шкала Кайта–Дулиттла (`KYTE_DOOLITTLE`, индекс по `residue_type`, порядок
  кодов алфавитный по трёхбуквенному имени).
- Если у кармана нет остатков в `rim`, `hydropathy_rim` и `aromatic_share_rim` берут
  значение по всему карману.
- Если в `pocketness.pdb` меньше 4 атомов, `pocket_elongation` и `pocket_flatness` равны 0
  (потом стандартизация оставит их в среднем).
- Пустой карман — `ValueError`.
- Ни одна из 13 величин не зависит от лиганда: для одного белка это константа.

## 4. Как значения доходят до сети

```text
arg-файл: --pair_descriptors --descriptor_mlp --descriptor_names=<17 имён>
  -> Dataloader.py: full_catalog_order(config) -> parse_descriptor_token (имя, coarse-спека)
  -> raw_values[имя]: липидные по кандидатам; карманные из protein_descriptor_table
     (chemistry_prior.py, самосохраняется между запусками)
  -> стандартизация (x - mean) / std ТОЛЬКО по train-строкам (train_stats;
     std < 1e-12 заменяется на 1.0)
  -> _descriptor_catalog_tensor [строка-кандидат x len(catalog_order)]
  -> protein_graph.descriptor_catalog_input[idx, candidate_index]
  -> DescriptorMLPHead.forward: index_select(catalog_columns) -> 17 колонок
  -> build_mlp(17, max(m*hiddim, hiddim), hiddim)   # hiddim=8: 17 -> 8m -> 8
  -> Final_Layer (логиты [batch, 2])
```

- Стандартизация train-only, так что значения held-out блоков (в `lipid_subclass`) не
  влияют на mean/std. Это не гарантия отсутствия утечки через сами признаки (см. §5).
- `--descriptor_mlp` и `--descriptors_head` читают один и тот же `descriptor_catalog_input`
  и одни и те же 17 колонок; различается только блок над ними (обычный MLP против
  `NamedDescriptorHead` с общим `Linear(1, dim)` на токен и self-attention).
- Парные признаки (`occupancy`, `volume_fit` и т.п.) в этом наборе **не используются**:
  mlp сам учит взаимодействие липид×карман из конкатенации 4+13.

## 5. Что известно про каждую группу

Числа — из комментариев в коде и `files/pocket_shape_descriptors.md`; η² считался по 9
семействам на 35 белках, пол «нет структуры» ≈ 0.235.

- **Семь family-neutral (5–11):** η² у порога 0.24, отбирались как не отпечаток
  семейства. В этом наборе они задаются явно по имени через `--descriptor_names`, а не
  флагом `--pocket_descriptors_family_neutral`.
- **`hydropathy_core` (η² 0.77), `depth_q10` (0.55), `hydropathy_mean` (0.611):**
  выше порога, то есть близки к метке семейства. `ev14_q10` (0.238) — на пороге.
  Для `ev28_q10` и `aromatic_share_rim` η² записан как «у порога», точного числа в коде
  нет. Они включены осознанно (в `lcs` белок не held-out ось), но в `lipid_subclass`
  защиты от идентичности белка нет: все 13 карманных значений — константы белка, их
  комбинация однозначно определяет белок среди 35.
- **Липидные 1–4:** формальной проверки «отпечаток класса липида» для этих четырёх в
  проекте не проводилось (`descriptor_catalog.md` §1). Единственная связанная находка —
  необъяснённая утечка на `LBP_BPI_CETP` в `descriptors_path`, где четыре липидных токена
  остаются среди неисключённых подозреваемых.

## 6. Что здесь не проверено

- Не пересчитывал η² и корреляции — они взяты из существующих документов.
- Не измерял, насколько каждое из 17 имён отличает блок `lipid_subclass`: связи признак
  → блок (то, что actually отвечает за провалы на PC/PI/Cer) нет.
- Не проверял, что `descriptor_names` в обоих arg-файлах побайтно совпадают, кроме
  беглого сравнения заголовков.
