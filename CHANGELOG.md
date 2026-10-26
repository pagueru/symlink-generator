# Changelog

Todas as mudanças importantes deste projeto ficam neste arquivo.

O formato segue o Keep a Changelog, e o projeto usa Versionamento Semântico.

## [1.0.0] - 2026-10-26

Primeira versão como repositório próprio, com o app reorganizado em camadas.

### Adicionado

- Aplicativo em quatro camadas: domínio puro, caso de uso com porta de sistema de arquivos, adaptador `pathlib` e apresentação Tk testável sem janela.
- Testes unitários com sistema de arquivos em memória, testes de integração em pasta temporária real e testes de janela marcados com `gui`.
- Integração contínua no GitHub Actions, rodando lint, checagem de formato e testes no Windows.
- Build do executável pelo PyInstaller, com spec versionado e modo `--smoke-test` para conferir o `.exe`.
- Documentação de uso, de arquitetura e de desenvolvimento, com screenshots da janela e dos diálogos.
- Licença MIT.

### Alterado

- Sobrescrever só substitui link. O script antigo apagava um arquivo real quando a opção estava marcada; agora arquivo ou pasta de verdade no caminho final vira erro e o app pede remoção manual.
- O nome do link passou a ser validado. O app recusa barra, `.` e `..`, os caracteres `< > : " | ? *`, ponto ou espaço no final e os nomes reservados do Windows. Antes, um nome como `..\x` criava o link fora do destino. Origem na raiz de unidade, como `C:\`, agora exige nome do link.
- Falta de permissão do Windows virou mensagem clara: em vez do código 1314, a tela explica como ligar o Modo de Desenvolvedor ou abrir como administrador.
- `ttkbootstrap` passou a ser dependência obrigatória e o fallback para `tkinter.ttk` saiu. Os diálogos continuam os nativos do `tkinter.messagebox`.
- O executável passou a se chamar `symlink-generator.exe` e a morar em `%LOCALAPPDATA%\Programs\symlink-generator\`.
- Erro esperado virou mensagem específica na tela, e erro inesperado passou a ser registrado no log com traceback e mostrado num diálogo genérico. Nenhuma exceção escapa do callback do Tk, o que importa no executável sem console.
