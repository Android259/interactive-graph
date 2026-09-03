"""Unit tests for dataloader.lipid_classes.class_level_positive_labels."""

import pandas as pd

from dataloader.lipid_classes import class_level_positive_labels


def _table():
    return pd.DataFrame(
        {
            "LTPProtein": ["A", "A", "A", "B"],
            "FullIdentityOfLipid": [
                "Phosphatidylcholine (32:1)",
                "Phosphatidylcholine (34:1)",
                "Phosphatidylserine (32:1)",
                "Phosphatidylcholine (32:1)",
            ],
            "Interaction": [1, 0, 0, 0],
        }
    )


def test_class_level_positive_labels_widens_positives_within_a_protein_class():
    widened = class_level_positive_labels(_table())

    # Row 1 shares protein A's Phosphatidylcholine class with row 0's measured
    # positive and is widened to positive even though its own species was not.
    assert widened.tolist() == [1, 1, 0, 0]


def test_class_level_positive_labels_does_not_cross_proteins():
    widened = class_level_positive_labels(_table())

    # Protein B's own Phosphatidylcholine row was never measured positive, and A's
    # positive must not leak across to a different protein sharing the same class.
    assert widened.iloc[3] == 0


def test_class_level_positive_labels_keeps_an_all_negative_class_negative():
    widened = class_level_positive_labels(_table())

    assert widened.iloc[2] == 0
