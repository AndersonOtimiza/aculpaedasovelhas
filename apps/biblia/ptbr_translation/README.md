# Belem Bible AnC - Tradução Literal Rígida (TEA)

**Autor**: Anderson Belem Costa (Belem, AnC)  
**Método**: Belém AnC-Ipísis Iliteris Fidelity Method  
**Nível de Rigidez**: TEA (Tradução Extremamente Rígida)  
**Data de Início**: 2025

---

## Sobre a Tradução

A **Belem Bible AnC** é uma tradução própria e independente dos códices bíblicos originais de domínio público, seguindo o princípio de **máxima fidelidade literal** aos textos hebraicos, aramaicos e gregos.

### Método: Belém AnC-Ipísis Iliteris Fidelity Method

Este método proprietário desenvolvido por Anderson Belem Costa prioriza:

1. **Fidelidade Morfológica**: Preservação das estruturas gramaticais originais
2. **Fidelidade Sintática**: Manutenção da ordem das palavras quando possível
3. **Fidelidade Lexical**: Tradução consistente de termos-chave
4. **Transparência Textual**: Indicação de variantes textuais e decisões tradutórias
5. **Rigor Acadêmico**: Baseada em edições críticas de domínio público

---

## Fontes Utilizadas

### Antigo Testamento
- **WLC** (Westminster Leningrad Codex) - Texto massorético completo

### Novo Testamento
- **Nestle 1904** - Edição crítica grega (fonte primária para Apocalipse)
- **Westcott-Hort 1881** - Edição crítica grega (consulta)
- **Textus Receptus 1550** - Texto recebido (consulta)

---

## Estrutura de Pastas

```
ptbr_translation/
├── glossary/              # Glossários centralizados
│   ├── greek_glossary.json # Glossário Grego-Português (JSON)
│   ├── greek_terms.md     # Documentação de termos gregos
│   └── hebrew_terms.md    # Documentação de termos hebraicos
├── glossary_manager.py    # Gerenciador de glossários
├── translate_revelation.py # Script principal de tradução (Apocalipse)
├── translate_all_revelation.py # Script de tradução em lote
├── OT/                    # Antigo Testamento (39 livros)
│   ├── Pentateuco/
│   ├── Historicos/
│   ├── Poeticos/
│   └── Profeticos/
│
├── NT/                    # Novo Testamento (27 livros)
│   ├── Evangelhos/
│   ├── Atos/
│   ├── Epistolas_Paulo/
│   ├── Epistolas_Gerais/
│   └── Apocalipse/
│
├── metadata/              # Metadados da tradução
│   ├── translation_notes.json
│   ├── variant_readings.json
│   └── lexical_decisions.json
│
└── glossary/              # Glossários e concordâncias
    ├── hebrew_terms.json
    ├── greek_glossary.json
    └── theological_concepts.json
```

---

## Formato dos Arquivos

### Formato JSON (estruturado)
```json
{
  "book": "Genesis",
  "chapter": 1,
  "verses": [
    {
      "verse": 1,
      "original": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
      "translation": "No princípio criou Deus os céus e a terra",
      "morphology": "...",
      "notes": "..."
    }
  ]
}
```

### Formato Markdown (leitura)
```markdown
# Gênesis 1

¹ No princípio criou Deus os céus e a terra.
² E a terra estava sem forma e vazia...
```

---

## Princípios de Tradução TEA

### 1. Literalidade Extrema
- Prioridade absoluta ao texto original
- Estruturas hebraicas/gregas mantidas quando viável em português
- Mínima interpretação ou paráfrase

### 2. Consistência Lexical
- Mesma palavra original = mesma palavra portuguesa (quando possível)
- Glossário mantido rigorosamente
- Exceções documentadas

### 3. Transparência
- Notas de rodapé para decisões complexas
- Indicação de variantes textuais significativas
- Referências cruzadas aos códices originais

### 4. Preservação Estrutural
- Ordem das palavras respeitada quando natural em português
- Paralelismos poéticos mantidos
- Estruturas quiásticas preservadas

---

## Status da Tradução

### Antigo Testamento
- [ ] Pentateuco (0/5 livros)
- [ ] Históricos (0/12 livros)
- [ ] Poéticos (0/5 livros)
- [ ] Profetas Maiores (0/5 livros)
- [ ] Profetas Menores (0/12 livros)

### Novo Testamento
- [ ] Evangelhos (0/4 livros)
- [ ] Atos (0/1 livro)
- [ ] Epístolas Paulinas (0/13 livros)
- [ ] Epístolas Gerais (0/8 livros)
- [ ] Apocalipse (0/1 livro)

**Total**: 0/66 livros completos

---

## Ferramentas de Suporte

### Análise Morfológica
- Parser hebraico: Morfologia WLC integrada
- Parser grego: Análise morfológica NT

### Verificação de Consistência
- Scripts Python para verificar consistência lexical
- Concordância automática
- Detecção de inconsistências

### Controle de Qualidade
- Revisão por camadas
- Validação contra códices originais
- Testes de legibilidade em português

---

## Direitos Autorais

**Código e Tradução**: © 2025 Anderson Belem Costa (Belem, AnC) - Todos os direitos reservados

**Textos Originais**: Domínio Público (WLC, Westcott-Hort 1881, TR 1550, Nestle 1904)

---

## Contato

Para questões sobre o método de tradução ou colaboração:
- Site: aculpaedasovelhas.com
- Projeto: O Livrinho

---

## Changelog

### 2025-12-06
- Estrutura inicial criada
- Documentação do método estabelecida
- Pastas organizadas para receber tradução
