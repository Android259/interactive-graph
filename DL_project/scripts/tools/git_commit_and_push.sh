#!/usr/bin/env bash
set -euo pipefail

REMOTE="${REMOTE:-origin}"
PUSH_BRANCH="${PUSH_BRANCH:-kalinina-main-patch-61030}"

if (( $# != 1 )) || [[ -z "$1" ]]; then
    printf 'Usage: bash %s "COMMIT MESSAGE"\n' "${0##*/}" >&2
    printf 'Example: bash %s "scripts"\n' "${0##*/}" >&2
    exit 2
fi

commit_message="$1"

git add .

if git diff --cached --quiet; then
    printf 'Nothing to commit.\n'
    exit 0
fi

git commit -m "${commit_message}"
git push "${REMOTE}" "HEAD:${PUSH_BRANCH}"
