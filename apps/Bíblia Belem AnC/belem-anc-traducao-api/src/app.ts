import express from "express";
import cors from "cors";

// Importar rotas
import { booksRoutes } from "./modules/books/books.routes";
import { versesRoutes } from "./modules/verses/verses.routes";
import { tokensRoutes } from "./modules/tokens/tokens.routes";
import { glossesRoutes } from "./modules/glosses/glosses.routes";
import { healthRoutes } from "./modules/health/health.routes";

const app = express();

// Middlewares
app.use(cors());
app.use(express.json());

// Rota raiz
app.get("/", (req, res) => {
  res.json({
    service: "API Tradução Bíblica Literal Rígida Belem AnC",
    version: "1.0.0",
    author: "Belem, Anderson Costa",
    description:
      "API para acesso aos textos bíblicos originais (Hebraico, Aramaico, Grego) com tradução literal PT-BR",
    endpoints: {
      health: "GET /health",
      books: "GET /api/v1/books",
      verses: "GET /api/v1/verses/:book/:chapter",
      tokens: "GET /api/v1/tokens/:verseId",
      glosses: "GET /api/v1/glosses/verse/:verseId",
      search: "GET /api/v1/verses/search?q=termo"
    },
    documentation: {
      layers: {
        N0: "Texto literal (padrão)",
        N1: "Glossário mínimo",
        N2: "Marcações morfológicas",
        N3: "Reordenação de leitura",
        N4: "Expansão de elipses",
        N5: "Alternativas lexicais"
      },
      scripts: {
        HE: "Hebraico",
        ARM: "Aramaico",
        GRC: "Grego"
      }
    }
  });
});

// Rotas da API v1
app.use("/health", healthRoutes);
app.use("/api/v1/books", booksRoutes);
app.use("/api/v1/verses", versesRoutes);
app.use("/api/v1/tokens", tokensRoutes);
app.use("/api/v1/glosses", glossesRoutes);

// Handler para rotas não encontradas
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: "Endpoint not found",
    path: req.path
  });
});

export { app };
