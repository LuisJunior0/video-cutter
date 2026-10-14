# Cortador de Vídeos em Massa

Oct 14, 2026 · @Jr

## Visão geral e escopo

Um programa de desktop em Python que corta a mesma área de vários vídeos de uma vez: você desenha o retângulo com o mouse em um vídeo de referência e ele aplica esse corte em toda a fila.

**Premissas do projeto**

- Todos os vídeos da fila têm a mesma resolução, então a área é guardada em pixels.
- O corte típico é tirar uma faixa de baixo, mas a seleção é um retângulo livre feito com o mouse.
- Entrada e saída em MP4, com o áudio copiado sem reprocessar.
- Roda no Windows, com placa de vídeo AMD (encoder `h264_amf`, com `libx264` como plano B).
- Uso pessoal: precisa ser funcional, não bonito.

**Fora do escopo**

- Cortes de tempo (trim de início/fim).
- Filtros, legendas, redimensionamento ou mudança de formato.
- Instalador ou empacotamento em `.exe` (fica como extra, se quiser).

## Stack e instalação

São quatro peças: o Python organiza, o OpenCV mostra o frame para a seleção, o Tkinter faz a janela e o FFmpeg corta.

| Peça | Para quê | Como instalar |
| --- | --- | --- |
| Python 3.11+ | Linguagem do projeto | python.org (marque "Add to PATH") |
| FFmpeg | Cortar e reencodar os vídeos | `winget install ffmpeg` ou baixar o build "full" do gyan.dev |
| opencv-python | Ler um frame e selecionar a área com o mouse | `pip install opencv-python` |
| Tkinter | Interface (janela, lista, botões) | Já vem com o Python |

Para confirmar o FFmpeg e o encoder AMD, rode no terminal:

```
ffmpeg -version
ffmpeg -hide_banner -encoders | findstr amf
```

Se aparecer `h264_amf` na segunda linha, a aceleração pela placa AMD está disponível.

Recomendado: criar um ambiente virtual com `python -m venv .venv` e guardar as dependências em `requirements.txt`.

## Fluxo do usuário

O uso inteiro cabe em cinco cliques: escolher vídeos, desenhar a área, conferir, processar e abrir a pasta de saída.

1. Abrir o programa e clicar em **Adicionar vídeos** (ou **Adicionar pasta**). Os arquivos entram na lista da fila.
2. Clicar em **Definir área**. Abre uma janela com um frame do primeiro vídeo (por volta de 1 segundo, para fugir de tela preta).
3. Arrastar o mouse sobre a parte que deve **ficar** no vídeo e apertar Enter. A janela mostra as dimensões resultantes, por exemplo `1920x1000 a partir de (0,0)`.
4. Escolher a pasta de saída (padrão: `cortados/` ao lado dos originais) e clicar em **Processar**.
5. A barra de progresso avança vídeo a vídeo. Ao final, aparece um resumo: quantos deram certo e quais falharam.

Detalhe importante: o retângulo marca o que **fica**, não o que sai. Para tirar dois dedos de baixo, você seleciona do topo até logo acima da faixa.

## Arquitetura e estrutura de pastas

Cada arquivo tem uma função só, e a interface (terminal na v0, janela na v1) apenas chama as mesmas funções de seleção e corte.

&#91;embedded content: arquitetura · 6 módulos\]

Como `selecao.py`, `corte.py` e `processador.py` não sabem nada de interface, a v1 reaproveita tudo da v0 sem reescrever.

```
cortador-videos/
├── cli.py            # v0: script de terminal
├── app.py            # v1: janela Tkinter
├── selecao.py        # selecionar_area() com OpenCV
├── corte.py          # cortar() com FFmpeg
├── processador.py    # loop da fila, validação e resumo
├── config.json       # v2: área salva (opcional)
├── requirements.txt  # opencv-python
└── README.md
```

## Detalhes técnicos

O coração do projeto são duas funções: uma devolve a área `(x, y, largura, altura)` em pixels reais, a outra chama o FFmpeg com essa área.

### 1. Selecionar a área

O frame é reduzido para caber na tela, a seleção é feita na versão reduzida e as coordenadas voltam para o tamanho real. Todos os valores são arredondados para baixo até um número par, porque o H.264 não aceita largura ou altura ímpar.

```python
import cv2

def selecionar_area(caminho, max_w=1280, max_h=720):
    cap = cv2.VideoCapture(caminho)
    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)  # pula a possivel tela preta inicial
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Nao consegui ler o video")

    h, w = frame.shape[:2]
    escala = min(max_w / w, max_h / h, 1.0)
    preview = cv2.resize(frame, (int(w * escala), int(h * escala)))

    x, y, cw, ch = cv2.selectROI("Selecione e aperte Enter", preview, showCrosshair=True)
    cv2.destroyAllWindows()
    if cw == 0 or ch == 0:
        return None  # usuario cancelou

    par = lambda v: int(v / escala) // 2 * 2
    return par(x), par(y), par(cw), par(ch)
```

### 2. Cortar com o FFmpeg

O filtro `crop=L:A:X:Y` corta a imagem; o áudio é copiado com `-c:a copy`. O vídeo precisa ser reencodado, então a escolha do encoder define a velocidade.

```python
import subprocess

def cortar(entrada, saida, area, encoder="h264_amf"):
    x, y, w, h = area
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", entrada, "-vf", f"crop={w}:{h}:{x}:{y}"]
    if encoder == "h264_amf":  # placa AMD
        cmd += ["-c:v", "h264_amf", "-quality", "quality",
                "-rc", "cqp", "-qp_i", "20", "-qp_p", "20"]
    else:  # plano B, pela CPU
        cmd += ["-c:v", "libx264", "-crf", "20", "-preset", "medium"]
    cmd += ["-c:a", "copy", "-movflags", "+faststart", saida]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stderr
```

| Parâmetro | O que controla | Valor inicial |
| --- | --- | --- |
| `-qp_i` / `-qp_p` (AMF) | Qualidade: menor = melhor e arquivo maior | 20 |
| `-crf` (libx264) | Mesma ideia, para o encoder da CPU | 20 (faixa útil: 18 a 23) |
| `-preset` (libx264) | Velocidade versus tamanho do arquivo | medium |
| `-movflags +faststart` | Vídeo começa a tocar antes de baixar inteiro | sempre ligado |

### 3. Validar a resolução

Mesmo com a premissa de resolução única, o programa confere cada vídeo antes de cortar: se a largura e a altura forem diferentes das do vídeo de referência, ele pula o arquivo e anota no resumo. Isso evita um corte torto silencioso. A leitura pode usar `cv2.CAP_PROP_FRAME_WIDTH` e `cv2.CAP_PROP_FRAME_HEIGHT`.

### 4. Nomes de saída

O arquivo cortado vai para a pasta de saída com o mesmo nome do original. Os originais nunca são sobrescritos: se entrada e saída apontarem para o mesmo arquivo, o programa recusa.

## Etapas de desenvolvimento

O projeto anda em três versões; a v0 sozinha já resolve o problema e serve de base para as outras.

### v0 — Script de linha de comando

Roda `python cli.py pasta_dos_videos`, abre a seleção no primeiro vídeo e corta a pasta inteira.

- [ ] Instalar Python, FFmpeg e opencv-python; confirmar `h264_amf`
- [ ] Escrever `selecionar_area()` e testar com um vídeo
- [ ] Escrever `cortar()` e testar com a área fixa
- [ ] Listar os `.mp4` da pasta e cortar em loop, imprimindo o progresso
- [ ] Validar resolução e pular os diferentes
- [ ] Imprimir o resumo final (ok / falhou)

### v1 — Interface com Tkinter

A mesma lógica, agora com janela, lista e barra de progresso.

- [ ] Janela com lista de vídeos e botões Adicionar vídeos / Adicionar pasta / Remover
- [ ] Botão Definir área, mostrando as dimensões escolhidas
- [ ] Escolha da pasta de saída
- [ ] Processar em uma thread separada, para a janela não travar
- [ ] Barra de progresso e resumo no fim

### v2 — Extras (opcionais)

- [ ] Salvar e carregar a área em um `config.json` (preset)
- [ ] Pré-visualizar o frame já cortado antes de processar
- [ ] Escolher encoder (AMD ou CPU) e qualidade na interface
- [ ] Processar 2 vídeos ao mesmo tempo
- [ ] Empacotar em `.exe` com PyInstaller

## Testes e problemas comuns

Teste sempre com 2 ou 3 vídeos curtos antes de soltar a fila de 50; a maioria dos erros aparece no primeiro arquivo.

**Roteiro rápido de teste**

- [ ] Um vídeo curto: o corte saiu na área certa e o áudio está sincronizado?
- [ ] Um vídeo com resolução diferente na fila: foi pulado e apareceu no resumo?
- [ ] Cancelar a seleção (Esc): o programa não quebra?
- [ ] Um nome de arquivo com espaço e acento: funcionou?
- [ ] Comparar o tempo com `h264_amf` e com `libx264` em um mesmo vídeo

| Sintoma | Causa provável | Solução |
| --- | --- | --- |
| `'ffmpeg' não é reconhecido` | FFmpeg fora do PATH | Reinstalar com winget ou adicionar a pasta `bin` ao PATH |
| Erro "width/height not divisible by 2" | Área com dimensão ímpar | Conferir o arredondamento para par em `selecionar_area()` |
| Erro ao abrir `h264_amf` | Driver AMD antigo ou build do FFmpeg sem AMF | Atualizar o driver ou usar `libx264` |
| Corte deslocado | Escala não foi desfeita | Dividir as coordenadas pela mesma `escala` usada na prévia |
| Janela congela durante o processamento | Processamento na thread da interface | Rodar o loop em `threading.Thread` |
| Vídeo sem som | Áudio em formato que o MP4 não aceita | Trocar `-c:a copy` por `-c:a aac -b:a 192k` |
| Frame preto na seleção | Vídeo começa com fade | Pegar o frame em 3 ou 5 segundos |
