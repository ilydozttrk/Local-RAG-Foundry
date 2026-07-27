
"""
Legacy utility.

Embeddings are now generated automatically during
document ingestion.

This script is kept only for maintenance tasks such as:

- rebuilding embeddings
- regenerating embeddings after changing the embedding model
- debugging

It is not part of the normal ingestion pipeline.
"""

from app.database_manager import get_chunks, insert_embedding
from app.query_embedding import MODEL_ALIAS, QueryEmbedder


def main() -> None:
    """Generate and store embeddings for database chunks."""

    chunks = get_chunks()

    if not chunks:
        print("No chunks found in the database.")
        return

    embedder = QueryEmbedder()

    try:
        for chunk in chunks:
            content = chunk["content"]

            embedding = embedder.generate_embedding(content)

            embedding_id = insert_embedding(
                chunk_id=chunk["id"],
                model_name=MODEL_ALIAS,
                embedding_vector=embedding,
            )

            print(
                f"Chunk ID: {chunk['id']} | "
                f"Embedding ID: {embedding_id} | "
                f"Dimensions: {len(embedding)}"
            )

    finally:
        embedder.unload()

    print("Chunk embeddings generated successfully.")


if __name__ == "__main__":
    main()