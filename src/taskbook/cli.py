"""Command-line interface: taskbook add|list|done|edit|history|rm."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from taskbook import storage
from taskbook.model import VALID_PRIORITIES, TaskError


def _db_path() -> Path:
    value = os.environ.get("TASKBOOK_FILE")
    if not value:
        raise SystemExit("TASKBOOK_FILE is not set: point it at the JSON file to store tasks in")
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskbook")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("--priority", choices=VALID_PRIORITIES, default="normal")
    lst = sub.add_parser("list", help="list tasks")
    lst.add_argument("--all", action="store_true", help="include completed tasks")
    done = sub.add_parser("done", help="mark a task completed")
    done.add_argument("id", type=int)
    edit = sub.add_parser("edit", help="change a task's title or priority")
    edit.add_argument("id", type=int)
    edit.add_argument("--title")
    edit.add_argument("--priority", choices=VALID_PRIORITIES)
    hist = sub.add_parser("history", help="list completed tasks, newest first")
    hist.add_argument("--since", metavar="YYYY-MM-DD", help="only tasks completed on/after")
    rm = sub.add_parser("rm", help="remove a task")
    rm.add_argument("id", type=int)
    return parser


def format_task(task) -> str:
    mark = "x" if task.done else " "
    return f"[{mark}] {task.id}. {task.title} ({task.priority})"


def _parse_since(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        if len(value) != 10:
            raise ValueError(value)
        return date.fromisoformat(value)
    except ValueError:
        raise TaskError(f"invalid --since {value!r}; expected a date as YYYY-MM-DD") from None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = _db_path()
    try:
        tasks = storage.load(path)
    except storage.StorageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        if args.command == "add":
            task = tasks.add(args.title, args.priority)
            print(f"added {task.id}")
        elif args.command == "list":
            shown = tasks.tasks if args.all else tasks.pending()
            for task in shown:
                print(format_task(task))
            print(f"{len(tasks.pending())} pending")
        elif args.command == "done":
            print(f"completed {tasks.complete(args.id).id}")
        elif args.command == "edit":
            print(f"edited {tasks.edit(args.id, args.title, args.priority).id}")
        elif args.command == "history":
            for task in tasks.history(_parse_since(args.since)):
                print(f"{task.completed_at} {task.id}. {task.title} ({task.priority})")
            return 0
        elif args.command == "rm":
            print(f"removed {tasks.remove(args.id).id}")
    except TaskError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    storage.save(tasks, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
