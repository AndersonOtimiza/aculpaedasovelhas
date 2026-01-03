"""
Script to build FAISS index from Bible API data.

Usage:
    cd #exeg.ai
    python -m scripts.build_faiss_index
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def main():
    print("=" * 60)
    print("Building FAISS index from Bible API")
    print("=" * 60)

    from src.services.bible_api_client import bible_api_client
    from src.services.embedding_service import embedding_service
    from src.services.faiss_service import faiss_service

    # Load embedding model
    print("\n[1/4] Loading embedding model...")
    embedding_service.load_model()

    # Fetch all verses from Bible API
    print("\n[2/4] Fetching verses from Bible API...")
    try:
        verses = await bible_api_client.get_all_verses_for_embedding()
        print(f"  Fetched {len(verses)} verses")
    except Exception as e:
        print(f"\nERROR: Could not connect to Bible API")
        print(f"  Make sure the Bible API is running on port 3001")
        print(f"  Error: {e}")
        return

    if not verses:
        print("\nNo verses found. Make sure Bible API is running and has data.")
        return

    # Filter out empty texts
    verses = [v for v in verses if v.get("text", "").strip()]
    print(f"  Filtered to {len(verses)} verses with text")

    # Generate embeddings
    print("\n[3/4] Generating embeddings...")
    texts = [v.get("text", "") for v in verses]
    embeddings = embedding_service.encode(texts)
    print(f"  Generated embeddings with shape: {embeddings.shape}")

    # Build and save index
    print("\n[4/4] Building FAISS index...")
    faiss_service.build_index(embeddings, verses)

    print("\n" + "=" * 60)
    print("Done! FAISS index saved to:")
    print(f"  Index: {faiss_service.index_path}")
    print(f"  Metadata: {faiss_service.metadata_path}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
