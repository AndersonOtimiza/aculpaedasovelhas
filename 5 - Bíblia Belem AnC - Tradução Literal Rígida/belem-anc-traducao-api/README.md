# API Tradução Bíblica Literal Rígida Belem AnC

**Autor**: Belem, Anderson Costa
**Parte do Ecossistema**: "A Culpa é das Ovelhas"

## Descrição

API REST para acesso aos textos bíblicos originais em **Hebraico (HE)**, **Aramaico (ARM)** e **Grego (GRC)**, com suporte à **Nova Tradução Bíblica Literal Rígida Belem AnC**.

### Princípio: Separação TEXTO x APOIO

- **Camada A (Imutável)**: Tradução literal rígida - sem normalização, sem harmonização
- **Camada B (Opcional)**: Normalização assistida comandada pelo leitor (N1-N5)

## Tecnologias

- Node.js + Express + TypeScript
- PostgreSQL 16
- Docker + Docker Compose

## Instalação

### Desenvolvimento Local

```bash
# Instalar dependências
npm install

# Copiar configuração
cp .env.example .env

# Iniciar PostgreSQL (via Docker)
docker-compose up -d postgres

# Iniciar servidor de desenvolvimento
npm run dev
```

### Docker (Produção)

```bash
docker-compose up -d
```

## Endpoints

| Método | Endpoint                               | Descrição                 |
| ------ | -------------------------------------- | ------------------------- |
| GET    | `/health`                              | Health check              |
| GET    | `/api/v1/books`                        | Lista livros bíblicos     |
| GET    | `/api/v1/books/:code`                  | Detalhes de um livro      |
| GET    | `/api/v1/verses/:book/:chapter`        | Versículos de um capítulo |
| GET    | `/api/v1/verses/:book/:chapter/:verse` | Versículo com tokens      |
| GET    | `/api/v1/verses/search?q=termo`        | Busca textual             |
| GET    | `/api/v1/tokens/:verseId`              | Tokens de um versículo    |
| GET    | `/api/v1/tokens/:verseId/interlinear`  | Visão interlinear         |
| GET    | `/api/v1/tokens/:verseId/morphology`   | Análise morfológica       |
| GET    | `/api/v1/glosses/verse/:verseId`       | Glosses/camadas de apoio  |

### Parâmetros de Query

- `?testament=AT|NT` - Filtrar por testamento
- `?trad_group=HEB_TM|ARM_TM|GRC_NT` - Filtrar por tradição
- `?layer=N1|N2|N3|N4|N5` - Camada de normalização
- `?script=HE|ARM|GRC` - Filtrar por idioma original

## Camadas de Normalização (Camada B)

| Camada | Descrição              |
| ------ | ---------------------- |
| N0     | Texto literal (padrão) |
| N1     | Glossário mínimo       |
| N2     | Marcações morfológicas |
| N3     | Reordenação de leitura |
| N4     | Expansão de elipses    |
| N5     | Alternativas lexicais  |

## ETL (Importação de Dados)

```bash
# Importar Hebraico (OSHB)
npm run etl:oshb

# Importar Grego (SBLGNT)
npm run etl:sblgnt

# Importar Aramaico (BHSA)
npm run etl:aramaic

# Importar todos
npm run etl:all
```

## Fontes de Dados

- **OSHB**: Open Scriptures Hebrew Bible (CC BY 4.0)
- **SBLGNT**: SBL Greek New Testament (CC BY 4.0)
- **BHSA**: Biblia Hebraica Stuttgartensia Amstelodamensis (CC BY-NC 4.0)

## Licença

MIT

---

**"A Verdade vos libertará"** - João 8:32
