# Spec Delta

## Purpose

Lets users see which tasks were completed and when, optionally limited to a period.

## ADDED Requirements

### Requirement: Completion time is recorded
The system SHALL record the date and time at which a task is marked done.

#### Scenario: Marking a task done
- **WHEN** the user runs `taskbook done <id>` on a pending task
- **THEN** the task is stored as done together with the completion date and time

### Requirement: History command
The system SHALL provide `taskbook history` listing completed tasks with their completion date and time, newest first.

#### Scenario: History without filter
- **WHEN** the user runs `taskbook history`
- **THEN** every completed task that has a completion time is listed, most recent first

#### Scenario: History with since
- **WHEN** the user runs `taskbook history --since 2026-01-15`
- **THEN** only tasks completed on or after 2026-01-15 are listed

#### Scenario: Invalid since value
- **WHEN** the user passes a `--since` value that is not a YYYY-MM-DD date
- **THEN** the command exits with an explicit error and a non-zero status

### Requirement: Existing task files remain readable
The system SHALL open task files written by earlier versions without manual user action and without losing tasks.

#### Scenario: Legacy file
- **WHEN** a task file in the previous format is loaded
- **THEN** all tasks are available, and tasks already done have no completion time and are not listed by `history`

### Requirement: Invalid task files are rejected
The system MUST fail with an explicit error, never an empty list, when the task file is corrupt or has an unrecognised format.

#### Scenario: Corrupt file
- **WHEN** the task file is not valid or has an unknown format version
- **THEN** the command exits non-zero with an error naming the file
