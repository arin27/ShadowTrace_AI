from __future__ import annotations

import pandas as pd
import streamlit as st

from database import db as dbmod
from ui.theme import severity_badge, status_badge


def render():
    st.title("Incidents")
    st.caption("Full incident register across all simulations.")

    incidents = dbmod.list_incidents()
    if not incidents:
        st.info("No incidents yet. Go to **Attack Simulator** to run a simulation.")
        return

    c1, c2 = st.columns(2)
    with c1:
        sev_filter = st.multiselect("Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                     default=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with c2:
        status_filter = st.multiselect("Status", ["UNDER INVESTIGATION", "RESOLVED", "CLOSED"],
                                        default=["UNDER INVESTIGATION", "RESOLVED", "CLOSED"])

    filtered = [i for i in incidents if i["severity"] in sev_filter and i["status"] in status_filter]

    st.markdown(f"**{len(filtered)} incident(s)**")
    for i in filtered:
        with st.container():
            cols = st.columns([2, 2, 1, 1, 2, 1])
            cols[0].markdown(f"**{i['incident_id']}**")
            cols[1].markdown(i["scenario"])
            cols[2].markdown(severity_badge(i["severity"]), unsafe_allow_html=True)
            cols[3].markdown(status_badge(i["status"]), unsafe_allow_html=True)
            cols[4].markdown(f"`{i.get('affected_user')}`")
            if cols[5].button("Open", key=f"open_{i['incident_id']}"):
                st.session_state["selected_incident_id"] = i["incident_id"]
                st.session_state["nav_override"] = "Investigations"
                st.rerun()
            st.markdown("---")
