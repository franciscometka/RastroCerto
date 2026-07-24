"""
Automação da consulta de rastreio na Atual Cargas (sistema SSW - ssw.inf.br).

Essa é a única das 3 transportadoras sem captcha, então é a única que
conseguimos consultar de ponta a ponta sem intervenção manual.

Baseado no formulário real de https://ssw.inf.br/2/rastreamento_dest?pwd=2:

    <form name="Form1" action="/2/resultSSW_dest" method="POST">
        <input name="cnpjdest">      -> CNPJ/CPF do destinatário, só números
        <textarea name="NR">         -> números de NF, um por linha (até 100)
        <input name="chave">         -> senha da transportadora (opcional)
    </form>

Parser validado contra respostas reais do site (testado com CNPJ inválido e
com CNPJ válido sem resultado - ainda não testado com um caso que retorne
eventos de fato, porque não tínhamos uma NF real com dado positivo à mão).
A tabela de resultado tem cabeçalho com células de classe "tdresult" e,
quando não acha nada, mostra uma linha única com colspan e um
<p class="titulo"> com a mensagem (mesmo padrão usado pra erro de CNPJ
inválido, só que esse aparece fora de tabela). Se o formato mudar ou vier
um caso com eventos reais e o parser não bater, olha o "html_bruto" no
retorno e ajusta as classes/seletores usados abaixo.
"""

import re
import requests
from bs4 import BeautifulSoup

SSW_URL = "https://ssw.inf.br/2/resultSSW_dest"


def _somente_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def consultar_atual_cargas(cnpj_cpf: str, numeros_nf: list[str], senha: str = "") -> dict:
    """Consulta o rastreio de uma ou mais NFs na Atual Cargas.

    Retorna dict com:
      - sucesso: bool (False só em caso de falha de rede/HTTP)
      - eventos: lista de dicts (quando conseguir estruturar a tabela)
      - mensagem: texto informativo do próprio SSW (ex: "CNPJ inválido",
        "nenhuma informação encontrada") - não é um erro nosso, é resposta
        do site
      - html_bruto: resposta completa, pra depuração se o parser não achar nada
      - erro: mensagem de erro nosso (rede/HTTP), se houver
    """
    payload = {
        "cnpjdest": _somente_digitos(cnpj_cpf),
        "NR": "\n".join(numeros_nf),
        "chave": senha or "",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Sebem-Rastreio/1.0)",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        resp = requests.post(SSW_URL, data=payload, headers=headers, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"sucesso": False, "eventos": [], "mensagem": None, "html_bruto": "", "erro": str(e)}

    eventos, mensagem = _parsear_resultado(resp.text)
    return {
        "sucesso": True,
        "eventos": eventos,
        "mensagem": mensagem,
        "html_bruto": resp.text,
        "erro": None,
    }


def _parsear_resultado(html: str) -> tuple[list[dict], str | None]:
    """Extrai a tabela de eventos de rastreio do HTML de resposta do SSW.

    Retorna (eventos, mensagem):
    - eventos: lista de dicts com uma entrada por linha de resultado real
    - mensagem: texto de um <p class="titulo"> encontrado (erro de CNPJ
      inválido, "nenhuma informação encontrada", etc.) ou None se não achou
      nenhum aviso desse tipo
    """
    soup = BeautifulSoup(html, "html.parser")

    mensagem = None
    aviso = soup.find("p", class_="titulo")
    if aviso:
        mensagem = aviso.get_text(strip=True)

    eventos = []
    tabela_resultado = None
    for tabela in soup.find_all("table"):
        if tabela.find(class_="tdresult"):
            tabela_resultado = tabela
            break

    if tabela_resultado is not None:
        linhas = tabela_resultado.find_all("tr")
        cabecalho_cels = linhas[0].find_all(["td", "th"], class_="tdresult") if linhas else []
        cabecalho = [c.get_text(separator=" ", strip=True) for c in cabecalho_cels]

        for linha in linhas[1:]:
            # linha de aviso (colspan) já foi capturada como "mensagem" acima
            if linha.find("p", class_="titulo"):
                continue
            celulas = linha.find_all("td")
            if not celulas:
                continue
            valores = [c.get_text(separator=" | ", strip=True) for c in celulas]
            if not any(valores):
                continue
            if cabecalho and len(cabecalho) == len(valores):
                eventos.append(dict(zip(cabecalho, valores)))
            else:
                eventos.append({"dados": valores})

    if not eventos and not mensagem:
        # fallback genérico: se o site mudou e não bateu com o padrão
        # conhecido, tenta achar qualquer tabela com mais de 1 linha
        for tabela in soup.find_all("table"):
            linhas = tabela.find_all("tr")
            if len(linhas) < 2:
                continue
            cabecalho = [td.get_text(strip=True) for td in linhas[0].find_all(["td", "th"])]
            candidatos = []
            for linha in linhas[1:]:
                celulas = [td.get_text(strip=True) for td in linha.find_all("td")]
                if not any(celulas):
                    continue
                if cabecalho and len(cabecalho) == len(celulas):
                    candidatos.append(dict(zip(cabecalho, celulas)))
                else:
                    candidatos.append({"dados": celulas})
            if candidatos:
                eventos = candidatos
                break

    return eventos, mensagem
