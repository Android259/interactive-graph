#!/usr/bin/env bash
# One shared SSH connection per cluster, opened once and reused by everything
# that follows. `source` this file after cluster_common.sh, which supplies
# SSH_CONTROL_PATH and remote.
#
# Why share one: every hop to bigfoot or kraken goes through the gricad jump
# host, and negotiating a fresh connection there costs seconds. A round of the
# watcher makes about six of them, so the difference is the difference between a
# poll that finishes and one that is still connecting when the next is due.
#
# The jump host resets the first attempt now and then (see the retry below), so
# every caller needs the same handling; that is why this is one file rather than
# a few lines repeated in each.

SSH_CONNECT_TIMEOUT="${SSH_CONNECT_TIMEOUT:-20}"
SSH_CONTROL_PERSIST="${SSH_CONTROL_PERSIST:-30m}"
SSH_MASTER_ATTEMPTS="${SSH_MASTER_ATTEMPTS:-3}"

# Is a usable shared connection already up?
#
# `-O check` must never block: without BatchMode and a timeout, a stale or
# half-dead control socket makes it fall through to a fresh jump-host connect
# that hangs forever with no terminal to answer, freezing the caller. `timeout`
# caps that -- a non-zero answer here only means "no usable connection", and the
# caller opens one.
ssh_master_alive() {
    timeout 15 ssh -S "${SSH_CONTROL_PATH}" -o BatchMode=yes \
        -o ConnectTimeout=10 -O check "${remote}" >/dev/null 2>&1
}

# Reuse the shared connection, or open one.
#
#   $1  1 (default) to allow an interactive password prompt if the key is
#       refused; 0 to force key-only, which is what an unattended caller needs so
#       it can never hang on a prompt nobody can answer.
#
# Taken under a lock, so two launchers starting at once open one connection
# between them rather than racing to create the same socket.
ensure_ssh_master() {
    local allow_password="${1:-1}"
    local batch_opt=() attempt status=1

    [[ "${allow_password}" == "1" ]] || batch_opt=(-o BatchMode=yes)

    {
        flock 9
        if ssh_master_alive; then
            status=0
        else
            # The jump host occasionally resets the very first attempt
            # ("Connection closed by UNKNOWN port 65535") even when the network
            # is fine, so retry rather than lose a whole poll interval to one
            # flaky attempt.
            for attempt in $(seq 1 "${SSH_MASTER_ATTEMPTS}"); do
                if ssh -M -S "${SSH_CONTROL_PATH}" \
                    "${batch_opt[@]+"${batch_opt[@]}"}" \
                    -o ConnectTimeout="${SSH_CONNECT_TIMEOUT}" \
                    -o ControlPersist="${SSH_CONTROL_PERSIST}" \
                    -o ServerAliveInterval=30 \
                    -o ServerAliveCountMax=10 \
                    -fN "${remote}"
                then
                    status=0
                    break
                fi
                printf 'Connection attempt %d/%s to %s failed; retrying.\n' \
                    "${attempt}" "${SSH_MASTER_ATTEMPTS}" "${remote}" >&2
                sleep 3
            done
        fi
    } 9>"${SSH_CONTROL_PATH}.lock"

    return "${status}"
}

# The arguments every later ssh and rsync should carry, so they all travel over
# the shared connection instead of opening their own.
#
# Sets two globals rather than printing, because one is an array (ssh) and one is
# a single string (rsync -e takes a command line).
ssh_set_transport() {
    ssh_args=(-S "${SSH_CONTROL_PATH}" -o BatchMode=yes
              -o ConnectTimeout="${SSH_CONNECT_TIMEOUT}")
    rsync_ssh="ssh -S ${SSH_CONTROL_PATH} -o BatchMode=yes -o ConnectTimeout=${SSH_CONNECT_TIMEOUT}"
}

# Shut the shared connection down. Only for a caller that opened one nobody else
# is using -- a watcher's connection must outlive any single command, so nothing
# in the normal path calls this.
close_ssh_master() {
    ssh -S "${SSH_CONTROL_PATH}" -O exit "${remote}" >/dev/null 2>&1 || true
}
