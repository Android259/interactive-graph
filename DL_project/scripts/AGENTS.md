# Scripts Contract

Cluster job submission, environment activation, and run lifecycle. These launch
**real training on remote GPUs** (OAR scheduler on `bigfoot`, or `kraken-gpu`).
Do not execute submitters, runners, or kill/sync scripts unless explicitly
requested — dry-run by stubbing `oarsub`/`ssh` when verifying logic.

## Cluster Abstraction

One implementation serves both clusters; `run_bigfoot.sh` / `run_kraken.sh` and
`wait_and_sync_*.sh` are thin wrappers that export `CLUSTER_NAME` and re-exec
the generic file.

- `cluster_common.sh` — sourced profile: every cluster-dependent value keyed off
  `CLUSTER_NAME`. Bigfoot = A100/V100, Kraken = H100/H200 (both `sm_90`).
- `run_cluster.sh`, `wait_and_sync_cluster.sh`, `cluster_queue_remote.sh`,
  `cluster_wait_watchdog.sh` — the shared implementations.
- `cluster_preflight_remote.sh` — read-only frontend checks (conda env present,
  torch built for the cluster's SM target, OAR tooling, project candidates).
  Runs after the rsync and before any remote state is created.

Artifacts are namespaced so both clusters can run at once: queue
`.<cluster>_job_queues/`, marker `.<cluster>_session_*`, tmux `<cluster>_wait`,
socket `/tmp/<cluster>-…sock`, and `JOB_ID_TAG` (empty on Bigfoot, `k` on
Kraken) which keeps OAR `.out` filenames distinct — the two clusters hand out
overlapping job IDs.

## Watching Clusters

`wait_and_sync.sh` is **one** loop that visits every cluster in `CLUSTERS`
(default `bigfoot kraken`) in turn, then rebuilds the metrics table **once per
round, locally**, from the merged `run/` + `test_metrics/` + `script_logs/`
tree. Building locally is what makes multi-cluster watching correct: the old
per-cluster loop regenerated the table on each cluster from only that cluster's
results and copied it over the local file, so two clusters overwrote each
other's rows in turn.

`run_cluster.sh` hands off to it with `HANDOFF_CLUSTER=<name>` (which cluster
the new session marker and queue belong to); `WATCH_CLUSTERS=<name>` narrows it.
`wait_and_sync_bigfoot.sh` / `wait_and_sync_kraken.sh` are single-cluster
wrappers. The tmux session, log and pid derive from the cluster *set* via
`cluster_wait_session()` (`wait_bigfoot_kraken`, `wait_kraken`, …), so a
combined watcher and a single-cluster one never adopt each other's session —
and `cluster_wait_watchdog.sh` uses the same formula, so it guards the daemon
it actually means to.

A round prints two tables: per-cluster job progress (`LABEL`, `EXCL GROUP`,
`SEED`, `CUR`, `CKPT`, `BEST VBA`, `TRAIN BA`, metrics to two decimals, sorted by
label/group/seed) and, once at the end, the OAR summary (`CLUSTER`, `RUNNING`,
`WAITING`, `TOTAL`, plus `OTHER`/`PENDING` only when some cluster reports a
non-zero one, plus `DRAINER` only for the watcher that has one). Both live in
`wait_progress_table.sh` and share one renderer, sourced by **both**
`wait_and_sync.sh` and `wait_and_sync2.sh`: they differ in how jobs keep flowing
(tmux daemon + local drain vs. foreground viewer + cluster cron) but observe the
same thing, so change the display there once rather than in each watcher.
`LABEL`/`EXCL GROUP`/`SEED` are read back out of the OAR `.out` path the
submitters build, and `TRAIN BA` comes from TensorBoard — `new_train.py` never
prints train balanced accuracy to the log.

Remaining caveat: the tee'd `script_logs/<label>/…` paths are identical on both
clusters, so do not run the same arg file on both at the same time.

### Third source: local jobs (`run_local.sh`)

Both watchers also poll `scripts/run_local.sh` grids on this machine every
round, via `poll_local` (`wait_progress_table.sh`) — no SSH, no rsync, just a
`pgrep` and a file read, so it is never gated behind `CLUSTERS`. It shows up
as an extra `LABEL … ` progress table (`----- local -----`) and an extra
`local` row in the summary table.

`run/`, `test_metrics/` and `metrics_summary.csv` need nothing extra: local
jobs are `training/new_train.py` running directly, the same code that runs on
a cluster and gets rsynced back, so their outputs already land in the same
collision-free (timestamp+config-keyed) paths, and `upsert_row`
(`analysis/build_metrics_table.py`) is `flock`-guarded against concurrent
writers — the case several local jobs finishing close together actually
creates, unlike two clusters, which write from different machines.

`script_logs/` is the one tree local jobs add new *conventions* to, not just
new files:

- A plain background process has no scheduler-assigned id, so `run_local.sh`
  manufactures one: `LOCAL_JOB_TAG="l"` plus the process's own pid, on a
  `*_l<pid>.out` file — the same `*_<tag><id>.out` convention bigfoot (tag
  `""`) and kraken (tag `"k"`) already use, so all three sources can never
  collide on a filename (three disjoint id namespaces, three tags). The
  friendly, stable-named `.log` `test_run.sh`/`submit_all_groups_all_seeds.sh`
  already write is the real file; `.out` is a symlink to it, created right
  after backgrounding once the pid is known.
- `script_logs/local_run.queue` (`variant<TAB>group<TAB>seed` per line) is
  `run_local.sh`'s own pending-jobs list, the local analogue of
  `.bigfoot_job_queues/active/pending.commands` — popped as each job launches,
  removed entirely on exit (a trap, so a crash never leaves phantom queued
  rows). `poll_local` reads it for the `WAITING` count and the `(queued)` rows.

Both are read-only from the watchers' side; only `run_local.sh` ever writes
them. A manually started `new_train.py` (`test_run.sh`, an ad hoc smoke run)
never gets tagged, so it never appears in the local table or count — only
grids actually launched through `run_local.sh` do.

## Config Variants: `arg_files/`

- Each `arg_files/<variant>.md` is a config: lines starting with `--` are flags
  passed verbatim to `training/new_train.py`. Non-`--` lines are ignored
  (e.g. `standard.md` = "(none; standard configuration)" → defaults only).
- The filename stem is the run `--label` and names the output tree
  (`run/<label>/`, `test_metrics/`, `graphics/<label>/`).
- Add a new experiment by adding an `arg_files/*.md`, not by editing submitters.
- Because non-`--` lines are ignored, an arg file can carry its own rationale above the
  flags — what the run tests, what to read afterwards, what it should be compared
  against. The `_GRL*` family does this; prefer it to leaving the hypothesis only in
  someone's memory.
- Keep the flag block of a variant identical to the run it is meant to be compared
  with, down to the line, so the difference in the result maps to one change. Suffixes
  extend the base stem (`bbp_nps3mlp_dpt01_wd0001_gm_plm64_hid64` + `_GRL`, `_GRLfit`,
  `_GRLdeepfit`, `_GRLnolip`, `_GRLnoprot`, `_bilinear`, `_lipidonly`, `_protonly`).
- Verify a new variant parses and builds before queueing it:
  `bash scripts/parameters.sh <variant>`.

## Canonical Multi-Job Submitters

- `submit_all_groups_all_seeds.sh <arg_file>` — 9 excluded groups × 5 seeds = 45
  jobs; each job excludes **one** group (that group is both val and test via a
  50/50 seeded split). If the arg file contains `--cold_split`, this script
  `exec`s the cold-split submitter below instead, so `--cold_split` is the single
  switch that selects the cold series (works via `run_bigfoot.sh` too, which
  always routes arg files here).
- `submit_cold_val_test_all_seeds.sh <arg_file>` — 45 jobs with **separate cold
  validation and test groups** (`--excluded_groups=TEST,VAL --test_group=TEST`).
  Test rotates over all 9 groups; VAL is a fixed, size/balance-aware choice per
  test group. The TEST→VAL table and its rationale are in the script header.
  The `--cold_split` config boolean (see `read_configuration.py`) marks a run as
  cold-split and is validated to require `test_group`.

Both read an `arg_files/*.md`, build the `oarsub` command (GPU model guard, GPU
memory `flock`, conda activation), and log to `script_logs/<...>/`.

## Packing: Several Experiments per OAR Job

45 five-hour jobs per variant is what makes this project look like it occupies
the cluster. `PACK_SIZE` experiments instead share one job. The canonical
`run_bigfoot.sh` default is 9 experiments per job; `run_kraken.sh` defaults to
12. Calling a submitter directly still defaults to `PACK_SIZE=1`, the historical
one-experiment-per-job path.

- `pack_lib.sh` — sourced by both submitters: walltime arithmetic, the cluster
  walltime check, and the pack-record format (documented in its header).
- `run_experiment_pack.sh` — the job command on the compute node. The submitters
  splice one base64 blob into the `oarsub` line; the logic lives in this file
  rather than in a printf'd one-liner so it can be read and tested.

**Concurrency is resolved inside the job, not at submit time.** With the
canonical launchers, `PACK_PARALLEL=0` and `PACK_HARDWARE_AUTO=1` select a
V100/A100/H100/H200 profile after `nvidia-smi` identifies the allocated card.
The runner then derives its slot count as
`min(profile cap, total_mib * PACK_GPU_PERCENT / 100 / GPU_MIB_PER_RUN,
nproc / PACK_CPU_PER_RUN)`. This also distinguishes memory variants of the
same model. The current profiles are:

| GPU | cap | MiB/run | min free MiB |
|---|---:|---:|---:|
| V100 | 2 | 12288 | 11000 |
| A100 | 4 | 14336 | 13000 |
| H100 | 4 | 16384 | 15000 |
| H200 | 8 | 16384 | 15000 |

The `nproc` term matters because
Kraken gives 48 cores per GPU and Bigfoot far fewer, while every training brings
`num_workers` DataLoader processes. Explicit positive `PACK_PARALLEL`,
`GPU_MIB_PER_RUN`, `PACK_CPU_PER_RUN`, or `PACK_MIN_FREE_GPU_MIB` values override
the corresponding automatic value. `PACK_HARDWARE_AUTO=0` restores the manual
runner behaviour.

**Walltime is fixed at submit time, so it is sized for the weakest card.**
`WALLTIME` stays the budget of ONE experiment; a packed job asks for
`ceil(PACK_SIZE / PACK_WALLTIME_PARALLEL) x WALLTIME`. `PACK_WALLTIME_PARALLEL`
defaults to 1 ("assume the card runs them one at a time"); raise it only when
every card `GPU_PROPERTY` admits is known to hold that many. Measured run time
is 75-300 min (median ~140), i.e. the 5 h per-experiment budget is already tight
at the tail.

`MAX_WALLTIME` is the documented scheduler cap, per cluster in
`cluster_common.sh`: **Bigfoot 48 h**; **Kraken unset**, because GRICAD
documents no maximum for its production jobs (only devel = 30 min, and a 2 h
default when none is given) and inventing one would silently shrink packs. A
pack that exceeds the cap is refused while the queue is being built — much
cheaper than an `oarsub` rejected at drain time, which stops the whole drain.

On Bigfoot `PACK_SIZE=9` means 45 h per job under the 48 h cap, and 45
experiments become 5 jobs. Kraken uses `PACK_SIZE=12` and sizes walltime for
four-way H100 execution (`PACK_WALLTIME_PARALLEL=4`): 45 experiments become
four jobs, while an H200 may execute up to eight streams and finish earlier.

Two properties the pack path must keep:

- **One failure must not take the pack down.** The runner is deliberately not
  `set -e`; each experiment's exit status is collected and reported at the end.
- **A walltime kill must not cost the finished work.** Each success writes
  `script_logs/<...>/.pack_done/<stem>`, and `PACK_SKIP_DONE=1` skips those on
  resubmission, so re-running a killed pack retries only what is missing.

Monitoring survives packing because the runner writes one
`..._${JOB_ID_TAG}${OAR_JOB_ID}.out` per experiment, in the same directory the
unpacked path uses — `wait_progress_table.sh` matches every one of them and
emits a row each (keyed `<job_id>#<n>`, since several rows now share a job id).
The packed job's own OAR output is named `*.pack.out` under `_packs/` precisely
so it does **not** match that pattern and become a phantom row.

Two things that look like details and are not:

- `GPU_MODEL_GLOB`'s `|` alternation works in the unpacked path only because the
  glob is spliced into the *text* of the generated command. Reaching the runner
  through the environment, `|` is an ordinary character, so the runner splits the
  alternatives itself before matching.
- The flag block from `arg_files/*.md` is interpreted by a shell exactly once in
  the unpacked path (`bash -c` removes the quotes in `--pool_type="gem"`). The
  runner reproduces that with `eval "set -- ${python_args}"`; plain word
  splitting would hand python the quote characters and change the run.

## Cluster Runners & Queue

- `run_bigfoot.sh` / `run_kraken.sh` — SSH orchestration to a remote host
  (`REMOTE_HOST`/`REMOTE_USER`/`REMOTE_PROJECT` env overrides); sync + submit.
- `cluster_queue_remote.sh capture|drain|count QUEUE_DIR` — manage the job queue
  under `.<cluster>_job_queues/`. `capture` records what `oarsub` *would* be
  called with (by exporting an `oarsub` shell function), which is also the
  dry-run hook for verifying a submitter. `bigfoot_queue_remote.sh` is a shim
  kept only for wait daemons started before the port.
- `run_excluded_group_tests.sh` / `run_excluded_subgroup_tests.sh` — per-group /
  per-subgroup runs; tunable via `EP`, `BATCH`, `NUM_WORKERS` env vars.
- `submit/` — one-off historical experiment submitters; treat as archive, not a
  reusable API.

## Cluster Environment

`cluster_env.yml` + `install_cluster_env.sh` reproduce Bigfoot's
`Kalinin_project_LP` on a cluster that has none (Kraken had no conda at all).
The installer drops Miniforge into `$HOME/miniconda3` — the same path Bigfoot
uses, so the default `CONDA_SH` resolves without an override — and is
idempotent.

The spec is `conda env export` from Bigfoot with three corrections; do not
regenerate it without re-applying them:

- pip needs `--extra-index-url .../whl/cu126` and
  `--find-links data.pyg.org/whl/torch-2.6.0+cu126.html`; `torch==2.6.0+cu126`
  and the `+pt26cu126` PyG wheels are not on PyPI.
- `numpy` and `sympy` are pinned to what Bigfoot actually **loads** (1.26.4 and
  1.13.1), not to what its `pip freeze` claims (2.2.6 / 1.14.0 — stale entries
  shadowed by conda). Reproducing the claimed pins yields numpy 2.x, which
  breaks this torch/PyG build, and a sympy that conflicts with torch's own pin.

Bigfoot's torch 2.6.0+cu126 is compiled for `sm_50…sm_90`, so the same
environment runs on Kraken's H100/H200 (`sm_90`) unchanged.

Checking the SM targets needs `torch._C._cuda_getArchFlags()`:
`torch.cuda.get_arch_list()` returns `[]` on a GPU-less frontend even for a
good CUDA build, so gating on it would reject every environment.

## Lifecycle & Helpers

- `enter_project_env.sh` / `activate_training_env.sh` — `source` to activate the
  `Kalinin_project_LP` conda env.
- `generate_config_graphics.sh LABEL` — builds `graphics/<label>/…` by calling the
  `analysis/` plot scripts.
- `kill_and_save_all.sh`, `kill_by_name.sh`, `kill_job.sh` — stop running jobs.
- `wait_and_sync_bigfoot.sh`, `wait_and_sync_kraken.sh` — block until jobs
  finish and pull results back (tmux daemon, live per-epoch progress).
- `bigfoot_wait_watchdog.sh`, `kraken_wait_watchdog.sh` — cron-friendly
  liveness checks for those daemons.
- `cancel_complete_missing_groups.sh`, `git_commit_and_push.sh` — completion and
  commit helpers.
- `_list_label_dimension.py`, `visualize_torchviz_architecture.py` — local helpers.

## Change Rules

- Keep the `oarsub` GPU guard, the GPU-memory `flock`, and the conda-activation
  prologue when copying a submitter. In the two canonical submitters these are
  parameterized by `GPU_PROPERTY` / `GPU_MODEL_GLOB` / `MIN_FREE_GPU_MIB` /
  `WALLTIME` / `PROJECT` / `CONDA_SH` / `CONDA_ENV`: retarget a cluster by
  setting those, **never** by rewriting submitter text. Defaults reproduce the
  Bigfoot values, so an unset environment behaves exactly as before.
- In the generated `train_command`, `GPU_MODEL_GLOB` must be spliced with `%s`
  (a `%q`-escaped glob matches nothing in a `case`); `MIN_FREE_GPU_MIB` uses
  `%q` and is validated digits-only. The conversion count must match the
  argument count — a mismatch silently duplicates the whole job script.
- `PROJECT` and `GPU_PROPERTY` use `${VAR-default}`, not `${VAR:-default}`, so
  an explicitly empty value omits the corresponding `oarsub` flag.
- Preserve the `arg_files/*.md` → `--label` → output-path convention; changing it
  breaks `analysis/` matching and `graphics/` layout.
- Verify a submitter by mocking `oarsub` (print/execute the generated command),
  not by submitting real jobs. For a packing change, the regression to run is
  "`PACK_SIZE=1` still emits the same 45 `oarsub` commands as before" — diff the
  mocked output against the previous revision of the submitter.
- `run_experiment_pack.sh` is testable off-cluster by putting stub `nvidia-smi`
  and `python` on `PATH`: the stub GPU decides the slot count, and a stub trainer
  that fails for one seed exercises the failure isolation and the `.pack_done`
  resume path.
