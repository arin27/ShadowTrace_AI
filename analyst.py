"""
AI Analyst orchestration.

Public entry point used by the UI: ask_analyst(incident_id, question) ->
{answer, sources, backend, observed_summary}

This ties together context_builder (incident-aware RAG context) and
llm_client (the actual reasoning step), then records the Q&A turn in
SQLite so a re-opened investigation shows its history.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from database import db as dbmod
from rag.context_builder import build_full_context
from rag.llm_client import ask_llm

SUGGESTED_QUESTIONS = [
    "What happened?",
    "Why is this suspicious?",
    "What evidence supports this?",
    "What attack behaviour does this resemble?",
    "What should I investigate next?",
    "What defensive controls should I review?",
    "Are there similar behaviours in the knowledge base?",
    "Explain this incident to a non-technical manager.",
]


def ask_analyst(incident_id: str, question: str) -> dict:
    ctx = build_full_context(incident_id, question)
    answer, backend = ask_llm(ctx["observed_summary"], ctx["knowledge_block"], question)

    sources = [
        {
            "document": r.chunk.doc_title,
            "section": r.chunk.section,
            "relevance": round(r.score, 3),
        }
        for r in ctx["retrieved"]
    ]

    qa_record = {
        "qa_id": f"QA-{uuid.uuid4().hex[:8]}",
        "incident_id": incident_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "asked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    dbmod.insert_qa(qa_record)

    return {
        "answer": answer,
        "sources": sources,
        "backend": backend,
        "observed_summary": ctx["observed_summary"],
    }
