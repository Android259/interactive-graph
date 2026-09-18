#!/usr/bin/env python3
"""Classify this project's lipid species into Titeca et al. 2023's own LTP-lipid
subclass scheme (Cer, PC, PE, PIPs, ...), Figure 3a of

    Titeca et al., "A system-wide analysis of lipid transfer proteins delineates
    lipid mobility in human cells", bioRxiv 2023, doi:10.1101/2023.12.21.572821

-- the paper this project's own interaction table (data/LTP-lipid_interaction.csv)
comes from (files/data_source.md). PROJECT_CLASS_TO_ARTICLE_SUBCLASS below is that
file's own project-class -> article-subclass table, kept in sync with it by hand
(files/data_source.md documents the reasoning for each row, not repeated here).

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

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataloader.dataset_source import interaction_csv_path  # noqa: E402
from training.pair_baseline_common import csv_classes  # noqa: E402

# files/data_source.md's own mapping table. Every class this project's csv_classes()
# currently produces is covered (verified against the live interaction table); two
# article subclasses (PIPs, Sterol) never appear here because this project's data
# has no species in them. A class not covered raises in classify() below rather
# than silently falling through, so a future data update that adds a new head-group
# class cannot go unclassified without notice.
PROJECT_CLASS_TO_ARTICLE_SUBCLASS = {
    "Bismonoacylglycerolphosphate": "BMP",
    "Cardiolipin": "CL",
    "Ceramide": "Cer",
    "Ceramide phosphate": "CerP",
    "Diacylglycerol": "DAG",
    "Dihexosyl ceramide": "Hex2Cer",
    "Hexosyl ceramide": "HexCer",
    "Lysophosphatidylcholine": "LPC",
    "Lysophosphatidylethanolamine": "LPE",
    "Lysophosphatidylglycerol": "LPG",
    "Phosphatidate": "PA",
    "Phosphatidylcholine": "PC",
    "Phosphatidylethanolamine": "PE",
    "Phosphatidylglycerol": "PG",
    "Phosphatidylglycerophosphate": "PGP",
    "Phosphatidylinositol": "PI",
    "Phosphatidylserine": "PS",
    "Retinol": "VA",
    "Sphingomyelin": "SM",
    "Sulfohexosyl ceramide": "SHexCer",
    "Triacylglycerol": "TAG",
    "docosapentaenoate": "FA",
    "docosatetraenoate": "FA",
    "docosatrienoate": "FA",
    "eicosapentaenoate": "FA",
    "eicosatetraenoate": "FA",
    "eicosatrienoate": "FA",
    "heptadecenoate": "FA",
    "hexadecenoate": "FA",
    "nonadecenoate": "FA",
    "octadecadienoate": "FA",
    "octadecatrienoate": "FA",
    "octadecatrienol": "FAL",
    "octadecenoate": "FA",
}


def classify(table: pd.DataFrame) -> dict[str, str]:
    """{FullIdentityOfLipid: article subclass}, one entry per distinct species."""
    classes = csv_classes(table)
    species_class = (
        table.assign(_class=classes)
        .drop_duplicates("FullIdentityOfLipid")
        .set_index("FullIdentityOfLipid")["_class"]
    )
    unmapped = sorted(set(species_class.unique()) - set(PROJECT_CLASS_TO_ARTICLE_SUBCLASS))
    if unmapped:
        raise ValueError(
            f"classify_lipids_by_article: no article subclass mapping for project "
            f"class(es) {unmapped} -- add them to PROJECT_CLASS_TO_ARTICLE_SUBCLASS "
            "(see files/data_source.md's own table) before running this again"
        )
    return {
        species: PROJECT_CLASS_TO_ARTICLE_SUBCLASS[project_class]
        for species, project_class in species_class.items()
    }


def main() -> None:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    table = pd.read_csv(interaction_csv_path(data_dir))
    mapping = classify(table)

    out_path = os.path.join(data_dir, "lipid_article_classification.json")
    with open(out_path, "w") as handle:
        json.dump(mapping, handle, indent=2, ensure_ascii=False, sort_keys=True)

    counts = pd.Series(mapping).value_counts()
    print(f"classified {len(mapping)} species into {len(counts)} article subclasses:")
    print(counts.to_string())
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
