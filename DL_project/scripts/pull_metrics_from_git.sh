#!/usr/bin/env bash
# Download run metrics -- run/, script_logs/, metrics_summary.csv and
# metrics_analysis.txt -- from the git remote branch onto this machine. The
# mirror of scripts/push_metrics_to_git.sh.
#
#   bash scripts/pull_metrics_from_git.sh
#   DRY_RUN=1 bash scripts/pull_metrics_from_git.sh   # show what would change
#
# Git has priority: for any of these paths that exist on the remote branch,
# the local copy is OVERWRITTEN with the remote version, including discarding
# any uncommitted local edits to it -- this machine is not treated as the
# source of truth for pushed results. Local files under these paths that are
# NOT (yet) on the remote branch are left alone: `git checkout <ref> -- <path>`
# only replaces paths present in <ref>, it never deletes local-only files, so
# results this machine has not pushed yet survive.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

REMOTE="${REMOTE:-origin}"
PULL_BRANCH="${PULL_BRANCH:-kalinina-main-patch-61030}"
DRY_RUN="${DRY_RUN:-0}"

METRICS_PATHS=(run script_logs metrics_summary.csv metrics_analysis.txt)

# Explicit destination refspec: a plain `git fetch origin branch` only
# guarantees FETCH_HEAD is updated, not refs/remotes/origin/branch. Naming the
# destination makes the remote-tracking ref used below reliable regardless of
# git version or existing refspec config.
remote_ref="${REMOTE}/${PULL_BRANCH}"
printf 'Fetching %s (%s)...\n' "${PULL_BRANCH}" "${REMOTE}"
# Leading '+' forces the remote-tracking ref to match the remote exactly, the
# same as a normal configured fetch refspec would -- this is bookkeeping only,
# not a merge, so there is no fast-forward safety to preserve here.
git fetch "${REMOTE}" "+${PULL_BRANCH}:refs/remotes/${remote_ref}"

existing_paths=()
for p in "${METRICS_PATHS[@]}"; do
    # `cmd && arr+=(...)` would exit the whole script under set -e the moment
    # cmd fails once (e.g. metrics_analysis.txt not yet on the remote) -- an
    # if with no else always exits 0, so it can't trip that.
    if git cat-file -e "${remote_ref}:${p}" 2>/dev/null; then
        existing_paths+=("${p}")
    fi
done
if (( ${#existing_paths[@]} == 0 )); then
    printf 'None of %s exist on %s.\n' "${METRICS_PATHS[*]}" "${remote_ref}" >&2
    exit 1
fi

if (( DRY_RUN )); then
    printf 'Dry run -- local changes that would be DISCARDED (git wins) for: %s\n' "${existing_paths[*]}"
    git diff --stat -- "${existing_paths[@]}" || true
    printf '\nFiles that would be added/updated from %s:\n' "${remote_ref}"
    git diff --stat "...${remote_ref}" -- "${existing_paths[@]}" 2>/dev/null \
        || git diff --stat "HEAD" "${remote_ref}" -- "${existing_paths[@]}"
    exit 0
fi

git checkout "${remote_ref}" -- "${existing_paths[@]}"
printf 'Restored from %s: %s\n' "${remote_ref}" "${existing_paths[*]}"
