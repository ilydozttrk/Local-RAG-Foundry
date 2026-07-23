from app.foundry_manager import get_foundry_manager

MODEL_ALIAS = "qwen2.5-0.5b"


class AnswerGenerator:
    """Generate answers with a local language model through Foundry Local."""

    def __init__(
        self,
        model_alias: str = MODEL_ALIAS,
    ) -> None:
        self.model_alias = model_alias
        self.model = None
        self.client = None

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize and load the selected chat model."""

        print("Initializing Foundry Local SDK...")

        manager = get_foundry_manager()

        print(f"Selecting model: {self.model_alias}")

        self.model = manager.catalog.get_model(self.model_alias)

        if self.model is None:
            raise RuntimeError(
                "Model alias could not be found in the SDK catalog: "
                f"{self.model_alias}"
            )

        print(f"Resolved model variant: {self.model.id}")
        print("Downloading model if necessary...")

        self.model.download(self._show_download_progress)
        print("\nModel download completed.")

        print("Loading model...")
        self.model.load()

        self.client = self.model.get_chat_client()

        print("Model loaded successfully.")

    @staticmethod
    def _show_download_progress(progress: float) -> None:
        """Display model download progress in the terminal."""

        print(
            f"\rDownload progress: {progress:6.2f}%",
            end="",
            flush=True,
        )

    def generate_answer(
        self,
        prompt: str,
        system_message: str = (
            "You are a helpful AI assistant. "
            "Answer only using the context provided in the prompt."
        ),
    ) -> str:
        """Generate and return an answer for the supplied prompt."""

        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            raise ValueError("Prompt cannot be empty.")

        if self.client is None:
            raise RuntimeError("The chat client has not been initialized.")

        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": cleaned_prompt,
            },
        ]

        answer_parts: list[str] = []

        try:
            for chunk in self.client.complete_streaming_chat(messages):
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    answer_parts.append(content)

        except Exception as exc:
            raise RuntimeError(
                f"Answer generation failed: {exc}"
            ) from exc

        answer = "".join(answer_parts).strip()

        if not answer:
            raise RuntimeError("The model returned an empty response.")

        return answer

    def close(self) -> None:
        """Unload the local model and release its resources."""

        if self.model is not None:
            print("Unloading model...")
            self.model.unload()
            self.model = None
            self.client = None
            print("Model unloaded successfully.")

    def __enter__(self) -> "AnswerGenerator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def main() -> None:
    """Run a standalone smoke test for the answer generator."""

    test_prompt = """
Context:
Retrieval-Augmented Generation retrieves relevant information before
asking a language model to generate an answer.

Question:
What does Retrieval-Augmented Generation do?
""".strip()

    with AnswerGenerator() as generator:
        answer = generator.generate_answer(test_prompt)

        print("\nGenerated answer:")
        print(answer)


if __name__ == "__main__":
    main()