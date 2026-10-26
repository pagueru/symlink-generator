"""Monta a aplicação gráfica e serve de ponto de entrada do app."""

import logging
import sys
from dataclasses import dataclass
from functools import partial
from tkinter import messagebox
from types import TracebackType

import ttkbootstrap as ttk

from symlink_generator.application.create_symlink import CreateSymlinkUseCase
from symlink_generator.infrastructure.local_filesystem import LocalFileSystem
from symlink_generator.presentation.messages import ERROR_TITLE
from symlink_generator.presentation.presenter import SymlinkFormPresenter
from symlink_generator.presentation.tk_view import TkSymlinkView

logger = logging.getLogger(__name__)

THEME_NAME: str = "superhero"
"""Tema escuro aplicado à janela."""

WINDOW_TITLE: str = "Symlink Generator"
"""Título mostrado na barra da janela."""

WINDOW_GEOMETRY: str = "760x220"
"""Tamanho inicial da janela, suficiente para as cinco linhas do formulário."""

UNEXPECTED_ERROR_MESSAGE: str = "Ocorreu um erro inesperado. Detalhes no log."
"""Aviso genérico do diálogo de erro que não tem explicação específica."""

SMOKE_TEST_FLAG: str = "--smoke-test"
"""Argumento que monta e fecha a janela sem entrar no laço de eventos."""

LOG_FORMAT: str = "%(asctime)s - %(module)s:%(lineno)03d - %(levelname)s - %(message)s"
"""Formato de log esperado no arquivo e no console."""


@dataclass
class App:
    """Reúne a janela, a view e o presenter já ligados entre si."""

    root: ttk.Window
    # Janela raiz do ttkbootstrap.

    view: TkSymlinkView
    # Formulário que lê os campos e mostra os diálogos.

    presenter: SymlinkFormPresenter
    # Ponte entre o formulário e o caso de uso.


def build_app() -> App:
    """Monta a janela principal com view, presenter e tratamento de erro ligados."""
    root = ttk.Window(themename=THEME_NAME)
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_GEOMETRY)
    root.minsize(760, 220)

    view = TkSymlinkView(root)
    presenter = SymlinkFormPresenter(
        view=view,
        use_case=CreateSymlinkUseCase(LocalFileSystem()),
    )
    view.bind_submit(partial(_submit_form, view, presenter))

    # Sem console, exceção no callback do Tk morre calada: logar e avisar na tela.
    root.report_callback_exception = _report_unexpected_error  # type: ignore[method-assign]

    return App(root=root, view=view, presenter=presenter)


def main(argv: list[str] | None = None) -> int:
    """Abre a janela e devolve zero ao fechar ou no modo smoke test."""
    _configure_logging()
    arguments = sys.argv[1:] if argv is None else argv
    app = build_app()

    if SMOKE_TEST_FLAG in arguments:
        app.root.update()
        app.root.destroy()
        return 0

    app.root.mainloop()

    return 0


def _configure_logging() -> None:
    """Liga o log em INFO no formato padrão do app."""
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )


def _submit_form(view: TkSymlinkView, presenter: SymlinkFormPresenter) -> None:
    """Envia o formulário preenchido ao presenter."""
    presenter.submit(view.read_command())


def _report_unexpected_error(
    exc: type[BaseException],
    val: BaseException,
    tb: TracebackType | None,
) -> None:
    """Registra o erro inesperado do Tk e avisa a pessoa sem detalhe técnico."""
    logger.error("Erro inesperado no callback da interface", exc_info=(exc, val, tb))
    messagebox.showerror(ERROR_TITLE, UNEXPECTED_ERROR_MESSAGE)
