#!/usr/bin/env python3
"""Classify this project's lipid species into Titeca et al. 2023's own LTP-lipid
subclass scheme (Cer, PC, PE, PIPs, ...), Figure 3a of

    Titeca et al., "A system-wide analysis of lipid transfer proteins delineates
    lipid mobility in human cells", bioRxiv 2023, doi:10.1101/2023.12.21.572821

-- the paper this project's own interaction table (data/LTP-lipid_interaction.csv)
comes from (files/reference/data_source.md). The project-class -> article-subclass
mapping is read from data/fig3a_subclass_correspondence.csv ("project_classes", a
";"-joined list of this project's class names per article subclass; empty for the two
subclasses -- PIPs, Sterol -- this project's data has no species in), not hand-copied
here, so the two cannot drift apart. files/reference/data_source.md documents the
reasoning for each row (why PC-O/PE-O fold into PC/PE, the PG/BMP merge, ...), not
repeated here.

Reads csv_classes(table) (training.pair_baseline_common, the same head-group class
every --lipid_coldsplit/--excluded_lipids path already uses) per species, not per
row -- ambiguous semicolon-joined FullIdentityOfLipid entries (multiple candidate
head groups for one recorded species) are already collapsed to one canonical class
by that function, so this script does not re-decide ambiguity itself.

Writes data/lipid_article_classification.json: {FullIdentityOfLipid: article
subclass}, one entry per distinct species in the table (positive and negative rows
alike -- classification is a property of the lipid, not of the label).

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

CORRESPONDENCE_CSV = "fig3a_subclass_correspondence.csv"


def load_project_class_to_article_subclass(data_dir: str) -> dict[str, str]:
    """{this project's class name: article subclass}, from the correspondence CSV.

    Raises on a project class claimed by two subclasses -- the CSV is meant to
    partition classes, not share them.
    """
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
