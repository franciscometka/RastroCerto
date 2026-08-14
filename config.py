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
# Tema da UI (fundo escuro + amarelo). Fonte única da paleta do app - o
# estilo.py monta o bloco :root do CSS a partir daqui.
# ---------------------------------------------------------------------------
TEMA = {
    "bg": "#050505",
    "bg-soft": "#121212",
    "line": "rgba(255,255,255,0.09)",
    "ink": "#F5F2E8",
    "ink-dim": "#9A968A",
    "accent": "#F4BE41",
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
# Rede (usado pelo http_utils)
# ---------------------------------------------------------------------------
USER_AGENT = "Mozilla/5.0 (compatible; Sebem-Rastreio/1.0)"
HTTP_TIMEOUT = 20
HTTP_RETRIES = 3
