# ShadowTrace AI

### AI-Assisted Cybersecurity Investigation & Threat Intelligence Platform

ShadowTrace AI is a **security investigation platform** that combines controlled attack simulation, anomaly detection, Retrieval-Augmented Generation (RAG), and AI-assisted incident analysis.

Instead of simply showing security logs, ShadowTrace helps answer:

> **What happened? Why is it suspicious? What evidence supports it? What should an analyst investigate next?**

The project is designed as a **safe, local cybersecurity laboratory** using synthetic enterprise security data and controlled attack scenarios.

---

## What ShadowTrace Does

ShadowTrace follows an end-to-end investigation workflow:

```text
Attack Simulation
       ↓
Security Events
       ↓
Detection & Anomaly Analysis
       ↓
Incident Investigation
       ↓
RAG Threat Intelligence
       ↓
AI-Assisted Analysis
       ↓
Investigation & Response Guidance
       ↓
Incident Report
```

### Core capabilities

* Controlled attack simulation
* Suspicious activity detection
* Anomaly detection
* Evidence-based incident analysis
* RAG-powered cybersecurity knowledge retrieval
* AI-assisted investigation
* Attack timeline reconstruction
* Severity classification
* Threat intelligence search
* Incident report generation
* RAG evaluation
* Incident history and persistence

---

## Controlled Attack Lab

ShadowTrace includes simulated enterprise security scenarios rather than attacking real systems.

Example scenarios include:

* Credential Abuse
* Suspicious Web Activity
* Insider Data Access
* Privilege Escalation

Each scenario generates a realistic sequence of synthetic security events.

For example:

```text
Failed Login
      ↓
Successful Login
      ↓
Unusual Source
      ↓
Sensitive Resource Access
      ↓
Privilege Attempt
```

The generated events become the evidence used by the investigation engine.

> All scenarios are simulated and intended for defensive learning and experimentation.

---

## Detection Engine

ShadowTrace analyzes generated security events using a combination of:

### Rule-based detection

Security rules identify known suspicious patterns such as:

* Repeated authentication failures
* Unusual access
* Privilege-related activity
* Sensitive resource access
* Suspicious web requests

### Anomaly detection

The project also includes an **Isolation Forest** model to identify unusual event behaviour.

This allows the system to combine deterministic security rules with lightweight machine-learning-based anomaly detection.

---

## RAG Threat Intelligence

The RAG component provides cybersecurity context for an investigation.

The knowledge base contains information about topics such as:

* Credential Abuse
* Privilege Escalation
* Insider Threats
* Web Application Attacks
* Incident Response
* Defensive Controls

When an incident is investigated:

```text
Incident Evidence
       ↓
Query Construction
       ↓
Knowledge Retrieval
       ↓
Relevant Security Context
       ↓
AI-Assisted Analysis
```

The retrieved information is shown with its source so that the analyst can understand where the security guidance came from.

---

## AI Analyst

The AI Analyst combines:

**Incident Evidence + Retrieved Security Knowledge**

to provide an investigation summary.

An analyst can ask questions such as:

> Why is this activity suspicious?

> What evidence supports this finding?

> What type of attack behaviour does this resemble?

> What should I investigate next?

> What defensive controls could reduce this risk?

The system is designed to **assist the analyst rather than replace the analyst**.

---

## Investigation Dashboard

The Streamlit interface provides a security-focused investigation workspace.

### Dashboard

Displays:

* Total incidents
* Active findings
* Severity distribution
* Detection statistics
* Recent investigations

### Incident Investigation

Each incident contains:

* Incident ID
* Scenario
* Severity
* Timeline
* Evidence
* Detection results
* Anomaly information
* Related threat intelligence
* Recommended investigation steps

### Threat Intelligence

Allows analysts to search the local cybersecurity knowledge base and retrieve relevant security guidance.

### Incident History

Previous investigations are stored locally using SQLite.

---

## Technology Stack

| Area              | Technology       |
| ----------------- | ---------------- |
| Language          | Python           |
| Interface         | Streamlit        |
| Data Processing   | Pandas           |
| Machine Learning  | Scikit-learn     |
| Anomaly Detection | Isolation Forest |
| RAG               | TF-IDF Retrieval |
| Database          | SQLite           |
| Reports           | ReportLab        |
| Testing           | Pytest           |
| Configuration     | Python-dotenv    |

The architecture is intentionally lightweight so that the project can run locally without requiring expensive infrastructure or external cloud services.

---

## Project Structure

```text
ShadowTraceAI/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── simulator.py
│   ├── detector.py
│   ├── anomaly.py
│   ├── rag.py
│   ├── analyst.py
│   ├── database.py
│   └── reporter.py
│
├── data/
│   └── knowledge_base/
│       ├── credential_abuse.txt
│       ├── privilege_escalation.txt
│       ├── insider_threat.txt
│       ├── web_attacks.txt
│       └── incident_response.txt
│
├── evaluation/
│   └── rag_eval.py
│
├── tests/
│   └── test_core.py
│
├── docs/
│   └── architecture.md
│
└── INTERVIEW_PREP.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/shadowtrace-ai.git
cd shadowtrace-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env
```

No external API key is required for the baseline local version.

---

## Run the Application

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

---

## Run Tests

```bash
pytest -q
```

---

## Evaluate the RAG System

The repository includes a small evaluation set for measuring whether the retrieval system returns relevant cybersecurity knowledge.

Run:

```bash
python evaluation/rag_eval.py
```

The evaluation focuses on retrieval relevance rather than claiming that the system is production-grade.

---

## Architecture


                  ┌─────────────────────┐
                  │  Attack Simulator   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Security Events   │
                  └──────────┬──────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐      ┌─────────────────┐
       │ Rule Detection  │      │ Anomaly Model   │
       └────────┬────────┘      └────────┬────────┘
                │                        │
                └────────────┬───────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Investigation Layer│
                  └──────────┬──────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ Incident Data   │   │ RAG Knowledge   │
        │ + Evidence      │   │ Base            │
        └────────┬────────┘   └────────┬────────┘
                 └──────────┬──────────┘
                            ▼
                  ┌─────────────────────┐
                  │     AI Analyst      │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Analyst Guidance &  │
                  │ Incident Report     │
                  └─────────────────────┘
```

---

## Security & Safety

ShadowTrace is intentionally designed as a **defensive cybersecurity project**.

It does not:

* Attack real websites
* Scan public infrastructure
* Generate real credentials
* Store real personal information
* Execute arbitrary attack payloads
* Perform destructive actions
* Automatically modify external systems

All security scenarios are simulated locally.

---

## Why This Project?

Traditional security dashboards often answer:

> **"What happened?"**

ShadowTrace attempts to go one step further:

> **"What happened, why does it matter, what evidence supports it, and what should the analyst investigate next?"**

The project demonstrates the integration of:

* Cybersecurity
* Machine Learning
* RAG
* Natural Language Interfaces
* Security Analytics
* Incident Response
* Data Processing

---

## Future Improvements

Possible extensions include:

* Vector database with semantic embeddings
* LLM-powered investigation summaries
* MITRE ATT&CK technique mapping
* More advanced event correlation
* Attack-chain visualization
* User authentication and role-based access
* Real-time event ingestion
* SIEM integration
* Automated detection-rule generation
* Larger RAG evaluation datasets
* Human-feedback-based evaluation

These features are intentionally left as future work rather than being presented as implemented functionality.

---

## Disclaimer

ShadowTrace AI is an **educational cybersecurity research project**.

All attack scenarios and security events are synthetic and designed for controlled experimentation.

Do not use the project to test systems or infrastructure without explicit authorization.

---

## Author

**Harini Eswari Ramesh Babu**

Cybersecurity Undergraduate
Python • Cybersecurity • Machine Learning • RAG • Security Analytics

---

⭐ If you found the project interesting, consider giving the repository a star.
