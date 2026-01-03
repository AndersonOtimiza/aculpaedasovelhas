"""
SentenceTransformers embedding service.
"""
import numpy as np
from typing import List, Union
from src.config.settings import settings


class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformers."""

    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
        self.cache_dir = settings.EMBEDDING_CACHE_DIR

    def load_model(self) -> None:
        """Load the embedding model."""
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(
                self.model_name, cache_folder=self.cache_dir
            )
            print(f"Loaded embedding model: {self.model_name}")

    def encode(
        self, texts: Union[str, List[str]], normalize: bool = True
    ) -> np.ndarray:
        """
        Encode texts into embeddings.

        Args:
            texts: Single text or list of texts
            normalize: Whether to L2-normalize embeddings

        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if self.model is None:
            self.load_model()

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts, normalize_embeddings=normalize, show_progress_bar=len(texts) > 100
        )

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return settings.EMBEDDING_DIMENSION


embedding_service = EmbeddingService()
