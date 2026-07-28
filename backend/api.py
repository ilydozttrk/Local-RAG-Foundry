from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
import shutil

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.document_manager import DocumentManager
from app.rag_pipeline import RAGPipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIRECTORY = PROJECT_ROOT / "data" / "uploads"

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


rag_pipeline: RAGPipeline | None = None
rag_pipeline_lock = Lock()


class ChatRequest(BaseModel):
    """Represent a chat request sent by the frontend."""

    question: str = Field(
        min_length=1,
        max_length=4000,
    )

    document_ids: list[int] = Field(
        min_length=1,
    )


class SourceResponse(BaseModel):
    """Represent one retrieved source passage."""

    document_id: int
    chunk_id: int
    chunk_index: int | None = None
    filename: str | None = None
    file_type: str | None = None
    source_path: str | None = None
    content: str | None = None
    similarity_score: float


class ChatResponse(BaseModel):
    """Represent a complete RAG response."""

    question: str
    answer: str
    sources: list[SourceResponse]


def get_rag_pipeline() -> RAGPipeline:
    """Create or return the shared RAG pipeline."""

    global rag_pipeline

    if rag_pipeline is None:
        rag_pipeline = RAGPipeline(
            top_k=3, 
            min_similarity_score=0.33,)

    return rag_pipeline


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application-level resources."""

    yield

    global rag_pipeline

    if rag_pipeline is not None:
        rag_pipeline.close()
        rag_pipeline = None


app = FastAPI(
    title="Local RAG API",
    description="API layer for the Local RAG AI Assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return basic API information."""

    return {
        "name": "Local RAG API",
        "status": "running",
    }


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Return the current API health status."""

    return {
        "status": "healthy",
        "application": "Local RAG AI Assistant",
    }

@app.get("/api/documents")
def list_documents() -> list[dict]:
    """Return all stored documents."""

    manager = DocumentManager()

    documents = manager.list_documents()

    return [
        {
            "document_id": document["id"],
            "filename": document["filename"],
            "file_type": document["file_type"],
            "chunk_count": document["chunk_count"],
            "embedding_count": document["embedding_count"],
            "is_active": bool(document["is_active"]),
        }
        for document in documents
    ]


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """Upload and ingest a supported document."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    safe_filename = Path(file.filename).name
    file_extension = Path(safe_filename).suffix.lower()

    if file_extension not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    destination = UPLOAD_DIRECTORY / safe_filename

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "The uploaded file could not be saved: "
                f"{error}"
            ),
        ) from error

    finally:
        await file.close()

    manager = DocumentManager()
    result = manager.add_document(destination)

    if result["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail=result["message"],
        )

    return result


@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
def chat_with_documents(
    request: ChatRequest,
) -> ChatResponse:
    """Answer a question using selected local documents."""

    cleaned_question = request.question.strip()

    if not cleaned_question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        # The local model is shared by the API. The lock prevents
        # simultaneous requests from using the same pipeline instance.
        with rag_pipeline_lock:
            pipeline = get_rag_pipeline()
            result = pipeline.ask(
                question=cleaned_question,
                document_ids=request.document_ids,
            )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except TypeError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {error}",
        ) from error

    return ChatResponse(
        question=result["question"],
        answer=result["answer"],
        sources=[
            SourceResponse(
                document_id=source["document_id"],
                chunk_id=source["chunk_id"],
                chunk_index=source.get("chunk_index"),
                filename=source.get("filename"),
                file_type=source.get("file_type"),
                source_path=source.get("source_path"),
                content=source.get("content"),
                similarity_score=source["similarity_score"],
            )
            for source in result["sources"]
        ],
    )