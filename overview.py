from __future__ import annotations

from collections import Counter

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from database import db as dbmod
from ui.theme import kpi, severity_badge, status_badge


def render():
    st.title("Overview")
    st.caption("ShadowTrace AI — AI-Powered Adversary Intelligence & Threat Investigation Platform")

    incidents = dbmod.list_incidents()
    simulations = dbmod.list_simulations()

    active = [i for i in incidents if i["status"] == "UNDER INVESTIGATION"]
    high_risk = [i for i in incidents if i["severity"] in ("HIGH", "CRITICAL")]
    anomalies = [i for i in incidents if i.get("anomaly_summary", {}).get("is_anomaly")]
    total_findings = sum(len(dbmod.get_findings(i["sim_id"])) for i in incidents)

    cols = st.columns(5)
    with cols[0]:
        kpi("Active Investigations", len(active))
    with cols[1]:
        kpi("Suspicious Events (Findings)", total_findings)
    with cols[2]:
        kpi("High-Risk Incidents", len(high_risk))
    with cols[3]:
        kpi("Anomalies Detected", len(anomalies))
    with cols[4]:
        kpi("Simulations Run", len(simulations))

    st.write("")
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-label">Incident Severity</div>', unsafe_allow_html=True)
        sev_counts = Counter(i["severity"] for i in incidents)
        order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        colors = {"CRITICAL": "#e5484d", "HIGH": "#f5a524", "MEDIUM": "#f5d90a", "LOW": "#3ecf8e"}
        if incidents:
            fig = go.Figure(go.Bar(
                x=[sev_counts.get(s, 0) for s in order],
                y=order,
                orientation="h",
                marker_color=[colors[s] for s in order],
                text=[sev_counts.get(s, 0) for s in order],
                textposition="outside",
            ))
            fig.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c4c9d1", xaxis=dict(gridcolor="#232936"),
                yaxis=dict(gridcolor="#232936"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run a simulation to populate this chart.")

    with right:
        st.markdown('<div class="section-label">Attack Techniques Distribution</div>', unsafe_allow_html=True)
        tech_counter = Counter()
        for i in incidents:
            for f in dbmod.get_findings(i["sim_id"]):
                if f.get("technique") and f["technique"] != "n/a":
                    tech_counter[f["technique"]] += 1
        if tech_counter:
            fig2 = go.Figure(go.Pie(
                labels=list(tech_counter.keys()),
                values=list(tech_counter.values()),
                hole=0.5,
            ))
            fig2.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", font_color="#c4c9d1",
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No detection findings yet.")

    st.markdown('<div class="section-label">Activity Trend (Events Over Time)</div>', unsafe_allow_html=True)
    all_events = []
    for s in simulations:
        for e in dbmod.get_events(s["sim_id"]):
            all_events.append(e)
    if all_events:
        df = pd.DataFrame(all_events)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour_bucket"] = df["timestamp"].dt.floor("h")
        trend = df.groupby("hour_bucket").size().reset_index(name="events")
        fig3 = go.Figure(go.Scatter(
            x=trend["hour_bucket"], y=trend["events"], mode="lines+markers",
            line=dict(color="#3b82f6"),
        ))
        fig3.update_layout(
            height=240, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c4c9d1", xaxis=dict(gridcolor="#232936"),
            yaxis=dict(gridcolor="#232936", title="Events"),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No simulated events yet. Go to Attack Simulator to generate activity.")

    st.markdown('<div class="section-label">Recent Investigations</div>', unsafe_allow_html=True)
    if incidents:
        rows = []
        for i in incidents[:10]:
            rows.append({
                "Incident ID": i["incident_id"],
                "Scenario": i["scenario"],
                "Severity": i["severity"],
                "Status": i["status"],
                "Time": i["created_at"],
                "Affected User": i.get("affected_user"),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No incidents yet. Launch a controlled attack simulation to begin.")
