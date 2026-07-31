from plot_metric_by_subgroup import (
    aggregate_subgroups,
    parse_report,
    read_positive_counts,
    select_reports,
    _group_color,
    _group_sort_key,
)


REPORT = """\
seed: {seed}
lr: 0.001
run_status: complete

per_protein_subgroup_metrics:
subgroup  total  real_positive  real_negative  predicted_positive  predicted_negative  TP  FP  TN  FN  accuracy  sensitivity  precision  specificity  IoU  FAR  F1  balanced_accuracy  loss
--------  -----  -------------  -------------  ------------------  ------------------  --  --  --  --  --------  -----------  ---------  -----------  ---  ---  --  -----------------  ----
PITPNA       10              5              5                   5                   5   4   1   4   1  0.800000     0.800000   0.800000     0.800000  0.6  0.2  0.8           {metric}  0.5
"""


def write_report(root, timestamp, seed, metric):
    directory = root / "model" / "groups_IP_trans"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"test_metrics_{timestamp}_1parameters_4_8_{seed}_0.001_16_64.txt"
    path.write_text(REPORT.format(seed=seed, metric=metric), encoding="utf-8")
    return path


def test_parses_and_aggregates_protein_subgroup_rows(tmp_path):
    first = parse_report(
        write_report(tmp_path, "20260101_000000", 0, "0.600000"),
        tmp_path,
    )
    second = parse_report(
        write_report(tmp_path, "20260101_000001", 1, "0.800000"),
        tmp_path,
    )

    selected = select_reports([first, second], [("lr", "0.001")], ["IP_trans"])
    result = aggregate_subgroups(selected, "balanced_accuracy")

    assert result[0]["subgroup"] == "PITPNA"
    assert result[0]["mean"] == 0.7
    assert result[0]["count"] == 2
    assert result[0]["seeds"] == ["0", "1"]


def test_selects_latest_report_for_group_and_seed(tmp_path):
    old = parse_report(
        write_report(tmp_path, "20260101_000000", 0, "0.400000"),
        tmp_path,
    )
    new = parse_report(
        write_report(tmp_path, "20260102_000000", 0, "0.900000"),
        tmp_path,
    )

    selected = select_reports([old, new], [("lr", "0.001")], [])
    result = aggregate_subgroups(selected, "balanced_accuracy")

    assert result[0]["mean"] == 0.9
    assert result[0]["count"] == 1


def test_reads_positive_counts_from_full_dataset(tmp_path):
    dataset = tmp_path / "dataset.csv"
    dataset.write_text(
        "LTPProtein,Interaction\nPITPNA,1\nPITPNA,0\nPITPNA,1\nGLTP,0\n",
        encoding="utf-8",
    )

    assert read_positive_counts(dataset) == {"PITPNA": 2}


def test_protein_group_order_and_colors_are_fixed():
    groups = ["scp2", "GLTP", "unknown", "CRAL-TRIO"]

    assert sorted(groups, key=_group_sort_key) == [
        "CRAL-TRIO",
        "GLTP",
        "scp2",
        "unknown",
    ]
    assert _group_color("GLTP") == "#F28E2B"
    assert _group_color("unknown") == "#7F7F7F"
