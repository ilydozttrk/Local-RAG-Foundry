from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.document_manager import DocumentManager
from app.rag_pipeline import RAGPipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIRECTORY = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

rag_pipeline: RAGPipeline | None = None
rag_pipeline_lock = Lock()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[int] = Field(min_length=1)


class SourceResponse(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int | None = None
    filename: str | None = None
    file_type: str | None = None
    source_path: str | None = None
    content: str | None = None
    similarity_score: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]


def get_rag_pipeline() -> RAGPipeline:
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline(
            top_k=3,
            min_similarity_score=0.33,
        )
    return rag_pipeline


@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag_pipeline
    yield
    with rag_pipeline_lock:
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"name": "Local RAG API", "status": "running"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "application": "Local RAG AI Assistant"}


@app.get("/api/documents")
def list_documents():
    manager = DocumentManager()
    return [{
        "document_id": d["id"],
        "filename": d["filename"],
        "file_type": d["file_type"],
        "chunk_count": d["chunk_count"],
        "embedding_count": d["embedding_count"],
        "is_active": bool(d["is_active"]),
    } for d in manager.list_documents()]


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename provided.")

    safe_filename = Path(file.filename).name
    ext = Path(safe_filename).suffix.lower()

    if ext not in {".pdf", ".txt"}:
        raise HTTPException(400, "Only PDF and TXT files are supported.")

    destination = UPLOAD_DIRECTORY / safe_filename

    if destination.exists():
        raise HTTPException(
            status_code=409,
            detail="A file with the same name already exists.",
        )

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        manager = DocumentManager()
        result = manager.add_document(destination)

        if result["status"] == "failed":
            destination.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail=result["message"],
            )

        return result

    except HTTPException:
        raise
    except Exception as error:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {error}",
        ) from error
    finally:
        await file.close()


@app.post("/api/chat", response_model=ChatResponse)
def chat_with_documents(request: ChatRequest) -> ChatResponse:
    cleaned_question = request.question.strip()
    if not cleaned_question:
        raise HTTPException(400, "Question cannot be empty.")

    try:
        with rag_pipeline_lock:
            result = get_rag_pipeline().ask(
                question=cleaned_question,
                document_ids=request.document_ids,
            )
    except (TypeError, ValueError) as error:
        raise HTTPException(400, str(error)) from error
    except Exception as error:
        raise HTTPException(
            500,
            f"Answer generation failed: {error}",
        ) from error

    return ChatResponse(
        question=result["question"],
        answer=result["answer"],
        sources=[SourceResponse(**source) for source in result["sources"]],
    )