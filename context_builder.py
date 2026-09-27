"""
Context builder.

This is the piece that makes the RAG system incident-aware rather than a
generic "chat with these PDFs" bot. It assembles:

  1. OBSERVED — a structured, factual summary of the actual simulation
     events, findings, and anomaly result for the current incident.
  2. RETRIEVED KNOWLEDGE — the top-k knowledge base chunks relevant to the
     analyst's question (and, for a default overview, relevant to the
     incident's scenario type).

The LLM is then asked to reason over this context and explicitly separate
OBSERVED fact from INTERPRETATION from RECOMMENDATION, so the AI Analyst
never presents speculation as fact.
"""

from __future__ import annotations

from database import db as dbmod
from rag.retrieval import get_retriever, RetrievalResult
from simulation.scenarios import SCENARIOS

SCENARIO_QUERY_HINTS = {
    "credential_abuse": "credential abuse repeated failed authentication valid accounts",
    "malicious_file": "suspicious process execution malware persistence outbound connection",
    "web_abuse": "web application abuse malformed input unauthorized access",
    "insider_threat": "insider threat unusual access data exfiltration",
}

# incidents store the scenario's display name (e.g. "Credential Abuse"); this
# maps that back to the internal scenario key (e.g. "credential_abuse") used
# by SCENARIO_QUERY_HINTS and NEXT_STAGE_BEHAVIOUR.
_NAME_TO_KEY = {v["name"]: k for k, v in SCENARIOS.items()}


def scenario_name_to_key(scenario_name: str) -> str:
    return _NAME_TO_KEY.get(scenario_name, scenario_name)


def build_observed_summary(incident: dict, findings: list[dict], events: list[dict],
                            anomaly: dict) -> str:
    lines = []
    lines.append(f"Incident: {incident['incident_id']} — {incident['scenario']}")
    lines.append(f"Affected user: {incident.get('affected_user')}")
    lines.append(f"Affected resources: {', '.join(incident.get('affected_resources', [])) or 'none recorded'}")
    lines.append(f"Total events recorded: {len(events)}")
    lines.append("")
    lines.append("Detection findings (deterministic rules that fired on actual events):")
    if findings:
        for f in findings:
            lines.append(f"  - {f['rule_name']}: {f['description']}")
    else:
        lines.append("  - No deterministic rule fired.")
    lines.append("")
    lines.append(f"Anomaly detection ({anomaly.get('method')}):")
    lines.append(f"  - is_anomaly = {anomaly.get('is_anomaly')}, anomaly_score = {anomaly.get('anomaly_score')}")
    for ex in anomaly.get("explanations", []):
        lines.append(f"  - {ex}")
    lines.append("")
    lines.append(f"Calculated severity: {incident['severity']} (score {incident['severity_score']})")
    for r in incident.get("severity_reasoning", []):
        lines.append(f"  - {r}")
    return "\n".join(lines)


def retrieve_for_question(scenario_key: str, question: str, top_k: int = 4) -> list[RetrievalResult]:
    retriever = get_retriever()
    # Blend the analyst's actual question with a scenario hint so retrieval
    # stays anchored to the incident's topic even for short/vague questions.
    hint = SCENARIO_QUERY_HINTS.get(scenario_key, "")
    query = f"{question} {hint}".strip()
    return retriever.search(query, top_k=top_k)


def build_full_context(incident_id: str, question: str) -> dict:
    """Assemble everything the LLM needs for one AI Analyst turn."""
    incident = dbmod.get_incident(incident_id)
    if not incident:
        raise ValueError(f"Unknown incident: {incident_id}")

    sim_id = incident["sim_id"]
    events = dbmod.get_events(sim_id)
    findings = dbmod.get_findings(sim_id)
    anomaly = incident.get("anomaly_summary", {})

    observed_summary = build_observed_summary(incident, findings, events, anomaly)
    scenario_key = scenario_name_to_key(incident["scenario"])
    retrieved = retrieve_for_question(scenario_key, question)

    knowledge_block = "\n\n".join(
        f"[Source: {r.chunk.doc_title} — {r.chunk.section}] (relevance {r.score:.2f})\n{r.chunk.text}"
        for r in retrieved
    ) if retrieved else "(no relevant knowledge base entries found)"

    return {
        "incident": incident,
        "observed_summary": observed_summary,
        "retrieved": retrieved,
        "knowledge_block": knowledge_block,
    }
