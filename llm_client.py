"""
LLM client abstraction.

Three backends, tried in this order based on what's configured in .env:

1. Anthropic (ANTHROPIC_API_KEY set) — uses the `anthropic` SDK if
   installed, else a plain HTTPS call to the Messages API.
2. Generic OpenAI-compatible endpoint (OPENAI_API_KEY + optional
   OPENAI_BASE_URL) — a plain HTTPS call to /chat/completions. This lets
   the app run against OpenAI itself, or any self-hosted OpenAI-compatible
   server, without code changes.
3. Offline template fallback — if no key is configured (or a call fails),
   the app must still be demoable per the spec ("must run without one
   too"). The fallback does NOT fabricate an AI response pretending to be
   a model; it builds an honest, clearly-labeled answer directly from the
   OBSERVED context and RETRIEVED knowledge already assembled by
   context_builder, using simple template logic. It is transparent about
   being a non-LLM fallback so the UI can say so.

No API key is ever hardcoded; both are read from environment variables
populated via python-dotenv from a local .env file.
"""

from __future__ import annotations

import os
import textwrap

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


ANALYST_SYSTEM_PROMPT = textwrap.dedent("""
    You are the AI Analyst inside ShadowTrace AI, a defensive security
    investigation platform that operates ONLY on simulated/synthetic
    incident data. You are given:

    (1) an OBSERVED section — factual data drawn directly from the
        simulated incident's events, detection findings, and anomaly
        score, and
    (2) a RETRIEVED KNOWLEDGE section — excerpts from a local security
        knowledge base relevant to the analyst's question.

    Rules you must follow:
    - Structure your answer into three clearly labeled parts: OBSERVED,
      INTERPRETATION, and RECOMMENDATION.
    - OBSERVED must only restate facts that are actually present in the
      OBSERVED context given to you. Never invent events, counts, IPs,
      users, or timestamps that are not present.
    - INTERPRETATION is where you reason about what the observed pattern
      may indicate, grounded in the retrieved knowledge. Clearly present
      this as interpretation, not certainty.
    - RECOMMENDATION lists concrete next investigative steps or defensive
      controls to consider, grounded in the retrieved knowledge where
      possible.
    - If the retrieved knowledge does not sufficiently address the
      question, say so explicitly: "The available security knowledge does
      not provide enough information to support this conclusion" rather
      than guessing.
    - This is a simulated environment for training/demo purposes. Do not
      provide real-world offensive/exploitation instructions under any
      framing.
    - Keep the answer focused and analyst-usable — prefer short
      paragraphs and bullet points over long prose.
""").strip()


def _build_user_prompt(observed_summary: str, knowledge_block: str, question: str) -> str:
    return textwrap.dedent(f"""
        OBSERVED (from the current simulated incident):
        {observed_summary}

        RETRIEVED KNOWLEDGE (from the local security knowledge base):
        {knowledge_block}

        ANALYST QUESTION:
        {question}

        Respond with OBSERVED / INTERPRETATION / RECOMMENDATION sections as instructed.
    """).strip()


def get_backend_name() -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai_compatible"
    return "offline_template"


def ask_llm(observed_summary: str, knowledge_block: str, question: str) -> tuple[str, str]:
    """Returns (answer_text, backend_used)."""
    backend = get_backend_name()
    user_prompt = _build_user_prompt(observed_summary, knowledge_block, question)

    if backend == "anthropic":
        try:
            return _call_anthropic(user_prompt), "anthropic"
        except Exception as e:
            return _offline_fallback(observed_summary, knowledge_block, question,
                                      note=f"(Anthropic API call failed: {e}; showing offline analysis instead.)"), "offline_template"

    if backend == "openai_compatible":
        try:
            return _call_openai_compatible(user_prompt), "openai_compatible"
        except Exception as e:
            return _offline_fallback(observed_summary, knowledge_block, question,
                                      note=f"(LLM API call failed: {e}; showing offline analysis instead.)"), "offline_template"

    return _offline_fallback(observed_summary, knowledge_block, question), "offline_template"


def _call_anthropic(user_prompt: str) -> str:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=1000,
            system=ANALYST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")
    except ImportError:
        if requests is None:
            raise RuntimeError("Neither 'anthropic' SDK nor 'requests' is installed.")
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 1000,
                "system": ANALYST_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


def _call_openai_compatible(user_prompt: str) -> str:
    if requests is None:
        raise RuntimeError("'requests' package is not installed.")
    api_key = os.environ["OPENAI_API_KEY"]
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 1000,
            "temperature": 0.2,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _offline_fallback(observed_summary: str, knowledge_block: str, question: str,
                       note: str = "") -> str:
    """
    Honest, non-LLM answer built directly from the assembled context so the
    app is fully demoable with zero API keys configured. This is template
    logic, not a language model — the UI labels it as such via backend name.
    """
    has_knowledge = "(no relevant knowledge base entries found)" not in knowledge_block
    parts = []
    if note:
        parts.append(note)
    parts.append("OBSERVED:")
    parts.append(observed_summary)
    parts.append("")
    parts.append("INTERPRETATION:")
    if has_knowledge:
        parts.append(
            "Based on the retrieved knowledge base entries below, the observed "
            "pattern of findings is consistent with the indicators described "
            "for this scenario type. Review the specific matched sections for "
            "the reasoning that applies to each finding."
        )
        # surface first ~2 sources briefly
        for block in knowledge_block.split("\n\n")[:2]:
            header = block.split("\n", 1)[0]
            parts.append(f"  - {header}")
    else:
        parts.append(
            "The available security knowledge does not provide enough "
            "information to support a specific conclusion for this question."
        )
    parts.append("")
    parts.append("RECOMMENDATION:")
    parts.append(
        "  - Review the listed findings and their evidence event IDs directly.\n"
        "  - Consult the cited knowledge base sources for standard response guidance.\n"
        "  - Escalate per severity if not already done.\n"
        "  (Note: this response was generated by the offline template fallback, "
        "not a language model, because no LLM API key is configured in .env.)"
    )
    return "\n".join(parts)
