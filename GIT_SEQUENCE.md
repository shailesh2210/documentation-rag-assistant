# Git history requirement

The assessment asks for `questions.jsonl` to be committed before the graph is built. This ZIP intentionally does not contain a fabricated `.git` history.

For your own private repository, create a new repository and commit in this order:
```powershell
git init
git add questions.jsonl data/docs
git commit -m "Add pinned documentation extracts and gold question set"
git add .
git commit -m "Implement local RAG ingestion, LangGraph workflow and API"
```
Do not claim this archive itself proves the historical sequence.
