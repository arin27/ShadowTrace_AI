"""
"What could happen next?" — potential next-stage behaviour.

Deliberately NOT LLM-generated: this is predefined scenario logic (see
simulation.scenarios.NEXT_STAGE_BEHAVIOUR) combined with a short retrieval
call so the UI can show which knowledge base entries back the statement.
It is always labeled in the UI as "Potential behaviour — not confirmed
activity," per the safety boundary in the spec, and never produces
actionable real-world attack instructions — only named categories of
behaviour (e.g. "privileged resource access attempt").
"""

from __future__ import annotations

from rag.retrieval import get_retriever
from simulation.scenarios import NEXT_STAGE_BEHAVIOUR


def get_next_stage(scenario_key: str) -> dict:
    behaviours = NEXT_STAGE_BEHAVIOUR.get(scenario_key, [])
    retriever = get_retriever()
    results = retriever.search(f"{scenario_key.replace('_', ' ')} next stage escalation", top_k=2)
    supporting_sources = [
        {"document": r.chunk.doc_title, "section": r.chunk.section, "relevance": round(r.score, 3)}
        for r in results
    ]
    return {
        "behaviours": behaviours,
        "supporting_sources": supporting_sources,
        "disclaimer": "Potential behaviour — not confirmed activity.",
    }
