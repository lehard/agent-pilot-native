"""JSON file persistence for a TaskList."""

from __future__ import annotations

import json
from pathlib import Path

from taskbook.model import Task, TaskList


class StorageError(RuntimeError):
    """Raised when the task file cannot be read or has an invalid shape."""


def load(path: Path) -> TaskList:
    if not path.exists():
        return TaskList()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StorageError(f"task file {path} is not valid JSON: {exc}") from exc
    if not isinstance(raw, list):
        raise StorageError(f"task file {path} must contain a JSON list")
    return TaskList(tasks=[Task(**item) for item in raw])


def save(task_list: TaskList, path: Path) -> None:
    data = [
        {"id": t.id, "title": t.title, "priority": t.priority, "done": t.done}
        for t in task_list.tasks
    ]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
