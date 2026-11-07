import pytest

from taskbook import storage
from taskbook.model import TaskList


def test_missing_file_is_empty_list(tmp_path):
    assert storage.load(tmp_path / "none.json").tasks == []


def test_roundtrip(tmp_path):
    path = tmp_path / "t.json"
    tl = TaskList()
    tl.add("write tests", "high")
    tl.complete(1)
    storage.save(tl, path)
    loaded = storage.load(path)
    assert loaded.tasks[0].title == "write tests"
    assert loaded.tasks[0].done is True


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "t.json"
    path.write_text("{oops", encoding="utf-8")
    with pytest.raises(storage.StorageError, match="not valid JSON"):
        storage.load(path)


def test_legacy_list_loads_and_upgrades(tmp_path):
    path = tmp_path / "t.json"
    path.write_text('[{"id": 1, "title": "a", "priority": "low", "done": true}]', encoding="utf-8")
    tl = storage.load(path)
    assert tl.tasks[0].done and tl.tasks[0].completed_at is None
    storage.save(tl, path)
    assert '"version": 2' in path.read_text(encoding="utf-8")
    assert storage.load(path).tasks[0].title == "a"


def test_completed_at_roundtrip(tmp_path):
    path = tmp_path / "t.json"
    tl = TaskList()
    tl.add("a")
    tl.complete(1)
    storage.save(tl, path)
    assert storage.load(path).tasks[0].completed_at == tl.tasks[0].completed_at


@pytest.mark.parametrize(
    "text", ['{"version": 3, "tasks": []}', '{"tasks": []}', '"x"', '{"version": 2}', "[1]"]
)
def test_unrecognised_format_raises(tmp_path, text):
    path = tmp_path / "t.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(storage.StorageError, match=path.name):
        storage.load(path)
