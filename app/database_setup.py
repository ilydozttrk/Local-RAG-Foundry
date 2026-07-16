import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "rag_database.db"


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

    FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id)
        REFERENCES chunks(id)
        ON DELETE CASCADE,

    UNIQUE (chunk_id, model_name)
);
"""


def create_database() -> None:
    """Create the SQLite database and initialize the required tables."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")
            connection.executescript(SCHEMA)
            connection.commit()

        print(f"Database created successfully: {DATABASE_PATH}")
        print("Tables created or verified:")
        print("- documents")
        print("- chunks")
        print("- embeddings")

    except sqlite3.Error as error:
        raise RuntimeError(
            f"Database initialization failed: {error}"
        ) from error


if __name__ == "__main__":
    create_database()