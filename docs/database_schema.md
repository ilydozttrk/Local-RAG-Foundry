# Database Schema

## Overview

The Local RAG AI Assistant stores documents, text chunks, and embedding vectors in a local SQLite database.

The database consists of three tables:

- documents
- chunks
- embeddings

The relationships are designed to support Retrieval-Augmented Generation (RAG) by organizing documents into chunks and associating each chunk with an embedding vector.

---

# Documents Table

Stores metadata about uploaded documents.

| Column | Type | Description |
|---------|------|-------------|
| id | INTEGER | Primary Key |
| filename | TEXT | Document filename |
| file_type | TEXT | File extension (pdf, txt, etc.) |
| source_path | TEXT | Local document path |
| created_at | TEXT | Insert timestamp |

---

# Chunks Table

Stores document chunks created during preprocessing.

| Column | Type | Description |
|---------|------|-------------|
| id | INTEGER | Primary Key |
| document_id | INTEGER | Foreign Key → documents.id |
| chunk_index | INTEGER | Chunk order |
| content | TEXT | Chunk text |
| character_count | INTEGER | Number of characters |
| created_at | TEXT | Insert timestamp |

---

# Embeddings Table

Stores vector embeddings generated from each chunk.

| Column | Type | Description |
|---------|------|-------------|
| id | INTEGER | Primary Key |
| chunk_id | INTEGER | Foreign Key → chunks.id |
| model_name | TEXT | Embedding model |
| dimension | INTEGER | Embedding dimension |
| vector | TEXT | JSON serialized embedding vector |
| created_at | TEXT | Insert timestamp |

---

# Relationships

documents

↓

1 → N

↓

chunks

↓

1 → N

↓

embeddings

Each document can contain multiple chunks.

Each chunk has one embedding for each embedding model used.

---

# Design Decisions

- SQLite is used because it is lightweight, serverless, and suitable for offline applications.
- Documents are separated from chunks to improve retrieval efficiency.
- Embeddings are stored independently from chunk content.
- Embedding vectors are serialized as JSON strings.
- The schema allows multiple embedding models for the same chunk.