import os
import tempfile

import streamlit as st

from estilo import aplicar_estilo, hero, hero_cta, partners_strip, topbar, trail_visual
from extractor import processar_pdf, TRANSPORTADORAS_CONHECIDAS
from imagem_rastreio import gerar_imagem_historico
from ssw_client import consultar_atual_cargas
from semi_auto import get_portal

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

st.set_page_config(page_title="Rastreio Automático - Sebem", page_icon=LOGO, layout="centered")
aplicar_estilo(st)
topbar(st)

NOMES_TRANSPORTADORA = {
    "atual_cargas": "Atual Cargas",
    "rodonaves": "Rodonaves",
    "expresso_sao_miguel": "Expresso São Miguel",
}

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
trail_visual(st)
partners_strip(st, list(NOMES_TRANSPORTADORA.values()))

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

                if not resultado["sucesso"]:
                    st.error(f"Erro na consulta: {resultado['erro']}")
                elif resultado.get("historico"):
                    st.success("Rastreamento encontrado:")
                    info = resultado.get("info", {})
                    imagem_png = gerar_imagem_historico(
                        resultado["historico"],
                        destinatario=info.get("destinatario", ""),
                        n_fiscal=info.get("n_fiscal", ""),
                        n_pedido=info.get("n_pedido", ""),
                        previsao_entrega=info.get("previsao_entrega", ""),
                    )
                    st.image(imagem_png)
                    st.download_button(
                        "📥 Baixar imagem do rastreio",
                        data=imagem_png,
                        file_name=f"rastreio_{numero_nf}.png",
                        mime="image/png",
                    )
                elif resultado["eventos"]:
                    st.success("Resultado encontrado:")
                    st.table(resultado["eventos"])
                    if resultado.get("mensagem"):
                        st.caption(resultado["mensagem"])
                elif resultado.get("mensagem"):
                    st.warning(resultado["mensagem"])
                else:
                    st.warning(
                        "Não consegui estruturar uma tabela de eventos automaticamente. "
                        "Vê a resposta bruta abaixo - se aparecer errado, me manda esse "
                        "HTML que eu ajusto o parser."
                    )
                    with st.expander("Resposta bruta do site (debug)"):
                        st.code(resultado["html_bruto"], language="html")

    else:
        portal = get_portal(transportadora_id)
        st.info(
            f"**{portal['nome']}** tem captcha no site, então essa parte é manual "
            f"(1 clique): copia os dados abaixo e cola no portal."
        )
        st.text_input("CPF/CNPJ (copiar)", value=cnpj_cpf, key="copia_cnpj")
        st.text_input("Número da NF-e (copiar)", value=numero_nf, key="copia_nf")
        st.caption(portal["instrucoes"])
        st.link_button(f"Abrir portal da {portal['nome']} ↗", portal["url"])
