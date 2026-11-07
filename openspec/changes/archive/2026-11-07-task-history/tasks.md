# Tasks

## 1. Model

- [x] 1.1 Add optional `completed_at` (UTC ISO 8601, seconds) to `Task`; `complete` sets it
- [x] 1.2 Add `TaskList.history(since)` returning completed tasks with a date, newest first

## 2. Storage

- [x] 2.1 Save as version 2 object with a `tasks` list
- [x] 2.2 Load bare list as version 1; reject other shapes, unknown versions and invalid items with `StorageError`

## 3. CLI

- [x] 3.1 Add `history [--since YYYY-MM-DD]` with explicit error on invalid date
- [x] 3.2 Report `StorageError` as an error naming the file with exit status 1

## 4. Tests and docs

- [x] 4.1 Tests for model, storage (legacy, corrupt, unknown version) and CLI
- [x] 4.2 Document the command and the v2 format in README
