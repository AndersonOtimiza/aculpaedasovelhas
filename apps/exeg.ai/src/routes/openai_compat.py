"""
OpenAI-compatible API endpoints for Chat UI integration.
Implements /v1/models and /v1/chat/completions
"""
import time
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from src.services.llm_service import llm_service
from src.config.settings import settings
from src.config.constants import EXEG_AI_SYSTEM_PROMPT

router = APIRouter(prefix="/v1")


# ============ Models ============

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 1700000000
    owned_by: str = "exeg.ai"


class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List available models (OpenAI-compatible)."""
    models = [
        ModelInfo(id="exeg-ai", owned_by="exeg.ai"),
        ModelInfo(id=settings.OLLAMA_MODEL, owned_by="ollama"),
    ]

    if settings.OPENAI_API_KEY:
        models.append(ModelInfo(id=settings.OPENAI_MODEL, owned_by="openai"))

    if settings.ANTHROPIC_API_KEY:
        models.append(ModelInfo(id=settings.ANTHROPIC_MODEL, owned_by="anthropic"))

    return ModelsResponse(data=models)


# ============ Chat Completions ============

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "exeg-ai"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False
    top_p: Optional[float] = 0.9


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Usage


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    Chat completions endpoint (OpenAI-compatible).
    Connects to local Ollama or other configured providers.
    """
    try:
        # Extract system prompt and user messages
        system_prompt = EXEG_AI_SYSTEM_PROMPT
        user_messages = []

        for msg in request.messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                user_messages.append(f"[{msg.role}]: {msg.content}")

        # Build the prompt from conversation history
        prompt = "\n".join(user_messages)
        if not prompt:
            prompt = request.messages[-1].content if request.messages else ""

        # Determine provider based on model
        provider = "ollama"
        if "gpt" in request.model.lower():
            provider = "openai"
        elif "claude" in request.model.lower():
            provider = "anthropic"

        # Generate response
        result = await llm_service.generate(
            prompt=prompt,
            provider=provider,
            system_prompt=system_prompt,
            temperature=request.temperature or 0.7,
        )

        # Build OpenAI-compatible response
        response_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

        if request.stream:
            return StreamingResponse(
                stream_response(response_id, request.model, result["response"]),
                media_type="text/event-stream"
            )

        return ChatCompletionResponse(
            id=response_id,
            created=int(time.time()),
            model=result.get("model", request.model),
            choices=[
                ChatChoice(
                    message=ChatMessage(
                        role="assistant",
                        content=result["response"]
                    )
                )
            ],
            usage=Usage(
                total_tokens=result.get("tokens_used", 0)
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def stream_response(response_id: str, model: str, content: str):
    """Stream response in SSE format."""
    # Send content in chunks
    chunk_size = 20
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": chunk},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(data)}\n\n"

    # Send final chunk
    final_data = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_data)}\n\n"
    yield "data: [DONE]\n\n"
