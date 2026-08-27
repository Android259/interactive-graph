#!/usr/bin/env bash
# Writes graphics/<label>/ (plots via generate_config_graphics.sh) and/or
# graphics/<label>/<label>.md (analysis/summarize_label.py +
# analysis/full_label_report.py) for one label.
#
# The single implementation of "what --graphics/--summarize actually does",
# shared by run_local.sh (fires the moment that label's own jobs finish),
# run_cluster.sh (fires once this cluster's queue drains) and
# wait_and_sync.sh's pending_reports handoff (fires on whichever computer's
# wait_and_sync.sh next sees the cluster idle, possibly a different one than
# submitted) -- one place to fix the report format instead of three.
#
# Usage: generate_label_report.sh <label> <seeds_csv> <do_graphics 0|1> <do_summarize 0|1>
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

label="$1"
seeds_csv="$2"
do_graphics="$3"
do_summarize="$4"

(( do_graphics || do_summarize )) || exit 0

mkdir -p "${PROJECT_ROOT}/graphics/${label}"

# Every caller (run_cluster.sh, wait_and_sync.sh's pending_reports handoff)
# already branches on this script's exit status to decide whether to leave a
# label queued for retry -- see their own "leaving its marker queued for
# retry" handling. That only works if a section failing below actually makes
# it here instead of being fully absorbed into the .md text: each section
# below still gets its resilient, human-readable "(failed) ..." text in the
# report (one broken section, or one broken label, must not cost every OTHER
# section/label its own report), but `failed` tracks whether that happened so
# the exit code -- checked, not the report text -- tells the caller the truth.
failed=0

if (( do_graphics )); then
    # No .log kept: generate_config_graphics.sh's own stdout/stderr is progress
    # narration, not something the summary needs, and its real output is the
    # graphics files themselves. Discarded, not redirected to a file -- a
    # failure is still visible from the exit code below.
    if bash "${PROJECT_ROOT}/scripts/generate_config_graphics.sh" "${label}" \
            > /dev/null 2>&1; then
        printf 'Graphics written under graphics/%s/.\n' "${label}"
    else
        printf 'generate_config_graphics.sh failed for %s (rerun it directly to see why).\n' \
            "${label}" >&2
        failed=1
    fi
fi

if (( do_summarize )); then
    summary_path="${PROJECT_ROOT}/graphics/${label}/${label}.md"
    summarize_failed=0
    full_report_failed=0
    {
        printf '# %s\n\n' "${label}"
        printf '## Summary (analysis/summarize_label.py)\n\n```\n'
        "${PROJECT_ROOT}/scripts/env.sh" python3 "${PROJECT_ROOT}/analysis/summarize_label.py" "${label}" --by-groups 2>&1 \
            || { printf '(summarize_label.py exited non-zero; output above, if any, is what it printed before failing)\n'; summarize_failed=1; }
        printf '```\n\n'
        # AUC against the chemistry null model and the in-sample increment, from
        # analysis/full_label_report.py -- reads model checkpoints under
        # models/<label>/. Its own stdout mixes two things: dataset-construction/
        # checkpoint-scoring narration ("lipid class holdout for X...", "seed0
        # epoch120 : scored...") ahead of the actual result tables, then the
        # tables themselves, each split introduced by a line of the form
        # "########## split = valid ##########" (analysis/full_label_report.py's
        # run_report). Everything before the first such line is the narration --
        # cut there instead of embedding it, same "tables, not logs" rule as the
        # summary above.
        #
        # One run, on whatever --label's own args file trains with --
        # --good_descriptors/--bad_descriptors resolved by analysis/
        # full_label_report.py's own --features default (falls back to the 4
        # lipid-only pair_descriptor tokens for a label that sets neither flag).
        # No separate tanimoto baseline run: the null model this label is judged
        # against is the one built from the SAME descriptor set the network
        # itself was trained to see, not a fixed, label-independent guess -- see
        # analysis/full_label_report.py --features. The null model is cached
        # across labels by --features-label (analysis/null_model.py CACHE_PATH):
        # every label sharing a resolved --features set and coldsplit params
        # gets the SAME chemistry null model, so only the first label calling
        # full_label_report.py for a given (features-label, family, seed, share,
        # ratio, split) actually recomputes it. full_label_report.py's own
        # output already states which features were resolved and used.
        printf '## AUC vs chemistry null model, in-sample increment\n\n'
        if full_report_out=$("${PROJECT_ROOT}/scripts/env.sh" python3 "${PROJECT_ROOT}/analysis/full_label_report.py" \
                --label "${label}" --seeds="${seeds_csv}" 2>&1); then
            printf '```\n'
            printf '%s\n' "${full_report_out}" | sed -n '/^##########/,$p'
            printf '```\n'
        else
            printf 'Failed: %s -- rerun for the full output: `python3 analysis/full_label_report.py --label %s --seeds=%s`\n' \
                "$(printf '%s\n' "${full_report_out}" | tail -n1)" \
                "${label}" "${seeds_csv}"
            full_report_failed=1
        fi
    } > "${summary_path}"
    printf 'Summary written to %s.\n' "${summary_path#"${PROJECT_ROOT}"/}"
    (( summarize_failed || full_report_failed )) && failed=1
fi

# Non-zero here does NOT mean nothing was written -- graphics/<label>/ and its
# .md (with "(failed) ..." text in whichever section broke) are already on
# disk either way. It means what it has always meant to run_cluster.sh/
# wait_and_sync.sh's own retry handling: don't treat this label as done.
exit "${failed}"
