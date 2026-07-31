#!/usr/bin/env bash
# Runs ON bigfoot. Targets ONLY jobs whose VALIDATION group is GLTP
# (OAR name matches *_vGLTP_*). GLTP-as-TEST jobs (named *_GLTP_v...) are left
# untouched. It:
#   1) cancels the active validation=GLTP OAR jobs,
#   2) removes them from the pending queue and re-queues the same START folds
#      with the corrected validation group LBP_BPI_CETP (label/variant kept),
#   3) deletes their logs.
#
# Invoke from your laptop (pipes this file to bigfoot; enter the password once):
#   ssh kalinina@bigfoot 'bash -s' < scripts/fix_gltp_validation_jobs.sh
set -u

USER_NAME="${REMOTE_USER:-kalinina}"
PROJECT="$HOME/DL_project"
Q="$PROJECT/.bigfoot_job_queues/active"

# ---- 1) cancel ACTIVE validation=GLTP jobs -----------------------------------
mapfile -t ids < <(oarstat -u "$USER_NAME" | awk '$1 ~ /^[0-9]+$/ {print $1}')
to_del=()
for j in "${ids[@]}"; do
    name=$(oarstat -f -j "$j" |
        awk -F ' = ' 'tolower($1) ~ /(^|[[:space:]])(job_)?name$/ {print $2; exit}')
    case "$name" in
        *vGLTP*) printf 'cancel %s (%s)\n' "$j" "$name"; to_del+=("$j");;
    esac
done
if [ "${#to_del[@]}" -gt 0 ]; then
    oardel "${to_del[@]}"
else
    printf 'No active validation=GLTP jobs.\n'
fi

# ---- 2) rewrite the pending queue under the drain lock -----------------------
mkdir -p "$Q"
exec 8>"$Q/drain.lock"
flock 8
tmp=$(mktemp)
# a) keep existing pending minus the vGLTP lines
if [ -f "$Q/pending.commands" ]; then
    grep -v vGLTP "$Q/pending.commands" > "$tmp" || true
fi
# b) append corrected START commands, derived from the known-good lines:
#    validation group GLTP -> LBP_BPI_CETP everywhere it appears (name, excluded
#    groups, log paths); the test group stays START.
grep -h vGLTP "$Q/submitted.commands" "$Q/pending.commands" 2>/dev/null |
    grep START | sort -u |
    sed 's/vGLTP/vLBP_BPI_CETP/g; s/START,GLTP/START,LBP_BPI_CETP/g; s/val-GLTP/val-LBP_BPI_CETP/g' \
    >> "$tmp"
mv "$tmp" "$Q/pending.commands"
printf 're-queued %s corrected START job(s); pending now %s line(s)\n' \
    "$(grep -c vLBP_BPI_CETP "$Q/pending.commands" 2>/dev/null || echo 0)" \
    "$(wc -l < "$Q/pending.commands")"
flock -u 8

# ---- 3) delete GLTP-validation logs -----------------------------------------
find "$PROJECT/script_logs" -name '*val-GLTP*' -exec rm -f {} + 2>/dev/null || true
printf 'GLTP-validation logs removed.\n'
