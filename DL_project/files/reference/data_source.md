# Источник данных о взаимодействиях LTP-липид

Все positive-строки интеракционной таблицы (`data/LTP-lipid_interaction.csv`,
исходный источник `Processed_Negative_Interaction_*` артефактов, которые реально
читает `dataloader/Dataloader.py`) взяты из:

**Titeca, K., Chiapparino, A., Türei, D., Zukowska, J., van Ek, L., Moqadam, M.,
Triana, S., Nielsen, I.Ø., Gehin, C., Maeda, K., Alexandrov, T., Saez-Rodriguez, J.,
Reuter, N., Hennrich, M.L., Gavin, A.-C.**
*"A system-wide analysis of lipid transfer proteins delineates lipid mobility in
human cells"*, bioRxiv, 2023.
DOI: [10.1101/2023.12.21.572821](https://doi.org/10.1101/2023.12.21.572821)

Работа комбинирует биохимические, липидомные и вычислительные методы, чтобы
охарактеризовать LTP-lipid комплексы (собранные in cellulo и in vitro) — источник
связей белок(LTP)×липид с указанием specificity по головной группе и жирным
кислотам, на семи белковых семействах (CRAL-TRIO, GLTP, IP_trans, LBP_BPI_CETP,
START, lipocalin, scp2), которые используются в этом проекте как `ProteinDomain`.

Головная группа и цепь липида аннотируются через LIPID MAPS REST API
(`data/lipid_maps_fetch.py`) для получения SMILES из масс-спектрометрических
данных (Conroy et al., *LIPID MAPS: update to databases and tools for the
lipidomics community*, Nucleic Acids Research, 2023,
DOI: [10.1093/nar/gkad896](https://doi.org/10.1093/nar/gkad896)).

Уже процитировано в `Report DL architecture FE LATEX/artigo.tex:101`
(`\cite{acg}`) и `refs.bib` (`@article{acg, ...}`) — эта заметка просто
дублирует ссылку в `files/`, чтобы источник данных был виден без открытия LaTeX.

Полный текст лежит в `files/literature/Reuter.pdf`.

## Сокращения липидов из Figure 3 статьи -> названия в проекте

Figure 3a (стр. 22 PDF) даёт ось Y LTP-lipid subclass матрицы -- это и есть
официальные сокращения источника. Сопоставление с `csv_classes()`/
`lipid_class_series()` (голова класса `FullIdentityOfLipid` в этом проекте) —
таблица `data/fig3a_subclass_correspondence.csv` (колонки `article_subclass`,
`full_name`, `project_classes` — класс(ы) этого проекта через `;`, пусто для
двух подклассов без видов в данных, `species_count`). Эта же таблица — то, что
реально читает `preprocessing/classify_lipids_by_article.py` (раньше был
хардкоженный словарь в коде, теперь один файл вместо двух копий); она пишет
`data/lipid_article_classification.json` (`{FullIdentityOfLipid: подкласс}`).

Итого 283 вида на 23 подкласса статьи (2 подкласса статьи, PIPs и Sterol, в
данных этого проекта не встречаются — пустая колонка `project_classes`).
`PG/BMP` (неоднозначная строка PG или BMP в самой статье) в проекте не является
отдельной категорией — `csv_classes()` уже разрешает такие
`FullIdentityOfLipid` (`"Bismonoacylglycerolphosphate (x);Phosphatidylglycerol (x)"`)
в один канонический класс до классификации. `CL` у статьи — своя строка и на
Figure 2, и на Figure 3a (проверено напрямую по странице 22 PDF, реальные
данные под CRAL-TRIO).

Ось X Figure 3a (белковые семейства): CRAL-TRIO, GLTP, PITP, START, OSBP, BPI,
ML, Lipocalin, SCP2 -- в проекте `ProteinDomain`: PITP -> `IP_trans`, BPI/ML ->
объединены в `LBP_BPI_CETP`, остальные пять названы одинаково.

## Подгруппы подклассов (по соседству строк оси Y Figure 3a)

Порядок строк на оси Y Figure 3a уже группирует соседние структурно родственные
подклассы -- разбиение на 6 подгрупп по этому соседству:

| Подгруппа | Подклассы статьи | Общий признак |
|---|---|---|
| Sphingolipids | Cer, CerP, HexCer, Hex2Cer, SHexCer, SM | сфингоидный backbone (керамид-производные) |
| Free acyls | FA, FAL | свободная жирная кислота/спирт, без глицеринового backbone |
| Lysophospholipids | LPC, LPE, LPE-O, LPG | один ацильный хвост (моноацил) |
| Glycerophospholipids | PA, PC, PC-O, PE, PE-O, PI, PIPs, PS, PGP, PG, PG/BMP, BMP, CL | диацилглицерофосфат-backbone, различаются головной группой (CL — bis(phosphatidyl)glycerol, ближе всего к PG/BMP и по химии, и по позиции на оси Y) |
| Neutral glycerolipids | DAG, TAG | без фосфатной головной группы |
| Прочее | Sterol (ST), VA | структурно не глицеролипиды (стерольное кольцо / изопреноид) |

## `--excluded_lipids` понимает подклассы статьи

`scripts/run_cron.py`/`scripts/run_gbm.py`'s `--excluded_lipids` принимает не
только точные `FullIdentityOfLipid` (`"Phosphatidylcholine (34:1)"`) и классы
проекта (`"Phosphatidylcholine"`), но и сокращения из таблицы выше
(`"PC"`, `"Cer"`, `"HexCer"`, ...), регистронезависимо — раскрывается в
соответствующий набор видов через `data/lipid_article_classification.json`
(`training.pair_baseline_common.resolve_excluded_lipids`). Например:

```bash
python3 scripts/run_cron.py --excluded_lipids=Cer --no_logs ...
```
