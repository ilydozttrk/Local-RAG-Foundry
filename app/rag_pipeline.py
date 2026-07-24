from typing import TypedDict

from app.answer_generator import AnswerGenerator
from app.context_builder import build_context
from app.prompt_builder import PromptBuilder
from app.retrieval import RetrievalResult, retrieve_top_k


class RAGResponse(TypedDict):
    """Represent the complete result of a RAG pipeline request."""

    question: str
    answer: str
    sources: list[RetrievalResult]


class RAGPipeline:
    """Coordinate retrieval, context building, and answer generation."""

    def __init__(
        self,
        top_k: int = 3,
    ) -> None:
        if not isinstance(top_k, int):
            raise TypeError("top_k must be an integer.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self.top_k = top_k
        self.prompt_builder = PromptBuilder()
        self.answer_generator = AnswerGenerator()
        self._closed = False

    def ask(self, question: str) -> RAGResponse:
        """Answer a question using retrieved document context."""

        if self._closed:
            raise RuntimeError("The RAG pipeline has already been closed.")

        if not isinstance(question, str):
            raise TypeError("Question must be a string.")

        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError("Question cannot be empty.")

        results = retrieve_top_k(
            query=cleaned_question,
            top_k=self.top_k,
        )

        if not results:
            return {
                "question": cleaned_question,
                "answer": (
                    "No relevant information was found in the "
                    "available documents."
                ),
                "sources": [],
            }

        context = build_context(results)

        prompt = self.prompt_builder.build_prompt(
            question=cleaned_question,
            context=context,
        )

        answer = self.answer_generator.generate_answer(prompt)

        return {
            "question": cleaned_question,
            "answer": answer,
            "sources": results,
        }

    def close(self) -> None:
        """Release the resources used by the pipeline."""

        if self._closed:
            return

        self.answer_generator.close()
        self._closed = True

    def __enter__(self) -> "RAGPipeline":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def main() -> None:
    """Run a standalone RAG pipeline smoke test."""

    question = "What is SQLite?"

    with RAGPipeline(top_k=3) as pipeline:
        response = pipeline.ask(question)

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(response["question"])

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(response["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    if not response["sources"]:
        print("No sources were retrieved.")
        return

    for index, source in enumerate(response["sources"], start=1):
        print(
            f"{index}. "
            f"Document ID: {source['document_id']} | "
            f"Chunk ID: {source['chunk_id']} | "
            f"Score: {source['similarity_score']:.4f}"
        )


if __name__ == "__main__":
    main()