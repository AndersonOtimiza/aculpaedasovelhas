"""
Health check endpoint.
"""
from fastapi import APIRouter
from src.services.faiss_service import faiss_service
from src.services.llm_service import llm_service
from src.services.bible_api_client import bible_api_client
from src.config.settings import settings
from src.models.responses import BaseResponse, HealthData

router = APIRouter()


@router.get("/health", response_model=BaseResponse[HealthData])
async def health_check():
    """Check health of all services."""
    ollama_status = await llm_service.check_health("ollama")
    bible_api_status = await bible_api_client.health_check()

    faiss_status = {
        "loaded": faiss_service.is_loaded(),
        "vectors": faiss_service.index.ntotal if faiss_service.is_loaded() else 0,
        "index_path": str(faiss_service.index_path),
    }

    return BaseResponse[HealthData](
        success=True,
        data=HealthData(
            service="exeg.ai - Advanced Exegesis Machine",
            version="1.0.0",
            status="healthy",
            components={
                "faiss_index": faiss_status,
                "ollama": ollama_status,
                "bible_api": bible_api_status,
                "config": {
                    "embedding_model": settings.EMBEDDING_MODEL,
                    "llm_model": settings.OLLAMA_MODEL,
                    "use_gpu": settings.USE_FAISS_GPU,
                },
            },
        ),
    )
