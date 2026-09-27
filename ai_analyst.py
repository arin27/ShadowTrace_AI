from __future__ import annotations

import streamlit as st

from database import db as dbmod
from rag.analyst import ask_analyst, SUGGESTED_QUESTIONS
from rag.llm_client import get_backend_name
from ui.common import select_incident


def render():
    st.title("AI Analyst")
    st.caption(
        "Ask questions about the currently selected incident. Every answer is grounded in "
        "the incident's actual evidence plus retrieved security knowledge, with sources cited."
    )

    incident_id = select_incident("ai_analyst")
    if not incident_id:
        return

    backend = get_backend_name()
    backend_label = {
        "anthropic": "Anthropic (live LLM)",
        "openai_compatible": "OpenAI-compatible endpoint (live LLM)",
        "offline_template": "Offline template fallback (no LLM API key configured)",
    }[backend]
    st.caption(f"Generation backend: `{backend_label}`")
    if backend == "offline_template":
        st.info(
            "No LLM API key is configured in `.env`. The AI Analyst is running in "
            "offline mode: answers are built directly and transparently from the "
            "incident's observed evidence and retrieved knowledge base sources, "
            "without a language model in the loop. Add ANTHROPIC_API_KEY or "
            "OPENAI_API_KEY to `.env` to enable live LLM reasoning."
        )

    incident = dbmod.get_incident(incident_id)
    st.markdown(f"**Incident:** {incident['incident_id']} — {incident['scenario']} "
                f"({incident['severity']})")

    st.markdown("**Suggested questions:**")
    q_cols = st.columns(4)
    clicked_q = None
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with q_cols[i % 4]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                clicked_q = q

    st.markdown("---")
    history = dbmod.get_qa_history(incident_id)
    for qa in history:
        with st.chat_message("user"):
            st.write(qa["question"])
        with st.chat_message("assistant"):
            st.write(qa["answer"])
            if qa.get("sources"):
                st.markdown("**Sources:**")
                for s in qa["sources"]:
                    st.markdown(
                        f'<span class="source-chip">{s["document"]} · {s["section"]} '
                        f'(relevance {s["relevance"]})</span>',
                        unsafe_allow_html=True,
                    )

    typed_q = st.chat_input("Ask the AI Analyst about this incident...")
    question = clicked_q or typed_q

    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving knowledge and reasoning over incident evidence..."):
                result = ask_analyst(incident_id, question)
            st.write(result["answer"])
            if result["sources"]:
                st.markdown("**Sources:**")
                for s in result["sources"]:
                    st.markdown(
                        f'<span class="source-chip">{s["document"]} · {s["section"]} '
                        f'(relevance {s["relevance"]})</span>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No relevant knowledge base entries were retrieved for this question.")
        st.rerun()
