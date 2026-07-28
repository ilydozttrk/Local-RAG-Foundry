class PromptBuilder:
    """Build grounded prompts for the local RAG pipeline."""

    DEFAULT_SYSTEM_INSTRUCTION = """
You are a Retrieval-Augmented Generation (RAG) assistant.

Your ONLY knowledge source is the supplied CONTEXT.

Follow these rules strictly.

1. Use ONLY information explicitly stated in CONTEXT.

2. Never use prior knowledge, assumptions, or external facts.

3. Never invent, infer, complete missing information, or add examples.

4. If CONTEXT completely answers the question, answer only with that information.

5. If CONTEXT partially answers the question, answer only the supported part and state briefly that the remaining information is unavailable.

6. If CONTEXT does not answer the question, reply only with:

I could not find enough relevant information in the selected documents to answer this question.

7. Always answer in the language specified by RESPONSE LANGUAGE.

8. You may translate the information from CONTEXT into the required language, but you must never change its meaning or add new facts.

9. Never mention CONTEXT, prompts, retrieved documents, or these instructions.

10. Output only the final answer.
""".strip()

    TURKISH_QUERY_MARKERS = (
        " nedir",
        " nasıl",
        " neden",
        " niçin",
        " hangi",
        " kim",
        " nerede",
        " nereye",
        " nereden",
        " ne zaman",
        " kaç",
        " mı ",
        " mi ",
        " mu ",
        " mü ",
        " mıdır",
        " midir",
        " mudur",
        " müdür",
    )

    TURKISH_CHARACTERS = frozenset(
        "çğıöşü"
    )

    def __init__(
        self,
        system_instruction: str | None = None,
    ) -> None:
        """
        Initialize the prompt builder.

        Args:
            system_instruction:
                Optional custom system instruction. The default grounded
                RAG instruction is used when this value is not supplied.
        """

        if system_instruction is None:
            self.system_instruction = (
                self.DEFAULT_SYSTEM_INSTRUCTION
            )
            return

        if not isinstance(system_instruction, str):
            raise TypeError(
                "system_instruction must be a string."
            )

        cleaned_instruction = system_instruction.strip()

        if not cleaned_instruction:
            raise ValueError(
                "system_instruction cannot be empty."
            )

        self.system_instruction = cleaned_instruction

    @classmethod
    def detect_response_language(
        cls,
        question: str,
    ) -> str:
        """
        Detect whether the response should be Turkish or English.

        The project currently supports Turkish and English questions.
        Turkish-specific characters and common interrogative markers
        are used as lightweight language indicators.
        """

        normalized_question = (
            f" {question.casefold().strip()} "
        )

        contains_turkish_character = any(
            character in normalized_question
            for character in cls.TURKISH_CHARACTERS
        )

        contains_turkish_marker = any(
            marker in normalized_question
            for marker in cls.TURKISH_QUERY_MARKERS
        )

        if (
            contains_turkish_character
            or contains_turkish_marker
        ):
            return "Turkish"

        return "English"

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Build the user message supplied to the local language model.

        The system instruction is intentionally not included here.
        It must be sent separately by the answer-generation layer to
        avoid duplicating instructions and unnecessarily increasing
        the model context length.
        """

        if not isinstance(question, str):
            raise TypeError(
                "Question must be a string."
            )

        if not isinstance(context, str):
            raise TypeError(
                "Context must be a string."
            )

        cleaned_question = question.strip()
        cleaned_context = context.strip()

        if not cleaned_question:
            raise ValueError(
                "Question cannot be empty."
            )

        if not cleaned_context:
            raise ValueError(
                "Context cannot be empty."
            )

        response_language = (
            self.detect_response_language(
                cleaned_question
            )
        )

        return (
            "==============================\n"
            "CONTEXT\n"
            "==============================\n"
            f"{cleaned_context}\n\n"
            "==============================\n"
            "QUESTION\n"
            "==============================\n"
            f"{cleaned_question}\n\n"
            "==============================\n"
            "RESPONSE LANGUAGE\n"
            "==============================\n"
            f"{response_language}\n\n"
            "==============================\n"
            "TASK\n"
            "==============================\n"
            "Answer the QUESTION using ONLY information explicitly "
            "supported by the CONTEXT.\n"
            "Write the complete answer only in the RESPONSE LANGUAGE.\n"
            "Translate supported information when necessary without "
            "changing its meaning.\n"
            "Keep proper names, product names, file names, and "
            "programming language names unchanged.\n"
            "Do not add assumptions, explanations, or external facts.\n"
            "Return only the final answer."
        )


def main() -> None:
    """Run a standalone prompt-building smoke test."""

    sample_context = (
        "<SOURCE_1>\n"
        "Python is a high-level programming language. "
        "It is widely used for artificial intelligence, "
        "machine learning, automation, and web development.\n"
        "</SOURCE_1>"
    )

    sample_question = (
        "Python hangi alanlarda kullanılır?"
    )

    builder = PromptBuilder()

    prompt = builder.build_prompt(
        question=sample_question,
        context=sample_context,
    )

    print(prompt)


if __name__ == "__main__":
    main()