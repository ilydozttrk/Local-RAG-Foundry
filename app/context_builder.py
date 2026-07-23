from app.prompt_builder import PromptBuilder
from app.retrieval import RetrievalResult, retrieve_top_k


def build_context(results: list[RetrievalResult]) -> str:
    """Build a formatted context string from retrieved chunks."""

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"[Document {index}]\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Similarity Score: {result['similarity_score']:.4f}\n"
            f"Content:\n"
            f"{result['content'].strip()}"
        )

    return "\n\n".join(context_parts)


def main() -> None:
    """Run a standalone context builder smoke test."""

    question = "What is SQLite?"

    results = retrieve_top_k(
        query=question,
        top_k=3,
    )

    print("=" * 80)
    print("RETRIEVED RESULTS")
    print("=" * 80)

    if not results:
        print("No relevant chunks were retrieved.")
        return

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"Score: {result['similarity_score']:.4f} | "
            f"Chunk ID: {result['chunk_id']}"
        )

    context = build_context(results)

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