# Design

## Context

Tasks are stored as a bare JSON list of `{id, title, priority, done}` (storage.py). See proposal.md and add.md for the storage decision.

## Goals / Non-Goals

**Goals:**
- Store a completion timestamp per task; migrate old files transparently.

**Non-Goals:**
- Reopening tasks, history of other changes, timezone configuration.

## Decisions

- Task gains optional `completed_at` (ISO 8601, UTC, seconds precision).
- File becomes `{"version": 2, "tasks": [...]}`; a bare list is read as version 1 and rewritten as version 2 on next save.
- Any other shape or unknown version raises `StorageError`.
- `history --since D` compares the UTC completion date to D (inclusive).

## Risks / Trade-offs

- Older taskbook versions cannot read v2 files → acceptable, documented in README.
- Legacy done tasks have no date → excluded from history, not guessed.
