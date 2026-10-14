"""Loop da fila: validação de resolução, nomes de saída e resumo.

Sem dependência de interface; usado por cli.py (v0) e app.py (v1).
"""
from pathlib import Path

import cv2

from corte import cortar


EXTENSOES = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v", ".flv", ".wmv", ".ts"}


def listar_videos(pasta):
    return sorted(p for p in Path(pasta).iterdir()
                  if p.is_file() and p.suffix.lower() in EXTENSOES)


def resolucao(caminho):
    cap = cv2.VideoCapture(str(caminho))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return w, h


def ajustar_area(area, res):
    """Limita a área aos limites do vídeo (largura e altura pares). None se não sobrar nada."""
    x, y, w, h = area
    W, H = res
    w = min(w, W - x) // 2 * 2
    h = min(h, H - y) // 2 * 2
    if w <= 0 or h <= 0:
        return None
    return x, y, w, h


def processar_fila(videos, area, pasta_saida, encoder=None, ao_progredir=None):
    """Corta `area` de cada vídeo, comparando a resolução com a do primeiro.

    Vídeos com resolução diferente da referência também são cortados: a área
    (em pixels) é limitada aos limites do vídeo e o aviso vai para `avisos`.

    `ao_progredir(i, total, caminho)` é chamado antes de cada vídeo.
    Devolve (ok, falhas, avisos): caminhos, (caminho, motivo) e (caminho, aviso).
    """
    videos = [Path(v) for v in videos]
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    ref = resolucao(videos[0])
    ok, falhas, avisos = [], [], []
    usadas = set()

    for i, video in enumerate(videos, 1):
        if ao_progredir:
            ao_progredir(i, len(videos), video)
        saida = pasta_saida / (video.stem + ".mp4")  # saída sempre em MP4
        if saida.resolve() == video.resolve():
            falhas.append((video, "saída seria o próprio original"))
            continue
        if saida in usadas:
            falhas.append((video, f"outro vídeo já gerou {saida.name}"))
            continue
        usadas.add(saida)
        res = resolucao(video)
        area_video = area
        if res != ref:
            area_video = ajustar_area(area, res)
            if area_video is None:
                falhas.append((video, f"área fora do vídeo ({res[0]}x{res[1]})"))
                continue
            if area_video != tuple(area):
                _, _, w, h = area_video
                avisos.append((video, f"resolução {res[0]}x{res[1]} (ref. {ref[0]}x{ref[1]}): área ajustada para {w}x{h}"))
            else:
                avisos.append((video, f"resolução {res[0]}x{res[1]} (ref. {ref[0]}x{ref[1]}): área mantida"))
        sucesso, erro = cortar(video, saida, area_video, encoder)
        if sucesso:
            ok.append(video)
        else:
            falhas.append((video, erro.strip() or "erro no ffmpeg"))
    return ok, falhas, avisos
