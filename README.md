Local RAG AI Assistant

A fully local Retrieval-Augmented Generation application for asking questions over PDF and TXT documents using Microsoft Foundry Local.



About

Local RAG AI Assistant is a full-stack application that retrieves relevant passages from user-selected documents and uses a local language model to generate source-grounded answers.

The entire pipeline runs on the user's device:

Document → Parse → Chunk → Embed → Store → Retrieve → Generate

Documents, embeddings, retrieved context, and model prompts are processed locally without a cloud inference API.

Features

PDF and TXT document ingestion

Text normalization and overlapping chunk generation

Local embedding generation

SQLite storage for documents, chunks, and embeddings

Document-filtered semantic search using cosine similarity

Configurable Top-K retrieval and similarity threshold

Grounded prompt construction with source metadata

Local inference through Microsoft Foundry Local

FastAPI backend

React, TypeScript, and Vite frontend

Multi-document selection

Markdown answer rendering

Retrieved source cards with similarity scores

Controlled fallback for unrelated questions

Architecture

flowchart TD
    A["PDF / TXT"] --> B["Parse and normalize"]
    B --> C["Create chunks"]
    C --> D["Generate embeddings"]
    D --> E[("SQLite")]
    F["User question"] --> G["Query embedding"]
    E --> H["Semantic retrieval"]
    G --> H
    H --> I["Context and prompt"]
    I --> J["Foundry Local / Phi-4 Mini"]
    J --> K["Answer and sources"]

Ingestion

The uploaded document is validated and parsed.

Extracted text is normalized.

Text is divided into overlapping chunks.

A local embedding is generated for each chunk.

Document metadata, chunks, and embeddings are stored in SQLite.

Default chunking configuration:

Setting

Value

Chunk size

600

Overlap

80

Minimum chunk size

50

Retrieval and generation

The user selects one or more indexed documents.

The question is converted into an embedding.

Retrieval is restricted to the selected document IDs.

Candidate chunks are ranked using cosine similarity.

Chunks below the minimum similarity threshold are excluded.

Relevant passages and their metadata are added to the prompt.

Phi-4 Mini generates an answer using the retrieved context.

The completed answer and its sources are returned to the interface.

If no sufficiently relevant passage is found, the application returns a controlled fallback instead of asking the model to guess.

Tech Stack

Layer

Technology

Local model runtime

Microsoft Foundry Local

Chat model

Phi-4 Mini

Backend

Python 3.12, FastAPI

Frontend

React, TypeScript, Vite

Database

SQLite

Retrieval

Local embeddings, cosine similarity

Supported files

PDF, TXT

Installation

Prerequisites

Python 3.12

Node.js and npm

Git

Microsoft Foundry Local

Compatible local chat and embedding models

1. Clone the repository

git clone https://github.com/ilydozttrk/Local-RAG-Foundry.git
cd Local-RAG-Foundry

2. Create a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

macOS or Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Install backend dependencies

pip install -r requirements.txt

4. Verify Foundry Local

foundry service status
foundry model list

Model aliases and execution providers may differ depending on the installed Foundry Local version and available hardware.

5. Install frontend dependencies

cd frontend
npm install

Running the Application

Run the backend and frontend in separate terminals.

Backend

From the repository root:

.\.venv\Scripts\Activate.ps1
uvicorn backend.api:app --reload

The API and interactive documentation are available at:

API: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

Frontend

cd frontend
npm run dev

Open http://localhost:5173.

If Vite selects a different port, ensure that the backend CORS configuration permits that origin.

Usage

Start Microsoft Foundry Local and the required models.

Start the FastAPI backend.

Start the React frontend.

Upload one or more PDF or TXT documents.

Wait for indexing to complete.

Select the documents to search.

Ask a question based on their contents.

Review the generated answer and retrieved sources.

Text-based PDFs with extractable content provide the best results. Image-only scanned PDFs require OCR, which is not included in the current release.

Validation

Version v0.1 was manually verified with:

PDF and TXT ingestion

chunk and embedding count checks

normalized source_path values

relevant and unrelated questions

retrieval and source matching

hallucination fallback behavior

multi-document retrieval

empty and invalid inputs

unsupported and corrupted files

frontend loading and error states

complete document-to-answer workflows

Automated tests are not included in v0.1.

Known Limitations

Large documents take longer to ingest because processing runs locally.

Performance depends on document size, chunk count, model selection, hardware, and execution provider.

Phi-4 Mini's answer quality depends on the retrieved context and prompt constraints.

Direct cosine similarity may become slower as the knowledge base grows.

Only PDF and TXT files are currently supported.

Scanned PDFs require a separate OCR stage.

The current release is intended for local, single-user use.

Roadmap

Add hybrid semantic and keyword retrieval

Add a reranking stage

Add OCR support

Add conversation memory

Add background indexing and progress reporting

Add automated retrieval evaluation

Add approximate nearest-neighbor search

Add Docker-based setup

Privacy

Uploaded documents, embeddings, retrieved passages, and prompts are processed on the user's device. Generated databases, uploaded files, environment files, and secrets should not be committed to version control.

License

This project is licensed under the MIT License.

Author

İlayda Öztürk