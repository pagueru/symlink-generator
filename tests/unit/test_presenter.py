"""Testa o presenter que liga o formulário ao caso de uso."""

from pathlib import PureWindowsPath

from fakes import FakeFileSystem

from symlink_generator.application.create_symlink import (
    CreateSymlinkCommand,
    CreateSymlinkUseCase,
)
from symlink_generator.presentation.messages import (
    ERROR_TITLE,
    FAILURE_STATUS,
    INITIAL_STATUS,
    SUCCESS_TITLE,
)
from symlink_generator.presentation.presenter import SymlinkFormPresenter

SOURCE = "C:\\origem\\relatorio.xlsx"
DESTINATION = "C:\\destino"
TARGET = PureWindowsPath("C:\\destino\\relatorio.xlsx")


class FakeView:
    """Registra as chamadas que o presenter faz na tela."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []
        self.status: str = INITIAL_STATUS

    def show_error(self, title: str, message: str) -> None:
        self.calls.append(("show_error", title, message))

    def show_info(self, title: str, message: str) -> None:
        self.calls.append(("show_info", title, message))

    def set_status(self, text: str) -> None:
        self.calls.append(("set_status", text))
        self.status = text

    def reset_form(self) -> None:
        self.calls.append(("reset_form",))
        self.status = INITIAL_STATUS


def make_command(*, source: str = SOURCE) -> CreateSymlinkCommand:
    return CreateSymlinkCommand(
        source=source,
        destination=DESTINATION,
        link_name="",
        overwrite=False,
    )


def build_presenter(fake_fs: FakeFileSystem) -> tuple[SymlinkFormPresenter, FakeView]:
    view = FakeView()
    return SymlinkFormPresenter(view, CreateSymlinkUseCase(fake_fs)), view


def test_empty_source_shows_error(fake_fs: FakeFileSystem) -> None:
    presenter, view = build_presenter(fake_fs)
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    result = presenter.submit(make_command(source=""))

    assert result is None
    assert view.calls == [("show_error", ERROR_TITLE, "Informe a origem.")]


def test_success_shows_info_then_resets(fake_fs: FakeFileSystem) -> None:
    presenter, view = build_presenter(fake_fs)
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    result = presenter.submit(make_command())

    assert result is not None
    assert result.target == TARGET
    assert [call[0] for call in view.calls] == ["show_info", "reset_form"]
    assert view.calls[0] == (
        "show_info",
        SUCCESS_TITLE,
        f"Symlink criado com sucesso:\n{TARGET}",
    )


def test_validation_error_keeps_form(fake_fs: FakeFileSystem) -> None:
    presenter, view = build_presenter(fake_fs)
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    result = presenter.submit(make_command())

    assert result is None
    assert [call[0] for call in view.calls] == ["show_error"]
    assert view.status == INITIAL_STATUS


def test_creation_failure_sets_failure_status(fake_fs: FakeFileSystem) -> None:
    presenter, view = build_presenter(fake_fs)
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.errors["create_symlink"] = OSError("disco cheio")

    result = presenter.submit(make_command())

    assert result is None
    assert [call[0] for call in view.calls] == ["set_status", "show_error"]
    assert view.calls[0] == ("set_status", FAILURE_STATUS)
    assert view.status == FAILURE_STATUS
    assert view.calls[1][1] == ERROR_TITLE
    assert "disco cheio" in view.calls[1][2]
