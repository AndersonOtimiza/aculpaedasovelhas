============================================================
ARQUIVO: README.md
============================================================
Otimiza AN Agent AI
"Matriz Belem, AnC — Revelação de sinais e hashes intertextuais Bíblicos"
### Desenvolvido por Anderson Belem Costa — Otimiza.pro
### Pacote Oficial — Estrutura Completa + Código CORE + ENGINE + Exemplos + App Local

## Visão Geral
**Matriz Belem, AnC — Revelação de sinais e hashes intertextuais bíblicos** é um conjunto de instruções (para LLM) + um motor local (Python) para detectar **"easter eggs" textuais mensuráveis** nos **textos bíblicos originais - Aramaico, Hebraico e Grego Koiné**.

Idiomas-alvo do texto:
- hebraico
- aramaico
- grego koiné

O Agent NÃO:
- interpreta doutrinariamente
- cria simbolismos
- harmoniza textos
- usa traduções como base de detecção

O Agent faz:
- mede padrões objetivos
- registra evidência mínima
- classifica e pontua (0–100)
- emite relatório

## Regiões (camadas) detectáveis
1) eco_lexical (lexical)  
2) paradoxo_numerico (numérica)  
3) espelho_estrutural (estrutura)  
4) tema_gemeo (temática objetiva por âncoras)  
5) ligacao_rara (raridade)  
6) assinatura_quiasmatica (quiasmo mapeável)

## O que este pacote entrega (de ponta a ponta)
1) **CORE** para colar no SYSTEM PROMPT de qualquer LLM.  
2) **ENGINE** (processo objetivo).  
3) **Catálogo** dos padrões.  
4) **Sistema de score** de raridade.  
5) **Exemplos** (modelos).  
6) **Docs do desenvolvedor**.  
7) **App local** em Python (um único arquivo), com:
   - SQLite + FTS5
   - normalização heb/aram/gre
   - hashes + similaridade (SHA-256, shingles, MinHash, SimHash)
   - saída “matriz” em Markdown no terminal

## Execução local (app Python)
### Preparo de dados (TSV)
Formato por linha:
`book<TAB>chapter<TAB>verse<TAB>text_raw`

Exemplo:
`GEN<TAB>1<TAB>1<TAB>בְּרֵאשִׁית בָּרָא אֱלֹהִים ...`

### Fluxo mínimo
```bash
python mtc_app.py init --db bible.db
python mtc_app.py ingest --db bible.db --corpus he  --tsv data/hebrew.tsv
python mtc_app.py ingest --db bible.db --corpus gr  --tsv data/greek.tsv
python mtc_app.py ingest --db bible.db --corpus arc --tsv data/aramaic.tsv
python mtc_app.py index --db bible.db --k 3 --perms 64
python mtc_app.py query --db bible.db --alvo "sete cabeças" --top 120 --max-pairs 300 --show 30
