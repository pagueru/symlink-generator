"""Modela os dados que atravessam as camadas do app."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LinkRequest:
    """Descreve o symlink que a pessoa pediu para criar."""

    source: Path
    # Caminho absoluto do arquivo ou pasta que o link aponta.

    destination_dir: Path
    # Pasta onde o link será criado.

    link_name: str
    # Nome pedido para o link; vazio significa copiar o nome da origem.

    overwrite: bool = field(kw_only=True)
    # Indica se um link que já existe pode ser substituído.

    @property
    def target(self) -> Path:
        """Retorna o caminho final do link."""
        return self.destination_dir / (self.link_name or self.source.name)


@dataclass(frozen=True)
class LinkResult:
    """Descreve o symlink recém-criado."""

    source: Path
    # Caminho absoluto do arquivo ou pasta que o link aponta.

    target: Path
    # Caminho final do link criado.

    is_directory: bool
    # Indica se a origem é pasta, o que vira target_is_directory no Windows.
