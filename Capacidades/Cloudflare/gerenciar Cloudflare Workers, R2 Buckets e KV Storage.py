Aqui está a **seção completa para o agente gerenciar Cloudflare Workers, R2 Buckets e KV Storage** — com o mesmo padrão de segurança, autenticação via 1Password CLI (`op`) e sem gravação de credenciais locais.

---

## ⚙️ SEÇÃO: Cloudflare Workers, R2 Storage e KV Namespace

Adicionar este bloco no final do arquivo `wp-intelligent-agent.js`.

```javascript
// ==================== WORKERS ====================

// Lista Workers em uma conta
async function cfListWorkers(accountId) {
  const client = await cfClientAuto();
  const res = await client.get(`/accounts/${accountId}/workers/scripts`);
  return res.data;
}

// Publica um Worker (upload de script JavaScript)
async function cfUploadWorker(accountId, name, scriptPath) {
  const fs = await import("fs");
  const script = fs.readFileSync(scriptPath, "utf8");
  const client = await cfClientAuto();
  const res = await client.put(
    `/accounts/${accountId}/workers/scripts/${name}`,
    script,
    { headers: { "Content-Type": "application/javascript" } }
  );
  return res.data;
}

// Deleta um Worker
async function cfDeleteWorker(accountId, name) {
  const client = await cfClientAuto();
  const res = await client.delete(`/accounts/${accountId}/workers/scripts/${name}`);
  return res.data;
}

// ==================== R2 STORAGE ====================

// Lista buckets R2
async function cfListR2Buckets(accountId) {
  const client = await cfClientAuto();
  const res = await client.get(`/accounts/${accountId}/r2/buckets`);
  return res.data;
}

// Cria bucket R2
async function cfCreateR2Bucket(accountId, name) {
  const client = await cfClientAuto();
  const res = await client.post(`/accounts/${accountId}/r2/buckets`, { name });
  return res.data;
}

// Apaga bucket R2
async function cfDeleteR2Bucket(accountId, name) {
  const client = await cfClientAuto();
  const res = await client.delete(`/accounts/${accountId}/r2/buckets/${name}`);
  return res.data;
}

// ==================== KV STORAGE ====================

// Lista Namespaces
async function cfListKVNamespaces(accountId) {
  const client = await cfClientAuto();
  const res = await client.get(`/accounts/${accountId}/storage/kv/namespaces`);
  return res.data;
}

// Cria Namespace
async function cfCreateKVNamespace(accountId, title) {
  const client = await cfClientAuto();
  const res = await client.post(`/accounts/${accountId}/storage/kv/namespaces`, { title });
  return res.data;
}

// Deleta Namespace
async function cfDeleteKVNamespace(accountId, namespaceId) {
  const client = await cfClientAuto();
  const res = await client.delete(`/accounts/${accountId}/storage/kv/namespaces/${namespaceId}`);
  return res.data;
}

// Coloca valor em KV
async function cfPutKV(accountId, namespaceId, key, value) {
  const client = await cfClientAuto();
  const res = await client.put(
    `/accounts/${accountId}/storage/kv/namespaces/${namespaceId}/values/${key}`,
    value,
    { headers: { "Content-Type": "text/plain" } }
  );
  return res.data;
}

// Lê valor de KV
async function cfGetKV(accountId, namespaceId, key) {
  const client = await cfClientAuto();
  const res = await client.get(
    `/accounts/${accountId}/storage/kv/namespaces/${namespaceId}/values/${key}`
  );
  return res.data;
}

// ==================== CLI EXTENDIDO ====================

cli
  .command("cf:workers:list <accountId>")
  .description("Lista Workers da conta")
  .action(async (accountId) => {
    try {
      const r = await cfListWorkers(accountId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:workers:upload <accountId> <name> <scriptPath>")
  .description("Publica Worker (upload de arquivo .js)")
  .action(async (accountId, name, scriptPath) => {
    try {
      const r = await cfUploadWorker(accountId, name, scriptPath);
      console.log("Worker publicado:", r.result);
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:r2:list <accountId>")
  .description("Lista buckets R2")
  .action(async (accountId) => {
    try {
      const r = await cfListR2Buckets(accountId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:kv:list <accountId>")
  .description("Lista namespaces de KV")
  .action(async (accountId) => {
    try {
      const r = await cfListKVNamespaces(accountId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  });
```

---

## 🧩 Exemplo de uso

```bash
# Listar Workers existentes
node wp-intelligent-agent.js cf:workers:list 1234567890abcdef1234567890abcdef

# Publicar Worker
node wp-intelligent-agent.js cf:workers:upload 1234567890abcdef1234567890abcdef my-worker ./scripts/my-worker.js

# Listar buckets R2
node wp-intelligent-agent.js cf:r2:list 1234567890abcdef1234567890abcdef

# Listar KV namespaces
node wp-intelligent-agent.js cf:kv:list 1234567890abcdef1234567890abcdef
```

---

## 📘 Como preparar o ambiente no 1Password

No mesmo item **`Cloudflare_API`**, adicione:

| Campo       | Valor                                                  |
| ----------- | ------------------------------------------------------ |
| `apiToken`  | Token de acesso Cloudflare                             |
| `accountId` | ID da conta Cloudflare (necessário para Workers/R2/KV) |

Para localizar o **accountId**:

```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts" \
     -H "Authorization: Bearer <apiToken>"
```

Exemplo de resposta:

```json
{"result":[{"id":"1234567890abcdef1234567890abcdef","name":"OtimizaPro"}]}
```

---

## 🔐 Permissões mínimas recomendadas do API Token

Ao criar o token “**OtimizaAgent**”, inclua:

| Recurso                | Permissão |
| ---------------------- | --------- |
| **Workers Scripts**    | Edit      |
| **R2 Storage Buckets** | Edit      |
| **Workers KV Storage** | Edit      |
| **Zone**               | Read      |
| **Account**            | Read      |

---

## 🧠 Boas práticas

1. Use um **token dedicado** para automação, escopado apenas à conta necessária.
2. Mantenha logs de upload de Workers e R2 em `logs/cloudflare-workers.log`.
3. Faça upload de scripts pequenos (máx. 1 MB); scripts maiores devem ser empacotados via Wrangler CLI.
4. Evite guardar valores sensíveis diretamente no KV Storage sem criptografia.

---

Deseja que eu adicione agora a **seção de deploy automático** (usar Wrangler API para publicar Workers direto do VSCode após build)?
