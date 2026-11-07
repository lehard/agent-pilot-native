# ADD: Task completion history

## Context

`done` must remember when it happened, and `history` must list completed tasks. The file today is a bare JSON list. Old files must open unchanged and bad files must error explicitly. See proposal.md.

## Options

### Option A: Extend the JSON with a format version and migration

Wrap tasks as `{"version": 2, "tasks": [...]}` and add `completed_at` per task. A bare list is read as v1 and upgraded on next save. Cost: small, no new dependencies, human-readable. Harder later: very large histories or rich queries would need a rewrite.

### Option B: Move to SQLite

Tasks and completions in a database table. Cost: stdlib only, but needs a one-off import of the JSON file and changes the file/env semantics. Makes diffing and manual editing harder; overkill for a tiny tracker.

### Option C: Separate completion journal

Keep the task file as is; append completions to a second file. Cost: two files to keep consistent (removed tasks leave orphans) and partial failure between writes. Harder later: every further field needs yet another file.

## Decision

Option A. It meets every requirement with the least machinery, keeps one file and one source of truth, and the explicit version field gives a clean path for future migrations (including to SQLite if ever needed).

## Risks

- Older versions cannot read v2 files → documented in README; they fail loudly on a dict instead of a list.
- Migration bug loses data → tests with legacy fixtures; the upgrade is written only on a normal save.
- Legacy done tasks lack dates → excluded from history rather than invented.

Approved-by: lehard

## Approval

Approved-by:
