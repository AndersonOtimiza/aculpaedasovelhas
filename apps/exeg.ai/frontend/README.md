# exeg.ai - Site Institucional

> Plataforma de IA para exegese bíblica avançada

**Posicao no Ecossistema:** `Site -> Blog -> Podcast -> Livrinho -> Biblia -> Comunidade -> exeg.ai`

**Dominio:** [exeg.ai](https://exeg.ai)
**Hospedagem:** Cloudflare Pages

---

## Visao Geral

Site institucional da plataforma **exeg.ai**, a maquina de exegese avancada do ecossistema "A Culpa e das Ovelhas". Apresenta a plataforma, planos de assinatura e documentacao legal.

---

## Paginas

| Arquivo           | Descricao               |
| ----------------- | ----------------------- |
| `index.html`      | Landing page principal  |
| `assinatura.html` | Planos e precos         |
| `legal.html`      | Termos e politicas      |
| `sla.html`        | Service Level Agreement |

---

## Tecnologias

| Tecnologia           | Uso                 |
| -------------------- | ------------------- |
| **HTML5**            | Estrutura semantica |
| **CSS3**             | Design responsivo   |
| **JavaScript**       | Interatividade      |
| **Cloudflare Pages** | Hospedagem e CDN    |

---

## Desenvolvimento Local

```powershell
# Iniciar servidor local na porta 8081
python -m http.server 8081
# ou
npx http-server -p 8081

# Acessar: http://localhost:8081
```

---

## Deploy

O deploy e feito via **Cloudflare Pages**:

```powershell
npx wrangler pages deploy . --project-name=exeg-ai
```

---

## URLs

| Ambiente | URL                   |
| -------- | --------------------- |
| Local    | http://localhost:8081 |
| Producao | https://exeg.ai       |

---

## Integracao com o Ecossistema

Este site institucional e a porta de entrada para:

- **API exeg.ai** - https://plataforma.exeg.ai
- **Documentacao API** - https://plataforma.exeg.ai/docs
- **Site principal** - https://aculpaedasovelhas.org

---

## Links

- [API exeg.ai](../exeg.ai/README.md)
- [Site Principal](../site/README.md)
- [Ecossistema](../../docs/RESUMO-ECOSSISTEMA.md)

---

_Ultima atualizacao: 2026-01-05_
