from foundry_local_sdk import Configuration, FoundryLocalManager

MODEL_ALIAS = "qwen2.5-0.5b"


def run_experiment(client, title: str, messages: list[dict]) -> None:
    """Run a prompt experiment and print the model response."""

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print("\nPROMPT:")
    for message in messages:
        print(f"[{message['role'].upper()}] {message['content']}")

    print("\nMODEL RESPONSE:")

    for chunk in client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)

    print()


def main() -> None:
    """Compare different prompt engineering strategies."""

    print("Initializing Foundry Local SDK...")

    config = Configuration(app_name="local_rag_foundry")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(MODEL_ALIAS)

    if model is None:
        raise RuntimeError(f"Model could not be found: {MODEL_ALIAS}")

    print(f"Selected model: {model.id}")
    print("Loading model...")

    model.load()

    try:
        client = model.get_chat_client()

        # Experiment 1: User prompt only
        experiment_1 = [
            {
                "role": "user",
                "content": (
                    "What database does the Local RAG Assistant project use?"
                ),
            }
        ]

        # Experiment 2: System prompt + user prompt
        experiment_2 = [
            {
                "role": "system",
                "content": (
                    "You are a concise technical assistant. "
                    "Answer clearly and briefly."
                ),
            },
            {
                "role": "user",
                "content": (
                    "What database does the Local RAG Assistant project use?"
                ),
            },
        ]

        # Experiment 3: Context provided
        experiment_3 = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using the provided context."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Context:\n"
                    "The Local RAG Assistant stores document metadata "
                    "and text chunks in SQLite.\n\n"
                    "Question:\n"
                    "What database does the Local RAG Assistant project use?"
                ),
            },
        ]

        # Experiment 4: Optimized hallucination reduction
        experiment_4 = [
            {
                "role": "system",
                "content": (
                    "You are a retrieval-based question-answering assistant. "
                    "You must follow the answer rules exactly."
                ),
            },
            {
                "role": "user",
                "content": (
                    "ANSWER RULES:\n"
                    "1. Use only the information inside the CONTEXT section.\n"
                    "2. Do not use prior knowledge.\n"
                    "3. Do not guess or infer missing information.\n"
                    "4. If the answer is not explicitly written in the context, "
                    "respond with exactly:\n"
                    "I don't know based on the provided context.\n\n"
                    "CONTEXT:\n"
                    "The Local RAG Assistant stores document metadata "
                    "and text chunks in SQLite.\n\n"
                    "QUESTION:\n"
                    "Which cloud provider hosts the Local RAG Assistant?\n\n"
                    "ANSWER:"
                ),
            },
        ]

        # Experiment 5: Few-shot hallucination reduction
        experiment_5 = [
            {
                "role": "system",
                "content": (
                    "You are a retrieval-based question-answering assistant. "
                    "Answer only from the supplied context."
                ),
            },
            {
                "role": "user",
                "content": (
                    "EXAMPLE 1\n"
                    "CONTEXT: The application uses PostgreSQL.\n"
                    "QUESTION: Which database does the application use?\n"
                    "ANSWER: PostgreSQL\n\n"
                    "EXAMPLE 2\n"
                    "CONTEXT: The application uses PostgreSQL.\n"
                    "QUESTION: Which cloud provider hosts the application?\n"
                    "ANSWER: I don't know based on the provided context.\n\n"
                    "NOW ANSWER THE FOLLOWING:\n"
                    "CONTEXT: The Local RAG Assistant stores document metadata "
                    "and text chunks in SQLite.\n"
                    "QUESTION: Which cloud provider hosts the Local RAG Assistant?\n"
                    "ANSWER:"
                ),
            },
        ]

        run_experiment(
            client,
            "EXPERIMENT 1 - USER PROMPT ONLY",
            experiment_1,
        )

        run_experiment(
            client,
            "EXPERIMENT 2 - SYSTEM PROMPT + USER PROMPT",
            experiment_2,
        )

        run_experiment(
            client,
            "EXPERIMENT 3 - CONTEXT PROVIDED",
            experiment_3,
        )

        run_experiment(
            client,
            "EXPERIMENT 4 - OPTIMIZED HALLUCINATION REDUCTION",
            experiment_4,
        )

        run_experiment(
            client,
            "EXPERIMENT 5 - FEW-SHOT HALLUCINATION REDUCTION",
            experiment_5,
        )

    finally:
        print("\nUnloading model...")
        model.unload()
        print("Model unloaded successfully.")


if __name__ == "__main__":
    main()