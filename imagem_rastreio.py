"""
Gera uma imagem PNG do histórico de rastreio, no estilo visual do
"Rastreamento detalhado" que aparece no site da Atual Cargas (fundo
branco, cabeçalho cinza, situação em vermelho negrito, linhas
alternadas) - pra dar pra baixar e mandar pro cliente.

Usa Pillow puro (sem depender de navegador/wkhtmltoimage) e as fontes
DejaVu Sans empacotadas em assets/, pra ficar consistente tanto local
(Windows) quanto no Streamlit Cloud (Linux, que não tem as fontes do
Windows disponíveis).
"""

import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

_DIR = os.path.dirname(os.path.abspath(__file__))
_FONTE_REGULAR = os.path.join(_DIR, "assets", "DejaVuSans.ttf")
_FONTE_BOLD = os.path.join(_DIR, "assets", "DejaVuSans-Bold.ttf")

COR_AZUL = (26, 62, 116)
COR_VERMELHO = (214, 40, 40)
COR_CINZA_TEXTO = (110, 110, 110)
COR_CINZA_HEADER = (150, 150, 150)
COR_LINHA_PAR = (255, 255, 255)
COR_LINHA_IMPAR = (240, 240, 240)
COR_BORDA = (210, 210, 210)

LARGURA = 780
MARGEM = 24
COL_DATA = 110
COL_UNIDADE = 150
COL_SITUACAO = LARGURA - 2 * MARGEM - COL_DATA - COL_UNIDADE
PAD_COL = 10


def _fonte(tamanho: int, negrito: bool = False) -> ImageFont.FreeTypeFont:
    caminho = _FONTE_BOLD if negrito else _FONTE_REGULAR
    return ImageFont.truetype(caminho, tamanho)


def _quebrar_texto(draw: ImageDraw.ImageDraw, texto: str, fonte, largura_max: int) -> list[str]:
    if not texto:
        return [""]
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        tentativa = f"{linha_atual} {palavra}".strip()
        if draw.textlength(tentativa, font=fonte) <= largura_max:
            linha_atual = tentativa
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas or [""]


def gerar_imagem_historico(
    historico: list[dict],
    destinatario: str = "",
    n_fiscal: str = "",
    n_pedido: str = "",
    previsao_entrega: str = "",
) -> bytes:
    """Gera a imagem PNG do histórico de rastreio e devolve os bytes
    (prontos pro st.download_button)."""
    fonte_normal = _fonte(13)
    fonte_negrito = _fonte(13, negrito=True)
    fonte_titulo = _fonte(19, negrito=True)
    fonte_marca = _fonte(21, negrito=True)

    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    largura_situacao_texto = COL_SITUACAO - 2 * PAD_COL
    largura_unidade_texto = COL_UNIDADE - 2 * PAD_COL

    linhas_tabela = []
    for evento in historico:
        linhas_situacao = _quebrar_texto(dummy, evento.get("Situação", ""), fonte_negrito, largura_situacao_texto)
        linhas_detalhe = _quebrar_texto(dummy, evento.get("Detalhe", ""), fonte_normal, largura_situacao_texto)
        linhas_unidade = _quebrar_texto(dummy, evento.get("Unidade", ""), fonte_normal, largura_unidade_texto)
        altura_situacao = 16 + len(linhas_situacao) * 18 + 4 + len(linhas_detalhe) * 16 + 12
        altura_unidade = 24 + len(linhas_unidade) * 16
        altura = max(altura_situacao, altura_unidade)
        linhas_tabela.append((evento, linhas_situacao, linhas_detalhe, linhas_unidade, max(altura, 46)))

    altura_topo = 128
    altura_cabecalho_tabela = 34
    altura_total = altura_topo + altura_cabecalho_tabela + sum(l[4] for l in linhas_tabela) + MARGEM

    img = Image.new("RGB", (LARGURA, altura_total), "white")
    draw = ImageDraw.Draw(img)

    y = MARGEM
    draw.text((LARGURA / 2, y), "ATUALCARGAS", font=fonte_marca, fill=COR_AZUL, anchor="ma")
    y += 36

    draw.text((MARGEM, y), "Rastreamento detalhado", font=fonte_titulo, fill=COR_VERMELHO)
    y += 30

    if destinatario:
        draw.text((MARGEM, y), f"Destinatário: {destinatario}", font=fonte_normal, fill=COR_AZUL)
    if previsao_entrega:
        texto_previsao = f"Previsão de entrega: {previsao_entrega}"
        largura_previsao = draw.textlength(texto_previsao, font=fonte_negrito)
        draw.text((LARGURA - MARGEM - largura_previsao, y), texto_previsao, font=fonte_negrito, fill=COR_AZUL)
    y += 22

    partes = []
    if n_fiscal:
        partes.append(f"N Fiscal: {n_fiscal}")
    if n_pedido:
        partes.append(f"N Pedido: {n_pedido}")
    if partes:
        draw.text((MARGEM, y), "     ".join(partes), font=fonte_normal, fill=COR_AZUL)
    y += 28

    x0 = MARGEM
    x1 = MARGEM + COL_DATA
    x2 = MARGEM + COL_DATA + COL_UNIDADE
    x3 = LARGURA - MARGEM

    draw.rectangle([x0, y, x3, y + altura_cabecalho_tabela], fill=COR_CINZA_HEADER)
    draw.text((x0 + PAD_COL, y + 9), "Data/Hora", font=fonte_negrito, fill="white")
    draw.text((x1 + PAD_COL, y + 9), "Unidade", font=fonte_negrito, fill="white")
    draw.text((x2 + PAD_COL, y + 9), "Situação", font=fonte_negrito, fill="white")
    y += altura_cabecalho_tabela

    for i, (evento, linhas_situacao, linhas_detalhe, linhas_unidade, altura_linha) in enumerate(linhas_tabela):
        cor_fundo = COR_LINHA_PAR if i % 2 == 0 else COR_LINHA_IMPAR
        draw.rectangle([x0, y, x3, y + altura_linha], fill=cor_fundo, outline=COR_BORDA)

        draw.text((x0 + PAD_COL, y + 12), evento.get("Data/Hora", ""), font=fonte_normal, fill=COR_CINZA_TEXTO)

        y_unidade = y + 12
        for linha in linhas_unidade:
            draw.text((x1 + PAD_COL, y_unidade), linha, font=fonte_normal, fill=COR_CINZA_TEXTO)
            y_unidade += 16

        y_texto = y + 10
        for linha in linhas_situacao:
            draw.text((x2 + PAD_COL, y_texto), linha, font=fonte_negrito, fill=COR_VERMELHO)
            y_texto += 18
        y_texto += 2
        for linha in linhas_detalhe:
            draw.text((x2 + PAD_COL, y_texto), linha, font=fonte_normal, fill=COR_CINZA_TEXTO)
            y_texto += 16

        y += altura_linha

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
