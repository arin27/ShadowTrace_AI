from __future__ import annotations

import streamlit as st

from simulation.pipeline import run_simulation_pipeline
from simulation.scenarios import SCENARIOS
from ui.theme import severity_badge

SCENARIO_CHAIN_TEXT = {
    "credential_abuse": "Multiple Failed Logins → Successful Authentication → Unusual Source → "
                         "Previously Unused Resource → Privilege Request → Sensitive Resource Access",
    "malicious_file": "Suspicious Attachment Received → User Opens Attachment → Suspicious Process → "
                       "Unexpected Outbound Connection → Persistence Attempt",
    "web_abuse": "Suspicious Request → Repeated Malformed Input → Application Error → "
                 "Unauthorized Resource Attempt → Repeated Suspicious Requests",
    "insider_threat": "Normal Activity → Unusual Access Time → Large Document Access → "
                       "Sensitive Resource Access → Large Transfer",
}


def render():
    st.title("Attack Simulator")
    st.caption(
        "Launch a controlled, fully synthetic attack scenario. All users, IPs, and "
        "resources are fictional. No real systems are contacted."
    )

    scenario_key = st.session_state.get("sim_scenario_key", "credential_abuse")

    cols = st.columns(4)
    keys = list(SCENARIOS.keys())
    for col, key in zip(cols, keys):
        with col:
            selected = scenario_key == key
            label = f"**{SCENARIOS[key]['name']}**" + (" ✅" if selected else "")
            if st.button(label, use_container_width=True, key=f"scenario_btn_{key}"):
                st.session_state["sim_scenario_key"] = key
                st.rerun()

    scenario_key = st.session_state.get("sim_scenario_key", "credential_abuse")
    scenario = SCENARIOS[scenario_key]

    st.markdown("---")
    st.subheader(scenario["name"])
    st.write(scenario["description"])
    st.markdown(f"`{SCENARIO_CHAIN_TEXT[scenario_key]}`")

    st.markdown("---")
    run_col, _ = st.columns([1, 3])
    with run_col:
        run_clicked = st.button("▶ RUN SIMULATION", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner("Generating synthetic events and running detection..."):
            incident_id = run_simulation_pipeline(scenario_key)
        st.session_state["last_incident_id"] = incident_id
        st.session_state["selected_incident_id"] = incident_id
        st.success(f"Simulation complete. Incident **{incident_id}** created.")

    last_id = st.session_state.get("last_incident_id")
    if last_id:
        from database import db as dbmod
        inc = dbmod.get_incident(last_id)
        if inc:
            st.markdown("### Result")
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Incident:** {inc['incident_id']}")
            c2.markdown(f"**Severity:** {severity_badge(inc['severity'])}", unsafe_allow_html=True)
            c3.markdown(f"**Status:** {inc['status']}")
            events = dbmod.get_events(inc["sim_id"])
            findings = dbmod.get_findings(inc["sim_id"])
            st.write(f"{len(events)} events generated · {len(findings)} detection finding(s) fired.")
            st.info("Open **Investigations** to explore the full evidence, attack chain, "
                    "timeline, and AI Analyst for this incident.")
