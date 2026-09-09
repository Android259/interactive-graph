"""Насколько близка к вынесенной химии та, на которой учат отрицательные примеры.

Зачем это измерение
-------------------
`--balanced_lipid_classes` стоит около -0.07 внутрибелковой парной AUC на двух читаемых
наборах, и знак воспроизводится на двух независимых наборах оценочных строк
(files/geometric_edge_and_solo_next_architecture.md 8.6). Гипотеза 8.7 объясняет это так:
флаг выравнивает отрицательные по ОСТАВШИМСЯ классам, то есть отбирает их у самых
многочисленных и отдаёт редким; самые многочисленные из оставшихся -- как правило те, что
химически БЛИЖЕ всего к вынесенному набору. А внутрибелковая метрика на тесте требует
различать молекулы одного класса, чему учат именно контрасты с близкой химией.

Гипотеза проверяется без обучения: собрать обучающий кадр обоими сэмплерами и посчитать,
насколько близки к вынесенному набору отрицательные строки, которые в нём оказались.

Что считается
-------------
Для каждого (набор, сид) и каждого сэмплера:
  * отрицательные строки обучающего кадра (после выноса классов, как в
    `_split_interactions`);
  * для каждой -- максимальное Tanimoto её вида липида к любому виду ИЗ ВЫНЕСЕННОГО
    набора (species x species, max по кандидатам -- `chemistry_prior.species_similarity`,
    та же редукция, которой пользуется загрузчик);
  * среднее этого максимума и доля строк выше порогов.

Сэмплеры берутся ровно те же, что и в обучении (dataloader/sampler.py):
`split_and_sample_lipid_class_balanced_interactions` против
`split_and_sample_protein_balanced_interactions` -- вторая стоит на линии без флага,
поскольку `--balanced_proteins` включён и там, и там.

Reads only: читает таблицу взаимодействий и матрицу Tanimoto, ничего не пишет и не учит.

Примеры
-------
    python analysis/negative_chemistry_proximity.py
    python analysis/negative_chemistry_proximity.py --sets choline --seeds 0,1,2,3,4
"""

import argparse
import os
import sys

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, PROJECT_ROOT)

from dataloader.chemistry_prior import species_similarity  # noqa: E402
from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from dataloader.sampler import (  # noqa: E402
    LIPID_COLDSPLIT_SETS,
    split_and_sample_lipid_class_balanced_interactions,
    split_and_sample_protein_balanced_interactions,
)
from preprocessing.lipid_marginal_baseline import lipid_class_series, lipid_split  # noqa: E402


def sampled_frame(csv, sampler, seed, ratio):
    import pandas as pd
    if sampler == "lipid_class_balanced":
        true_rows, false_rows = split_and_sample_lipid_class_balanced_interactions(
            csv, seed, ratio=ratio
        )
    else:
        true_rows, false_rows = split_and_sample_protein_balanced_interactions(
            csv, seed, ratio=ratio
        )
    return pd.concat([true_rows, false_rows])


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--sets", default=",".join(sorted(LIPID_COLDSPLIT_SETS)))
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--ratio", type=int, default=2,
                        help="negatives_per_positive, как в конфигах линии (по умолчанию 2)")
    parser.add_argument("--thresholds", default="0.4,0.5,0.6,0.7")
    args = parser.parse_args()

    import pandas as pd
    data_dir = os.path.join(PROJECT_ROOT, "data")
    csv = pd.read_csv(interaction_csv_path(data_dir + "/"))
    similarity, index = species_similarity(csv, data_dir)
    classes = lipid_class_series(csv).str.lower()
    species_all = csv["FullIdentityOfLipid"]
    thresholds = [float(t) for t in args.thresholds.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]

    print(f"ratio={args.ratio} | сидов {len(seeds)} | порог(и) {thresholds}\n")
    header = (f"{'набор':16}{'сэмплер':22}{'отриц.':>8}{'ср. max Tanimoto':>18}"
              + "".join(f"{'>=' + str(t):>9}" for t in thresholds))
    print(header)
    print("-" * len(header))

    for set_name in args.sets.split(","):
        held_classes = {name.lower() for name in LIPID_COLDSPLIT_SETS[set_name]}
        held_species = sorted({
            name for name, klass in zip(species_all, classes) if klass in held_classes
        })
        held_columns = [index[name] for name in held_species if name in index]
        rows = {}
        for sampler in ("protein_balanced", "lipid_class_balanced"):
            means, shares, counts = [], {t: [] for t in thresholds}, []
            for seed in seeds:
                frame = sampled_frame(csv, sampler, seed, args.ratio)
                train = lipid_split(frame, LIPID_COLDSPLIT_SETS[set_name], seed)[0]
                negatives = train[train["Interaction"] != 1]
                values = []
                for name in negatives["FullIdentityOfLipid"]:
                    position = index.get(name)
                    if position is None:
                        continue
                    values.append(similarity[position, held_columns].max())
                values = np.asarray(values, dtype=np.float32)
                if values.size == 0:
                    continue
                means.append(float(values.mean()))
                counts.append(int(values.size))
                for t in thresholds:
                    shares[t].append(float((values >= t).mean()))
            rows[sampler] = (means, shares, counts)
            line = (f"{set_name:16}{sampler:22}{int(np.mean(counts)):>8}"
                    f"{np.mean(means):>12.3f} ±{np.std(means) / max(len(means) - 1, 1) ** 0.5:.3f}")
            for t in thresholds:
                line += f"{np.mean(shares[t]):>9.3f}"
            print(line)
        base_means = np.array(rows["protein_balanced"][0])
        flag_means = np.array(rows["lipid_class_balanced"][0])
        delta = flag_means - base_means
        sem = delta.std() / max(len(delta) - 1, 1) ** 0.5
        line = f"{'':16}{'Δ (флаг − без него)':22}{'':>8}{delta.mean():>+12.3f} ±{sem:.3f}"
        for t in thresholds:
            d = np.array(rows["lipid_class_balanced"][1][t]) - np.array(rows["protein_balanced"][1][t])
            line += f"{d.mean():>+9.3f}"
        print(line + "\n")


if __name__ == "__main__":
    main()
