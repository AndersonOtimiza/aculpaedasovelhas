"""
Client for the Bible API on port 3001.
"""
import httpx
from typing import Optional, List, Dict, Any
from src.config.settings import settings


class BibleAPIClient:
    """Async client for Bible API integration."""

    def __init__(self):
        self.base_url = settings.BIBLIA_API_URL
        self.timeout = settings.BIBLIA_API_TIMEOUT

    async def get_books(self) -> List[Dict[str, Any]]:
        """Get all biblical books."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v1/books")
            response.raise_for_status()
            result = response.json()
            return result.get("data", [])

    async def get_verses(self, book_code: str, chapter: int) -> List[Dict[str, Any]]:
        """Get verses for a chapter."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/verses/{book_code}/{chapter}"
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data", [])

    async def get_verse_with_tokens(
        self, book_code: str, chapter: int, verse: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific verse with morphological tokens."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/verses/{book_code}/{chapter}/{verse}"
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            result = response.json()
            return result.get("data")

    async def get_tokens(self, verse_id: int) -> List[Dict[str, Any]]:
        """Get tokens for a verse with morphology."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v1/tokens/{verse_id}")
            response.raise_for_status()
            result = response.json()
            return result.get("data", [])

    async def search_verses(
        self, query: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search verses by text."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/verses/search",
                params={"q": query, "limit": limit},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data", [])

    async def health_check(self) -> Dict[str, Any]:
        """Check Bible API health."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return {"status": "online", "url": self.base_url}
        except Exception as e:
            return {"status": "offline", "url": self.base_url, "error": str(e)}
        return {"status": "unknown", "url": self.base_url}

    async def get_all_verses_for_embedding(self) -> List[Dict[str, Any]]:
        """
        Get all verses for building FAISS index.
        Returns list with: id, reference, text, testament
        """
        all_verses = []
        books = await self.get_books()

        for book in books:
            book_code = book.get("code")
            chapters = book.get("chapters", book.get("chapters_count", 0))
            testament = book.get("testament", "NT")
            book_name = book.get("name_pt", book_code)

            print(f"  Processing {book_name}...")

            for chapter in range(1, chapters + 1):
                try:
                    verses = await self.get_verses(book_code, chapter)
                    for verse_data in verses:
                        # Build text from tokens if available
                        tokens = verse_data.get("tokens", [])
                        if tokens:
                            text = " ".join(
                                [
                                    t.get("pt_literal", "")
                                    for t in tokens
                                    if t.get("pt_literal")
                                ]
                            )
                        else:
                            # Fallback to verse text
                            text = verse_data.get("text", "")

                        if text.strip():
                            all_verses.append(
                                {
                                    "id": verse_data.get("id"),
                                    "reference": verse_data.get(
                                        "canonical_ref",
                                        f"{book_code} {chapter}:{verse_data.get('verse', 0)}",
                                    ),
                                    "book_code": book_code,
                                    "chapter": verse_data.get("chapter", chapter),
                                    "verse": verse_data.get("verse", 0),
                                    "text": text.strip(),
                                    "testament": testament,
                                }
                            )
                except Exception as e:
                    print(f"    Error fetching {book_code} {chapter}: {e}")
                    continue

        return all_verses


bible_api_client = BibleAPIClient()
