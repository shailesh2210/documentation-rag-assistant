from typing import TypedDict, Optional
import json
import re
from langgraph.graph import StateGraph, END
from .config import CONFIG
from .models import ollama_generate
from .retrieval import retrieve

class RAGState(TypedDict, total=False):
    question: str
    search_query: str
    retrieved: list[dict]
    retained: list[dict]
    sufficient: bool
    sufficiency_reason: str
    answer: str
    citations: list[dict]
    verified: Optional[bool]
    verification_reason: str
    retries: int
    verification_retries: int
    termination: str
    refused: bool
    node_trace: list[str]

def parse_json(prompt):
    raw = ollama_generate(prompt, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise ValueError("LLM did not return JSON")
        return json.loads(m.group(0))

def retrieve_node(s):
    k = CONFIG["retrieval"]["retry_top_k"] if s.get("retries", 0) else CONFIG["retrieval"]["top_k"]
    docs = retrieve(s.get("search_query") or s["question"], top_k=k)
    return {"retrieved": docs, "node_trace": s.get("node_trace", []) + ["retrieve"]}

def grade_node(s):
    docs = s.get("retrieved", [])
    if not docs:
        return {"retained": [], "sufficient": False, "sufficiency_reason": "No passages retrieved.",
                "node_trace": s.get("node_trace", []) + ["grade"]}
    context = "\n\n".join(f"[{i}] {d['doc']} / {d['section']}\n{d['text']}" for i, d in enumerate(docs))
    prompt = ("You are a strict documentation context grader. Use ONLY these passages.\n"
              f"Question: {s['question']}\nPassages:\n{context}\n"
              'Return JSON only: {"sufficient":true/false,"relevant_indices":[integer],"reason":"brief"}. '
              "Sufficient means the passages directly contain enough evidence; otherwise false.")
    try:
        obj = parse_json(prompt)
        indexes = [i for i in obj.get("relevant_indices", []) if isinstance(i, int) and 0 <= i < len(docs)]
        retained = [docs[i] for i in indexes]
        sufficient = bool(obj.get("sufficient")) and bool(retained)
        reason = str(obj.get("reason", "LLM graded context"))
    except Exception as exc:
        # Conservative fallback if the grader is unavailable: require at least two overlapping terms.
        terms = set(re.findall(r"[a-zA-Z_]{3,}", s["question"].lower()))
        retained = [d for d in docs if len(terms & set(re.findall(r"[a-zA-Z_]{3,}", d["text"].lower()))) >= 2]
        sufficient, reason = bool(retained), f"Lexical fallback used: {type(exc).__name__}"
    return {"retained": retained, "sufficient": sufficient, "sufficiency_reason": reason,
            "node_trace": s.get("node_trace", []) + ["grade"]}

def route_grade(s):
    if s.get("sufficient"): return "generate"
    if s.get("retries", 0) < CONFIG["workflow"]["max_retrieval_retries"]: return "recover"
    return "refuse"

def recover_node(s):
    prompt = ("Rewrite this documentation search query. Preserve technical names. "
              f"Question: {s['question']} Previous query: {s.get('search_query', s['question'])}. "
              "Return only the rewritten query.")
    try: rewritten = ollama_generate(prompt).strip().strip('"')
    except Exception: rewritten = s["question"] + " exact API signature parameter behavior"
    return {"search_query": rewritten or s["question"], "retries": s.get("retries", 0) + 1,
            "node_trace": s.get("node_trace", []) + ["recover"]}

def generate_node(s):
    docs = s.get("retained", [])
    context = "\n\n".join(f"[{d['chunk_id']}] {d['doc']} / {d['section']} / {d['version']}\n{d['text']}" for d in docs)
    prompt = ("Answer using ONLY the supplied documentation. Do not use prior knowledge. "
              "Cite every factual claim with [chunk_id]. If absent, say the docs do not specify it.\n"
              f"Question: {s['question']}\nDocumentation:\n{context}\nAnswer:")
    answer = ollama_generate(prompt)
    citations = [{"doc": d["doc"], "location": f"{d['section']} (#{d['anchor']})", "chunk_id": d["chunk_id"]}
                 for d in docs if d["chunk_id"] in answer]
    if not citations:
        citations = [{"doc": d["doc"], "location": f"{d['section']} (#{d['anchor']})", "chunk_id": d["chunk_id"]} for d in docs[:2]]
    return {"answer": answer, "citations": citations, "node_trace": s.get("node_trace", []) + ["generate"]}

def verify_node(s):
    retained = s.get("retained", [])
    ids = {c["chunk_id"] for c in s.get("citations", [])}
    docs = [d for d in retained if d["chunk_id"] in ids]
    if not docs:
        return {"verified": False, "verification_reason": "No cited passage retained.",
                "node_trace": s.get("node_trace", []) + ["verify"]}
    context = "\n\n".join(f"[{d['chunk_id']}] {d['text']}" for d in docs)
    prompt = ('Check whether every factual claim in the answer is supported by these cited passages. '
              'Use no outside knowledge. Return JSON only: {"supported":true/false,"reason":"brief"}.\n'
              f"Question: {s['question']}\nAnswer: {s.get('answer','')}\nPassages:\n{context}")
    try:
        obj = parse_json(prompt); verified = bool(obj.get("supported")); reason = str(obj.get("reason", ""))
    except Exception as exc:
        verified, reason = False, f"Verification unavailable: {type(exc).__name__}"
    return {"verified": verified, "verification_reason": reason, "node_trace": s.get("node_trace", []) + ["verify"]}

def route_verify(s):
    if s.get("verified"): return "done"
    if s.get("verification_retries", 0) < CONFIG["workflow"]["max_verification_retries"]: return "regenerate"
    return "unverified"

def regenerate_node(s):
    docs = s.get("retained", [])
    context = "\n\n".join(f"[{d['chunk_id']}] {d['text']}" for d in docs)
    answer = ollama_generate("Rewrite conservatively using ONLY this evidence and cite [chunk_id]. "
                             f"Question: {s['question']} Evidence: {context} Previous: {s.get('answer','')}")
    citations = [{"doc": d["doc"], "location": f"{d['section']} (#{d['anchor']})", "chunk_id": d["chunk_id"]} for d in docs[:2]]
    return {"answer": answer, "citations": citations, "verification_retries": s.get("verification_retries", 0) + 1,
            "node_trace": s.get("node_trace", []) + ["regenerate"]}

def refuse_node(s):
    return {"answer": "I cannot answer this from the indexed documentation. I searched the available local passages, but they did not provide sufficient evidence.",
            "citations": [], "refused": True, "verified": None, "termination": "refused_no_context",
            "node_trace": s.get("node_trace", []) + ["refuse"]}

def unverified_node(s):
    return {"answer": "I am withholding this answer because it could not be verified against the cited documentation.",
            "refused": True, "termination": "refused_unverified", "node_trace": s.get("node_trace", []) + ["unverified_refusal"]}

def done_node(s):
    return {"refused": False, "termination": "answered", "node_trace": s.get("node_trace", []) + ["done"]}

def build_graph():
    g = StateGraph(RAGState)
    for name, fn in [("retrieve", retrieve_node), ("grade", grade_node), ("recover", recover_node),
                     ("generate", generate_node), ("verify", verify_node), ("regenerate", regenerate_node),
                     ("refuse", refuse_node), ("unverified", unverified_node), ("done", done_node)]:
        g.add_node(name, fn)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "grade")
    g.add_conditional_edges("grade", route_grade, {"generate": "generate", "recover": "recover", "refuse": "refuse"})
    g.add_edge("recover", "retrieve")
    g.add_edge("generate", "verify")
    g.add_conditional_edges("verify", route_verify, {"done": "done", "regenerate": "regenerate", "unverified": "unverified"})
    g.add_edge("regenerate", "verify")
    for node in ("refuse", "unverified", "done"): g.add_edge(node, END)
    return g.compile()

RAG_GRAPH = build_graph()

def run_query(question):
    initial = {"question": question, "search_query": question, "retries": 0, "verification_retries": 0,
               "node_trace": [], "refused": False, "verified": None}
    return RAG_GRAPH.invoke(initial)
