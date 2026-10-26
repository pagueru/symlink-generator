"""Confere onde o app grava o log."""

from pathlib import Path

import pytest

from symlink_generator.main import log_file_path


def test_log_file_path_uses_localappdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Grava o log em %LOCALAPPDATA%\\symlink-generator quando a variável existe."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert log_file_path() == tmp_path / "symlink-generator" / "symlink-generator.log"


def test_log_file_path_falls_back_to_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Usa ~/.local/state quando não há LOCALAPPDATA, fora do Windows."""
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    expected = tmp_path / ".local" / "state" / "symlink-generator" / "symlink-generator.log"
    assert log_file_path() == expected
