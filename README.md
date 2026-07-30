<div align="center">

🧠 Local RAG AI Assistant

Ask questions across your own documents — locally, privately, and with sources.

<p>
  A full-stack Retrieval-Augmented Generation application powered by
  <strong>Microsoft Foundry Local</strong>.
</p>



</div>

📑 Table of Contents

Project

Setup & Usage

✦ Overview

🚀 Installation

⚡ Features

▶️ Running the Application

🏗️ Architecture

💬 Usage

🧩 Source-Aware Context

⚙️ Retrieval Configuration

🛠️ Technology Stack

✅ Validation

⚠️ Known Limitations

🗺️ Roadmap

🔐 Privacy

📚 Project Background

📄 License



✦ Overview

Local RAG AI Assistant is a local-first document question-answering system. It parses PDF and TXT files, divides their content into overlapping chunks, generates embeddings, retrieves the most relevant passages, and asks a locally running language model to answer using only that context.

The application is designed around three principles:

Local processing — documents and prompts are processed on the user's device.

Grounded generation — answers are produced from retrieved document passages.

Source transparency — retrieved sources and similarity scores are shown with the answer.

Current release: v0.1 — the complete document-to-answer pipeline is implemented and manually verified.

<br>

<!-- Replace these files with clean screenshots using the same paths. -->

<table>
  <tr>
    <td align="center">
      <img src="docs/screenshots/app-overview.png" alt="Local RAG application overview" width="100%">
      <br>
      <sub><b>Local knowledge base and document selection</b></sub>
    </td>
    <td align="center">
      <img src="docs/screenshots/grounded-answer.png" alt="Grounded answer with source cards" width="100%">
      <br>
      <sub><b>Generated answer with retrieved sources</b></sub>
    </td>
  </tr>
</table>

⚡ Features

<table>
<tr>
<td width="50%" valign="top">

📄 Document Pipeline

PDF and TXT ingestion

Shared text normalization

Overlapping text chunking

Local embedding generation

Normalized source paths

SQLite document storage

</td>
<td width="50%" valign="top">

🔎 Semantic Retrieval

Cosine-similarity search

Multi-document filtering

Configurable relevance threshold

Structured source context

Similarity scores

Controlled fallback responses

</td>
</tr>
<tr>
<td width="50%" valign="top">

🛡️ Local-First AI

Microsoft Foundry Local inference

Phi-4 Mini chat model

No cloud model API required

Local document processing

Local knowledge base

Privacy-oriented workflow

</td>
<td width="50%" valign="top">

🖥️ Full-Stack Interface

FastAPI backend

React + TypeScript frontend

Multiple document selection

Markdown answer rendering

Source cards

Loading and error states

</td>
</tr>
</table>

🏗️ Architecture

flowchart TB
    subgraph Ingestion["Document Ingestion"]
        A["PDF / TXT"] --> B["Parse & Normalize"]
        B --> C["Create Chunks"]
        C --> D["Generate Embeddings"]
        D --> E[("SQLite Knowledge Base")]
    end

    subgraph QuestionAnswering["Question Answering"]
        F["User Question"] --> G["Query Embedding"]
        G --> H["Semantic Retrieval"]
        E --> H
        H --> I["Context Builder"]
        I --> J["Foundry Local LLM"]
        J --> K["Answer + Sources"]
    end

Ingestion pipeline

PDF / TXT
   │
   ▼
Parse & normalize text
   │
   ▼
Create overlapping chunks
   │
   ▼
Generate local embeddings
   │
   ▼
Store documents, chunks and metadata in SQLite

Chunking setting

Default

Chunk size

600

Overlap

80

Minimum chunk size

50

Retrieval pipeline

The user selects one or more indexed documents.

The question is converted into an embedding.

Retrieval is limited to the selected document IDs.

Cosine similarity scores are calculated.

Passages below the relevance threshold are removed.

Relevant chunks are converted into structured context.

Phi-4 Mini generates an answer using that context.

The completed answer and its source cards are returned to the interface.

If no sufficiently relevant passage is found, the system returns a controlled fallback instead of asking the model to guess.

🧩 Source-Aware Context

Retrieved passages are sent to the model in structured source blocks:

<SOURCE_1>
filename: example.pdf
source_path: data/uploads/example.pdf
document_id: 1
chunk_index: 3
similarity_score: 0.82

Retrieved document content...
</SOURCE_1>

This format preserves provenance throughout the RAG pipeline and makes it possible to verify whether the displayed source matches the context used to produce the answer.

🛠️ Technology Stack

Layer

Technology

Local inference

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

Documents

PDF, TXT

🚀 Installation

Prerequisites

Before starting, install:

Python 3.12

Node.js and npm

Git

Microsoft Foundry Local

The local models configured for the project

1. Clone the repository

git clone https://github.com/ilydozttrk/Local-RAG-Foundry.git
cd Local-RAG-Foundry

2. Create a virtual environment

<details>
<summary><b>Windows PowerShell</b></summary>

python -m venv .venv
.\.venv\Scripts\Activate.ps1

</details>

<details>
<summary><b>macOS / Linux</b></summary>

python3 -m venv .venv
source .venv/bin/activate

</details>

3. Install backend dependencies

pip install -r requirements.txt

4. Verify Foundry Local

foundry service status
foundry model list

Foundry Local model aliases and execution providers may vary depending on the installed version and available hardware.

5. Install frontend dependencies

cd frontend
npm install

▶️ Running the Application

The backend and frontend run in separate terminals.

Terminal 1 — Backend

From the repository root:

.\.venv\Scripts\Activate.ps1
uvicorn backend.api:app --reload

Service

Address

FastAPI backend

http://127.0.0.1:8000

Interactive API docs

http://127.0.0.1:8000/docs

Terminal 2 — Frontend

cd frontend
npm run dev

Open http://localhost:5173 in the browser.

If Vite selects another port, make sure the backend CORS configuration permits that frontend origin.

💬 Usage

Start Microsoft Foundry Local and the required models.

Run the FastAPI backend.

Run the React frontend.

Upload one or more PDF or TXT files.

Wait for local indexing to finish.

Select the documents you want to search.

Ask a question whose answer appears in those documents.

Review the generated answer and retrieved source cards.

For the best results, use text-based PDFs with extractable content.

⚙️ Retrieval Configuration

Setting

Purpose

top_k

Maximum number of chunks returned

min_similarity_score

Minimum accepted relevance score

document_ids

Documents included in the search

Chunk size

Amount of text stored in each chunk

Overlap

Context shared between adjacent chunks

These values should be calibrated with controlled retrieval tests. Changing them without evaluation may reduce answer quality or introduce irrelevant context.

✅ Validation

The v0.1 release was manually verified with:

PDF and TXT ingestion

normalized source_path values

chunk and embedding count checks

relevant and unrelated questions

retrieval and source matching

hallucination fallback behavior

multi-document queries

empty questions and missing document selection

unsupported, empty, and corrupted documents

frontend loading and controlled error states

responsive interface behavior

complete document-to-answer workflows

No critical issue remained after the final manual smoke tests. An automated test suite is planned for a future release.

⚠️ Known Limitations

Large documents take longer to ingest because parsing, chunking, and embedding generation run locally.

Processing speed depends on document size, chunk count, model selection, and available hardware.

Phi-4 Mini is lightweight, but its answer quality is more limited than larger models.

Direct cosine-similarity search may become slower as the knowledge base grows.

Only PDF and TXT files are supported.

Image-only scanned PDFs require OCR, which is not included in v0.1.

The current release is intended primarily for local, single-user usage.

🗺️ Roadmap

Compare Phi-4 Mini with larger local models

Add hybrid semantic and keyword retrieval

Add a reranking stage

Support OCR for scanned PDFs

Add conversation memory

Add background document indexing

Display detailed ingestion progress

Build an automated retrieval evaluation suite

Add approximate nearest-neighbor search

Provide Docker-based installation

🔐 Privacy

Uploaded documents, generated embeddings, retrieved passages, and model prompts are processed on the user's device. Generated databases, uploaded documents, environment files, and secrets should not be committed to version control.

📚 Project Background

This application was developed as a 20-day computer engineering internship project focused on:

Retrieval-Augmented Generation

offline and local AI systems

semantic search

backend and frontend integration

prompt grounding

source-aware generation

The project evolved from an initial RAG prototype into a complete FastAPI and React application with local inference and end-to-end document retrieval.

📄 License

This project is available under the MIT License.

<div align="center">

<br>

Local inference. Grounded answers. Your documents.

<sub>Developed by <a href="https://github.com/ilydozttrk">İlayda Öztürk</a></sub>

</div>
