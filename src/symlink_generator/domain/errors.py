"""Define os erros esperados do gerador de symlinks."""

from pathlib import Path
from typing import Literal


class SymlinkGeneratorError(Exception):
    """Representa a base de todo erro esperado, que a interface sabe explicar."""


class EmptyPathError(SymlinkGeneratorError):
    """Indica que um dos campos de caminho chegou vazio."""

    def __init__(self, field: Literal["source", "destination"]) -> None:
        """Guarda qual campo ficou vazio."""
        self.field: Literal["source", "destination"] = field
        """Nome do campo vazio, usado para escolher a mensagem."""
        super().__init__(f"O campo {field} está vazio.")


class InvalidPathError(SymlinkGeneratorError):
    """Indica que o sistema não conseguiu interpretar o texto do caminho."""

    def __init__(self, raw: str) -> None:
        """Guarda o texto que falhou na resolução."""
        self.raw: str = raw
        """Texto cru digitado na tela."""
        super().__init__(f"Caminho inválido: {raw}")


class SourceNotFoundError(SymlinkGeneratorError):
    """Indica que a origem informada não existe."""

    def __init__(self, path: Path) -> None:
        """Guarda o caminho da origem ausente."""
        self.path: Path = path
        """Caminho absoluto da origem."""
        super().__init__(f"A origem não existe: {path}")


class DestinationNotFoundError(SymlinkGeneratorError):
    """Indica que o diretório de destino não existe."""

    def __init__(self, path: Path) -> None:
        """Guarda o caminho do destino ausente."""
        self.path: Path = path
        """Caminho absoluto do diretório de destino."""
        super().__init__(f"O diretório de destino não existe: {path}")


class DestinationNotADirectoryError(SymlinkGeneratorError):
    """Indica que o destino informado é arquivo, não pasta."""

    def __init__(self, path: Path) -> None:
        """Guarda o caminho do destino que não é pasta."""
        self.path: Path = path
        """Caminho absoluto do destino."""
        super().__init__(f"O destino precisa ser um diretório: {path}")


class InvalidLinkNameError(SymlinkGeneratorError):
    """Indica que o nome do link tem texto que o Windows recusa."""

    def __init__(self, name: str) -> None:
        """Guarda o nome recusado."""
        self.name: str = name
        """Nome do link depois do strip."""
        super().__init__(f"Nome de link inválido: {name}")


class LinkNameRequiredError(SymlinkGeneratorError):
    """Indica que a origem não tem nome próprio e o nome do link ficou vazio."""

    def __init__(self, source: Path) -> None:
        """Guarda a origem sem nome."""
        self.source: Path = source
        """Caminho absoluto da origem."""
        super().__init__(f"A origem não tem nome próprio: {source}")


class TargetExistsError(SymlinkGeneratorError):
    """Indica que o caminho final já existe e não foi autorizado sobrescrever."""

    def __init__(self, path: Path) -> None:
        """Guarda o caminho final ocupado."""
        self.path: Path = path
        """Caminho final do link."""
        super().__init__(f"O caminho final já existe: {path}")


class TargetNotALinkError(SymlinkGeneratorError):
    """Indica que o caminho final é item real, que o app não substitui."""

    def __init__(self, path: Path) -> None:
        """Guarda o caminho final que não é link."""
        self.path: Path = path
        """Caminho final ocupado por arquivo ou pasta real."""
        super().__init__(f"O caminho final já existe e não é um link: {path}")


class LinkCreationError(SymlinkGeneratorError):
    """Indica falha do sistema ao remover o link antigo ou ao criar o novo."""

    def __init__(self, source: Path, target: Path, detail: str) -> None:
        """Guarda os caminhos envolvidos e o detalhe técnico."""
        self.source: Path = source
        """Caminho absoluto da origem."""
        self.target: Path = target
        """Caminho final do link."""
        self.detail: str = detail
        """Mensagem técnica da exceção original."""
        super().__init__(f"Falha ao criar o symlink de {source} para {target}: {detail}")


class PrivilegeRequiredError(LinkCreationError):
    """Indica que o Windows recusou a criação por falta de permissão."""
