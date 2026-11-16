from pathlib import Path
import json
import faiss
from .config import CONFIG
from .models import embed_texts

def build_index(chunks):
    vectors = embed_texts([x["text"] for x in chunks]).astype("float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    out = Path(CONFIG["paths"]["index_dir"]); out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "chunks.faiss"))
    (out / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

def load_index():
    out = Path(CONFIG["paths"]["index_dir"])
    if not (out / "chunks.faiss").exists() or not (out / "chunks.json").exists():
        raise RuntimeError("Index missing; run python ingest.py first.")
    return faiss.read_index(str(out / "chunks.faiss")), json.loads((out / "chunks.json").read_text(encoding="utf-8"))

def retrieve(question, top_k=None):
    index, chunks = load_index()
    q = embed_texts([question]).astype("float32")
    k = min(top_k or CONFIG["retrieval"]["top_k"], len(chunks))
    scores, ids = index.search(q, k)
    out = []
    for score, idx in zip(scores[0], ids[0]):
        if idx >= 0:
            item = dict(chunks[int(idx)]); item["score"] = float(score); out.append(item)
    return out

def indexed_documents():
    _, chunks = load_index()
    counts = {}
    for c in chunks:
        counts[c["doc"]] = counts.get(c["doc"], 0) + 1
    return [{"document": k, "chunk_count": v} for k, v in sorted(counts.items())]
