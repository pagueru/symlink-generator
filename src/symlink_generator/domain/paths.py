"""Valida o texto do caminho e o nome do link antes de tocar no disco."""

from typing import Literal

from symlink_generator.domain.errors import EmptyPathError, InvalidLinkNameError

INVALID_NAME_CHARS: frozenset[str] = frozenset('<>:"|?*')
"""Caracteres que o Windows proíbe em qualquer nome de arquivo."""

PATH_SEPARATORS: frozenset[str] = frozenset({"/", "\\"})
"""Barras que tornam o nome do link um caminho, em vez de um nome."""

RESERVED_DEVICE_NAMES: frozenset[str] = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)},
)
"""Nomes de dispositivo do Windows, reservados com ou sem extensão."""


def clean_path_text(raw: str, *, field: Literal["source", "destination"]) -> str:
    """Remove espaços e aspas em volta do texto do caminho."""
    cleaned = raw.strip().strip("'\"").strip()

    if not cleaned:
        raise EmptyPathError(field)

    return cleaned


def validate_link_name(name: str) -> str:
    """Valida o nome do link e devolve a forma sem espaços nas pontas."""
    cleaned = name.strip()

    # Vazio é válido aqui: quem chama decide usar o nome da origem.
    if not cleaned:
        return ""

    has_bad_char = any(char in INVALID_NAME_CHARS or char in PATH_SEPARATORS for char in cleaned)
    ends_badly = cleaned.endswith((".", " "))

    if cleaned in {".", ".."} or has_bad_char or ends_badly:
        raise InvalidLinkNameError(cleaned)

    # O Windows reserva o nome do dispositivo mesmo quando há extensão (nul.txt).
    stem = cleaned.split(".", maxsplit=1)[0].lower()

    if stem in RESERVED_DEVICE_NAMES:
        raise InvalidLinkNameError(cleaned)

    return cleaned
