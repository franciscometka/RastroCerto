"""
Constantes centralizadas do app: identidade, nomes das transportadoras,
paletas de cor (tema escuro da UI + cores da imagem de rastreio) e
parâmetros de rede.

Ter tudo aqui evita duplicar os mesmos valores em app.py, estilo.py,
imagem_rastreio.py e ssw_client.py - mudou uma cor ou uma URL, muda num
lugar só.
"""

import os

# ---------------------------------------------------------------------------
# Identidade / caminhos
# ---------------------------------------------------------------------------
APP_NOME = "Rastreio Sebem"
PAGE_TITLE = "Rastreio Automático - Sebem"

_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
LOGO_B64_PATH = os.path.join(ASSETS_DIR, "logo_b64.txt")
FONTE_REGULAR = os.path.join(ASSETS_DIR, "DejaVuSans.ttf")
FONTE_BOLD = os.path.join(ASSETS_DIR, "DejaVuSans-Bold.ttf")

# ---------------------------------------------------------------------------
# Transportadoras
# ---------------------------------------------------------------------------
# Chave = identificador interno usado no resto do sistema.
NOMES_TRANSPORTADORA = {
    "atual_cargas": "Atual Cargas",
    "rodonaves": "Rodonaves",
    "expresso_sao_miguel": "Expresso São Miguel",
}

# ---------------------------------------------------------------------------
# Tema da UI (fundo escuro + azul da marca). Fonte única da paleta do app - o
# estilo.py monta o bloco :root do CSS a partir daqui. A cor de destaque é o
# azul da logo (~#0838F8), ajustado pra ficar legível em tela escura; os
# neutros são levemente frios (azulados) pra casar com o azul em vez do creme
# quente que vinha do mockup antigo.
# ---------------------------------------------------------------------------
TEMA = {
    "bg": "#05070D",
    "bg-soft": "#0F1320",
    "line": "rgba(255,255,255,0.09)",
    "ink": "#EDF1FA",
    "ink-dim": "#8B93A7",
    "accent": "#1E50FF",         # azul da marca (fills, botões, dot)
    "accent-hover": "#3A66FF",   # hover dos botões
    "accent-soft": "#5B8CFF",    # azul mais claro pra texto/realce sobre fundo escuro
}

# ---------------------------------------------------------------------------
# Cores da imagem PNG de rastreio (imita o "Rastreamento detalhado" do site
# da Atual Cargas: fundo branco, azul da marca, situação em vermelho). É uma
# paleta separada do tema da UI, com propósito diferente.
# ---------------------------------------------------------------------------
CORES_IMAGEM = {
    "azul": (26, 62, 116),
    "vermelho": (214, 40, 40),
    "cinza_texto": (110, 110, 110),
    "cinza_header": (150, 150, 150),
    "linha_par": (255, 255, 255),
    "linha_impar": (240, 240, 240),
    "borda": (210, 210, 210),
}

# ---------------------------------------------------------------------------
# Atual Cargas / SSW (ssw.inf.br)
# ---------------------------------------------------------------------------
SSW_BASE = "https://ssw.inf.br"
SSW_URL = f"{SSW_BASE}/2/resultSSW_dest_nro"

# ---------------------------------------------------------------------------
# Rodonaves - API oficial (portal dev.rodonaves.com.br, docs públicas em
# https://dev.rodonaves.com.br/reference/rastreio-1). Autenticação é OAuth
# password grant (auth_type=DEV fixo, confirmado na documentação); token
# expira e precisa ser pedido de novo a cada consulta (não há endpoint de
# refresh documentado, e o token dura ~8h, mais que suficiente pro padrão
# de uso do app - uma consulta por vez).
# ---------------------------------------------------------------------------
RODONAVES_TOKEN_URL = "https://tracking-apigateway.rte.com.br/token"
RODONAVES_TRACKING_URL = "https://tracking-apigateway.rte.com.br/api/v1/tracking"
RODONAVES_AUTH_TYPE = "DEV"

# ---------------------------------------------------------------------------
# Expresso São Miguel - API oficial (documentação recebida por e-mail:
# "Manual Técnico - Integração Clientes", 2026). Autenticação é só nos
# headers da própria consulta (Access_Key + Customer) - sem endpoint de
# token separado como a Rodonaves.
#
# A Sebem tem 3 CNPJs diferentes que despacham por essa transportadora,
# cada um com seu próprio par Customer/Access_Key. Como o extractor.py só
# pega o CNPJ do destinatário (não o do remetente que emitiu a nota), o
# sao_miguel_client tenta os 3 pares em sequência até um funcionar.
# ---------------------------------------------------------------------------
SAO_MIGUEL_TRACKING_URL = "https://wsintegcli02.expressosaomiguel.com.br:40504/wsservernet/api/tracking"
SAO_MIGUEL_MODELO_CONSULTA = "TRACKING_COMPLETO_POR_NOTA_FISCAL_E_COMPROVANTE"

# ---------------------------------------------------------------------------
# Rede (usado pelo http_utils)
# ---------------------------------------------------------------------------
USER_AGENT = "Mozilla/5.0 (compatible; Sebem-Rastreio/1.0)"
HTTP_TIMEOUT = 20
# 5 tentativas com backoff 1.0 (1s, 2s, 4s, 8s, 16s ~ até 31s de espera total)
# - subiu de 3/0.5 depois de falhas de DNS transitórias no container do
# Streamlit Cloud (tracking-apigateway.rte.com.br, domínio saudável testado
# de fora, então o problema é rede interna do Cloud, não do lado de cá).
HTTP_RETRIES = 5
HTTP_BACKOFF_FACTOR = 1.0
