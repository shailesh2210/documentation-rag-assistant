from pathlib import Path
import os
import yaml

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

def load_config():
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    for key in ("docs_dir", "index_dir", "questions_file", "results_file", "report_dir"):
        cfg["paths"][key] = str((ROOT / cfg["paths"][key]).resolve())
    return cfg

CONFIG = load_config()
