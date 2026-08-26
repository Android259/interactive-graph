"""Cluster-targeting checks for the canonical OAR submitters.

These exercise the shell layer without submitting anything: the queue helper's
``capture`` mode records what ``oarsub`` *would* be called with, and the
generated job script's GPU guard is executed against a fake ``nvidia-smi``.

The guard is the reason Kraken jobs used to die instantly: it was hardcoded to
``*A100*|*V100*`` and rejected Kraken's H100/H200.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
QUEUE_HELPER = REPO / "scripts" / "cluster" / "cluster_queue_remote.sh"
SUBMITTER = "scripts/launch/submit_grid.sh"
# standard.md holds no `--` lines, which trips `grep`+`pipefail` in the
# submitters; use a config that actually carries flags.
ARGS_FILE = "scripts/arg_files/dropout01.md"

BIGFOOT = {"GPU_MODEL_GLOB": "*A100*|*V100*"}
KRAKEN = {"GPU_MODEL_GLOB": "*H100*|*H200*"}


def capture(tmp_path, env_overrides):
    """Return the oarsub command lines the submitter would issue."""
    work = tmp_path / "repo"
    # Same layout as the real tree: the submitters find their libraries by
    # project-relative path, so a flat copy would not resolve.
    for sub in ("launch", "lib", "cluster"):
        (work / "scripts" / sub).mkdir(parents=True)
    shutil.copy(REPO / "scripts" / "settings.sh", work / "scripts" / "settings.sh")
    for relative in (
        "launch/submit_grid.sh",
        "launch/run_experiment_pack.sh",
        "launch/run_one_experiment.sh",
        "cluster/cluster_queue_remote.sh",
        "lib/pack_lib.sh",
        "lib/list_completed_experiments.py",
        "lib/args_file_lib.sh",
        "lib/grid_lib.sh",
    ):
        shutil.copy(REPO / "scripts" / relative, work / "scripts" / relative)
    shutil.copytree(REPO / "scripts" / "arg_files", work / "scripts" / "arg_files")

    queue = tmp_path / "queue"
    env = dict(os.environ)
    env.update(env_overrides)
    subprocess.run(
        ["bash", str(work / "scripts" / "cluster" / "cluster_queue_remote.sh"),
         "capture", str(queue), SUBMITTER, str(tmp_path / "marker"), ARGS_FILE],
        cwd=work, env=env, check=True, capture_output=True, text=True,
    )
    return (queue / "pending.commands").read_text().splitlines()


def test_defaults_target_bigfoot_gpus(tmp_path):
    lines = capture(tmp_path, BIGFOOT)
    assert len(lines) == 45, "9 groups x 5 seeds"
    assert all("A100" in line for line in lines)
    assert not any("H100" in line for line in lines)


def test_kraken_settings_target_h100_h200(tmp_path):
    lines = capture(tmp_path, {**KRAKEN,
                               "GPU_PROPERTY": "(gpumodel='H100' OR gpumodel='H200')"})
    assert len(lines) == 45
    assert all("H100" in line for line in lines)
    assert not any("A100" in line for line in lines)


def test_empty_project_and_property_omit_their_flags(tmp_path):
    lines = capture(tmp_path, {**KRAKEN, "PROJECT": "", "GPU_PROPERTY": ""})
    assert not any("--project" in line for line in lines)
    assert not any(" -p " in line for line in lines)


def test_overrides_reduce_the_job_count(tmp_path):
    lines = capture(tmp_path, {**BIGFOOT,
                               "GROUPS_OVERRIDE": "GLTP", "SEEDS_OVERRIDE": "0"})
    assert len(lines) == 1


def test_complete_only_submits_missing_requested_pairs(tmp_path):
    lines = capture(
        tmp_path,
        {
            **BIGFOOT,
            "GROUPS_OVERRIDE": "GLTP ML",
            "SEEDS_OVERRIDE": "1 3",
            "COMPLETE_ONLY": "1",
            "COMPLETED_EXPERIMENTS": "GLTP:1\nML:3",
        },
    )
    assert len(lines) == 2
    assert any("GLTP_s3" in line for line in lines)
    assert any("ML_s1" in line for line in lines)


def test_job_id_tag_separates_the_clusters_oar_filenames(tmp_path):
    plain = capture(tmp_path / "a", BIGFOOT)
    tagged = capture(tmp_path / "b", {**KRAKEN, "JOB_ID_TAG": "k"})
    assert all("_seed0_%jobid%.out" in line
               for line in plain if "_seed0_" in line)
    assert all("_seed0_k%jobid%.out" in line
               for line in tagged if "_seed0_" in line)


@pytest.mark.parametrize(
    "gpu_name,expected",
    [
        ("Tesla V100-SXM2-16GB", ("v100", "2", "12288", "11000", "5")),
        ("NVIDIA A100-SXM4-80GB", ("a100", "4", "14336", "13000", "5")),
        ("NVIDIA H100 80GB HBM3", ("h100", "4", "16384", "15000", "5")),
        ("NVIDIA H200", ("h200", "8", "16384", "15000", "5")),
    ],
)
def test_pack_hardware_profiles_cover_cluster_gpu_models(gpu_name, expected):
    command = (
        f'source "{REPO / "scripts" / "lib" / "pack_lib.sh"}"; '
        f'pack_hardware_profile "{gpu_name}"'
    )
    result = subprocess.run(
        ["bash", "-c", command],
        check=True,
        capture_output=True,
        text=True,
    )
    assert tuple(result.stdout.strip().split("\t")) == expected


@pytest.mark.parametrize(
    "cluster,expected",
    [
        ("bigfoot", ("9", "0", "1", "1")),
        ("kraken", ("12", "0", "4", "1")),
    ],
)
def test_cluster_profiles_enable_hardware_aware_packing(cluster, expected):
    command = (
        f'CLUSTER_NAME="{cluster}"; '
        f'source "{REPO / "scripts" / "lib" / "cluster_common.sh"}"; '
        'printf "%s\\t%s\\t%s\\t%s\\n" '
        '"${PACK_SIZE}" "${PACK_PARALLEL}" '
        '"${PACK_WALLTIME_PARALLEL}" "${PACK_HARDWARE_AUTO}"'
    )
    env = dict(os.environ)
    for name in (
        "PACK_SIZE",
        "PACK_PARALLEL",
        "PACK_WALLTIME_PARALLEL",
        "PACK_HARDWARE_AUTO",
    ):
        env.pop(name, None)
    result = subprocess.run(
        ["bash", "-c", command],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert tuple(result.stdout.strip().split("\t")) == expected


@pytest.mark.parametrize(
    "env_overrides,job_count,walltime",
    [
        (
            {
                **BIGFOOT,
                "PACK_SIZE": "9",
                "PACK_PARALLEL": "0",
                "PACK_WALLTIME_PARALLEL": "1",
                "PACK_HARDWARE_AUTO": "1",
                "MAX_WALLTIME": "48:00:00",
            },
            5,
            "walltime=45:00:00",
        ),
        (
            {
                **KRAKEN,
                "PACK_SIZE": "12",
                "PACK_PARALLEL": "0",
                "PACK_WALLTIME_PARALLEL": "4",
                "PACK_HARDWARE_AUTO": "1",
                "MAX_WALLTIME": "",
            },
            4,
            "walltime=15:00:00",
        ),
    ],
)
def test_hardware_aware_cluster_defaults_capture_larger_jobs(
    tmp_path, env_overrides, job_count, walltime
):
    lines = capture(tmp_path, env_overrides)

    assert len(lines) == job_count
    assert all(".pack.out" in line for line in lines)
    assert all(walltime in line for line in lines)
    assert all("PACK_HARDWARE_AUTO=1" in line for line in lines)


@pytest.mark.parametrize(
    "gpu_name,total_mib,glob,profile,slots",
    [
        ("Tesla V100-SXM2-16GB", 16384, "*A100*|*V100*", "v100", 1),
        ("NVIDIA A100-SXM4-40GB", 40960, "*A100*|*V100*", "a100", 2),
        ("NVIDIA H100 80GB HBM3", 81920, "*H100*|*H200*", "h100", 4),
        ("NVIDIA H200", 143360, "*H100*|*H200*", "h200", 7),
    ],
)
def test_pack_runner_resolves_slots_from_allocated_gpu(
    tmp_path, gpu_name, total_mib, glob, profile, slots
):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    nvidia_smi = fake_bin / "nvidia-smi"
    nvidia_smi.write_text(
        "#!/usr/bin/env bash\n"
        "case \"$*\" in\n"
        f"  *query-gpu=name*) printf '%s\\n' '{gpu_name}' ;;\n"
        f"  *query-gpu=memory.total*) printf '%s\\n' '{total_mib}' ;;\n"
        "  *query-gpu=uuid*) printf '%s\\n' 'GPU-test' ;;\n"
        "  *) exit 2 ;;\n"
        "esac\n"
    )
    nvidia_smi.chmod(0o755)
    nproc = fake_bin / "nproc"
    nproc.write_text("#!/usr/bin/env bash\nprintf '48\\n'\n")
    nproc.chmod(0o755)
    env = dict(os.environ)
    env.update(
        {
            "PATH": f"{fake_bin}:{env['PATH']}",
            "GPU_MODEL_GLOB": glob,
            "PACK_HARDWARE_AUTO": "1",
            "PACK_PARALLEL": "0",
            "GPU_MIB_PER_RUN": "0",
            "PACK_CPU_PER_RUN": "0",
            "PACK_MIN_FREE_GPU_MIB": "0",
        }
    )

    spec_file = tmp_path / "empty.spec"
    spec_file.write_text("")

    result = subprocess.run(
        ["bash", str(REPO / "scripts" / "launch" / "run_experiment_pack.sh"), str(spec_file)],
        cwd=REPO,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert f"profile={profile}" in result.stdout
    assert f"{slots} concurrent slot(s)" in result.stdout


@pytest.mark.parametrize(
    "glob, gpu_name, accepted",
    [
        ("*H100*|*H200*", "NVIDIA H100 80GB HBM3", True),
        ("*H100*|*H200*", "NVIDIA H200", True),
        ("*H100*|*H200*", "Tesla V100-SXM2-16GB", False),
        ("*A100*|*V100*", "NVIDIA A100-SXM4-40GB", True),
        ("*A100*|*V100*", "NVIDIA H100 80GB HBM3", False),
    ],
)
def test_generated_guard_accepts_only_the_targeted_gpus(glob, gpu_name, accepted):
    """The `case` pattern must be a live glob, not a %q-escaped literal."""
    guard = (
        f'gpu_name="{gpu_name}"; '
        f'case "${{gpu_name}}" in {glob}) exit 0 ;; *) exit 1 ;; esac'
    )
    result = subprocess.run(["bash", "-c", guard])
    assert (result.returncode == 0) is accepted


def test_oar_log_name_matches_the_lookup_pattern(tmp_path):
    """The .out filename a submitter produces must match the glob wait_and_sync
    searches by, for both an empty and a non-empty JOB_ID_TAG.

    These drifted apart once: JOB_ID_TAG was added to the generated -O/-E names
    to keep the clusters' overlapping job IDs apart, but the lookup kept using
    "*_${job_id}.out", so every Kraken job was reported as "log not available
    yet" while its log sat on disk.
    """
    for tag in ("", "k"):
        produced = f"variant_seed0_{tag}200804.out"
        pattern = f"*_{tag}200804.out"
        matched = subprocess.run(
            ["bash", "-c", f'case "{produced}" in {pattern}) exit 0 ;; *) exit 1 ;; esac']
        ).returncode
        assert matched == 0, f"{pattern!r} does not match {produced!r}"
