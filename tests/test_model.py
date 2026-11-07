import pytest

from taskbook.model import Task, TaskError, TaskList


def test_add_assigns_increasing_ids():
    tl = TaskList()
    assert tl.add("a").id == 1
    assert tl.add("b").id == 2


def test_empty_title_rejected():
    with pytest.raises(TaskError, match="title"):
        TaskList().add("   ")


def test_unknown_priority_rejected():
    with pytest.raises(TaskError, match="priority"):
        Task(id=1, title="x", priority="urgent")


def test_complete_and_pending():
    tl = TaskList()
    tl.add("a")
    tl.add("b")
    tl.complete(1)
    assert [t.id for t in tl.pending()] == [2]


def test_remove_missing_raises():
    with pytest.raises(TaskError, match="no task with id 9"):
        TaskList().remove(9)


def test_complete_sets_completed_at():
    tl = TaskList()
    tl.add("a")
    assert tl.complete(1).completed_at.endswith("Z")


def test_history_filters_and_orders():
    from datetime import date

    tl = TaskList()
    for title in "abcd":
        tl.add(title)
    tl.get(1).done = True  # legacy: no date
    for i, day in ((2, "2026-01-10"), (3, "2026-01-15"), (4, "2026-02-01")):
        tl.get(i).done = True
        tl.get(i).completed_at = f"{day}T12:00:00Z"
    assert [t.id for t in tl.history()] == [4, 3, 2]
    assert [t.id for t in tl.history(date(2026, 1, 15))] == [4, 3]
