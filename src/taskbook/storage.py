"""JSON file persistence for a TaskList."""

from __future__ import annotations

import json
from pathlib import Path

from taskbook.model import Task, TaskList

VERSION = 2


class StorageError(RuntimeError):
    """Raised when the task file cannot be read or has an invalid shape."""


def load(path: Path) -> TaskList:
    if not path.exists():
        return TaskList()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StorageError(f"task file {path} is not valid JSON: {exc}") from exc
    if isinstance(raw, list):
        items = raw  # version 1: bare list
    elif (
        isinstance(raw, dict)
        and raw.get("version") == VERSION
        and isinstance(raw.get("tasks"), list)
    ):
        items = raw["tasks"]
    else:
        raise StorageError(
            f"task file {path} has an unrecognised format: expected a JSON list "
            f"or an object with version {VERSION} and a tasks list"
        )
    try:
        return TaskList(tasks=[Task(**item) for item in items])
    except (TypeError, ValueError) as exc:
        raise StorageError(f"task file {path} contains an invalid task: {exc}") from exc


def save(task_list: TaskList, path: Path) -> None:
    tasks = [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "done": t.done,
            "completed_at": t.completed_at,
        }
        for t in task_list.tasks
    ]
    data = {"version": VERSION, "tasks": tasks}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
