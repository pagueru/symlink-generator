"""Testa o caso de uso que cria o symlink a partir do pedido da tela."""

from pathlib import PureWindowsPath

import pytest
from conftest import FakeFileSystem

from symlink_generator.application.create_symlink import (
    CreateSymlinkCommand,
    CreateSymlinkUseCase,
)
from symlink_generator.domain.errors import (
    DestinationNotADirectoryError,
    DestinationNotFoundError,
    EmptyPathError,
    InvalidLinkNameError,
    InvalidPathError,
    LinkCreationError,
    LinkNameRequiredError,
    PrivilegeRequiredError,
    SourceNotFoundError,
    TargetExistsError,
    TargetNotALinkError,
)

SOURCE = "C:\\origem\\relatorio.xlsx"
DESTINATION = "C:\\destino"
SOURCE_DIR = "C:\\origem\\projetos"


def make_command(
    *,
    source: str = SOURCE,
    destination: str = DESTINATION,
    link_name: str = "",
    overwrite: bool = False,
) -> CreateSymlinkCommand:
    """Monta o comando com os padrões usados nos testes."""
    return CreateSymlinkCommand(
        source=source,
        destination=destination,
        link_name=link_name,
        overwrite=overwrite,
    )


def test_creates_file_link(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    result = CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert result.target == PureWindowsPath("C:\\destino\\relatorio.xlsx")
    assert result.source == PureWindowsPath(SOURCE)
    assert result.is_directory is False
    assert fake_fs.calls == [
        (
            "create_symlink",
            PureWindowsPath("C:\\destino\\relatorio.xlsx"),
            PureWindowsPath(SOURCE),
            False,
        ),
    ]


def test_creates_directory_link_with_flag(fake_fs: FakeFileSystem) -> None:
    fake_fs.dirs.add(PureWindowsPath(SOURCE_DIR))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    result = CreateSymlinkUseCase(fake_fs).execute(make_command(source=SOURCE_DIR))

    assert result.is_directory is True
    assert fake_fs.calls == [
        (
            "create_symlink",
            PureWindowsPath("C:\\destino\\projetos"),
            PureWindowsPath(SOURCE_DIR),
            True,
        ),
    ]


def test_empty_source(fake_fs: FakeFileSystem) -> None:
    with pytest.raises(EmptyPathError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(source='  ""  '))

    assert error.value.field == "source"


def test_empty_destination(fake_fs: FakeFileSystem) -> None:
    with pytest.raises(EmptyPathError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(destination="   "))

    assert error.value.field == "destination"


def test_unresolvable_path(fake_fs: FakeFileSystem) -> None:
    with pytest.raises(InvalidPathError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(source="C:\\a\x00b"))

    assert error.value.raw == "C:\\a\x00b"


def test_missing_source(fake_fs: FakeFileSystem) -> None:
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    with pytest.raises(SourceNotFoundError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.path == PureWindowsPath(SOURCE)


def test_missing_destination(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))

    with pytest.raises(DestinationNotFoundError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.path == PureWindowsPath(DESTINATION)


def test_destination_is_file(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.files.add(PureWindowsPath(DESTINATION))

    with pytest.raises(DestinationNotADirectoryError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.path == PureWindowsPath(DESTINATION)


def test_invalid_link_name_blocks_before_writing(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    with pytest.raises(InvalidLinkNameError):
        CreateSymlinkUseCase(fake_fs).execute(make_command(link_name="a/b"))

    assert fake_fs.calls == []


def test_source_without_name_requires_link_name(fake_fs: FakeFileSystem) -> None:
    fake_fs.dirs.add(PureWindowsPath("C:\\"))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))

    with pytest.raises(LinkNameRequiredError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(source="C:\\"))

    assert error.value.source == PureWindowsPath("C:\\")


def test_existing_target_without_overwrite(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.files.add(PureWindowsPath("C:\\destino\\relatorio.xlsx"))

    with pytest.raises(TargetExistsError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.path == PureWindowsPath("C:\\destino\\relatorio.xlsx")
    assert fake_fs.calls == []


def test_existing_real_file_with_overwrite_is_refused(fake_fs: FakeFileSystem) -> None:
    target = PureWindowsPath("C:\\destino\\relatorio.xlsx")
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.files.add(target)

    with pytest.raises(TargetNotALinkError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(overwrite=True))

    assert error.value.path == target
    assert fake_fs.calls == []
    assert target in fake_fs.files


def test_existing_link_with_overwrite_is_replaced(fake_fs: FakeFileSystem) -> None:
    target = PureWindowsPath("C:\\destino\\relatorio.xlsx")
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.links.add(target)

    CreateSymlinkUseCase(fake_fs).execute(make_command(overwrite=True))

    assert fake_fs.calls == [
        ("remove_link", target),
        ("create_symlink", target, PureWindowsPath(SOURCE), False),
    ]


def test_remove_failure_maps_to_link_creation_error(fake_fs: FakeFileSystem) -> None:
    target = PureWindowsPath("C:\\destino\\relatorio.xlsx")
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.links.add(target)
    fake_fs.errors["remove_link"] = OSError("arquivo em uso")

    with pytest.raises(LinkCreationError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command(overwrite=True))

    assert error.value.detail == "arquivo em uso"
    assert error.value.target == target
    assert type(error.value) is LinkCreationError


def test_privilege_error_maps_to_privilege_required(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    denied = OSError("privilégio insuficiente")
    denied.winerror = 1314
    fake_fs.errors["create_symlink"] = denied

    with pytest.raises(PrivilegeRequiredError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.detail == "privilégio insuficiente"


def test_other_oserror_maps_to_link_creation_error(fake_fs: FakeFileSystem) -> None:
    fake_fs.files.add(PureWindowsPath(SOURCE))
    fake_fs.dirs.add(PureWindowsPath(DESTINATION))
    fake_fs.errors["create_symlink"] = OSError("disco cheio")

    with pytest.raises(LinkCreationError) as error:
        CreateSymlinkUseCase(fake_fs).execute(make_command())

    assert error.value.detail == "disco cheio"
    assert type(error.value) is LinkCreationError
