from pathlib import Path

from app.chunking import SUPPORTED_EXTENSIONS, chunk_text, read_document
from app.database_manager import (
    insert_chunk,
    insert_document,
    insert_embedding,
)
from app.query_embedding import MODEL_ALIAS, QueryEmbedder


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data"

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50
DEFAULT_MINIMUM_CHUNK_SIZE = 50


def find_documents(data_directory: Path) -> list[Path]:
    """
    Find supported documents in the data directory.
    """

    if not data_directory.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_directory}"
        )

    documents = [
        file_path
        for file_path in data_directory.iterdir()
        if (
            file_path.is_file()
            and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
    ]

    return sorted(documents)


def ingest_document(
    file_path: Path,
    embedder: QueryEmbedder,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
    minimum_chunk_size: int = DEFAULT_MINIMUM_CHUNK_SIZE,
) -> tuple[int, int]:
    """
    Read, chunk, embed, and store a single document.
    """

    document_text = read_document(file_path)

    if not document_text.strip():
        print(f"Skipped empty document: {file_path.name}")
        return 0, 0

    chunks = chunk_text(
        text=document_text,
        chunk_size=chunk_size,
        overlap=overlap,
        minimum_chunk_size=minimum_chunk_size,
    )

    if not chunks:
        print(f"No chunks generated for: {file_path.name}")
        return 0, 0

    relative_source_path = file_path.relative_to(PROJECT_ROOT)

    document_id = insert_document(
        filename=file_path.name,
        file_type=file_path.suffix.lower().lstrip("."),
        source_path=str(relative_source_path),
    )

    embedding_count = 0

    for chunk_index, content in enumerate(chunks):
        chunk_id = insert_chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
        )

        embedding_vector = embedder.generate_embedding(content)

        insert_embedding(
            chunk_id=chunk_id,
            model_name=MODEL_ALIAS,
            embedding_vector=embedding_vector,
        )

        embedding_count += 1

        print(
            f"  Chunk {chunk_index} stored | "
            f"Chunk ID: {chunk_id} | "
            f"Characters: {len(content)} | "
            f"Dimensions: {len(embedding_vector)}"
        )

    return len(chunks), embedding_count


def main() -> None:
    """
    Ingest all supported documents from the data directory.
    """

    documents = find_documents(DATA_DIRECTORY)

    if not documents:
        print("No supported documents found.")
        return

    print(f"Documents found: {len(documents)}")
    print(f"Embedding model: {MODEL_ALIAS}")
    print(f"Chunk size: {DEFAULT_CHUNK_SIZE}")
    print(f"Overlap: {DEFAULT_OVERLAP}")

    embedder = QueryEmbedder()

    total_chunks = 0
    total_embeddings = 0

    try:
        for file_path in documents:
            print(f"\nProcessing: {file_path.name}")

            chunk_count, embedding_count = ingest_document(
                file_path=file_path,
                embedder=embedder,
            )

            total_chunks += chunk_count
            total_embeddings += embedding_count

            print(
                f"Completed: {file_path.name} | "
                f"Chunks: {chunk_count} | "
                f"Embeddings: {embedding_count}"
            )
    finally:
        embedder.unload()

    print("\nIngestion completed successfully.")
    print(f"Documents processed: {len(documents)}")
    print(f"Chunks stored: {total_chunks}")
    print(f"Embeddings stored: {total_embeddings}")


if __name__ == "__main__":
    main()