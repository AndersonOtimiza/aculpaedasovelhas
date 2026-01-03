# Deploy - exeg.ai + Bible API

> Expor as APIs publicamente via Cloudflare Tunnel

---

## Arquitetura

```
Internet
    │
    ▼
┌─────────────────────────────────────────────┐
│         Cloudflare Tunnel                   │
│  (Túnel seguro para sua máquina local)      │
└─────────────────────────────────────────────┘
    │                           │
    ▼                           ▼
┌─────────────────┐    ┌─────────────────┐
│ exeg.ai :8000   │    │ Bible API :3001 │
│ FastAPI/Python  │    │ Node.js/TS      │
└─────────────────┘    └─────────────────┘
    │
    ▼
┌─────────────────┐
│ Ollama :11434   │
│ LLM Local       │
└─────────────────┘
```

---

## Passo a Passo

### 1. Configurar Tunnel (uma vez)

```powershell
# Login na Cloudflare
cloudflared tunnel login

# Criar tunnel
cloudflared tunnel create aculpaedasovelhas-api

# Anotar o TUNNEL_ID gerado (ex: abc123-def456-...)
```

### 2. Configurar DNS

```powershell
# Adicionar rotas DNS
cloudflared tunnel route dns aculpaedasovelhas-api exeg.aculpaedasovelhas.org
cloudflared tunnel route dns aculpaedasovelhas-api biblia.aculpaedasovelhas.org
```

### 3. Atualizar cloudflared.yml

Edite `#exeg.ai/cloudflared.yml` e substitua:

- `TUNNEL_ID_AQUI` pelo ID do tunnel criado

### 4. Iniciar Serviços

**Terminal 1 - Bible API:**

```powershell
cd "5 - Bíblia Belem AnC - Tradução Literal Rígida\belem-anc-traducao-api"
npm run dev
```

**Terminal 2 - Ollama:**

```powershell
ollama serve
```

**Terminal 3 - exeg.ai:**

```powershell
cd "#exeg.ai"
python -m src.main
```

**Terminal 4 - Tunnel:**

```powershell
cd "#exeg.ai"
.\start-tunnel.ps1
```

---

## Endpoints Públicos

| Endpoint     | URL                                     |
| ------------ | --------------------------------------- |
| exeg.ai API  | https://exeg.aculpaedasovelhas.org      |
| exeg.ai Docs | https://exeg.aculpaedasovelhas.org/docs |
| Bible API    | https://biblia.aculpaedasovelhas.org    |

---

## Exemplos de Uso

### Busca Semântica (exeg.ai)

```bash
curl -X POST https://exeg.aculpaedasovelhas.org/find-similar \
  -H "Content-Type: application/json" \
  -d '{"text": "o número da besta", "top_k": 5}'
```

### Query LLM (exeg.ai)

```bash
curl -X POST https://exeg.aculpaedasovelhas.org/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Explique o significado de 666"}'
```

### Livros da Bíblia (Bible API)

```bash
curl https://biblia.aculpaedasovelhas.org/api/v1/books
```

### Versículos (Bible API)

```bash
curl https://biblia.aculpaedasovelhas.org/api/v1/verses/REV/13
```

---

## Troubleshooting

### Tunnel não conecta

```powershell
# Verificar status
cloudflared tunnel info aculpaedasovelhas-api

# Recriar credenciais
cloudflared tunnel delete aculpaedasovelhas-api
cloudflared tunnel create aculpaedasovelhas-api
```

### Serviço offline

```powershell
# Verificar portas
netstat -an | findstr "3001 8000 11434"
```

### CORS errors

O CORS está habilitado em ambas as APIs. Se houver problemas, verifique os headers.

---

## Segurança

- O tunnel é criptografado end-to-end
- Não expõe seu IP público
- Autenticação pode ser adicionada via Cloudflare Access

---

_Última atualização: 2025-01-03_
