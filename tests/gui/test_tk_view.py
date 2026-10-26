"""Exercita a janela Tk real, sem abrir nenhum diálogo modal."""

import tkinter as tk
from collections.abc import Iterator
from tkinter import messagebox

import pytest

from symlink_generator.application.create_symlink import CreateSymlinkCommand
from symlink_generator.main import App, build_app, main
from symlink_generator.presentation.messages import INITIAL_STATUS

pytestmark = pytest.mark.gui

GENERIC_ERROR_MESSAGE = "Ocorreu um erro inesperado. Detalhes no log."


@pytest.fixture
def app() -> Iterator[App]:
    """Monta a janela do app e garante o destroy mesmo quando o teste falha."""
    try:
        built = build_app()
    except tk.TclError as exc:
        # Sem display não há como montar janela: o teste é pulado, não reprovado.
        pytest.skip(f"sem display para o Tk: {exc}")

    try:
        yield built
    finally:
        built.root.destroy()


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

    def explode(_path: object) -> bool:
        message = "falha inesperada de propósito"
        raise RuntimeError(message)

    monkeypatch.setattr(
        "symlink_generator.infrastructure.local_filesystem.LocalFileSystem.exists",
        explode,
    )
    app.view.fill(
        CreateSymlinkCommand(
            source="C:\\tmp\\origem.txt",
            destination="C:\\tmp\\destino",
            link_name="",
            overwrite=False,
        ),
    )

    app.view.submit_button.invoke()

    assert dialogs == [("Erro", GENERIC_ERROR_MESSAGE)]


def test_main_smoke_test_returns_zero() -> None:
    """Monta, atualiza e fecha a janela pelo modo smoke test."""
    assert main(["--smoke-test"]) == 0
