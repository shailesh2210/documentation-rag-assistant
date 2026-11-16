import time
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import CONFIG
from .graph import run_query
from .retrieval import indexed_documents

app = FastAPI(title="Commtel Local RAG Assistant", version="1.0.0")

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents")
def documents():
    try:
        docs = indexed_documents()
        stamp = (Path(CONFIG["paths"]["index_dir"]) / "chunks.faiss").stat().st_mtime
        return {"documents": docs, "ingestion_timestamp": stamp}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Index is not ready; run ingest.py first.") from exc

@app.post("/query")
def query(payload: QueryRequest):
    request_id = str(uuid.uuid4())
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question must not be blank.")
    started = time.perf_counter()
    try:
        result = run_query(question)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Local RAG workflow failed.") from exc
    return {"request_id": request_id, "answer": result.get("answer", ""),
            "refused": bool(result.get("refused", False)), "citations": result.get("citations", []),
            "retrieved": [x["chunk_id"] for x in result.get("retrieved", [])],
            "retained": [x["chunk_id"] for x in result.get("retained", [])],
            "verified": result.get("verified"), "retries": result.get("retries", 0),
            "termination": result.get("termination", "unknown"),
            "latency_s": time.perf_counter() - started}
