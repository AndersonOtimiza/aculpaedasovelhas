DEVELOPER/local_engine_integration.md

# Integração Local (Python) — mtc_app.py (arquivo único)

## Preparo de dados (TSV)
book<TAB>chapter<TAB>verse<TAB>text_raw

## Fluxo mínimo
python mtc_app.py init --db bible.db
python mtc_app.py ingest --db bible.db --corpus he  --tsv data/hebrew.tsv
python mtc_app.py ingest --db bible.db --corpus gr  --tsv data/greek.tsv
python mtc_app.py ingest --db bible.db --corpus arc --tsv data/aramaic.tsv
python mtc_app.py index --db bible.db --k 3 --perms 64
python mtc_app.py query --db bible.db --alvo "sete cabeças" --top 120 --max-pairs 300 --show 30

## Nota
Este núcleo faz literal + hashes por similaridade.
Para “alvo em qualquer idioma → originais”, adicionar dicionário PT/EN → lemma/Strong’s + tokens.
