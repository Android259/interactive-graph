# geometric_edge*: усиление взаимодействия и регуляризация — три непроверенных изменения

Три отдельных, независимых изменения `architecture`/`training` кода этой сессии,
каждое со своим argfile, ни одно ещё не прогонялось на кластере. Ориентир — тот
же baseline `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
bilinear_norm`, что и в [edge_geometry_pruning_rbf6_orient_raw3.md](edge_geometry_pruning_rbf6_orient_raw3.md).

## 1. `--bilinear_weight_decay` — точечная регуляризация именно Bilinear-слоя

**Диагноз, откуда это взялось.** `--bilinear_pooled_norm`
([architecture/final_layer.py:430-439](../architecture/final_layer.py#L430-L439)) —
не регуляризация, а `LayerNorm(affine=False)` на пуленных lip/prot-векторах прямо
перед `torch.nn.Bilinear`. Причина существования флага — в его же комментарии:
`--pool_type=add` суммирует РАЗНОЕ число узлов на карман/липид, так что масштаб
пуленного вектора гуляет от сэмпла к сэмплу независимо от нормировки узлов внутри
CrossAttention.

Сравнение пары конфигов, отличающихся РОВНО этим одним флагом
(`geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion` vs
`..._bilinear_norm`), по `metrics_summary.csv`, 7 семей × 5 сидов:

- Без нормы: `final_train_balanced_accuracy` часто на уровне случайности
  (0.50–0.62), тестовый loss иногда взрывается до 12–93 (пример: `LBP_BPI_CETP`
  seed4: 92.96) — редкий сэмпл с большим карманом/липидом даёт выброс масштаба.
- С нормой: train BA скачет до 0.75–0.88, loss стабилен (0.6–1.1) — сеть
  впервые может реально доучить билинейное взаимодействие.
- Цена: `mean_train_valid_gap` вырастает на порядок (было ~0.00–0.05, часто
  отрицательное; стало 0.10–0.28) — норма чинит взрыв масштаба, но тем самым
  ВПЕРВЫЕ даёт сети возможность переобучиться на train.
- Sensitivity/specificity разрыв норма НЕ устраняет, а переворачивает
  направление: без нормы коллапс к «да» (`GLTP` seed1: sens=1.0/spec=0.0), с
  нормой — к «нет» (`lipocalin` seed1: sens=0.0/spec=1.0).

**Предложение.** `--dropout` действует только ПОСЛЕ `self.bilinear` (в
классификаторе `self.binar`), на сам Bilinear-слой не давит вообще. `--weight_decay`
действует на него с той же силой, что и на все остальные слои. Но в коде уже
есть нетронутый, никогда не запускавшийся рычаг именно под это —
`--bilinear_weight_decay=<N>` ([training/read_configuration.py:262](../training/read_configuration.py#L262),
своя optimizer-группа для `self.bilinear.weight`/`.bias`,
[training/new_train.py:356-357](../training/new_train.py#L356-L357)), по умолчанию
равен общему `--weight_decay`. Проверено по `metrics_summary.csv` — ни разу не
использовался с ненулевым значением.

**Оговорка**: часть train-valid разрыва — cold-split по семье (систематический
сдвиг), а не шум; регуляризация может ужать и полезную часть сигнала вместе со
спурной. Не гарантированное решение, требует прогона.

**argfile**: `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_bilinear_wd01`
(`--bilinear_weight_decay=0.1`, 10× общего `--weight_decay=0.01`).

## 2. `--cross_attention_forced_interaction` — форсированное взаимодействие ВМЕСТО residual-суммы cross-attention

**Диагноз.** Cross-attention в geometric_edge* — soft-attention, взвешенная
СУММА чужих value-векторов, никогда не произведение своего и чужого содержимого
— это дословно написано в комментарии `architecture/cross_attention.py:61-67`
самого файла. Skip-путь существует всегда: если внимание вырождается к
равномерному/почти нулевому, `lip = lip + lip_outs` всё равно пропускает
собственное содержимое узла почти без изменений.

**Что уже пробовано и не помогло**: `--node_bilinear_fusion` — тот же класс
`ForcedInteraction`, что и здесь, но как ДОПОЛНИТЕЛЬНЫЙ канал (отдельный пуленный
вектор, конкатенируется в `common_out`), не замена самого cross-attention update.
Результат из более раннего анализа этой сессии: никакого улучшения BA/gap,
втрое больше замороженных эпох на `LBP_BPI_CETP`.

**Новое, непроверенное изменение**: не добавлять параллельный канал, а заменить
сам residual-update в `CrossAttention.finish()`
([architecture/cross_attention.py](../architecture/cross_attention.py)) —
`lip = lip + lip_outs` → `lip = lip + ForcedInteraction(lip, lip_outs)` (и
аналогично для `prot`). Skip-путь исчезает: обновление узла структурно обязано
зависеть и от собственного содержимого, и от того, что притянуло внимание от
партнёра — не добавочный термин рядом с непринудительным, а замена самого
механизма.

**argfile**: `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_cross_forced`
(`--cross_attention_forced_interaction`).

## 3. `--protein_descriptors=<парные имена>` — липид-зависимый broadcast на ноды белка

**Находка**: `--protein_descriptors=`/`architecture/protein_encoder.py::
expand_named_protein_descriptors` не ограничивает список именами белковой
стороны каталога — читает ЛЮБОЕ имя `DESCRIPTOR_CATALOG` по индексу колонки,
включая `PAIR_DESCRIPTOR_NAMES`. Проверено напрямую (`read_configuration` +
реальный forward/backward — не падает, не отвергается валидацией).

**Почему это меняет поведение принципиально, не просто «другие числа»**: до
сих пор каждое имя в `--protein_descriptors=` было константой НА БЕЛОК —
одно и то же число независимо от того, с каким липидом его сравнивают в этой
строке. Парное имя (`volume_fit`, `buriedness_match`, ...) зависит от
КОНКРЕТНОГО партнёра в каждой строке — один и тот же белок получает разные
входные признаки узлов в зависимости от того, какой липид оценивается. Это
форсирует learning message passing быть кондиционированным на липид с первого
слоя GNN, раньше, чем отработает cross-attention — более фундаментальная версия
«обязательного взаимодействия», чем правка №2 выше.

**Набор**: 6 из 7 текущих family-neutral дескрипторов заменены на их парные
формы (`pocket_volume_per_sasa`→`volume_fit`, `pocket_elongation`→
`elongation_shape_match`, `pocket_flatness`→`flatness_shape_match`,
`buriedness_q50`→`buriedness_match`, `aromatic_share`→`aromatic_contact`,
`hydropathy_rim`→`hydropathy_rim_match`); `apolar_sasa_share` оставлен как есть
— готовой парной формы под него в каталоге нет.

**argfile**: `geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pair_broadcast`.

## Три новых pair-дескриптора, на которых держится №3 (и часть thematical_paths-варианта)

Реализованы в `dataloader/pair_descriptors.py::PAIR_DESCRIPTOR_NAMES`
(формулы — `pair_descriptor_value`, тесты — `tests/test_descriptor_catalog.py`),
задокументированы в [descriptor_catalog.md](descriptor_catalog.md) §5 и
литературно обоснованы в [protein_lipid_binding_family_literature.md](protein_lipid_binding_family_literature.md):
`hydropathy_rim_match`, `elongation_shape_match`, `flatness_shape_match`.
Побочный найденный и исправленный баг: тренировочный путь
(`dataloader/Dataloader.py`) строил липидный словарь для `pair_descriptor_value`
вручную, без `npr1`/`npr2` — новые дескрипторы упали бы `KeyError` при первом
реальном запуске; починено по образцу уже существовавшей обработки `tail_count`.

## Статус кэша (для памяти, не для действия)

Правка `pair_descriptors.py` меняет SHA256-отпечаток файла
(`dataloader/pair_descriptor_cache.py::_code_fingerprint`), так что
`data/pair_descriptor_cache_deterministic_<hash>.json` пересоберётся под новым
именем при следующем запуске. Пересборка НЕ означает пересчёт `npr1`/`npr2` с
нуля — `_previous_cache_values`/`seed_entry` (`pair_descriptor_cache.py:121-171`)
переносят уже известные по каждому SMILES измерения из самого свежего старого
кэш-файла; пересчитывается только то, что реально новое. Новые pair-дескрипторы
не добавляют новых `_MEASURES`, так что для них пересчитывать нечего — только
copy под новое имя файла.
