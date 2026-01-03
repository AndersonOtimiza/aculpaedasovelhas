import { Request, Response } from "express";
import { pool } from "../../config/db";

export async function handleHealthCheck(
  req: Request,
  res: Response
): Promise<void> {
  try {
    // Verificar conexão com o banco
    const dbCheck = await pool.query("SELECT 1 as check");
    const dbOk = dbCheck.rows[0]?.check === 1;

    // Verificar contagem de livros
    const booksCount = await pool.query("SELECT COUNT(*) as count FROM books");
    const versesCount = await pool.query(
      "SELECT COUNT(*) as count FROM verses"
    );
    const tokensCount = await pool.query(
      "SELECT COUNT(*) as count FROM tokens"
    );

    res.json({
      success: true,
      status: "healthy",
      service: "belem-anc-traducao-api",
      version: "1.0.0",
      timestamp: new Date().toISOString(),
      database: {
        connected: dbOk,
        stats: {
          books: parseInt(booksCount.rows[0].count, 10),
          verses: parseInt(versesCount.rows[0].count, 10),
          tokens: parseInt(tokensCount.rows[0].count, 10)
        }
      }
    });
  } catch (error) {
    console.error("Health check failed:", error);
    res.status(503).json({
      success: false,
      status: "unhealthy",
      service: "belem-anc-traducao-api",
      version: "1.0.0",
      timestamp: new Date().toISOString(),
      database: {
        connected: false,
        error: error instanceof Error ? error.message : "Unknown error"
      }
    });
  }
}
