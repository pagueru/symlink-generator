"""Liga o formulário ao caso de uso, sem depender do Tk."""

import logging
from typing import Protocol

from symlink_generator.application.create_symlink import (
    CreateSymlinkCommand,
    CreateSymlinkUseCase,
)
from symlink_generator.domain.errors import LinkCreationError, SymlinkGeneratorError
from symlink_generator.domain.models import LinkResult
from symlink_generator.presentation.messages import (
    ERROR_TITLE,
    FAILURE_STATUS,
    SUCCESS_TITLE,
    describe_error,
    success_message,
)

logger = logging.getLogger(__name__)


class SymlinkView(Protocol):
    """Descreve o que o presenter precisa que a tela ofereça."""

    def show_error(self, title: str, message: str) -> None:
        """Mostra um diálogo de erro."""
        ...

    def show_info(self, title: str, message: str) -> None:
        """Mostra um diálogo informativo."""
        ...

    def set_status(self, text: str) -> None:
        """Troca o texto de status do rodapé."""
        ...

    def reset_form(self) -> None:
        """Limpa os campos, desmarca a sobrescrita e volta o status inicial."""
        ...


class SymlinkFormPresenter:
    """Transforma o envio do formulário em criação de symlink e resposta na tela."""

    def __init__(self, view: SymlinkView, use_case: CreateSymlinkUseCase) -> None:
        """Recebe a tela e o caso de uso que ela dispara."""
        self.view: SymlinkView = view
        """Tela que exibe status, diálogos e limpeza do formulário."""

        self.use_case: CreateSymlinkUseCase = use_case
        """Caso de uso que cria o symlink."""

    def submit(self, command: CreateSymlinkCommand) -> LinkResult | None:
        """Cria o symlink pedido e devolve o resultado, ou None quando falha."""
        try:
            result = self.use_case.execute(command)
        except LinkCreationError as exc:
            # Falha do sistema: o traceback vai para o log, como no original.
            logger.exception(
                "Falha ao criar symlink: origem=%s destino=%s",
                command.source,
                command.destination,
            )
            self.view.set_status(FAILURE_STATUS)
            self.view.show_error(ERROR_TITLE, describe_error(exc))
            return None
        except SymlinkGeneratorError as exc:
            # Erro de validação: só explica, sem marcar falha nem limpar a tela.
            self.view.show_error(ERROR_TITLE, describe_error(exc))
            return None

        self.view.show_info(SUCCESS_TITLE, success_message(result))
        self.view.reset_form()

        return result
