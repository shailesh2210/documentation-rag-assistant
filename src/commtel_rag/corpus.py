from pathlib import Path
import hashlib
import re
from .config import CONFIG

VERSIONS = {"python_csv_312": "Python 3.12", "python_pathlib_312": "Python 3.12", "pandas_io_223": "pandas 2.2.3"}

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "section"

def split_document(path):
    raw = path.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)(?=^#{1,4}\s+)", raw)
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.search(r"(?m)^#{1,4}\s+(.+)$", block)
        section = m.group(1).strip() if m else path.stem
        lines, tables, normal, current = block.splitlines(), [], [], []
        for line in lines:
            if line.strip().startswith("|"):
                current.append(line)
            else:
                if current:
                    tables.append("\n".join(current)); current = []
                normal.append(line)
        if current:
            tables.append("\n".join(current))
        text = "\n".join(normal).strip()
        max_chars, overlap = CONFIG["chunking"]["max_chars"], CONFIG["chunking"]["overlap_chars"]
        pieces = []
        if text:
            start = 0
            while start < len(text):
                end = min(start + max_chars, len(text))
                if end < len(text):
                    boundary = text.rfind("\n", start, end)
                    if boundary > start + max_chars // 2:
                        end = boundary
                pieces.append(text[start:end].strip())
                if end >= len(text):
                    break
                start = max(end - overlap, start + 1)
        pieces.extend(tables)  # table header and rows remain together
        for i, piece in enumerate(pieces):
            if not piece:
                continue
            anchor = slug(section)
            cid = hashlib.sha1(f"{path.stem}|{anchor}|{i}|{piece}".encode()).hexdigest()[:16]
            result.append({"chunk_id": cid, "doc": path.stem, "section": section, "anchor": anchor,
                           "version": VERSIONS.get(path.stem, "unspecified"), "text": piece,
                           "source_file": path.name, "kind": "table" if piece.lstrip().startswith("|") else "text"})
    return result

def load_all_chunks():
    paths = sorted(Path(CONFIG["paths"]["docs_dir"]).glob("*.md"))
    chunks = [chunk for path in paths for chunk in split_document(path)]
    if not chunks:
        raise RuntimeError("No Markdown corpus documents found.")
    return chunks
