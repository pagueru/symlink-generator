"""Fornece o sistema de arquivos falso usado nos testes unitários."""

from pathlib import PurePath, PureWindowsPath

import pytest

from symlink_generator.domain.errors import InvalidPathError


class FakeFileSystem:
    """Simula a porta de sistema de arquivos inteira em memória."""

    def __init__(self) -> None:
        """Começa com um disco vazio e sem falhas programadas."""
        self.files: set[PurePath] = set()
        """Arquivos reais que existem no disco simulado."""

        self.dirs: set[PurePath] = set()
        """Pastas que existem no disco simulado."""

        self.links: set[PurePath] = set()
        """Symlinks e junctions que existem no disco simulado."""

        self.errors: dict[str, OSError] = {}
        """Falha programada por nome de método, para simular erro do sistema."""

        self.calls: list[tuple[object, ...]] = []
        """Registra as escritas na ordem em que foram pedidas."""

    def _raise_programmed_error(self, method: str) -> None:
        """Levanta a falha programada para o método, quando existe."""
        error = self.errors.get(method)

        if error is not None:
            raise error

    # Devolve Windows puro de propósito: no Linux, PurePath("C:\\") tem name
    # preenchido e o teste de origem sem nome próprio não provaria nada.
    def resolve(self, path_text: str) -> PurePath:
        """Interpreta o texto como caminho absoluto do Windows."""
        self._raise_programmed_error("resolve")

        if "\x00" in path_text:
            raise InvalidPathError(path_text)

        return PureWindowsPath(path_text)

    def exists(self, path: PurePath) -> bool:
        """Informa se o caminho existe, contando links como existentes."""
        self._raise_programmed_error("exists")

        return path in self.files or path in self.dirs or path in self.links

    def lexists(self, path: PurePath) -> bool:
        """Informa se algo ocupa o caminho, mesmo que o link esteja quebrado."""
        self._raise_programmed_error("lexists")

        return path in self.files or path in self.dirs or path in self.links

    def is_dir(self, path: PurePath) -> bool:
        """Informa se o caminho é pasta."""
        self._raise_programmed_error("is_dir")

        return path in self.dirs

    def is_link(self, path: PurePath) -> bool:
        """Informa se o caminho é symlink ou junction."""
        self._raise_programmed_error("is_link")

        return path in self.links

    def remove_link(self, link_path: PurePath) -> None:
        """Remove o link, sem tocar no que ele aponta."""
        self._raise_programmed_error("remove_link")
        self.calls.append(("remove_link", link_path))
        self.links.discard(link_path)

    def create_symlink(
        self,
        link_path: PurePath,
        points_to: PurePath,
        *,
        is_directory: bool,
    ) -> None:
        """Cria o link e registra o pedido de escrita."""
        self._raise_programmed_error("create_symlink")
        self.calls.append(("create_symlink", link_path, points_to, is_directory))
        self.links.add(link_path)


@pytest.fixture
def fake_fs() -> FakeFileSystem:
    """Entrega um sistema de arquivos falso vazio."""
    return FakeFileSystem()
