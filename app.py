import os
import tempfile

import streamlit as st

from config import LOGO_PATH, NOMES_TRANSPORTADORA, PAGE_TITLE
from estilo import aplicar_estilo, hero, hero_cta, partners_strip, topbar
from extractor import processar_pdf
from resultado_display import (
    mostrar_portal_manual,
    mostrar_resultado_atual_cargas,
    mostrar_resultado_rodonaves,
)
from rodonaves_client import consultar_rodonaves
from semi_auto import get_portal
from ssw_client import consultar_atual_cargas
from validators import documento_valido, numero_nf_valido


def _credencial_rodonaves(chave: str) -> str:
    """Lê a credencial da Rodonaves de st.secrets (local: .streamlit/secrets.toml;
    produção: Secrets do Streamlit Cloud), com fallback pra variável de
    ambiente - assim o mesmo código funciona rodando fora do Streamlit
    também (ex: script de teste)."""
    try:
        if chave in st.secrets:
            return st.secrets[chave]
    except Exception:
        pass
    return os.environ.get(chave, "")

st.set_page_config(page_title=PAGE_TITLE, page_icon=LOGO_PATH, layout="centered")
aplicar_estilo(st)
topbar(st)

hero(
    st,
    eyebrow="Sobe a nota, a gente acha a encomenda",
    titulo_html='Rastreie a entrega<br>sem sair <span class="accent">caçando link</span>',
    subtitulo=(
        "Sobe o PDF da nota fiscal e o sistema extrai o CPF/CNPJ e o número "
        "da NF automaticamente, identifica a transportadora e já traz o "
        "status da entrega."
    ),
)
hero_cta(st)

st.markdown('<div id="rastrear"></div>', unsafe_allow_html=True)
pdf = st.file_uploader("PDF da Nota Fiscal (DANFE)", type=["pdf"])

if pdf is not None:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf.read())
        caminho_tmp = tmp.name

    if "dados_extraidos" not in st.session_state or st.session_state.get("_arquivo") != pdf.name:
        with st.spinner("Lendo o PDF..."):
            st.session_state["dados_extraidos"] = processar_pdf(caminho_tmp)
            st.session_state["_arquivo"] = pdf.name

    dados = st.session_state["dados_extraidos"]

    st.subheader("Confirme os dados extraídos")
    st.caption("Revisa antes de rastrear - a extração pode errar dependendo do layout da nota.")

    cnpj_cpf = st.text_input(
        "CPF/CNPJ do destinatário (só números)",
        value=dados.get("cnpj_cpf_destinatario") or "",
    )
    numero_nf = st.text_input(
        "Número da NF-e",
        value=dados.get("numero_nf") or "",
    )

    opcoes = list(NOMES_TRANSPORTADORA.keys())
    detectada = dados.get("transportadora")
    index_padrao = opcoes.index(detectada) if detectada in opcoes else 0
    transportadora_id = st.selectbox(
        "Transportadora",
        options=opcoes,
        format_func=lambda k: NOMES_TRANSPORTADORA[k],
        index=index_padrao,
    )
    if detectada:
        st.caption(f"Detectado automaticamente pela nota: {NOMES_TRANSPORTADORA[detectada]}")

    if not dados.get("cnpj_cpf_destinatario") or not dados.get("numero_nf"):
        st.warning(
            "Não consegui achar todos os dados automaticamente nessa nota - "
            "confirma/completa os campos acima antes de rastrear."
        )

    # Validação de dígito verificador: pega erro grosseiro de extração antes
    # de fazer uma consulta que com certeza não acharia nada.
    if cnpj_cpf and not documento_valido(cnpj_cpf):
        st.warning(
            "O CPF/CNPJ acima não parece válido (dígito verificador não bate) "
            "- confere se a extração pegou o número certo antes de rastrear."
        )
    if numero_nf and not numero_nf_valido(numero_nf):
        st.warning("O número da NF-e acima não parece válido - confere antes de rastrear.")

    with st.expander("Texto extraído do PDF (pra depurar, se algo vier errado)"):
        st.text(dados.get("texto_bruto", ""))

    st.divider()

    if transportadora_id == "atual_cargas":
        if st.button("🔎 Rastrear na Atual Cargas", type="primary"):
            if not cnpj_cpf or not numero_nf:
                st.error("Preenche CPF/CNPJ e número da NF antes de rastrear.")
            else:
                with st.spinner("Consultando..."):
                    resultado = consultar_atual_cargas(cnpj_cpf, [numero_nf])
                mostrar_resultado_atual_cargas(st, resultado, numero_nf)

    elif transportadora_id == "rodonaves":
        username = _credencial_rodonaves("RODONAVES_API_USERNAME")
        password = _credencial_rodonaves("RODONAVES_API_PASSWORD")

        if not username or not password:
            st.warning(
                "Credenciais da API da Rodonaves não configuradas - caindo pro modo manual."
            )
            mostrar_portal_manual(
                st,
                {
                    "nome": "Rodonaves",
                    "url": "https://cliente.rte.com.br/Tracking/",
                    "instrucoes": (
                        "No portal, troque 'Consultar por' para 'Nota Fiscal', cole o "
                        "CPF/CNPJ e o número da NF-e nos campos e clique em Rastrear."
                    ),
                },
                cnpj_cpf,
                numero_nf,
            )
        elif st.button("🔎 Rastrear na Rodonaves", type="primary"):
            if not cnpj_cpf or not numero_nf:
                st.error("Preenche CPF/CNPJ e número da NF antes de rastrear.")
            else:
                with st.spinner("Consultando..."):
                    resultado = consultar_rodonaves(cnpj_cpf, numero_nf, username, password)
                mostrar_resultado_rodonaves(st, resultado)

    else:
        portal = get_portal(transportadora_id)
        mostrar_portal_manual(st, portal, cnpj_cpf, numero_nf)

partners_strip(st, list(NOMES_TRANSPORTADORA.values()))
