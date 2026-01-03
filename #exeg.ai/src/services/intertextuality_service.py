"""
Service for finding intertextual connections and Easter Eggs.
"""
import re
from typing import List, Dict, Any
from src.config.constants import STOPWORDS_PT


class IntertextualityService:
    """Service for finding intertextual connections in biblical texts."""

    # Book code mappings (Portuguese names to codes)
    BOOK_ALIASES = {
        # Old Testament
        "genesis": "GEN", "gen": "GEN", "gn": "GEN",
        "exodo": "EXO", "ex": "EXO",
        "levitico": "LEV", "lv": "LEV",
        "numeros": "NUM", "nm": "NUM",
        "deuteronomio": "DEU", "dt": "DEU",
        "josue": "JOS", "js": "JOS",
        "juizes": "JDG", "jz": "JDG",
        "rute": "RUT", "rt": "RUT",
        "1samuel": "1SA", "1sm": "1SA",
        "2samuel": "2SA", "2sm": "2SA",
        "1reis": "1KI", "1rs": "1KI",
        "2reis": "2KI", "2rs": "2KI",
        "1cronicas": "1CH", "1cr": "1CH",
        "2cronicas": "2CH", "2cr": "2CH",
        "esdras": "EZR", "ed": "EZR",
        "neemias": "NEH", "ne": "NEH",
        "ester": "EST", "et": "EST",
        "jo": "JOB", "job": "JOB",
        "salmos": "PSA", "sl": "PSA", "salmo": "PSA",
        "proverbios": "PRO", "pv": "PRO",
        "eclesiastes": "ECC", "ec": "ECC",
        "cantares": "SNG", "ct": "SNG",
        "isaias": "ISA", "is": "ISA",
        "jeremias": "JER", "jr": "JER",
        "lamentacoes": "LAM", "lm": "LAM",
        "ezequiel": "EZK", "ez": "EZK",
        "daniel": "DAN", "dn": "DAN",
        "oseias": "HOS", "os": "HOS",
        "joel": "JOL", "jl": "JOL",
        "amos": "AMO", "am": "AMO",
        "obadias": "OBA", "ob": "OBA",
        "jonas": "JON", "jn": "JON",
        "miqueias": "MIC", "mq": "MIC",
        "naum": "NAM", "na": "NAM",
        "habacuque": "HAB", "hc": "HAB",
        "sofonias": "ZEP", "sf": "ZEP",
        "ageu": "HAG", "ag": "HAG",
        "zacarias": "ZEC", "zc": "ZEC",
        "malaquias": "MAL", "ml": "MAL",
        # New Testament
        "mateus": "MAT", "mt": "MAT",
        "marcos": "MRK", "mc": "MRK",
        "lucas": "LUK", "lc": "LUK",
        "joao": "JHN", "jo": "JHN",
        "atos": "ACT", "at": "ACT",
        "romanos": "ROM", "rm": "ROM",
        "1corintios": "1CO", "1co": "1CO",
        "2corintios": "2CO", "2co": "2CO",
        "galatas": "GAL", "gl": "GAL",
        "efesios": "EPH", "ef": "EPH",
        "filipenses": "PHP", "fp": "PHP",
        "colossenses": "COL", "cl": "COL",
        "1tessalonicenses": "1TH", "1ts": "1TH",
        "2tessalonicenses": "2TH", "2ts": "2TH",
        "1timoteo": "1TI", "1tm": "1TI",
        "2timoteo": "2TI", "2tm": "2TI",
        "tito": "TIT", "tt": "TIT",
        "filemom": "PHM", "fm": "PHM",
        "hebreus": "HEB", "hb": "HEB",
        "tiago": "JAS", "tg": "JAS",
        "1pedro": "1PE", "1pe": "1PE",
        "2pedro": "2PE", "2pe": "2PE",
        "1joao": "1JN", "1jo": "1JN",
        "2joao": "2JN", "2jo": "2JN",
        "3joao": "3JN", "3jo": "3JN",
        "judas": "JUD", "jd": "JUD",
        "apocalipse": "REV", "ap": "REV", "rev": "REV",
    }

    def parse_reference(self, reference: str) -> Dict[str, Any]:
        """
        Parse a Bible reference into components.

        Supports formats:
        - "REV 13:18"
        - "Apocalipse 13:18"
        - "Ap 13:18"
        - "1CO 1:1"
        """
        reference = reference.strip()

        # Pattern for references like "1CO 1:1" or "REV 13:18"
        pattern = r"^(\d?\s*[A-Za-zÀ-ú]+)\s+(\d+)[:\s](\d+)$"
        match = re.match(pattern, reference, re.IGNORECASE)

        if not match:
            raise ValueError(f"Invalid reference format: {reference}")

        book_part = match.group(1).strip().lower().replace(" ", "")
        chapter = int(match.group(2))
        verse = int(match.group(3))

        # Try to find book code
        book_code = book_part.upper()
        if book_part in self.BOOK_ALIASES:
            book_code = self.BOOK_ALIASES[book_part]

        return {"book_code": book_code, "chapter": chapter, "verse": verse}

    async def find_connections(
        self, reference: str, top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Find intertextual connections for a verse.

        Args:
            reference: Bible reference (e.g., "REV 13:18")
            top_k: Number of similar verses to find

        Returns:
            Dict with verse data and connections
        """
        from src.services.bible_api_client import bible_api_client
        from src.services.embedding_service import embedding_service
        from src.services.faiss_service import faiss_service

        # Parse reference
        parsed = self.parse_reference(reference)
        book_code = parsed["book_code"]
        chapter = parsed["chapter"]
        verse = parsed["verse"]

        # Get verse from Bible API
        verse_data = await bible_api_client.get_verse_with_tokens(
            book_code, chapter, verse
        )
        if not verse_data:
            raise ValueError(f"Verse not found: {reference}")

        # Build text from tokens
        tokens = verse_data.get("tokens", [])
        if tokens:
            verse_text = " ".join(
                [t.get("pt_literal", "") for t in tokens if t.get("pt_literal")]
            )
        else:
            verse_text = verse_data.get("text", "")

        canonical_ref = verse_data.get(
            "canonical_ref", f"{book_code} {chapter}:{verse}"
        )

        # Get similar verses using FAISS
        connections = []
        if faiss_service.is_loaded() and verse_text.strip():
            query_embedding = embedding_service.encode(verse_text)
            similar = faiss_service.search(query_embedding, top_k=top_k + 1)

            for meta, score in similar:
                # Skip self-reference
                if meta.get("reference") == canonical_ref:
                    continue

                # Identify shared terms
                shared_terms = self._find_shared_terms(verse_text, meta.get("text", ""))

                connections.append(
                    {
                        "source_reference": reference,
                        "target_reference": meta.get("reference"),
                        "link_type": self._classify_link(score, shared_terms),
                        "similarity_score": score,
                        "shared_terms": shared_terms,
                        "target_text": meta.get("text"),
                    }
                )

                if len(connections) >= top_k:
                    break

        return {
            "reference": reference,
            "canonical_ref": canonical_ref,
            "verse_text": verse_text,
            "tokens": tokens,
            "connections": connections,
        }

    def _find_shared_terms(self, text1: str, text2: str) -> List[str]:
        """Find significant shared terms between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Filter stopwords and short words
        shared = words1.intersection(words2) - STOPWORDS_PT
        shared = [w for w in shared if len(w) > 2]

        return sorted(shared)[:5]

    def _classify_link(self, score: float, shared_terms: List[str]) -> str:
        """Classify the type of intertextual link."""
        if score > 0.9:
            return "quotation"
        elif score > 0.7:
            return "allusion"
        elif len(shared_terms) > 2:
            return "thematic"
        else:
            return "echo"

    async def explain_connections(
        self, verse_data: Dict[str, Any], provider: str = "ollama"
    ) -> str:
        """Use LLM to explain intertextual connections."""
        from src.services.llm_service import llm_service

        connections = verse_data.get("connections", [])
        if not connections:
            return "Nenhuma conexao intertextual significativa encontrada."

        # Build prompt
        prompt = f"""Analise as conexoes intertextuais para {verse_data['reference']}:

Texto do versiculo:
{verse_data['verse_text']}

Conexoes encontradas:
"""
        for conn in connections[:5]:
            prompt += f"""
- {conn['target_reference']} (similaridade: {conn['similarity_score']:.2f})
  Texto: {conn.get('target_text', 'N/A')[:100]}...
  Termos compartilhados: {', '.join(conn['shared_terms']) if conn['shared_terms'] else 'nenhum'}
  Tipo: {conn['link_type']}
"""

        prompt += """
Explique estas conexoes do ponto de vista de:
1. Padroes tematicos compartilhados
2. Possiveis "Easter Eggs" (padroes ocultos intencionais)
3. Significado teologico das conexoes
"""

        result = await llm_service.generate(prompt, provider=provider)
        return result.get("response", "")


intertextuality_service = IntertextualityService()
