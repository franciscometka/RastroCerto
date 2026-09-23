"""
Sessão HTTP compartilhada com retry automático.

O ssw.inf.br às vezes devolve 5xx transitório ou fecha a conexão no meio -
uma sessão com retry (backoff exponencial) evita que uma falha momentânea
de rede vire um "erro na consulta" pro usuário. Centralizar aqui também
garante que todo request do app sai com o mesmo User-Agent e timeout.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import HTTP_BACKOFF_FACTOR, HTTP_RETRIES, HTTP_TIMEOUT, USER_AGENT

_STATUS_RETRY = (429, 500, 502, 503, 504)


def _montar_retry() -> Retry:
    # allowed_methods é o nome atual (urllib3 >= 1.26); versões antigas usavam
    # method_whitelist. Como GET e POST aqui são consultas idempotentes de
    # rastreio, dá pra permitir retry nos dois com segurança.
    #
    # total=5 cobre também falhas de conexão (DNS, timeout de conexão), não
    # só os status HTTP em status_forcelist - é o que salva a consulta
    # quando o problema é tipo "NameResolutionError" transitório do lado do
    # Streamlit Cloud, não um erro de verdade da API.
    try:
        return Retry(
            total=HTTP_RETRIES,
            backoff_factor=HTTP_BACKOFF_FACTOR,
            status_forcelist=_STATUS_RETRY,
            allowed_methods=frozenset(["GET", "POST"]),
        )
    except TypeError:  # urllib3 antigo
        return Retry(
            total=HTTP_RETRIES,
            backoff_factor=HTTP_BACKOFF_FACTOR,
            status_forcelist=_STATUS_RETRY,
            method_whitelist=frozenset(["GET", "POST"]),
        )


def criar_sessao() -> requests.Session:
    """Cria uma requests.Session com retry montado nos dois protocolos e o
    User-Agent padrão já aplicado."""
    sessao = requests.Session()
    adapter = HTTPAdapter(max_retries=_montar_retry())
    sessao.mount("https://", adapter)
    sessao.mount("http://", adapter)
    sessao.headers.update({"User-Agent": USER_AGENT})
    return sessao


def post(url: str, **kwargs) -> requests.Response:
    """POST com a sessão de retry e timeout padrão (sobrescrevível)."""
    kwargs.setdefault("timeout", HTTP_TIMEOUT)
    return criar_sessao().post(url, **kwargs)


def get(url: str, **kwargs) -> requests.Response:
    """GET com a sessão de retry e timeout padrão (sobrescrevível)."""
    kwargs.setdefault("timeout", HTTP_TIMEOUT)
    return criar_sessao().get(url, **kwargs)
