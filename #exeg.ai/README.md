# exeg.ai - Máquina de Exegese Avançada

> IA especializada em encontrar "Easter Eggs" em textos bíblicos

**Posição no Ecossistema:** `Site → Blog → Podcast → Livrinho → Bíblia → Comunidade → exeg.ai`

**Versão:** 2.0.0 (com Sistema de Billing)

---

## Visão Geral

O **exeg.ai** é o motor de inteligência artificial do ecossistema "A Culpa é das Ovelhas". Especializado em análise exegética avançada, utiliza busca semântica e LLMs para encontrar padrões ocultos nos textos bíblicos originais.

### Capacidades

- **Busca Semântica** - FAISS + SentenceTransformers para encontrar passagens similares
- **Análise de Easter Eggs** - Gematria, acrósticos, quiasmos, padrões numéricos
- **Intertextualidade** - Conexões entre passagens do AT e NT
- **LLM Multi-Provider** - Ollama (local), OpenAI, Anthropic
- **Sistema de Billing** - Assinaturas, créditos por tokens, Stripe

---

## Modelo de Preços (Cline-like)

### Planos

| Plano | Preço | Tokens/mês | BYOK | Descrição |
|-------|-------|------------|------|-----------|
| **Free** | Grátis | 10.000 | ✅ | Para testar |
| **Pay-as-you-go** | Grátis | Ilimitado* | ✅ | Pague só o que usar |
| **Starter** | R$ 29,90 | 100.000 | ✅ | Para uso pessoal |
| **Pro** | R$ 99,90 | 500.000 | ✅ | Para pesquisadores |
| **Enterprise** | Sob consulta | Ilimitado | ✅ | Com suporte dedicado |

*Pay-as-you-go: Compre créditos avulsos, sem mensalidade.

### Pacotes de Créditos (Compra Avulsa)

| Pacote | Preço | Créditos | Bônus | Total |
|--------|-------|----------|-------|-------|
| **Pequeno** | R$ 9,90 | 50.000 | - | 50.000 |
| **Médio** | R$ 29,90 | 200.000 | +10% | 220.000 |
| **Grande** | R$ 59,90 | 500.000 | +20% | 600.000 |
| **Mega** | R$ 99,90 | 1.000.000 | +30% | 1.300.000 |

**BYOK (Bring Your Own Key)**: Disponível em **todos os planos**! Use suas próprias API keys de OpenAI/Anthropic.

### Pagamento via PIX (Otimiza Pagamentos)

Além do Stripe, oferecemos pagamento via **PIX** através da **Otimiza Pagamentos**.

**Sobre a Otimiza:**
> A **OtimizaPro** é uma WorkTech brasileira especializada em benefícios e pagamentos corporativos. Pioneira na criação da Gestão Inteligente de Vale-Transporte, economiza até 40% para os clientes. Localizada no Cubo Itaú, Vila Olímpia, São Paulo.

**Fluxo de Pagamento (Modelo Binance):**
1. Gere o QR Code PIX no sistema
2. Faça o pagamento no seu banco
3. Envie o comprovante via WhatsApp: **+55 21 99448-7472**
4. A **ANA** (IA da Otimiza) valida automaticamente
5. Créditos carregados em até 5 minutos

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/billing/pix/create` | POST | Gerar QR Code PIX |
| `/billing/pix/status/{id}` | GET | Status do pagamento |
| `/billing/pix/history` | GET | Histórico PIX |
| `/billing/pix/info` | GET | Info da Otimiza |

---

## Endpoints da API

### Core

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações do serviço |
| `/health` | GET | Status de todos os componentes |
| `/ask` | POST | Query direta ao LLM |
| `/find-similar` | POST | Busca semântica FAISS |
| `/explain-links` | POST | Intertextualidade + explicação LLM |

### Autenticação

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/auth/register` | POST | Registro de usuário |
| `/auth/login` | POST | Login (retorna JWT) |
| `/auth/refresh` | POST | Renovar access token |
| `/auth/me` | GET | Dados do usuário atual |

### Billing

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/billing/credits` | GET | Saldo de créditos |
| `/billing/usage` | GET | Histórico de uso |
| `/billing/plans` | GET | Planos disponíveis |
| `/billing/packages` | GET | Pacotes de créditos (compra avulsa) |
| `/billing/subscribe` | POST | Criar assinatura (Stripe) |
| `/billing/purchase-credits` | POST | Comprar pacote de créditos |
| `/billing/estimate` | GET | Estimar custo em BRL |
| `/billing/cancel` | POST | Cancelar assinatura |
| `/billing/portal` | GET | Portal Stripe |

### Exemplos

**Busca Semântica:**
```bash
curl -X POST http://localhost:8000/find-similar \
  -H "Content-Type: application/json" \
  -d '{"text": "o número da besta", "top_k": 5}'
```

**Query ao LLM:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual o significado de 666 em Apocalipse?"}'
```

**Conexões Intertextuais:**
```bash
curl -X POST http://localhost:8000/explain-links \
  -H "Content-Type: application/json" \
  -d '{"reference": "REV 13:18", "explain_with_llm": true}'
```

---

## Instalação

### Pré-requisitos

- Python 3.11+
- CUDA 12.4 (para GPU)
- Ollama instalado e rodando
- Bible API rodando na porta 3001

### Passos

1. **Instalar dependências:**
```bash
cd "#exeg.ai"

# CPU
pip install -r requirements.txt

# GPU (recomendado)
pip install -r requirements-gpu.txt
conda install -c pytorch faiss-gpu
```

2. **Configurar ambiente:**
```bash
cp .env.example .env
# Edite .env conforme necessário
```

3. **Construir índice FAISS:**
```bash
python -m scripts.build_faiss_index
```

4. **Iniciar servidor:**
```bash
python -m src.main
```

5. **Acessar documentação:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Configuração

### Variáveis de Ambiente

```env
# Servidor
API_PORT=8000
DEBUG=true

# Bible API
BIBLIA_API_URL=http://localhost:3001

# Ollama (LLM local)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b

# OpenAI (opcional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (opcional)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-haiku-20240307

# FAISS
FAISS_INDEX_PATH=./indexes/faiss/bible_index.faiss
USE_FAISS_GPU=true

# Embeddings
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

---

## Estrutura do Projeto

```
#exeg.ai/
├── src/
│   ├── main.py                    # Entry point FastAPI
│   ├── config/
│   │   ├── settings.py            # Pydantic Settings
│   │   └── constants.py           # System prompts
│   ├── auth/                      # Autenticação
│   │   ├── password.py            # Bcrypt hash
│   │   ├── jwt_handler.py         # JWT tokens
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── billing/                   # Sistema de billing
│   │   ├── plans.py               # Definição de planos
│   │   ├── credit_service.py      # Gestão de créditos
│   │   ├── usage_tracker.py       # Tracking de uso
│   │   └── stripe_service.py      # Integração Stripe
│   ├── models/
│   │   ├── requests.py            # Request schemas
│   │   ├── responses.py           # Response schemas
│   │   ├── user.py                # User models
│   │   ├── billing.py             # Billing models
│   │   └── db_models.py           # SQLAlchemy models
│   ├── routes/
│   │   ├── health.py              # /health
│   │   ├── auth.py                # /auth/*
│   │   ├── billing.py             # /billing/*
│   │   ├── ask.py                 # /ask
│   │   ├── find_similar.py        # /find-similar
│   │   └── explain_links.py       # /explain-links
│   └── services/
│       ├── bible_api_client.py    # Cliente HTTP Bible API
│       ├── embedding_service.py   # SentenceTransformers
│       ├── faiss_service.py       # FAISS index
│       ├── llm_service.py         # Ollama/OpenAI/Anthropic
│       └── intertextuality_service.py
├── database/
│   └── init_db.py                 # SQLAlchemy setup
├── scripts/
│   └── build_faiss_index.py       # Construir índice
├── indexes/faiss/                 # Índices FAISS salvos
├── models/sentence-transformers/  # Cache de modelos ML
├── data/embeddings/               # Cache de embeddings
├── requirements.txt               # Dependências (CPU)
├── requirements-gpu.txt           # Dependências (GPU)
└── .env.example                   # Template de configuração
```

---

## Integração com o Ecossistema

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
              │      [exeg.ai :8000]          │
              │  - FAISS (embeddings)         │
              │  - LLMs (Ollama/OpenAI)       │
              │  - Busca semântica            │
              └───────────────────────────────┘
                              │
                         HTTP REST
                              ▼
              ┌───────────────────────────────┐
              │     [1-Site Cloudflare]       │
              │  - Chat com IA                │
              │  - Busca de Easter Eggs       │
              └───────────────────────────────┘
```

---

## Stack Tecnológico

| Componente | Tecnologia |
|------------|------------|
| Framework | FastAPI |
| Embeddings | SentenceTransformers |
| Busca Vetorial | FAISS (GPU) |
| LLM Local | Ollama (qwen3:4b) |
| LLM Cloud | OpenAI, Anthropic |
| HTTP Client | httpx (async) |
| Validação | Pydantic v2 |
| Autenticação | JWT (python-jose) |
| Banco de Dados | SQLite / PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Pagamentos | Stripe |
| Hash Senhas | bcrypt (passlib) |

---

## Tipos de Easter Eggs Suportados

1. **Gematria** - Valores numéricos de palavras gregas/hebraicas
2. **Acrósticos** - Primeiras letras formando mensagens
3. **Quiasmos** - Estruturas literárias espelhadas (A-B-C-B-A)
4. **Palavras-chave** - Padrões de repetição intencional
5. **Intertextualidade** - Referências cruzadas ocultas
6. **Jogos de palavras** - Trocadilhos nos idiomas originais
7. **Estruturas numéricas** - Padrões de 7, 12, 40, etc.
8. **Tipologia** - Prefigurações do AT no NT

---

## Links

- [Ecossistema Principal](../README.md)
- [Bible API](../apps/biblia/README.md)
- [Site](../apps/site/README.md)

---

*Última atualização: 2026-01-03*
