#!/usr/bin/env bash
# Finding a config in arg_files/ and turning it into flags for
# training/new_train.py. `source` this file; it defines functions only.
#
# One copy for every launcher, so a config named three different ways is the same
# file everywhere and its flags reach python identically however it was started.

ARGS_FILE_DIR="${ARGS_FILE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../arg_files" && pwd)}"

# Config name -> path to it. Accepts all three spellings a caller may type:
#
#   arg_files/archive/dpt01.md   a path, taken as given
#   dpt01                        a bare stem
#   dpt01.md                     a filename
#
# A path that exists is returned unchanged (relative stays relative), because
# run_cluster.sh needs the project-relative form to rsync it and to name it on
# the far side.
resolve_args_file() {
    local name="$1"

    if [[ -f "${name}" ]]; then
        printf '%s\n' "${name}"
        return 0
    fi
    if [[ -f "${ARGS_FILE_DIR}/${name}.md" ]]; then
        printf '%s\n' "${ARGS_FILE_DIR}/${name}.md"
        return 0
    fi
    if [[ -f "${ARGS_FILE_DIR}/${name}" ]]; then
        printf '%s\n' "${ARGS_FILE_DIR}/${name}"
        return 0
    fi
    # Configs live in per-family subdirectories (arg_files/<family>/<label>.md), so a
    # bare stem is also looked up one level down. Labels are unique across the tree;
    # two hits would mean two configs claiming one label, which is refused.
    local stem="${name%.md}"
    local matches=()
    mapfile -t matches < <(find "${ARGS_FILE_DIR}" -mindepth 2 -type f -name "${stem}.md" 2>/dev/null)
    if (( ${#matches[@]} == 1 )); then
        printf '%s\n' "${matches[0]}"
        return 0
    fi
    if (( ${#matches[@]} > 1 )); then
        printf 'Ambiguous config name %s: %s\n' "${name}" "${matches[*]}" >&2
    fi
    return 1
}

# Label -> its family: the arg_files/ subdirectory holding <label>.md, or "unsorted".
# Every result tree (run/, test_metrics/, models/, script_logs/, graphics/) files a
# label under <tree>/<family>/<label>/. Same rule as training/results_layout.py's
# label_family(); keep the two in step.
label_family() {
    local label="$1"
    local match
    match="$(find "${ARGS_FILE_DIR}" -mindepth 2 -type f -name "${label}.md" 2>/dev/null | sort | head -n 1)"
    if [[ -z "${match}" ]]; then
        printf 'unsorted\n'
        return 0
    fi
    match="${match#"${ARGS_FILE_DIR}"/}"
    printf '%s\n' "${match%%/*}"
}

# The "--" lines of a config, one per line, with a long value allowed to wrap:
# a line indented with leading whitespace right after a "--flag=value" line is
# joined onto it (comma-separated, so a --x=a,b, / c,d pair of lines becomes
# --x=a,b,c,d whether or not the break itself carries a comma). Any other line
# -- unindented, or indented with no flag currently open -- is commentary and is
# ignored, which is what lets a config carry its own rationale above the flags.
#
# Quotes around a value are stripped. Bash does not re-interpret quote characters
# that come out of a variable, so --pool_type="gem" would otherwise reach
# read_configuration.py with the quotes still attached and fail its pool_type
# check. The cluster path got away without this only because its flags are
# spliced into a command the compute node runs through `bash -c`, which strips
# them there; stripping here reaches the same python argv by one route instead of
# two. The one case this could not survive is a quoted value containing a space,
# and no config has one.
args_file_flag_lines() {
    awk '
        function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
        {
            line = $0
            if (line ~ /^--/) {
                if (havePending) { print pending }
                eq = index(line, "=")
                if (eq > 0) {
                    name = substr(line, 1, eq)
                    val = substr(line, eq + 1)
                    sub(/^"/, "", val)
                    sub(/"$/, "", val)
                    pending = name val
                    havePending = 1
                } else {
                    print line
                    havePending = 0
                }
            } else if (havePending && line ~ /^[ \t]+[^ \t]/) {
                frag = trim(line)
                if (frag != "") {
                    sub(/,+$/, "", pending)
                    sub(/^,+/, "", frag)
                    pending = pending "," frag
                }
            } else {
                if (havePending) { print pending }
                havePending = 0
            }
        }
        END { if (havePending) print pending }
    ' "$1"
}

# The same flags as one line, ready to be word-split into python's argv.
args_file_flags() {
    args_file_flag_lines "$1" | tr '\n' ' '
}

# Is a flag present in the config? Matched as a whole flag, so --cold_split does
# not also match a hypothetical --cold_split_something.
args_file_has_flag() {
    grep -qE "^${2}([[:space:]=]|\$)" "$1"
}
