from app.retrieval import RetrievalResult, retrieve_top_k


SYSTEM_PROMPT = (
    "You are a helpful AI assistant.\n"
    "Answer the user's question using only the provided context.\n"
    "If the answer cannot be found in the context, say that you do not know.\n"
)


def build_context(results: list[RetrievalResult]) -> str:
    """Build a context string from retrieved chunks."""

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"[Document {index}]\n"
            f"{result['content']}"
        )

    return "\n\n".join(context_parts)


def build_prompt(question: str, context: str) -> str:
    """Assemble the final prompt."""

    cleaned_question = question.strip()
    cleaned_context = context.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    if not cleaned_context:
        cleaned_context = "No relevant context was retrieved."

    return (
        f"{SYSTEM_PROMPT}\n"
        "Context:\n"
        "--------------------\n"
        f"{cleaned_context}\n"
        "--------------------\n\n"
        "Question:\n"
        f"{cleaned_question}\n\n"
        "Answer:"
    )


def main() -> None:
    """Run a local context builder test."""

    question = "What is SQLite?"

    results = retrieve_top_k(
        query=question,
        top_k=3,
    )

    print("=" * 80)
    print("RETRIEVED RESULTS")
    print("=" * 80)

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. "
            f"Score: {result['similarity_score']:.4f} | "
            f"Chunk ID: {result['chunk_id']}"
        )

    context = build_context(results)
    prompt = build_prompt(question, context)

    print()
    print("=" * 80)
    print("FINAL PROMPT")
    print("=" * 80)
    print(prompt)


if __name__ == "__main__":
    main()