# Cortador de Vídeos em Massa

Corta a mesma área de vários vídeos de uma vez. Veja o planejamento completo em
`Cortador de Vídeos em Massa.md`.

## Instalação

1. Python 3.11+ (no Windows, marque "Add to PATH").
2. FFmpeg: `winget install ffmpeg`. Para conferir a aceleração NVIDIA: `ffmpeg -hide_banner -encoders | findstr nvenc` (deve listar `h264_nvenc`).
3. Dependências:

```
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Uso (Windows)

Abra o terminal (PowerShell ou CMD) na pasta do projeto e ative o ambiente:

```
cd C:\caminho\do\video-cutter
.venv\Scripts\activate
```

**Sempre coloque o caminho entre aspas** se ele tiver espaços (ex.: `Op Black`).

### 1. Separar os vídeos por resolução (`res.py`)

Move cada vídeo da pasta para uma subpasta com a sua resolução (`1920x1080`, `1345x1080`...).
Faça isso antes de cortar, pois o corte exige que todos os vídeos tenham a mesma resolução.

```
python res.py "C:\Users\Razac\OneDrive\Documentos\Op Black\MankoPrincess\videosvip"
```

Resultado:

```
videosvip\
  1920x1080\  video1.mp4, video2.mp4
  1345x1080\  video3.mp4
```

Vídeos que não puderem ser lidos vão para `ilegiveis`.

### 2. Cortar a mesma área de todos os vídeos (`cli.py`)

Rode em uma pasta de resolução (a que `res.py` criou). Uma janela abre com o primeiro vídeo:
selecione a área com o mouse e aperte **Enter** (**Esc** cancela). Os cortes vão para `cortados`.

```
python cli.py "C:\...\videosvip\1920x1080"
```

Para escolher a pasta de saída:

```
python cli.py "C:\...\videosvip\1920x1080" "C:\...\saida"
```

### Atualizar o projeto

```
git pull
```

## Estrutura

- `selecao.py`: `selecionar_area()` com OpenCV
- `corte.py`: `cortar()` com FFmpeg
- `processador.py`: loop da fila, validação e resumo
- `res.py`: separa os vídeos em subpastas por resolução
- `cli.py`: v0, terminal
- `app.py`: v1, janela Tkinter
