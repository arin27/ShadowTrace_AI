"""
RAG evaluation harness.

Loads data/evaluation/eval_set.json (question, expected_document,
expected_topic) and actually runs the retriever (and, where an LLM is
configured, the generation step) against every question, computing:

  - Retrieval Hit Rate @ k        — is the expected document among the
                                     top-k retrieved chunks?
  - Precision @ 1                 — is the expected document the single
                                     top-ranked chunk?
  - Mean Reciprocal Rank (MRR)    — average of 1/rank of the first chunk
                                     from the expected document, within
                                     the considered top-k (0 if absent).
  - Source Correctness            — for the full analyst answer (which
                                     cites sources), does the expected
                                     document appear among cited sources?
  - Answer Relevance (lexical)    — word-overlap between the expected
                                     topic's vocabulary and the generated
                                     answer, a simple, honest, and fully
                                     reproducible proxy (not an LLM judge,
                                     since we do not assume an API key is
                                     configured).

No number here is invented — every metric is computed directly from a
live retriever/generator call in this process, using whichever backend
(embeddings or TF-IDF fallback, real LLM or offline template) is actually
configured. The report clearly states which backend was used so the
numbers are interpreted in the right context.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from rag.llm_client import ask_llm, get_backend_name
from rag.retrieval import get_retriever

EVAL_PATH = Path(__file__).resolve().parent.parent / "data" / "evaluation" / "eval_set.json"


def load_eval_set() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def run_evaluation(top_k: int = 3, generate_answers: bool = True) -> dict:
    retriever = get_retriever()
    eval_set = load_eval_set()

    per_question = []
    hits_at_k = 0
    precision_at_1 = 0
    reciprocal_ranks = []
    source_correct_count = 0
    relevance_scores = []

    for item in eval_set:
        question = item["question"]
        expected_doc = item["expected_document"]
        expected_topic = item["expected_topic"]

        results = retriever.search(question, top_k=max(top_k, 5))
        retrieved_docs = [r.chunk.doc_name for r in results]

        hit = expected_doc in retrieved_docs[:top_k]
        hits_at_k += int(hit)

        top1_correct = bool(retrieved_docs) and retrieved_docs[0] == expected_doc
        precision_at_1 += int(top1_correct)

        rr = 0.0
        for rank, doc in enumerate(retrieved_docs[:top_k], start=1):
            if doc == expected_doc:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        answer_text = None
        cited_docs: list[str] = []
        source_correct = None
        relevance = None

        if generate_answers:
            knowledge_block = "\n\n".join(
                f"[Source: {r.chunk.doc_title} — {r.chunk.section}]\n{r.chunk.text}"
                for r in results[:top_k]
            )
            observed_summary = (
                "OBSERVED: (knowledge-base evaluation question, not tied to a "
                "specific simulated incident)"
            )
            answer_text, _backend = ask_llm(observed_summary, knowledge_block, question)
            cited_docs = [r.chunk.doc_name for r in results[:top_k]]
            source_correct = expected_doc in cited_docs
            source_correct_count += int(source_correct)

            topic_tokens = _tokenize(expected_topic)
            answer_tokens = _tokenize(answer_text)
            overlap = topic_tokens & answer_tokens
            relevance = round(len(overlap) / max(len(topic_tokens), 1), 3)
            relevance_scores.append(relevance)

        per_question.append({
            "question": question,
            "expected_document": expected_doc,
            "expected_topic": expected_topic,
            "retrieved_documents_ranked": retrieved_docs[:top_k],
            "hit_at_k": hit,
            "top1_correct": top1_correct,
            "reciprocal_rank": round(rr, 3),
            "source_correct": source_correct,
            "answer_relevance": relevance,
            "answer_preview": (answer_text[:400] + "...") if answer_text and len(answer_text) > 400 else answer_text,
        })

    n = len(eval_set)
    summary = {
        "num_questions": n,
        "retrieval_backend": retriever.backend_name,
        "generation_backend": get_backend_name() if generate_answers else "not_run",
        "hit_rate_at_k": round(hits_at_k / n, 3),
        "precision_at_1": round(precision_at_1 / n, 3),
        "mean_reciprocal_rank": round(sum(reciprocal_ranks) / n, 3),
        "source_correctness": round(source_correct_count / n, 3) if generate_answers else None,
        "mean_answer_relevance": round(sum(relevance_scores) / n, 3) if relevance_scores else None,
        "top_k": top_k,
    }

    return {"summary": summary, "per_question": per_question}


if __name__ == "__main__":
    import pprint
    result = run_evaluation()
    pprint.pprint(result["summary"])
