"""
/find-similar endpoint for FAISS semantic search.
"""
from fastapi import APIRouter, HTTPException
from src.models.requests import FindSimilarRequest
from src.models.responses import BaseResponse, FindSimilarResponseData, SimilarVerse
from src.services.embedding_service import embedding_service
from src.services.faiss_service import faiss_service

router = APIRouter()


@router.post("", response_model=BaseResponse[FindSimilarResponseData])
async def find_similar(request: FindSimilarRequest):
    """
    Semantic search using FAISS.

    Find biblically similar verses based on semantic meaning,
    not just keyword matching.
    """
    if not faiss_service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="FAISS index not loaded. Run 'python -m scripts.build_faiss_index' first.",
        )

    try:
        # Generate embedding for query
        query_embedding = embedding_service.encode(request.text)

        # Build filter function
        def filter_fn(meta):
            if request.testament and request.testament != "all":
                if meta.get("testament") != request.testament:
                    return False
            if request.book:
                if meta.get("book_code", "").upper() != request.book.upper():
                    return False
            return True

        # Search
        results = faiss_service.search(
            query_embedding,
            top_k=request.top_k,
            filter_fn=filter_fn if (request.testament != "all" or request.book) else None,
        )

        # Format results
        similar_verses = [
            SimilarVerse(
                reference=meta.get("reference", ""),
                book_code=meta.get("book_code", ""),
                chapter=meta.get("chapter", 0),
                verse=meta.get("verse", 0),
                text=meta.get("text", ""),
                similarity_score=score,
                testament=meta.get("testament", ""),
            )
            for meta, score in results
        ]

        return BaseResponse[FindSimilarResponseData](
            success=True,
            data=FindSimilarResponseData(
                query=request.text,
                results=similar_verses,
                count=len(similar_verses),
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
