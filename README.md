<h1 align="center">Local RAG AI Assistant with Microsoft Foundry Local</h1>

<p align="center">
  A privacy-first, fully local Retrieval-Augmented Generation assistant for grounded question answering over PDF and TXT documents.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/Microsoft-Foundry%20Local-0078D4?style=for-the-badge&logo=microsoft&logoColor=white" alt="Microsoft Foundry Local"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React and TypeScript"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Status-v0.1-success?style=for-the-badge" alt="Status v0.1"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
</p>

Overview

Local RAG AI Assistant is a full-stack application that answers questions using information retrieved from user-selected documents. Parsing, chunking, embedding generation, retrieval, prompt construction, and language-model inference all run locally.

The project combines:

a Python and FastAPI backend,

a React, Vite, and TypeScript frontend,

SQLite document storage,

a local embedding model,

and a local LLM served through Microsoft Foundry Local.

This local-first design keeps uploaded documents and model requests on the user's device while providing source-aware, grounded answers without a cloud inference API.

Key Features

Fully local RAG workflow

PDF and TXT document ingestion

Shared text normalization for parsed documents

Configurable overlapping chunk generation

Local embedding generation

SQLite storage for documents, chunks, and embeddings

Document-filtered semantic retrieval using cosine similarity

Configurable Top-K retrieval and minimum similarity threshold

Structured context with source metadata

Grounded prompt instructions designed to reduce hallucinations

Local streaming response generation

FastAPI backend

Modern React chat interface

Multiple document selection

Markdown answer rendering

Source cards for retrieved evidence

Upload, loading, auto-scroll, responsive layout, and controlled error states

Current Status

Component

Status

PDF and TXT parsing

✅

Text normalization and chunking

✅

Local embeddings

✅

SQLite storage

✅

Semantic retrieval

✅

Similarity threshold and document filtering

✅

Context and prompt construction

✅

Local response generation

✅

FastAPI integration

✅

React frontend

✅

Source display and multi-document queries

✅

End-to-end and resilience smoke tests

✅

Initial release

v0.1

Architecture

flowchart TD
    A["PDF / TXT Upload"] --> B["Parse & Normalize"]
    B --> C["Chunk Text"]
    C --> D["Generate Local Embeddings"]
    D --> E["SQLite Knowledge Base"]
    F["User Question"] --> G["Query Embedding"]
    E --> H["Filtered Semantic Retrieval"]
    G --> H
    H --> I["Context & Prompt Builder"]
    I --> J["Microsoft Foundry Local LLM"]
    J --> K["Streamed Answer & Sources"]

Ingestion flow

The user uploads a PDF or TXT document.

The backend validates and parses the file.

Extracted text is normalized.

Text is split into overlapping chunks.

A local embedding is generated for every chunk.

Document metadata, chunks, and embeddings are stored in SQLite.

Default chunking values:

Setting

Value

Chunk size

600

Overlap

80

Minimum chunk size

50

Query flow

The user selects one or more indexed documents and submits a question.

The question is converted into an embedding with the same embedding model used during ingestion.

Candidate chunks are filtered to the selected document IDs.

Cosine similarity scores are calculated and ranked.

Results below min_similarity_score are excluded.

Retrieved chunks are converted into structured source blocks.

The prompt instructs the model to answer only from the provided context and preserve the user's language.

The local model streams the answer to the frontend.

The interface displays the answer together with its source cards.

When no sufficiently relevant chunk is available, the pipeline returns a controlled fallback instead of asking the model to guess.

Context and Grounding

Each retrieved passage is passed to the model in an explicit source block:

<SOURCE_1>
filename: ...
source_path: ...
document_id: ...
chunk_index: ...
similarity_score: ...

Retrieved document content...
</SOURCE_1>

This structure preserves provenance and makes it easier to verify that the displayed source matches the context used to produce an answer.

Technology Stack

Layer

Technology

Local model runtime

Microsoft Foundry Local

Backend

Python 3.12, FastAPI

Frontend

React, Vite, TypeScript

Database

SQLite

Retrieval

Local embeddings, cosine similarity

Current chat model

Qwen2.5-0.5B

Supported documents

PDF, TXT

Installation

Prerequisites

Python 3.12

Node.js and npm

Git

Microsoft Foundry Local

A compatible local chat model and embedding model

1. Clone the repository

git clone https://github.com/ilydozttrk/Local-RAG-Foundry.git
cd Local-RAG-Foundry

2. Create and activate a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

macOS or Linux:

python3 -m venv .venv
source .venv/bin/activate

3. Install backend dependencies

pip install -r requirements.txt

4. Verify Microsoft Foundry Local

foundry service status
foundry model list

Download or start the models configured by the project before launching the backend. Model aliases and commands may differ between Foundry Local versions and hardware configurations.

5. Install frontend dependencies

cd frontend
npm install

Running the Application

Use two terminals so the backend and frontend can run together.

Backend

From the repository root, activate the virtual environment and start the configured FastAPI application.

python main.py

The API is expected to be available at:

http://127.0.0.1:8000

Frontend

cd frontend
npm run dev

Vite normally serves the interface at:

http://localhost:5173

If Vite chooses another port because 5173 is already in use, ensure that the backend CORS configuration allows the selected frontend origin.

Usage

Start Microsoft Foundry Local and the required models.

Start the FastAPI backend.

Start the React frontend.

Upload one or more PDF or TXT documents.

Wait until indexing is complete.

Select the documents to use.

Ask a question whose answer is contained in the selected documents.

Review the generated answer and source cards.

For best results, use text-based PDFs with extractable content. Scanned image-only PDFs require OCR, which is not part of the current release.

Retrieval Configuration

Retrieval behavior can be calibrated through:

top_k — maximum number of candidate chunks returned,

min_similarity_score — minimum relevance score required for a chunk,

document_ids — selected documents used to constrain the search,

chunk size and overlap — ingestion-time settings that affect retrieval granularity.

These values should be adjusted using controlled test documents rather than changed without evaluation.

Validation

The v0.1 pipeline was verified with:

PDF and TXT uploads,

chunk and embedding count checks,

normalized source_path values,

relevant and unrelated questions,

retrieval accuracy and source matching,

hallucination fallback behavior,

multi-document retrieval,

empty or invalid input scenarios,

unsupported and corrupted files,

loading and error states,

responsive frontend behavior,

and end-to-end document-to-answer workflows.

No critical issue remained after the final smoke tests.

Known Limitations

Ingestion time increases for large documents because parsing, chunking, and embedding generation are performed entirely on the local device.

Processing speed depends on document size, generated chunk count, model choice, and available hardware.

The current Qwen2.5-0.5B chat model is lightweight and suitable for local testing, but answer quality is more limited than with larger models.

Semantic retrieval currently uses direct cosine similarity and may become slower as the knowledge base grows substantially.

Only PDF and TXT ingestion are supported.

Image-only scanned PDFs are not processed without a separate OCR stage.

The application is intended for local development and single-user use in its current form.

Future Improvements

Compare Phi-4 Mini and larger Qwen models using the same evaluation questions

Add hybrid semantic and keyword retrieval

Add reranking for retrieved chunks

Add OCR support for scanned PDFs

Add conversation memory

Add incremental and background indexing

Add ingestion progress reporting for large documents

Add an automated retrieval evaluation suite

Add approximate nearest-neighbor search for larger collections

Add Docker-based setup and packaging

Privacy

The system is designed to run locally. Uploaded documents, embeddings, retrieved context, and prompts are processed on the user's machine. Users should still review their own environment, model configuration, logs, and repository contents before working with sensitive documents.

Generated databases, uploaded documents, environment files, and secrets should not be committed to version control.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements

Developed as a 20-day internship project focused on offline AI, Retrieval-Augmented Generation, and Microsoft Foundry Local.

<div align="center">
  Built with Microsoft Foundry Local, Python, FastAPI, React, and SQLite.
</div>