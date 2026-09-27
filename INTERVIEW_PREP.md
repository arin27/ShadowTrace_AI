# ShadowTrace AI — Interview Preparation

Simple, technically accurate answers you can give confidently in an
interview. Each answer is a few sentences — expand with specifics from the
README if asked to go deeper.

---

**1. Why did you build ShadowTrace?**
I wanted a project that showed genuine AI + security engineering rather
than a generic "chat with a PDF" demo. The idea was: simulate a realistic
incident, detect it with real logic, and let an AI Analyst investigate it
using the incident's own evidence plus a grounded knowledge base — the
same shape as a real SOC investigation, just running on synthetic data.

**2. Why RAG instead of just asking an LLM directly?**
An LLM on its own would either hallucinate security guidance or give
generic, ungrounded advice. RAG lets me retrieve specific, curated
knowledge-base passages relevant to the question and force the model to
reason from that plus the incident's actual evidence, which makes answers
both more accurate and traceable back to a source.

**3. Why isn't this just a chatbot?**
A generic chatbot answers questions about a static document set with no
awareness of what's actually happening. Every AI Analyst call here
automatically builds an OBSERVED context block from the *current*
incident's real events, findings, and anomaly score — the incident is
never optional context, it's injected into every single request.

**4. How does the RAG pipeline work end to end?**
Knowledge base markdown files are chunked by section → embedded (or
TF-IDF vectorized, as a fallback) → indexed for similarity search. When
the analyst asks a question, I build a query from the question plus a
scenario hint, retrieve the top-k chunks, and combine them with an
OBSERVED summary of the incident into one prompt. The LLM is instructed
to answer only from that combined context.

**5. Why embeddings?**
Embeddings capture semantic similarity, not just keyword overlap, so a
question like "why did the login succeed after failing" can match a
passage about "successful authentication following repeated failures"
even without exact word overlap.

**6. Why FAISS?**
FAISS gives fast, in-memory approximate/exact nearest-neighbor search over
the embedding vectors. For a knowledge base this small (a few dozen
chunks) an exact flat index (`IndexFlatIP`) is plenty — the choice mainly
demonstrates I understand the standard vector-search tool, and FAISS
scales if the knowledge base grew much larger.

**7. What happens if FAISS/sentence-transformers aren't available?**
The retriever transparently falls back to TF-IDF + cosine similarity
(scikit-learn only, no model download needed) behind the exact same
`search(query, top_k)` interface. Nothing downstream — context builder,
analyst, evaluation — needs to know which backend served a query. The UI
shows which backend is active so it's never silently misleading.

**8. How does the AI receive incident context?**
`context_builder.py` pulls the incident record, its events, its detection
findings, and its anomaly result from SQLite, formats them into a plain
OBSERVED text block, and concatenates that with the retrieved knowledge
chunks before sending anything to the LLM (or the offline fallback).

**9. How do you prevent hallucinations?**
Three layers: (1) the system prompt explicitly instructs the model to only
state facts present in OBSERVED and to say when retrieved knowledge is
insufficient rather than guess; (2) I structure every answer into
OBSERVED / INTERPRETATION / RECOMMENDATION so speculation is never
presented as fact; (3) every answer shows its cited sources so a human can
verify.

**10. How do you distinguish observed behaviour from AI interpretation?**
Structurally, via the required three-part answer format. OBSERVED can only
restate what's actually in the evidence I hand the model. INTERPRETATION
is explicitly framed as reasoning, not certainty. This is enforced by the
system prompt and reinforced by the UI presenting sources separately.

**11. How does anomaly detection work?**
I extract six interpretable features per session (resource accesses,
distinct resources, failed-auth count, documents accessed, transfer
volume, distinct source IPs), fit an IsolationForest on a synthetic
baseline population representing "normal" sessions, and score the current
session against it. IsolationForest isolates points that are easy to
separate from the bulk of the data — anomalies need fewer random splits
to isolate, which gives a continuous anomaly score.

**12. Why Isolation Forest specifically?**
It doesn't require labeled anomaly examples (which I don't have, since
these are synthetic scenarios, not a large labeled dataset), it's fast on
small feature vectors, and it's easy to explain: "this session was easy to
separate from typical sessions" is intuitive to a non-technical audience.

**13. How are attack scenarios generated?**
Each scenario is a stage chain (used for the attack-chain visualization)
plus generation logic that produces a randomized sequence of structured
events — variable failure counts, timing jitter, and resource/source
selection — so repeated runs of the same scenario look different but
follow the same underlying pattern.

**14. Why are attacks simulated rather than real?**
Because the goal is to demonstrate detection and investigation reasoning,
not to build an offensive tool. Real exploitation would be both unsafe and
inappropriate for a demo/portfolio project; synthetic data lets me control
exactly what "ground truth" looks like, which is also what makes rigorous,
non-fabricated evaluation possible.

**15. How is severity calculated?**
It's the sum of each fired detection rule's severity-point contribution,
plus a bonus if the anomaly detector flagged the session, mapped to
CRITICAL/HIGH/MEDIUM/LOW bands. Every point is traceable to a specific
finding or the anomaly result — nothing is assigned severity without a
listed reason.

**16. How did you evaluate RAG?**
I built a 12-question evaluation set, each with an expected source
document and topic, and wrote a harness that actually runs retrieval (and
generation, if configured) against every question, computing Hit
Rate@k, Precision@1, Mean Reciprocal Rank, Source Correctness, and a
lexical Answer Relevance proxy. These are live-computed, not invented —
I can re-run it any time and get a number.

**17. What are the limitations?**
Detection rules only catch patterns I explicitly encoded; the anomaly
baseline is synthetic, not learned from a real environment; the offline
LLM fallback is template logic, not a model, so its reasoning is
shallower; TF-IDF retrieval is lexical and can miss paraphrases an
embedding model would catch; and my Answer Relevance metric is a lexical
proxy, not an LLM-judge score.

**18. What would you change for production?**
Add per-user/per-role behavioural baselines instead of one global
synthetic baseline, add an LLM-judge evaluation mode, add real
case-management features (assignment, audit log, SLA tracking), and
harden the anomaly model with real historical data rather than a
documented-range synthetic population.

**19. How would this integrate into a real SOC?**
The detection/anomaly/severity layer would sit downstream of a real SIEM
or log pipeline instead of the synthetic event generator — the interfaces
(`run_detection(events)`, `detect_anomaly(events)`) already take a plain
list of structured event dicts, so swapping the data source doesn't
require changing the detection logic. The RAG knowledge base would be
expanded with the organization's actual playbooks and threat intel feeds.

**20. What part of the system is deterministic, and what part uses AI?**
Deterministic: event generation logic, all 11 detection rules, severity
scoring, and the report/next-stage template logic. AI/ML: the
IsolationForest anomaly model, the embedding-based (or TF-IDF) retrieval
ranking, and the LLM reasoning step in the AI Analyst. Keeping this split
explicit is intentional — an interviewer should be able to point at any
feature and I can say exactly which category it falls into.

**21. Why did you keep the architecture "boring" (no microservices, no Kafka,
no multi-agent system)?**
Because none of that complexity would make the product better — it's a
single-analyst, single-machine investigation tool. Adding infrastructure
the problem doesn't need would be worse engineering, not better, and
would distract from the actual technical substance: the detection logic,
the anomaly model, and the RAG grounding.

**22. How do you keep the app secure by construction?**
No `eval`/`exec`/shell execution anywhere; all SQL is parameterized; no
hardcoded secrets (API keys load from `.env` via `python-dotenv`); all
data is synthetic so there's no real sensitive data to leak; input to the
app itself (scenario selection, chat questions) doesn't touch the
filesystem or execute code.
