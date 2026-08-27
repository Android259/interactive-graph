#!/usr/bin/env bash
# The project's python, from anywhere, without remembering where conda lives.
#
# Analysis and preprocessing scripts import torch, which not every system
# python3 has. The training path already solved this (run_local.sh and
# tools/parameters.sh both source lib/activate_training_env.sh, warning and
# falling back to whatever python3 is on PATH when conda isn't there), but
# nothing solved it for the one-off command -- so this file is that entry
# point, and it sources the same helper the same way rather than repeating the
# conda search and hard-failing a fourth way.
#
# Three ways to use it:
#
#     scripts/env.sh python3 analysis/null_model.py --split valid
#         run one command in the env and exit with its status
#
#     source scripts/env.sh
#         activate the env in THIS shell, for a session of several commands
#
#     scripts/env.sh
#         print which interpreter you would get, and what it has
#
# It deliberately does not cd: project scripts resolve their own paths from
# __file__, so a command keeps running where you typed it. What it does export
# is PYTHONPATH, so `python3 -c 'import dataloader...'` works from any directory.
#
# For a first-time setup that CREATES the env when it is missing, use
# tools/enter_project_env.sh instead; this file only activates an existing one
# and warns (rather than failing) when there isn't one to activate.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Sourced or executed: the difference decides whether a trailing command is
# expected at all.
_env_sh_sourced=0
[[ "${BASH_SOURCE[0]}" != "$0" ]] && _env_sh_sourced=1

_env_sh_conda_active=0
if [[ "${CONDA_DEFAULT_ENV:-}" != "Kalinin_project_LP" ]]; then
    # Same activation, and same fallback, as run_local.sh and parameters.sh:
    # warn and keep going with whatever python3 is on PATH rather than
    # hard-fail. Some machines genuinely have no conda and still have every
    # package these scripts need on the system python3.
    if source "${SCRIPT_DIR}/lib/activate_training_env.sh"; then
        _env_sh_conda_active=1
    else
        printf 'Could not activate Kalinin_project_LP (create it with: source %s/tools/enter_project_env.sh); using current python3: %s\n' \
            "${SCRIPT_DIR}" "$(command -v python3 || echo 'not found')" >&2
    fi
else
    _env_sh_conda_active=1
fi

export PROJECT_ROOT
export PYTHONPATH="${PROJECT_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

# torch and rdkit disagree about libstdc++, and the loser is whoever imports
# second. The torch wheel is built against the SYSTEM libstdc++ and loads
# /usr/lib/x86_64-linux-gnu/libstdc++.so.6 (3.4.30 on this Debian); rdkit is
# built against the env's own (3.4.34) and needs at least 3.4.31. A soname is
# loaded once per process, so `import torch; import rdkit` dies on
# "GLIBCXX_3.4.31 not found" while `import rdkit; import torch` is fine --
# a failure that depends on the order of two import lines.
#
# Forcing the env's copy fixes it in both orders: 3.4.34 is backward compatible,
# and torch runs on it unchanged (verified: matmul, cuda build string, rdkit
# fingerprints, all in one process). LD_PRELOAD rather than putting
# ${CONDA_PREFIX}/lib on LD_LIBRARY_PATH on purpose -- that would shadow EVERY
# system library with the env's, which is the usual way a conda env starts
# breaking unrelated binaries. Here exactly one library is overridden.
#
# Guarded on the file existing, so an env built without its own libstdc++ (or a
# cluster whose system copy is already new enough) is left alone.
if [[ -n "${CONDA_PREFIX:-}" && -e "${CONDA_PREFIX}/lib/libstdc++.so.6" ]]; then
    export LD_PRELOAD="${CONDA_PREFIX}/lib/libstdc++.so.6${LD_PRELOAD:+:${LD_PRELOAD}}"
fi

if (( _env_sh_sourced )); then
    if (( _env_sh_conda_active )); then
        printf 'Kalinin_project_LP active: %s\n' "$(command -v python3)"
    else
        printf 'Kalinin_project_LP not available; using current python3: %s\n' "$(command -v python3)"
    fi
    unset _env_sh_sourced _env_sh_conda_active
    return 0
fi

unset _env_sh_sourced _env_sh_conda_active

if (( $# == 0 )); then
    printf 'env      : %s\n' "${CONDA_DEFAULT_ENV:-none}"
    printf 'python3  : %s\n' "$(command -v python3 || echo 'not found')"
    python3 - <<'PY'
import importlib
import sys

print(f"version  : {sys.version.split()[0]}")
for module in ("torch", "numpy", "pandas", "scipy", "rdkit"):
    # Broad except on purpose. A package can be installed and still refuse to
    # import -- a wrong libstdc++ raises ImportError, not ModuleNotFoundError --
    # and that is the case worth naming, not hiding behind a traceback that
    # stops the rest of the report. It is also how the LD_PRELOAD above is
    # checked: without it, rdkit lands here.
    try:
        found = importlib.import_module(module)
    except ModuleNotFoundError:
        print(f"{module:<9}: not installed")
    except Exception as failure:
        print(f"{module:<9}: INSTALLED BUT BROKEN -- {type(failure).__name__}: {failure}")
    else:
        print(f"{module:<9}: {getattr(found, '__version__', 'unknown')}")
PY
    # Said plainly because running this file is the natural thing to try, and it
    # leaves the caller's shell untouched -- a subprocess cannot change its
    # parent's environment. Without this line the report looks like it worked.
    printf '\nThis did NOT change your shell. To enter the env here:\n'
    printf '    source scripts/env.sh\n'
    printf 'Or run one command without entering it:\n'
    printf '    scripts/env.sh python3 analysis/<script>.py\n'
    exit 0
fi

exec "$@"
