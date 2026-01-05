import { Router } from "express";
import {
  handleListTokens,
  handleGetInterlinear,
  handleGetMorphology
} from "./tokens.controller";

const router = Router();

// GET /api/v1/tokens/:verseId - Lista tokens de um versículo
router.get("/:verseId", handleListTokens);

// GET /api/v1/tokens/:verseId/interlinear - Visão interlinear
router.get("/:verseId/interlinear", handleGetInterlinear);

// GET /api/v1/tokens/:verseId/morphology - Análise morfológica completa
router.get("/:verseId/morphology", handleGetMorphology);

export { router as tokensRoutes };
