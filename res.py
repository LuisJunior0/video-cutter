"""python res.py pasta_dos_videos  -> imprime 'nome_video=LxA' para cada vídeo"""
import sys

from processador import listar_videos, resolucao


def listar_resolucoes(pasta):
    for video in listar_videos(pasta):
        w, h = resolucao(video)
        print(f"{video.name}={w}x{h}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python res.py pasta_dos_videos")
    listar_resolucoes(" ".join(sys.argv[1:]))
