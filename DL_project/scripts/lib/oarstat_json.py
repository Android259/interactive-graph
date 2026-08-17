#!/usr/bin/env python3
"""Read `oarstat -J -f` output on stdin and print the two things the watcher needs.

    oarstat -J -f -u USER | python3 oarstat_json.py jobs
        job_id <TAB> name <TAB> stdout_file, one job per line

    oarstat -J -f -u USER | python3 oarstat_json.py next-waiting
        job_id <SPACE> scheduled_start_epoch, for the waiting job OAR expects to
        start soonest; nothing at all when OAR has not scheduled one yet

Both used to be shell-embedded Python, in two different files, written twice and
therefore drifting: one of them understood only a flat {"<id>": {...}} payload
while the other walked nested ones too, so the same cluster could produce a
"next waiting job" line in one watcher and not the other.

Every field is looked up under several spellings because `oarstat -J` names them
differently across OAR versions, and a missing field must degrade to "unknown"
rather than to a crash -- this runs inside a poll loop that has to survive
whatever the scheduler says.
"""

import json
import sys
import time

STATE_KEYS = ("state", "job_state", "jobState")
ID_KEYS = ("job_id", "jobId", "id", "Job_Id")
NAME_KEYS = ("name", "job_name", "Job_Name")
STDOUT_KEYS = ("stdout_file", "stdoutFile", "stdout")
START_KEYS = ("scheduledStart", "scheduled_start", "scheduled_start_time")
WAITING_STATES = {"w", "waiting", "tolaunch", "to_launch"}


def first(record, keys, default=""):
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return default


def jobs(payload, inherited_id=None):
    """Every job object in the payload, whatever shape it arrived in.

    A dict may be {"<id>": {...}} or one job object; a list may be a list of job
    objects. Nested payloads are walked too, carrying the id down from the key
    that named them, because that key is sometimes the only place the id appears.
    """
    if isinstance(payload, dict):
        job_id = first(payload, ID_KEYS, inherited_id)
        if any(key in payload for key in STATE_KEYS):
            yield job_id, payload
        for key, value in payload.items():
            child_id = key if str(key).isdigit() else job_id
            yield from jobs(value, child_id)
    elif isinstance(payload, list):
        for value in payload:
            yield from jobs(value, inherited_id)


def parse_epoch(value):
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if seconds > 0 else None


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("jobs", "next-waiting"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if sys.argv[1] == "jobs":
        for job_id, job in jobs(payload):
            name = first(job, NAME_KEYS)
            stdout_file = first(job, STDOUT_KEYS)
            if name or stdout_file:
                print(f"{job_id}\t{name}\t{stdout_file}")
        return 0

    now = time.time()
    candidates = []
    for job_id, job in jobs(payload):
        if str(first(job, STATE_KEYS)).lower() not in WAITING_STATES:
            continue
        start = parse_epoch(first(job, START_KEYS, 0))
        # A start already in the past is a stale estimate, not a prediction.
        if start is not None and start >= now - 60:
            candidates.append((start, str(job_id or "?")))
    if candidates:
        start, job_id = min(candidates)
        print(job_id, round(start))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
