"""Fornece a janela única compartilhada pelos testes de GUI."""

from collections.abc import Iterator

import pytest

from symlink_generator.main import App, build_app


@pytest.fixture(scope="session")
def session_app() -> Iterator[App]:
    """Monta uma única janela para a sessão inteira de testes."""
    # Uma janela só: o ttkbootstrap 2.x aceita uma raiz viva por processo, e no Windows
    # criar e destruir várias raizes seguidas falha de forma intermitente ao ler o init.tcl.
    built = build_app()

    try:
        yield built
    finally:
        built.root.destroy()


@pytest.fixture
def app(session_app: App) -> Iterator[App]:
    """Entrega a janela limpa e devolve o callback original do botão ao final."""
    original_callback = session_app.view._submit_callback
    assert original_callback is not None
    session_app.view.reset_form()

    try:
        yield session_app
    finally:
        session_app.view.bind_submit(original_callback)
        session_app.view.reset_form()
