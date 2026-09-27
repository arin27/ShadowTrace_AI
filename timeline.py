from __future__ import annotations

import streamlit as st

from database import db as dbmod
from rag.context_builder import retrieve_for_question, scenario_name_to_key
from ui.common import select_incident

# Maps a specific event action to a short "why it matters" + detection rule
# name + illustrative technique label, purely for the timeline explainer.
EVENT_EXPLAINERS = {
    "login_failed": ("Repeated failures can indicate password guessing.", "Repeated Authentication Failure", "Brute Force (simulated)"),
    "login_success": ("A success immediately after failures may indicate the correct credential was eventually used.", "Repeated Authentication Failure Followed by Success", "Valid Accounts (simulated)"),
    "session_source_flagged": ("Authentication from a new source is a corroborating signal, not proof alone.", "Authentication From Previously Unseen Source", "Valid Accounts (simulated)"),
    "resource_access": ("First-time or sensitive resource access changes the risk of a session.", "Sensitive Resource Accessed / Data Access Anomaly", "Collection (simulated)"),
    "privilege_request": ("Escalation requests are a common pivot point in an incident.", "Privilege Request Following Unfamiliar Resource Access", "Privilege Escalation (simulated)"),
    "attachment_received": ("Delivery is the first stage of a phishing-style chain.", "n/a (delivery stage)", "Phishing (simulated)"),
    "attachment_opened": ("User execution is the trigger point for most malware chains.", "n/a (execution stage)", "User Execution (simulated)"),
    "child_process_spawned": ("Unexpected parent-child process relationships are a strong malware indicator.", "Suspicious Process Followed by Outbound Connection", "Execution (simulated)"),
    "outbound_connection": ("Outbound connections to unknown destinations may indicate C2 activity.", "Suspicious Process Followed by Outbound Connection", "Command & Control (simulated)"),
    "persistence_artifact_created": ("Persistence mechanisms let an attacker survive a reboot/logoff.", "Persistence Mechanism Observed", "Persistence (simulated)"),
    "http_request": ("Repeated malformed/suspicious requests suggest probing behaviour.", "Repeated Malformed Input", "Exploit Public-Facing Application (simulated)"),
    "application_error": ("Errors correlated with malformed input may indicate an unexpected code path was reached.", "n/a (correlation signal)", "Defense Evasion (simulated)"),
    "resource_access_attempt": ("A denied attempt at a restricted resource is a direct authorization-boundary test.", "Unauthorized Resource Access Attempt", "Privilege Escalation (simulated)"),
    "document_access": ("High-volume document access is the main insider-threat volume signal.", "Abnormally High Document Access Volume", "Collection (simulated)"),
    "large_data_transfer": ("Large transfers following bulk access are the clearest exfiltration signal.", "Large Outbound Data Transfer", "Exfiltration (simulated)"),
}


def render():
    st.title("Attack Timeline")
    st.caption("Interactive, ordered view of the events that make up a simulated session.")

    incident_id = select_incident("timeline")
    if not incident_id:
        return

    incident = dbmod.get_incident(incident_id)
    events = dbmod.get_events(incident["sim_id"])
    scenario_key = scenario_name_to_key(incident["scenario"])

    st.markdown("---")
    for e in events:
        ts = e["timestamp"].split("T")[-1][:8]
        label = f"**{ts}**  ·  {e['event_type']}  ·  {e['action']}"
        if e.get("resource"):
            label += f"  ·  `{e['resource']}`"
        st.markdown(f'<div class="timeline-item">{label}</div>', unsafe_allow_html=True)

        with st.expander("Details", expanded=False):
            st.json({
                "event_id": e["event_id"], "timestamp": e["timestamp"],
                "user": e["user"], "source_ip": e["source_ip"],
                "resource": e["resource"], "action": e["action"],
                "status": e["status"], "detail": e["detail"],
            })
            explain, rule, technique = EVENT_EXPLAINERS.get(
                e["action"], ("This event contributes session context.", "n/a", "n/a")
            )
            st.markdown(f"**Why it matters:** {explain}")
            st.markdown(f"**Related detection rule:** {rule}")
            st.markdown(f"**Possible technique label:** {technique}")

            related = [
                other for other in events
                if other["event_id"] != e["event_id"]
                and (other.get("resource") == e.get("resource") or other.get("source_ip") == e.get("source_ip"))
            ][:5]
            if related:
                st.markdown("**Related events:**")
                for r in related:
                    st.caption(f"{r['timestamp']} · {r['action']} · {r.get('resource') or '-'}")

            kb_results = retrieve_for_question(scenario_key, f"{e['action']} {e['event_type']}", top_k=2)
            if kb_results:
                st.markdown("**Relevant knowledge base entries:**")
                for r in kb_results:
                    st.markdown(
                        f'<span class="source-chip">{r.chunk.doc_title} · {r.chunk.section}</span>',
                        unsafe_allow_html=True,
                    )
