from foundry_local_sdk import Configuration, FoundryLocalManager

MODEL_ALIAS = "qwen2.5-0.5b"


def main() -> None:
    """Run the first local chat completion with Foundry Local SDK."""

    print("Initializing Foundry Local SDK...")

    config = Configuration(app_name="local_rag_foundry")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    print(f"Selecting model: {MODEL_ALIAS}")
    model = manager.catalog.get_model(MODEL_ALIAS)

    if model is None:
        raise RuntimeError(
            f"Model alias could not be found in the SDK catalog: {MODEL_ALIAS}"
        )

    print(f"Resolved model variant: {model.id}")

    print("Downloading model if necessary...")

    def show_download_progress(progress: float) -> None:
        print(
            f"\rDownload progress: {progress:6.2f}%",
            end="",
            flush=True,
        )

    model.download(show_download_progress)
    print("\nModel download completed.")

    print("Loading model...")
    model.load()
    print("Model loaded successfully.")

    try:
        client = model.get_chat_client()

        messages = [
            {
                "role": "system",
                "content": "You are a concise and helpful AI assistant.",
            },
            {
                "role": "user",
                "content": "Hello! Introduce yourself in one short sentence.",
            },
        ]

        print("\nAssistant: ", end="", flush=True)

        for chunk in client.complete_streaming_chat(messages):
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                print(content, end="", flush=True)

        print()

    finally:
        print("\nUnloading model...")
        model.unload()
        print("Model unloaded successfully.")


if __name__ == "__main__":
    main()