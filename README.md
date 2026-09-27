# ShadowTrace AI

**AI-Powered Adversary Intelligence & Threat Investigation Platform**

> SIMULATE → DETECT → INVESTIGATE → UNDERSTAND → RESPOND

ShadowTrace AI is a small, self-contained platform that lets a security
analyst launch a controlled, fully synthetic attack simulation, watch a
detection engine and an anomaly model flag suspicious behaviour in the
resulting events, and then investigate the incident with an AI Analyst
that is grounded in both the incident's real evidence and a local security
knowledge base via retrieval-augmented generation (RAG).

**Everything in this project is simulated.** All users, IP addresses,
resources, and event data are synthetic or drawn from documentation
address ranges (RFC 5737). No functionality here attacks real systems,
steals real credentials, or performs real exploitation. See
[Security Considerations](#security-considerations--safety-boundary).

---

## Table of Contents

- [Problem & Motivation](#problem--motivation)
- [Product Overview](#product-overview)
- [Architecture](#architecture)
- [Simulation Engine](#simulation-engine)
- [Detection Engine](#detection-engine)
- [Anomaly Detection](#anomaly-detection)
- [RAG Pipeline](#rag-pipeline)
- [AI Analyst](#ai-analyst)
- [Investigation Workflow](#investigation-workflow)
- [Evaluation](#evaluation)
- [Security Considerations & Safety Boundary](#security-considerations--safety-boundary)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Example Investigation](#example-investigation)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Resume Bullets](#resume-bullets)

---

## Problem & Motivation

Security analysts spend a large share of investigation time doing three
things repeatedly: reconstructing what happened from raw logs, recalling
or looking up what a given pattern of behaviour typically means, and
deciding what to do next. Generic chatbots that answer questions about a
static document set don't help here, because they have no awareness of
the *current* incident's actual evidence.

ShadowTrace AI was built to demonstrate a narrower, more useful idea:
an AI Analyst whose every answer is automatically grounded in **(a)** the
specific incident's real, structured evidence and **(b)** retrieved
security knowledge — with the two kept clearly separate so the analyst
always knows what's an observed fact versus an AI's interpretation.

## Product Overview

An analyst opens ShadowTrace, launches one of four controlled attack
simulations, and watches a realistic (but entirely synthetic) sequence of
events get generated. A detection engine and a statistical anomaly model
independently analyze those events. Findings and an anomaly score feed
an evidence-based severity calculation. The analyst opens the resulting
incident, reviews the evidence, attack chain, and timeline, asks the AI
Analyst questions (grounded in the incident + a local RAG knowledge base,
with sources cited), reviews a clearly-labeled "potential next stage"
section, and generates a full incident report.

## Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                          Streamlit UI (app.py)                      │
│  Overview │ Simulator │ Investigations │ Timeline │ Threat Intel     │
│  AI Analyst │ Incidents │ Reports │ RAG Evaluation                  │
└───────────────┬───────────────────────────────────┬─────────────────┘
                │                                     │
                ▼                                     ▼
    ┌───────────────────────┐            ┌─────────────────────────┐
    │   simulation/          │            │   rag/                  │
    │   - scenarios.py        │            │   - ingestion.py         │
    │   - event_generator.py  │            │   - retrieval.py         │
    │   - pipeline.py          ──────┐    │   - context_builder.py   │
    └───────────────────────┘        │    │   - llm_client.py        │
                │                     │    │   - analyst.py           │
                ▼                     │    │   - next_stage.py        │
    ┌───────────────────────┐        │    └───────────┬─────────────┘
    │   detection/            │        │                │
    │   - rules.py             │        │                ▼
    │   - anomaly_detection.py │        │     ┌─────────────────────┐
    │   - severity.py          │        │     │ data/knowledge_base/ │
    └───────────┬───────────┘        │     │ (11 synthetic .md docs)│
                │                     │     └─────────────────────┘
                ▼                     ▼
        ┌─────────────────────────────────┐
        │      database/db.py (SQLite)     │
        │  simulations · events · findings │
        │  incidents · analyst_qa           │
        └─────────────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────┐
        │  reporting/incident_report.py    │
        │  evaluation/rag_evaluation.py    │
        └─────────────────────────────────┘
```

## Simulation Engine

Four controlled scenarios (`simulation/scenarios.py`) each define a stage
chain (used for the attack-chain visualization) and generation parameters.
`simulation/event_generator.py` turns a scenario into a concrete, randomized
sequence of structured JSON-like events — failure counts, timing jitter,
and source/resource selection vary between runs so repeated simulations of
the same scenario don't look identical. Every event is stored in SQLite
with a stable schema (`timestamp`, `event_type`, `user`, `source_ip`,
`resource`, `action`, `status`, `detail`).

Scenarios: **Credential Abuse**, **Malicious File**, **Web Application
Abuse**, **Insider Threat**.

## Detection Engine

`detection/rules.py` implements 11 deterministic rules, each of which
inspects the actual generated events for a session and only fires if its
condition is genuinely met (e.g. "≥4 failed logins immediately followed by
a success", "a suspicious process event followed by an outbound
connection", "≥20 document accesses in one session"). Every finding
carries the description, contributing event IDs (the evidence), a
severity-point contribution, and an illustrative technique label. Nothing
is hardcoded independent of the actual events.

## Anomaly Detection

`detection/anomaly_detection.py` extracts six interpretable session
features (resource accesses, distinct resources, failed-auth count,
documents accessed, transfer volume, distinct source IPs) and scores the
session with a **scikit-learn IsolationForest** trained on a synthetic
baseline population of "normal" sessions built from documented typical
ranges. If IsolationForest genuinely isn't informative (e.g. import
failure), the module transparently falls back to a threshold check on the
same features rather than force an ML verdict.

## RAG Pipeline

```text
Current Investigation → Question → Query Embedding → Vector Search
   → Relevant Knowledge → Context Construction (OBSERVED + RETRIEVED)
   → LLM → Grounded Answer (OBSERVED / INTERPRETATION / RECOMMENDATION)
```

`rag/ingestion.py` chunks the 11 knowledge-base markdown documents by
section. `rag/retrieval.py` embeds chunks with `sentence-transformers`
(`all-MiniLM-L6-v2`) and indexes them in **FAISS** for cosine-similarity
search; if that stack isn't available in a given environment (no network
to download the model, dependency not installed), it transparently falls
back to **TF-IDF + cosine similarity** (scikit-learn only) behind the
identical `search(query, top_k)` interface, so nothing downstream needs to
know which backend served a query — the UI shows which one is active.

`rag/context_builder.py` is what makes this genuinely incident-aware
rather than a generic document chatbot: every AI Analyst call
automatically assembles an **OBSERVED** block from the *current
incident's* real events, findings, and anomaly result, alongside
**RETRIEVED KNOWLEDGE** chunks relevant to the analyst's question. The
current incident is never optional context — it's always injected.

## AI Analyst

`rag/llm_client.py` tries, in order: **Anthropic** (`ANTHROPIC_API_KEY`),
a **generic OpenAI-compatible endpoint** (`OPENAI_API_KEY` +
`OPENAI_BASE_URL`), or an **offline template fallback** if neither is
configured (or a live call fails) — the fallback builds an honest,
clearly-labeled answer straight from the OBSERVED + RETRIEVED context
rather than fabricating a model response, so the whole app remains fully
demoable with zero API keys.

The system prompt instructs the model to structure every answer as
**OBSERVED / INTERPRETATION / RECOMMENDATION**, to only state facts
present in the given OBSERVED context, and to explicitly say *"The
available security knowledge does not provide enough information to
support this conclusion"* when retrieval doesn't cover the question,
rather than guessing. Every answer displays its cited sources
(document + section + relevance score).

## Investigation Workflow

1. **Simulate** — pick a scenario, click Run Simulation.
2. **Detect** — rules + anomaly detection run automatically; severity is
   calculated from what actually fired.
3. **Investigate** — open the incident: evidence with linked event IDs,
   attack chain, full related-event timeline, relevant threat intel.
4. **Understand** — ask the AI Analyst follow-up questions; review the
   clearly-labeled "Potential Next-Stage Behaviour" section.
5. **Respond** — review recommended investigation steps and defensive
   controls (recommendations only — nothing is auto-executed); generate
   a full incident report (Markdown + PDF).

## Evaluation

`evaluation/rag_evaluation.py` runs the retriever (and, where an LLM is
configured, the generator) live against `data/evaluation/eval_set.json`
(12 question → expected-document → expected-topic triples) and computes:
**Hit Rate@k**, **Precision@1**, **Mean Reciprocal Rank**, **Source
Correctness**, and a lexical **Answer Relevance** proxy. Nothing is
invented — every number comes from an actual run against whichever
backend (embeddings or TF-IDF fallback, live LLM or offline template) is
configured; a sample run using the TF-IDF fallback + offline template
produced Hit Rate@3 = 0.917, Precision@1 = 0.833, MRR = 0.875. Results are
shown live in the **RAG Evaluation** page.

## Security Considerations & Safety Boundary

- All simulation data (users, IPs, resources, events) is synthetic;
  IP addresses are drawn from RFC 5737 documentation ranges.
- No functionality performs real network requests to attack targets,
  real credential theft, real malware deployment, or real data
  exfiltration.
- No `eval()`/`exec()`/arbitrary shell execution is used anywhere in the
  app.
- Secrets (LLM API keys) are read from environment variables via
  `python-dotenv`; nothing is hardcoded, and `.env` is git-ignored.
- All SQL is parameterized.
- The "Potential Next-Stage Behaviour" and "What Could Happen Next"
  features only ever surface predefined, non-actionable category labels
  (e.g. "additional account access attempts") — never step-by-step
  offensive instructions.
- Defensive recommendations are informational only; the app never
  auto-executes a response action.

## Technology Stack

Python · Streamlit · SQLite · Pandas · Plotly · scikit-learn
(IsolationForest, TF-IDF) · sentence-transformers · FAISS · an
Anthropic/OpenAI-compatible LLM (optional) · reportlab (PDF export)

## Installation

```bash
git clone <this project>
cd ShadowTrace
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # optionally add an LLM API key
```

## Running the Application

```bash
streamlit run app.py
```

On first launch, `data/shadowtrace.db` (SQLite) is created automatically.
Use the **Reset all demo data** control in the sidebar at any time to
start fresh. If `sentence-transformers`/`faiss-cpu` aren't installed or
can't reach the network to download the embedding model, the app
automatically uses the TF-IDF fallback retriever — everything still works,
just with a simpler retrieval backend (this is logged in the UI).

## Example Investigation

1. Go to **Attack Simulator**, select **Credential Abuse**, click
   **Run Simulation**. A new incident (e.g. `ST-1042`) is created.
2. Go to **Investigations**, select `ST-1042`. Review the findings (e.g.
   "Repeated Authentication Failure Followed by Success"), the attack
   chain, and the related events.
3. Go to **AI Analyst**, ask *"Why is this suspicious?"* — the answer
   cites the actual failed/success login events and the relevant
   "Authentication Attacks" / "Credential Abuse" knowledge base sections.
4. Go to **Reports**, generate and download the full incident report.

## Limitations

- Detection rules are deterministic and scenario-scoped; they will not
  generalize to attack patterns outside their defined conditions.
- The anomaly baseline is a synthetic population, not a learned baseline
  from a real historical environment.
- The offline LLM fallback is template-based, not a language model — it's
  transparent about this, but its reasoning is naturally shallower than a
  live LLM call.
- The TF-IDF retrieval fallback is lexical, not semantic — it can miss
  paraphrased matches that an embedding model would catch.
- Answer Relevance in the evaluation harness is a lexical-overlap proxy,
  not an LLM-judge score, since no API key is assumed to be configured.

## Future Improvements

- Add an LLM-judge-based evaluation mode when an API key is configured,
  alongside the always-available lexical proxy.
- Learn per-user baselines for anomaly detection instead of one global
  synthetic baseline.
- Add a lightweight case-management layer (assignment, comments, audit
  log of status changes).
- Expand the knowledge base and add citation-level highlighting in the
  UI.

---

## Resume Bullets

- Built ShadowTrace AI, an AI-assisted threat investigation platform
  combining a rule-based + Isolation-Forest anomaly detection engine with
  an incident-aware RAG pipeline (sentence-transformer embeddings + FAISS,
  with a graceful TF-IDF fallback) that grounds every AI Analyst answer in
  live incident evidence and cited security knowledge sources.
- Designed and implemented a controlled adversary-simulation engine
  generating four distinct, randomized synthetic attack scenarios
  (credential abuse, malware execution, web abuse, insider threat), with
  evidence-based severity scoring fully traceable to the detection
  findings that produced it.
- Built and ran a live RAG evaluation harness (retrieval hit-rate,
  precision@1, MRR, source correctness, answer relevance) against a
  held-out question set, producing reproducible, non-fabricated metrics
  surfaced in-product.
