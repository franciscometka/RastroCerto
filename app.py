import tempfile

import streamlit as st

from extractor import processar_pdf, TRANSPORTADORAS_CONHECIDAS
from semi_auto import get_portal

st.set_page_config(page_title="Rastreio Automático - Sebem", page_icon="📦", layout="centered")

NOMES_TRANSPORTADORA = {
    "atual_cargas": "Atual Cargas",
    "rodonaves": "Rodonaves",
    "expresso_sao_miguel": "Expresso São Miguel",
}

st.title("📦 Rastreio Automático de Notas")
st.caption("Sobe o PDF da nota, confirma os dados e rastreia na transportadora.")

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

    with st.expander("Texto extraído do PDF (pra depurar, se algo vier errado)"):
        st.text(dados.get("texto_bruto", ""))

    st.divider()

    portal = get_portal(transportadora_id)
    st.info(
        f"Rastreio da **{portal['nome']}** é manual (1 clique): copia os "
        f"dados abaixo e cola no portal."
    )
    st.text_input("CPF/CNPJ (copiar)", value=cnpj_cpf, key="copia_cnpj")
    st.text_input("Número da NF-e (copiar)", value=numero_nf, key="copia_nf")
    st.caption(portal["instrucoes"])
    st.link_button(f"Abrir portal da {portal['nome']} ↗", portal["url"])
