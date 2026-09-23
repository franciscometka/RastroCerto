# Rastreio Automático de Notas - Sebem

App em Streamlit: sobe o PDF da nota fiscal, extrai CNPJ/CPF do destinatário
e número da NF, detecta a transportadora e rastreia.

- **Atual Cargas**: automático de ponta a ponta (sem captcha no site deles).
- **Rodonaves**: automático via API oficial (`dev.rodonaves.com.br`) - precisa
  configurar `RODONAVES_API_USERNAME`/`RODONAVES_API_PASSWORD` (ver
  `.streamlit/secrets.toml.example`). Sem credencial, o app cai
  automaticamente pro modo manual.
- **Expresso São Miguel**: automático via API oficial (`wsintegcli02.expressosaomiguel.com.br`)
  - precisa configurar até 3 pares `SAO_MIGUEL_CUSTOMER_N`/`SAO_MIGUEL_ACCESS_KEY_N`
  (um por CNPJ do grupo Sebem que despacha por essa transportadora; ver
  `.streamlit/secrets.toml.example`). Sem nenhum configurado, o app cai
  automaticamente pro modo manual.

## Rodar localmente

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # preenche com as credenciais quando tiver
streamlit run app.py
```

## Estrutura do projeto

- `app.py` — tela principal (Streamlit): orquestra upload → extração → rastreio
- `config.py` — constantes centralizadas: nomes das transportadoras, paletas de cor (tema da UI + cores da imagem), URLs e parâmetros de rede
- `extractor.py` — extração de dados do PDF (CNPJ/CPF, número da NF, transportadora)
- `validators.py` — validação de CPF/CNPJ (dígito verificador) e número da NF, pra avisar antes de rastrear se a extração pegou algo inválido
- `ssw_client.py` — automação da Atual Cargas (scraping do formulário SSW, sem captcha)
- `rodonaves_client.py` — cliente da API oficial da Rodonaves (autenticação + rastreio)
- `sao_miguel_client.py` — cliente da API oficial da Expresso São Miguel (rastreio; tenta até 3 pares de credencial)
- `semi_auto.py` — fallback de portal manual (fica vazio hoje - as 3 transportadoras são automáticas; usado se faltar credencial)
- `resultado_display.py` — formatação dos resultados na tela
- `imagem_rastreio.py` — gera a imagem PNG baixável do histórico de cada transportadora
- `estilo.py` — CSS/tema do app (fundo escuro + azul da marca), monta o `:root` a partir de `config.TEMA`
- `http_utils.py` — sessão HTTP com retry automático, usada pelos três clientes
- `assets/` — logo (favicon + cabeçalho) e fontes DejaVu Sans (usadas na imagem PNG)
- `.streamlit/secrets.toml` — credenciais (nunca commitado; veja o `.example`)

## Pegadinha resolvida: URL certa da Atual Cargas no ssw.inf.br

O formulário "Rastreamento pelo destinatário" do ssw.inf.br
(`https://ssw.inf.br/2/rastreamento_dest?pwd=2`) tem duas variantes que
parecem idênticas na tela mas submetem pra **actions diferentes**
(confirmado lendo `https://ssw.inf.br/scripts/rastreamento4.js`):

- "Pelo destinatário - **30 dias**" → `/2/resultSSW_dest` (só shipments
  recentes; na prática deu "nenhuma informação encontrada" até pra notas
  reais e válidas).
- "Pelo destinatário" (sem limite de dias) → **`/2/resultSSW_dest_nro`**
  (essa é a que funciona de verdade).

`ssw_client.py` já usa a URL certa (`resultSSW_dest_nro`). Se um dia parar
de achar resultado de novo, o jeito de confirmar é abrir o formulário num
navegador de verdade, testar uma nota que você sabe que existe, e ver pra
qual `action` ele está de fato submetendo.

Detalhe do parser: a linha de um evento real pode ter um
`<p class="titulo">` dentro da célula de situação (só pra destacar o texto
em negrito) - isso não pode ser confundido com a linha de aviso de "nada
encontrado" (que tem uma estrutura diferente: 1 único `<td colspan=...>`).

## Sobre o portal novo da Atual Cargas (cliente.atualcargas.com.br)

A Atual Cargas também tem um portal mais novo em
`cliente.atualcargas.com.br`, com uma API própria
(`/api/rastreio/deslogado`). Não usamos essa API porque ela rejeitou
requisições feitas fora da navegação real da página com "token inválido" -
parece ter alguma proteção anti-bot própria, e não vale a pena tentar
contornar. Ficamos com o `ssw.inf.br` mesmo, que funciona bem com a URL
certa.

## Rodonaves - API oficial

Documentação pública em https://dev.rodonaves.com.br/reference/rastreio-1
(não precisa estar logado pra ver). Fluxo:

1. `POST https://tracking-apigateway.rte.com.br/token` com
   `auth_type=DEV`, `grant_type=password`, `username`, `password` (form-data)
   → devolve um `access_token` (JWT).
2. `GET https://tracking-apigateway.rte.com.br/api/v1/tracking` com
   `TaxIdRegistration` (CPF/CNPJ) e `InvoiceNumber` (número da NF) como
   query params, `Authorization: Bearer <token>` no header.

Pegadinhas descobertas testando com notas reais:
- Credencial errada devolve **400**, não 401.
- Nota/CPF sem correspondência devolve **204 sem corpo** (não 404) - o
  cliente trata os dois como "nada encontrado".

O token não é cacheado entre consultas (autentica de novo a cada clique) -
simples e sem custo perceptível pro padrão de uso do app.

## Expresso São Miguel - API oficial

Documentação recebida por e-mail ("Manual Técnico - Integração Clientes",
2026) - sem portal público, então se o formato mudar não tem onde
conferir, só pedir a documentação atualizada de novo. Fluxo:

`POST https://wsintegcli02.expressosaomiguel.com.br:40504/wsservernet/api/tracking`
com headers `Access_Key`, `Customer` (CNPJ dono da chave) e
`Modelo_Consulta: TRACKING_COMPLETO_POR_NOTA_FISCAL_E_COMPROVANTE`, corpo
`{"valoresParametros": [cpfOuCnpjDestinatario, numeroNF, serieOuNull]}`.
Sem endpoint de token separado - a autenticação é só nesses headers.

A Sebem despacha por essa transportadora com 3 CNPJs diferentes, cada um
com seu próprio par Customer/Access_Key - como o `extractor.py` só extrai
o CNPJ do destinatário (não o do remetente que emitiu a nota), o cliente
tenta os 3 pares em sequência até um funcionar.

Pegadinhas descobertas testando com notas reais (a doc erra os status):
- CPF/CNPJ mal formado devolve **400** com corpo JSON
  `{"message": "Documento inválido: ..."}`, não 401 - a doc chama isso de
  "chave de acesso inválida", mas na prática é validação do dado enviado.
  Nesse caso não faz sentido tentar os outros pares de credencial (o erro
  se repetiria), então o cliente já retorna direto com a mensagem da API.
- CPF/CNPJ bem formado mas sem correspondência devolve **200 com lista
  vazia** (`[]`) - esse sim é tratado como "nada encontrado".
- Credencial de fato inválida (chave errada) também devolve **400**, com
  mensagem tipo `"Cliente não encontrado! Verifique parametros."` - não dá
  pra distinguir "documento errado" de "credencial errada" só pelo status
  HTTP, então o cliente trata os dois igual: devolve a mensagem da própria
  API sem tentar os outros pares de credencial (não adiantaria, já que o
  problema geralmente está no dado enviado, não em qual chave foi usada).

## Próximos passos / pontos de atenção

1. **Extração do PDF (`extractor.py`) é heurística**, mas já validada com
   DANFEs reais da Sebem de várias transportadoras (CNPJ/CPF, número da NF
   e detecção de transportadora bateram certo). Se aparecer um layout
   diferente e a extração errar, me manda o PDF (pode tampar dados
   sensíveis que não importem pro teste) e eu ajusto os padrões de busca.

2. **Deploy**: mesmo fluxo do Trayo - sobe num repositório no GitHub e
   conecta no Streamlit Cloud. Lembrar de configurar
   `RODONAVES_API_USERNAME`/`RODONAVES_API_PASSWORD` nos Secrets do app no
   Streamlit Cloud (mesmo formato do `secrets.toml` local).
