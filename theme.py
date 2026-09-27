"""Shared theme: CSS injection + small reusable UI components."""

from __future__ import annotations

import streamlit as st

SEVERITY_COLORS = {
    "CRITICAL": "#e5484d",
    "HIGH": "#f5a524",
    "MEDIUM": "#f5d90a",
    "LOW": "#3ecf8e",
}

STATUS_COLORS = {
    "UNDER INVESTIGATION": "#f5a524",
    "RESOLVED": "#3ecf8e",
    "CLOSED": "#8a8f98",
}


def inject_css():
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: #0d1117;
        }}
        [data-testid="stSidebar"] {{
            background-color: #10141c;
            border-right: 1px solid #1f2530;
        }}
        [data-testid="stSidebar"] * {{
            color: #d6dae0 !important;
        }}
        html, body, [class*="css"] {{
            font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        h1, h2, h3 {{
            color: #e8eaed;
            font-weight: 600;
        }}
        p, li, span, label, div {{
            color: #c4c9d1;
        }}
        .st-card {{
            background: #151a23;
            border: 1px solid #232936;
            border-radius: 10px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }}
        .kpi-value {{
            font-size: 30px;
            font-weight: 700;
            color: #f0f2f5;
            line-height: 1.1;
        }}
        .kpi-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #8a8f98;
            margin-bottom: 6px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: #0d1117;
        }}
        .section-label {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6e7581;
            font-weight: 700;
            margin-top: 6px;
            margin-bottom: 6px;
        }}
        .source-chip {{
            display: inline-block;
            background: #1a2030;
            border: 1px solid #2a3142;
            border-radius: 6px;
            padding: 4px 10px;
            margin: 3px 4px 3px 0;
            font-size: 12px;
            color: #9fb4d1 !important;
        }}
        .evidence-line {{
            font-family: "SF Mono", Menlo, Consolas, monospace;
            font-size: 12px;
            color: #8ea0b8;
            background: #0f141d;
            padding: 8px 10px;
            border-radius: 6px;
            border: 1px solid #1c2330;
            margin-bottom: 4px;
        }}
        .timeline-item {{
            border-left: 2px solid #2a3142;
            padding-left: 16px;
            margin-left: 8px;
            padding-bottom: 18px;
            position: relative;
        }}
        .timeline-item::before {{
            content: "";
            position: absolute;
            left: -6px;
            top: 2px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #3b82f6;
        }}
        .chain-node {{
            background: #151a23;
            border: 1px solid #2a3142;
            border-radius: 8px;
            padding: 10px 16px;
            text-align: center;
            font-size: 13px;
            color: #e8eaed;
        }}
        .chain-arrow {{
            text-align: center;
            color: #4a5568;
            font-size: 18px;
        }}
        div[data-testid="stMetricValue"] {{
            color: #f0f2f5;
        }}
    </style>
    """, unsafe_allow_html=True)


def severity_badge(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, "#8a8f98")
    return f'<span class="badge" style="background:{color}">{severity}</span>'


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#8a8f98")
    return f'<span class="badge" style="background:{color}">{status}</span>'


def card_start():
    st.markdown('<div class="st-card">', unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def kpi(label: str, value):
    st.markdown(f"""
        <div class="st-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)
