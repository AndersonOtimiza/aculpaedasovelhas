README Pré-Projeto

# Matriz Belem, AnC — revelação de sinais e hashes intertextuais bíblicos (MTC/CTM)

## O que é este projeto
Projeto local em Python (arquivo único) para:
- Ingerir texto bíblico **original** (hebraico, aramaico, grego) em banco SQLite.
- Normalizar e indexar o texto.
- Consultar um **alvo** (texto/motivo/número).
- Gerar uma **matriz** de achados com:
  - sinais textuais (MT / II / EIC; SE reservado)
  - hashes e similaridade (HASH_EXATO, SHINGLE_k, MINHASH, SIMHASH, HASH_MTC)
  - score objetivo e auditável

Este núcleo funciona **sem internet**.  
Ele não interpreta. Ele só identifica coincidências/similaridades objetivas no texto.

## Como o Agent deve aplicar no ambiente (VSCODE local)
O Agent deve:
1) Criar um ambiente Python local.
2) Criar o banco SQLite.
3) Ingerir os textos originais (TSV).
4) Construir índices/hashes.
5) Executar consultas por alvo e salvar/visualizar a matriz.

## Estrutura (mínima)
- `mtc_app.py` (arquivo único do app)
- `data/` (seus TSVs)
- `bible.db` (banco gerado localmente)

Exemplo:
```

project/
mtc_app.py
data/
hebrew.tsv
greek.tsv
aramaic.tsv
bible.db

````

## Requisitos
- Python 3.10+ (recomendado 3.11+)
- SQLite com FTS5 habilitado (normal no macOS/Linux; no Windows costuma vir OK)

Dependência opcional:
- `regex` (recomendado para Unicode).  
  Se não instalar, o app usa `re` padrão.

## Instalação (local)
### Opção A — sem venv (não recomendado)
Nada.

### Opção B — com venv (recomendado)
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install --upgrade pip
pip install regex
````

## Formato do TSV (obrigatório)

Cada linha deve ter (por padrão):

* coluna 0: `book`
* coluna 1: `chapter` (int)
* coluna 2: `verse` (int)
* coluna 3: `text_raw` (texto original bruto)

Separador padrão: TAB.

Exemplo (hebraico):

```
GEN<TAB>1<TAB>1<TAB>בְּרֵאשִׁית בָּרָא אֱלֹהִים ...
```

Se seu TSV tiver colunas diferentes, ajuste `--bookcol`, `--chapcol`, `--versecol`, `--textcol`, `--sep`.

## Comandos (fluxo completo)

### 1) Inicializar banco

```bash
python mtc_app.py init --db bible.db
```

### 2) Ingerir textos

```bash
python mtc_app.py ingest --db bible.db --corpus he  --tsv data/hebrew.tsv
python mtc_app.py ingest --db bible.db --corpus gr  --tsv data/greek.tsv
python mtc_app.py ingest --db bible.db --corpus arc --tsv data/aramaic.tsv
```

Notas:

* Por padrão o app normaliza removendo marcas/acentos (he/gr).
* Para manter marcas, use `--keep-marks`.

Exemplo:

```bash
python mtc_app.py ingest --db bible.db --corpus he --tsv data/hebrew.tsv --keep-marks
```

### 3) Construir hashes (index)

```bash
python mtc_app.py index --db bible.db --k 3 --perms 64
```

Significados:

* `--k 3` = shingles (n-grams) de 3 tokens
* `--perms 64` = tamanho da assinatura MinHash (maior = mais lento, mais estável)

### 4) Consultar alvo e gerar matriz

```bash
python mtc_app.py query --db bible.db --alvo "sete cabeças" --top 120 --max-pairs 300 --show 30
```

Parâmetros:

* `--top` = quantos versos candidatos pegar via FTS
* `--max-pairs` = quantos pares máximos comparar (evita explosão)
* `--show` = quantas linhas da matriz imprimir

## O que o Agent deve esperar como saída

O comando `query` imprime no terminal uma tabela Markdown:

Colunas:

* `A_ref`, `B_ref` (corpus:livro cap:verso)
* `Cat` (MT/II/EIC)
* `0/1/2` (detecção)
* evidências (shared_k, minhash, simhash, score, classificação)
* `HASH_MTC` (string curta de assinatura do par)

## Definições objetivas (resumo)

* **FTS**: busca literal em texto normalizado
* **HASH_EXATO**: SHA-256 do texto normalizado (igualdade)
* **SHINGLE_k**: n-grams para coincidência parcial
* **MINHASH**: similaridade aproximada por shingles (eco)
* **SIMHASH**: similaridade aproximada por shingles (eco)
* **HASH_MTC**: assinatura legível do par (A->B + parâmetros)

## Limitações atuais (do núcleo)

1. Sem base de tokens/lemmas/Strong’s, o app não faz busca por lema.
2. SE (estrutura: inclusio/quiasmo/paralelismo) está reservado (placeholder).
3. A consulta atual compara pares dentro do conjunto de candidatos retornados pelo FTS.

## Como o Agent deve evoluir (roadmap técnico curto)

Se você (Agent) estiver estendendo este núcleo:

1. Adicionar `tokens` (lemma/strongs/morph) e um `mapper` PT/EN->Strong’s.
2. Implementar `SE`:

   * Inclusio: âncoras repetidas nas bordas do intervalo de versos
   * Quiasmo: mapa de pares por unidades
   * Paralelismo: padrão morfológico (se houver morph)
3. Adicionar “intervalo de versos” como unidade de busca (agregador).
4. Exportação de matriz em `csv/yaml/json` por flag.

## Checklist final para o Agent (execução correta)

* [ ] Python local funciona
* [ ] `init` executou e criou `bible.db`
* [ ] `ingest` para `he/gr/arc` concluiu
* [ ] `index` concluiu
* [ ] `query` retorna matriz para um alvo simples (ex.: "666", "sete cabeças")
* [ ] Se a saída vier vazia: aumentar `--top`, reduzir filtros, confirmar TSV

```
::contentReference[oaicite:0]{index=0}
```
