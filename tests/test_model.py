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
