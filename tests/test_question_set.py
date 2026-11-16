import json
from pathlib import Path

def test_question_distribution():
    rows = [json.loads(x) for x in Path("questions.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(rows) == 20
    counts = {}
    for row in rows: counts[row["category"]] = counts.get(row["category"], 0) + 1
    assert counts == {"single_passage":9,"table_lookup":4,"multi_document":2,"version_dependent":1,"unanswerable":4}
    assert all({"id","question","category","gold_answer","gold_passages"} <= set(x) for x in rows)
