"""
Rodonaves e Expresso São Miguel têm captcha/reCAPTCHA nos formulários de
rastreio, então não são automatizadas de ponta a ponta - isso seria bypass
de proteção anti-bot. (Atual Cargas não entra aqui: é consultada
automaticamente via ssw_client.py.)

O que este módulo faz: guarda o link direto do portal de cada uma, pra a
tela mostrar os dados já extraídos (CNPJ/CPF + número da NF) prontos pra
copiar, com um botão que abre o portal certo em outra aba. Usuário só cola
os dados, resolve o captcha e clica em rastrear - 1 clique manual em vez de
digitar tudo do zero.
"""

PORTAIS = {
    "rodonaves": {
        "nome": "Rodonaves",
        "url": "https://cliente.rte.com.br/Tracking/",
        "instrucoes": (
            "No portal, troque 'Consultar por' para 'Nota Fiscal', cole o "
            "CPF/CNPJ e o número da NF-e nos campos, resolva o reCAPTCHA e "
            "clique em Rastrear."
        ),
    },
    "expresso_sao_miguel": {
        "nome": "Expresso São Miguel",
        "url": "https://portaldocliente.expressosaomiguel.com.br/rastrear-mercadoria",
        "instrucoes": (
            "No portal, selecione o tipo 'NF-e', cole a chave/número da NF-e "
            "e o CPF/CNPJ, digite a chave de segurança que aparecer na tela "
            "e clique em Consultar."
        ),
    },
}


def get_portal(transportadora_id: str) -> dict | None:
    return PORTAIS.get(transportadora_id)
