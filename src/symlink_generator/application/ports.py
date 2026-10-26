"""Declara a porta de sistema de arquivos que o caso de uso consome."""

from pathlib import Path
from typing import Protocol


class FileSystemPort(Protocol):
    """Descreve as operações de disco necessárias para criar o symlink."""

    def resolve(self, path_text: str) -> Path:
        """Devolve o caminho absoluto do texto, ou levanta InvalidPathError."""
        ...

    def exists(self, path: Path) -> bool:
        """Informa se o caminho existe, seguindo links."""
        ...

    def lexists(self, path: Path) -> bool:
        """Informa se algo ocupa o caminho, mesmo que o link esteja quebrado."""
        ...

    def is_dir(self, path: Path) -> bool:
        """Informa se o caminho é pasta."""
        ...

    def is_link(self, path: Path) -> bool:
        """Informa se o caminho é symlink ou junction."""
        ...

    def remove_link(self, link_path: Path) -> None:
        """Remove o link sem tocar no que ele aponta."""
        ...

    def create_symlink(self, link_path: Path, points_to: Path, *, is_directory: bool) -> None:
        """Cria o symlink apontando para a origem informada."""
        ...
