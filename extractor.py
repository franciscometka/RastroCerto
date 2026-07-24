"""
Extração de dados de PDFs de Nota Fiscal (DANFE) para o rastreador automático.

Extrai:
- Número da NF-e
- CPF/CNPJ do destinatário
- Nome da transportadora (quando aparece na nota)

A extração é feita por padrões de texto comuns em DANFEs. Como o layout varia
um pouco entre emissores, os campos extraídos SEMPRE devem ser confirmados/
editados pelo usuário na tela antes de rastrear (o app.py já faz isso).
"""

import re
import pdfplumber

# Nomes/variações conhecidas das transportadoras usadas pela Sebem.
# Chave = identificador interno usado no restante do sistema.
TRANSPORTADORAS_CONHECIDAS = {
    "atual_cargas": [
        "atual cargas",
        "atual cargas transportes",
    ],
    "rodonaves": [
        "rodonaves",
        "rte rodonaves",
        "empresa de transportes rte",
    ],
    "expresso_sao_miguel": [
        "expresso sao miguel",
        "expresso são miguel",
        "esm - expresso",
    ],
}

CNPJ_RE = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
CPF_RE = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
# Número da NF-e: geralmente aparece como "Nº 000.123.456" ou "N. 123456"
NF_NUMERO_RE = re.compile(r"N[ºo°.]{0,2}\s*[:\-]?\s*(\d{1,3}(?:\.\d{3}){1,3}|\d{4,9})")


def extract_text(pdf_path: str) -> str:
    """Extrai todo o texto do PDF, página por página."""
    texto_completo = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text() or ""
            texto_completo.append(texto)
    return "\n".join(texto_completo)


def _somente_digitos(s: str) -> str:
    return re.sub(r"\D", "", s)


def extract_documentos(texto: str) -> list[str]:
    """Retorna todos os CNPJ/CPF encontrados no texto, na ordem em que aparecem,
    já normalizados (só dígitos), sem duplicados consecutivos."""
    encontrados = []
    for m in CNPJ_RE.finditer(texto):
        encontrados.append(_somente_digitos(m.group()))
    for m in CPF_RE.finditer(texto):
        digitos = _somente_digitos(m.group())
        # evita capturar pedaço de CNPJ como CPF
        if digitos not in encontrados:
            encontrados.append(digitos)
    return encontrados


def extract_cnpj_cpf_destinatario(texto: str) -> str | None:
    """Tenta achar o CPF/CNPJ do destinatário: procura a palavra 'Destinatário'
    e pega o CNPJ/CPF mais próximo depois dela. Se não achar, usa o segundo
    documento encontrado no texto (o primeiro costuma ser do emitente/remetente)."""
    idx = texto.lower().find("destinat")
    if idx != -1:
        trecho = texto[idx: idx + 400]
        m = CNPJ_RE.search(trecho) or CPF_RE.search(trecho)
        if m:
            return _somente_digitos(m.group())

    docs = extract_documentos(texto)
    if len(docs) >= 2:
        return docs[1]
    if docs:
        return docs[0]
    return None


def extract_numero_nf(texto: str) -> str | None:
    """Tenta achar o número da NF-e. Procura perto da palavra 'NOTA FISCAL'
    primeiro; se não achar, usa o primeiro padrão de número compatível."""
    idx = texto.upper().find("NOTA FISCAL")
    janelas = [texto[idx: idx + 200]] if idx != -1 else []
    janelas.append(texto)

    for janela in janelas:
        m = NF_NUMERO_RE.search(janela)
        if m:
            return _somente_digitos(m.group(1))
    return None


def detectar_transportadora(texto: str) -> str | None:
    """Procura o nome de uma das transportadoras conhecidas no texto do PDF.
    Retorna o identificador interno (ex: 'rodonaves') ou None se não achar."""
    texto_lower = texto.lower()
    for chave, variantes in TRANSPORTADORAS_CONHECIDAS.items():
        for variante in variantes:
            if variante in texto_lower:
                return chave
    return None


def processar_pdf(pdf_path: str) -> dict:
    """Função principal: recebe o caminho do PDF e devolve um dict com os
    campos extraídos, pronto pra tela de confirmação no Streamlit."""
    texto = extract_text(pdf_path)
    return {
        "cnpj_cpf_destinatario": extract_cnpj_cpf_destinatario(texto),
        "numero_nf": extract_numero_nf(texto),
        "transportadora": detectar_transportadora(texto),
        "texto_bruto": texto,  # útil pra depurar quando a extração falhar
    }
