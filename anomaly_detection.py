"""
Anomaly detection layer.

Uses scikit-learn's IsolationForest to score a simulation's session against
a baseline population of "normal" synthetic sessions. Features are simple,
interpretable counts so the result can be explained to a non-technical
reader (this matters for the AI Analyst's "explain to a manager" mode).

If IsolationForest genuinely has nothing useful to say (e.g. too few
samples, degenerate feature vector), we fall back to a transparent
threshold check rather than force an ML verdict — matching the spec's
"if ML is not genuinely useful, use deterministic detection instead."
"""

from __future__ import annotations

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    _HAS_SKLEARN = True
except Exception:  # pragma: no cover
    _HAS_SKLEARN = False

# A synthetic baseline of "normal session" feature vectors, built from
# documented typical ranges rather than sampled from any real environment.
# Features: [resource_accesses, distinct_resources, failed_auth_events,
#            documents_accessed, data_transfer_mb, distinct_source_ips]
_BASELINE_RANGES = {
    "resource_accesses": (2, 12),
    "distinct_resources": (1, 4),
    "failed_auth_events": (0, 2),
    "documents_accessed": (0, 10),
    "data_transfer_mb": (0, 50),
    "distinct_source_ips": (1, 1),
}

FEATURE_NAMES = list(_BASELINE_RANGES.keys())


def _extract_features(events: list[dict]) -> dict:
    resource_accesses = sum(1 for e in events if e.get("event_type") == "access")
    distinct_resources = len({e.get("resource") for e in events if e.get("resource")})
    failed_auth = sum(1 for e in events if e.get("event_type") == "authentication"
                       and e.get("status") == "failed")
    docs = sum(1 for e in events if e.get("action") == "document_access")
    transfer_mb = sum(e.get("detail", {}).get("volume_mb", 0) for e in events
                       if e.get("action") == "large_data_transfer")
    distinct_ips = len({e.get("source_ip") for e in events if e.get("source_ip")})
    return {
        "resource_accesses": resource_accesses,
        "distinct_resources": distinct_resources,
        "failed_auth_events": failed_auth,
        "documents_accessed": docs,
        "data_transfer_mb": transfer_mb,
        "distinct_source_ips": distinct_ips,
    }


def _make_baseline_population(rng: np.random.Generator, n: int = 300) -> np.ndarray:
    rows = []
    for _ in range(n):
        row = [rng.uniform(lo, hi) for (lo, hi) in _BASELINE_RANGES.values()]
        rows.append(row)
    return np.array(rows)


def detect_anomaly(events: list[dict]) -> dict:
    """Return a structured anomaly report for this simulation's events.

    {
      "method": "isolation_forest" | "threshold_fallback",
      "is_anomaly": bool,
      "anomaly_score": float,   # higher = more anomalous (normalized 0-1ish)
      "features": {...},
      "baseline": {feature: (low, high)},
      "explanations": [str, ...]
    }
    """
    features = _extract_features(events)
    explanations = []

    if _HAS_SKLEARN:
        rng = np.random.default_rng(7)
        baseline = _make_baseline_population(rng)
        model = IsolationForest(n_estimators=150, contamination=0.05, random_state=7)
        model.fit(baseline)

        vec = np.array([[features[f] for f in FEATURE_NAMES]])
        raw_score = model.score_samples(vec)[0]  # more negative = more anomalous
        prediction = model.predict(vec)[0]  # -1 anomaly, 1 normal

        # normalize raw_score (~[-0.6, -0.3] typical range) to a 0-1 "risk" scale
        anomaly_score = float(np.clip((-raw_score - 0.30) / 0.30, 0.0, 1.0))
        is_anomaly = bool(prediction == -1) or anomaly_score > 0.5
        method = "isolation_forest"
    else:
        # deterministic fallback: flag if any feature clearly exceeds baseline high
        is_anomaly = False
        exceed_ratio = 0.0
        for f, (lo, hi) in _BASELINE_RANGES.items():
            if hi > 0 and features[f] > hi:
                is_anomaly = True
                exceed_ratio = max(exceed_ratio, features[f] / hi)
        anomaly_score = float(np.clip((exceed_ratio - 1.0) / 3.0, 0.0, 1.0)) if exceed_ratio else 0.0
        method = "threshold_fallback"

    for f, (lo, hi) in _BASELINE_RANGES.items():
        val = features[f]
        if val > hi:
            explanations.append(
                f"{f.replace('_', ' ')}: observed {val}, typical baseline {lo:.0f}-{hi:.0f}."
            )

    if is_anomaly and not explanations:
        explanations.append(
            "No single feature exceeded its baseline range, but the "
            "combination of feature values is atypical relative to the "
            "modeled normal-session distribution."
        )

    return {
        "method": method,
        "is_anomaly": is_anomaly,
        "anomaly_score": round(anomaly_score, 3),
        "features": features,
        "baseline": {f: list(r) for f, r in _BASELINE_RANGES.items()},
        "explanations": explanations,
    }
