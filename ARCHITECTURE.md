# Arquitetura do Projeto exeg.ai

> Diretrizes que orientam o desenho, a implementacao e a evolucao da arquitetura do projeto.

**Versao**: 1.0.0
**Data**: 2026-01-11
**Autor**: Anderson Costa Belem
**Status**: Operacional

---

## 1. Visao Geral

Este documento define as diretrizes de arquitetura do projeto exeg.ai, descrevendo sua estrutura logica, componentes principais, responsabilidades de cada camada e a forma como os modulos se comunicam. A arquitetura deve garantir clareza, separacao de responsabilidades, escalabilidade, manutenibilidade e alinhamento com os objetivos do sistema.

### 1.1 Objetivo do Sistema

Apoiar o leitor no entendimento das Escrituras atraves de uma plataforma de exegese assistida por IA, utilizando exclusivamente a **Bible Belem AnC 2025** como fonte textual.

### 1.2 Principios Arquiteturais

| Principio                          | Descricao                                                        |
| ---------------------------------- | ---------------------------------------------------------------- |
| **Fonte Unica**                    | Toda consulta biblica vem exclusivamente da Bible Belem AnC 2025 |
| **Literalidade**                   | Traducao literal rigida, sem suavizacao automatica               |
| **Autoridade do Leitor**           | IA como ferramenta assistiva, nunca interprete autonomo          |
| **Separacao de Responsabilidades** | Cada servico tem funcao especifica e isolada                     |
| **Escalabilidade**                 | Arquitetura permite crescimento horizontal                       |

---

## 2. Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                       │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │     CLOUDFLARE TUNNEL             │
                    │     (Seguranca + Roteamento)      │
                    │                                   │
                    │  plataforma.exeg.ai    → :8000    │
                    │  chat.exeg.ai          → :5173    │
                    │  biblia.aculpaedasovelhas → :3001 │
                    └─────────────────┬─────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   EXEG.AI API    │      │    CHAT UI       │      │   BIBLE API      │
│   FastAPI :8000  │      │   Static :5173   │      │   Node.js :3001  │
│                  │      │                  │      │                  │
│  ┌────────────┐  │      │  HTML/CSS/JS     │      │  Express.js      │
│  │  Routes    │  │      │  Interface       │      │  PostgreSQL      │
│  └─────┬──────┘  │      │  do Leitor       │      │  Textos Originais│
│        │         │      └────────┬─────────┘      └────────┬─────────┘
│  ┌─────▼──────┐  │               │                         │
│  │  Services  │  │               │                         │
│  └─────┬──────┘  │               │                         │
│        │         │               │                         │
│  ┌─────▼──────┐  │               │                         │
│  │  Database  │  │               │                         │
│  └────────────┘  │               │                         │
└────────┬─────────┘               │                         │
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │                                                   │
         ▼                                                   ▼
┌──────────────────┐                              ┌──────────────────┐
│     OLLAMA       │                              │      FAISS       │
│   LLM Local      │                              │  Busca Vetorial  │
│     :11434       │                              │                  │
│                  │                              │  ┌────────────┐  │
│  qwen2.5:3b      │                              │  │  Index     │  │
│  (instalado)     │                              │  │  384-dim   │  │
│                  │                              │  └────────────┘  │
└──────────────────┘                              └──────────────────┘
```

---

## 3. Camadas da Arquitetura

### 3.1 Camada de Apresentacao (Presentation Layer)

**Responsabilidade**: Interface com o usuario final.

| Componente | Tecnologia  | Porta     | Funcao                          |
| ---------- | ----------- | --------- | ------------------------------- |
| Chat UI    | HTML/CSS/JS | 5173      | Interface de chat para o leitor |
| API Docs   | Swagger UI  | 8000/docs | Documentacao interativa da API  |

**Restricoes**:

- Nenhuma logica de negocio
- Apenas chamadas HTTP para a API
- Estado minimo (stateless)

### 3.2 Camada de API (API Layer)

**Responsabilidade**: Exposicao de endpoints e roteamento de requisicoes.

```
apps/exeg.ai/src/routes/
├── health.py          # GET /health
├── ask.py             # POST /ask
├── find_similar.py    # POST /find-similar
├── explain_links.py   # POST /explain-links
├── auth.py            # /auth/*
├── billing.py         # /billing/*
├── openai_compat.py   # /v1/* (OpenAI compatible)
└── leads.py           # /leads/*
```

**Padroes**:

- RESTful
- JSON request/response
- Pydantic validation
- JWT authentication (quando requerido)

### 3.3 Camada de Servicos (Service Layer)

**Responsabilidade**: Logica de negocio e orquestracao.

```
apps/exeg.ai/src/services/
├── llm_service.py              # Orquestracao de LLMs
├── embedding_service.py        # SentenceTransformers
├── faiss_service.py            # Busca vetorial
├── bible_api_client.py         # Cliente HTTP para Bible API
└── intertextuality_service.py  # Conexoes entre passagens
```

**Padroes**:

- Dependency Injection via FastAPI
- Async/await para operacoes I/O
- Singleton para servicos pesados (embeddings, FAISS)

### 3.4 Camada de Dados (Data Layer)

**Responsabilidade**: Persistencia e acesso a dados.

| Componente | Tecnologia | Dados                                |
| ---------- | ---------- | ------------------------------------ |
| SQLite     | SQLAlchemy | Users, Subscriptions, Credits, Usage |
| PostgreSQL | Bible API  | Books, Verses, Tokens, Morphology    |
| FAISS      | faiss-cpu  | Embeddings vetoriais                 |

### 3.5 Camada de Integracao (Integration Layer)

**Responsabilidade**: Comunicacao com servicos externos.

| Integracao | Protocolo  | Endpoint        |
| ---------- | ---------- | --------------- |
| Ollama     | HTTP REST  | localhost:11434 |
| Bible API  | HTTP REST  | localhost:3001  |
| Stripe     | SDK Python | api.stripe.com  |
| Cloudflare | Tunnel     | Automatico      |

---

## 4. Componentes Principais

### 4.1 exeg.ai API (FastAPI)

**Arquivo Principal**: `apps/exeg.ai/src/main.py`

```python
# Estrutura do Application
app = FastAPI(
    title="exeg.ai",
    description="Advanced Exegesis Machine",
    version="2.0.0"
)

# Middlewares
- CORS
- Request logging
- Error handling

# Routers
- /health
- /ask
- /find-similar
- /explain-links
- /auth
- /billing
- /v1 (OpenAI compat)
```

### 4.2 LLM Service

**Arquivo**: `apps/exeg.ai/src/services/llm_service.py`

**Responsabilidades**:

1. Roteamento para provider correto (Ollama/OpenAI/Anthropic)
2. Aplicacao do System Prompt
3. Contagem de tokens
4. Tratamento de erros

**Fluxo**:

```
Request → Provider Selection → System Prompt Injection → LLM Call → Token Count → Response
```

### 4.3 Embedding Service

**Arquivo**: `apps/exeg.ai/src/services/embedding_service.py`

**Configuracao**:

- Modelo: `paraphrase-multilingual-MiniLM-L12-v2`
- Dimensao: 384
- Cache: `./models/sentence-transformers/`

### 4.4 FAISS Service

**Arquivo**: `apps/exeg.ai/src/services/faiss_service.py`

**Configuracao**:

- Index Type: `IndexFlatIP` (Inner Product)
- Index Path: `./indexes/faiss/bible_index.faiss`
- Metadata: `./indexes/faiss/bible_index.faiss.metadata.json`

### 4.5 Bible API Client

**Arquivo**: `apps/exeg.ai/src/services/bible_api_client.py`

**Endpoints Consumidos**:

```
GET  /api/v1/books
GET  /api/v1/verses/{book}/{chapter}
GET  /api/v1/verses/{book}/{chapter}/{verse}
GET  /api/v1/tokens/{verse_id}
```

---

## 5. Fluxos Operacionais

### 5.1 Fluxo de Query ao LLM

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│  /ask   │────▶│   LLM   │────▶│ Ollama  │
└─────────┘     │ Route   │     │ Service │     │ :11434  │
                └─────────┘     └─────────┘     └─────────┘
                     │               │               │
                     │               │               │
                     ▼               ▼               ▼
              ┌───────────┐   ┌───────────┐   ┌───────────┐
              │ Validate  │   │  System   │   │ Generate  │
              │ Request   │   │  Prompt   │   │ Response  │
              └───────────┘   └───────────┘   └───────────┘
```

### 5.2 Fluxo de Busca Semantica

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│ /find-  │────▶│Embedding│────▶│  FAISS  │
└─────────┘     │ similar │     │ Service │     │ Search  │
                └─────────┘     └─────────┘     └─────────┘
                     │               │               │
                     ▼               ▼               ▼
              ┌───────────┐   ┌───────────┐   ┌───────────┐
              │   Text    │   │  Encode   │   │  Top-K    │
              │   Input   │   │  384-dim  │   │  Results  │
              └───────────┘   └───────────┘   └───────────┘
```

### 5.3 Fluxo de Intertextualidade

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Cliente │────▶│/explain-│────▶│  Bible  │────▶│  FAISS  │
└─────────┘     │  links  │     │  API    │     │ Search  │
                └─────────┘     └─────────┘     └─────────┘
                     │               │               │
                     │               │               │
                     ▼               ▼               ▼
              ┌───────────┐   ┌───────────┐   ┌───────────┐
              │  Parse    │   │   Fetch   │   │  Find     │
              │ Reference │   │   Verse   │   │  Similar  │
              └───────────┘   └───────────┘   └───────────┘
                                                    │
                                                    ▼
                                             ┌───────────┐
                                             │    LLM    │
                                             │  Explain  │
                                             └───────────┘
```

---

## 6. Decisoes Arquiteturais (ADR)

### ADR-001: Fonte Unica de Dados Biblicos

**Status**: Aceito
**Contexto**: Necessidade de garantir consistencia e literalidade dos textos.
**Decisao**: Usar exclusivamente a Bible Belem AnC 2025 via API local.
**Consequencias**:

- (+) Consistencia garantida
- (+) Controle total sobre os dados
- (-) Dependencia de servico local

### ADR-002: LLM Local como Padrao

**Status**: Aceito
**Contexto**: Custo e privacidade sao preocupacoes.
**Decisao**: Ollama como provider padrao, cloud como opcional.
**Consequencias**:

- (+) Sem custo por token para usuarios free
- (+) Privacidade dos dados
- (-) Requer hardware local

### ADR-003: FAISS para Busca Semantica

**Status**: Aceito
**Contexto**: Necessidade de busca por similaridade em textos biblicos.
**Decisao**: Usar FAISS com embeddings multilinguais.
**Consequencias**:

- (+) Busca rapida e precisa
- (+) Suporte a GPU
- (-) Index precisa ser reconstruido quando dados mudam

### ADR-004: Proibicao de Gematria e Misticismo

**Status**: Aceito
**Contexto**: Foco em metodos exegeticos academicos.
**Decisao**: Remover Gematria, Cabala, Numerologia do escopo.
**Consequencias**:

- (+) Foco em exegese tecnica
- (+) Alinhamento com proposito academico
- (-) Limita alguns tipos de analise

### ADR-005: Fluxo de Confirmacao de Intencao

**Status**: Aceito
**Contexto**: Inputs ambiguos geram respostas imprecisas.
**Decisao**: Implementar menu de confirmacao [1]-[4] para inputs ambiguos.
**Consequencias**:

- (+) Respostas mais precisas
- (+) Controle do leitor sobre a acao
- (-) Passo adicional na interacao

---

## 7. Restricoes e Antipadroes

### 7.1 Restricoes

| Restricao                    | Justificativa                            |
| ---------------------------- | ---------------------------------------- |
| Sem fontes externas          | Garantir consistencia da Bible Belem AnC |
| Sem interpretacao automatica | Autoridade interpretativa e do leitor    |
| Sem suavizacao automatica    | Manter literalidade da traducao          |
| Sem conteudo mistico         | Foco em exegese academica                |

### 7.2 Antipadroes a Evitar

| Antipadrao     | Descricao                  | Solucao                         |
| -------------- | -------------------------- | ------------------------------- |
| God Object     | Servico unico fazendo tudo | Separar em servicos especificos |
| Spaghetti Code | Dependencias circulares    | Injecao de dependencias         |
| Magic Numbers  | Valores hardcoded          | Usar constants.py e .env        |
| Tight Coupling | Servicos muito acoplados   | Interfaces e abstractions       |

---

## 8. Comunicacao entre Modulos

### 8.1 Protocolos

| De          | Para        | Protocolo  | Formato      |
| ----------- | ----------- | ---------- | ------------ |
| Chat UI     | exeg.ai API | HTTP/REST  | JSON         |
| exeg.ai API | Bible API   | HTTP/REST  | JSON         |
| exeg.ai API | Ollama      | HTTP/REST  | JSON         |
| exeg.ai API | FAISS       | In-process | numpy arrays |
| exeg.ai API | SQLite      | SQLAlchemy | ORM          |

### 8.2 Portas Padrao

| Servico     | Porta | Protocolo |
| ----------- | ----- | --------- |
| exeg.ai API | 8000  | HTTP      |
| Chat UI     | 5173  | HTTP      |
| Bible API   | 3001  | HTTP      |
| Ollama      | 11434 | HTTP      |
| PostgreSQL  | 5432  | TCP       |

---

## 9. Seguranca

### 9.1 Autenticacao

- JWT com HS256
- Access Token: 30 minutos
- Refresh Token: 7 dias
- Senha: bcrypt hash

### 9.2 Autorizacao

- Rotas publicas: `/health`, `/docs`
- Rotas autenticadas: `/ask`, `/billing/*`, `/auth/me`
- Rotas admin: Futuro

### 9.3 Dados Sensiveis

| Dado            | Armazenamento | Encriptacao |
| --------------- | ------------- | ----------- |
| Senhas          | SQLite        | bcrypt      |
| API Keys (BYOK) | SQLite        | Fernet      |
| JWT Secret      | .env          | N/A         |

---

## 10. Escalabilidade

### 10.1 Horizontal

- API: Multiplas instancias atras de load balancer
- FAISS: Index compartilhado via NFS ou S3
- Database: PostgreSQL com replicas

### 10.2 Vertical

- Ollama: GPU para inferencia mais rapida
- FAISS: GPU para buscas mais rapidas
- Embeddings: Batch processing

---

## 11. Monitoramento

### 11.1 Health Check

```
GET /health
Response:
{
  "status": "healthy",
  "components": {
    "ollama": "online",
    "bible_api": "online/offline",
    "faiss_index": "loaded",
    "config": {...}
  }
}
```

### 11.2 Metricas (Futuro)

- Requests por segundo
- Latencia media
- Tokens consumidos
- Erros por endpoint

---

## 12. Evolucao e Versionamento

### 12.1 Versionamento da API

- Formato: Semantic Versioning (MAJOR.MINOR.PATCH)
- Breaking changes: Incrementar MAJOR
- Novas features: Incrementar MINOR
- Bug fixes: Incrementar PATCH

### 12.2 Processo de Mudanca

1. Propor mudanca via Issue/PR
2. Revisar impacto arquitetural
3. Atualizar este documento se necessario
4. Implementar com testes
5. Deploy gradual

---

## 13. Referencias

| Documento              | Localizacao                                   |
| ---------------------- | --------------------------------------------- |
| README Principal       | `apps/exeg.ai/README.md`                      |
| Diretrizes de Exegese  | `.AnC Treinamento/DIRETRIZES_EXEGESE.md`      |
| Objetivo da Plataforma | `.AnC Treinamento/Objetivo da plataforma.txt` |
| Deploy Guide           | `apps/exeg.ai/DEPLOY.md`                      |
| API Docs               | `http://localhost:8000/docs`                  |

---

## 14. Changelog

| Versao | Data       | Autor          | Mudancas       |
| ------ | ---------- | -------------- | -------------- |
| 1.0.0  | 2026-01-11 | Anderson Belem | Versao inicial |

---

_Alteracoes estruturais devem respeitar este guideline e ser devidamente documentadas._

---

**Ecossistema "A Culpa e das Ovelhas" - 2025**
