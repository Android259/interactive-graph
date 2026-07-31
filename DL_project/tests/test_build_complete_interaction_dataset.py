import pandas as pd
import pytest

from preprocessing.build_complete_interaction_dataset import (
    build_complete_dataset,
)


def test_builds_one_row_per_pair_and_keeps_metadata_aligned():
    source = pd.DataFrame(
        [
            {
                "SmileGlobal": "L1-a",
                "SmileFragment": "0",
                "LTPProtein": "PROT_A",
                "ProteinDomain": "FAMILY_A",
                "FullIdentityOfLipid": "LIPID_1",
                "Lipid": "L1",
                "Screen": "in vitro",
                "Interaction": 1,
            },
            {
                "SmileGlobal": "L1-b",
                "SmileFragment": "0",
                "LTPProtein": "PROT_A",
                "ProteinDomain": "FAMILY_A",
                "FullIdentityOfLipid": "LIPID_1",
                "Lipid": "L1",
                "Screen": "in cellulo",
                "Interaction": 1,
            },
            {
                "SmileGlobal": "L2",
                "SmileFragment": "fragment",
                "LTPProtein": "PROT_B",
                "ProteinDomain": "FAMILY_B",
                "FullIdentityOfLipid": "LIPID_2",
                "Lipid": "L2",
                "Screen": "in vitro",
                "Interaction": 1,
            },
        ]
    )

    result = build_complete_dataset(source)

    assert len(result) == 4
    assert not result.duplicated(
        ["LTPProtein", "FullIdentityOfLipid"]
    ).any()
    assert result["Interaction"].tolist() == [1, 1, 0, 0]
    assert result["index"].tolist() == [0, 1, 2, 3]

    domains = result.groupby("LTPProtein")["ProteinDomain"].unique().to_dict()
    assert domains == {
        "PROT_A": ["FAMILY_A"],
        "PROT_B": ["FAMILY_B"],
    }

    positive = result[
        (result["LTPProtein"] == "PROT_A")
        & (result["FullIdentityOfLipid"] == "LIPID_1")
    ].iloc[0]
    assert positive["Screen"] == "in vitro; in cellulo"
    assert positive["SmileGlobal"] == "L1-a; L1-b"

    negative = result[
        (result["LTPProtein"] == "PROT_B")
        & (result["FullIdentityOfLipid"] == "LIPID_1")
    ].iloc[0]
    assert negative["ProteinDomain"] == "FAMILY_B"
    assert negative["Screen"] == ""
    assert negative["SmileGlobal"] == "L1-a; L1-b"


def test_rejects_conflicting_domains_for_one_protein():
    source = pd.DataFrame(
        {
            "LTPProtein": ["PROT_A", "PROT_A"],
            "ProteinDomain": ["FAMILY_A", "FAMILY_B"],
            "FullIdentityOfLipid": ["LIPID_1", "LIPID_2"],
            "Interaction": [1, 1],
        }
    )

    with pytest.raises(ValueError, match="Expected one ProteinDomain"):
        build_complete_dataset(source)
