from __future__ import annotations

import streamlit as st

from database import db as dbmod
from rag.context_builder import scenario_name_to_key
from rag.next_stage import get_next_stage
from ui.common import select_incident
from ui.theme import severity_badge, status_badge


def render():
    st.title("Investigations")
    st.caption("Investigation workspace — evidence, attack chain, and grounded analysis for a single incident.")

    incident_id = select_incident("investigations")
    if not incident_id:
        return

    incident = dbmod.get_incident(incident_id)
    events = dbmod.get_events(incident["sim_id"])
    findings = dbmod.get_findings(incident["sim_id"])
    scenario_key = scenario_name_to_key(incident["scenario"])

    st.markdown("---")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown(f"## INCIDENT #{incident['incident_id']}")
        st.markdown(f"**Scenario:** {incident['scenario']}")
    with c2:
        st.markdown("**Severity**")
        st.markdown(severity_badge(incident["severity"]), unsafe_allow_html=True)
    with c3:
        st.markdown("**Status**")
        new_status = st.selectbox(
            "status", ["UNDER INVESTIGATION", "RESOLVED", "CLOSED"],
            index=["UNDER INVESTIGATION", "RESOLVED", "CLOSED"].index(incident["status"]),
            label_visibility="collapsed", key="status_select",
        )
        if new_status != incident["status"]:
            dbmod.update_incident_status(incident_id, new_status)
            st.rerun()

    st.markdown(f"**Affected User:** `{incident.get('affected_user')}`  \n"
                f"**Affected Resources:** {', '.join(incident.get('affected_resources', [])) or 'none recorded'}")

    tabs = st.tabs([
        "What Happened", "Evidence", "Attack Chain", "Threat Intelligence",
        "Next-Stage Behaviour", "Recommended Response",
    ])

    with tabs[0]:
        st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
        if findings:
            st.write(
                f"This session produced {len(findings)} detection finding(s) and was "
                f"scored **{incident['severity']}** (score {incident['severity_score']})."
            )
            for f in findings:
                st.markdown(f"- **{f['rule_name']}** — {f['description']}")
        else:
            st.write("No deterministic detection rule fired for this simulation.")
        anomaly = incident.get("anomaly_summary", {})
        st.markdown('<div class="section-label">Anomaly Detection</div>', unsafe_allow_html=True)
        st.write(f"Method: `{anomaly.get('method')}` — "
                 f"Anomaly flagged: **{anomaly.get('is_anomaly')}** "
                 f"(score {anomaly.get('anomaly_score')})")
        for ex in anomaly.get("explanations", []):
            st.markdown(f"- {ex}")

        st.markdown('<div class="section-label">Severity Reasoning</div>', unsafe_allow_html=True)
        for r in incident.get("severity_reasoning", []):
            st.markdown(f"✓ {r}")

    with tabs[1]:
        st.markdown('<div class="section-label">Suspicious Behaviour & Evidence</div>', unsafe_allow_html=True)
        if not findings:
            st.info("No findings to display evidence for.")
        for f in findings:
            with st.expander(f"{f['rule_name']}  ·  +{f['severity_points']} pts  ·  {f.get('technique') or 'n/a'}"):
                st.write(f["description"])
                st.markdown("**Evidence (event IDs):**")
                ev_map = {e["event_id"]: e for e in events}
                for ev_id in f["evidence"]:
                    e = ev_map.get(ev_id)
                    if e:
                        st.markdown(
                            f'<div class="evidence-line">{e["timestamp"]} · {e["event_type"]} · '
                            f'{e["action"]} · {e.get("resource") or "-"} · {e["status"]}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f'<div class="evidence-line">{ev_id}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Related Events (Full Session)</div>', unsafe_allow_html=True)
        import pandas as pd
        df = pd.DataFrame(events)[["timestamp", "event_type", "action", "resource", "status", "source_ip"]]
        st.dataframe(df, use_container_width=True, hide_index=True, height=300)

    with tabs[2]:
        _render_attack_chain(scenario_key)

    with tabs[3]:
        st.markdown('<div class="section-label">Relevant Threat Intelligence</div>', unsafe_allow_html=True)
        from rag.context_builder import retrieve_for_question
        results = retrieve_for_question(scenario_key, "relevant indicators and response guidance", top_k=5)
        for r in results:
            with st.expander(f"{r.chunk.doc_title} — {r.chunk.section}  (relevance {r.score:.2f})"):
                st.write(r.chunk.text)

    with tabs[4]:
        next_stage = get_next_stage(scenario_key)
        st.warning(next_stage["disclaimer"])
        for b in next_stage["behaviours"]:
            st.markdown(f"→ {b}")
        if next_stage["supporting_sources"]:
            st.markdown('<div class="section-label">Supporting Sources</div>', unsafe_allow_html=True)
            for s in next_stage["supporting_sources"]:
                st.markdown(
                    f'<span class="source-chip">{s["document"]} · {s["section"]}</span>',
                    unsafe_allow_html=True,
                )

    with tabs[5]:
        from reporting.incident_report import recommended_investigation_steps, recommended_defensive_controls
        st.markdown('<div class="section-label">Recommended Investigation Steps</div>', unsafe_allow_html=True)
        for step in recommended_investigation_steps(scenario_key):
            st.markdown(f"- {step}")
        st.markdown('<div class="section-label">Recommended Defensive Controls</div>', unsafe_allow_html=True)
        for ctrl in recommended_defensive_controls(scenario_key):
            st.markdown(f"- {ctrl}")
        st.caption("These are recommendations only. No action is executed automatically.")


def _render_attack_chain(scenario_key: str):
    from simulation.scenarios import SCENARIOS
    stages = SCENARIOS[scenario_key]["stages"]
    st.markdown('<div class="section-label">Attack Chain (based on simulated scenario)</div>', unsafe_allow_html=True)
    st.caption("This visualizes the simulated scenario's stage sequence. It does not represent a real-world compromise.")
    for i, stage in enumerate(stages):
        st.markdown(f'<div class="chain-node">{stage["label"]}<br><small style="color:#6e7581">{stage["technique"]}</small></div>',
                    unsafe_allow_html=True)
        if i < len(stages) - 1:
            st.markdown('<div class="chain-arrow">↓</div>', unsafe_allow_html=True)
