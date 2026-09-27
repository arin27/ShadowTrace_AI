"""
Severity calculation.

Severity is derived ENTIRELY from what fired: the sum of finding severity
points, plus a bonus if the anomaly detector flagged the session. Bands are
simple and documented so they can be defended in an interview. This is
intentionally simple and auditable rather than a black box.
"""

from __future__ import annotations

BANDS = [
    (70, "CRITICAL"),
    (45, "HIGH"),
    (20, "MEDIUM"),
    (0, "LOW"),
]


def calculate_severity(findings: list[dict], anomaly: dict) -> dict:
    """Return {severity, score, reasoning: [str,...]}"""
    score = sum(f["severity_points"] for f in findings)
    reasoning = [f"{f['rule_name']} (+{f['severity_points']})" for f in findings]

    if anomaly.get("is_anomaly"):
        bonus = int(15 * anomaly.get("anomaly_score", 0.5)) + 10
        score += bonus
        reasoning.append(
            f"Statistical anomaly detected relative to baseline session "
            f"behaviour (+{bonus})"
        )

    severity = "LOW"
    for threshold, label in BANDS:
        if score >= threshold:
            severity = label
            break

    if not findings and not anomaly.get("is_anomaly"):
        reasoning = ["No detection rules fired and no statistical anomaly was found."]

    return {
        "severity": severity,
        "score": score,
        "reasoning": reasoning,
    }
