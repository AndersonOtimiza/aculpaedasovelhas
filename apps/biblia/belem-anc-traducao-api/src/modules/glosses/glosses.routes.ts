import { Router } from "express";
import {
  handleGetGlossesByToken,
  handleGetGlossesByVerse
} from "./glosses.controller";

const router = Router();

// GET /api/v1/glosses/token/:tokenId - Glosses por token
router.get("/token/:tokenId", handleGetGlossesByToken);

// GET /api/v1/glosses/verse/:verseId - Glosses por versículo
router.get("/verse/:verseId", handleGetGlossesByVerse);

export { router as glossesRoutes };
