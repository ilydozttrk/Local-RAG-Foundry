import math

from foundry_local_sdk import Configuration, FoundryLocalManager


MODEL_ALIAS = "qwen3-embedding-0.6b"


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same number of dimensions.")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(value * value for value in vector_a)
    )
    magnitude_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def print_embedding_summary(
    text: str,
    embedding: list[float],
) -> None:
    """Print basic information about an embedding vector."""

    print("\n" + "-" * 70)
    print(f"TEXT: {text}")
    print(f"DIMENSIONS: {len(embedding)}")
    print(f"FIRST 10 VALUES: {embedding[:10]}")


def main() -> None:
    """Generate embeddings and compare their semantic similarity."""

    print("Initializing Foundry Local SDK...")

    config = Configuration(app_name="local_rag_foundry")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    print(f"Selecting embedding model: {MODEL_ALIAS}")

    model = manager.catalog.get_model(MODEL_ALIAS)

    if model is None:
        raise RuntimeError(
            f"Embedding model could not be found: {MODEL_ALIAS}"
        )

    print(f"Resolved model: {model.id}")
    print("Downloading model if necessary...")

    model.download(
        lambda progress: print(
            f"\rDownload progress: {progress:.2f}%",
            end="",
            flush=True,
        )
    )

    print("\nLoading embedding model...")
    model.load()
    print("Embedding model loaded successfully.")

    try:
        client = model.get_embedding_client()

        texts = [
            "Artificial intelligence can process natural language.",
            "AI systems are able to understand human language.",
            "SQLite is a lightweight local database.",
            "Chocolate cake is made with cocoa and sugar.",
        ]

        print("\nGenerating embeddings...")

        response = client.generate_embeddings(texts)

        embeddings = [
            item.embedding
            for item in response.data
        ]

        for text, embedding in zip(texts, embeddings):
            print_embedding_summary(text, embedding)

        reference_text = texts[0]
        reference_embedding = embeddings[0]

        print("\n" + "=" * 70)
        print("COSINE SIMILARITY RESULTS")
        print("=" * 70)

        results = []

        for text, embedding in zip(texts[1:], embeddings[1:]):
            score = cosine_similarity(
                reference_embedding,
                embedding,
            )

            results.append((text, score))

        results.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        print(f"\nREFERENCE TEXT:\n{reference_text}")

        for text, score in results:
            print("\n" + "-" * 70)
            print(f"COMPARED TEXT: {text}")
            print(f"SIMILARITY SCORE: {score:.4f}")

        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)

        most_similar_text, highest_score = results[0]
        least_similar_text, lowest_score = results[-1]

        print("\nMost similar text:")
        print(most_similar_text)
        print(f"Score: {highest_score:.4f}")

        print("\nLeast similar text:")
        print(least_similar_text)
        print(f"Score: {lowest_score:.4f}")

        print(
            "\nHigher cosine similarity values indicate that "
            "the texts are semantically closer."
        )

    finally:
        print("\nUnloading embedding model...")
        model.unload()
        print("Embedding model unloaded successfully.")


if __name__ == "__main__":
    main()