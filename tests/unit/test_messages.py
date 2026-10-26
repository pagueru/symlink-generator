"""Testa os textos fixos e a tradução dos erros para a tela."""

from pathlib import PureWindowsPath

import pytest

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
from symlink_generator.presentation.messages import (
    ERROR_TITLE,
    FAILURE_STATUS,
    INITIAL_STATUS,
    SUCCESS_TITLE,
    describe_error,
    success_message,
)

SOURCE = PureWindowsPath("C:\\origem\\relatorio.xlsx")
DESTINATION = PureWindowsPath("C:\\destino")
TARGET = PureWindowsPath("C:\\destino\\relatorio.xlsx")
RAW_PATH = "C:\\origem\\rela\x00torio.xlsx"
DETAIL = "O sistema negou acesso."

ERROR_CASES: list[tuple[SymlinkGeneratorError, str]] = [
    (EmptyPathError(field="source"), "origem"),
    (EmptyPathError(field="destination"), "destino"),
    (InvalidPathError(RAW_PATH), RAW_PATH),
    (SourceNotFoundError(SOURCE), str(SOURCE)),
    (DestinationNotFoundError(DESTINATION), str(DESTINATION)),
    (DestinationNotADirectoryError(DESTINATION), str(DESTINATION)),
    (InvalidLinkNameError("a/b"), "a/b"),
    (LinkNameRequiredError(SOURCE), str(SOURCE)),
    (TargetExistsError(TARGET), str(TARGET)),
    (TargetNotALinkError(TARGET), str(TARGET)),
    (PrivilegeRequiredError(SOURCE, TARGET, DETAIL), "Modo de Desenvolvedor"),
    (LinkCreationError(SOURCE, TARGET, DETAIL), DETAIL),
]


ERROR_IDS: list[str] = [type(error).__name__ for error, _expected in ERROR_CASES]


@pytest.mark.parametrize(("error", "expected"), ERROR_CASES, ids=ERROR_IDS)
def test_describe_error_is_not_empty_and_names_the_field(
    error: SymlinkGeneratorError,
    expected: str,
) -> None:
    message = describe_error(error)

    assert message.strip()
    assert expected in message


def test_empty_source_message() -> None:
    assert describe_error(EmptyPathError(field="source")) == "Informe a origem."


def test_empty_destination_message() -> None:
    assert describe_error(EmptyPathError(field="destination")) == "Informe o diretório de destino."


def test_privilege_message_explains_developer_mode() -> None:
    message = describe_error(PrivilegeRequiredError(SOURCE, TARGET, DETAIL))

    assert message == (
        "O Windows recusou a criação do symlink por falta de permissão.\n\n"
        "Ative o Modo de Desenvolvedor (Configurações > Sistema > Para desenvolvedores)"
        " ou abra o app como administrador."
    )


def test_success_message_shows_target() -> None:
    result = LinkResult(source=SOURCE, target=TARGET, is_directory=False)

    assert success_message(result) == f"Symlink criado com sucesso:\n{TARGET}"


def test_fixed_texts_match_the_interface() -> None:
    assert INITIAL_STATUS == "Preencha os campos e clique em criar."
    assert FAILURE_STATUS == "Falha ao criar symlink."
    assert ERROR_TITLE == "Erro"
    assert SUCCESS_TITLE == "Sucesso"
