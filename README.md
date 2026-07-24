# Rastreio Automático de Notas - Sebem

App em Streamlit: sobe o PDF da nota fiscal, extrai CNPJ/CPF do destinatário
e número da NF, detecta a transportadora e rastreia.

- **Atual Cargas**: automático de ponta a ponta (sem captcha no site deles).
- **Rodonaves** e **Expresso São Miguel**: têm captcha/reCAPTCHA, então o app
  só prepara os dados e abre o portal certo - falta 1 clique manual (resolver
  o captcha e apertar rastrear).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

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

## Próximos passos / pontos de atenção

1. **Extração do PDF (`extractor.py`) é heurística**, mas já validada com 10
   DANFEs reais da Sebem (CNPJ/CPF, número da NF e detecção de
   transportadora bateram certo em todos). Se aparecer um layout diferente
   e a extração errar, me manda o PDF (pode tampar dados sensíveis que não
   importem pro teste) e eu ajusto os padrões de busca.

2. **Deploy**: mesmo fluxo do Trayo - sobe num repositório no GitHub e
   conecta no Streamlit Cloud.
