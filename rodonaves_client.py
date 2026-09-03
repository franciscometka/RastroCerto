"""
Cliente da API oficial de rastreio da Rodonaves.

Diferente da Atual Cargas (scraping de HTML do ssw.inf.br), a Rodonaves
libera uma API REST de verdade com autenticação OAuth (password grant) -
documentação pública em https://dev.rodonaves.com.br/reference/rastreio-1.

Fluxo: POST /token (usuário/senha do portal do desenvolvedor) -> Bearer
token -> GET /api/v1/tracking?TaxIdRegistration=...&InvoiceNumber=...

O token não é cacheado entre consultas (o app faz uma consulta de cada
vez, então o custo de autenticar de novo a cada clique é desprezível e
evita lidar com expiração de token guardado em sessão).
"""

import requests

from config import RODONAVES_AUTH_TYPE, RODONAVES_TOKEN_URL, RODONAVES_TRACKING_URL
from http_utils import criar_sessao


def _somente_digitos(s: str) -> str:
    import re
    return re.sub(r"\D", "", s or "")


def _autenticar(sessao: requests.Session, username: str, password: str) -> str:
    """Pede o token de acesso. Levanta requests.HTTPError se as credenciais
    estiverem erradas (401) ou requests.RequestException em erro de rede."""
    resp = sessao.post(
        RODONAVES_TOKEN_URL,
        data={
            "auth_type": RODONAVES_AUTH_TYPE,
            "grant_type": "password",
            "username": username,
            "password": password,
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def consultar_rodonaves(cnpj_cpf: str, numero_nf: str, username: str, password: str) -> dict:
    """Consulta o rastreio de uma NF na Rodonaves.

    Retorna dict com:
      - sucesso: bool (False em falha de rede/HTTP, incluindo credencial
        inválida ou nota não encontrada)
      - eventos: lista de dicts {"Data/Hora": ..., "Situação": ...} com o
        histórico completo, na ordem em que a API devolveu
      - info: dict com remetente, destinatário, número do protocolo/CT-e e
        previsão de entrega (em dias, a partir da emissão)
      - mensagem: aviso não-fatal (ex: NF sem eventos ainda)
      - erro: mensagem de erro, se houver
    """
    if not username or not password:
        return {
            "sucesso": False,
            "eventos": [],
            "info": {},
            "mensagem": None,
            "erro": "Credenciais da API da Rodonaves não configuradas (RODONAVES_API_USERNAME/PASSWORD).",
        }

    sessao = criar_sessao()

    try:
        token = _autenticar(sessao, username, password)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status in (400, 401):
            erro = "Usuário/senha da API da Rodonaves inválidos."
        else:
            erro = f"Erro ao autenticar na API da Rodonaves: {e}"
        return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": erro}
    except requests.RequestException as e:
        return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": str(e)}

    try:
        resp = sessao.get(
            RODONAVES_TRACKING_URL,
            params={
                "TaxIdRegistration": _somente_digitos(cnpj_cpf),
                "InvoiceNumber": numero_nf,
            },
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=20,
        )
    except requests.RequestException as e:
        return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": str(e)}

    # Nota não encontrada: a API responde 204 (sem corpo) ou 404, dependendo
    # do caso - tratamos os dois como "nada encontrado", não como erro.
    if resp.status_code in (204, 404) or not resp.text.strip():
        return {
            "sucesso": True,
            "eventos": [],
            "info": {},
            "mensagem": "Nenhuma informação encontrada pra esse CPF/CNPJ e número de NF.",
            "erro": None,
        }

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        return {"sucesso": False, "eventos": [], "info": {}, "mensagem": None, "erro": str(e)}

    dados = resp.json()
    return _formatar_resposta(dados)


def _formatar_resposta(dados: dict) -> dict:
    eventos = []
    for evento in dados.get("Events", []):
        eventos.append({
            "Data/Hora": _formatar_data(evento.get("Date", "")),
            "Situação": evento.get("Description", "").strip(),
        })

    info = {
        "remetente": dados.get("SenderDescription", ""),
        "destinatario": dados.get("RecipientDescription", ""),
        "protocolo": dados.get("ProtocolNumber", ""),
        "cte": dados.get("CTeNumber", ""),
        "previsao_dias": dados.get("ExpectedDeliveryDays"),
    }

    mensagem = None
    if not eventos:
        mensagem = "Nota encontrada, mas ainda sem eventos de rastreio registrados."

    return {"sucesso": True, "eventos": eventos, "info": info, "mensagem": mensagem, "erro": None}


def _formatar_data(iso: str) -> str:
    """'2026-08-26T08:22:08-03:00' -> '26/08/26 08:22' (mesmo formato usado
    pelo ssw_client, pra manter consistência visual entre transportadoras)."""
    if not iso or len(iso) < 16:
        return iso
    try:
        data, hora = iso[:10], iso[11:16]
        ano, mes, dia = data.split("-")
        return f"{dia}/{mes}/{ano[2:]} {hora}"
    except ValueError:
        return iso
