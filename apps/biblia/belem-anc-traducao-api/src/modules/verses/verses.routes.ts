import { Router } from "express";
import {
  handleListVerses,
  handleGetVerse,
  handleSearchVerses,
} from "./verses.controller";

const router = Router();

// GET /api/v1/verses/search?q=termo&script=GRC - Busca textual
router.get("/search", handleSearchVerses);

// GET /api/v1/verses/:book/:chapter - Lista versículos de um capítulo
router.get("/:book/:chapter", handleListVerses);

// GET /api/v1/verses/:book/:chapter/:verse - Versículo específico com tokens
router.get("/:book/:chapter/:verse", handleGetVerse);

export { router as versesRoutes };
