from app.answer_generator import AnswerGenerator
from app.context_builder import build_context
from app.prompt_builder import PromptBuilder
from app.retrieval import retrieve_top_k


def main() -> None:
    """Run the complete Local RAG pipeline."""

    question = input("Ask a question: ").strip()

    if not question:
        print("Question cannot be empty.")
        return

    results = retrieve_top_k(
        query=question,
        top_k=3,
    )

    if not results:
        print("No relevant documents were found.")
        return

    context = build_context(results)

    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build_prompt(
        question=question,
        context=context,
    )

    generator = AnswerGenerator()

    try:
        answer = generator.generate_answer(prompt)

    finally:
        generator.close()

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()