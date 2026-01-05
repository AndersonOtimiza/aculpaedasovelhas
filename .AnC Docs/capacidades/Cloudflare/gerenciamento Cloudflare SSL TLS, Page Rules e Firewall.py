Aqui está a **seção completa e real de gerenciamento Cloudflare — SSL/TLS, Page Rules e Firewall** — para incluir no mesmo projeto do seu agente inteligente.
Tudo segue o padrão de segurança (sem senhas locais, usando 1Password CLI, via `op`).

---

## 🔒 SEÇÃO: GERENCIAMENTO SSL, PAGE RULES E FIREWALL (Cloudflare API)

Adicionar este trecho ao arquivo `wp-intelligent-agent.js` (abaixo das funções DNS).
O código usa o mesmo cliente `cfClientAuto()` e o mesmo vault `OtimizaPro → Cloudflare_API`.

```javascript
// ==================== SSL/TLS ====================

// Lê o modo SSL/TLS atual (flexible, full, strict)
async function cfGetSSLMode(zoneId) {
  const client = await cfClientAuto();
  const res = await client.get(`/zones/${zoneId}/settings/ssl`);
  return res.data;
}

// Define o modo SSL/TLS
async function cfSetSSLMode(zoneId, mode) {
  // modos válidos: off | flexible | full | strict
  const client = await cfClientAuto();
  const res = await client.patch(`/zones/${zoneId}/settings/ssl`, { value: mode });
  return res.data;
}

// ==================== Page Rules ====================

// Lista Page Rules da zona
async function cfListPageRules(zoneId) {
  const client = await cfClientAuto();
  const res = await client.get(`/zones/${zoneId}/pagerules`);
  return res.data;
}

// Cria uma Page Rule simples
async function cfCreatePageRule(zoneId, target, actions, priority = 1) {
  const client = await cfClientAuto();
  const body = {
    targets: [{ target: "url", constraint: { operator: "matches", value: target } }],
    actions: actions, // ex: [{ id: "forwarding_url", value: { url: "https://novo.site.com/$1", status_code: 301 } }]
    priority,
    status: "active",
  };
  const res = await client.post(`/zones/${zoneId}/pagerules`, body);
  return res.data;
}

// Apaga uma Page Rule por ID
async function cfDeletePageRule(zoneId, ruleId) {
  const client = await cfClientAuto();
  const res = await client.delete(`/zones/${zoneId}/pagerules/${ruleId}`);
  return res.data;
}

// ==================== Firewall ====================

// Lista regras de firewall (Rulesets API)
async function cfListFirewallRules(zoneId) {
  const client = await cfClientAuto();
  const res = await client.get(`/zones/${zoneId}/firewall/rules`);
  return res.data;
}

// Cria regra de firewall (exemplo: bloquear IP)
async function cfCreateFirewallRule(zoneId, description, expression, action = "block") {
  const client = await cfClientAuto();
  const body = [{ action, description, filter: { expression } }];
  const res = await client.post(`/zones/${zoneId}/firewall/rules`, body);
  return res.data;
}

// Remove regra de firewall por ID
async function cfDeleteFirewallRule(zoneId, ruleId) {
  const client = await cfClientAuto();
  const res = await client.delete(`/zones/${zoneId}/firewall/rules/${ruleId}`);
  return res.data;
}

// ==================== CLI EXTENDIDO ====================
cli
  .command("cf:ssl:get <zoneOrDomain>")
  .description("Lê o modo SSL/TLS (off, flexible, full, strict)")
  .action(async (zoneOrDomain) => {
    try {
      const zoneId = zoneOrDomain.includes(".") ? await cfGetZoneIdByName(zoneOrDomain) : zoneOrDomain;
      const r = await cfGetSSLMode(zoneId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error("Erro SSL get:", err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:ssl:set <zoneOrDomain> <mode>")
  .description("Define o modo SSL/TLS (off, flexible, full, strict)")
  .action(async (zoneOrDomain, mode) => {
    try {
      const zoneId = zoneOrDomain.includes(".") ? await cfGetZoneIdByName(zoneOrDomain) : zoneOrDomain;
      const r = await cfSetSSLMode(zoneId, mode);
      console.log("SSL mode atualizado:", r.result.value);
    } catch (err) {
      console.error("Erro SSL set:", err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:pagerule:list <zoneOrDomain>")
  .description("Lista Page Rules da zona")
  .action(async (zoneOrDomain) => {
    try {
      const zoneId = zoneOrDomain.includes(".") ? await cfGetZoneIdByName(zoneOrDomain) : zoneOrDomain;
      const r = await cfListPageRules(zoneId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error("Erro Page Rules list:", err.message);
      process.exit(1);
    }
  });

cli
  .command("cf:firewall:list <zoneOrDomain>")
  .description("Lista regras de Firewall")
  .action(async (zoneOrDomain) => {
    try {
      const zoneId = zoneOrDomain.includes(".") ? await cfGetZoneIdByName(zoneOrDomain) : zoneOrDomain;
      const r = await cfListFirewallRules(zoneId);
      console.log(JSON.stringify(r.result, null, 2));
    } catch (err) {
      console.error("Erro Firewall list:", err.message);
      process.exit(1);
    }
  });
```

---

## 🧩 Exemplos de uso (terminal VSCode)

### SSL/TLS

```bash
node wp-intelligent-agent.js cf:ssl:get otimiza.pro
node wp-intelligent-agent.js cf:ssl:set otimiza.pro strict
```

### Page Rules

```bash
node wp-intelligent-agent.js cf:pagerule:list otimiza.pro
```

Para criar manualmente (exemplo em cURL):

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/pagerules" \
     -H "Authorization: Bearer <apiToken>" \
     -H "Content-Type: application/json" \
     --data '{
       "targets": [{"target":"url","constraint":{"operator":"matches","value":"http://otimiza.pro/*"}}],
       "actions": [{"id":"forwarding_url","value":{"url":"https://www.otimiza.pro/$1","status_code":301}}],
       "priority":1,"status":"active"
     }'
```

### Firewall

```bash
node wp-intelligent-agent.js cf:firewall:list otimiza.pro
```

Para criar regra bloqueando IP 200.160.1.1:

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/firewall/rules" \
     -H "Authorization: Bearer <apiToken>" \
     -H "Content-Type: application/json" \
     --data '[{
        "action": "block",
        "description": "Bloquear IP suspeito",
        "filter": {"expression": "(ip.src eq 200.160.1.1)"}
     }]'
```

---

## 🔐 Boas práticas

1. Use **API Tokens com escopos mínimos**:

   * `SSL and Certificates: Edit`
   * `Page Rules: Edit`
   * `Firewall Services: Edit`
   * `Zone: Read`
2. Guarde os tokens no 1Password (`Cloudflare_API` → campo `apiToken`).
3. O agente nunca grava dados sensíveis localmente.
4. Mantenha o log de auditoria no repositório:

   ```bash
   node wp-intelligent-agent.js cf:ssl:get otimiza.pro >> logs/cf_ssl.log
   ```

---

Deseja que eu adicione a próxima seção para **Workers / R2 / KV Storage** (para deploy e cache distribuído do agente dentro do Cloudflare)?
