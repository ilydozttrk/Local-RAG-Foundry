from typing import Sequence, TypedDict

from app.database_manager import get_chunks_with_embeddings
from app.query_embedding import MODEL_ALIAS, QueryEmbedder
from app.similarity import cosine_similarity


# Enable only when detailed retrieval diagnostics are required.
DEBUG_RETRIEVAL = False


class RetrievalResult(TypedDict):
    """Represent a ranked semantic retrieval result."""

    chunk_id: int
    document_id: int
    chunk_index: int
    filename: str
    file_type: str
    source_path: str
    content: str
    model_name: str
    similarity_score: float


def parse_embedding(vector_text: str) -> list[float]:
    """Convert a comma-separated embedding string into a float list."""

    if not isinstance(vector_text, str):
        raise TypeError("vector_text must be a string.")

    cleaned_vector = vector_text.strip()

    if not cleaned_vector:
        raise ValueError("Embedding vector cannot be empty.")

    try:
        return [
            float(value.strip())
            for value in cleaned_vector.split(",")
        ]
    except ValueError as error:
        raise ValueError(
            "Embedding vector contains an invalid numeric value."
        ) from error


def validate_document_ids(
    document_ids: Sequence[int] | None,
) -> list[int] | None:
    """Validate and normalize document IDs used for retrieval."""

    if document_ids is None:
        return None

    if isinstance(document_ids, (str, bytes)):
        raise TypeError(
            "document_ids must be a sequence of integers."
        )

    try:
        normalized_document_ids = list(document_ids)
    except TypeError as error:
        raise TypeError(
            "document_ids must be a sequence of integers."
        ) from error

    if not normalized_document_ids:
        return []

    if any(
        not isinstance(document_id, int)
        or isinstance(document_id, bool)
        or document_id <= 0
        for document_id in normalized_document_ids
    ):
        raise ValueError(
            "document_ids must contain positive integers."
        )

    return list(dict.fromkeys(normalized_document_ids))


def print_retrieval_debug_header(
    query: str,
    document_ids: list[int] | None,
    threshold: float,
    candidate_count: int,
) -> None:
    """Print diagnostic information before candidate evaluation."""

    print("\n" + "=" * 80)
    print("RETRIEVAL DEBUG")
    print("=" * 80)
    print(f"Query                 : {query}")
    print(f"Selected document IDs : {document_ids}")
    print(f"Embedding model       : {MODEL_ALIAS}")
    print(f"Similarity threshold  : {threshold:.4f}")
    print(f"Candidate chunks      : {candidate_count}")
    print("-" * 80)


def print_candidate_debug(
    filename: str,
    document_id: int,
    chunk_id: int,
    chunk_index: int,
    similarity_score: float,
    threshold: float,
) -> None:
    """Print the score and filtering status of one candidate chunk."""

    status = (
        "ACCEPTED"
        if similarity_score >= threshold
        else "FILTERED OUT"
    )

    print(
        f"Filename: {filename}\n"
        f"Document ID: {document_id}\n"
        f"Chunk ID: {chunk_id}\n"
        f"Chunk Index: {chunk_index}\n"
        f"Similarity Score: {similarity_score:.4f} "
        f"({similarity_score * 100:.2f}%)\n"
        f"Status: {status}\n"
        f"{'-' * 80}"
    )


def build_retrieval_result(
    row,
    similarity_score: float,
) -> RetrievalResult:
    """Build a normalized retrieval result from a database row."""

    return {
        "chunk_id": int(row["chunk_id"]),
        "document_id": int(row["document_id"]),
        "chunk_index": int(row["chunk_index"]),
        "filename": str(row["filename"]),
        "file_type": str(row["file_type"]),
        "source_path": str(row["source_path"]),
        "content": str(row["content"]),
        "model_name": str(row["model_name"]),
        "similarity_score": similarity_score,
    }


def retrieve_top_k(
    query: str,
    top_k: int = 3,
    document_ids: Sequence[int] | None = None,
    min_similarity_score: float = 0.50,
) -> list[RetrievalResult]:
    """
    Retrieve the most semantically similar chunks for a query.

    Results below min_similarity_score are excluded.

    When document_ids is supplied, retrieval is restricted to chunks
    belonging to the selected active documents.
    """

    if not isinstance(query, str):
        raise TypeError("Query must be a string.")

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("Query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if (
        not isinstance(min_similarity_score, (int, float))
        or isinstance(min_similarity_score, bool)
    ):
        raise TypeError(
            "min_similarity_score must be a numeric value."
        )

    normalized_minimum_score = float(min_similarity_score)

    if not -1.0 <= normalized_minimum_score <= 1.0:
        raise ValueError(
            "min_similarity_score must be between -1.0 and 1.0."
        )

    cleaned_document_ids = validate_document_ids(
        document_ids
    )

    if cleaned_document_ids == []:
        if DEBUG_RETRIEVAL:
            print(
                "\n[RETRIEVAL DEBUG] "
                "No document was selected."
            )

        return []

    rows = get_chunks_with_embeddings(
        model_name=MODEL_ALIAS,
        document_ids=cleaned_document_ids,
    )

    if not rows:
        if DEBUG_RETRIEVAL:
            print(
                "\n[RETRIEVAL DEBUG] No indexed chunks were found "
                "for the selected documents."
            )

        return []

    if DEBUG_RETRIEVAL:
        print_retrieval_debug_header(
            query=cleaned_query,
            document_ids=cleaned_document_ids,
            threshold=normalized_minimum_score,
            candidate_count=len(rows),
        )

    embedder = QueryEmbedder()

    try:
        query_embedding = embedder.generate_embedding(
            cleaned_query
        )
    finally:
        embedder.unload()

    results: list[RetrievalResult] = []

    for row in rows:
        chunk_embedding = parse_embedding(
            row["vector"]
        )

        if len(query_embedding) != len(chunk_embedding):
            raise ValueError(
                "Embedding dimension mismatch for chunk "
                f"{row['chunk_id']}: "
                f"query={len(query_embedding)}, "
                f"chunk={len(chunk_embedding)}"
            )

        similarity_score = cosine_similarity(
            query_embedding,
            chunk_embedding,
        )

        if DEBUG_RETRIEVAL:
            print_candidate_debug(
                filename=str(row["filename"]),
                document_id=int(row["document_id"]),
                chunk_id=int(row["chunk_id"]),
                chunk_index=int(row["chunk_index"]),
                similarity_score=similarity_score,
                threshold=normalized_minimum_score,
            )

        if similarity_score < normalized_minimum_score:
            continue

        results.append(
            build_retrieval_result(
                row=row,
                similarity_score=similarity_score,
            )
        )

    results.sort(
        key=lambda result: result["similarity_score"],
        reverse=True,
    )

    final_results = results[:top_k]

    if DEBUG_RETRIEVAL:
        print(
            f"Accepted candidates   : {len(results)}\n"
            f"Returned results      : {len(final_results)}"
        )
        print("=" * 80 + "\n")

    return final_results


def main() -> None:
    """Run a standalone multilingual retrieval smoke test."""

    query = "Python hangi alanlarda kullanılır?"
    top_k = 3
    min_similarity_score = 0.33

    # Set this to a currently active document ID before running
    # retrieval.py directly.
    document_ids: list[int] | None = None

    results = retrieve_top_k(
        query=query,
        top_k=top_k,
        document_ids=document_ids,
        min_similarity_score=min_similarity_score,
    )

    print(f"Query: {query}")
    print(f"Selected document IDs: {document_ids}")
    print(f"Top K: {top_k}")
    print(
        "Minimum similarity score: "
        f"{min_similarity_score:.2f}"
    )
    print(f"Retrieved results: {len(results)}")

    if not results:
        print(
            "No sufficiently relevant chunks were found in "
            "the selected documents."
        )
        return

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\nRank: {rank}\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Document ID: {result['document_id']}\n"
            f"Filename: {result['filename']}\n"
            f"File Type: {result['file_type']}\n"
            f"Source Path: {result['source_path']}\n"
            f"Chunk Index: {result['chunk_index']}\n"
            f"Model: {result['model_name']}\n"
            f"Similarity Score: "
            f"{result['similarity_score']:.4f}\n"
            f"Content: {result['content']}"
        )


if __name__ == "__main__":
    main()