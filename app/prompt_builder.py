class PromptBuilder:
    """Build grounded prompts for the local RAG pipeline."""

    DEFAULT_SYSTEM_INSTRUCTION = (
        "You are a helpful AI assistant. "
        "Answer the user's question using only the provided context. "
        "If the answer cannot be found in the context, clearly state that "
        "the available information is insufficient."
    )

    def __init__(
        self,
        system_instruction: str | None = None,
    ) -> None:
        self.system_instruction = (
            system_instruction.strip()
            if system_instruction
            else self.DEFAULT_SYSTEM_INSTRUCTION
        )

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """Return a structured prompt containing context and question."""

        cleaned_question = question.strip()
        cleaned_context = context.strip()

        if not cleaned_question:
            raise ValueError("Question cannot be empty.")

        if not cleaned_context:
            raise ValueError("Context cannot be empty.")

        return (
            f"{self.system_instruction}\n\n"
            "--------------------\n"
            "CONTEXT\n"
            "--------------------\n"
            f"{cleaned_context}\n\n"
            "--------------------\n"
            "QUESTION\n"
            "--------------------\n"
            f"{cleaned_question}\n\n"
            "--------------------\n"
            "ANSWER\n"
            "--------------------"
        )


def main() -> None:
    """Run a standalone prompt builder smoke test."""

    sample_context = (
        "Retrieval-Augmented Generation retrieves relevant information "
        "before sending a prompt to a language model."
    )

    sample_question = "What does Retrieval-Augmented Generation do?"

    builder = PromptBuilder()

    prompt = builder.build_prompt(
        question=sample_question,
        context=sample_context,
    )

    print(prompt)


if __name__ == "__main__":
    main()