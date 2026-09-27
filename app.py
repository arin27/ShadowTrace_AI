"""
ShadowTrace AI — main Streamlit entry point.

SIMULATE -> DETECT -> INVESTIGATE -> UNDERSTAND -> RESPOND

Run with:  streamlit run app.py
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # populate os.environ from a local .env, if present — never hardcode secrets

from database import db as dbmod
from ui import (ai_analyst, incidents, investigations, overview, rag_eval,
                 reports, simulator, threat_intel, timeline)
from ui.theme import inject_css

st.set_page_config(
    page_title="ShadowTrace AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

dbmod.init_db()
inject_css()

PAGES = {
    "Overview": overview,
    "Attack Simulator": simulator,
    "Investigations": investigations,
    "Attack Timeline": timeline,
    "Threat Intelligence": threat_intel,
    "AI Analyst": ai_analyst,
    "Incidents": incidents,
    "Reports": reports,
    "RAG Evaluation": rag_eval,
}


def main():
    with st.sidebar:
        st.markdown("## 🛰️ ShadowTrace AI")
        st.caption("AI-Powered Adversary Intelligence & Threat Investigation Platform")
        st.markdown("---")

        default_page = st.session_state.pop("nav_override", "Overview")
        page_names = list(PAGES.keys())
        default_idx = page_names.index(default_page) if default_page in page_names else 0
        choice = st.radio("Navigate", page_names, index=default_idx, label_visibility="collapsed")

        st.markdown("---")
        st.caption("Safety boundary: all activity is simulated. No real systems, "
                   "credentials, or data are touched by this application.")

        with st.expander("Demo data"):
            if st.button("Reset all demo data", use_container_width=True):
                dbmod.reset_db()
                for k in ("last_incident_id", "selected_incident_id", "eval_result",
                          "generated_report_md"):
                    st.session_state.pop(k, None)
                st.success("Demo data reset.")
                st.rerun()

    PAGES[choice].render()


if __name__ == "__main__":
    main()
