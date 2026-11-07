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
