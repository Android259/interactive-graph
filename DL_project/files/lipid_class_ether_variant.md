# Вариант классификации с отдельным -O классом, и аудит на ошибки типа CL

## Аудит: сверка с реальной Figure 3a (files/Reuter.pdf, стр. 22)

Проверил файл напрямую (рендер страницы в 400 dpi), построчно транскрибировал Y-ось
(29 строк) и сверил с таблицей files/data_source.md. Дополнительно пересчитал species
count каждого проектного класса напрямую по `data/Processed_Negative_Interaction_
Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv` и сверил все 23
числа в таблице data_source.md — **все 23 совпали с живой таблицей ровно**, ошибок в
числах нет.

Найдено и исправлено (в этом заходе, в дополнение к CL-строке, исправленной раньше):

- **CL отсутствовал в таблице "Подгруппы подклассов"** ([files/data_source.md](data_source.md),
  раздел "Подгруппы подклассов") — все 6 подгрупп в сумме давали 28 подклассов вместо
  29 реальных строк оси Y. Добавлен в Glycerophospholipids (и по позиции на оси —
  между BMP и DAG, и по химии — cardiolipin = bis(phosphatidyl)glycerol, ближе всего к
  PG/BMP).

Больше расхождений не нашёл: все 29 строк Figure 3a учтены (23 самостоятельных +
PIPs/Sterol отсутствуют в датасете + 4 эфирные/неоднозначные строки PC-O/PE-O/LPE-O/
PG-BMP задокументированы как слитые с соответствующим родительским классом).

## Новый вариант: -O как отдельный класс

Добавлена функция `dataloader/lipid_classes.ether_split_class_series` (и
`ether_split_head_group_class` для одной записи) — **аддитивно**, действующая
`lipid_class_series`/`csv_classes` не менялась, ни один сплит не переключён на новую
схему.

Единственные 3 класса, где вообще есть смесь эфирных и диацильных видов (проверено
по живой таблице):

| Старый класс | species (старый) | -> новый класс (не-эфир) | species | -> новый класс (эфир) | species | positives (эфир) | белков с позитивом (эфир) |
|---|---:|---|---:|---|---:|---:|---:|
| Phosphatidylcholine | 76 | Phosphatidylcholine | 45 | Phosphatidylcholine-O | 31 | 63 | 11 |
| Phosphatidylethanolamine | 24 | Phosphatidylethanolamine | 22 | Phosphatidylethanolamine-O | 2 | 2 | 1 |
| Lysophosphatidylethanolamine | 10 | Lysophosphatidylethanolamine | 9 | Lysophosphatidylethanolamine-O | 1 | 1 | 1 |

Остальные 20 задокументированных классов (PG, HexCer, SM, Cer, FA, PA, CerP, CL, TAG,
PI, LPC, LPG, PS, Hex2Cer, DAG, SHexCer, PGP, BMP, VA, FAL) — все виды одного типа
(либо все диацил, либо изначально нет эфирной формы), split их не трогает.

Неоднозначные (semicolon-joined) записи разрешаются как раньше (`AMBIGUOUS_CLASS_
RESOLUTION`), а -O присваивается только если СЕГМЕНТ, давший победивший класс, сам
несёт маркер `(O-` — не по наличию `(O-` где-либо в записи. Пример: `"Lysophosphatidyl-
ethanolamine (18:1);Phosphatidylethanolamine (O-18:1)"` разрешается в LPE (структурно
проверено раньше), и LPE-сегмент маркера `(O-` не несёт — остаётся plain LPE, а не
LPE-O.

## Где сплиты придётся менять с одного класса на два (сам сплит не меняется)

Если когда-нибудь переключить дефолт на `ether_split_class_series`, эти места молча
исключат МЕНЬШЕ видов, чем раньше, если не добавить туда `-O` явно:

| Место | Сейчас исключает (1 класс) | Нужно будет исключать (2 класса), чтобы набор видов не изменился |
|---|---|---|
| `dataloader/sampler.py` `LIPID_COLDSPLIT_SETS["choline"]` | `Phosphatidylcholine` | `Phosphatidylcholine` + `Phosphatidylcholine-O` |
| `dataloader/lipid_subclass_blocks.py` `FIG3_SUBCLASS_BLOCKS` — блок `"PC"` | `PC` (через article classification, = весь Phosphatidylcholine) | `PC` + `PC-O` |
| `dataloader/lipid_subclass_blocks.py` `FIG3_SUBCLASS_BLOCKS` — блок `"PE"` | `PE` (= весь Phosphatidylethanolamine) | `PE` + `PE-O` |
| `dataloader/lipid_subclass_blocks.py` `FIG3_SUBCLASS_BLOCKS` — блок `"LPC+LPE+LPG"` | `LPC+LPE+LPG` (LPE-часть = весь Lysophosphatidylethanolamine) | `LPC+LPE+LPE-O+LPG` |

`LIPID_COLDSPLIT_SETS`'s остальные 3 набора (`sphingolipids`, `phosphorus_free`,
`anionic`) и `FIG3_SUBCLASS_BLOCKS`'s `PA`, `PI`, `PS+PGP+DAG+TAG` не задевают ни один
из трёх смешанных классов — не требуют изменений.

Никакой из этих файлов в этом заходе не менялся — эквивалентность выше нужна, только
если решите реально переключить дефолт на -O-раздельную схему.
