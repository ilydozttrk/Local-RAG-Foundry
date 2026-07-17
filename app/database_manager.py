import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "rag_database.db"


def connect_database():
    """
    Connect to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def insert_document(filename, file_type, source_path):
    """
    Insert a new document into the documents table.
    """

    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO documents (
                filename,
                file_type,
                source_path
            )
            VALUES (?, ?, ?)
            """,
            (
                filename,
                file_type,
                source_path,
            ),
        )

        document_id = cursor.lastrowid

    return document_id


def insert_chunk(document_id, chunk_index, content):
    """
    Insert a document chunk into the chunks table.
    """

    character_count = len(content)

    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute(
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
                content,
                character_count,
            ),
        )

        chunk_id = cursor.lastrowid

    return chunk_id


def insert_embedding(chunk_id, model_name, embedding_vector):
    """
    Insert an embedding vector into the embeddings table.
    """

    embedding_text = ",".join(map(str, embedding_vector))
    dimension = len(embedding_vector)

    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute(
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
                model_name,
                dimension,
                embedding_text,
            ),
        )

        embedding_id = cursor.lastrowid

    return embedding_id


def get_chunks():
    """
    Retrieve all chunks from the database.
    """

    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM chunks
            ORDER BY id
            """
        )

        chunks = cursor.fetchall()

    return chunks


def get_embeddings():
    """
    Retrieve all embeddings from the database.
    """

    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM embeddings
            ORDER BY id
            """
        )

        embeddings = cursor.fetchall()

    return embeddings


def main():
    """
    Test database insert and query operations.
    """

    document_id = insert_document(
        filename="sample.txt",
        file_type="txt",
        source_path="data/sample.txt",
    )

    chunk_id = insert_chunk(
        document_id=document_id,
        chunk_index=0,
        content="This is a sample document chunk.",
    )

    embedding_id = insert_embedding(
        chunk_id=chunk_id,
        model_name="test-embedding-model",
        embedding_vector=[0.12, -0.45, 0.78],
    )

    print(f"Inserted document ID: {document_id}")
    print(f"Inserted chunk ID: {chunk_id}")
    print(f"Inserted embedding ID: {embedding_id}")

    chunks = get_chunks()
    embeddings = get_embeddings()

    print("\nStored chunks:")

    for chunk in chunks:
        print(
            f"Chunk ID: {chunk['id']} | "
            f"Document ID: {chunk['document_id']} | "
            f"Text: {chunk['content']} | "
            f"Characters: {chunk['character_count']}"
        )

    print("\nStored embeddings:")

    for embedding in embeddings:
        print(
            f"Embedding ID: {embedding['id']} | "
            f"Chunk ID: {embedding['chunk_id']} | "
            f"Model: {embedding['model_name']} | "
            f"Dimension: {embedding['dimension']} | "
            f"Vector: {embedding['vector']}"
        )


if __name__ == "__main__":
    main()