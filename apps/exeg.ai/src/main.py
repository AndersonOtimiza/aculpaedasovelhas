"""
FastAPI application entry point for exeg.ai.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting exeg.ai - Advanced Exegesis Machine...")

    # Initialize database
    print("Initializing database...")
    from database.init_db import init_database, seed_plans
    init_database()
    seed_plans()

    from src.services.embedding_service import embedding_service
    from src.services.faiss_service import faiss_service

    # Pre-load embedding model
    print("Loading embedding model...")
    embedding_service.load_model()

    # Load FAISS index if exists
    print("Loading FAISS index...")
    if faiss_service.load_index():
        print(f"FAISS index loaded with {faiss_service.index.ntotal} vectors")
    else:
        print("FAISS index not found. Run 'python -m scripts.build_faiss_index' to create it.")

    print(f"exeg.ai ready on port {settings.API_PORT}")
    yield
    # Shutdown
    print("Shutting down exeg.ai...")


app = FastAPI(
    title="exeg.ai - Advanced Exegesis Machine",
    description="AI specialized in finding Easter Eggs in biblical texts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from src.routes import health, ask, find_similar, explain_links, auth, billing, openai_compat, leads

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(billing.router, tags=["Billing"])
app.include_router(leads.router, tags=["Leads"])
app.include_router(ask.router, prefix="/ask", tags=["LLM"])
app.include_router(find_similar.router, prefix="/find-similar", tags=["Semantic Search"])
app.include_router(explain_links.router, prefix="/explain-links", tags=["Intertextuality"])
app.include_router(openai_compat.router, tags=["OpenAI Compatible"])


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "success": True,
        "data": {
            "service": "exeg.ai - Advanced Exegesis Machine",
            "version": "2.0.0",
            "description": "AI specialized in finding Easter Eggs in biblical texts",
            "endpoints": {
                "/health": "Service health check",
                "/auth/register": "User registration",
                "/auth/login": "User authentication",
                "/api/register": "Lead capture (institutional site)",
                "/api/download": "Track lead sources",
                "/ask": "Direct LLM query (requires auth)",
                "/find-similar": "Semantic search using FAISS",
                "/explain-links": "Find and explain intertextual connections",
                "/billing/credits": "Check credit balance",
                "/billing/plans": "View subscription plans",
                "/v1/models": "OpenAI-compatible models list",
                "/v1/chat/completions": "OpenAI-compatible chat completions",
            },
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
