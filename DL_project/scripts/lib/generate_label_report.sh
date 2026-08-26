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
    fi
fi

if (( do_summarize )); then
    summary_path="${PROJECT_ROOT}/graphics/${label}/${label}.md"
    {
        printf '# %s\n\n' "${label}"
        printf '## Summary (analysis/summarize_label.py)\n\n```\n'
        "${PROJECT_ROOT}/scripts/env.sh" python3 "${PROJECT_ROOT}/analysis/summarize_label.py" "${label}" --by-groups 2>&1 \
            || printf '(summarize_label.py exited non-zero; output above, if any, is what it printed before failing)\n'
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
        fi
    } > "${summary_path}"
    printf 'Summary written to %s.\n' "${summary_path#"${PROJECT_ROOT}"/}"
fi
