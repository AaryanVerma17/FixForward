from pathlib import Path
import json
import re

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_documents.json"

def retrieve_documents(case: dict, limit: int = 3) -> list[dict]:
    if not DATA_FILE.exists():
        return []
    docs = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    query_terms = set(re.findall(r"[a-z0-9]+", " ".join([
        str(case.get("category", "")), " ".join(case.get("symptoms", [])),
        str(case.get("warranty_status", "")), str(case.get("notes", ""))
    ]).lower()))
    scored = []
    for doc in docs:
        if doc.get("category") not in {case.get("category"), "all"}:
            continue
        terms = set(re.findall(r"[a-z0-9]+", (doc.get("title", "") + " " + doc.get("content", "")).lower()))
        score = len(query_terms & terms)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [{
        "title": doc["title"], "source": doc["source"],
        "excerpt": doc["content"], "verified": doc.get("verified", False),
        "source_url": doc.get("source_url"), "score": score
    } for score, doc in scored[:limit]]
