"""
Cliente da API oficial de rastreio da Expresso São Miguel.

Diferente da Rodonaves (autenticação OAuth com endpoint de token
separado), aqui a autenticação é só nos headers da própria consulta:
Access_Key + Customer (CNPJ da empresa dona da chave). Documentação
recebida por e-mail ("Manual Técnico - Integração Clientes", 2026) -
sem portal público, então se o formato mudar não tem onde ir conferir,
só pedir a documentação atualizada de novo.

A Sebem tem 3 CNPJs diferentes que despacham por essa transportadora,
cada um com seu próprio par Customer/Access_Key - como não sabemos de
antemão qual CNPJ emitiu a nota sendo consultada (extractor.py só pega o
destinatário), o cliente tenta os 3 pares em sequência até um funcionar.
"""

import re

import requests

from config import SAO_MIGUEL_MODELO_CONSULTA, SAO_MIGUEL_TRACKING_URL
from http_utils import criar_sessao


def _somente_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def _formatar_data(iso: str) -> str:
    """'2026-05-10T13:45:00-03:00' -> '10/05/26 13:45' (mesmo formato usado
    pelo rodonaves_client, pra manter consistência visual entre transportadoras)."""
    if not iso or len(iso) < 16:
        return iso or ""
    try:
        data, hora = iso[:10], iso[11:16]
        ano, mes, dia = data.split("-")
        return f"{dia}/{mes}/{ano[2:]} {hora}"
    except ValueError:
        return iso


def consultar_sao_miguel(cnpj_cpf: str, numero_nf: str, credenciais: list[tuple[str, str]]) -> dict:
    """Consulta o rastreio de uma NF na Expresso São Miguel.

    `credenciais`: lista de (customer, access_key) - tenta cada par em
    sequência (cobre os múltiplos CNPJs da Sebem que despacham por essa
    transportadora) até um devolver dado real ou até esgotar as opções.

    Retorna dict com sucesso/eventos/info/mensagem/erro, mesmo formato dos
    outros clientes (ssw_client, rodonaves_client).
    """
    if not credenciais:
        return {
            "sucesso": False,
            "eventos": [],
            "info": {},
            "mensagem": None,
            "erro": "Credenciais da API da Expresso São Miguel não configuradas.",
        }

    numero_digitos = _somente_digitos(numero_nf)
    if not numero_digitos:
        return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": "Número da NF inválido."}

    payload = {"valoresParametros": [_somente_digitos(cnpj_cpf), int(numero_digitos), None]}
    sessao = criar_sessao()

    ultimo_erro = None
    for customer, access_key in credenciais:
        headers = {
            "Content-Type": "application/json",
            "Access_Key": access_key,
            "Customer": customer,
            "Modelo_Consulta": SAO_MIGUEL_MODELO_CONSULTA,
        }
        try:
            resp = sessao.post(SAO_MIGUEL_TRACKING_URL, json=payload, headers=headers, timeout=20)
        except requests.RequestException as e:
            ultimo_erro = str(e)
            continue

        # 401 = chave errada pra esse par específico (ou limite de taxa) -
        # tenta o próximo par de credenciais antes de desistir.
        if resp.status_code == 401:
            ultimo_erro = "Chave de acesso inválida (ou limite de requisições excedido)."
            continue

        if resp.status_code == 404:
            return {
                "sucesso": True,
                "eventos": [],
                "info": {},
                "mensagem": "Nenhuma informação encontrada pra esse CPF/CNPJ e número de NF.",
                "erro": None,
            }

        # A doc diz que erro de validação vem como 401, mas na prática (
        # testado com CPF/CNPJ mal formado) veio 400 com um corpo JSON tipo
        # {"message": "Documento inválido: 11111111111"} - isso é problema
        # do dado enviado, não da credencial, então não faz sentido tentar
        # os outros pares (ia repetir o mesmo erro 3x); retorna direto com
        # a mensagem da própria API.
        if resp.status_code == 400:
            try:
                mensagem_api = resp.json().get("message")
            except ValueError:
                mensagem_api = None
            return {
                "sucesso": False,
                "eventos": [],
                "info": {},
                "mensagem": None,
                "erro": mensagem_api or "Requisição inválida (400) na API da Expresso São Miguel.",
            }

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            ultimo_erro = str(e)
            continue

        dados = resp.json()
        if not dados:
            return {
                "sucesso": True,
                "eventos": [],
                "info": {},
                "mensagem": "Nenhuma informação encontrada pra esse CPF/CNPJ e número de NF.",
                "erro": None,
            }

        return _formatar_resposta(dados[0])

    return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": ultimo_erro or "Erro desconhecido."}


def _formatar_resposta(item: dict) -> dict:
    eventos = []
    for ocorrencia in item.get("ocorrencias", []):
        eventos.append({
            "Data/Hora": _formatar_data(ocorrencia.get("dataRegistro", "")),
            "Situação": (ocorrencia.get("descricaoOcorrencia") or "").strip(),
        })

    unidade_destino = item.get("unidadeDestino") or {}
    info = {
        "numero_documento": item.get("numero", ""),
        "unidade_destino": unidade_destino.get("nome", ""),
        "previsao_entrega": _formatar_data(item.get("prevEntrega", "")),
    }

    mensagem = None
    if not eventos:
        mensagem = "Nota encontrada, mas ainda sem eventos de rastreio registrados."

    return {"sucesso": True, "eventos": eventos, "info": info, "mensagem": mensagem, "erro": None}
