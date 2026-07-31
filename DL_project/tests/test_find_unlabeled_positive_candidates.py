import pandas as pd

from data.find_unlabeled_positive_candidates import find_candidates


def test_candidate_requires_same_protein_similarity_and_exact_family_support():
    table = pd.DataFrame(
        [
            {
                "SmileGlobal": "CCCC",
                "LTPProtein": "P1",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L1",
                "Lipid": "L1(4:0)",
                "Screen": "in vitro",
                "Interaction": 1,
            },
            {
                "SmileGlobal": "CCCCC",
                "LTPProtein": "P2",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L2",
                "Lipid": "L2(5:0)",
                "Screen": "in vitro",
                "Interaction": 1,
            },
            {
                "SmileGlobal": "CCCCC",
                "LTPProtein": "P1",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L2",
                "Lipid": "L2(5:0)",
                "Screen": "in vitro",
                "Interaction": 0,
            },
            {
                "SmileGlobal": "NNNN",
                "LTPProtein": "P1",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L3",
                "Lipid": "L3",
                "Screen": "in vitro",
                "Interaction": 0,
            },
        ],
        index=[10, 11, 12, 13],
    )

    candidates = find_candidates(table, same_protein_similarity=0.0)

    assert candidates["pair_id"].tolist() == [12]
    candidate = candidates.iloc[0]
    assert candidate["nearest_positive_lipid_same_protein"] == "L1"
    assert candidate["exact_lipid_positive_family_protein_count"] == 1
    assert candidate["exact_lipid_positive_family_proteins"] == "P2"


def test_candidate_excludes_exact_support_from_the_same_protein():
    table = pd.DataFrame(
        [
            {
                "SmileGlobal": "CCCC",
                "LTPProtein": "P1",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L1",
                "Lipid": "L1",
                "Screen": "in vitro",
                "Interaction": 1,
            },
            {
                "SmileGlobal": "CCCC",
                "LTPProtein": "P1",
                "ProteinDomain": "F1",
                "FullIdentityOfLipid": "L1",
                "Lipid": "L1",
                "Screen": "in vitro",
                "Interaction": 0,
            },
        ]
    )

    candidates = find_candidates(table, same_protein_similarity=0.0)

    assert candidates.empty
