from pathlib import Path
from typing import TypedDict

from app.chunking import SUPPORTED_EXTENSIONS
from app.database_manager import (
    delete_all_documents,
    delete_document,
    get_document,
    get_document_by_source_path,
    get_documents,
    normalize_source_path,
)
from app.ingest_documents import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MINIMUM_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    PROJECT_ROOT,
    ingest_document,
)
from app.query_embedding import QueryEmbedder


class DocumentIngestionResult(TypedDict):
    """Represent the ingestion result of a single document."""

    filename: str
    source_path: str
    status: str
    document_id: int | None
    chunk_count: int
    embedding_count: int
    message: str


class DocumentManager:
    """Manage document ingestion, metadata, and deletion."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
        minimum_chunk_size: int = DEFAULT_MINIMUM_CHUNK_SIZE,
    ) -> None:
        if not isinstance(chunk_size, int):
            raise TypeError("chunk_size must be an integer.")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if not isinstance(overlap, int):
            raise TypeError("overlap must be an integer.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        if not isinstance(minimum_chunk_size, int):
            raise TypeError(
                "minimum_chunk_size must be an integer."
            )

        if minimum_chunk_size <= 0:
            raise ValueError(
                "minimum_chunk_size must be greater than zero."
            )

        if minimum_chunk_size > chunk_size:
            raise ValueError(
                "minimum_chunk_size cannot exceed chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.minimum_chunk_size = minimum_chunk_size

    @staticmethod
    def _validate_file_path(
        file_path: str | Path,
    ) -> Path:
        """Validate and resolve a supported document path."""

        if not isinstance(file_path, (str, Path)):
            raise TypeError(
                "file_path must be a string or pathlib.Path."
            )

        resolved_path = Path(file_path).expanduser().resolve()

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"Document not found: {resolved_path}"
            )

        if not resolved_path.is_file():
            raise ValueError(
                f"Path is not a file: {resolved_path}"
            )

        extension = resolved_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            supported_types = ", ".join(
                sorted(SUPPORTED_EXTENSIONS)
            )

            raise ValueError(
                f"Unsupported document type: {extension}. "
                f"Supported types: {supported_types}"
            )

        return resolved_path

    @staticmethod
    def _build_source_path(file_path: Path) -> str:
        """Build the source path used in document metadata."""

        try:
            source_path = file_path.relative_to(PROJECT_ROOT)
        except ValueError:
            source_path = file_path

        return normalize_source_path(str(source_path))

    def document_exists(
        self,
        file_path: str | Path,
    ) -> bool:
        """Return whether the supplied document is already stored."""

        validated_path = self._validate_file_path(file_path)
        source_path = self._build_source_path(validated_path)

        return get_document_by_source_path(source_path) is not None

    def add_document(
        self,
        file_path: str | Path,
    ) -> DocumentIngestionResult:
        """Ingest and store a single supported document."""

        results = self.add_documents([file_path])

        return results[0]

    def add_documents(
        self,
        file_paths: list[str | Path],
    ) -> list[DocumentIngestionResult]:
        """Ingest multiple supported documents with one embedder."""

        if not isinstance(file_paths, list):
            raise TypeError("file_paths must be a list.")

        if not file_paths:
            raise ValueError("file_paths cannot be empty.")

        validated_paths = [
            self._validate_file_path(file_path)
            for file_path in file_paths
        ]

        results: list[DocumentIngestionResult] = []
        paths_to_ingest: list[tuple[Path, str]] = []

        seen_source_paths: set[str] = set()

        for file_path in validated_paths:
            source_path = self._build_source_path(file_path)

            if source_path in seen_source_paths:
                results.append(
                    {
                        "filename": file_path.name,
                        "source_path": source_path,
                        "status": "skipped",
                        "document_id": None,
                        "chunk_count": 0,
                        "embedding_count": 0,
                        "message": (
                            "The same document was supplied more "
                            "than once in this batch."
                        ),
                    }
                )
                continue

            seen_source_paths.add(source_path)

            existing_document = get_document_by_source_path(
                source_path
            )

            if existing_document is not None:
                results.append(
                    {
                        "filename": file_path.name,
                        "source_path": source_path,
                        "status": "skipped",
                        "document_id": existing_document["id"],
                        "chunk_count": 0,
                        "embedding_count": 0,
                        "message": (
                            "Document already exists in the database."
                        ),
                    }
                )
                continue

            paths_to_ingest.append(
                (
                    file_path,
                    source_path,
                )
            )

        if not paths_to_ingest:
            return results

        embedder = QueryEmbedder()

        try:
            for file_path, source_path in paths_to_ingest:
                try:
                    chunk_count, embedding_count = ingest_document(
                        file_path=file_path,
                        embedder=embedder,
                        chunk_size=self.chunk_size,
                        overlap=self.overlap,
                        minimum_chunk_size=(
                            self.minimum_chunk_size
                        ),
                    )

                    stored_document = get_document_by_source_path(
                        source_path
                    )

                    if chunk_count == 0:
                        results.append(
                            {
                                "filename": file_path.name,
                                "source_path": source_path,
                                "status": "skipped",
                                "document_id": None,
                                "chunk_count": 0,
                                "embedding_count": 0,
                                "message": (
                                    "No usable content was found "
                                    "in the document."
                                ),
                            }
                        )
                        continue

                    if stored_document is None:
                        raise RuntimeError(
                            "The document was ingested but its "
                            "metadata could not be retrieved."
                        )

                    results.append(
                        {
                            "filename": file_path.name,
                            "source_path": source_path,
                            "status": "success",
                            "document_id": stored_document["id"],
                            "chunk_count": chunk_count,
                            "embedding_count": embedding_count,
                            "message": (
                                "Document ingested successfully."
                            ),
                        }
                    )

                except Exception as error:
                    results.append(
                        {
                            "filename": file_path.name,
                            "source_path": source_path,
                            "status": "failed",
                            "document_id": None,
                            "chunk_count": 0,
                            "embedding_count": 0,
                            "message": str(error),
                        }
                    )

        finally:
            embedder.unload()

        return results

    @staticmethod
    def list_documents():
        """Return metadata for all stored documents."""

        return get_documents()

    @staticmethod
    def get_document(document_id: int):
        """Return metadata for one stored document."""

        document = get_document(document_id)

        if document is None:
            raise LookupError(
                f"Document not found: {document_id}"
            )

        return document

    @staticmethod
    def remove_document(document_id: int) -> bool:
        """Delete one document and its related records."""

        document = get_document(document_id)

        if document is None:
            return False

        return delete_document(document_id)

    @staticmethod
    def clear_documents() -> int:
        """Delete every document and related database record."""

        return delete_all_documents()


def print_ingestion_result(
    result: DocumentIngestionResult,
) -> None:
    """Print a formatted document ingestion result."""

    print(
        f"Filename: {result['filename']}\n"
        f"Status: {result['status']}\n"
        f"Document ID: {result['document_id']}\n"
        f"Chunks: {result['chunk_count']}\n"
        f"Embeddings: {result['embedding_count']}\n"
        f"Source: {result['source_path']}\n"
        f"Message: {result['message']}"
    )


def main() -> None:
    """Run a read-only Document Manager smoke test."""

    manager = DocumentManager()

    print("=" * 80)
    print("DOCUMENT MANAGER")
    print("=" * 80)

    documents = manager.list_documents()

    print(f"Stored documents: {len(documents)}")

    if not documents:
        print("No documents are currently stored.")
        return

    for document in documents:
        print(
            f"- ID: {document['id']} | "
            f"Filename: {document['filename']} | "
            f"Type: {document['file_type']} | "
            f"Chunks: {document['chunk_count']} | "
            f"Embeddings: {document['embedding_count']} | "
            f"Created: {document['created_at']}"
        )


if __name__ == "__main__":
    main()