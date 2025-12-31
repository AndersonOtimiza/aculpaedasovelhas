import { Router } from "express";
import { handleHealthCheck } from "./health.controller";

const router = Router();

// GET /health - Health check
router.get("/", handleHealthCheck);

export { router as healthRoutes };
