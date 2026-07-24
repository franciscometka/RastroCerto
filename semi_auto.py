"""
As 3 transportadoras (Atual Cargas, Rodonaves, Expresso São Miguel) são
rastreadas de forma semi-automática, não de ponta a ponta - isso seria
bypass de proteção anti-bot.

- Rodonaves e Expresso São Miguel: têm reCAPTCHA visível no formulário.
- Atual Cargas: não tem captcha visível, mas o site novo deles
  (cliente.atualcargas.com.br) roda numa SPA cuja API de rastreio
  (/api/rastreio/deslogado) rejeita requisições feitas fora da navegação
  real da página com "token inválido" - indício de alguma proteção
  anti-bot própria deles. Não investigamos mais fundo pra não correr o
  risco de estar contornando esse mecanismo.

O que este módulo faz: guarda o link direto do portal de cada uma, pra a
tela mostrar os dados já extraídos (CNPJ/CPF + número da NF) prontos pra
copiar, com um botão que abre o portal certo em outra aba. Usuário só cola
os dados e clica em rastrear (resolvendo o captcha quando houver) - 1 clique
manual em vez de digitar tudo do zero.
"""

PORTAIS = {
    "atual_cargas": {
        "nome": "Atual Cargas",
        "url": "https://cliente.atualcargas.com.br/rastreamento?tipo=destinatario",
        "instrucoes": (
            "No portal, cole o CPF/CNPJ e o número da NF-e nos campos e "
            "clique em 'Buscar Encomendas'."
        ),
    },
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
