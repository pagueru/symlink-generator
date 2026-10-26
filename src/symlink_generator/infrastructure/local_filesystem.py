"""Implementa a porta de sistema de arquivos sobre o pathlib."""

import os
from pathlib import Path

from symlink_generator.domain.errors import InvalidPathError


class LocalFileSystem:
    """Executa as operações de disco no sistema real."""

    def resolve(self, path_text: str) -> Path:
        """Devolve o caminho absoluto do texto digitado."""
        # No Windows o resolve() aceita caractere nulo e só falha depois, ao criar o link.
        if "\x00" in path_text:
            raise InvalidPathError(path_text)

        try:
            return Path(path_text).expanduser().resolve()
        except (OSError, ValueError) as exc:
            # Texto que o sistema não interpreta (caractere nulo, nome inválido).
            raise InvalidPathError(path_text) from exc

    def exists(self, path: Path) -> bool:
        """Informa se o caminho existe, seguindo links."""
        return path.exists()

    def lexists(self, path: Path) -> bool:
        """Informa se algo ocupa o caminho, mesmo que o link esteja quebrado."""
        return os.path.lexists(path)

    def is_dir(self, path: Path) -> bool:
        """Informa se o caminho é pasta."""
        return path.is_dir()

    def is_link(self, path: Path) -> bool:
        """Informa se o caminho é symlink ou junction."""
        return path.is_symlink() or path.is_junction()

    def remove_link(self, link_path: Path) -> None:
        """Remove o link sem tocar no que ele aponta."""
        # unlink() apaga symlink de pasta e junction sem apagar o destino.
        link_path.unlink()

    def create_symlink(self, link_path: Path, points_to: Path, *, is_directory: bool) -> None:
        """Cria o symlink apontando para a origem informada."""
        link_path.symlink_to(points_to, target_is_directory=is_directory)
