import re

from app.foundry_manager import get_foundry_manager


MODEL_ALIAS = "phi-4-mini"

# Temporary diagnostic switch.
# Set this to False after prompt-flow debugging is complete.
DEBUG_GENERATION_MESSAGES = True


class AnswerGenerator:
    """Generate grounded answers through Foundry Local."""

    def __init__(
        self,
        model_alias: str = MODEL_ALIAS,
    ) -> None:
        if not isinstance(model_alias, str):
            raise TypeError(
                "model_alias must be a string."
            )

        cleaned_model_alias = model_alias.strip()

        if not cleaned_model_alias:
            raise ValueError(
                "model_alias cannot be empty."
            )

        self.model_alias = cleaned_model_alias
        self.model = None
        self.client = None

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize and load the selected chat model."""

        print("Initializing Foundry Local SDK...")

        manager = get_foundry_manager()

        print(f"Selecting model: {self.model_alias}")

        self.model = manager.catalog.get_model(
            self.model_alias
        )

        if self.model is None:
            raise RuntimeError(
                "Model alias could not be found in the SDK catalog: "
                f"{self.model_alias}"
            )

        print(
            f"Resolved model variant: {self.model.id}"
        )
        print("Downloading model if necessary...")

        self.model.download(
            self._show_download_progress
        )

        print("\nModel download completed.")
        print("Loading model...")

        self.model.load()

        self.client = self.model.get_chat_client()

        print("Model loaded successfully.")

    @staticmethod
    def _show_download_progress(
        progress: float,
    ) -> None:
        """Display model download progress."""

        print(
            f"\rDownload progress: {progress:6.2f}%",
            end="",
            flush=True,
        )

    @staticmethod
    def _validate_message(
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a chat message."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                f"{field_name} cannot be empty."
            )

        return cleaned_value

    @staticmethod
    def _clean_generated_answer(
        answer: str,
    ) -> str:
        """
        Remove common generation artifacts without changing content.

        Small local models occasionally emit closing XML-like tags even
        when those tags are not part of the requested response.
        """

        cleaned_answer = answer.strip()

        artifact_patterns = (
            r"</ANSWER>",
            r"</DECISION>",
            r"</sentence>",
            r"</response>",
        )

        for pattern in artifact_patterns:
            cleaned_answer = re.sub(
                pattern,
                "",
                cleaned_answer,
                flags=re.IGNORECASE,
            )

        cleaned_answer = re.sub(
            r"\n{3,}",
            "\n\n",
            cleaned_answer,
        )

        return cleaned_answer.strip()

    @staticmethod
    def _print_generation_debug(
        system_instruction: str,
        prompt: str,
    ) -> None:
        """Print the exact messages sent to the chat model."""

        print("\n" + "=" * 80)
        print("GENERATION DEBUG")
        print("=" * 80)

        print("\nSYSTEM MESSAGE")
        print("-" * 80)
        print(system_instruction)

        print("\nUSER MESSAGE")
        print("-" * 80)
        print(prompt)

        print("\n" + "=" * 80)

    def generate_answer(
        self,
        prompt: str,
        system_instruction: str,
    ) -> str:
        """
        Generate an answer using separate system and user messages.

        The system instruction defines grounding rules, while the user
        message contains only the retrieved context and question.
        """

        cleaned_prompt = self._validate_message(
            prompt,
            "Prompt",
        )

        cleaned_system_instruction = (
            self._validate_message(
                system_instruction,
                "System instruction",
            )
        )

        if self.client is None:
            raise RuntimeError(
                "The chat client has not been initialized."
            )

        if DEBUG_GENERATION_MESSAGES:
            self._print_generation_debug(
                system_instruction=cleaned_system_instruction,
                prompt=cleaned_prompt,
            )

        messages = [
            {
                "role": "system",
                "content": cleaned_system_instruction,
            },
            {
                "role": "user",
                "content": cleaned_prompt,
            },
        ]

        answer_parts: list[str] = []

        try:
            for chunk in self.client.complete_streaming_chat(
                messages
            ):
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta is None:
                    continue

                content = delta.content

                if content:
                    answer_parts.append(content)

        except Exception as exc:
            raise RuntimeError(
                f"Answer generation failed: {exc}"
            ) from exc

        raw_answer = "".join(answer_parts)

        if DEBUG_GENERATION_MESSAGES:
            print("\nRAW MODEL RESPONSE")
            print("-" * 80)
            print(raw_answer)
            print("=" * 80 + "\n")

        answer = self._clean_generated_answer(
            raw_answer
        )

        if not answer:
            raise RuntimeError(
                "The model returned an empty response."
            )

        return answer

    def close(self) -> None:
        """Unload the local model."""

        if self.model is None:
            return

        print("Unloading model...")

        self.model.unload()

        self.model = None
        self.client = None

        print("Model unloaded successfully.")

    def __enter__(self) -> "AnswerGenerator":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()


def main() -> None:
    """Run a standalone grounded-generation smoke test."""

    system_instruction = """
You are a strictly grounded RAG assistant.

Use only information explicitly stated in the supplied context.
Do not use prior knowledge.
Do not infer, invent, expand, or add examples.
Answer in the same language as the question.
""".strip()

    prompt = """
CONTEXT

Python is a high-level programming language. It is widely used for
artificial intelligence, machine learning, automation, and web development.

QUESTION

Python hangi alanlarda kullanılır?

Write only the final answer.
""".strip()

    with AnswerGenerator() as generator:
        answer = generator.generate_answer(
            prompt=prompt,
            system_instruction=system_instruction,
        )

    print("\nGenerated answer:\n")
    print(answer)


if __name__ == "__main__":
    main()