from foundry_local_sdk import Configuration, FoundryLocalManager


MODEL_ALIAS = "qwen3-embedding-0.6b"


class QueryEmbedder:
    """Generate embeddings for user queries."""

    def __init__(self):
        config = Configuration(app_name="local_rag_foundry")
        FoundryLocalManager.initialize(config)

        self.manager = FoundryLocalManager.instance

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

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        response = self.client.generate_embedding(query)

        return response.data[0].embedding

    def unload(self):
        """Unload embedding model."""

        self.model.unload()


if __name__ == "__main__":
    embedder = QueryEmbedder()

    query = "How do I install Microsoft Foundry Local?"

    embedding = embedder.generate_embedding(query)

    print(f"Query: {query}")
    print(f"Dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")

    embedder.unload()