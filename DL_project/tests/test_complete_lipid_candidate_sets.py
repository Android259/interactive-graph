import pandas as pd

from preprocessing.complete_lipid_candidate_sets import complete_table


# Propan-1-ol and propan-2-ol stand in for two isomer candidates of one lipid (same
# formula, different structure); butan-1-ol is the different molecule.
CANDIDATE_A = "CCCO"
CANDIDATE_B = "CC(C)O"
OTHER_MOLECULE = "CCCCO"


def make_table(pairs, **columns):
    table = pd.DataFrame(
        [
            {"SmileGlobal": smile_global, "SmileFragment": smile_fragment}
            for smile_global, smile_fragment in pairs
        ]
    )
    for name, values in columns.items():
        table[name] = values
    return table


def test_completes_a_short_candidate_list_from_a_longer_one():
    table = make_table([(CANDIDATE_A, "0"), (f"{CANDIDATE_A}; {CANDIDATE_B}", "0")])

    completed, changes, _ = complete_table(table)

    assert completed.loc[0, "SmileGlobal"] == f"{CANDIDATE_A}; {CANDIDATE_B}"
    assert completed.loc[1, "SmileGlobal"] == f"{CANDIDATE_A}; {CANDIDATE_B}"
    assert [change["candidates_before"] for change in changes] == [1]
    assert [change["candidates_after"] for change in changes] == [2]


def test_keeps_the_first_candidate_so_first_fragment_only_runs_are_unaffected():
    table = make_table([(CANDIDATE_B, "0"), (f"{CANDIDATE_A}; {CANDIDATE_B}", "0")])

    completed, _, _ = complete_table(table)

    assert completed.loc[0, "SmileGlobal"].split(";")[0].strip() == CANDIDATE_B
    assert completed.loc[1, "SmileGlobal"].split(";")[0].strip() == CANDIDATE_A


def test_rewrites_the_column_the_loader_actually_reads():
    table = make_table([("0", CANDIDATE_A), ("0", f"{CANDIDATE_A}; {CANDIDATE_B}")])

    completed, changes, _ = complete_table(table)

    assert completed.loc[0, "SmileGlobal"] == "0"
    assert completed.loc[0, "SmileFragment"] == f"{CANDIDATE_A}; {CANDIDATE_B}"
    assert [change["column"] for change in changes] == ["SmileFragment"]


def test_leaves_a_component_spanning_two_molecular_formulas_untouched():
    table = make_table([(CANDIDATE_A, "0"), (f"{CANDIDATE_A}; {OTHER_MOLECULE}", "0")])

    completed, changes, diagnostics = complete_table(table)

    assert changes == []
    assert completed.loc[0, "SmileGlobal"] == CANDIDATE_A
    assert len(diagnostics["mixed"]) == 1


def test_preserves_row_order_and_every_other_column():
    table = make_table(
        [(CANDIDATE_A, "0"), (f"{CANDIDATE_A}; {CANDIDATE_B}", "0")],
        LTPProtein=["GM2A", "PITPNA"],
        Interaction=[1, 0],
    )

    completed, _, _ = complete_table(table)

    assert completed["LTPProtein"].tolist() == ["GM2A", "PITPNA"]
    assert completed["Interaction"].tolist() == [1, 0]
    assert completed["SmileFragment"].tolist() == ["0", "0"]


def test_ignores_empty_and_trailing_separator_parts():
    table = make_table([(f"{CANDIDATE_A}; ", "0"), (f"{CANDIDATE_A};{CANDIDATE_B}", "0")])

    completed, changes, _ = complete_table(table)

    assert completed.loc[0, "SmileGlobal"] == f"{CANDIDATE_A}; {CANDIDATE_B}"
    assert changes[0]["added"] == CANDIDATE_B
