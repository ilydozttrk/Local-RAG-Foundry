from app.prompt_builder import PromptBuilder
from app.retrieval import RetrievalResult, retrieve_top_k


def build_context(
    results: list[RetrievalResult],
) -> str:
    """Build a structured context string from retrieved chunks."""

    if not isinstance(results, list):
        raise TypeError(
            "results must be a list of retrieval results."
        )

    if not results:
        return ""

    context_parts: list[str] = []

    for source_number, result in enumerate(
        results,
        start=1,
    ):
        content = result["content"].strip()

        if not content:
            continue

        context_parts.append(
            f"<SOURCE_{source_number}>\n"
            f"Document ID: {result['document_id']}\n"
            f"Filename: {result['filename']}\n"
            f"File Type: {result['file_type']}\n"
            f"Source Path: {result['source_path']}\n"
            f"Chunk Index: {result['chunk_index']}\n"
            f"Similarity Score: "
            f"{result['similarity_score']:.4f}\n"
            f"Content:\n"
            f"{content}\n"
            f"</SOURCE_{source_number}>"
        )

    return "\n\n".join(context_parts)


def main() -> None:
    """Run a standalone context builder smoke test."""

    question = "What is SQLite?"

    # Replace this value with an active document ID
    # available in the local database.
    document_ids = [1]

    results = retrieve_top_k(
        query=question,
        top_k=3,
        document_ids=document_ids,
        min_similarity_score=0.50,
    )

    print("=" * 80)
    print("RETRIEVED RESULTS")
    print("=" * 80)

    if not results:
        print(
            "No sufficiently relevant chunks were retrieved."
        )
        return

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"{index}. "
            f"Score: {result['similarity_score']:.4f} | "
            f"Document ID: {result['document_id']} | "
            f"Chunk ID: {result['chunk_id']} | "
            f"Chunk Index: {result['chunk_index']}"
        )

    context = build_context(results)

    if not context:
        print(
            "Retrieved chunks did not contain usable content."
        )
        return

    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build_prompt(
        question=question,
        context=context,
    )

    print()
    print("=" * 80)
    print("BUILT CONTEXT")
    print("=" * 80)
    print(context)

    print()
    print("=" * 80)
    print("FINAL PROMPT")
    print("=" * 80)
    print(prompt)


if __name__ == "__main__":
    main()