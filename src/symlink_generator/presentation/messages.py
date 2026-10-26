"""Centraliza os textos fixos da janela e a explicação de cada erro."""

from collections.abc import Callable

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
    SymlinkGeneratorError,
    TargetExistsError,
    TargetNotALinkError,
)
from symlink_generator.domain.models import LinkResult

INITIAL_STATUS: str = "Preencha os campos e clique em criar."
FAILURE_STATUS: str = "Falha ao criar symlink."
ERROR_TITLE: str = "Erro"
SUCCESS_TITLE: str = "Sucesso"

_PRIVILEGE_MESSAGE: str = (
    "O Windows recusou a criação do symlink por falta de permissão.\n\n"
    "Ative o Modo de Desenvolvedor (Configurações > Sistema > Para desenvolvedores)"
    " ou abra o app como administrador."
)
"""Explica como obter permissão, já que sem ela o link nunca é criado."""

_INVALID_LINK_NAME_HINT: str = (
    '\n\nUse só o nome, sem barras, sem os caracteres < > : " | ? *, '
    "sem ponto ou espaço no final e sem nomes reservados do Windows "
    "(CON, NUL, COM1...)."
)
"""Diz o que corrigir no nome, para a pessoa não tentar adivinhar a regra."""


def describe_error(error: SymlinkGeneratorError) -> str:
    """Traduz o erro esperado na mensagem que explica o problema."""
    # Percorre a herança para pegar a mensagem mais específica que existir.
    for error_type in type(error).__mro__:
        describe = _DESCRIBERS.get(error_type)

        if describe is not None:
            return describe(error)

    return str(error)


def success_message(result: LinkResult) -> str:
    """Monta o texto do diálogo de sucesso com o caminho final."""
    return f"Symlink criado com sucesso:\n{result.target}"


def _describe_empty_path(error: EmptyPathError) -> str:
    """Aponta qual dos dois campos de caminho ficou vazio."""
    if error.field == "source":
        return "Informe a origem."

    return "Informe o diretório de destino."


def _describe_invalid_path(error: InvalidPathError) -> str:
    """Mostra o texto que o sistema não conseguiu interpretar."""
    return f"Falha ao interpretar o caminho:\n{error.raw}"


def _describe_source_not_found(error: SourceNotFoundError) -> str:
    """Informa que a origem apontada não existe."""
    return f"A origem não existe:\n{error.path}"


def _describe_destination_not_found(error: DestinationNotFoundError) -> str:
    """Informa que o diretório de destino não existe."""
    return f"O diretório de destino não existe:\n{error.path}"


def _describe_destination_not_a_directory(error: DestinationNotADirectoryError) -> str:
    """Informa que o destino informado é arquivo, não pasta."""
    return f"O destino precisa ser um diretório:\n{error.path}"


def _describe_invalid_link_name(error: InvalidLinkNameError) -> str:
    """Explica por que o nome do link foi recusado."""
    return f"Nome de link inválido: {error.name}{_INVALID_LINK_NAME_HINT}"


def _describe_link_name_required(error: LinkNameRequiredError) -> str:
    """Pede o nome do link quando a origem não tem nome próprio."""
    return f"A origem não tem nome próprio:\n{error.source}\n\nInforme o nome do link."


def _describe_target_exists(error: TargetExistsError) -> str:
    """Avisa que o caminho final está ocupado e como liberar."""
    return f"O caminho final já existe:\n{error.path}\n\nMarque 'Sobrescrever' para recriar."


def _describe_target_not_a_link(error: TargetNotALinkError) -> str:
    """Avisa que item real não é substituído pelo app."""
    return (
        f"O caminho final já existe e não é um link:\n{error.path}"
        "\n\nRemova ou renomeie esse item manualmente. O app só substitui links."
    )


def _describe_privilege_required(_error: PrivilegeRequiredError) -> str:
    """Explica o Modo de Desenvolvedor no lugar do detalhe técnico."""
    return _PRIVILEGE_MESSAGE


def _describe_link_creation(error: LinkCreationError) -> str:
    """Monta a mensagem genérica de falha com os caminhos e o detalhe."""
    return (
        "Não foi possível criar o symlink.\n"
        f"\nOrigem: {error.source}\nDestino: {error.target}"
        f"\n\nDetalhe técnico: {error.detail}"
    )


# Chave por classe e chamada elástica: cada descritor tipa o erro concreto que recebe.
_DESCRIBERS: dict[type[object], Callable[..., str]] = {
    EmptyPathError: _describe_empty_path,
    InvalidPathError: _describe_invalid_path,
    SourceNotFoundError: _describe_source_not_found,
    DestinationNotFoundError: _describe_destination_not_found,
    DestinationNotADirectoryError: _describe_destination_not_a_directory,
    InvalidLinkNameError: _describe_invalid_link_name,
    LinkNameRequiredError: _describe_link_name_required,
    TargetExistsError: _describe_target_exists,
    TargetNotALinkError: _describe_target_not_a_link,
    PrivilegeRequiredError: _describe_privilege_required,
    LinkCreationError: _describe_link_creation,
}
"""Mapeia cada erro esperado para o texto que a tela mostra."""
