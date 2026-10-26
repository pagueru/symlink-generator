"""Desenha o formulário em Tk e responde pelos diálogos nativos."""

import tkinter as tk
from collections.abc import Callable
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from symlink_generator.application.create_symlink import CreateSymlinkCommand
from symlink_generator.presentation.messages import INITIAL_STATUS

STATUS_WRAP_LENGTH: int = 700
"""Largura em pixels a partir da qual o texto de status quebra a linha."""


class TkSymlinkView:
    """Monta o layout do formulário e cumpre a porta de tela do presenter."""

    def __init__(self, root: tk.Misc) -> None:
        """Cria os campos e os widgets dentro da janela recebida."""
        self.root: tk.Misc = root
        """Janela que hospeda o formulário."""

        self.source_var: tk.StringVar = tk.StringVar(master=root)
        """Texto do campo Origem."""

        self.destination_var: tk.StringVar = tk.StringVar(master=root)
        """Texto do campo Destino."""

        self.link_name_var: tk.StringVar = tk.StringVar(master=root)
        """Texto do campo Nome do link."""

        self.overwrite_var: tk.BooleanVar = tk.BooleanVar(master=root, value=False)
        """Estado do checkbox Sobrescrever se já existir."""

        self.status_var: tk.StringVar = tk.StringVar(master=root, value=INITIAL_STATUS)
        """Mensagem fixa mostrada no rodapé."""

        self._submit_callback: Callable[[], None] | None = None
        """Ação a executar quando o botão Criar symlink é acionado."""

        self.submit_button: ttk.Button = self._build_layout()
        """Botão que dispara a criação do symlink."""

    def _build_layout(self) -> ttk.Button:
        """Monta a grade de widgets e devolve o botão de envio."""
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        self._add_source_row(frame)
        self._add_destination_row(frame)
        self._add_link_name_row(frame)

        ttk.Checkbutton(
            frame,
            text="Sobrescrever se já existir",
            variable=self.overwrite_var,
        ).grid(row=3, column=1, sticky="w", pady=(0, 10))

        submit_button = ttk.Button(frame, text="Criar symlink", command=self._notify_submit)
        submit_button.grid(row=4, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(
            frame,
            textvariable=self.status_var,
            wraplength=STATUS_WRAP_LENGTH,
            justify="left",
        ).grid(row=5, column=0, columnspan=4, sticky="w")

        return submit_button

    def _add_source_row(self, frame: ttk.Frame) -> None:
        """Desenha a linha da origem, com os botões de arquivo e pasta."""
        ttk.Label(frame, text="Origem").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(0, 8),
        )
        ttk.Entry(frame, textvariable=self.source_var).grid(
            row=0,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )
        ttk.Button(
            frame,
            text="Arquivo",
            command=lambda: self._browse(self.source_var, is_directory=False),
        ).grid(row=0, column=2, padx=(8, 4), pady=(0, 8))
        ttk.Button(
            frame,
            text="Pasta",
            command=lambda: self._browse(self.source_var, is_directory=True),
        ).grid(row=0, column=3, pady=(0, 8))

    def _add_destination_row(self, frame: ttk.Frame) -> None:
        """Desenha a linha do destino, só com seleção de pasta."""
        ttk.Label(frame, text="Destino").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(0, 8),
        )
        ttk.Entry(frame, textvariable=self.destination_var).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )
        ttk.Button(
            frame,
            text="Selecionar",
            command=lambda: self._browse(self.destination_var, is_directory=True),
        ).grid(row=1, column=2, columnspan=2, padx=(8, 0), pady=(0, 8), sticky="ew")

    def _add_link_name_row(self, frame: ttk.Frame) -> None:
        """Desenha a linha opcional do nome do link."""
        ttk.Label(frame, text="Nome do link").grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(0, 8),
        )
        ttk.Entry(frame, textvariable=self.link_name_var).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=(0, 8),
        )

    def _browse(self, target: tk.StringVar, *, is_directory: bool) -> None:
        """Abre o seletor nativo e grava o caminho escolhido no campo."""
        selected_path: str = (
            filedialog.askdirectory() if is_directory else filedialog.askopenfilename()
        )

        if not selected_path:
            return

        target.set(selected_path)

    def _notify_submit(self) -> None:
        """Executa a ação ligada ao botão, quando existe."""
        if self._submit_callback is None:
            return

        self._submit_callback()

    def bind_submit(self, callback: Callable[[], None]) -> None:
        """Liga o botão Criar symlink à ação informada."""
        self._submit_callback = callback

    def read_command(self) -> CreateSymlinkCommand:
        """Monta o pedido com o texto cru que está nos campos."""
        return CreateSymlinkCommand(
            source=self.source_var.get(),
            destination=self.destination_var.get(),
            link_name=self.link_name_var.get(),
            overwrite=self.overwrite_var.get(),
        )

    def fill(self, command: CreateSymlinkCommand) -> None:
        """Escreve um pedido nos campos, para testes e captura de tela."""
        self.source_var.set(command.source)
        self.destination_var.set(command.destination)
        self.link_name_var.set(command.link_name)
        self.overwrite_var.set(command.overwrite)

    def show_error(self, title: str, message: str) -> None:
        """Mostra o erro no diálogo nativo do sistema."""
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str) -> None:
        """Mostra o aviso no diálogo nativo do sistema."""
        messagebox.showinfo(title, message)

    def set_status(self, text: str) -> None:
        """Troca a mensagem do rodapé."""
        self.status_var.set(text)

    def reset_form(self) -> None:
        """Limpa os campos, desmarca a sobrescrita e volta o status inicial."""
        self.source_var.set("")
        self.destination_var.set("")
        self.link_name_var.set("")
        self.overwrite_var.set(value=False)
        self.status_var.set(INITIAL_STATUS)
