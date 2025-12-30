# Modelo de Usuários - Ecossistema "A Culpa é das Ovelhas"

## Visão Geral

```text
                              USUÁRIOS
                                  │
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │    GERAL      │     │  REGISTRADO   │     │     PAGO      │
   │  (Visitante)  │     │   (Membro)    │     │  (Assinante)  │
   └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
           │                     │                     │
           ▼                     ▼                     ▼
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │ Site          │     │ Bíblia Online │     │ Plataforma IA │
   │ Institucional │     │ + Comunidade  │     │ + Tudo abaixo │
   │ + Artigos     │     │               │     │               │
   └───────────────┘     └───────────────┘     └───────────────┘
```

---

## Tipos de Usuário

### 1. GERAL (Visitante)

| Atributo       | Valor                        |
| -------------- | ---------------------------- |
| **Custo**      | Gratuito                     |
| **Cadastro**   | Não requer                   |
| **Acesso**     | Site Institucional + Artigos |

### 2. REGISTRADO (Membro)

| Atributo       | Valor                                     |
| -------------- | ----------------------------------------- |
| **Custo**      | Gratuito                                  |
| **Cadastro**   | Requer cadastro                           |
| **Acesso**     | Bíblia Online + Comunidade + acesso Geral |

### 3. PAGO (Assinante)

| Atributo       | Valor                         |
| -------------- | ----------------------------- |
| **Custo**      | Assinatura                    |
| **Cadastro**   | Requer cadastro + pagamento   |
| **Acesso**     | Plataforma de IA + TUDO       |

---

## Matriz de Acesso

| Recurso            | Geral | Registrado | Pago |
| ------------------ | :---: | :--------: | :--: |
| Site Institucional | ✓     | ✓          | ✓    |
| Artigos            | ✓     | ✓          | ✓    |
| Bíblia Online      | ✗     | ✓          | ✓    |
| Comunidade         | ✗     | ✓          | ✓    |
| Plataforma de IA   | ✗     | ✗          | ✓    |

---

## Funil de Conversão

```text
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     ┌──────────────┐                            │
│                     │     SITE     │                            │
│                     │  (gratuito)  │                            │
│                     └──────┬───────┘                            │
│                            │                                    │
│                       INTERESSE                                 │
│                            │                                    │
│              ┌─────────────┴─────────────┐                      │
│              ▼                           ▼                      │
│         CONVERSÃO                   CONVERSÃO                   │
│              │                           │                      │
│              ▼                           ▼                      │
│     ┌────────────────┐          ┌────────────────┐              │
│     │   REGISTRO     │          │  ASSINATURA    │              │
│     │   (gratuito)   │          │    (pago)      │              │
│     └────────┬───────┘          └────────┬───────┘              │
│              │                           │                      │
│              ▼                           ▼                      │
│     ┌────────────────┐          ┌────────────────┐              │
│     │ Bíblia Online  │          │ Plataforma IA  │              │
│     │ + Comunidade   │          │ + TUDO         │              │
│     └────────────────┘          └────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Interfaces por Tipo de Usuário

| Interface                              | Tipo de Usuário         | Tecnologia    |
| -------------------------------------- | ----------------------- | ------------- |
| aculpaedasovelhas.com                  | Geral, Registrado, Pago | HTML/CSS/JS   |
| Bíblia Online                          | Registrado, Pago        | Web App       |
| Comunidade                             | Registrado, Pago        | Web App       |
| Plataforma IA (exeg.ai)                | Pago                    | Web App (Suite) |

---

## Proposta de Valor por Nível

| Nível           | Proposta de Valor                                            |
| --------------- | ------------------------------------------------------------ |
| **Geral**       | Conhecer o projeto, ler artigos, entender a visão            |
| **Registrado**  | Estudar a Bíblia online, participar da comunidade            |
| **Pago**        | Análise profunda com IA: lexical, numérica, estrutural, temática |

---

*Documento atualizado em: 2025-12-29*
*Mantido por: AI AN Agent (Claude Code)*
