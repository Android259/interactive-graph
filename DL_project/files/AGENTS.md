# files/ Contract

Human-readable documents: proposals, measurement writeups, architecture notes,
report cards for finished experiment batches. Nothing here is read by training
or `analysis/` code — these are for people (and agents) to read, not for the
pipeline to consume. Written to survive a plain `git clone`, so treat every
prompt below as text to copy verbatim into a task, not as a description of one.

## Prompt: comprehensive analysis of a finished run batch

Use when a set of cluster jobs (one or more `scripts/arg_files/*.md` labels,
run with `--graphics --summarize`) has finished and the ask is "what happened,
in which direction do we go" — not a from-scratch investigation. Saves the
exploration this project's layout otherwise costs every time: which files
hold what, which metric is authoritative, what the log format actually is.

```
Analyze the finished run(s) for label(s) <LABEL1[, LABEL2, ...]> against
baseline <BASELINE_LABEL>. Comprehensive, evidence-grounded — if some variant
is worse than baseline, explain why FROM THE EVIDENCE; if the evidence does
not support a specific mechanism, say the worsening is unexplained rather than
guessing. Look at: gradient (see note below), the sensitivity/specificity gap
AND the train/valid/test generalization gap, loss, the descriptor/feature set
each config actually uses, and the training dynamics over the whole run (not
just the final epoch).

Data sources, in order:
1. `metrics_summary.csv` — canonical aggregated table (built by
   analysis/build_metrics_table.py + friends, see analysis/AGENTS.md). Filter
   to these labels. RANK BY TEST METRICS PER EXCLUDED GROUP, never validation
   -- validation is for early stopping/model selection only, per this
   project's own convention.
2. `graphics/<label>/<label>.md` — already-generated per-label writeup from
   `--graphics --summarize`. Read it, but verify its numbers against
   metrics_summary.csv rather than trusting it blind.
3. `script_logs/<label>_seeds*/<excluded_group>/*_seedN_ep*.log` — per-(group,
   seed) raw log. Format: repeated
       EPOCH k:
       VALIDATION
       valid epoch balanced_accuracy: <float>
   blocks (this is the per-epoch training-dynamics trace -- read it for noise/
   oscillation/flatness, not just the final number), followed by ONE final
   TEST block:
       accuracy: <f>
       sensitivity: <f>
       precision: <f>
       specificity: <f>
       IoU: <f>
       FAR: <f>
       F1: <f>
       balanced_accuracy: <f>
       loss: <f>
   There is NO gradient-norm logging in these files. If gradient evidence is
   genuinely needed, `analysis/geometric_edge_attention_diagnostics.py` can
   recompute real (not fabricated) gradient norms post-hoc from
   `--save_model_in_dynamics` checkpoints under
   `models/<label>/groups_<group>/dynamics/`; only report gradient claims
   backed by its actual output.
4. `files/descriptor_catalog.md` (which descriptors/edge-geometry columns
   each label's flags actually turn on) and the architecture source
   (`architecture/*.py`) for what a flag mechanically changes.

Write the result to a new `files/*.md` file, in the style of the existing
files there (technical, evidence-grounded, concrete file/line/number
references, no generic ML-checklist filler). Give an explicit directional
recommendation only if asked for one; otherwise present findings/options and
leave the priority call to the user.
```

## Prompt: proposals for architecture or descriptor-set changes

Use for "what could hypothetically be improved" requests. This is a design
question, not a metrics comparison — the user can and will compare existing
run tables themselves; producing another table comparison here has burned
tokens for nothing before.

```
Propose concrete, hypothetical changes to <COMPONENT> (architecture piece or
descriptor set) aimed at <GOAL — generalization / signal / stability / a
specific failure mode>. Required steps, in order:
1. Read the actual feature/architecture construction code (not just the
   arg-file flag name) to know precisely what is being changed.
2. Do at least 2-3 targeted WebSearch/WebFetch queries against the relevant
   domain literature (structural biology / geometric deep learning / whatever
   applies) before writing proposals -- cite sources. Do not skip this: a
   proposal with no literature grounding and no code-level reasoning is not
   an answer to this kind of request.
3. Reason concretely about which sub-components are likely doing what
   physically -- which carry the target signal vs. which are nuisance/
   identity-correlated -- using this project's own measured analogues (e.g.
   files/descriptor_catalog.md's per-descriptor eta^2-by-family table) as the
   template for the kind of reasoning expected, even where the specific
   component in question has not itself been measured yet.
4. Give concrete, testable proposals, each with: the mechanism by which it
   should help, and what existing evidence (a run, an ablation, a measured
   eta^2) supports or contradicts it. Do not invent support that is not
   actually in the data/logs.
5. Do not rank/prioritize the proposals unless the user explicitly asked for
   a directional conclusion -- present the findings and options, priority is
   the user's call.
```

## Cluster launch command template

Once an analysis above lands on next-step configs, hand back a ready-to-run
launch line, not just bare filenames (see `scripts/launch/run_cluster.sh
--help` / its usage banner for the full flag set):

```
bash scripts/run_<CLUSTER_NAME>.sh --graphics --summarize --no_groups=<GROUP1>,<GROUP2> <label1> <label2> <label3>
```

- `<CLUSTER_NAME>`: `bigfoot` or `kraken` (`scripts/run_bigfoot.sh` /
  `scripts/run_kraken.sh` are the two entry points; both just set
  `CLUSTER_NAME` and exec `scripts/launch/run_cluster.sh`).
- `<label*>`: bare `scripts/arg_files/<label>.md` basenames (no path, no
  `.md`), space-separated, all on one line -- multiple labels queue together
  under one shared OAR queue/drain and run concurrently.
- `--graphics --summarize`: waits for the whole batch to drain once, then
  writes `graphics/<label>/<label>.md` and appends to `metrics_summary.csv`
  per label -- include these unless the user asked for a bare submit.
- `--no_groups=A,B`: skip specific excluded groups (default: all 9 canonical
  ones) -- use when a prior batch already covered them and only the
  remaining groups need this config. `--groups=A,B` is the inverse (run only
  these). `--seeds=0,1,2` narrows seeds (default `0,1,2,3,4`).
- Never run this command yourself -- it queues real cluster jobs. Hand it to
  the user to run.
