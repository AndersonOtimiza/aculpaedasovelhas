"""
Response Pydantic models following the standard { success, data, error } pattern.
"""
from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Generic, TypeVar

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Standard response wrapper."""

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None


class AskResponseData(BaseModel):
    """Data for /ask response."""

    response: str
    provider: str
    model: str
    tokens_used: Optional[int] = None


class SimilarVerse(BaseModel):
    """A similar verse result."""

    reference: str
    book_code: str
    chapter: int
    verse: int
    text: str
    similarity_score: float
    testament: str


class FindSimilarResponseData(BaseModel):
    """Data for /find-similar response."""

    query: str
    results: List[SimilarVerse]
    count: int


class IntertextualLink(BaseModel):
    """An intertextual connection."""

    source_reference: str
    target_reference: str
    link_type: str  # "quotation", "allusion", "echo", "thematic"
    similarity_score: float
    shared_terms: List[str]
    target_text: Optional[str] = None


class EasterEgg(BaseModel):
    """An Easter Egg discovery."""

    type: str  # "gematria", "acrostic", "chiasm", etc.
    location: str
    original_text: Optional[str] = None
    pattern: str
    description: str
    connections: Optional[List[str]] = None


class ExplainLinksResponseData(BaseModel):
    """Data for /explain-links response."""

    reference: str
    verse_text: str
    connections: List[IntertextualLink]
    explanation: Optional[str] = None
    easter_eggs: Optional[List[EasterEgg]] = None


class HealthData(BaseModel):
    """Health check data."""

    service: str
    version: str
    status: str
    components: Dict[str, Any]
