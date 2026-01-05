# Download e Importação do Evangelho de João

## Fonte de Dados

- **Texto**: SBLGNT (SBL Greek New Testament)
- **Repositório**: https://github.com/LogosBible/SBLGNT
- **Licença**: CC BY 4.0 (Creative Commons Attribution)
- **Formato**: Texto grego do Novo Testamento com códigos morfológicos

## Passo a Passo

### 1. Download do Evangelho de João

```powershell
# Executar no terminal PowerShell
.\scripts\download-john.ps1
```

Este script:

- Baixa o arquivo `43-JHN.txt` do repositório SBLGNT
- Salva em `data/sblgnt/`
- Arquivo contém texto grego com análise morfológica

### 2. Converter para JSON

```powershell
.\scripts\convert-sblgnt-to-json.ps1
```

Este script:

- Lê o arquivo `43-JHN.txt`
- Parse do formato SBLGNT (Referência TAB Texto TAB Parsing)
- Gera arquivo `john.json` estruturado
- Formato: array de versículos com tokens

### 3. Importar para o Banco de Dados

```bash
# Garantir que o banco está rodando
createdb biblia_codices_ai  # Se ainda não criou
psql -d biblia_codices_ai -f database/schema.sql

# Importar João
cd backend
npx ts-node src/etl/import-john.ts
```

Este script:

- Lê `john.json`
- Insere versículos na tabela `verses`
- Insere tokens na tabela `tokens`
- Insere morfologia na tabela `morphology`
- Total: ~879 versículos, ~15.635 tokens

## Estrutura do Arquivo SBLGNT

Formato original:

```
430101	Ἐν	P-
430101	ἀρχῇ	N-DSF
430101	ἦν	V-IAI-3S
430101	ὁ	T-NSM
430101	λόγος	N-NSM
...
```

Formato JSON gerado:

```json
[
  {
    "book": "JHN",
    "chapter": 1,
    "verse": 1,
    "tokens": [
      {"text": "Ἐν", "lemma": "", "morph": "P-", "strong": ""},
      {"text": "ἀρχῇ", "lemma": "", "morph": "N-DSF", "strong": ""},
      ...
    ]
  }
]
```

## Verificar Importação

Após importação, testar os endpoints:

### Listar livros (incluindo João)

```bash
curl http://localhost:3000/books
# Procurar por: {"id": 5, "code": "JHN", ...}
```

### Listar versículos de João 1

```bash
curl http://localhost:3000/verses/5/1
# Retorna todos os versículos do capítulo 1
```

### Ver tokens do primeiro versículo

```bash
# Pegar ID do versículo da query anterior
curl http://localhost:3000/tokens/[ID_DO_VERSICULO]
```

### Buscar por palavra específica (exemplo: λόγος - logos)

```bash
# Quando implementado endpoint de busca
curl "http://localhost:3000/tokens/search?text=λόγος"
```

## Formato dos Códigos Morfológicos

SBLGNT usa códigos Robinson:

- `N-NSM` = Noun, Nominative, Singular, Masculine
- `V-IAI-3S` = Verb, Imperfect, Active, Indicative, 3rd person, Singular
- `P-` = Preposition
- `T-NSM` = Article, Nominative, Singular, Masculine

## Estatísticas do Evangelho de João

- **Capítulos**: 21
- **Versículos**: ~879
- **Palavras**: ~15.635
- **Versículo mais longo**: João 21:25
- **Versículo mais conhecido**: João 3:16

## Melhorias Futuras

1. **Adicionar lemmas**: Usar MorphGNT para formas lexicais
2. **Números Strong's**: Integrar Strong's numbers
3. **Tradução**: Adicionar glossas em português
4. **Variantes textuais**: Importar variantes de manuscritos
5. **Sintaxe**: Adicionar análise sintática (cláusulas, frases)

## Troubleshooting

### Erro ao baixar

- Verificar conexão com internet
- GitHub pode estar temporariamente indisponível
- Tentar novamente após alguns minutos

### Erro na conversão

- Verificar encoding do arquivo (UTF-8)
- Arquivo pode estar corrompido, baixar novamente

### Erro na importação

- Verificar se banco de dados está rodando
- Confirmar que schema.sql foi executado
- Verificar credenciais no .env
- Garantir que livro "JHN" existe na tabela books

### Livro não encontrado

Se João não estiver na tabela books, adicionar:

```sql
INSERT INTO books (canon_order, code, name_original, name_pt, testament, trad_group)
VALUES (43, 'JHN', 'Κατὰ Ἰωάννην', 'João', 'NT', 'GRC_NT')
ON CONFLICT (code) DO NOTHING;
```

## Licença

Os dados do SBLGNT são licenciados sob CC BY 4.0:

- Uso livre para qualquer propósito
- Atribuição requerida
- Fonte: SBLGNT © 2010 Logos Bible Software / SBL

## Recursos Adicionais

- Site oficial: http://sblgnt.com/
- Documentação: https://github.com/LogosBible/SBLGNT/blob/master/README.md
- Códigos morfológicos: https://github.com/morphgnt/sblgnt
