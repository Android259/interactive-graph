"""Where a run is filed: its label, its exclusion-set directory and every output path.

Both are path components of run/, test_metrics/, models/ and checkpoints/ (under the
label's family directory, training/results_layout.py), and
(label, exclusion_set, seed) is the key of every row of results/tables/metrics_summary.csv.
The launchers in scripts/launch/ derive the same exclusion-set name independently, so a
change here has to be mirrored there or a job's log and its results land apart.
"""

import os
import re
import time
from dataclasses import dataclass
from datetime import datetime

from results_layout import label_family


SAFE_PATH_PART = re.compile(r"[^A-Za-z0-9._=-]+")


def run_label(conf):
    """The sanitised --label, else the OAR job name minus its group suffix, else a
    name built from the attention flags."""
    config_name = f"{'addLayers' if conf.third_layers_in_mlps else 'base'}_{'protSA' if conf.protein_self_attention else ''}_{'lipSA' if conf.lipid_self_attention else ''}_{'CA' if conf.cross_attention else ''}_{'doubleAtt' if conf.double_attention else ''}_{'protPosBias' if conf.prot_attention_pos_bias else ''}"
    raw_label = conf.label.strip()
    if not raw_label:
        oar_job_name = os.environ.get("OAR_JOB_NAME", "").strip()
        if oar_job_name:
            group_suffix = (
                r"_(CRAL-TRIO|START|lipocalin|GLTP|IP_trans|"
                r"LBP_BPI_CETP|scp2|ML|OSBP)_s-?\d+$"
            )
            raw_label = re.sub(group_suffix, "", oar_job_name)
        else:
            raw_label = config_name
    label_name = SAFE_PATH_PART.sub("_", raw_label).strip("._")
    if not label_name:
        raise ValueError(f"Invalid label value: {raw_label!r}")
    return label_name


def excluded_set_name(conf):
    """Directory name of the held-out set: "random", or "groups_..."/"subgroups_..." parts."""
    excluded_set_parts = []
    if conf.excluded_groups:
        excluded_set_parts.append("groups_" + "-".join(conf.excluded_groups))
    if conf.lipid_coldsplit:
        # Under --lipid_coldsplit no protein group is excluded, so without this every set
        # would land in the same "random" directory: four different experiments sharing one
        # test_metrics folder, and a progress table that cannot tell their event files apart
        # and reports n/a for all of them. The "groups_" prefix is deliberate even though a
        # lipid set is not a protein group -- it is the prefix every consumer of this path
        # already keys on (the progress table's dirs_by_set, list_completed_experiments,
        # build_metrics_table, the plotting scripts), and what the directory really names is
        # the exclusion set, whichever axis it lies on.
        excluded_set_parts.append("groups_" + conf.lipid_coldsplit)
    if conf.lipid_isolation:
        # Same reasoning as --lipid_coldsplit just above, and the same "groups_" prefix
        # every consumer of this path keys on. The key is the requested isolation, so the
        # directory reads "groups_iso0.85" and says what the block is without a lookup.
        excluded_set_parts.append("groups_iso" + conf.lipid_isolation)
    if conf.lipid_subclass:
        # Same axis again, cut by the source paper's own subclass -- same "groups_" prefix
        # and the same reason for it. The spec goes in verbatim ("groups_PC",
        # "groups_LPC+LPE+LPG"), so the directory says which block was held out without a
        # lookup; SAFE_PATH_PART is not applied here because a spec is only letters,
        # digits and "+", all safe in a path.
        excluded_set_parts.append("groups_" + conf.lipid_subclass)
    if conf.lipid_species_coldsplit:
        # Same axis, same "groups_" prefix, same reason. The share goes in as two digits
        # ("groups_species15") because that is what identifies the split here -- the block
        # itself is a per-seed draw, so unlike a subclass spec there is no name to put in
        # the path, and the seed already has its own place in every consumer of it.
        # int(x + 0.5), not round(): the launchers name the same directory from awk, which
        # rounds halves up, while Python's round() rounds them to even. The two disagree at
        # exactly the halfway shares (0.125 -> 13 against 12), and a disagreement here puts
        # the job's log in one directory and its run/ and test_metrics/ in another.
        excluded_set_parts.append(
            "groups_species%02d" % int(conf.lipid_species_coldsplit * 100 + 0.5)
        )
    if conf.drop_uncovered_protein_subclass:
        # Same block, a different EVALUATED SET of it: the rows whose (protein, subclass)
        # cell is absent from training are dropped instead of scored. That changes what every
        # test number means, so it has to change the path too -- without this a filtered and
        # an unfiltered run of the same label share one run/ directory, one test_metrics
        # folder and one (exclusion_set, seed) key in metrics_summary.csv, and whichever
        # finished last would silently stand for both. Appended rather than folded into the
        # "groups_species%02d" part so the "groups_" prefix every consumer keys on still
        # starts the name.
        excluded_set_parts.append("covered")
    if conf.family_only:
        # Third axis, same argument as --lipid_coldsplit just above. --family_only excludes
        # nothing, it RESTRICTS training to one family, so without this every family landed
        # in the same "random" directory under one label: nine runs sharing one
        # test_metrics folder, one models/<label>/random/seed0.pt that each family
        # overwrote in turn, and nine metrics_summary.csv rows that
        # analysis/compare_labels.py's latest_rows_for_label -- keyed on
        # (exclusion_set, seed) -- collapsed to whichever finished last. Eight of the nine
        # families were invisible to every summary.
        # "groups_" and not "family_" because that prefix is what every consumer of this
        # path keys on (the progress table's dirs_by_set, list_completed_experiments,
        # build_metrics_table, the plotting scripts); as with the lipid sets above, what
        # the directory names is the run's own axis, not necessarily a held-OUT group.
        excluded_set_parts.append("groups_" + conf.family_only)
    if conf.excluded_subgroups:
        excluded_set_parts.append("subgroups_" + "-".join(conf.excluded_subgroups))
    return "_".join(excluded_set_parts) if excluded_set_parts else "random"


@dataclass
class RunPaths:
    """Every directory and file name one run writes to."""

    label_name: str
    # arg_files/ subdirectory of the run's config (training/results_layout.py); every
    # result tree files the run under <tree>/<family>/<label>/.
    family: str
    excluded_set_name: str
    timestamp: str
    log_dir: str
    run_root: str
    test_metrics_root: str
    test_metrics_dir: str
    checkpoints_root: str
    models_root: str
    metrics_table_path: str

    @property
    def run_models_dir(self):
        """models/<family>/<label>/<excluded_set>/ -- --save_model weights and dynamics milestones."""
        return os.path.join(self.models_root, self.family, self.label_name, self.excluded_set_name)

    @property
    def run_checkpoints_dir(self):
        """checkpoints/<family>/<label>/<excluded_set>/ -- --save_checkpoint weights."""
        return os.path.join(self.checkpoints_root, self.family, self.label_name, self.excluded_set_name)


def create_run_paths(project_root, conf, label_name, excluded_set_name, number_of_parameters):
    """Resolve the run's paths and create its TensorBoard and test-report directories.

    --testmode redirects every artifact under testmode_outputs/, so a smoke run cannot
    touch the real tables. The TensorBoard directory is created exclusively: two jobs
    starting in the same second wait one second and retry with the next timestamp.
    """
    artifact_root = os.path.join(project_root, "testmode_outputs") if conf.testmode else project_root
    run_root = os.path.join(artifact_root, "run")
    test_metrics_root = os.path.join(artifact_root, "test_metrics")
    checkpoints_root = os.path.join(artifact_root, "checkpoints")
    models_root = os.path.join(artifact_root, "models")
    metrics_table_path = os.path.join(artifact_root, "results", "tables", "metrics_summary.csv")
    family = label_family(label_name)
    while True:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = os.path.join(
            run_root,
            family,
            label_name,
            excluded_set_name,
            f'train{timestamp}_{number_of_parameters}parameters_{conf.m}_{conf.HEADS}_{conf.seed}_{conf.lr}_{conf.batch}_{conf.hiddim}',
        )
        try:
            os.makedirs(log_dir, exist_ok=False)
            break
        except FileExistsError:
            time.sleep(1)
    test_metrics_dir = os.path.join(test_metrics_root, family, label_name, excluded_set_name)
    os.makedirs(test_metrics_dir, exist_ok=True)
    return RunPaths(
        label_name=label_name,
        family=family,
        excluded_set_name=excluded_set_name,
        timestamp=timestamp,
        log_dir=log_dir,
        run_root=run_root,
        test_metrics_root=test_metrics_root,
        test_metrics_dir=test_metrics_dir,
        checkpoints_root=checkpoints_root,
        models_root=models_root,
        metrics_table_path=metrics_table_path,
    )
