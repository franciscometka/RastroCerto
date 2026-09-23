"""
Gera imagens PNG do histórico de rastreio, no mesmo estilo visual (fundo
branco, cabeçalho cinza, linhas alternadas) pra dar pra baixar e mandar
pro cliente - uma versão pra Atual Cargas (`gerar_imagem_historico`,
imita o "Rastreamento detalhado" do site deles, com coluna de Unidade) e
uma pra Rodonaves (`gerar_imagem_rodonaves`, 2 colunas só, já que os
eventos da API vêm como frase única em vez de título+unidade separados).

Usa Pillow puro (sem depender de navegador/wkhtmltoimage) e as fontes
DejaVu Sans empacotadas em assets/, pra ficar consistente tanto local
(Windows) quanto no Streamlit Cloud (Linux, que não tem as fontes do
Windows disponíveis).
"""

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from config import CORES_IMAGEM, FONTE_BOLD as _FONTE_BOLD, FONTE_REGULAR as _FONTE_REGULAR

COR_AZUL = CORES_IMAGEM["azul"]
COR_VERMELHO = CORES_IMAGEM["vermelho"]
COR_CINZA_TEXTO = CORES_IMAGEM["cinza_texto"]
COR_CINZA_HEADER = CORES_IMAGEM["cinza_header"]
COR_LINHA_PAR = CORES_IMAGEM["linha_par"]
COR_LINHA_IMPAR = CORES_IMAGEM["linha_impar"]
COR_BORDA = CORES_IMAGEM["borda"]

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


def gerar_imagem_rodonaves(
    eventos: list[dict],
    destinatario: str = "",
    protocolo: str = "",
    previsao_dias: int | None = None,
) -> bytes:
    """Gera a imagem PNG do histórico de rastreio da Rodonaves. Fina camada
    sobre `gerar_imagem_2_colunas` só pra formatar a previsão em "X dias
    após a emissão" (formato que a API da Rodonaves devolve) e o rótulo
    "Protocolo"."""
    previsao_texto = f"{previsao_dias} dias após a emissão" if previsao_dias is not None else ""
    linha_info = f"Protocolo: {protocolo}" if protocolo else ""
    return gerar_imagem_2_colunas(
        marca="RODONAVES",
        eventos=eventos,
        destinatario=destinatario,
        linha_info=linha_info,
        previsao_texto=previsao_texto,
    )


def gerar_imagem_sao_miguel(
    eventos: list[dict],
    numero_documento: str = "",
    unidade_destino: str = "",
    previsao_entrega: str = "",
) -> bytes:
    """Gera a imagem PNG do histórico de rastreio da Expresso São Miguel.
    Fina camada sobre `gerar_imagem_2_colunas` - a API deles não devolve o
    nome do destinatário (só endereço de entrega), então mostra o número
    do documento e a unidade de destino em vez disso."""
    partes = []
    if numero_documento:
        partes.append(f"Documento: {numero_documento}")
    if unidade_destino:
        partes.append(f"Unidade destino: {unidade_destino}")
    return gerar_imagem_2_colunas(
        marca="EXPRESSO SÃO MIGUEL",
        eventos=eventos,
        linha_info=" · ".join(partes),
        previsao_texto=previsao_entrega,
    )


def gerar_imagem_2_colunas(
    marca: str,
    eventos: list[dict],
    destinatario: str = "",
    linha_info: str = "",
    previsao_texto: str = "",
) -> bytes:
    """Gera uma imagem PNG de histórico de rastreio com layout de 2 colunas
    (Data/Hora | Situação) - usado por transportadoras cuja API devolve cada
    evento como uma frase única (`descrição`/`Description`), sem título
    curto e unidade separados como o HTML do SSW tem (não dá pra fingir a
    mesma estrutura de 3 colunas da Atual Cargas sem inventar dado).

    O evento mais recente (último da lista, que é a ordem que essas APIs
    devolvem) fica em negrito/vermelho pra destacar o status atual; os
    anteriores ficam em cinza normal.
    """
    fonte_normal = _fonte(13)
    fonte_negrito = _fonte(13, negrito=True)
    fonte_titulo = _fonte(19, negrito=True)
    fonte_marca = _fonte(21, negrito=True)

    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    col_data = 110
    col_situacao = LARGURA - 2 * MARGEM - col_data
    largura_situacao_texto = col_situacao - 2 * PAD_COL

    ultimo_indice = len(eventos) - 1
    linhas_tabela = []
    for i, evento in enumerate(eventos):
        fonte_linha = fonte_negrito if i == ultimo_indice else fonte_normal
        linhas_situacao = _quebrar_texto(dummy, evento.get("Situação", ""), fonte_linha, largura_situacao_texto)
        altura = 24 + len(linhas_situacao) * 17
        linhas_tabela.append((evento, linhas_situacao, max(altura, 44)))

    altura_topo = 128
    altura_cabecalho_tabela = 34
    altura_total = altura_topo + altura_cabecalho_tabela + sum(l[2] for l in linhas_tabela) + MARGEM

    img = Image.new("RGB", (LARGURA, altura_total), "white")
    draw = ImageDraw.Draw(img)

    y = MARGEM
    draw.text((LARGURA / 2, y), marca, font=fonte_marca, fill=COR_AZUL, anchor="ma")
    y += 36

    draw.text((MARGEM, y), "Rastreamento detalhado", font=fonte_titulo, fill=COR_VERMELHO)
    y += 30

    if destinatario:
        draw.text((MARGEM, y), f"Destinatário: {destinatario}", font=fonte_normal, fill=COR_AZUL)
    if previsao_texto:
        texto_previsao = f"Previsão de entrega: {previsao_texto}"
        largura_previsao = draw.textlength(texto_previsao, font=fonte_negrito)
        draw.text((LARGURA - MARGEM - largura_previsao, y), texto_previsao, font=fonte_negrito, fill=COR_AZUL)
    y += 22

    if linha_info:
        draw.text((MARGEM, y), linha_info, font=fonte_normal, fill=COR_AZUL)
    y += 28

    x0 = MARGEM
    x1 = MARGEM + col_data
    x2 = LARGURA - MARGEM

    draw.rectangle([x0, y, x2, y + altura_cabecalho_tabela], fill=COR_CINZA_HEADER)
    draw.text((x0 + PAD_COL, y + 9), "Data/Hora", font=fonte_negrito, fill="white")
    draw.text((x1 + PAD_COL, y + 9), "Situação", font=fonte_negrito, fill="white")
    y += altura_cabecalho_tabela

    for i, (evento, linhas_situacao, altura_linha) in enumerate(linhas_tabela):
        cor_fundo = COR_LINHA_PAR if i % 2 == 0 else COR_LINHA_IMPAR
        draw.rectangle([x0, y, x2, y + altura_linha], fill=cor_fundo, outline=COR_BORDA)

        draw.text((x0 + PAD_COL, y + 12), evento.get("Data/Hora", ""), font=fonte_normal, fill=COR_CINZA_TEXTO)

        destaque = i == ultimo_indice
        fonte_texto = fonte_negrito if destaque else fonte_normal
        cor_texto = COR_VERMELHO if destaque else COR_CINZA_TEXTO
        y_texto = y + 12
        for linha in linhas_situacao:
            draw.text((x1 + PAD_COL, y_texto), linha, font=fonte_texto, fill=cor_texto)
            y_texto += 17

        y += altura_linha

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
