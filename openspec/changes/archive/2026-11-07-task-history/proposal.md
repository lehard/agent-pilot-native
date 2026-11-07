# Proposal

## Why

Completed tasks cannot be reviewed by period because the completion date is not stored anywhere (Issue #3).

## What Changes

- `taskbook done` records the date and time of completion.
- New command `taskbook history [--since YYYY-MM-DD]` lists completed tasks with their completion timestamps, newest first.
- Existing task files keep opening without manual action; a corrupt or unrecognised file fails with an explicit error.
- The persistent storage format changes (see add.md for the chosen approach).

## Capabilities

### New Capabilities
- `task-history`: recording completion time and listing completed tasks by period.

### Modified Capabilities

## Impact

- `src/taskbook/model.py`, `storage.py`, `cli.py`, tests, README.
- On-disk task file format (migration of existing files).
