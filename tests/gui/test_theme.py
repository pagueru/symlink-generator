"""Confere que a janela usa o tema 2.x, sem nome legado."""

import pytest

from symlink_generator.main import App
from symlink_generator.presentation.theme import THEME_NAME

pytestmark = pytest.mark.gui


def test_window_uses_registered_theme(app: App) -> None:
    """A janela abre com a variante superhero-dark registrada pela API Theme."""
    assert THEME_NAME == "superhero-dark"
    assert app.root.style.theme_use() == THEME_NAME
