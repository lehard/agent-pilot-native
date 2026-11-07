"""Task model and in-memory operations."""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_PRIORITIES = ("low", "normal", "high")


class TaskError(ValueError):
    """Raised when a task operation receives invalid input."""


@dataclass
class Task:
    id: int
    title: str
    priority: str = "normal"
    done: bool = False

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise TaskError("task title must not be empty")
        if self.priority not in VALID_PRIORITIES:
            raise TaskError(
                f"unknown priority {self.priority!r}; expected one of {', '.join(VALID_PRIORITIES)}"
            )


@dataclass
class TaskList:
    tasks: list[Task] = field(default_factory=list)

    def add(self, title: str, priority: str = "normal") -> Task:
        next_id = max((t.id for t in self.tasks), default=0) + 1
        task = Task(id=next_id, title=title, priority=priority)
        self.tasks.append(task)
        return task

    def get(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskError(f"no task with id {task_id}")

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        task.done = True
        return task

    def edit(self, task_id: int, title: str | None = None, priority: str | None = None) -> Task:
        task = self.get(task_id)
        if title is None and priority is None:
            raise TaskError("nothing to edit: pass --title and/or --priority")
        # Validate via a candidate Task so a rejected edit leaves the task untouched.
        candidate = Task(
            id=task.id,
            title=task.title if title is None else title,
            priority=task.priority if priority is None else priority,
            done=task.done,
        )
        task.title = candidate.title
        task.priority = candidate.priority
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        self.tasks.remove(task)
        return task

    def pending(self) -> list[Task]:
        return [t for t in self.tasks if not t.done]
