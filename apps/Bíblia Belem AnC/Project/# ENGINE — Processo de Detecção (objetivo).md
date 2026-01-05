# ENGINE — Processo de Detecção (objetivo)

## 1) mapear_ocorrencias_lexicais

Saída: repetição lexical (token/lema/raiz), expressão idêntica, variação mínima, shingles repetidos.
Evidência mínima: verso + trecho original.

Exemplo (modelo):

- raiz “בנה”
  → Gn 4:17
  → Gn 11:4

## 2) mapear_numeros

Saída: números, séries (6–60–600–666) se existirem.
Evidência mínima: verso + número.

## 3) mapear_estruturas_repetidas

Saída: moldes (A→B→C) replicados.
Evidência mínima: mapa objetivo de blocos.

## 4) mapear_posicoes_estruturais

Saída: bordas/centro; inclusio quando mensurável.
Evidência mínima: termos-borda + refs.

## 5) mapear_temas_redundantes (temática objetiva)

Saída: motivos delimitados por âncoras lexicais, coocorrência, ordem.
Evidência mínima: âncoras + contexto mínimo.

## 6) combinar_com_rare_trigger_words

Saída: raros e interseções raras.
Evidência mínima: contagem + refs.

## 7) combinar_com_numeric_triggers

Gatilhos: 6, 60, 600, 66, 606, 660, 666.
Evidência mínima: verso + número.

## 8) avaliar_raridade

Saída: score 0–100 com componentes.

## 9) gerar_relatorio

Saída: relatório Markdown final.
