import { app } from "./app";
import { env } from "./config/env";
import { pool } from "./config/db";

async function startServer() {
  try {
    // Testar conexão com o banco
    console.log("Connecting to database...");
    await pool.query("SELECT 1");
    console.log("Database connected successfully!");

    // Iniciar servidor
    app.listen(env.server.port, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   API Tradução Bíblica Literal Rígida Belem AnC                   ║
║   ─────────────────────────────────────────────                   ║
║                                                                   ║
║   Author: Belem, Anderson Costa                                   ║
║   Server running on port ${env.server.port}                                    ║
║   Environment: ${env.server.nodeEnv.padEnd(12)}                               ║
║                                                                   ║
║   Endpoints:                                                      ║
║   • GET  /health                    Health check                  ║
║   • GET  /api/v1/books              List books                    ║
║   • GET  /api/v1/verses/:book/:ch   List verses                   ║
║   • GET  /api/v1/tokens/:verseId    List tokens                   ║
║   • GET  /api/v1/glosses/verse/:id  Get glosses                   ║
║   • GET  /api/v1/verses/search?q=   Search verses                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
      `);
    });
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

startServer();
