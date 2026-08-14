"""
Validação de CPF/CNPJ (dígito verificador) e de número de NF.

A extração do PDF (extractor.py) é heurística e pode pegar um documento
errado dependendo do layout da nota. Estas funções servem pra o app avisar
o usuário *antes* de rastrear quando o CPF/CNPJ extraído não fecha no dígito
verificador - assim dá pra corrigir na hora em vez de fazer uma consulta que
com certeza não vai achar nada.
"""

import re


def _digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf: str) -> bool:
    """True se o CPF (11 dígitos) tem dígitos verificadores válidos."""
    cpf = _digitos(cpf)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:  # rejeita 000..., 111..., etc.
        return False

    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        digito = 0 if resto == 10 else resto
        if digito != int(cpf[tamanho]):
            return False
    return True


def validar_cnpj(cnpj: str) -> bool:
    """True se o CNPJ (14 dígitos) tem dígitos verificadores válidos."""
    cnpj = _digitos(cnpj)
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_segundo = [6] + pesos_primeiro

    for pesos in (pesos_primeiro, pesos_segundo):
        base = cnpj[: len(pesos)]
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(cnpj[len(pesos)]):
            return False
    return True


def documento_valido(doc: str) -> bool:
    """Valida CPF ou CNPJ automaticamente pelo comprimento. Retorna False
    pra comprimentos que não são nem CPF (11) nem CNPJ (14)."""
    doc = _digitos(doc)
    if len(doc) == 11:
        return validar_cpf(doc)
    if len(doc) == 14:
        return validar_cnpj(doc)
    return False


def numero_nf_valido(numero: str) -> bool:
    """Sanidade básica do número da NF: só dígitos, 1 a 9 posições, e não
    pode ser tudo zero. Não dá pra validar de verdade sem consultar a
    transportadora - isso só pega erro grosseiro de extração."""
    numero = _digitos(numero)
    if not (1 <= len(numero) <= 9):
        return False
    return numero != "0" * len(numero)
