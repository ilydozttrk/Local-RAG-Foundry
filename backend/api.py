from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Local RAG API",
    description="API layer for the Local RAG AI Assistant.",
    version="0.1.0",
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