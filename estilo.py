"""
CSS + marcação customizada do app: fundo escuro com o azul da marca (a
mesma cor da logo) como destaque, fonte Manrope/IBM Plex Mono, barra fixa
no topo (por cima da barra padrão do Streamlit, que fica escondida), hero
com brilho azul suave e faixa de transportadoras no rodapé.

A paleta vem toda de config.TEMA (o :root do CSS é montado a partir dela),
então pra trocar as cores mexe lá, não aqui - só os valores rgba() dos
brilhos/sombras é que estão escritos direto no CSS.

Os seletores de botão/input usam atributos data-testid (stButton,
stDownloadButton, etc) em vez de classes CSS geradas, porque essas classes
mudam de hash entre versões do Streamlit - data-testid é o jeito estável
de mirar nos componentes.
"""

from config import APP_NOME, LOGO_B64_PATH, TEMA


def _logo_base64() -> str:
    with open(LOGO_B64_PATH, encoding="ascii") as f:
        return f.read().strip()


# :root montado a partir de config.TEMA (fonte única da paleta) - o resto do
# CSS abaixo só referencia var(--x).
_ROOT = ":root {\n" + "\n".join(f"  --{k}: {v};" for k, v in TEMA.items()) + "\n}"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

__ROOT__

.stApp {""".replace("__ROOT__", _ROOT) + """
  background: var(--bg);
  font-family: 'Manrope', sans-serif;
}

.stApp p, .stApp label, .stApp span, .stApp li, .stMarkdown {
  color: var(--ink-dim);
}

.stApp a { text-decoration: none !important; }

h1, h2, h3 {
  font-weight: 800 !important;
  letter-spacing: -0.02em;
  color: var(--ink) !important;
}

/* esconde a barra padrão do Streamlit (Deploy/menu) pra nossa barra
   customizada ser o único cabeçalho visível */
header[data-testid="stHeader"] { display: none; }

/* compensa o espaço que a barra fixa ocupa, já que position:fixed tira
   ela do fluxo normal do documento */
.block-container { padding-top: 96px !important; }

/* ---------- Barra do topo ---------- */
.topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 32px;
  background: rgba(10,13,18,0.85);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--line);
}
.topbar .brand { display: flex; align-items: center; gap: 10px; }
.topbar .brand img { width: 32px; height: 32px; border-radius: 8px; }
.topbar .brand span { font-weight: 800; font-size: 17px; color: var(--ink); letter-spacing: -0.01em; }

.topnav { display: flex; align-items: center; gap: 28px; }
.topnav a { font-size: 14px; font-weight: 500; color: var(--ink-dim); }
.topnav a:hover { color: var(--ink); }
.topnav .nav-cta {
  background: var(--accent); color: #fff !important;
  padding: 9px 18px; border-radius: 999px;
  font-weight: 700; font-size: 13.5px;
}
.topnav .nav-cta:hover { background: var(--accent-hover); color: #fff !important; }

@media (max-width: 700px) {
  .topnav a:not(.nav-cta) { display: none; }
}

/* ---------- Hero ---------- */
.hero {
  display: flex; flex-direction: column; align-items: center;
  text-align: center;
  padding: 40px 8px 20px;
  background: radial-gradient(620px 340px at 50% 6%, rgba(30,80,255,0.16), transparent 70%);
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
  0% { box-shadow: 0 0 0 0 rgba(30,80,255,0.55); }
  70% { box-shadow: 0 0 0 8px rgba(30,80,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(30,80,255,0); }
}

.hero-title {
  font-size: clamp(34px, 6vw, 60px);
  font-weight: 800; line-height: 1.06; letter-spacing: -0.02em;
  color: var(--ink); margin: 0; max-width: 680px;
}
.hero-title .accent { color: var(--accent-soft); }

.hero-sub {
  margin: 18px auto 0; max-width: 520px;
  font-size: 16px; line-height: 1.6; color: var(--ink-dim); font-weight: 500;
}

.hero-cta-row { margin-top: 32px; display: flex; gap: 14px; flex-wrap: wrap; justify-content: center; }
.hero-cta-row a { display: inline-block; }
.hero-cta-row .btn-primary {
  background: var(--accent); color: #fff !important;
  padding: 13px 26px; border-radius: 999px;
  font-weight: 800; font-size: 14.5px;
  box-shadow: 0 6px 20px rgba(30,80,255,0.35);
  transition: transform .18s ease, background .18s ease, box-shadow .18s ease;
}
.hero-cta-row .btn-primary:hover { transform: translateY(-2px); background: var(--accent-hover); box-shadow: 0 10px 28px rgba(30,80,255,0.45); }

/* ---------- Faixa de transportadoras (rodapé) ---------- */
.partners {
  margin-top: 64px; margin-bottom: 12px;
  padding-top: 28px;
  border-top: 1px solid var(--line);
  display: flex; flex-direction: column; align-items: center; gap: 14px;
}
.partners .label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11.5px; letter-spacing: 0.08em; color: var(--ink-dim); opacity: 0.7;
}
.partners .row {
  display: flex; gap: 32px; flex-wrap: wrap; justify-content: center;
  font-weight: 700; font-size: 14px; color: rgba(237,241,250,0.5);
}

/* ---------- Componentes Streamlit ---------- */
div[data-testid="stButton"] > button,
div[data-testid="stDownloadButton"] > button,
div[data-testid="stLinkButton"] > a {
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 999px !important;
  font-weight: 800 !important;
  padding: 10px 24px !important;
  box-shadow: 0 6px 20px rgba(30,80,255,0.30);
  transition: transform .15s ease, background .15s ease, box-shadow .15s ease;
}
div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stLinkButton"] > a:hover {
  background: var(--accent-hover) !important;
  color: #fff !important;
  transform: translateY(-1px);
  box-shadow: 0 10px 28px rgba(30,80,255,0.40);
}

div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {
  background: var(--bg-soft) !important;
  border: 1px solid var(--line) !important;
  color: var(--ink) !important;
  border-radius: 10px !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(30,80,255,0.20) !important;
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
        f"<span>{APP_NOME}</span>"
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
