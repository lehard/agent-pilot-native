# taskbook

Tiny command-line task tracker, used as a fixture for an autonomous-agent pilot.

    pip install -e . && export TASKBOOK_FILE=~/tasks.json
    taskbook add "buy milk" --priority high && taskbook list --all

`taskbook list` ends with a line `N pending` (count of uncompleted tasks, also with `--all`).

`taskbook edit <id> [--title TEXT] [--priority low|normal|high]` changes a task's title and/or
priority; the id stays the same. It fails (exit 1) if neither option is given, the id does not
exist, or the title is empty.

`taskbook done` records the completion time (UTC). `taskbook history [--since YYYY-MM-DD]` lists
completed tasks with their completion time, newest first; `--since` is inclusive and an invalid
date fails (exit 1). Tasks completed before this feature have no time and are not listed.

The task file is now an object with `version` 2 and a `tasks` list. Old bare-list files open
unchanged and are rewritten as version 2 on the next save; corrupt files or unknown versions fail
with an error naming the file. Older taskbook versions cannot read version 2 files.

Development: `ruff check . && python -m pytest -q`.
Larger changes go through OpenSpec (schema `add-gated`, OpenSpec CLI pinned to 1.16.0):
proposal → specs → design → `add.md` (Architecture Decision Doc) → tasks.
CI job `test` refuses tasks or implementation of a change whose `add.md` lacks the
owner's line `Approved-by: lehard`. Small edits without an OpenSpec change need no ADD.
