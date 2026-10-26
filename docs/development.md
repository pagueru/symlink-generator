# Desenvolvimento

O projeto usa Python 3.13 e `uv` para dependências, execução e ferramentas. PyInstaller só instala no Windows, porque o executável é só para Windows.

## Preparar o ambiente

```bash
uv sync
```

Isso cria o `.venv` e instala o grupo `dev`. No homelab, todo comando `uv`, `python` e `pytest` roda com `env -u PYTHONPATH` na frente, porque o ambiente exporta um `PYTHONPATH` de outro Python e quebra o venv do projeto.

Para rodar o app a partir do código:

```bash
uv run symlink-generator
```

## Rodar os testes

```bash
uv run pytest
```

A suíte tem 75 testes no Windows. Dois marcadores separam o que depende de ambiente:

- `gui`: monta uma janela Tk real. Precisa de display.
- `windows`: cria junction de verdade e só roda no Windows.

Os testes sem marcador rodam em qualquer sistema. No Linux:

```bash
xvfb-run -a uv run pytest -m "not gui"
```

Para rodar os testes de janela no Linux são necessários `xvfb-run` e um Python com `_tkinter` compartilhado, vindo da distro ou do pyenv. O CPython que o `uv` baixa traz `_tkinter` embutido, e o `Pillow.ImageTk` do ttkbootstrap falha com `bad argument type for built-in operation` nesse caso. A saída é criar o venv com o Python do sistema:

```bash
uv venv --python /usr/bin/python3.13
uv sync
xvfb-run -a uv run pytest
```

## Formatação e lint

O `pyproject.toml` liga `fix` e `unsafe-fixes` no ruff, então o gate reescreve arquivo. Durante a edição, rode nos arquivos que você mexeu:

```bash
uv run ruff check <arquivos>
uv run ruff format <arquivos> && uv run ruff check <arquivos>
```

Para verificar sem editar, como faz o CI:

```bash
uv run ruff check --no-fix .
uv run ruff format --check .
```

Escolha que contraria um autofix precisa de `# noqa: <regra>` com o motivo em comentário. Não aumente a lista `ignore` do projeto para calar um caso isolado.

## Gerar o executável

```bash
uv run pyinstaller packaging/symlink-generator.spec --noconfirm
```

O resultado fica em `dist/symlink-generator.exe`, com cerca de 20 MB. O spec desliga o UPX de propósito: compactador de executável costuma disparar falso positivo de antivírus. Também não assinamos o arquivo, então o SmartScreen avisa na primeira execução.

Depois do build, confira que o executável abre e fecha:

```powershell
Start-Process dist\symlink-generator.exe -ArgumentList --smoke-test -Wait -PassThru
```

O `ExitCode` tem que ser 0. O `--smoke-test` monta a janela, processa um ciclo de eventos e fecha, sem entrar no laço principal. É a forma barata de pegar erro de import ou de asset faltando.

O arquivo `build/symlink-generator/warn-symlink-generator.txt` lista módulos opcionais que o PyInstaller não achou: numpy, olefile, defusedxml e screeninfo. Nenhum deles é usado pelo app. Se aparecer um módulo do próprio `symlink_generator` ou do `ttkbootstrap` nessa lista, o build está errado.

## Regenerar as screenshots

As imagens de `docs/images/` vêm da janela real, não de mockup:

```powershell
uv run python tools/capture_screenshots.py
```

O script roda só no Windows e precisa da sessão do usuário com a tela desbloqueada. Por SSH ele não serve, porque a sessão não garante janela visível. Ele monta um cenário descartável em `C:\tmp\symlink-demo`, captura a janela pelo retângulo do DWM, fotografa os diálogos nativos por título e apaga a pasta no fim. Se a tela estiver bloqueada, o script recusa a imagem lisa em vez de gravar um PNG preto.

## Integração contínua

O workflow em `.github/workflows/ci.yml` roda em `windows-latest` a cada push ou pull request para `main`. Os passos são `uv sync`, `uv run ruff check --no-fix .`, `uv run ruff format --check .` e `uv run pytest`. O job é único porque o app é só Windows: não há matriz de sistemas.

## Dívida conhecida

O tema `superhero` é o nome legado do ttkbootstrap 2.x. Ele vale até a versão 3.0, e a dependência está travada em `<3` por isso. Antes de liberar a 3.x, troque o tema em `main.THEME_NAME` e remova o filtro de aviso do `pyproject.toml`.
