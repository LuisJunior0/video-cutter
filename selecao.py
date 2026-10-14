import cv2


def _ler_frame(caminho):
    """Frame em ~1s (foge de tela preta); se o vídeo for curto ou não permitir
    pular, usa o primeiro frame."""
    for pos_ms in (1000, 0):
        cap = cv2.VideoCapture(caminho)
        if pos_ms:
            cap.set(cv2.CAP_PROP_POS_MSEC, pos_ms)
        ok, frame = cap.read()
        cap.release()
        if ok:
            return frame
    raise RuntimeError(f"Não consegui ler o vídeo: {caminho}")


def selecionar_area(caminho, max_w=1280, max_h=720):
    """Mostra um frame do vídeo e devolve a área (x, y, largura, altura) em pixels reais."""
    frame = _ler_frame(caminho)

    h, w = frame.shape[:2]
    escala = min(max_w / w, max_h / h, 1.0)
    preview = cv2.resize(frame, (int(w * escala), int(h * escala)))

    x, y, cw, ch = cv2.selectROI("Selecione e aperte Enter", preview, showCrosshair=True)
    cv2.destroyAllWindows()
    if cw == 0 or ch == 0:
        return None  # usuário cancelou

    par = lambda v: int(v / escala) // 2 * 2  # H.264 não aceita dimensão ímpar
    return par(x), par(y), par(cw), par(ch)
