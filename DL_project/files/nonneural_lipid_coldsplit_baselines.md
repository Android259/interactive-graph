# Ненейронные baseline'ы на --lipid_coldsplit: Kron-RLS vs HistGradientBoosting

Снимок на 2026-09-17. Задача: известный белок (никогда не исключается) × новый липид
(head-group класс исключён из train) — то, что `--lipid_coldsplit` реально проверяет.
Источники: `analysis/kronrls_baseline.py`, `analysis/gbm_baseline.py`,
`training/pair_baseline_common.py`, `preprocessing/build_tanimoto_headgroup.py`.

## TL;DR

**Kron-RLS выигрывает у HistGradientBoostingClassifier с большим отрывом на всех
метриках.** Headgroup-only Tanimoto лучше whole-molecule Tanimoto для Kron-RLS, но
как доп. фича не помогает GBM. `--positive_weight` у Kron-RLS — доказанный
математически no-op (детали внизу), реальное перевзвешивание классов есть только у
GBM (`class_weight="balanced"`), но оно не спасает: GBM всё равно хуже.

| модель | конфиг | test BA | test F1 | test AUC | pair AUC |
|---|---|---|---|---|---|
| Kron-RLS | protunion14 × tanimoto | 0.607 | 0.541 | 0.616 | 0.610 |
| **Kron-RLS** | **protunion14 × tanimoto_headgroup** | **0.619** | **0.562** | 0.592 | **0.636** |
| GBM | best hparams, без similarity-фичи | 0.554 | 0.517 | 0.514 | 0.547 |
| GBM | best hparams + tanimoto_headgroup фича | 0.545 | 0.415 | 0.464 | 0.521 |

(5 сидов, 4 группы LIPID_COLDSPLIT_SETS: sphingolipids/phosphorus_free/choline/anionic;
valid/test пересэмплированы до 1:2 pos:neg, порог подобран на valid по BA.)

Команды воспроизведения:
```bash
# Kron-RLS, лучшая связка (protunion14 pocket-дескрипторы + headgroup Tanimoto)
python3 analysis/kronrls_baseline.py --split_mode lipid_coldsplit \
    --protein_kernel pocket_subset \
    --protein_descriptor_names=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,depth_q10,hydropathy_core,pocket_extent \
    --lipid_kernel tanimoto_headgroup --lambda_grid 0.01,0.1,1,10,100

# GBM, лучшие гиперпараметры из свипа
python3 analysis/gbm_baseline.py --max_depth 6 --min_samples_leaf 20 --learning_rate 0.1
```

## По группам (Kron-RLS, tanimoto_headgroup)

| группа | test BA |
|---|---|
| sphingolipids | 0.774 |
| choline | 0.590 |
| anionic | 0.587 |
| phosphorus_free | 0.526 (у шанса) |

`phosphorus_free` — стабильно слабая группа у обеих моделей, во всех конфигурациях.

## Почему Kron-RLS сильнее GBM здесь

GBM — построчный классификатор, сплитует по raw-значениям дескрипторов; в группе
LIPID_COLDSPLIT_SETS всего 3-17 уникальных белков (`n_proteins` в отчёте) — слишком
мало точек для дерева, чтобы найти полезные пороги по белковой стороне. Kron-RLS
вместо жёстких сплитов использует гладкое similarity-ядро — на таком масштабе (35
белков всего) это выигрывает. Полный свип по гиперпараметрам GBM (24 конфига ×
max_depth∈{2,3,6} × min_samples_leaf∈{5,20} × learning_rate∈{0.05,0.1} ×
train_negatives_per_positive∈{0,2}, 3 сида) — лучший результат BA=0.551, F1=0.524,
AUC=0.512, все depth=2/3 конфиги хуже (BA 0.51-0.54). Прорезание train до 1:2
(`--train_negatives_per_positive=2`) почти всегда хуже полного train.

## Headgroup-only Tanimoto: новый лайвер, но только для Kron-RLS

`preprocessing/build_tanimoto_headgroup.py` уже строил артефакт
(`data/Tanimoto_headgroup_compact_*`, acyl-хвосты отрезаны, оставлен только head
group). Добавлена `species_headgroup_tanimoto_similarity` +
`--lipid_kernel tanimoto_headgroup` в `training/pair_baseline_common.py` /
`analysis/kronrls_baseline.py`. Для Kron-RLS это явный выигрыш (+0.012 BA, +0.021
F1, +0.026 pair AUC против whole-molecule tanimoto). Как ДОБАВОЧНАЯ фича в GBM
(`--lipid_similarity_feature tanimoto_headgroup`, leak-safe leave-one-out на train
через `dataloader.chemistry_prior.null_scores_leave_one_row_out`) — не помогает и
даже роняет F1/AUC: структурные дескрипторы GBM уже неявно кодируют то же самое.

## `--positive_weight` (Kron-RLS): доказанный no-op, не просто слабый рычаг

`two_step_kronrls`'s `A = (Kp+λpI)⁻¹Y(Kl+λlI)⁻¹` — точное решение объектива, где Y
входит **только линейно** (доказано через собственные разложения Kp⊗Kl, см.
докстринг `analysis/kronrls_baseline.py`). Раз Y бинарная (0/1), любой скаляр на
позитивных клетках (негативы 0×W=0 не меняются) — это буквально глобальное
растяжение ВСЕЙ матрицы A и всех предсказаний, что не может изменить ни AUC, ни
BA/F1 при адаптивном пороге. Настоящее перевзвешивание классов внутри Kron-RLS
математически невозможно без смены оценщика (нужен residual-form примал с
итеративным CG-решателем, который НЕ сводится к текущей замкнутой форме при W≡1 —
т.е. это другая, невалидированная модель, а не фикс существующей). Флаг оставлен в
коде задокументированным как мёртвый (для честности), не удалён.

## Что реально работает / инфраструктура

- `analysis/kronrls_baseline.py --split_mode lipid_coldsplit` — точная реконструкция
  сплита (`preprocessing.lipid_marginal_baseline.lipid_split`), вынесена в
  `training.pair_baseline_common.cold_split_pools` (используется обоими baseline'ами).
- valid/test пересэмплированы до `negatives_per_positive=2`
  (`training.pair_baseline_common.balance_pool_negatives`) — та же пропорция, на
  которой реально оценивается сеть (`dataloader/Dataloader.py`'s
  `_sample_interactions` балансирует working set ДО сплита), а не raw ~6-7% held-out
  блока. Train у Kron-RLS остаётся полным (нужно для complete-rectangle замкнутой
  формы); у GBM train можно прорезать (`--train_negatives_per_positive`), но это не
  помогает.
- Порог для BA/F1 подбирается на valid (`best_threshold_for_metric`,
  `--threshold_metric {ba,f1}`), никогда на test.
- `analysis/gbm_baseline.py` — новый, `HistGradientBoostingClassifier` по строкам
  (protein_pocket_features ⊕ explicit_lipid_features), с реальным
  `class_weight="balanced"` и опциональной similarity-фичей.

## Вывод

Kron-RLS (protunion14 pocket-дескрипторы × headgroup-only Tanimoto) — лучший из
проверенных ненейронных baseline'ов для сценария "известный белок × новый липид":
test BA 0.62, F1 0.56, pair AUC 0.64. GBM с любыми проверенными гиперпараметрами
и с/без химической similarity-фичи остаётся заметно слабее (test BA ≤0.55) на этом
масштабе данных (35 белков, 3-17 на группу).
