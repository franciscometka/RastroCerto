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

## Próximos passos / pontos de atenção

1. **Testar a consulta real da Atual Cargas.** Como o robots.txt do
   ssw.inf.br bloqueia as ferramentas de busca que eu uso aqui no chat, não
   consegui ver uma página de RESULTADO real - só o formulário. O parser em
   `ssw_client.py` tenta achar a tabela de eventos sozinho, mas pode não vir
   perfeito de primeira. Se vier estranho, roda localmente, copia o HTML que
   aparece na caixa "Resposta bruta do site (debug)" dentro do app e me manda
   que eu ajusto o `_parsear_resultado`.

2. **Extração do PDF (`extractor.py`) é heurística.** Testa com notas reais
   da Sebem - se o CNPJ/CPF ou número da NF vier errado, me manda um PDF de
   exemplo (pode tampar dados sensíveis que não importem pro teste) e eu
   ajusto os padrões de busca.

3. **Deploy**: mesmo fluxo do Trayo - sobe num repositório no GitHub e
   conecta no Streamlit Cloud.
