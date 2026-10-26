"""Executa a criação do symlink a partir do pedido cru da tela."""

import logging
from dataclasses import dataclass
from pathlib import Path

from symlink_generator.application.ports import FileSystemPort
from symlink_generator.domain.errors import (
    DestinationNotADirectoryError,
    DestinationNotFoundError,
    LinkCreationError,
    LinkNameRequiredError,
    PrivilegeRequiredError,
    SourceNotFoundError,
    TargetExistsError,
    TargetNotALinkError,
)
from symlink_generator.domain.models import LinkRequest, LinkResult
from symlink_generator.domain.paths import clean_path_text, validate_link_name

logger = logging.getLogger(__name__)

WINDOWS_ACCESS_DENIED_ERROR: int = 1314
"""Código de erro do Windows para falta de privilégio na criação do symlink."""


@dataclass(frozen=True)
class CreateSymlinkCommand:
    """Carrega o texto cru digitado na tela."""

    source: str
    # Texto do campo Origem, antes de qualquer limpeza.

    destination: str
    # Texto do campo Destino, antes de qualquer limpeza.

    link_name: str
    # Texto do campo Nome do link; vazio usa o nome da origem.

    overwrite: bool
    # Indica se o checkbox Sobrescrever estava marcado.


class CreateSymlinkUseCase:
    """Cria o symlink depois de validar origem, destino e nome."""

    def __init__(self, filesystem: FileSystemPort) -> None:
        """Recebe a porta usada para falar com o sistema de arquivos."""
        self.filesystem: FileSystemPort = filesystem
        """Porta de disco injetada pela composition root."""

    def execute(self, command: CreateSymlinkCommand) -> LinkResult:
        """Cria o symlink pedido e devolve o resultado."""
        source = self.filesystem.resolve(clean_path_text(command.source, field="source"))
        destination_dir = self.filesystem.resolve(
            clean_path_text(command.destination, field="destination"),
        )
        self._ensure_source_exists(source)
        self._ensure_destination_is_directory(destination_dir)
        link_name = validate_link_name(command.link_name)

        # Origem sem nome próprio (raiz de drive) só pode virar link com nome digitado.
        if not link_name and not source.name:
            raise LinkNameRequiredError(source)

        request = LinkRequest(
            source=source,
            destination_dir=destination_dir,
            link_name=link_name,
            overwrite=command.overwrite,
        )
        target = request.target
        self._ensure_target_is_replaceable(target, overwrite=command.overwrite)
        is_directory = self.filesystem.is_dir(source)

        try:
            if self.filesystem.lexists(target):
                self.filesystem.remove_link(target)

            self.filesystem.create_symlink(target, source, is_directory=is_directory)
        except OSError as exc:
            raise self._creation_error(exc, source, target) from exc

        logger.info("Symlink criado: %s -> %s", target, source)

        return LinkResult(source=source, target=target, is_directory=is_directory)

    def _ensure_source_exists(self, source: Path) -> None:
        """Recusa origem que não existe no disco."""
        if not self.filesystem.exists(source):
            raise SourceNotFoundError(source)

    def _ensure_destination_is_directory(self, destination_dir: Path) -> None:
        """Recusa destino ausente ou que é arquivo."""
        if not self.filesystem.exists(destination_dir):
            raise DestinationNotFoundError(destination_dir)

        if not self.filesystem.is_dir(destination_dir):
            raise DestinationNotADirectoryError(destination_dir)

    def _ensure_target_is_replaceable(self, target: Path, *, overwrite: bool) -> None:
        """Recusa caminho final ocupado, salvo link com sobrescrita autorizada."""
        if not self.filesystem.lexists(target):
            return

        if not overwrite:
            raise TargetExistsError(target)

        # Só link pode ser substituído: apagar item real seria perda de dado silenciosa.
        if not self.filesystem.is_link(target):
            raise TargetNotALinkError(target)

    @staticmethod
    def _creation_error(exc: OSError, source: Path, target: Path) -> LinkCreationError:
        """Converte o erro do sistema no erro esperado correspondente."""
        if getattr(exc, "winerror", None) == WINDOWS_ACCESS_DENIED_ERROR:
            return PrivilegeRequiredError(source, target, str(exc))

        return LinkCreationError(source, target, str(exc))
