from app.foundry_manager import get_foundry_manager


MODEL_ALIAS = "qwen3-embedding-0.6b"


class QueryEmbedder:
    """Generate embeddings for user queries."""

    def __init__(self) -> None:
        self.manager = get_foundry_manager()

        self.model = self.manager.catalog.get_model(MODEL_ALIAS)

        if self.model is None:
            raise RuntimeError(
                f"Embedding model could not be found: {MODEL_ALIAS}"
            )

        self.model.download()
        self.model.load()

        self.client = self.model.get_embedding_client()

    def generate_embedding(self, query: str) -> list[float]:
        """Generate an embedding vector from a user query."""

        if not isinstance(query, str):
            raise TypeError("Query must be a string.")

        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        response = self.client.generate_embedding(cleaned_query)

        return response.data[0].embedding

    def unload(self) -> None:
        """Unload the embedding model."""

        self.model.unload()


def main() -> None:
    """Run a standalone query embedding smoke test."""

    embedder = QueryEmbedder()

    try:
        query = "How do I install Microsoft Foundry Local?"

        embedding = embedder.generate_embedding(query)

        print(f"Query: {query}")
        print(f"Dimensions: {len(embedding)}")
        print(f"First 10 values: {embedding[:10]}")

    finally:
        embedder.unload()


if __name__ == "__main__":
    main()