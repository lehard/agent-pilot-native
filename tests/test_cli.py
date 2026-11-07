import pytest

from taskbook.cli import main


def test_add_list_done(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKBOOK_FILE", str(tmp_path / "t.json"))
    assert main(["add", "buy milk", "--priority", "high"]) == 0
    assert main(["done", "1"]) == 0
    capsys.readouterr()
    assert main(["list", "--all"]) == 0
    assert "[x] 1. buy milk (high)" in capsys.readouterr().out


def test_list_prints_pending_count(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKBOOK_FILE", str(tmp_path / "t.json"))
    assert main(["add", "a"]) == 0
    assert main(["add", "b"]) == 0
    assert main(["done", "1"]) == 0
    capsys.readouterr()
    assert main(["list"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "1 pending"
    assert main(["list", "--all"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "1 pending"


def test_missing_env_fails(monkeypatch):
    monkeypatch.delenv("TASKBOOK_FILE", raising=False)
    with pytest.raises(SystemExit, match="TASKBOOK_FILE"):
        main(["list"])


def test_done_unknown_id_returns_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKBOOK_FILE", str(tmp_path / "t.json"))
    assert main(["done", "5"]) == 1
    assert "no task with id 5" in capsys.readouterr().err


def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("TASKBOOK_FILE", str(tmp_path / "t.json"))


def test_edit_title_and_priority_keeps_id(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["add", "by milk"]) == 0
    assert main(["add", "other"]) == 0
    assert main(["edit", "1", "--title", "buy milk", "--priority", "high"]) == 0
    capsys.readouterr()
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "[ ] 1. buy milk (high)" in out
    assert "[ ] 2. other (normal)" in out


def test_edit_only_priority_keeps_title(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["add", "a"]) == 0
    assert main(["edit", "1", "--priority", "low"]) == 0
    capsys.readouterr()
    assert main(["list"]) == 0
    assert "[ ] 1. a (low)" in capsys.readouterr().out


def test_edit_without_options_fails(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["add", "a"]) == 0
    assert main(["edit", "1"]) == 1
    assert "nothing to edit" in capsys.readouterr().err


def test_edit_unknown_id_returns_error(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["edit", "5", "--title", "x"]) == 1
    assert "no task with id 5" in capsys.readouterr().err


def test_edit_empty_title_rejected_and_task_unchanged(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["add", "a", "--priority", "high"]) == 0
    assert main(["edit", "1", "--title", "  ", "--priority", "low"]) == 1
    assert "title" in capsys.readouterr().err
    assert main(["list"]) == 0
    assert "[ ] 1. a (high)" in capsys.readouterr().out


def test_done_then_history(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    assert main(["add", "a"]) == 0
    assert main(["add", "b"]) == 0
    assert main(["done", "1"]) == 0
    capsys.readouterr()
    assert main(["history"]) == 0
    out = capsys.readouterr().out
    assert "1. a (normal)" in out and "b" not in out
    assert main(["history", "--since", "2999-01-01"]) == 0
    assert capsys.readouterr().out == ""


def test_history_invalid_since(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    for bad in ("yesterday", "2026-1-5", "20260115"):
        assert main(["history", "--since", bad]) == 1
        assert "YYYY-MM-DD" in capsys.readouterr().err


def test_legacy_file_history_excludes_undated(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    (tmp_path / "t.json").write_text(
        '[{"id": 1, "title": "old", "priority": "normal", "done": true}]', encoding="utf-8"
    )
    assert main(["history"]) == 0
    assert capsys.readouterr().out == ""
    assert main(["list", "--all"]) == 0
    assert "[x] 1. old" in capsys.readouterr().out


def test_corrupt_file_errors_naming_file(tmp_path, monkeypatch, capsys):
    _env(tmp_path, monkeypatch)
    (tmp_path / "t.json").write_text('{"version": 9, "tasks": []}', encoding="utf-8")
    assert main(["list"]) == 1
    assert "t.json" in capsys.readouterr().err
