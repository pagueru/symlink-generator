"""Gera as screenshots da documentação a partir da janela real do app (só Windows)."""

import ctypes
import logging
import shutil
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

from PIL import ImageGrab, ImageStat

from symlink_generator.application.create_symlink import CreateSymlinkCommand
from symlink_generator.main import App, build_app

logging.basicConfig(
    format="%(asctime)s - %(module)s:%(lineno)03d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

REPO_ROOT: Path = Path(__file__).resolve().parents[1]
"""Raiz do repositório, usada para achar a pasta de imagens."""

IMAGES_DIR: Path = REPO_ROOT / "docs" / "images"
"""Pasta onde as screenshots da documentação ficam versionadas."""

DEMO_DIR: Path = Path(r"C:\tmp\symlink-demo")
"""Pasta descartável com caminhos neutros, para não expor dado pessoal na imagem."""

DIALOG_CLASS: str = "#32770"
"""Classe de janela dos diálogos nativos do Windows (MessageBox)."""

DWMWA_EXTENDED_FRAME_BOUNDS: int = 9
"""Atributo do DWM com a moldura visível, sem as bordas invisíveis de redimensionamento."""

WM_CLOSE: int = 0x0010
"""Mensagem que fecha o diálogo depois da captura."""

DIALOG_TIMEOUT_SECONDS: float = 10.0
"""Tempo máximo esperando o diálogo aparecer."""

SETTLE_SECONDS: float = 0.3
"""Pausa para o Windows terminar de desenhar a janela antes da captura."""

MIN_PIXEL_STDDEV: float = 5.0
"""Desvio padrão mínimo de pixel; abaixo disso a imagem saiu lisa (tela bloqueada)."""


def window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    """Devolve o retângulo visível da janela segundo o DWM."""
    rect = wintypes.RECT()
    result = ctypes.windll.dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )

    if result != 0:
        msg = f"DwmGetWindowAttribute falhou com HRESULT {result:#x}"
        raise OSError(msg)

    return rect.left, rect.top, rect.right, rect.bottom


def capture_window(hwnd: int, output: Path) -> None:
    """Fotografa a janela e recusa imagem lisa, sinal de tela bloqueada."""
    image = ImageGrab.grab(bbox=window_bounds(hwnd), all_screens=True)
    stddev = max(ImageStat.Stat(image.convert("RGB")).stddev)

    if stddev < MIN_PIXEL_STDDEV:
        msg = f"Captura lisa em {output.name} (desvio {stddev:.1f}): a tela está bloqueada?"
        raise RuntimeError(msg)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    logger.info("Capturado %s (%sx%s, desvio %.1f)", output.name, *image.size, stddev)


def find_dialog(title: str) -> int:
    """Espera o diálogo nativo com o título informado e devolve o hwnd."""
    deadline = time.monotonic() + DIALOG_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        hwnd = ctypes.windll.user32.FindWindowW(DIALOG_CLASS, title)

        if hwnd:
            return hwnd

        time.sleep(0.1)

    msg = f"Diálogo '{title}' não apareceu em {DIALOG_TIMEOUT_SECONDS:.0f} s"
    raise TimeoutError(msg)


def capture_dialog_in_background(title: str, output: Path, errors: list[BaseException]) -> None:
    """Captura o diálogo que o botão vai abrir e o fecha, numa thread à parte."""

    def worker() -> None:
        """Acha, fotografa e fecha o diálogo, guardando o erro para a thread principal."""
        hwnd = 0
        try:
            hwnd = find_dialog(title)
            time.sleep(SETTLE_SECONDS)
            capture_window(hwnd, output)
        except (OSError, RuntimeError, TimeoutError) as exc:
            errors.append(exc)
        finally:
            # Fecha mesmo se a captura falhar, senão o diálogo modal prende o script.
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

    threading.Thread(target=worker, daemon=True).start()


def prepare_demo() -> CreateSymlinkCommand:
    """Cria a pasta de demonstração e devolve o pedido usado nas imagens."""
    shutil.rmtree(DEMO_DIR, ignore_errors=True)
    project_dir = DEMO_DIR / "origem" / "Projetos"
    project_dir.mkdir(parents=True)
    (project_dir / "relatorio-2026.xlsx").write_bytes(b"demo")
    (DEMO_DIR / "atalhos").mkdir()

    return CreateSymlinkCommand(
        source=str(project_dir),
        destination=str(DEMO_DIR / "atalhos"),
        link_name="Projetos",
        overwrite=False,
    )


def cleanup_demo() -> None:
    """Remove o link antes da pasta, para nunca seguir o link ao apagar."""
    link = DEMO_DIR / "atalhos" / "Projetos"

    if link.is_symlink():
        link.unlink()

    shutil.rmtree(DEMO_DIR, ignore_errors=True)


def submit_and_capture(app: App, title: str, output: Path) -> None:
    """Clica em Criar symlink e captura o diálogo que aparecer."""
    errors: list[BaseException] = []
    capture_dialog_in_background(title, output, errors)
    app.view.submit_button.invoke()
    app.root.update()

    if errors:
        raise errors[0]


def run() -> int:
    """Gera as três imagens da documentação e devolve o código de saída."""
    if sys.platform != "win32":
        logger.error("Este script só roda no Windows")
        return 1

    command = prepare_demo()
    app = build_app()

    try:
        # Mantém a janela acima das outras: a captura lê os pixels da tela.
        app.root.attributes("-topmost", True)  # noqa: FBT003
        app.view.fill(command)
        app.root.update()
        time.sleep(SETTLE_SECONDS)

        main_hwnd = int(app.root.wm_frame(), 16)
        capture_window(main_hwnd, IMAGES_DIR / "janela-principal.png")

        submit_and_capture(app, "Sucesso", IMAGES_DIR / "sucesso.png")

        # Mesmo pedido de novo, sem Sobrescrever: o link já existe e o app recusa.
        app.view.fill(command)
        app.root.update()
        submit_and_capture(app, "Erro", IMAGES_DIR / "erro-ja-existe.png")
    finally:
        app.root.destroy()
        cleanup_demo()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
