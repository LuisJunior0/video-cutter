"""python res.py pasta_dos_videos  -> move cada vídeo para uma subpasta com a sua resolução (ex.: 1920x1080)"""
import shutil
import sys
from pathlib import Path

from processador import listar_videos, resolucao


def separar_por_resolucao(pasta):
    pasta = Path(pasta)
    contagem = {}
    for video in listar_videos(pasta):
        w, h = resolucao(video)
        nome_pasta = f"{w}x{h}" if w and h else "ilegiveis"
        destino = pasta / nome_pasta
        if (destino / video.name).exists():
            print(f"PULADO {video.name}: já existe em {nome_pasta}")
            continue
        destino.mkdir(exist_ok=True)
        shutil.move(str(video), str(destino / video.name))
        contagem[nome_pasta] = contagem.get(nome_pasta, 0) + 1
        print(f"{video.name} -> {nome_pasta}")

    print("\nResumo:")
    for nome_pasta, n in sorted(contagem.items()):
        print(f"  {nome_pasta}: {n} vídeo(s)")
    return contagem


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Uso: python res.py pasta_dos_videos")
    pasta = Path(" ".join(sys.argv[1:])).expanduser()
    if not pasta.is_dir():
        sys.exit(f'Pasta não encontrada: {pasta}\nSe o caminho tem espaços, use aspas: python res.py "C:\\minha pasta\\videos"')
    separar_por_resolucao(pasta)
