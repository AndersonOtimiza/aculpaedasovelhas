# URLs dos Projetos

## Site institucional aculpaedasovelhas

- **Site em Prod:** https://aculpaedasovelhas.org
- **URL Local:** http://localhost:8080/
- **Interface "O Livrinho" Client:** http://localhost:8080/livrinho.html

---

## Bible Belem, An.C

- **Site em Prod:** https://aculpaedasovelhas.org/biblia-belem
- **URL Local:** http://localhost:8080/biblia-belem.html
- **Interface Client:** Leitor bíblico interativo
- **URL Local:** http://localhost:8080/ler-biblia.html
- **API Prod:** https://biblia.aculpaedasovelhas.org
- **API Local:** http://localhost:3001

---

## exeg.ai

- **Site em Prod:** https://exeg.ai / https://exeg.aculpaedasovelhas.org
- **URL Local:** http://localhost:8002
- **Interface Client:** http://localhost:8080/exegai.html
- **Docs API:** https://exeg.aculpaedasovelhas.org/docs (Prod) / http://localhost:8002/docs (Local)

---

## Otimizapro.com

- **Site em Prod:** https://otimizapro.com
- **URL Local:** _(serviço externo)_
- **Site que redireciona:** https://otimiza.pro
- **Interface Client:** https://plataforma.otimiza.pro
- **PIX (CNPJ):** 32920260000171

---

# Infraestrutura

## Cloudflare

### Configuração Principal

- **Account ID:** `28248f850aef40d0c91531280962a88a`
- **Domínio Principal:** `aculpaedasovelhas.org`
- **Hospedagem:** Cloudflare Pages (integração GitHub)
- **Deploy automático:** Push para branch `master`

### Túnel Cloudflared

- **Arquivo de config:** `apps/exeg.ai/cloudflared.yml`
- **Rotas configuradas:**
  - `exeg.aculpaedasovelhas.org` → localhost:8000
  - `biblia.aculpaedasovelhas.org` → localhost:3001

### Setup do Túnel (comandos iniciais)

```powershell
cloudflared tunnel login
cloudflared tunnel create aculpaedasovelhas-api
cloudflared tunnel route dns aculpaedasovelhas-api exeg.aculpaedasovelhas.org
cloudflared tunnel route dns aculpaedasovelhas-api biblia.aculpaedasovelhas.org
```

---

## Mapeamento de Portas Locais

| Serviço     | Porta Local | Endpoint Público             | Tecnologia                 |
| ----------- | ----------- | ---------------------------- | -------------------------- |
| Site Web    | 8080        | aculpaedasovelhas.org        | Nginx/HTML/CSS/JS          |
| Bible API   | 3001        | biblia.aculpaedasovelhas.org | Node.js/TypeScript/Express |
| exeg.ai API | 8000/8002   | exeg.aculpaedasovelhas.org   | Python/FastAPI             |
| PostgreSQL  | 5433        | localhost (interno)          | PostgreSQL 16              |
| Ollama      | 11434       | localhost (interno)          | LLM Local                  |

---

## Dependências Entre Serviços

```
Internet
   ↓
Cloudflare Tunnel
   ├→ exeg.ai (8000) → Ollama (11434)
   │                 → Bible API (3001)
   └→ Bible API (3001) → PostgreSQL (5433)
```

---

## Health Checks

| Serviço   | Endpoint                           |
| --------- | ---------------------------------- |
| Bible API | `GET http://localhost:3001/health` |
| exeg.ai   | `GET http://localhost:8002/health` |
| Site      | `GET http://localhost:8080/`       |

---

## Deploy

### Site (Cloudflare Pages)

```powershell
.\deploy.ps1 -m "feat: descrição da alteração"
```

- Trigger: push para `master`
- Workflow: `.github/workflows/deploy.yml`

### Serviços Locais (4 terminais)

```powershell
# Terminal 1 - Bible API
cd "apps/Bíblia Belem AnC/belem-anc-traducao-api"
npm run dev

# Terminal 2 - Ollama
ollama serve

# Terminal 3 - exeg.ai
cd "apps/exeg.ai"
python -m src.main

# Terminal 4 - Tunnel
cd "apps/exeg.ai"
.\start-tunnel.ps1
```

---

## Variáveis de Ambiente Principais

### Site (`apps/site/.env`)

```env
TUNNEL_TOKEN=<token>
TUNNEL_NAME=aculpaedasovelhas
PRIMARY_DOMAIN=aculpaedasovelhas.org
LOCAL_PORT=8080
```

### Bible API (`apps/Bíblia Belem AnC/.env`)

```env
DB_HOST=localhost
DB_PORT=5433
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=belem_anc_traducao
PORT=3001
```

### exeg.ai (`apps/exeg.ai/.env`)

```env
API_PORT=8002
BIBLIA_API_URL=http://localhost:3001
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
DATABASE_URL=sqlite:///./database/exeg.db
OTIMIZA_PIX_KEY=pix@otimizapagamentos.com.br
```

---

## Docker

### Bible API

```powershell
cd "apps/Bíblia Belem AnC/belem-anc-traducao-api"
docker-compose up -d
```

- Container: `belem-anc-postgres` (porta 5433)
- Container: `belem-anc-api` (porta 3001)

---

## Scripts Úteis

| Script             | Localização        | Função                     |
| ------------------ | ------------------ | -------------------------- |
| `start-site.ps1`   | apps/site/         | Inicia site + tunnel       |
| `start-tunnel.ps1` | apps/exeg.ai/      | Inicia túnel Cloudflare    |
| `deploy.ps1`       | apps/site/scripts/ | Deploy para produção       |
| `server.ps1`       | apps/site/scripts/ | Gerencia servidores locais |
| `abrir-sites.ps1`  | apps/site/         | Abre URLs no navegador     |

---

## Endpoints Públicos

| URL                                        | Descrição       |
| ------------------------------------------ | --------------- |
| https://aculpaedasovelhas.org              | Site principal  |
| https://aculpaedasovelhas.org/livrinho     | Página do livro |
| https://aculpaedasovelhas.org/biblia-belem | Bíblia Belem    |
| https://biblia.aculpaedasovelhas.org       | API da Bíblia   |
| https://exeg.aculpaedasovelhas.org         | API exeg.ai     |
| https://exeg.aculpaedasovelhas.org/docs    | Swagger UI      |
