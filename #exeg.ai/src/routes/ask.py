"""
/ask endpoint for direct LLM queries.
"""
from fastapi import APIRouter, HTTPException
from src.models.requests import AskRequest
from src.models.responses import BaseResponse, AskResponseData
from src.services.llm_service import llm_service

router = APIRouter()


@router.post("", response_model=BaseResponse[AskResponseData])
async def ask(request: AskRequest):
    """
    Direct LLM query endpoint.

    Send a question and receive an AI-generated response focused on
    biblical exegesis and Easter Egg hunting.
    """
    try:
        # Build prompt with optional context
        prompt = request.query
        if request.context:
            prompt = f"""Contexto fornecido:
{request.context}

Pergunta: {request.query}"""

        result = await llm_service.generate(
            prompt=prompt,
            provider=request.provider,
            temperature=request.temperature,
        )

        return BaseResponse[AskResponseData](
            success=True,
            data=AskResponseData(
                response=result["response"],
                provider=result["provider"],
                model=result["model"],
                tokens_used=result.get("tokens_used"),
            ),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
