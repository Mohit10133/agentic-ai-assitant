from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    stop = {"the", "is", "a", "an", "to", "for", "of", "and", "or", "my", "i", "how", "can", "do"}
    return {w for w in words if w not in stop}


def _load_domain_docs(domain: str) -> List[str]:
    file_map = {
        "ecommerce": "ecommerce.md",
        "travel": "travel.md",
        "healthcare": "healthcare.md",
    }
    filename = file_map.get(domain)
    if not filename:
        return []

    path = KNOWLEDGE_DIR / filename
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return chunks


def retrieve_top_chunks(domain: str, query: str, top_k: int = 2) -> List[str]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored: List[Tuple[int, str]] = []
    for chunk in _load_domain_docs(domain):
        score = len(query_tokens.intersection(_tokenize(chunk)))
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]


def answer_knowledge_query(domain: str, query: str) -> Dict[str, object]:
    chunks = retrieve_top_chunks(domain=domain, query=query, top_k=2)
    if not chunks:
        return {
            "success": True,
            "message": "I could not find a direct policy answer. Please rephrase your question.",
            "intent": "knowledge.qa",
            "data": {"sources": []},
        }

    answer = " ".join(chunks)
    return {
        "success": True,
        "message": answer,
        "intent": "knowledge.qa",
        "data": {"sources": chunks},
    }
