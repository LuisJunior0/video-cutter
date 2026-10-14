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

## Uso (v0)

```
python cli.py pasta_dos_videos
```

## Estrutura

- `selecao.py`: `selecionar_area()` com OpenCV
- `corte.py`: `cortar()` com FFmpeg
- `processador.py`: loop da fila, validação e resumo
- `cli.py`: v0, terminal
- `app.py`: v1, janela Tkinter
