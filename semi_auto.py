"""
Expresso São Miguel tem captcha/reCAPTCHA no formulário de rastreio, então
não é automatizada de ponta a ponta - isso seria bypass de proteção
anti-bot. (Atual Cargas e Rodonaves não entram aqui: são consultadas
automaticamente via ssw_client.py e rodonaves_client.py.)

O que este módulo faz: guarda o link direto do portal, pra a tela mostrar
os dados já extraídos (CNPJ/CPF + número da NF) prontos pra copiar, com um
botão que abre o portal em outra aba. Usuário só cola os dados, resolve o
captcha e clica em rastrear - 1 clique manual em vez de digitar tudo do
zero.
"""

PORTAIS = {
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
