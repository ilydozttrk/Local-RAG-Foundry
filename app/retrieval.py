from typing import TypedDict

from app.database_manager import get_chunks_with_embeddings
from app.query_embedding import MODEL_ALIAS, QueryEmbedder
from app.similarity import cosine_similarity


class RetrievalResult(TypedDict):
    """
    Represent a ranked retrieval result.
    """

    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    model_name: str
    similarity_score: float


def parse_embedding(vector_text: str) -> list[float]:
    """
    Convert a comma-separated embedding string into a float list.
    """

    if not vector_text.strip():
        raise ValueError("Embedding vector cannot be empty.")

    try:
        return [
            float(value.strip())
            for value in vector_text.split(",")
        ]
    except ValueError as error:
        raise ValueError(
            "Embedding vector contains an invalid numeric value."
        ) from error


def retrieve_top_k(
    query: str,
    top_k: int = 3,
) -> list[RetrievalResult]:
    """
    Retrieve the most semantically similar chunks for a query.
    """

    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(top_k, int):
        raise TypeError("top_k must be an integer.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    rows = get_chunks_with_embeddings(MODEL_ALIAS)

    if not rows:
        return []

    embedder = QueryEmbedder()

    try:
        query_embedding = embedder.generate_embedding(query)
    finally:
        embedder.unload()

    results: list[RetrievalResult] = []

    for row in rows:
        chunk_embedding = parse_embedding(row["vector"])

        if len(query_embedding) != len(chunk_embedding):
            raise ValueError(
                f"Embedding dimension mismatch for chunk "
                f"{row['chunk_id']}: "
                f"query={len(query_embedding)}, "
                f"chunk={len(chunk_embedding)}"
            )

        similarity_score = cosine_similarity(
            query_embedding,
            chunk_embedding,
        )

        results.append(
            {
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "chunk_index": row["chunk_index"],
                "content": row["content"],
                "model_name": row["model_name"],
                "similarity_score": similarity_score,
            }
        )

    ranked_results = sorted(
        results,
        key=lambda result: result["similarity_score"],
        reverse=True,
    )

    return ranked_results[:top_k]


def main() -> None:
    """
    Test the retrieval pipeline.
    """

    query = "What does the sample document contain?"
    top_k = 3

    results = retrieve_top_k(
        query=query,
        top_k=top_k,
    )

    print(f"Query: {query}")
    print(f"Retrieved results: {len(results)}")

    if not results:
        print("No matching chunks were found.")
        return

    for rank, result in enumerate(results, start=1):
        print(
            f"\nRank: {rank}\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Document ID: {result['document_id']}\n"
            f"Chunk Index: {result['chunk_index']}\n"
            f"Model: {result['model_name']}\n"
            f"Similarity Score: "
            f"{result['similarity_score']:.4f}\n"
            f"Content: {result['content']}"
        )


if __name__ == "__main__":
    main()