# biblia-codices-ai

Plataforma base para um sistema de IA especializado em estudos bíblicos a partir dos textos originais e códices.

## Objetivo

1. Armazenar textos bíblicos em nível de:
   - Livro / capítulo / versículo
   - Token (palavra)
   - Morfologia e sintaxe
   - Variantes textuais
   - Links para imagens oficiais de manuscritos

2. Expor uma API REST para:
   - Listar livros, capítulos e versículos
   - Buscar tokens e morfologia
   - Ver variantes por versículo
   - Ver links para manuscritos e imagens (sem armazenar imagens localmente)

## Stack

- Node.js + TypeScript
- Express
- PostgreSQL
- `pg` para acesso ao banco

## Ollama (LLM local)

Ollama roda como servico externo; nao e pacote Python.

Instalacao (Windows):
```bash
winget install --id Ollama.Ollama -e
```

Iniciar servico (se nao estiver rodando):
```bash
ollama serve
```

Se o modelo nao estiver baixado, baixe e teste (padrao recomendado):
```bash
ollama pull qwen3:4b
ollama run qwen3:4b "teste rapido"
```

API padrao: http://localhost:11434

## Como começar

### 1. Criar banco PostgreSQL local

```bash
createdb biblia_codices_ai
```

### 2. Criar arquivo .env na raiz

```bash
cp .env.example .env
```

Ajustar variáveis conforme o ambiente.

### 3. Rodar o script SQL

```bash
psql -d biblia_codices_ai -f database/schema.sql
```

### 4. Instalar dependências do backend

```bash
cd backend
npm install
```

### 5. Rodar servidor em modo desenvolvimento

```bash
npm run dev
```

### 6. Testar health-check

```
GET http://localhost:3000/health
```

## Endpoints da API

### Health Check
- `GET /health` - Verifica status do servidor

### Books
- `GET /books` - Lista todos os livros

### Verses
- `GET /verses/:bookId/:chapter` - Lista versículos de um capítulo (bookId é numérico)

### Tokens
- `GET /tokens/:verseId` - Lista tokens de um versículo (com opcional ?sourceId=N)

### Manuscripts
- `GET /manuscripts` - Lista todos os manuscritos
- `GET /manuscripts/:bookId/:chapter/:verse` - Lista imagens de manuscritos para um versículo específico

## Próximos Passos

### Implementar ETL de:
- OSHB + WLC para o AT (Antigo Testamento)
- SBLGNT + MorphGNT para o NT (Novo Testamento)

### Adicionar endpoints de busca avançada:
- Por lemma
- Por morfologia
- Por alinhamento entre versões (TM vs LXX vs NT)

## Estrutura do Projeto

```
biblia-codices-ai/
├── README.md
├── .env.example
├── .env
├── database/
│   └── schema.sql
└── backend/
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── server.ts
        ├── app.ts
        ├── config/
        │   ├── env.ts
        │   └── db.ts
        └── modules/
            ├── health/
            │   └── health.routes.ts
            ├── books/
            │   ├── books.controller.ts
            │   ├── books.routes.ts
            │   └── books.service.ts
            ├── verses/
            │   ├── verses.controller.ts
            │   ├── verses.routes.ts
            │   └── verses.service.ts
            ├── tokens/
            │   ├── tokens.controller.ts
            │   ├── tokens.routes.ts
            │   └── tokens.service.ts
            └── manuscripts/
                ├── manuscripts.controller.ts
                ├── manuscripts.routes.ts
                └── manuscripts.service.ts
```
