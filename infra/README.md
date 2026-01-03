# Ecossistema "A Culpa é das Ovelhas"

> Um projeto completo. Feito para levar você da curiosidade até o estudo bíblico mais avançado.

**Autor:** Anderson Belem Costa
**Domínio Principal:** [aculpaedasovelhas.org](https://aculpaedasovelhas.org)

---

## Roteiro do Ecossistema

```text
Site → Blog → Livrinho → Bíblia → exeg.ai
```

---

## Estrutura do Projeto

```text
aculpaedasovelhas/
├── apps/                    # Aplicações principais
│   ├── site/               # Portal aculpaedasovelhas.org
│   ├── blog/               # Sistema de artigos
│   ├── biblia/             # API Tradução Belem AnC (junction)
│   ├── exeg-ai/            # IA de exegese (junction)
│   ├── podcast/            # Conteúdo em áudio (futuro)
│   └── comunidade/         # Espaço coletivo (futuro)
├── content/
│   └── livro/              # O Livrinho - A Culpa é das Ovelhas
├── docs/
│   ├── vendas/             # Material comercial
│   └── ecossistema/        # Documentação do ecossistema
├── infra/
│   └── capacidades/        # Integrações (Cloudflare, 1Password, etc.)
└── README.md
```

| Módulo | Path | Status |
| ------ | ---- | ------ |
| Site | [apps/site/](apps/site/) | Ativo |
| Blog | [apps/blog/](apps/blog/) | Ativo |
| Bíblia | [apps/biblia/](apps/biblia/) | Ativo |
| exeg.ai | [apps/exeg-ai/](apps/exeg-ai/) | Ativo |
| Livro | [content/livro/](content/livro/) | Ativo |
| Podcast | [apps/podcast/](apps/podcast/) | Futuro |
| Comunidade | [apps/comunidade/](apps/comunidade/) | Futuro |

---

## Módulos Ativos

### 1. Site aculpaedasovelhas.org

A base do projeto e os caminhos de acesso. Tudo começa aqui.

- **Tecnologias:** HTML5, CSS3, JavaScript, Cloudflare Pages
- **Recursos:** Modo Kindle, tema dark/light, centro legal completo
- **Integra com:** Blog, Livro, exeg.ai

### 2. Blog

O autor publica artigos inéditos revelando códigos bíblicos ocultos, com apoio da IA exeg.ai, especializada em Easter Eggs bíblicos.

> Porque existem chaves de revelação no próprio texto.

- **Integra com:** Site (publicação), exeg.ai (análise), Bíblia (referências)

### 4. O Livrinho — A Culpa é das Ovelhas

O livro que abre olhos e ouvidos para a Revelação de Jesus Cristo. Online gratuito ou físico.

**Edições:**

- 666 — The Beast Exposed
- O anticristo revelado

- **Integra com:** Site (leitura online), Bíblia (textos originais)

### 5. Bíblia Belém An.C 2025

Tradução fiel, literal e rígida, direto do hebraico, aramaico e grego. Sem normalizações. Sem interpretação no texto.

**Você lê. E a interpretação é sua.**

- **Fontes:** BHSA, SBLGNT, TR1550, WLC, Nestle 1904
- **Tecnologias:** Node.js, TypeScript, PostgreSQL, API REST (:3001)
- **Integra com:** exeg.ai (API), Site (leitura), Blog (referências)

### 7. exeg.ai

No nível avançado, a máquina de exegese do ecossistema. IA especializada em análise bíblica profunda.

- **Recursos:** Busca semântica, detecção de intertextualidade, integração com LLMs
- **Tecnologias:** Python, FastAPI, FAISS, SentenceTransformers, Ollama (:8000)
- **Integra com:** Bíblia (consome API), Blog (gera análises), Site (expõe IA)

---

## Arquitetura de Integração

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                  ECOSSISTEMA "A CULPA É DAS OVELHAS"                    │
│                       by Belem, Anderson Costa                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐         ┌─────────────────┐                       │
│   │  5 - BÍBLIA     │ ──API──►│  7 - EXEG.AI    │                       │
│   │  API Tradução   │         │  AI Agent       │                       │
│   │  :3001          │         │  :8000          │                       │
│   └────────┬────────┘         └────────┬────────┘                       │
│            │                           │                                │
│            │         ┌─────────────────┘                                │
│            │         │                                                  │
│            ▼         ▼                                                  │
│   ┌─────────────────────────────────────────────┐                       │
│   │              1 - SITE                       │                       │
│   │         aculpaedasovelhas.org               │                       │
│   │            Cloudflare Pages                 │                       │
│   └──────────┬──────────────────┬───────────────┘                       │
│              │                  │                                       │
│              ▼                  ▼                                       │
│   ┌──────────────────┐  ┌──────────────────┐                            │
│   │   2 - BLOG       │  │   4 - LIVRO      │                            │
│   │   Artigos        │  │   O Livrinho     │                            │
│   └──────────────────┘  └──────────────────┘                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Fluxo de Dados

| De | Para | Tipo | Descrição |
| -- | ---- | ---- | --------- |
| Bíblia | exeg.ai | HTTP REST | Textos originais, morfologia, tokens |
| exeg.ai | Blog | Análise | Easter Eggs, intertextualidade |
| exeg.ai | Site | API | Busca semântica, explicações |
| Livro | Site | Conteúdo | Capítulos, manifesto |
| Bíblia | Site | Leitura | Tradução literal para usuário |

---

## Proposta Central

> "Um projeto inteiro para quem quer abandonar versões e começar a ler os Textos Sagrados como eles verdadeiramente são."

---

## Licença

Todos os direitos reservados © 2025 Anderson Belem Costa
