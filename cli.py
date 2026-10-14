"""v0: python cli.py pasta_dos_videos [pasta_saida]  (entrada: mp4, webm, mkv...; saída: mp4)"""
import sys
from pathlib import Path

from corte import escolher_encoder
from processador import listar_videos, processar_fila
from selecao import selecionar_area


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python cli.py pasta_dos_videos [pasta_saida]")
    pasta = Path(sys.argv[1]).expanduser()
    if not pasta.is_dir():
        sys.exit(f"Pasta não encontrada: {pasta}")
    saida = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else pasta / "cortados"

    videos = listar_videos(pasta)
    if not videos:
        sys.exit(f"Nenhum vídeo em {pasta}")
    print(f"{len(videos)} vídeo(s). Selecione a área no primeiro e aperte Enter (Esc cancela).")

    area = selecionar_area(str(videos[0]))
    if area is None:
        sys.exit("Seleção cancelada.")
    x, y, w, h = area
    print(f"Área: {w}x{h} a partir de ({x},{y}) | encoder: {escolher_encoder()}")

    ok, falhas, avisos = processar_fila(
        videos, area, saida,
        ao_progredir=lambda i, n, v: print(f"[{i}/{n}] {v.name}"))

    print(f"\nResumo: {len(ok)} ok, {len(falhas)} falharam. Saída: {saida}")
    for video, aviso in avisos:
        print(f"  AVISO  {video.name}: {aviso}")
    for video, motivo in falhas:
        print(f"  FALHOU {video.name}: {motivo}")


if __name__ == "__main__":
    main()
