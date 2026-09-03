"""
Formatação dos resultados de rastreio na tela do Streamlit.

Separa a apresentação (o que aparece pro usuário) da lógica de consulta
(ssw_client, semi_auto). O app.py só decide qual transportadora e chama a
função certa daqui.
"""

from imagem_rastreio import gerar_imagem_historico


def mostrar_resultado_atual_cargas(st, resultado: dict, numero_nf: str) -> None:
    """Exibe o resultado da consulta automática à Atual Cargas.

    Ordem de prioridade:
    1. Falha de rede/HTTP -> erro
    2. Histórico completo -> imagem PNG + botão de download
    3. Só a tabela resumida -> tabela simples
    4. Mensagem do próprio SSW (CNPJ inválido, nada encontrado) -> aviso
    5. Nada reconhecido -> HTML bruto pra depuração
    """
    if not resultado["sucesso"]:
        st.error(f"Erro na consulta: {resultado['erro']}")
        return

    if resultado.get("historico"):
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
        return

    if resultado["eventos"]:
        st.success("Resultado encontrado:")
        st.table(resultado["eventos"])
        if resultado.get("mensagem"):
            st.caption(resultado["mensagem"])
        return

    if resultado.get("mensagem"):
        st.warning(resultado["mensagem"])
        return

    st.warning(
        "Não consegui estruturar uma tabela de eventos automaticamente. "
        "Vê a resposta bruta abaixo - se aparecer errado, me manda esse "
        "HTML que eu ajusto o parser."
    )
    with st.expander("Resposta bruta do site (debug)"):
        st.code(resultado["html_bruto"], language="html")


def mostrar_resultado_rodonaves(st, resultado: dict) -> None:
    """Exibe o resultado da consulta automática à Rodonaves (API oficial).

    Ordem de prioridade:
    1. Falha de rede/HTTP/credencial -> erro
    2. Eventos -> tabela + info de destinatário/protocolo/previsão de entrega
    3. Mensagem sem eventos (nota sem histórico ainda) -> aviso
    """
    if not resultado["sucesso"]:
        st.error(f"Erro na consulta: {resultado['erro']}")
        return

    info = resultado.get("info", {})
    if info.get("destinatario") or info.get("protocolo"):
        partes = []
        if info.get("destinatario"):
            partes.append(f"**Destinatário:** {info['destinatario']}")
        if info.get("protocolo"):
            partes.append(f"**Protocolo:** {info['protocolo']}")
        if info.get("previsao_dias") is not None:
            partes.append(f"**Previsão de entrega:** {info['previsao_dias']} dias após a emissão")
        st.markdown(" &nbsp;·&nbsp; ".join(partes))

    if resultado["eventos"]:
        st.success("Rastreamento encontrado:")
        st.table(resultado["eventos"])
        return

    if resultado.get("mensagem"):
        st.warning(resultado["mensagem"])
        return

    st.warning("Não consegui achar informações de rastreio pra essa nota.")


def mostrar_portal_manual(st, portal: dict, cnpj_cpf: str, numero_nf: str) -> None:
    """Exibe o modo semi-automático (transportadoras com captcha): mostra os
    dados prontos pra copiar e um botão que abre o portal certo."""
    st.info(
        f"**{portal['nome']}** tem captcha no site, então essa parte é manual "
        f"(1 clique): copia os dados abaixo e cola no portal."
    )
    st.text_input("CPF/CNPJ (copiar)", value=cnpj_cpf, key="copia_cnpj")
    st.text_input("Número da NF-e (copiar)", value=numero_nf, key="copia_nf")
    st.caption(portal["instrucoes"])
    st.link_button(f"Abrir portal da {portal['nome']} ↗", portal["url"])
