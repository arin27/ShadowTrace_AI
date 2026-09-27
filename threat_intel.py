from __future__ import annotations

import streamlit as st

from rag.retrieval import get_retriever

SUGGESTIONS = [
    "credential abuse", "insider threat", "privilege escalation",
    "suspicious authentication", "data exfiltration", "web application abuse",
]


def render():
    st.title("Threat Intelligence")
    st.caption("Search the local security knowledge base used by the RAG pipeline and AI Analyst.")

    retriever = get_retriever()
    st.caption(f"Retrieval backend: `{retriever.backend_name}` · {len(retriever.chunks)} indexed chunks")

    query = st.text_input("Search the knowledge base", placeholder="e.g. repeated failed authentication")
    st.write("Try:")
    chip_cols = st.columns(len(SUGGESTIONS))
    for col, s in zip(chip_cols, SUGGESTIONS):
        with col:
            if st.button(s, key=f"sugg_{s}", use_container_width=True):
                query = s
                st.session_state["ti_query"] = s

    query = st.session_state.get("ti_query", query) if not query else query

    if query:
        results = retriever.search(query, top_k=8)
        st.markdown(f"**{len(results)} result(s) for** `{query}`")
        for r in results:
            with st.container():
                st.markdown(f"##### {r.chunk.doc_title} — {r.chunk.section}")
                st.caption(f"Source document: `{r.chunk.doc_name}` · Relevance score: {r.score:.3f}")
                st.write(r.chunk.text)
                st.markdown("---")
    else:
        st.info("Enter a search term or choose a suggestion above.")
