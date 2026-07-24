"""
CSS customizado do app, baseado no design aprovado (fundo escuro, amarelo
de destaque, fonte Manrope/IBM Plex Mono) - mantendo o nome e a logo atuais
(Sebem), só aplicando a paleta/tipografia por cima dos componentes nativos
do Streamlit.

Os seletores de botão/input usam atributos data-testid (stButton,
stDownloadButton, etc) em vez de classes CSS geradas, porque essas classes
mudam de hash entre versões do Streamlit - data-testid é o jeito estável
de mirar nos componentes.
"""

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

.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12.5px; letter-spacing: 0.06em; color: var(--ink-dim);
  border: 1px solid var(--line);
  background: var(--bg-soft);
  padding: 8px 16px; border-radius: 999px;
  margin: 4px 0 20px;
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
  font-size: clamp(30px, 4.5vw, 48px);
  font-weight: 800; line-height: 1.1; letter-spacing: -0.02em;
  color: var(--ink); margin: 0;
}
.hero-title .accent { color: var(--accent); }

.hero-sub {
  margin-top: 14px; max-width: 560px;
  font-size: 16px; line-height: 1.6; color: var(--ink-dim); font-weight: 500;
}

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


def hero(st, eyebrow: str, titulo_html: str, subtitulo: str) -> None:
    st.markdown(
        f'<div class="hero-eyebrow"><span class="dot"></span>{eyebrow}</div>'
        f'<div class="hero-title">{titulo_html}</div>'
        f'<div class="hero-sub">{subtitulo}</div>',
        unsafe_allow_html=True,
    )
