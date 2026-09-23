"""
Portais manuais de rastreio, pra transportadoras sem automação disponível.

Hoje as 3 transportadoras usadas pela Sebem (Atual Cargas, Rodonaves,
Expresso São Miguel) têm API/scraping automático - ver ssw_client.py,
rodonaves_client.py e sao_miguel_client.py. Esse dicionário fica vazio
por enquanto, mas o mecanismo continua existindo: se uma credencial de
API não estiver configurada (ou uma transportadora nova sem automação
aparecer), o app cai pro modo manual (link do portal + dados prontos pra
copiar) em vez de quebrar.
"""

PORTAIS = {}


def get_portal(transportadora_id: str) -> dict | None:
    return PORTAIS.get(transportadora_id)
