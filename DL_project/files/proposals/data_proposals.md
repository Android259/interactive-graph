# Предложения по нормализации данных

Цель: перенести искусственные переименования, special cases и скрытые fallback
из runtime-кода в проверяемые данные без изменения pair IDs, sampling, tensor
values и результатов существующих запусков.

## Текущее состояние

- Active interaction table: 11 018 строк, 11 колонок.
- `Unnamed: 0` во всех строках совпадает с исходной позицией строки и фактически
  является неявным `pair_id`.
- В каждой строке ровно одна из колонок `SmileGlobal`/`SmileFragment` содержит
  `"0"`; другая содержит данные. Обе `"0"`: 0 строк. Обе содержат данные: 0 строк.
- 35 protein IDs имеют graphs и ESM3 artifacts.
- CSV/artifact names расходились для четырёх proteins
  (`RBP1→RET1`, `RBP4→RET4`, `RBP5→RET5`, `STARD11→CERT`). **Исправлено:**
  артефакты переименованы под имена из таблицы взаимодействий, rename map удалён,
  колонки `artifact_stem` в registry больше нет.
- ESM3 v1 требовал дополнительного trim для `GM2A` и `PITPNA`. **Исправлено:**
  причиной были MSE-остатки, выброшенные Voronota; графы перегенерированы из
  `data/structures/mse_fixed/`, обрезка сведена к удалению BOS/EOS.
- RBP4 (ранее RET4) несогласован: 174 graph nodes, 175 pocket residues и edge
  endpoint 175, отсутствующий в node table — у остатка 175 разрешён единственный
  атом N. Loader снимает последнюю строку `pocketness.pdb`, рёбра к 175
  отбрасываются с предупреждением.
- Аудит non-isomeric embedding path против реального
  `lipid_SMILES_embedding.pkl`: 11 018/11 018 строк имеют валидный lookup;
  random fallback фактически не используется.
- Аудит canonical lipid SMILES: missing/invalid lipid, требующий фиксированного
  PC fallback, в текущей active таблице не найден.

## 1. Явный `pair_id`

Добавить в производную interaction table явную колонку `pair_id`, равную
текущему `Unnamed: 0`. Первую миграцию выполнять без сортировки и перенумерации.

Это сохраняет:

- Tanimoto alignment;
- GRAB endpoints;
- train/validation/test splits;
- sampling и существующие результаты.

После перехода удалить зависимость loader от позиции строки и временной колонки
`_tanimoto_orig_idx`.

Статус: предложение, не реализовано.

## 2. Единый protein registry

Отменено. Registry (`data/protein_registry.csv` + `dataloader/protein_registry.py`)
существовал и удалён: всё, что он хранил, уже есть в таблице взаимодействий или
перестало быть нужным.

- `artifact_stem` — артефакты четырёх белков переименованы (`RET1→RBP1`, `RET4→RBP4`,
  `RET5→RBP5`, `CERT→STARD11`), имя из `LTPProtein` теперь и есть имя каталога графа
  и префикс эмбеддингов;
- `family` — дублировала колонку `ProteinDomain`, которая у каждого белка принимает
  ровно одно значение (проверено на всех 35, расхождений нет);
- `uniprot_id` — не читался ни одной строкой кода;
- `esm3_v1_extra_trim_pairs` / `esm3_v1_drop_rows` — обрезка сведена к снятию пары
  BOS/EOS, потому что графы всех 35 белков имеют по узлу на каждый остаток
  последовательности (MSE конвертируются в MET до построения графа —
  `preprocessing/convert_mse_to_met.py`).

`ProteinGraphBuilder.protein_family` читает `ProteinDomain` напрямую. Runtime-словари
`familydic`, `Gene_uni`, rename map и `EXTRA_TRIM_PAIRS` в active path не нужны.

Legacy `Dataloader.py` и `tanimoto_Dataloader.py` намеренно не изменены.

Статус: реализовано.

## 3. Нормализованные protein bundles

Создавать один проверенный bundle на protein:

```python
{
    "protein_id": ...,
    "node_ids": ...,
    "x": ...,
    "edge_index": ...,
    "edge_attr": ...,
    "pocket": ...,
    "plm": ...,
}
```

Генератор обязан проверить:

- каждый edge endpoint существует;
- node count == pocket count == embedding rows;
- residue order согласован;
- tensors имеют ожидаемые dtype/shape и finite values.

Loader после этого только читает bundle: без CSV/PDB parsing, glob и runtime
residue remapping.

Статус: частично существует как `protein_graph_tensors.pt`; требуется расширить
до embedding/pocket/alignment manifest.

## 4. RBP4 (ранее RET4)

Исправлять не в loader, а в отдельной версии artifacts:

1. Определить происхождение residue 175.
2. Выбрать единый residue set из исходной структуры.
3. Перегенерировать nodes, edges и pocket из одного set.
4. Запрещать неизвестные edge endpoints вместо преобразования в node 0.
5. Сравнивать исправленный вариант как новую data/model configuration.

Статус: предложение. Нельзя включать в чистый эквивалентный рефакторинг.

## 5. ESM embeddings без runtime trim

Preprocessing должен сохранять residue-only tensor формы
`[number_of_graph_nodes, embedding_dim]`. BOS/EOS и дополнительные historical
tokens удаляются один раз при генерации.

Metadata:

```json
{
  "raw_rows": 180,
  "trim_left": 1,
  "trim_right": 1,
  "output_rows": 178,
  "node_rows": 178,
  "source_hash": "..."
}
```

До переключения loader требуется `torch.equal(new, old_after_runtime_trim)` для
всех 35 proteins.

Статус: предложение.

## 6. Lipid representation

Текущий подтверждённый инвариант позволяет в active dataset выбирать данные
одним условием: если `SmileGlobal == "0"`, берётся `SmileFragment`, иначе
берётся `SmileGlobal`. Ветки для обеих `"0"` и обеих заполненных колонок удалены:
таких строк в active dataset нет.

Долгосрочный формат:

```text
lipids.csv:
lipid_id,representation_mode,status

lipid_variants.csv:
lipid_id,variant_index,canonical_smiles,is_valid,is_fallback
```

Одна SMILES-вариация должна занимать одну строку вместо строки с `;`. Это уберёт
runtime `split(";")`, canonicalization и поиск первого валидного fragment.

Статус: короткое условие реализовано; неиспользуемые проверки удалены; отдельные
lipid tables пока не создавались.

Реализация разделена по режимам: embedding path находится в
`dataloader/lipid_graph_builder.py`, а `lipid_graph_isomers=True` path — в
`dataloader/lipid_isomer_graph_builder.py`.

## 7. Явный fallback status

Предлагалось хранить `valid|missing|invalid|fallback` и `fallback_reason` в
lipid metadata. Аудит показал, что в текущем active dataset fallback не нужен:

- embedding lookup успешен для 11 018/11 018 строк;
- random embedding fallback: 0 строк;
- fixed PC SMILES fallback: 0 строк.

Поэтому materialize fallback rows сейчас не требуется. В будущем появление нового
invalid/missing lipid желательно обнаруживать при preprocessing, но текущий random
и fixed-PC fallback этим изменением не удалялся и не менялся.

Статус: аудит выполнен. `try/except`, random tensor fallback, ветка
`lipid_text == "0"` и связанные state flags удалены из embedding path; ошибки
теперь не скрываются. Флаг `lipid_random_choice` сохранён.

## 8. Tanimoto и GRAB по явному `pair_id`

Сохранить `tanimoto_pair_ids.npy`; GRAB уже использует поля
`source_pair_id,target_pair_id`. Все cross-file joins должны выполняться по
значению ID, а не по предположению об одинаковом порядке строк.

Статус: предложение.

## Безопасная последовательность миграции

1. Создать производный `data/normalized_v1/`, не изменяя исходные artifacts.
2. Сохранить текущие pair IDs и row order.
3. Materialize текущие rename/trim/SMILES decisions.
4. Сравнить old/new samples, splits и tensors через `torch.equal`.
5. Сравнить Tanimoto positions и GRAB coefficients.
6. Выполнить одинаковый deterministic 1-epoch testmode old/new.
7. Только после совпадения переключить active loader.
8. Scientific corrections, включая RBP4, выпускать отдельно как
   `normalized_v2`, поскольку они могут изменить accuracy.
