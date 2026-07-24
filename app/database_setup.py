import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "rag_database.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    source_path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    character_count INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chunks_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_chunks_document_index
        UNIQUE (document_id, chunk_index),

    CONSTRAINT ck_chunks_chunk_index
        CHECK (chunk_index >= 0),

    CONSTRAINT ck_chunks_character_count
        CHECK (character_count >= 0)
);

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_embeddings_chunk
        FOREIGN KEY (chunk_id)
        REFERENCES chunks(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_embeddings_chunk_model
        UNIQUE (chunk_id, model_name),

    CONSTRAINT ck_embeddings_dimension
        CHECK (dimension > 0)
);

CREATE INDEX IF NOT EXISTS idx_documents_filename
    ON documents(filename);

CREATE INDEX IF NOT EXISTS idx_documents_file_type
    ON documents(file_type);

CREATE INDEX IF NOT EXISTS idx_documents_created_at
    ON documents(created_at);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id
    ON chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_document_index
    ON chunks(document_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id
    ON embeddings(chunk_id);

CREATE INDEX IF NOT EXISTS idx_embeddings_model_name
    ON embeddings(model_name);

CREATE INDEX IF NOT EXISTS idx_embeddings_model_chunk
    ON embeddings(model_name, chunk_id);
"""


def connect_database() -> sqlite3.Connection:
    """Create a configured SQLite connection for database setup."""

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")

    return connection


def verify_foreign_keys(
    connection: sqlite3.Connection,
) -> None:
    """Verify that SQLite foreign-key enforcement is enabled."""

    result = connection.execute(
        "PRAGMA foreign_keys;"
    ).fetchone()

    if result is None or result[0] != 1:
        raise RuntimeError(
            "SQLite foreign-key enforcement could not be enabled."
        )


def verify_database_integrity(
    connection: sqlite3.Connection,
) -> None:
    """Run SQLite integrity and foreign-key checks."""

    integrity_result = connection.execute(
        "PRAGMA integrity_check;"
    ).fetchone()

    if (
        integrity_result is None
        or integrity_result[0].lower() != "ok"
    ):
        raise RuntimeError(
            "SQLite database integrity check failed."
        )

    foreign_key_violations = connection.execute(
        "PRAGMA foreign_key_check;"
    ).fetchall()

    if foreign_key_violations:
        raise RuntimeError(
            "SQLite foreign-key violations were detected: "
            f"{foreign_key_violations}"
        )


def get_table_names(
    connection: sqlite3.Connection,
) -> list[str]:
    """Return the application table names stored in the database."""

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    return [row[0] for row in rows]


def get_index_names(
    connection: sqlite3.Connection,
) -> list[str]:
    """Return the custom index names stored in the database."""

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    return [row[0] for row in rows]


def create_database() -> None:
    """Create and verify the Local RAG SQLite database."""

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with connect_database() as connection:
            verify_foreign_keys(connection)

            connection.executescript(SCHEMA)
            connection.commit()

            verify_database_integrity(connection)

            table_names = get_table_names(connection)
            index_names = get_index_names(connection)

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Database initialization failed: {error}"
        ) from error

    print("=" * 80)
    print("DATABASE INITIALIZATION")
    print("=" * 80)
    print(f"Database path: {DATABASE_PATH}")
    print("Database created or verified successfully.")

    print("\nTables:")

    for table_name in table_names:
        print(f"- {table_name}")

    print("\nIndexes:")

    for index_name in index_names:
        print(f"- {index_name}")

    print("\nConfiguration:")
    print("- Foreign keys: enabled")
    print("- Delete cascade: enabled")
    print("- Journal mode: WAL")
    print("- Integrity check: passed")


if __name__ == "__main__":
    create_database()