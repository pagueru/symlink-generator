"""Declara o tema escuro do app pela API de temas do ttkbootstrap 2.x."""

import ttkbootstrap as ttk

THEME_FAMILY: str = "superhero"
"""Família do tema; o ttkbootstrap gera a variante escura a partir dela."""

THEME_NAME: str = f"{THEME_FAMILY}-dark"
"""Nome da variante usada pela janela."""

# Mesma paleta do antigo tema superhero (nome pré-2.0, removido no ttkbootstrap 3.0),
# declarada pela API pública Theme para manter o visual sem depender do nome legado.
SUPERHERO_THEME: ttk.Theme = ttk.Theme(
    name=THEME_FAMILY,
    primary="#4c9be8",
    secondary="#4e5d6c",
    success="#5cb85c",
    info="#5bc0de",
    warning="#f0ad4e",
    danger="#d9534f",
    dark={"background": "#2b3e50", "foreground": "#ffffff"},
)
"""Tema escuro azul-ardósia que o app usa desde a primeira versão."""


def register_theme() -> str:
    """Registra o tema no ttkbootstrap e devolve o nome para a janela usar."""
    SUPERHERO_THEME.register()
    return THEME_NAME
