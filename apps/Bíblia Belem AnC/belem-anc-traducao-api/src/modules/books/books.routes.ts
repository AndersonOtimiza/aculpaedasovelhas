import { Router } from "express";
import { handleListBooks, handleGetBook } from "./books.controller";

const router = Router();

// GET /api/v1/books - Lista todos os livros
router.get("/", handleListBooks);

// GET /api/v1/books/:code - Detalhes de um livro
router.get("/:code", handleGetBook);

export { router as booksRoutes };
