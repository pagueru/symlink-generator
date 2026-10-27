"""Fornece fixtures comuns e pula os testes de janela quando não há display."""

import os
import sys

import pytest
from fakes import FakeFileSystem

# Sem display só no Linux; em qualquer outro caso, falha do Tk é falha do teste.
NO_DISPLAY = sys.platform.startswith("linux") and not os.environ.get("DISPLAY")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Marca como skip os testes gui quando o Linux roda sem DISPLAY."""
    if not NO_DISPLAY:
        return

    skip_gui = pytest.mark.skip(reason="sem DISPLAY: rode com xvfb-run -a")

    for item in items:
        if "gui" in item.keywords:
            item.add_marker(skip_gui)


@pytest.fixture
def fake_fs() -> FakeFileSystem:
    """Entrega um sistema de arquivos falso vazio."""
    return FakeFileSystem()
