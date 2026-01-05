"""
/explain-links endpoint for intertextuality analysis.
"""
from fastapi import APIRouter, HTTPException
from src.models.requests import ExplainLinksRequest
from src.models.responses import (
    BaseResponse,
    ExplainLinksResponseData,
    IntertextualLink,
)
from src.services.intertextuality_service import intertextuality_service

router = APIRouter()


@router.post("", response_model=BaseResponse[ExplainLinksResponseData])
async def explain_links(request: ExplainLinksRequest):
    """
    Find and explain intertextual connections.

    Given a Bible reference, find related passages and optionally
    use LLM to explain the connections and potential Easter Eggs.
    """
    try:
        # Find connections
        result = await intertextuality_service.find_connections(
            reference=request.reference, top_k=request.top_k
        )

        # Format connections
        connections = [
            IntertextualLink(
                source_reference=conn["source_reference"],
                target_reference=conn["target_reference"],
                link_type=conn["link_type"],
                similarity_score=conn["similarity_score"],
                shared_terms=conn["shared_terms"],
                target_text=conn.get("target_text"),
            )
            for conn in result.get("connections", [])
        ]

        # Get LLM explanation if requested
        explanation = None
        if request.explain_with_llm and connections:
            explanation = await intertextuality_service.explain_connections(
                result, provider=request.provider
            )

        return BaseResponse[ExplainLinksResponseData](
            success=True,
            data=ExplainLinksResponseData(
                reference=request.reference,
                verse_text=result.get("verse_text", ""),
                connections=connections,
                explanation=explanation,
            ),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
