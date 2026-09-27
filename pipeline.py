"""
Orchestration pipeline: SIMULATE -> DETECT -> incident creation.

This is the single function the UI calls when the analyst clicks
"Run Simulation". It generates events, runs the deterministic detection
engine and anomaly detector, computes severity, and persists a
simulation + its events + findings + a new incident record.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from database import db as dbmod
from detection.anomaly_detection import detect_anomaly
from detection.rules import run_detection
from detection.severity import calculate_severity
from simulation.event_generator import generate_simulation
from simulation.scenarios import SCENARIOS


def run_simulation_pipeline(scenario_key: str, seed: int | None = None) -> str:
    """Runs the full pipeline and returns the new incident_id."""
    sim = generate_simulation(scenario_key, seed=seed)
    dbmod.insert_simulation(sim)
    dbmod.insert_events(sim["sim_id"], sim["events"])

    findings = run_detection(sim["events"])
    if findings:
        dbmod.insert_findings(sim["sim_id"], findings)

    anomaly = detect_anomaly(sim["events"])
    severity = calculate_severity(findings, anomaly)

    existing_count = len(dbmod.list_incidents())
    incident_id = f"ST-{1042 + existing_count}"
    incident = {
        "incident_id": incident_id,
        "sim_id": sim["sim_id"],
        "scenario": SCENARIOS[scenario_key]["name"],
        "severity": severity["severity"],
        "severity_score": severity["score"],
        "severity_reasoning": severity["reasoning"],
        "status": "UNDER INVESTIGATION",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "affected_user": sim["affected_user"],
        "affected_resources": sim["affected_resources"],
        "anomaly_summary": anomaly,
    }
    dbmod.insert_incident(incident)
    return incident_id
