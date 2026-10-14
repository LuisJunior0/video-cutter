import shutil
import subprocess
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def localizar_ffmpeg():
    """FFmpeg do PATH; se não houver, usa o binário que vem com imageio-ffmpeg."""
    caminho = shutil.which("ffmpeg")
    if caminho:
        return caminho
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError("FFmpeg não encontrado: instale no PATH ou rode pip install -r requirements.txt")


@lru_cache(maxsize=1)
def escolher_encoder():
    """h264_nvenc (placa NVIDIA) se disponível e funcionando; senão libx264 (CPU)."""
    ffmpeg = localizar_ffmpeg()
    lista = subprocess.run([ffmpeg, "-hide_banner", "-encoders"],
                           capture_output=True, text=True).stdout
    if "h264_nvenc" not in lista:
        return "libx264"
    teste = subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
         "-i", "color=c=black:s=256x256:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
        capture_output=True)
    return "h264_nvenc" if teste.returncode == 0 else "libx264"


def cortar(entrada, saida, area, encoder=None):
    """Corta `area` (x, y, largura, altura) de `entrada` e grava em `saida` (MP4).

    O áudio é copiado quando possível; se o formato não couber no MP4
    (ex.: Opus do .webm), é reencodado para AAC. Devolve (sucesso, stderr).
    """
    encoder = encoder or escolher_encoder()
    copiavel = Path(entrada).suffix.lower() in {".mp4", ".m4v", ".mov"}
    if copiavel:
        sucesso, erro = _rodar(entrada, saida, area, encoder, ["-c:a", "copy"])
        if sucesso:
            return True, erro
    return _rodar(entrada, saida, area, encoder, ["-c:a", "aac", "-b:a", "192k"])


def _rodar(entrada, saida, area, encoder, audio):
    x, y, w, h = area
    cmd = [localizar_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(entrada), "-vf", f"crop={w}:{h}:{x}:{y}"]
    if encoder == "h264_nvenc":  # placa NVIDIA
        cmd += ["-c:v", "h264_nvenc", "-preset", "p5",
                "-rc", "constqp", "-qp", "20"]
    else:  # plano B, pela CPU
        cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium"]
    cmd += audio + ["-movflags", "+faststart", str(saida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr
