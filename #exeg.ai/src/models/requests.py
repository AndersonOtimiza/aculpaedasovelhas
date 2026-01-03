"""
Request Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AskRequest(BaseModel):
    """Request model for /ask endpoint."""

    query: str = Field(..., min_length=1, description="Question or query for the LLM")
    provider: Literal["ollama", "openai", "anthropic"] = Field(
        default="ollama", description="LLM provider to use"
    )
    context: Optional[str] = Field(
        default=None, description="Additional context (verses, text) for analysis"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class FindSimilarRequest(BaseModel):
    """Request model for /find-similar endpoint."""

    text: str = Field(
        ..., min_length=1, description="Text to find similar passages for"
    )
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    testament: Optional[Literal["AT", "NT", "all"]] = Field(
        default="all", description="Filter by testament"
    )
    book: Optional[str] = Field(default=None, description="Filter by book code")


class ExplainLinksRequest(BaseModel):
    """Request model for /explain-links endpoint."""

    reference: str = Field(
        ..., description="Bible reference (e.g., 'REV 13:18' or 'Apocalipse 13:18')"
    )
    find_connections: bool = Field(
        default=True, description="Find intertextual connections"
    )
    explain_with_llm: bool = Field(
        default=True, description="Use LLM to explain the connections"
    )
    top_k: int = Field(default=10, ge=1, le=50, description="Number of connections")
    provider: Literal["ollama", "openai", "anthropic"] = Field(default="ollama")
