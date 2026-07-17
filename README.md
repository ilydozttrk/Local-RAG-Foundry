# Local RAG AI Assistant with Microsoft Foundry Local

## Overview

This project aims to develop a local-first Retrieval-Augmented Generation (RAG) AI Assistant using Microsoft Foundry Local.

The assistant retrieves relevant information from a local knowledge base and generates context-grounded responses using a locally running language model. After the required models and dependencies are downloaded, normal inference does not require a cloud LLM API.

This project is being developed as part of the Microsoft AI Innovators Summer School and an undergraduate software engineering internship.

---

## Project Goal

The main goal of this project is to design and implement a local RAG architecture that combines document retrieval, semantic search, and local language model inference.

The system is designed to process local documents, divide them into text chunks, generate embeddings, store document data locally, retrieve relevant context for user queries, and generate grounded answers through Microsoft Foundry Local.

A key architectural objective is to reduce hallucination by validating retrieval results before calling the local language model. If sufficient relevant context cannot be retrieved, the application is designed to return a fallback response instead of allowing the model to generate an unsupported answer.

The project emphasizes privacy, offline inference, modular software architecture, and reproducible local AI workflows.

---

## Features

- Local-first RAG architecture
- Local LLM inference with Microsoft Foundry Local
- PDF and TXT document processing
- Text chunking pipeline
- Document and query embedding generation
- Local SQLite storage
- Semantic retrieval using cosine similarity
- Top-K relevant chunk selection
- Retrieval relevance threshold validation
- Hallucination reduction through context-grounded prompting
- Fallback response when sufficient context is unavailable
- Streamlit-based user interface
- Local document metadata and text chunk management
- Source metadata support for generated answers

---

## Tech Stack

- Python 3.12
- Microsoft Foundry Local
- Foundry Local Python SDK
- Local Language Models
- Embedding Models
- SQLite
- Streamlit
- Cosine Similarity
- Git
- GitHub
- NumPy
- pypdf

---

## Installation

### Clone the repository

```bash
git clone https://github.com/ilydozttrk/Local-RAG-Foundry.git
cd Local-RAG-Foundry
```

### Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install Microsoft Foundry Local

Install Microsoft Foundry Local and download the required local language model and embedding model before running the application.

### Verify the installation

```bash
python app/hello_model.py
```

If the installation is successful, the local model should generate a response.

---

## Usage

Run the individual modules during development.

### Initialize the database

```bash
python app/database_setup.py
```

### Test database operations

```bash
python app/database_manager.py
```

### Test document chunking

```bash
python app/chunking.py
```

### Run the local model

```bash
python app/hello_model.py
```

Future versions will provide a unified application entry point through `main.py`.

### Typical Development Workflow (Current Version)

During development, the modules can be executed in the following order:

```bash
python app/database_setup.py

python app/chunking.py

python app/database_manager.py

python app/hello_model.py
```

## Current Status

### Week 1

- [x] Project initialized
- [x] Development environment configured
- [x] Python virtual environment created
- [x] Microsoft Foundry Local installed and configured
- [x] Project structure created
- [x] Local model downloaded and loaded
- [x] First local model inference completed
- [x] Foundry Local SDK integration tested
- [x] Prompt engineering experiments completed
- [x] System and user prompt behavior analyzed
- [x] Context-grounded prompting tested
- [x] Hallucination behavior analyzed
- [x] Few-shot prompting tested
- [x] Final software architecture designed

### Week 2 🚧

- [x] Document parsing
- [x] PDF/TXT reader
- [x] Chunking pipeline
- [x] SQLite database design
- [x] SQLite database initialization
- [x] SQLite storage layer
- [x] Database query operations
- [ ] Embedding model integration
- [ ] Complete ingestion pipeline

---

## Project Structure

```text
Local-RAG-Foundry/
│
├── app/
│   ├── __init__.py
│   ├── hello_model.py
│   ├── prompt_experiments.py
│   ├── chunking.py
│   ├── database_setup.py
│   └── database_manager.py
│
├── data/
│   ├── rag_database.db
│   └── sample.txt
│
├── docs/
│   ├── Database_Schema.drawio
│   └── Local_RAG_Final_Software_Architecture.drawio
│
├── prompts/
│
├── tests/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```
---

### Folder Responsibilities

- `app/` - Core application modules and local model experiments
- `data/` - Local documents, application data, and future database files
- `docs/` - Software architecture and project documentation
- `prompts/` - Reusable system and RAG prompt templates
- `tests/` - Unit and integration tests

---

## Software Architecture

The project consists of two main pipelines.

---

## Database Structure

The application stores documents, text chunks, and embeddings in a local SQLite database.

The database schema follows a normalized three-table design:

```text
documents
     │
     ▼
chunks
     │
     ▼
embeddings
```

---

### documents

| Column | Description |
|----------|-------------|
| id | Primary key |
| filename | Original document name |
| file_type | Document type |
| source_path | Local document path |
| created_at | Creation timestamp |

### chunks

| Column | Description |
|----------|-------------|
| id | Primary key |
| document_id | Related document |
| chunk_index | Chunk order |
| content | Chunk text |
| character_count | Number of characters |
| created_at | Creation timestamp |

### embeddings

| Column | Description |
|----------|-------------|
| id | Primary key |
| chunk_id | Related chunk |
| model_name | Embedding model |
| dimension | Embedding size |
| vector | Serialized embedding |
| created_at | Creation timestamp |

--- 

### Ingestion Pipeline

```text
PDF / TXT Documents
        |
        v
Document Parsing
        |
        v
Text Chunking
        |
        v
Document Embedding Generation
        |
        v
SQLite Storage
```

The ingestion pipeline processes local documents, divides the extracted text into smaller chunks, generates embedding vectors, and stores document metadata, text chunks, and serialized embeddings in SQLite.

### Query and Response Pipeline

```text
User Query
    |
    v
Query Processing
    |
    v
Query Embedding Generation
    |
    v
Semantic Retrieval
    |
    v
Cosine Similarity + Top-K Selection
    |
    v
Similarity Score >= Threshold?
       / \
     Yes  No
      |    |
      |    `--> Fallback Response
      |         LLM Not Called
      v
Context Builder
      |
      v
Prompt Assembly
      |
      v
Microsoft Foundry Local
Local Chat LLM
      |
      v
Generated Answer + Source Metadata
```

The query pipeline retrieves relevant context before invoking the local language model. Retrieval results are validated using a similarity threshold. If sufficient context is unavailable, the system returns a fallback response without calling the LLM.

The complete software architecture is available in:

docs/Local_RAG_Final_Software_Architecture.drawio

---

## Prompt Engineering Experiments

Initial prompt engineering experiments were conducted using a locally running Qwen2.5 0.5B model through Microsoft Foundry Local.

The experiments compared:

1. User prompt only
2. System prompt and user prompt
3. Context-grounded prompting
4. Rule-based hallucination reduction
5. Few-shot hallucination reduction

The experiments demonstrated that prompt instructions alone were not sufficient to completely prevent hallucination in the tested small language model.

When explicit context was provided, the model produced the correct database information. However, when the requested information was absent from the context, the model still generated unsupported cloud provider names despite strict answer rules.

These observations directly influenced the final software architecture. A retrieval validation layer was added so that the application can return a fallback response before calling the LLM when sufficient relevant context is unavailable.

---

## Roadmap

- Week 1 - RAG foundations, Foundry Local setup, local inference, prompt engineering, and software architecture
- Week 2 - Document processing, text chunking, embeddings, and SQLite storage
- Week 3 - Semantic retrieval, cosine similarity, Top-K selection, and RAG pipeline integration
- Week 4 - Streamlit interface, testing, optimization, documentation, and final project delivery

---

## Offline Usage

The application follows a local-first architecture.

Initial setup, dependency installation, and model download may require an internet connection. After the required resources are available locally, normal application inference is designed to run without a cloud LLM API.

---

## Development Progress

| Week | Status |
|------|--------|
| Week 1 | ✅ Completed |
| Week 2 | 🚧 In Progress |
| Week 3 | ⏳ Planned |
| Week 4 | ⏳ Planned |

---

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.