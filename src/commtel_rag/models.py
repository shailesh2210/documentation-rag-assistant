from functools import lru_cache
import requests
from sentence_transformers import SentenceTransformer
from .config import CONFIG

@lru_cache(maxsize=1)
def get_embedder():
    return SentenceTransformer(CONFIG["models"]["embedding_model"], device="cpu")

def embed_texts(texts):
    return get_embedder().encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)

def ollama_generate(prompt, json_mode=False):
    base = CONFIG["models"]["ollama_base_url"].rstrip("/")
    payload = {"model": CONFIG["models"]["ollama_model"], "prompt": prompt, "stream": False,
               "options": {"temperature": CONFIG["models"]["temperature"], "num_predict": CONFIG["models"]["max_predict_tokens"]}}
    if json_mode:
        payload["format"] = "json"
    try:
        r = requests.post(base + "/api/generate", json=payload, timeout=CONFIG["models"]["timeout_seconds"])
        r.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError("Local Ollama is unavailable. Start Ollama and install the configured model.") from exc
    return r.json().get("response", "").strip()
