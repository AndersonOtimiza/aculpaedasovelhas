# Ecossistema Completo "A Culpa é das Ovelhas"

> **Core:** Encontrar a Verdade Bíblica através de traduções literais rígidas dos textos originais (hebraico, aramaico, grego) sem normalização ou interpretação - deixando a interpretação para o leitor.

---

## Fluxo Conceitual

```
Site → Blog → Podcast → Livrinho → Bíblia → Comunidade → exeg.ai
```

1. **aculpaedasovelhas.org** - Porta de entrada, base do projeto
2. **Blog** - Artigos inéditos revelando códigos bíblicos ocultos (com IA exeg.ai)
3. **Podcast** - Conteúdo acessível no dia a dia
4. **O Livrinho** - "A Culpa é das Ovelhas" (online gratuito ou físico)
   - Edições: _666 — The Beast Exposed_ e _O anticristo revelado_
5. **Bíblia Belém An.C 2025** - Tradução literal rígida (hebraico, aramaico, grego)
6. **Comunidade** - Acompanhamento coletivo
7. **exeg.ai** - Máquina de exegese avançada (IA especializada em "Easter Eggs bíblicos")

---

## Status dos Módulos

| #   | Módulo     | Status              | Observações                                                  |
| --- | ---------- | ------------------- | ------------------------------------------------------------ |
| 1   | Site       | **Funcional**       | 22+ páginas HTML, Docker, Cloudflare, API Python             |
| 2   | Blog       | Estrutura apenas    | Só pasta `Artigos/` - precisa implementar                    |
| 3   | Podcast    | Vazio               | Só README - precisa implementar                              |
| 4   | Livro      | **Conteúdo pronto** | 3 documentos .docx prontos                                   |
| 5   | Bíblia     | **Funcional**       | API Node.js/TypeScript, fontes textuais (BHSA, SBLGNT, etc.) |
| 6   | Comunidade | Vazio               | Só `Project.txt` - precisa implementar                       |
| 7   | exeg.ai    | **Implementado**    | Python FastAPI, FAISS GPU, SentenceTransformers, Ollama      |

---

## Estrutura do Monorepo

```
aculpaedasovelhas/
├── #exeg.ai/           ✅ Máquina de Exegese Avançada (IMPLEMENTADO)
│   ├── src/            ✅ Código fonte FastAPI
│   ├── scripts/        ✅ Build FAISS index
│   └── indexes/        ✅ Índices FAISS
├── apps/
│   ├── site/           ✅ Portal principal
│   ├── blog/           ⚠️ Estrutura apenas
│   ├── biblia/         ✅ API Tradução Belem AnC
│   ├── podcast/        ⚠️ Futuro
│   └── comunidade/     ⚠️ Futuro
├── content/
│   └── livro/          ✅ O Livrinho
├── docs/
│   └── RESUMO-ECOSSISTEMA.md
├── infra/
│   └── capacidades/    ✅ Cloudflare, 1Password, etc.
└── README.md           ✅ Atualizado
```

---

## Fluxo de Dados Real

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO DE INTEGRAÇÃO                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │     [5-Bíblia API :3001]      │
              │  - PostgreSQL (textos originais)│
              │  - Tokens, morfologia, glosses │
              └───────────────────────────────┘
                              │
                         HTTP REST
                              ▼
              ┌───────────────────────────────┐
              │      [7-exeg.ai :8000]        │
              │  - FAISS (embeddings)         │
              │  - LLMs (OpenAI/Anthropic/Ollama)│
              │  - Busca semântica            │
              └───────────────────────────────┘
                              │
                         HTTP REST
                              ▼
              ┌───────────────────────────────┐
              │     [1-Site API :8000]        │
              │  - AN Agent Bible Study       │
              │  - Ollama local               │
              │  - Knowledge base (Livro, Easter Eggs)│
              └───────────────────────────────┘
                              │
                         JSON/HTML
                              ▼
              ┌───────────────────────────────┐
              │     [Frontend Cloudflare]     │
              │  - Leitura do Livro           │
              │  - Chat com IA                │
              │  - Tradução interlinear       │
              └───────────────────────────────┘
```

---

## Integrações Técnicas Verificadas

| Status | Integração                            | Protocolo         |
| ------ | ------------------------------------- | ----------------- |
| ✅     | Site (1) ↔ exeg.ai (7)                | API HTTP          |
| ✅     | Bíblia (5) ↔ exeg.ai (7)              | API :3001 → :8000 |
| ✅     | Site (1) hospeda Livrinho (4)         | HTML/EPUB         |
| ⚠️     | Blog (2) precisa de backend           | -                 |
| ⚠️     | Podcast (3) precisa de infraestrutura | -                 |
| ⚠️     | Comunidade (6) precisa de plataforma  | -                 |

---

## Integrações Confirmadas (Implementadas)

| De           | Para              | Implementação       | Arquivo                                     |
| ------------ | ----------------- | ------------------- | ------------------------------------------- |
| Bíblia :3001 | exeg.ai :8000     | Cliente HTTP Python | `#exeg.ai/src/services/bible_api_client.py` |
| exeg.ai      | Ollama            | LLM Service         | `#exeg.ai/src/services/llm_service.py`      |
| exeg.ai      | FAISS             | Busca Semântica     | `#exeg.ai/src/services/faiss_service.py`    |
| Site         | AI Agent (Ollama) | FastAPI + Ollama    | `apps/site/api/ai_agent.py`                 |
| Livro        | Site              | JSON knowledge base | `apps/site/knowledge/`                      |

---

## APIs Disponíveis

### Site API (`/api`)

- `/api/ai/chat` - Chat com AN Agent Bible Study
- `/api/ai/verse` - Busca versículos Belem AnC
- `/api/ai/search` - Busca texto
- `/api/ai/analyze` - Análise de termos originais
- `/api/ai/compare` - Comparação de traduções

### Bíblia API (`:3001`)

- `/api/v1/books` - Livros bíblicos
- `/api/v1/verses/{book}/{chapter}` - Versículos
- `/api/v1/tokens/{verseId}` - Tokens/morfologia
- `/api/v1/glosses` - Camadas de glossário N1-N5

### exeg.ai API (`:8000`)

- `GET /` - Informações do serviço
- `GET /health` - Status de todos os componentes (FAISS, Ollama, Bible API)
- `POST /ask` - Query direta ao LLM (Ollama/OpenAI/Anthropic)
- `POST /find-similar` - Busca semântica FAISS com filtros (testamento, livro)
- `POST /explain-links` - Intertextualidade + explicação LLM
- `GET /docs` - Swagger UI (documentação interativa)

**Localização:** `#exeg.ai/`

---

## Stack Tecnológico

| Componente   | Tecnologia                        | Status          |
| ------------ | --------------------------------- | --------------- |
| API Tradução | Node.js + TypeScript + PostgreSQL | **Pronto**      |
| AI Agent     | Python + FastAPI + FAISS + Torch  | **Pronto**      |
| Frontend     | HTML/CSS/JS + Cloudflare Pages    | **Pronto**      |
| LLMs         | OpenAI, Anthropic, Cohere, Ollama | **Configurado** |

### Tecnologias Identificadas

- **Frontend:** HTML/CSS/JavaScript
- **Backend:** Node.js + TypeScript, Python
- **IA/ML:** PyTorch, TensorRT, GPU support
- **Infra:** Docker, Cloudflare Workers, Wrangler
- **Dados:** PostgreSQL, textos bíblicos (BHSA, SBLGNT, TR1550, WLC)

---

## Site aculpaedasovelhas.org

| Aspecto                | Descrição                                                       |
| ---------------------- | --------------------------------------------------------------- |
| Posição no Ecossistema | **Portal Principal** - Porta de entrada para todo o ecossistema |
| Domínio                | aculpaedasovelhas.org                                           |
| Hospedagem             | Cloudflare Pages (deploy manual via Wrangler)                   |
| Repositório            | Privado no GitHub                                               |
| Branch                 | master                                                          |

### Assets do Site

- `styles.css` - Estilos principais (tema dark/light)
- `script.js` - JavaScript principal
- `kindle-reader.js` - Modo leitura imersiva
- `api/` - API FastAPI para autenticação/downloads

### Características

- Design responsivo (mobile-first)
- Tema Dark/Light com persistência (localStorage)
- Paleta minimalista estilo Claude/VS Code
- Modo Kindle para leitura imersiva
- SEO otimizado (meta tags, Open Graph)
- EPUB disponível para download

### Estrutura Principal (22 arquivos HTML)

**Páginas Principais:**

- `index.html` - Home/Portal principal
- `manifesto.html` - O Manifesto
- `livrinho.html` - Leitura do livro (modo Kindle)
- `autor.html` - Sobre o autor
- `artigos.html` - Sistema de artigos
- `traducao.html` - Tradução bíblica
- `sobre.html` - Sobre o projeto / IA Bible Study

**Artigos:**

- `artigo-666.html`
- `artigo-666-enigma.html`
- `artigo-chaves-frameworks.html`
- `artigo-lobos-ovelhas.html`

**Centro Legal (7 páginas):**

- `legal.html`, `termos.html`, `licenca.html`, `contrato-b2b.html`
- `politica-api.html`, `sla.html`, `rfc.html`, `iso.html`, `guideline.html`

### Deploy

O deploy é **manual** via Wrangler CLI:

```bash
npx wrangler pages deploy . --project-name=aculpaedasovelhas
```

---

## Repositório

| Propriedade   | Valor                  |
| ------------- | ---------------------- |
| Nome          | aculpaedasovelhas-site |
| Visibilidade  | **private**            |
| Privado       | true                   |
| Branch padrão | master                 |

> O repositório é **privado**, o que reduz significativamente o risco de exposição dos dados que estavam no histórico.

---

## Padrão dos READMEs

Todos os READMEs agora incluem:

- Título alinhado ao ecossistema
- Posição no roteiro: `Site → Blog → Podcast → Livrinho → Bíblia → Comunidade → exeg.ai`
- Descrição do módulo
- Seção de integração com links para outros módulos
- Link de volta para o README raiz

---

## Commits Recentes

- `98ae146` - Reorganiza projeto para estrutura monorepo (1950 arquivos)

---

_Última atualização: 2025-01-03 - exeg.ai implementado_
