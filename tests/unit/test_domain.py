from pathlib import Path

import pytest

from symlink_generator.domain.errors import EmptyPathError, InvalidLinkNameError
from symlink_generator.domain.models import LinkRequest
from symlink_generator.domain.paths import clean_path_text, validate_link_name


def test_clean_path_text_strips_quotes_and_spaces():
    assert clean_path_text('  "C:\\a b"  ', field="source") == "C:\\a b"


def test_clean_path_text_empty_raises_with_field():
    with pytest.raises(EmptyPathError) as error_info:
        clean_path_text('  ""  ', field="destination")

    assert error_info.value.field == "destination"


def test_validate_link_name_strips():
    assert validate_link_name("  meu-link ") == "meu-link"


def test_validate_link_name_empty_returns_empty():
    assert validate_link_name("   ") == ""


@pytest.mark.parametrize(
    "name",
    [
        "a/b",
        "a\\b",
        ".",
        "..",
        "x:y",
        "a*b",
        'a"b',
        "a<b",
        "a>b",
        "a|b",
        "a?b",
        "nome.",
        "CON",
        "nul.txt",
        "com1",
        "LPT9.log",
    ],
)
def test_validate_link_name_rejects(name):
    with pytest.raises(InvalidLinkNameError):
        validate_link_name(name)


@pytest.mark.parametrize("name", ["CONSOLE", "com10", "a.b"])
def test_validate_link_name_accepts_lookalikes(name):
    assert validate_link_name(name) == name


def test_link_request_target_defaults_to_source_name():
    request = LinkRequest(
        source=Path("C:/origem/relatorio-2026.xlsx"),
        destination_dir=Path("C:/destino"),
        link_name="",
        overwrite=False,
    )

    assert request.target == Path("C:/destino/relatorio-2026.xlsx")


def test_link_request_target_uses_link_name():
    request = LinkRequest(
        source=Path("C:/origem/relatorio-2026.xlsx"),
        destination_dir=Path("C:/destino"),
        link_name="atalho",
        overwrite=False,
    )

    assert request.target == Path("C:/destino/atalho")
