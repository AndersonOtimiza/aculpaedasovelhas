"""
FAISS index management service.
"""
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path
from src.config.settings import settings


class FAISSService:
    """Service for FAISS semantic search."""

    def __init__(self):
        self.index = None
        self.index_path = Path(settings.FAISS_INDEX_PATH)
        self.metadata_path = self.index_path.with_suffix(".metadata.json")
        self.metadata: List[Dict[str, Any]] = []
        self._faiss = None

    def _get_faiss(self):
        """Lazy load FAISS module."""
        if self._faiss is None:
            if settings.USE_FAISS_GPU:
                try:
                    import faiss

                    # Check if GPU is available
                    if faiss.get_num_gpus() > 0:
                        print(f"FAISS GPU available: {faiss.get_num_gpus()} GPU(s)")
                    else:
                        print("No GPU detected, falling back to CPU FAISS")
                    self._faiss = faiss
                except ImportError:
                    import faiss

                    self._faiss = faiss
            else:
                import faiss

                self._faiss = faiss
        return self._faiss

    def load_index(self) -> bool:
        """Load existing FAISS index from disk."""
        faiss = self._get_faiss()

        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))

            # Move to GPU if available and configured
            if settings.USE_FAISS_GPU and faiss.get_num_gpus() > 0:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
                print("FAISS index moved to GPU")

            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            print(f"Loaded FAISS index with {self.index.ntotal} vectors")
            return True
        return False

    def build_index(
        self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Build and save FAISS index.

        Args:
            embeddings: numpy array of shape (n_verses, embedding_dim)
            metadata: List of dicts with verse info (id, reference, text, etc.)
        """
        faiss = self._get_faiss()
        dimension = embeddings.shape[1]

        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(dimension)

        # Add vectors
        self.index.add(embeddings.astype(np.float32))
        self.metadata = metadata

        # Save to disk (always save as CPU index)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))

        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        print(f"Built FAISS index with {self.index.ntotal} vectors")

        # Move to GPU after saving if configured
        if settings.USE_FAISS_GPU and faiss.get_num_gpus() > 0:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            print("FAISS index moved to GPU")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search for similar verses.

        Args:
            query_embedding: Query vector of shape (embedding_dim,)
            top_k: Number of results to return
            filter_fn: Optional function to filter results

        Returns:
            List of (metadata_dict, similarity_score) tuples
        """
        if self.index is None:
            raise ValueError("FAISS index not loaded. Call load_index() first.")

        # Reshape for FAISS
        query = query_embedding.reshape(1, -1).astype(np.float32)

        # Search (get more results if filtering)
        search_k = top_k * 3 if filter_fn else top_k
        scores, indices = self.index.search(query, min(search_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:  # FAISS returns -1 for unfilled slots
                continue

            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            if filter_fn and not filter_fn(meta):
                continue

            results.append((meta, float(score)))

            if len(results) >= top_k:
                break

        return results

    def is_loaded(self) -> bool:
        """Check if index is loaded."""
        return self.index is not None and len(self.metadata) > 0


faiss_service = FAISSService()
