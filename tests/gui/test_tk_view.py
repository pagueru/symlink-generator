"""Exercita a janela Tk real, sem abrir nenhum diálogo modal."""

import os
import subprocess
import sys
from collections.abc import Iterator
from tkinter import messagebox

import pytest

from symlink_generator.application.create_symlink import CreateSymlinkCommand
from symlink_generator.main import App, build_app
from symlink_generator.presentation.messages import INITIAL_STATUS

# Sem display só no Linux; em qualquer outro caso, falha do Tk é falha do teste.
NO_DISPLAY = sys.platform.startswith("linux") and not os.environ.get("DISPLAY")

pytestmark = [
    pytest.mark.gui,
    pytest.mark.skipif(NO_DISPLAY, reason="sem DISPLAY: rode com xvfb-run -a"),
]

GENERIC_ERROR_MESSAGE = "Ocorreu um erro inesperado. Detalhes no log."
SMOKE_TIMEOUT_SECONDS = 60


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


def test_build_app_has_title_and_initial_status(app: App) -> None:
    """Confere o título da janela e o status de abertura."""
    assert app.root.title() == "Symlink Generator"
    assert app.view.status_var.get() == INITIAL_STATUS


def test_fill_and_read_command_roundtrip(app: App) -> None:
    """Preenche o formulário e lê de volta o pedido equivalente."""
    command = CreateSymlinkCommand(
        source="C:\\tmp\\origem.txt",
        destination="C:\\tmp\\destino",
        link_name="meu-link",
        overwrite=True,
    )

    app.view.fill(command)

    assert app.view.read_command() == command


def test_reset_form_clears_fields_and_status(app: App) -> None:
    """Limpa campos, checkbox e status depois de um envio bem-sucedido."""
    app.view.fill(CreateSymlinkCommand("a", "b", "c", overwrite=True))
    app.view.set_status("qualquer coisa")

    app.view.reset_form()

    assert app.view.read_command() == CreateSymlinkCommand("", "", "", overwrite=False)
    assert app.view.status_var.get() == INITIAL_STATUS


def test_submit_button_calls_callback(app: App) -> None:
    """Liga um callback no botão e confere que ele dispara no invoke."""
    calls: list[str] = []
    app.view.bind_submit(lambda: calls.append("enviado"))

    app.view.submit_button.invoke()

    assert calls == ["enviado"]


def test_unexpected_callback_error_shows_generic_dialog(
    app: App,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Erro inesperado no callback vira diálogo genérico, sem quebrar o laço."""
    dialogs: list[tuple[str, str]] = []
    monkeypatch.setattr(messagebox, "showerror", lambda *args: dialogs.append(args))

    def explode(_self: object, _path: object) -> bool:
        message = "falha inesperada de propósito"
        raise RuntimeError(message)

    monkeypatch.setattr(
        "symlink_generator.infrastructure.local_filesystem.LocalFileSystem.exists",
        explode,
    )
    app.view.fill(
        CreateSymlinkCommand("C:\\tmp\\origem.txt", "C:\\tmp\\destino", "", overwrite=False),
    )

    app.view.submit_button.invoke()

    assert dialogs == [("Erro", GENERIC_ERROR_MESSAGE)]


def test_entry_point_smoke_test_returns_zero() -> None:
    """Roda o ponto de entrada real num processo à parte e espera saída zero."""
    # Processo próprio: a janela da sessão continua viva e o ttkbootstrap recusa a segunda.
    result = subprocess.run(
        [sys.executable, "-m", "symlink_generator", "--smoke-test"],
        capture_output=True,
        text=True,
        timeout=SMOKE_TIMEOUT_SECONDS,
        check=False,
    )

    assert result.returncode == 0, result.stderr
