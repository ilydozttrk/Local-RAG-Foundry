import sqlite3
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "rag_database.db"


def connect_database() -> sqlite3.Connection:
    """Connect to the Local RAG SQLite database."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=5.0,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA busy_timeout = 5000;")

    return connection


def normalize_source_path(source_path: str) -> str:
    """Normalize a document source path before database operations."""

    if not isinstance(source_path, str):
        raise TypeError("source_path must be a string.")

    cleaned_source_path = source_path.strip()

    if not cleaned_source_path:
        raise ValueError("source_path cannot be empty.")

    return (
    cleaned_source_path
    .replace("\\", "/")
    .rstrip("/")
    )


def insert_document(
    filename: str,
    file_type: str,
    source_path: str,
) -> int:
    """Insert a document and return its database ID."""

    if not isinstance(filename, str):
        raise TypeError("filename must be a string.")

    if not isinstance(file_type, str):
        raise TypeError("file_type must be a string.")

    cleaned_filename = filename.strip()
    cleaned_file_type = file_type.strip().lower().lstrip(".")
    cleaned_source_path = normalize_source_path(source_path)

    if not cleaned_filename:
        raise ValueError("filename cannot be empty.")

    if not cleaned_file_type:
        raise ValueError("file_type cannot be empty.")

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                INSERT INTO documents (
                    filename,
                    file_type,
                    source_path
                )
                VALUES (?, ?, ?)
                """,
                (
                    cleaned_filename,
                    cleaned_file_type,
                    cleaned_source_path,
                ),
            )

            document_id = cursor.lastrowid

            if document_id is None:
                raise RuntimeError(
                    "The document was inserted, but no ID was returned."
                )

            return int(document_id)

    except sqlite3.IntegrityError as error:
        raise ValueError(
            "A document with the same source path already exists: "
            f"{cleaned_source_path}"
        ) from error

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document insertion failed: {error}"
        ) from error


def insert_chunk(
    document_id: int,
    chunk_index: int,
    content: str,
) -> int:
    """Insert a document chunk and return its database ID."""

    if not isinstance(document_id, int):
        raise TypeError("document_id must be an integer.")

    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")

    if not isinstance(chunk_index, int):
        raise TypeError("chunk_index must be an integer.")

    if chunk_index < 0:
        raise ValueError("chunk_index cannot be negative.")

    if not isinstance(content, str):
        raise TypeError("content must be a string.")

    cleaned_content = content.strip()

    if not cleaned_content:
        raise ValueError("content cannot be empty.")

    character_count = len(cleaned_content)

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                INSERT INTO chunks (
                    document_id,
                    chunk_index,
                    content,
                    character_count
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    document_id,
                    chunk_index,
                    cleaned_content,
                    character_count,
                ),
            )

            chunk_id = cursor.lastrowid

            if chunk_id is None:
                raise RuntimeError(
                    "The chunk was inserted, but no ID was returned."
                )

            return int(chunk_id)

    except sqlite3.IntegrityError as error:
        raise ValueError(
            "The chunk could not be inserted. Verify the document ID "
            "and ensure that the chunk index is unique."
        ) from error

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Chunk insertion failed: {error}"
        ) from error


def insert_embedding(
    chunk_id: int,
    model_name: str,
    embedding_vector: Sequence[float],
) -> int:
    """Insert an embedding vector and return its database ID."""

    if not isinstance(chunk_id, int):
        raise TypeError("chunk_id must be an integer.")

    if chunk_id <= 0:
        raise ValueError("chunk_id must be greater than zero.")

    if not isinstance(model_name, str):
        raise TypeError("model_name must be a string.")

    cleaned_model_name = model_name.strip()

    if not cleaned_model_name:
        raise ValueError("model_name cannot be empty.")

    if not embedding_vector:
        raise ValueError("embedding_vector cannot be empty.")

    try:
        normalized_vector = [
            float(value)
            for value in embedding_vector
        ]
    except (TypeError, ValueError) as error:
        raise ValueError(
            "embedding_vector must contain only numeric values."
        ) from error

    embedding_text = ",".join(
        str(value)
        for value in normalized_vector
    )

    dimension = len(normalized_vector)

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                INSERT INTO embeddings (
                    chunk_id,
                    model_name,
                    dimension,
                    vector
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    cleaned_model_name,
                    dimension,
                    embedding_text,
                ),
            )

            embedding_id = cursor.lastrowid

            if embedding_id is None:
                raise RuntimeError(
                    "The embedding was inserted, but no ID was returned."
                )

            return int(embedding_id)

    except sqlite3.IntegrityError as error:
        raise ValueError(
            "The embedding could not be inserted. Verify the chunk ID "
            "and ensure that the model embedding is not duplicated."
        ) from error

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Embedding insertion failed: {error}"
        ) from error


def get_documents() -> list[sqlite3.Row]:
    """Return all stored documents with chunk and embedding counts."""

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                SELECT
                    documents.id,
                    documents.filename,
                    documents.file_type,
                    documents.source_path,
                    documents.is_active,
                    documents.archived_at,
                    documents.created_at,
                    COUNT(DISTINCT chunks.id) AS chunk_count,
                    COUNT(DISTINCT embeddings.id) AS embedding_count
                FROM documents
                LEFT JOIN chunks
                    ON chunks.document_id = documents.id
                LEFT JOIN embeddings
                    ON embeddings.chunk_id = chunks.id
                GROUP BY documents.id
                ORDER BY documents.created_at DESC, documents.id DESC
                """
            )

            return cursor.fetchall()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document retrieval failed: {error}"
        ) from error


def get_document(
    document_id: int,
) -> sqlite3.Row | None:
    """Return a document by ID with chunk and embedding counts."""

    if not isinstance(document_id, int):
        raise TypeError("document_id must be an integer.")

    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                SELECT
                    documents.id,
                    documents.filename,
                    documents.file_type,
                    documents.source_path,
                    documents.is_active,
                    documents.archived_at,
                    documents.created_at,
                    COUNT(DISTINCT chunks.id) AS chunk_count,
                    COUNT(DISTINCT embeddings.id) AS embedding_count
                FROM documents
                LEFT JOIN chunks
                    ON chunks.document_id = documents.id
                LEFT JOIN embeddings
                    ON embeddings.chunk_id = chunks.id
                WHERE documents.id = ?
                GROUP BY documents.id
                """,
                (document_id,),
            )

            return cursor.fetchone()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document retrieval failed: {error}"
        ) from error


def get_document_by_source_path(
    source_path: str,
) -> sqlite3.Row | None:
    """Return a document matching the supplied source path."""

    cleaned_source_path = normalize_source_path(source_path)

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                SELECT
                    documents.id,
                    documents.filename,
                    documents.file_type,
                    documents.source_path,
                    documents.is_active,
                    documents.archived_at,
                    documents.created_at,
                    COUNT(DISTINCT chunks.id) AS chunk_count,
                    COUNT(DISTINCT embeddings.id) AS embedding_count
                FROM documents
                LEFT JOIN chunks
                    ON chunks.document_id = documents.id
                LEFT JOIN embeddings
                    ON embeddings.chunk_id = chunks.id
                WHERE documents.source_path = ?
                GROUP BY documents.id
                """,
                (cleaned_source_path,),
            )

            return cursor.fetchone()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document lookup failed: {error}"
        ) from error


def document_exists(source_path: str) -> bool:
    """Return whether a document with the source path already exists."""

    return get_document_by_source_path(source_path) is not None


def get_active_documents() -> list[sqlite3.Row]:
    """Return all active documents."""

    return [
        document
        for document in get_documents()
        if document["is_active"] == 1
    ]


def get_archived_documents() -> list[sqlite3.Row]:
    """Return all archived documents."""

    return [
        document
        for document in get_documents()
        if document["is_active"] == 0
    ]


def activate_document(document_id: int) -> bool:
    """Move a document into the active knowledge base."""

    if not isinstance(document_id, int):
        raise TypeError("document_id must be an integer.")

    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                UPDATE documents
                SET
                    is_active = 1,
                    archived_at = NULL
                WHERE id = ?
                """,
                (document_id,),
            )

            return cursor.rowcount > 0

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document activation failed: {error}"
        ) from error


def archive_document(document_id: int) -> bool:
    """Move a document into the archive."""

    if not isinstance(document_id, int):
        raise TypeError("document_id must be an integer.")

    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                UPDATE documents
                SET
                    is_active = 0,
                    archived_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (document_id,),
            )

            return cursor.rowcount > 0

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document archiving failed: {error}"
        ) from error


def delete_document(document_id: int) -> bool:
    """Delete a document and its related chunks and embeddings."""

    if not isinstance(document_id, int):
        raise TypeError("document_id must be an integer.")

    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (document_id,),
            )

            return cursor.rowcount > 0

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document deletion failed: {error}"
        ) from error


def delete_all_documents() -> int:
    """Delete all documents and cascade related database records."""

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                """
                DELETE FROM documents
                """
            )

            return cursor.rowcount

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Document cleanup failed: {error}"
        ) from error


def get_chunks(
    document_id: int | None = None,
) -> list[sqlite3.Row]:
    """Return all chunks or chunks belonging to one document."""

    if document_id is not None:
        if not isinstance(document_id, int):
            raise TypeError("document_id must be an integer.")

        if document_id <= 0:
            raise ValueError("document_id must be greater than zero.")

    try:
        with connect_database() as connection:
            if document_id is None:
                cursor = connection.execute(
                    """
                    SELECT *
                    FROM chunks
                    ORDER BY document_id, chunk_index
                    """
                )
            else:
                cursor = connection.execute(
                    """
                    SELECT *
                    FROM chunks
                    WHERE document_id = ?
                    ORDER BY chunk_index
                    """,
                    (document_id,),
                )

            return cursor.fetchall()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Chunk retrieval failed: {error}"
        ) from error


def get_embeddings(
    model_name: str | None = None,
) -> list[sqlite3.Row]:
    """Return all embeddings or embeddings for one model."""

    if model_name is not None:
        if not isinstance(model_name, str):
            raise TypeError("model_name must be a string.")

        model_name = model_name.strip()

        if not model_name:
            raise ValueError("model_name cannot be empty.")

    try:
        with connect_database() as connection:
            if model_name is None:
                cursor = connection.execute(
                    """
                    SELECT *
                    FROM embeddings
                    ORDER BY id
                    """
                )
            else:
                cursor = connection.execute(
                    """
                    SELECT *
                    FROM embeddings
                    WHERE model_name = ?
                    ORDER BY id
                    """,
                    (model_name,),
                )

            return cursor.fetchall()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Embedding retrieval failed: {error}"
        ) from error


def get_chunks_with_embeddings(
    model_name: str,
    document_ids: Sequence[int] | None = None,
) -> list[sqlite3.Row]:
    """
    Return chunks and embedding vectors for semantic retrieval.

    When document_ids is supplied, retrieval is restricted to those
    documents.
    """

    if not isinstance(model_name, str):
        raise TypeError("model_name must be a string.")

    cleaned_model_name = model_name.strip()

    if not cleaned_model_name:
        raise ValueError("model_name cannot be empty.")

    cleaned_document_ids: list[int] | None = None

    if document_ids is not None:
        cleaned_document_ids = list(document_ids)

        if not cleaned_document_ids:
            return []

        if any(
            not isinstance(document_id, int)
            or document_id <= 0
            for document_id in cleaned_document_ids
        ):
            raise ValueError(
                "document_ids must contain positive integers."
            )

    base_query = """
        SELECT
            chunks.id AS chunk_id,
            chunks.document_id,
            documents.filename,
            documents.file_type,
            documents.source_path,
            chunks.chunk_index,
            chunks.content,
            chunks.character_count,
            embeddings.model_name,
            embeddings.dimension,
            embeddings.vector
        FROM chunks
        INNER JOIN documents
            ON documents.id = chunks.document_id
        INNER JOIN embeddings
            ON embeddings.chunk_id = chunks.id
        WHERE embeddings.model_name = ?
          AND documents.is_active = 1
    """

    parameters: list[object] = [cleaned_model_name]

    if cleaned_document_ids:
        placeholders = ",".join(
            "?"
            for _ in cleaned_document_ids
        )

        base_query += (
            f"\nAND chunks.document_id IN ({placeholders})"
        )

        parameters.extend(cleaned_document_ids)

    base_query += "\nORDER BY chunks.id"

    try:
        with connect_database() as connection:
            cursor = connection.execute(
                base_query,
                parameters,
            )

            return cursor.fetchall()

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Retrieval data query failed: {error}"
        ) from error


def get_database_statistics() -> dict[str, int]:
    """Return document, chunk, and embedding record counts."""

    try:
        with connect_database() as connection:
            document_count = connection.execute(
                "SELECT COUNT(*) FROM documents"
            ).fetchone()[0]

            active_document_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM documents
                WHERE is_active = 1
                """
            ).fetchone()[0]

            archived_document_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM documents
                WHERE is_active = 0
                """
            ).fetchone()[0]

            chunk_count = connection.execute(
                "SELECT COUNT(*) FROM chunks"
            ).fetchone()[0]

            embedding_count = connection.execute(
                "SELECT COUNT(*) FROM embeddings"
            ).fetchone()[0]

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Database statistics retrieval failed: {error}"
        ) from error

    return {
        "documents": int(document_count),
        "active_documents": int(active_document_count),
        "archived_documents": int(archived_document_count),
        "chunks": int(chunk_count),
        "embeddings": int(embedding_count),
    }


def main() -> None:
    """Run a read-only database manager smoke test."""

    print("=" * 80)
    print("DATABASE MANAGER")
    print("=" * 80)
    print(f"Database path: {DATABASE_PATH}")

    statistics = get_database_statistics()

    print("\nStatistics:")
    print(f"- Documents: {statistics['documents']}")
    print(f"- Active documents: {statistics['active_documents']}")
    print(f"- Archived documents: {statistics['archived_documents']}")
    print(f"- Chunks: {statistics['chunks']}")
    print(f"- Embeddings: {statistics['embeddings']}")

    documents = get_documents()

    print("\nStored documents:")

    if not documents:
        print("- No documents found.")
        return

    for document in documents:
        print(
            f"- ID: {document['id']} | "
            f"Filename: {document['filename']} | "
            f"Type: {document['file_type']} | "
            f"Status: {'active' if document['is_active'] == 1 else 'archived'} | "
            f"Chunks: {document['chunk_count']} | "
            f"Embeddings: {document['embedding_count']} | "
            f"Source: {document['source_path']}"
        )


if __name__ == "__main__":
    main()