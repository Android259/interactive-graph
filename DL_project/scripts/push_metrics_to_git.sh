#!/usr/bin/env bash
# Commit and push run metrics -- run/, script_logs/, metrics_summary.csv and
# metrics_analysis.txt -- to the git remote branch, so results generated on
# this machine are reachable from git and not only via cluster rsync (see
# scripts/update_local.sh / update_clusters.sh, which deliberately skip these
# paths). Mirrored by scripts/pull_metrics_from_git.sh.
#
#   bash scripts/push_metrics_to_git.sh
#   DRY_RUN=1 bash scripts/push_metrics_to_git.sh   # show what would be committed
#
# The commit message lists the job labels (the run/<label>/ and
# script_logs/<label>/ directory names) whose files changed, so the history
# stays legible without opening the diff. Separate from scripts/git_commit_and_push.sh
# (which commits everything with a caller-supplied message) because this
# script's whole point is deriving that message from the changed paths.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

REMOTE="${REMOTE:-origin}"
PUSH_BRANCH="${PUSH_BRANCH:-kalinina-main-patch-61030}"
DRY_RUN="${DRY_RUN:-0}"

METRICS_PATHS=(run script_logs metrics_summary.csv metrics_analysis.txt)

existing_paths=()
for p in "${METRICS_PATHS[@]}"; do
    if [[ -e "${p}" ]]; then
        existing_paths+=("${p}")
    fi
done
if (( ${#existing_paths[@]} == 0 )); then
    printf 'None of the metrics paths exist here: %s\n' "${METRICS_PATHS[*]}" >&2
    exit 1
fi

changed="$(git status --porcelain -- "${existing_paths[@]}")"
if [[ -z "${changed}" ]]; then
    printf 'Nothing to commit under: %s\n' "${existing_paths[*]}"
    exit 0
fi

# `git status --porcelain` prints paths relative to the repo TOPLEVEL, not to
# this script's cwd (the two differ here: the repo root is one level above
# this project directory). Strip that prefix before splitting on '/' so label
# extraction below does not depend on where the project sits inside the repo.
prefix="$(git rev-parse --show-prefix)"
changed_paths="$(
    printf '%s\n' "${changed}" \
        | cut -c4- \
        | sed 's/.* -> //' \
        | sed "s#^${prefix}##"
)"

# Only the SECOND path component is a job label when it names an actual
# directory: run/ and script_logs/ each also hold a few top-level files of
# their own (script_logs/*.pid, *.log, *.queue from the wait/drain/queue
# scripts) that must not be mistaken for job labels.
labels="$(
    printf '%s\n' "${changed_paths}" \
        | awk -F/ '$1 == "run" || $1 == "script_logs" { print $1"/"$2 }' \
        | sort -u \
        | while IFS= read -r rel; do
              # `[[ -d ]] && printf` would return non-zero (and, under set -e,
              # silently kill this whole command substitution) on the first
              # non-directory candidate -- an `if` with no else always exits 0.
              if [[ -d "${rel}" ]]; then
                  printf '%s\n' "${rel#*/}"
              fi
          done
)"

extra_notes=()
if printf '%s\n' "${changed_paths}" | grep -qx 'metrics_summary\.csv'; then
    extra_notes+=("metrics_summary.csv")
fi
if printf '%s\n' "${changed_paths}" | grep -qx 'metrics_analysis\.txt'; then
    extra_notes+=("metrics_analysis.txt")
fi

label_count="$(printf '%s\n' "${labels}" | grep -c . || true)"
if [[ -z "${labels}" && ${#extra_notes[@]} -eq 0 ]]; then
    printf 'Changed files under %s did not match run/<label>/ or script_logs/<label>/, and neither aggregate table changed:\n' "${existing_paths[*]}" >&2
    printf '%s\n' "${changed}" >&2
    exit 1
fi

if (( label_count > 0 )); then
    subject="metrics: ${label_count} job label(s) updated"
else
    subject="metrics: aggregate table update"
fi

message="${subject}"$'\n'
if (( label_count > 0 )); then
    mapfile -t label_arr <<< "${labels}"
    message+=$'\n'"$(printf -- '- %s\n' "${label_arr[@]}")"
fi
if (( ${#extra_notes[@]} )); then
    message+=$'\n'"Also: ${extra_notes[*]}"
fi

printf 'Labels (%s): %s\n' "${label_count}" "${labels:-<none>}"
if (( ${#extra_notes[@]} )); then
    printf 'Also: %s\n' "${extra_notes[*]}"
fi

if (( DRY_RUN )); then
    printf '\nDry run -- would commit and push to %s HEAD:%s with message:\n---\n%s\n---\n' \
        "${REMOTE}" "${PUSH_BRANCH}" "${message}"
    exit 0
fi

git add -- "${existing_paths[@]}"
printf '%s\n' "${message}" | git commit -F -
git push "${REMOTE}" "HEAD:${PUSH_BRANCH}"
