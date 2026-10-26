"""Confere que a versão do pacote acompanha o pyproject."""

import tomllib
from pathlib import Path

import symlink_generator

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def test_version_matches_pyproject() -> None:
    """Falha quando alguém sobe a versão em um lugar e esquece o outro."""
    with PYPROJECT.open("rb") as file:
        project_version = tomllib.load(file)["project"]["version"]

    assert symlink_generator.__version__ == project_version
