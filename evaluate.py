import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import json, math, statistics, time
from pathlib import Path
from collections import defaultdict
from commtel_rag.config import CONFIG
from commtel_rag.graph import run_query

def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")

def hit(gold, chunks):
    norm = lambda s: " ".join(s.replace("`", "").lower().split())
    return any(any(c["doc"] == g["doc"] and norm(g["quote"]) in norm(c["text"]) for c in chunks) for g in gold)

def pct(values, p):
    if not values: return None
    vals = sorted(values); pos = (len(vals)-1)*p; lo, hi = math.floor(pos), math.ceil(pos)
    return vals[lo] if lo == hi else vals[lo]*(hi-pos)+vals[hi]*(pos-lo)

def main():
    qs = read_jsonl(Path(CONFIG["paths"]["questions_file"]))
    rows, stats, latencies = [], defaultdict(lambda: {"n":0,"retrieved":0,"retained":0}), []
    refused_unanswerable = wrong_refusals = 0
    for q in qs:
        t = time.perf_counter(); r = run_query(q["question"]); latency = time.perf_counter()-t; latencies.append(latency)
        retrieved, retained = r.get("retrieved", []), r.get("retained", [])
        unanswerable = q["category"] == "unanswerable"
        if unanswerable and r.get("refused"): refused_unanswerable += 1
        if not unanswerable:
            if r.get("refused"): wrong_refusals += 1
            s = stats[q["category"]]; s["n"] += 1
            s["retrieved"] += int(hit(q["gold_passages"], retrieved))
            s["retained"] += int(hit(q["gold_passages"], retained))
        rows.append({"id":q["id"],"answer":r.get("answer",""),"refused":bool(r.get("refused",False)),
                     "citations":r.get("citations",[]),"retrieved":[x["chunk_id"] for x in retrieved],
                     "retained":[x["chunk_id"] for x in retained],"verified":r.get("verified"),
                     "retries":int(r.get("retries",0)),"termination":r.get("termination","unknown"),
                     "latency_s":round(latency,4)})
        print(f"{q['id']}: {rows[-1]['termination']} ({latency:.2f}s)")
    Path(CONFIG["paths"]["results_file"]).write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows),encoding="utf-8")
    summary = {"question_count":len(rows),"answerable_retrieval":{},
               "unanswerable_refused":f"{refused_unanswerable}/4","answerable_wrongly_refused":f"{wrong_refusals}/16",
               "median_latency_s":statistics.median(latencies) if latencies else None,
               "p95_latency_s":pct(latencies,.95),
               "groundedness":"MANUAL REVIEW REQUIRED; see reports/groundedness_review_template.csv",
               "gold_match_method":"normalized exact quote substring in same-document chunk"}
    for cat,v in stats.items():
        summary["answerable_retrieval"][cat] = {"n":v["n"],"retrieved_hit_rate":v["retrieved"]/v["n"],
                                                 "retained_hit_rate":v["retained"]/v["n"]}
    out = Path(CONFIG["paths"]["report_dir"]); out.mkdir(parents=True,exist_ok=True)
    (out/"evaluation_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__": main()
