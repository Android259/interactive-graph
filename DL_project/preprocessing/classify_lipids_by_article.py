#!/usr/bin/env python3
"""Map lipid species to the article's subclass scheme.

Use data/fig3a_subclass_correspondence.csv to map project classes to subclasses
from Titeca et al., Figure 3a, doi:10.1101/2023.12.21.572821.
See files/reference/data_source.md for the mapping rationale.

Read species classes with csv_classes(). Write data/lipid_article_classification.json
as {FullIdentityOfLipid: article subclass} for the interaction table's species.

    python3 preprocessing/classify_lipids_by_article.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from training.pair_baseline_common import csv_classes  # noqa: E402

CORRESPONDENCE_CSV = "unpreprocessed_files/fig3a_subclass_correspondence.csv"


def load_project_class_to_article_subclass(data_dir: str) -> dict[str, str]:
    """Read the correspondence CSV; reject project classes assigned to multiple subclasses."""
    path = os.path.join(data_dir, CORRESPONDENCE_CSV)
    mapping: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            subclass = row["article_subclass"]
            for project_class in row["project_classes"].split(";"):
                project_class = project_class.strip()
                if not project_class:
                    continue
                if project_class in mapping and mapping[project_class] != subclass:
                    raise ValueError(
                        f"{CORRESPONDENCE_CSV}: project class {project_class!r} is "
                        f"listed under both {mapping[project_class]!r} and {subclass!r}"
                    )
                mapping[project_class] = subclass
    return mapping


def classify(table: pd.DataFrame, data_dir: str) -> dict[str, str]:
    """{FullIdentityOfLipid: article subclass}, one entry per distinct species."""
    project_class_to_article_subclass = load_project_class_to_article_subclass(data_dir)
    classes = csv_classes(table)
    species_class = (
        table.assign(_class=classes)
        .drop_duplicates("FullIdentityOfLipid")
        .set_index("FullIdentityOfLipid")["_class"]
    )
    unmapped = sorted(set(species_class.unique()) - set(project_class_to_article_subclass))
    if unmapped:
        raise ValueError(
            f"classify_lipids_by_article: no article subclass mapping for project "
            f"class(es) {unmapped} -- add them to {CORRESPONDENCE_CSV} "
            "(see files/reference/data_source.md's own table) before running this again"
        )
    return {
        species: project_class_to_article_subclass[project_class]
        for species, project_class in species_class.items()
    }


def main() -> None:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    table = pd.read_csv(interaction_csv_path(data_dir))
    mapping = classify(table, data_dir)

    out_path = os.path.join(data_dir, "lipid_article_classification.json")
    with open(out_path, "w") as handle:
        json.dump(mapping, handle, indent=2, ensure_ascii=False, sort_keys=True)

    counts = pd.Series(mapping).value_counts()
    print(f"classified {len(mapping)} species into {len(counts)} article subclasses:")
    print(counts.to_string())
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
