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

    def __init__(
        self,
        system_instruction: str | None = None,
    ) -> None:

        if system_instruction is not None:
            cleaned_instruction = system_instruction.strip()

            if not cleaned_instruction:
                raise ValueError(
                    "system_instruction cannot be empty."
                )

            self.system_instruction = cleaned_instruction

        else:
            self.system_instruction = (
                self.DEFAULT_SYSTEM_INSTRUCTION
            )

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """Build the final RAG prompt."""

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

        question_lower = cleaned_question.casefold()

        turkish_keywords = (
            " nedir",
            " nasıl",
            " neden",
            " niçin",
            " hangi",
            " kim",
            " nerede",
            " ne zaman",
            " kaç",
            " mı",
            " mi",
            " mu",
            " mü",
            "ç",
            "ğ",
            "ı",
            "ö",
            "ş",
            "ü",
        )

        is_turkish = any(
            keyword in question_lower
            for keyword in turkish_keywords
        )

        response_language = (
            "Turkish"
            if is_turkish
            else "English"
        )

        return (
            f"{self.system_instruction}\n\n"

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
            "Answer the QUESTION using ONLY the CONTEXT.\n"
            "Translate the supported information into the RESPONSE LANGUAGE.\n"
            "Write the complete answer only in the RESPONSE LANGUAGE.\n"
            "Translate ordinary words.\n"
            "Keep only proper names and programming language names unchanged.\n"
            "Return only the final answer."
        )


def main() -> None:
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