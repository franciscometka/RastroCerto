"""
Automação da consulta de rastreio na Atual Cargas (sistema SSW - ssw.inf.br).

Essa é a única das 3 transportadoras sem captcha, então é a única que
conseguimos consultar de ponta a ponta sem intervenção manual.

IMPORTANTE sobre a URL: o formulário "Rastreamento pelo destinatário" tem
duas variantes que parecem idênticas na tela mas submetem pra ações
diferentes (confirmado lendo o JS do próprio site,
https://ssw.inf.br/scripts/rastreamento4.js):

- "Pelo destinatário - 30 dias" -> action "/2/resultSSW_dest" (só shipments
  dos últimos 30 dias; na prática voltou "nenhuma informação encontrada"
  pra notas reais e válidas nos testes).
- "Pelo destinatário" (sem limite de dias) -> action
  "/2/resultSSW_dest_nro" (a que funciona - foi essa que achou o resultado
  real testado).

Por isso o cliente usa resultSSW_dest_nro. Se o site mudar de novo, o jeito
de confirmar é abrir https://ssw.inf.br/2/rastreamento_dest?pwd=2 num
navegador de verdade, testar uma nota válida e ver pra qual action o
formulário está de fato submetendo.

Parser validado contra respostas reais do site: CNPJ inválido, CNPJ válido
sem resultado, e CNPJ válido com um evento de rastreio real. A tabela de
resultado tem cabeçalho com células de classe "tdresult"; quando não acha
nada, mostra uma linha com colspan e um <p class="titulo"> com a mensagem.
Quando acha, cada linha de evento pode *também* ter um <p class="titulo">
dentro da célula de situação (usado só pra destacar o texto em negrito,
não é aviso de "não encontrado") - por isso o parser não pode simplesmente
pular qualquer linha que contenha essa classe, tem que olhar a forma da
linha (1 <td> com colspan = aviso; 3 <td> = evento real).

A tabela de resumo (resultSSW_dest_nro) só traz a última situação de cada
NF. Pra pegar o histórico completo (todas as unidades por onde passou),
tem um link "Mais detalhes" na resposta que aponta pra
/2/SSWDetalhado?id=...&md=... - esse link é seguido automaticamente
(_extrair_link_detalhe + _parsear_detalhe) pra montar o "historico".
"""

import re
import requests
from bs4 import BeautifulSoup

SSW_BASE = "https://ssw.inf.br"
SSW_URL = f"{SSW_BASE}/2/resultSSW_dest_nro"


def _somente_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def consultar_atual_cargas(cnpj_cpf: str, numeros_nf: list[str], senha: str = "") -> dict:
    """Consulta o rastreio de uma ou mais NFs na Atual Cargas.

    Retorna dict com:
      - sucesso: bool (False só em caso de falha de rede/HTTP)
      - eventos: lista de dicts com a última situação de cada NF (tabela
        resumida devolvida na primeira consulta)
      - historico: lista de dicts com o histórico completo (todas as
        unidades/eventos), seguindo o link "Mais detalhes" da primeira NF -
        vazio se não achou o link ou a página de detalhe não bateu com o
        formato esperado
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
        return {
            "sucesso": False,
            "eventos": [],
            "historico": [],
            "info": {},
            "mensagem": None,
            "html_bruto": "",
            "erro": str(e),
        }

    eventos, mensagem = _parsear_resultado(resp.text)

    historico = []
    info = {}
    link_detalhe = _extrair_link_detalhe(resp.text)
    if link_detalhe:
        try:
            resp_detalhe = requests.get(link_detalhe, headers=headers, timeout=20)
            resp_detalhe.raise_for_status()
            historico = _parsear_detalhe(resp_detalhe.text)
            info = _extrair_info_cabecalho(resp_detalhe.text)
        except requests.RequestException:
            pass  # sem histórico detalhado, mas a consulta resumida já funcionou

    return {
        "sucesso": True,
        "eventos": eventos,
        "historico": historico,
        "info": info,
        "mensagem": mensagem,
        "html_bruto": resp.text,
        "erro": None,
    }


def _extrair_info_cabecalho(html: str) -> dict:
    """Extrai os dados do cabeçalho da página de detalhe: destinatário,
    previsão de entrega, N Fiscal e N Pedido."""
    info = {}
    padroes = {
        "destinatario": r'Destinat[aá]rio:</span>\s*<span[^>]*>([^<]*)</span>',
        "previsao_entrega": r'Previs[aã]o de entrega:<span[^>]*>([^<]*)</span>',
        "n_fiscal": r'N Fiscal:</span>\s*<span[^>]*>([^<]*)</span>',
        "n_pedido": r'N Pedido:</span>\s*<span[^>]*>([^<]*)</span>',
    }
    for chave, padrao in padroes.items():
        m = re.search(padrao, html)
        if m:
            info[chave] = _limpar_celula(m.group(1))
    return info


def _extrair_link_detalhe(html: str) -> str | None:
    """Acha o link 'Mais detalhes' (opx('/2/SSWDetalhado?id=...&md=...'))
    na resposta resumida e monta a URL completa. Se tiver mais de uma NF
    na consulta, pega o primeiro link encontrado."""
    m = re.search(r"opx\('(/2/(?:ssw_)?SSWDetalhado\?[^']+)'\)", html)
    if not m:
        return None
    return SSW_BASE + m.group(1)


def _parsear_detalhe(html: str) -> list[dict]:
    """Extrai o histórico completo de eventos da página de detalhe
    (/2/SSWDetalhado). Cada linha real tem 3 <td class="rastreamento">
    (Data/Hora, Unidade, Situação) - as linhas espaçadoras entre eventos
    não têm essa classe, então dá pra filtrar direto por ela."""
    soup = BeautifulSoup(html, "html.parser")

    tabela = None
    for t in soup.find_all("table"):
        if t.find(class_="tdresult"):
            tabela = t
            break
    if tabela is None:
        return []

    eventos = []
    for linha in tabela.find_all("tr"):
        celulas = linha.find_all("td", class_="rastreamento")
        if len(celulas) != 3:
            continue

        data_hora = _limpar_celula(celulas[0].get_text(separator=" ", strip=True))
        unidade = _limpar_celula(celulas[1].get_text(separator=" ", strip=True))

        titulo_el = celulas[2].find("p", class_="titulo")
        situacao = _limpar_celula(titulo_el.get_text(strip=True)) if titulo_el else ""
        detalhe_el = celulas[2].find("p", class_="tdb")
        detalhe = _limpar_celula(detalhe_el.get_text(strip=True)) if detalhe_el else ""

        if not any([data_hora, unidade, situacao, detalhe]):
            continue

        eventos.append({
            "Data/Hora": data_hora,
            "Unidade": unidade,
            "Situação": situacao,
            "Detalhe": detalhe,
        })

    return eventos


def _limpar_celula(texto: str) -> str:
    texto = texto.replace("\xa0", " ")
    texto = re.sub(r"\s*\n\s*", " ", texto)
    return texto.strip()


def _parsear_resultado(html: str) -> tuple[list[dict], str | None]:
    """Extrai a tabela de eventos de rastreio do HTML de resposta do SSW.

    Retorna (eventos, mensagem):
    - eventos: lista de dicts com uma entrada por linha de resultado real
    - mensagem: texto de um <p class="titulo"> "solto" (fora da tabela de
      eventos, tipo erro de CNPJ inválido) ou da linha de aviso dentro da
      tabela ("nenhuma informação encontrada"); None se não achou nenhum
    """
    soup = BeautifulSoup(html, "html.parser")

    tabela_resultado = None
    for tabela in soup.find_all("table"):
        if tabela.find(class_="tdresult"):
            tabela_resultado = tabela
            break

    eventos = []
    mensagem_tabela = None

    if tabela_resultado is not None:
        linhas = tabela_resultado.find_all("tr")
        cabecalho_cels = linhas[0].find_all(["td", "th"], class_="tdresult") if linhas else []
        cabecalho = [c.get_text(separator=" ", strip=True) for c in cabecalho_cels]

        for linha in linhas[1:]:
            celulas = linha.find_all("td")
            if not celulas:
                continue

            # linha de aviso: 1 único <td colspan=...> com a mensagem
            if len(celulas) == 1 and celulas[0].has_attr("colspan"):
                aviso = celulas[0].find("p", class_="titulo")
                if aviso:
                    mensagem_tabela = aviso.get_text(strip=True)
                continue

            valores = [_limpar_celula(c.get_text(separator=" | ", strip=True)) for c in celulas]
            if not any(valores):
                continue  # linha espaçadora vazia

            if cabecalho and len(cabecalho) == len(valores):
                eventos.append(dict(zip(cabecalho, valores)))
            else:
                eventos.append({"dados": valores})

    # mensagem "solta" fora da tabela (ex: CNPJ inválido) - só considera se
    # não achamos nada melhor ainda
    mensagem = mensagem_tabela
    if mensagem is None and not eventos:
        aviso_solto = soup.find("p", class_="titulo")
        if aviso_solto:
            mensagem = aviso_solto.get_text(strip=True)

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
