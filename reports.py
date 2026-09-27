from __future__ import annotations

import streamlit as st

from database import db as dbmod
from reporting.incident_report import generate_report_markdown, generate_report_pdf_bytes
from ui.common import select_incident


def render():
    st.title("Reports")
    st.caption("Generate a full incident report from the persisted evidence, findings, and AI Analyst Q&A.")

    incident_id = select_incident("reports")
    if not incident_id:
        return

    incident = dbmod.get_incident(incident_id)
    st.markdown(f"**Incident:** {incident['incident_id']} — {incident['scenario']} ({incident['severity']})")

    if st.button("📄 Generate Incident Report", type="primary"):
        with st.spinner("Assembling report from evidence, findings, and Q&A history..."):
            md_report = generate_report_markdown(incident_id)
        st.session_state["generated_report_md"] = md_report
        st.session_state["generated_report_incident"] = incident_id

    md_report = st.session_state.get("generated_report_md")
    if md_report and st.session_state.get("generated_report_incident") == incident_id:
        st.markdown("---")
        st.download_button(
            "⬇ Download as Markdown (.md)",
            data=md_report,
            file_name=f"{incident_id}_report.md",
            mime="text/markdown",
        )

        pdf_bytes = generate_report_pdf_bytes(incident_id)
        if pdf_bytes:
            st.download_button(
                "⬇ Download as PDF",
                data=pdf_bytes,
                file_name=f"{incident_id}_report.pdf",
                mime="application/pdf",
            )
        else:
            st.caption("Install `reportlab` to enable PDF export (Markdown export always available).")

        st.markdown("---")
        st.markdown(md_report)
