import html
import tempfile

import streamlit as st

from extractor import processar_pdf, TRANSPORTADORAS_CONHECIDAS
from ssw_client import consultar_atual_cargas
from semi_auto import get_portal


def render_historico(historico: list[dict]) -> str:
    """Monta uma tabela HTML parecida com a do 'Rastreamento detalhado' do
    site da Atual Cargas (título da situação em destaque, linhas
    alternadas), em vez do st.table genérico do Streamlit.

    Importante: o HTML não pode ter indentação nas linhas quando passado
    pro st.markdown - 4+ espaços no início da linha fazem o Markdown
    interpretar como bloco de código e mostrar as tags cruas em vez de
    renderizar."""
    td_style = "padding:8px 10px;border:1px solid #444;vertical-align:top;"
    linhas_html = []
    for i, evento in enumerate(historico):
        cor_fundo = "#ffffff" if i % 2 == 0 else "#f4f4f4"
        data_hora = html.escape(evento.get("Data/Hora", ""))
        unidade = html.escape(evento.get("Unidade", ""))
        situacao = html.escape(evento.get("Situação", ""))
        detalhe = html.escape(evento.get("Detalhe", ""))
        linhas_html.append(
            f'<tr style="background-color:{cor_fundo};">'
            f'<td style="{td_style}white-space:nowrap;">{data_hora}</td>'
            f'<td style="{td_style}white-space:nowrap;">{unidade}</td>'
            f'<td style="{td_style}">'
            f'<b style="color:#e63946;">{situacao}</b><br>'
            f'<span style="color:#bbb;font-size:0.9em;">{detalhe}</span>'
            f"</td></tr>"
        )

    th_style = "padding:8px 10px;border:1px solid #444;text-align:left;"
    linhas = "".join(linhas_html)
    return (
        '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">'
        f'<tr style="background-color:#2b2b2b;color:#fff;">'
        f'<th style="{th_style}">Data/Hora</th>'
        f'<th style="{th_style}">Unidade</th>'
        f'<th style="{th_style}">Situação</th>'
        f"</tr>{linhas}</table>"
    )

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
                    st.markdown(render_historico(resultado["historico"]), unsafe_allow_html=True)
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
