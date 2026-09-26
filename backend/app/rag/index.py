"""
KAVACH RAG Index CLI & Utility
Builds or refreshes the local security knowledge vector index.
Usage:
  python -m backend.app.rag.index
"""

import sys
import asyncio
import logging
from backend.app.rag.retriever import rag_retriever
from backend.app.rag.vector_store import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kavach.rag.indexer")


async def main():
    print("=" * 60)
    print("KAVACH SECURITY INTELLIGENCE — RAG INDEX BUILDER")
    print("=" * 60)
    print("Loading security documents from Knowledge Engine...")

    stats = await rag_retriever.rebuild_index()

    print("\n--- Indexing Complete ---")
    print(f"Documents Indexed : {stats['documents_indexed']}")
    print(f"Chunks Created    : {stats['chunks_created']}")
    print(f"Embedding Model   : {stats['embedding_model']}")
    print(f"Retrieval Mode    : {stats['retrieval_mode']}")
    print(f"Vector Store Dir  : {stats['vector_store']['storage_dir']}")
    print(f"Engine Type       : {stats['vector_store']['engine']}")
    print(f"Vector Dimension  : {stats['vector_store']['vector_dimension']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
