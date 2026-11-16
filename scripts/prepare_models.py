import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sentence_transformers import SentenceTransformer
from commtel_rag.config import CONFIG
if __name__ == "__main__":
    print("Caching", CONFIG["models"]["embedding_model"])
    SentenceTransformer(CONFIG["models"]["embedding_model"], device="cpu")
    print("Embedding cache prepared.")
