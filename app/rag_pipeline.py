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
        min_similarity_score: float = 0.33,
    ) -> None:
        self.top_k = self._validate_top_k(top_k)
        self.min_similarity_score = (
            self._validate_min_similarity_score(
                min_similarity_score
            )
        )

        self.prompt_builder = PromptBuilder()
        self.answer_generator = AnswerGenerator()
        self._closed = False

    @staticmethod
    def _validate_top_k(top_k: int) -> int:
        """Validate and normalize the retrieval result limit."""

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
        ):
            raise TypeError(
                "top_k must be an integer."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        return top_k

    @staticmethod
    def _validate_min_similarity_score(
        min_similarity_score: float,
    ) -> float:
        """Validate and normalize the minimum similarity score."""

        if (
            not isinstance(
                min_similarity_score,
                (int, float),
            )
            or isinstance(min_similarity_score, bool)
        ):
            raise TypeError(
                "min_similarity_score must be numeric."
            )

        normalized_score = float(
            min_similarity_score
        )

        if not -1.0 <= normalized_score <= 1.0:
            raise ValueError(
                "min_similarity_score must be between "
                "-1.0 and 1.0."
            )

        return normalized_score

    @staticmethod
    def _validate_question(question: str) -> str:
        """Validate and normalize a user question."""

        if not isinstance(question, str):
            raise TypeError(
                "Question must be a string."
            )

        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError(
                "Question cannot be empty."
            )

        return cleaned_question

    @staticmethod
    def _validate_document_ids(
        document_ids: list[int],
    ) -> list[int]:
        """Validate, deduplicate, and normalize document IDs."""

        if not isinstance(document_ids, list):
            raise TypeError(
                "document_ids must be a list of integers."
            )

        if not document_ids:
            raise ValueError(
                "At least one document must be selected."
            )

        if any(
            not isinstance(document_id, int)
            or isinstance(document_id, bool)
            or document_id <= 0
            for document_id in document_ids
        ):
            raise ValueError(
                "Every document ID must be a positive integer."
            )

        return list(
            dict.fromkeys(document_ids)
        )

    def _build_no_results_answer(
        self,
        question: str,
    ) -> str:
        """
        Build a language-aware answer when no usable context exists.

        Language detection is delegated to PromptBuilder so that prompt
        generation and fallback responses use the same detection logic.
        """

        response_language = (
            self.prompt_builder.detect_response_language(
                question
            )
        )

        if response_language == "Turkish":
            return (
                "Seçili belgelerde bu soruyu güvenilir şekilde "
                "yanıtlamak için yeterince ilgili bilgi bulamadım."
            )

        return (
            "I could not find sufficiently relevant information "
            "in the selected documents to answer this question "
            "reliably."
        )

    def _build_empty_response(
        self,
        question: str,
    ) -> RAGResponse:
        """Build a response when retrieval yields no usable context."""

        return {
            "question": question,
            "answer": self._build_no_results_answer(
                question
            ),
            "sources": [],
        }

    def ask(
        self,
        question: str,
        document_ids: list[int],
    ) -> RAGResponse:
        """Answer a question using the selected document context."""

        if self._closed:
            raise RuntimeError(
                "The RAG pipeline has already been closed."
            )

        cleaned_question = self._validate_question(
            question
        )

        unique_document_ids = (
            self._validate_document_ids(
                document_ids
            )
        )

        results = retrieve_top_k(
            query=cleaned_question,
            top_k=self.top_k,
            document_ids=unique_document_ids,
            min_similarity_score=self.min_similarity_score,
        )

        if not results:
            return self._build_empty_response(
                cleaned_question
            )

        context = build_context(results)

        if not context:
            return self._build_empty_response(
                cleaned_question
            )

        prompt = self.prompt_builder.build_prompt(
            question=cleaned_question,
            context=context,
        )

        answer = self.answer_generator.generate_answer(
            prompt=prompt,
            system_instruction=(
                self.prompt_builder.system_instruction
            ),
        )

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
        """Return the active pipeline instance."""

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """Release pipeline resources when leaving a context block."""

        self.close()


def main() -> None:
    """Run a standalone RAG pipeline smoke test."""

    question = "Python hangi alanlarda kullanılır?"

    # Replace this value with an active document ID
    # available in the local database.
    document_ids = [1]

    with RAGPipeline(
        top_k=3,
        min_similarity_score=0.33,
    ) as pipeline:
        response = pipeline.ask(
            question=question,
            document_ids=document_ids,
        )

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

    for index, source in enumerate(
        response["sources"],
        start=1,
    ):
        print(
            f"{index}. "
            f"Document ID: {source['document_id']} | "
            f"Chunk ID: {source['chunk_id']} | "
            f"Filename: {source['filename']} | "
            f"Score: {source['similarity_score']:.4f}"
        )


if __name__ == "__main__":
    main()