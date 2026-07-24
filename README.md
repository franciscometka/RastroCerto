# Rastreio Automático de Notas - Sebem

App em Streamlit: sobe o PDF da nota fiscal, extrai CNPJ/CPF do destinatário
e número da NF, detecta a transportadora e prepara o rastreio.

As 3 transportadoras (**Atual Cargas**, **Rodonaves** e **Expresso São
Miguel**) são semi-automáticas: o app extrai e mostra os dados prontos pra
copiar, com um botão que abre o portal certo numa aba nova. O clique final
(e o captcha, quando tem) é manual.

- Rodonaves e Expresso São Miguel têm reCAPTCHA visível no formulário.
- Atual Cargas não tem captcha visível, mas o portal novo deles
  (`cliente.atualcargas.com.br`) é uma SPA cuja API de rastreio rejeita
  requisições feitas fora da navegação real da página ("token inválido") -
  indício de alguma proteção anti-bot própria. Por isso ela também ficou
  semi-automática, em vez de consultada de ponta a ponta como se imaginava
  no início do projeto (o formulário antigo do `ssw.inf.br` que seria usado
  pra isso não reflete mais os dados reais da transportadora e foi removido).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Próximos passos / pontos de atenção

1. **Extração do PDF (`extractor.py`) é heurística**, mas já validada com 10
   DANFEs reais da Sebem (CNPJ/CPF, número da NF e detecção de
   transportadora bateram certo em todos). Se aparecer um layout diferente
   e a extração errar, me manda o PDF (pode tampar dados sensíveis que não
   importem pro teste) e eu ajusto os padrões de busca.

2. **Atual Cargas automática de verdade**: só dá pra reconsiderar se a
   Atual Cargas tiver uma API oficial com credenciais (perguntar direto pra
   transportadora). Não vale a pena tentar contornar a proteção do portal
   deles.

3. **Deploy**: mesmo fluxo do Trayo - sobe num repositório no GitHub e
   conecta no Streamlit Cloud.
