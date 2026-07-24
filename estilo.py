"""
CSS + marcação customizada do app, seguindo o design aprovado (fundo
escuro, amarelo de destaque, fonte Manrope/IBM Plex Mono, barra fixa no
topo, hero com "trilha" de pontinhos animados e faixa de transportadoras)
- mantendo o nome e a logo atuais (Sebem/robozinho) em vez da marca
"Rastro" do mockup original.

Os seletores de botão/input usam atributos data-testid (stButton,
stDownloadButton, etc) em vez de classes CSS geradas, porque essas classes
mudam de hash entre versões do Streamlit - data-testid é o jeito estável
de mirar nos componentes.
"""

import base64
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGO_B64_PATH = os.path.join(_DIR, "assets", "logo_b64.txt")


def _logo_base64() -> str:
    with open(_LOGO_B64_PATH, encoding="ascii") as f:
        return f.read().strip()


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --bg: #050505;
  --bg-soft: #121212;
  --line: rgba(255,255,255,0.09);
  --ink: #F5F2E8;
  --ink-dim: #9A968A;
  --accent: #F4BE41;
}

.stApp {
  background: var(--bg);
  font-family: 'Manrope', sans-serif;
}

.stApp p, .stApp label, .stApp span, .stApp li, .stMarkdown {
  color: var(--ink-dim);
}

h1, h2, h3 {
  font-weight: 800 !important;
  letter-spacing: -0.02em;
  color: var(--ink) !important;
}

/* ---------- Barra do topo ---------- */
.topbar {
  position: sticky; top: 0; z-index: 999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 8px;
  background: rgba(10,13,18,0.72);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--line);
  margin: -1rem -1rem 2rem;
}
.topbar .brand { display: flex; align-items: center; gap: 10px; padding-left: 24px; }
.topbar .brand img { width: 32px; height: 32px; border-radius: 8px; }
.topbar .brand span { font-weight: 800; font-size: 17px; color: var(--ink); letter-spacing: -0.01em; }

.topnav { display: flex; align-items: center; gap: 28px; padding-right: 24px; }
.topnav a { font-size: 14px; font-weight: 500; color: var(--ink-dim); }
.topnav a:hover { color: var(--ink); }
.topnav .nav-cta {
  background: var(--ink); color: var(--bg);
  padding: 9px 18px; border-radius: 999px;
  font-weight: 700; font-size: 13.5px;
}
.topnav .nav-cta:hover { background: var(--accent); color: var(--bg); }

@media (max-width: 700px) {
  .topnav a:not(.nav-cta) { display: none; }
}

/* ---------- Hero ---------- */
.hero {
  display: flex; flex-direction: column; align-items: center;
  text-align: center;
  padding: 40px 8px 20px;
}

.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12.5px; letter-spacing: 0.06em; color: var(--ink-dim);
  border: 1px solid var(--line);
  background: var(--bg-soft);
  padding: 8px 16px; border-radius: 999px;
  margin: 4px 0 28px;
}
.hero-eyebrow .dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
  display: inline-block;
  animation: ping 2.2s ease-out infinite;
}
@keyframes ping {
  0% { box-shadow: 0 0 0 0 rgba(244,190,65,0.5); }
  70% { box-shadow: 0 0 0 8px rgba(244,190,65,0); }
  100% { box-shadow: 0 0 0 0 rgba(244,190,65,0); }
}

.hero-title {
  font-size: clamp(34px, 6vw, 60px);
  font-weight: 800; line-height: 1.06; letter-spacing: -0.02em;
  color: var(--ink); margin: 0; max-width: 680px;
}
.hero-title .accent { color: var(--accent); }

.hero-sub {
  margin: 18px auto 0; max-width: 520px;
  font-size: 16px; line-height: 1.6; color: var(--ink-dim); font-weight: 500;
}

.hero-cta-row { margin-top: 32px; display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; }
.hero-cta-row a { display: inline-block; }
.btn-primary {
  background: var(--ink); color: var(--bg);
  padding: 13px 26px; border-radius: 999px;
  font-weight: 800; font-size: 14.5px;
  transition: transform .18s ease, background .18s ease;
}
.btn-primary:hover { transform: translateY(-2px); background: var(--accent); color: var(--bg); }
.btn-ghost {
  padding: 13px 24px; border-radius: 999px;
  border: 1px solid var(--line); color: var(--ink-dim);
  font-weight: 700; font-size: 14.5px;
}
.btn-ghost:hover { color: var(--ink); border-color: rgba(255,255,255,0.24); }

/* ---------- Trilha ---------- */
.trail-visual { margin-top: 56px; display: flex; align-items: center; justify-content: center; gap: 0; flex-wrap: wrap; }
.trail-track { display: flex; align-items: flex-end; gap: 18px; height: 50px; }
.trail-dot { border-radius: 50%; background: var(--accent); animation: rise 2.6s ease-in-out infinite; }
.trail-dot:nth-child(1) { width: 7px; height: 7px; opacity: 0.35; animation-delay: 0s; }
.trail-dot:nth-child(2) { width: 9px; height: 9px; opacity: 0.5; animation-delay: .15s; }
.trail-dot:nth-child(3) { width: 12px; height: 12px; opacity: 0.68; animation-delay: .3s; }
.trail-dot:nth-child(4) { width: 15px; height: 15px; opacity: 0.84; animation-delay: .45s; }
.trail-dot:nth-child(5) { width: 18px; height: 18px; opacity: 1; animation-delay: .6s; }
@keyframes rise { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.trail-card {
  margin-left: 20px;
  display: flex; align-items: center; gap: 12px;
  background: var(--bg-soft); border: 1px solid var(--line);
  border-radius: 16px; padding: 12px 18px;
  font-family: 'IBM Plex Mono', monospace; font-size: 12.5px;
}
.trail-card .pin { width: 22px; height: 22px; flex-shrink: 0; }
.trail-card .status { color: var(--ink-dim); }
.trail-card .code { color: var(--ink); font-weight: 500; }
.trail-card .live { color: var(--accent); font-weight: 500; }

/* ---------- Faixa de transportadoras ---------- */
.partners {
  margin-top: 52px; margin-bottom: 12px;
  display: flex; flex-direction: column; align-items: center; gap: 14px;
}
.partners .label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11.5px; letter-spacing: 0.08em; color: var(--ink-dim); opacity: 0.7;
}
.partners .row {
  display: flex; gap: 32px; flex-wrap: wrap; justify-content: center;
  font-weight: 700; font-size: 14px; color: rgba(245,242,232,0.55);
}

/* ---------- Componentes Streamlit ---------- */
div[data-testid="stButton"] > button,
div[data-testid="stDownloadButton"] > button,
div[data-testid="stLinkButton"] > a {
  background: var(--ink) !important;
  color: var(--bg) !important;
  border: none !important;
  border-radius: 999px !important;
  font-weight: 800 !important;
  padding: 10px 24px !important;
  transition: transform .15s ease, background .15s ease;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stLinkButton"] > a:hover {
  background: var(--accent) !important;
  color: var(--bg) !important;
  transform: translateY(-1px);
}

div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {
  background: var(--bg-soft) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  border-radius: 10px !important;
}

div[data-testid="stFileUploaderDropzone"] {
  background: var(--bg-soft) !important;
  border: 1px dashed var(--line) !important;
  border-radius: 12px !important;
}

hr { border-color: var(--line) !important; }
</style>
"""


def aplicar_estilo(st) -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def topbar(st) -> None:
    logo_b64 = _logo_base64()
    st.markdown(
        '<div class="topbar">'
        '<a class="brand" href="#">'
        f'<img src="data:image/png;base64,{logo_b64}" alt="logo">'
        "<span>Rastreio Sebem</span>"
        "</a>"
        '<nav class="topnav">'
        '<a href="#rastrear">Rastrear</a>'
        '<a href="#">Como funciona</a>'
        '<a href="#">Sobre</a>'
        '<a class="nav-cta" href="#rastrear">Testar agora</a>'
        "</nav>"
        "</div>",
        unsafe_allow_html=True,
    )


def hero(st, eyebrow: str, titulo_html: str, subtitulo: str) -> None:
    st.markdown(
        '<div class="hero">'
        f'<div class="hero-eyebrow"><span class="dot"></span>{eyebrow}</div>'
        f'<div class="hero-title">{titulo_html}</div>'
        f'<div class="hero-sub">{subtitulo}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def hero_cta(st) -> None:
    st.markdown(
        '<div class="hero-cta-row">'
        '<a class="btn-primary" href="#rastrear">Rastrear uma nota</a>'
        '<a class="btn-ghost" href="#">Como funciona</a>'
        "</div>",
        unsafe_allow_html=True,
    )


def trail_visual(st) -> None:
    st.markdown(
        '<div class="trail-visual">'
        '<div class="trail-track">'
        '<span class="trail-dot"></span><span class="trail-dot"></span>'
        '<span class="trail-dot"></span><span class="trail-dot"></span>'
        '<span class="trail-dot"></span>'
        "</div>"
        '<div class="trail-card">'
        '<svg class="pin" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<path d="M255 78 c34 0 61 26.5 61 60 c0 41 -45 80 -61 101 c-16 -21 -61 -60 -61 -101 '
        'c0 -33.5 27 -60 61 -60 Z" fill="#F4BE41"></path>'
        '<circle cx="255" cy="138" r="22" fill="#050505"></circle>'
        "</svg>"
        "<div>"
        '<div class="code">NF-e 000.482.910</div>'
        '<div class="status">Rodonaves · <span class="live">saiu para entrega</span></div>'
        "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def partners_strip(st, nomes: list[str]) -> None:
    linhas = "".join(f"<span>{nome}</span>" for nome in nomes)
    st.markdown(
        '<div class="partners">'
        '<div class="label">TRANSPORTADORAS SUPORTADAS</div>'
        f'<div class="row">{linhas}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
