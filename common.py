from __future__ import annotations

import streamlit as st

from database import db as dbmod


def select_incident(key_prefix: str) -> str | None:
    """Renders an incident selector and returns the chosen incident_id, or
    None if there are no incidents yet. Persists selection in session_state
    so navigating between pages keeps the same incident in context."""
    incidents = dbmod.list_incidents()
    if not incidents:
        st.info("No incidents yet. Go to **Attack Simulator** to run a simulation first.")
        return None

    options = {f"{i['incident_id']} — {i['scenario']} ({i['severity']})": i["incident_id"]
               for i in incidents}
    current = st.session_state.get("selected_incident_id")
    labels = list(options.keys())
    default_idx = 0
    if current:
        for idx, (label, iid) in enumerate(options.items()):
            if iid == current:
                default_idx = idx
                break

    chosen_label = st.selectbox("Select Incident", labels, index=default_idx, key=f"{key_prefix}_incident_select")
    incident_id = options[chosen_label]
    st.session_state["selected_incident_id"] = incident_id
    return incident_id
