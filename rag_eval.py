from __future__ import annotations

import pandas as pd
import streamlit as st

from evaluation.rag_evaluation import run_evaluation


def render():
    st.title("RAG Evaluation")
    st.caption(
        "Runs the retrieval (and, where configured, generation) pipeline live "
        "against a held-out evaluation set of question → expected-document → "
        "expected-topic triples. No numbers here are hardcoded."
    )

    generate_answers = st.checkbox("Also evaluate generated answers (source correctness + relevance)",
                                    value=True)
    if st.button("▶ Run Evaluation", type="primary"):
        with st.spinner("Running retrieval and generation over the evaluation set..."):
            result = run_evaluation(top_k=3, generate_answers=generate_answers)
        st.session_state["eval_result"] = result

    result = st.session_state.get("eval_result")
    if not result:
        st.info("Click **Run Evaluation** to compute live metrics.")
        return

    s = result["summary"]
    st.caption(f"Retrieval backend: `{s['retrieval_backend']}` · "
               f"Generation backend: `{s['generation_backend']}`")

    cols = st.columns(5)
    cols[0].metric("Hit Rate @ k", s["hit_rate_at_k"])
    cols[1].metric("Precision @ 1", s["precision_at_1"])
    cols[2].metric("Mean Reciprocal Rank", s["mean_reciprocal_rank"])
    if s["source_correctness"] is not None:
        cols[3].metric("Source Correctness", s["source_correctness"])
    if s["mean_answer_relevance"] is not None:
        cols[4].metric("Mean Answer Relevance", s["mean_answer_relevance"])

    st.markdown("---")
    st.markdown("### Per-Question Results")
    rows = []
    for q in result["per_question"]:
        rows.append({
            "Question": q["question"],
            "Expected Doc": q["expected_document"],
            "Retrieved (ranked)": ", ".join(q["retrieved_documents_ranked"]),
            "Hit@k": q["hit_at_k"],
            "Top-1 Correct": q["top1_correct"],
            "RR": q["reciprocal_rank"],
            "Source Correct": q["source_correct"],
            "Answer Relevance": q["answer_relevance"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Metric definitions"):
        st.markdown("""
- **Hit Rate @ k** — fraction of questions where the expected document appears
  among the top-k retrieved chunks.
- **Precision @ 1** — fraction where the single top-ranked chunk is from the
  expected document.
- **Mean Reciprocal Rank (MRR)** — average of 1/rank of the first chunk from
  the expected document (0 if absent from the considered top-k).
- **Source Correctness** — for the generated answer, whether the expected
  document is among the cited sources.
- **Mean Answer Relevance** — lexical (word-overlap) similarity between the
  expected topic's vocabulary and the generated answer. A simple, fully
  reproducible proxy since no LLM-judge is assumed to be configured.
        """)
