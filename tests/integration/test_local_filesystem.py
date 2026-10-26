"""Testa o adaptador de sistema de arquivos contra o disco real."""

import sys
from pathlib import Path

import pytest

from symlink_generator.application.create_symlink import (
    CreateSymlinkCommand,
    CreateSymlinkUseCase,
)
from symlink_generator.domain.errors import InvalidPathError, TargetExistsError
from symlink_generator.infrastructure.local_filesystem import LocalFileSystem


def make_command(
    source: Path,
    destination: Path,
    *,
    link_name: str = "",
    overwrite: bool = False,
) -> CreateSymlinkCommand:
    """Monta o comando com os caminhos reais do teste."""
    return CreateSymlinkCommand(
        source=str(source),
        destination=str(destination),
        link_name=link_name,
        overwrite=overwrite,
    )


def test_resolve_invalid_path_raises() -> None:
    with pytest.raises(InvalidPathError):
        LocalFileSystem().resolve("a\x00b")


def test_end_to_end_file_link(tmp_path: Path) -> None:
    source = tmp_path / "origem.txt"
    source.write_text("conteudo original", encoding="utf-8")
    destination = tmp_path / "atalhos"
    destination.mkdir()

    result = CreateSymlinkUseCase(LocalFileSystem()).execute(make_command(source, destination))

    assert result.target == destination / "origem.txt"
    assert result.target.is_symlink()
    assert result.target.read_text(encoding="utf-8") == "conteudo original"


def test_end_to_end_directory_link(tmp_path: Path) -> None:
    source = tmp_path / "projetos"
    source.mkdir()
    (source / "relatorio.txt").write_text("dentro da pasta", encoding="utf-8")
    destination = tmp_path / "atalhos"
    destination.mkdir()

    result = CreateSymlinkUseCase(LocalFileSystem()).execute(make_command(source, destination))

    assert result.is_directory is True
    assert result.target.is_symlink()
    assert (result.target / "relatorio.txt").read_text(encoding="utf-8") == "dentro da pasta"


def test_replace_existing_link(tmp_path: Path) -> None:
    source = tmp_path / "origem.txt"
    source.write_text("novo", encoding="utf-8")
    other = tmp_path / "outro.txt"
    other.write_text("antigo", encoding="utf-8")
    destination = tmp_path / "atalhos"
    destination.mkdir()
    old_link = destination / "origem.txt"
    old_link.symlink_to(other)

    result = CreateSymlinkUseCase(LocalFileSystem()).execute(
        make_command(source, destination, overwrite=True),
    )

    assert result.target.is_symlink()
    assert result.target.resolve() == source.resolve()
    # O arquivo apontado pelo link antigo continua intacto.
    assert other.read_text(encoding="utf-8") == "antigo"


def test_broken_link_counts_as_existing_link(tmp_path: Path) -> None:
    source = tmp_path / "origem.txt"
    source.write_text("novo", encoding="utf-8")
    destination = tmp_path / "atalhos"
    destination.mkdir()
    broken = destination / "origem.txt"
    broken.symlink_to(tmp_path / "nao-existe.txt")

    with pytest.raises(TargetExistsError):
        CreateSymlinkUseCase(LocalFileSystem()).execute(make_command(source, destination))

    assert broken.is_symlink()


@pytest.mark.windows
@pytest.mark.skipif(sys.platform != "win32", reason="junction só existe no Windows")
def test_replace_existing_junction(tmp_path: Path) -> None:
    import _winapi

    source = tmp_path / "projetos"
    source.mkdir()
    other = tmp_path / "outra-pasta"
    other.mkdir()
    destination = tmp_path / "atalhos"
    destination.mkdir()
    junction = destination / "projetos"
    _winapi.CreateJunction(str(other), str(junction))

    result = CreateSymlinkUseCase(LocalFileSystem()).execute(
        make_command(source, destination, overwrite=True),
    )

    assert result.target.is_symlink()
    assert result.target.resolve() == source.resolve()
    assert other.is_dir()
