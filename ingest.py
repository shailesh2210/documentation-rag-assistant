import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from commtel_rag.corpus import load_all_chunks
from commtel_rag.retrieval import build_index

if __name__ == "__main__":
    chunks = load_all_chunks()
    build_index(chunks)
    print(f"Ingestion complete: {len(chunks)} chunks indexed.")
