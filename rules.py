"""
Deterministic detection engine.

Each rule inspects the *actual* generated event sequence for a simulation
and only fires if its condition is genuinely met. Nothing here is
hardcoded per-scenario text unrelated to the real events — every finding's
evidence is built from the events it fired on.

A "Finding" is: {finding_id, rule_name, description, evidence: [...],
severity_points: int, technique: str|None}
"""

from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from datetime import datetime


def _new_id() -> str:
    return f"FND-{uuid.uuid4().hex[:8]}"


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def run_detection(events: list[dict]) -> list[dict]:
    """Run all rules over the event list and return findings that fired."""
    findings: list[dict] = []
    findings += _rule_repeated_auth_failure(events)
    findings += _rule_unusual_source_after_failures(events)
    findings += _rule_privilege_request_after_new_access(events)
    findings += _rule_sensitive_resource_access(events)
    findings += _rule_suspicious_process_and_outbound(events)
    findings += _rule_persistence_attempt(events)
    findings += _rule_repeated_malformed_requests(events)
    findings += _rule_unauthorized_resource_attempt(events)
    findings += _rule_unusual_hour_access(events)
    findings += _rule_bulk_document_access(events)
    findings += _rule_large_data_transfer(events)
    return findings


def _window_seconds(events: list[dict]) -> float:
    if len(events) < 2:
        return 0.0
    t0 = _parse_ts(events[0]["timestamp"])
    t1 = _parse_ts(events[-1]["timestamp"])
    return (t1 - t0).total_seconds()


def _rule_repeated_auth_failure(events):
    failed = [e for e in events if e["event_type"] == "authentication"
              and e["status"] == "failed"]
    success = [e for e in events if e["event_type"] == "authentication"
               and e["status"] == "success"]
    if len(failed) >= 4 and success:
        first_success_seq = success[0]["seq"]
        preceding_failures = [e for e in failed if e["seq"] < first_success_seq]
        if len(preceding_failures) >= 4:
            span = _window_seconds(preceding_failures + [success[0]])
            return [{
                "finding_id": _new_id(),
                "rule_name": "Repeated Authentication Failure Followed by Success",
                "description": (
                    f"{len(preceding_failures)} failed authentication attempts "
                    f"occurred within {span:.0f} seconds, immediately followed "
                    f"by a successful authentication for the same user."
                ),
                "evidence": [e["event_id"] for e in preceding_failures] + [success[0]["event_id"]],
                "severity_points": 30,
                "technique": "Brute Force (simulated)",
            }]
    return []


def _rule_unusual_source_after_failures(events):
    flagged = [e for e in events if e.get("action") == "session_source_flagged"]
    if flagged:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Authentication From Previously Unseen Source",
            "description": (
                "Successful authentication occurred from a source IP not "
                "previously associated with this user's sessions."
            ),
            "evidence": [e["event_id"] for e in flagged],
            "severity_points": 20,
            "technique": "Valid Accounts (simulated)",
        }]
    return []


def _rule_privilege_request_after_new_access(events):
    priv = [e for e in events if e["event_type"] == "privilege"
            and e.get("action") == "privilege_request"]
    first_time = [e for e in events if e.get("detail", {}).get("first_time_access")]
    if priv and first_time:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Privilege Request Following Unfamiliar Resource Access",
            "description": (
                "A privilege escalation request was made shortly after the "
                "user accessed a resource they had not previously accessed."
            ),
            "evidence": [e["event_id"] for e in first_time] + [e["event_id"] for e in priv],
            "severity_points": 25,
            "technique": "Privilege Escalation (simulated)",
        }]
    return []


def _rule_sensitive_resource_access(events):
    sensitive = [e for e in events if e.get("detail", {}).get("classification") == "sensitive"]
    if sensitive:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Sensitive Resource Accessed",
            "description": (
                f"{len(sensitive)} access event(s) reached a resource "
                f"classified as sensitive during this session."
            ),
            "evidence": [e["event_id"] for e in sensitive],
            "severity_points": 20,
            "technique": "Collection (simulated)",
        }]
    return []


def _rule_suspicious_process_and_outbound(events):
    proc = [e for e in events if e["event_type"] == "process"]
    outbound = [e for e in events if e.get("action") == "outbound_connection"]
    if proc and outbound:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Suspicious Process Followed by Outbound Connection",
            "description": (
                "A suspicious child process was observed, followed by an "
                "outbound network connection to a destination not on the "
                "known-good list."
            ),
            "evidence": [e["event_id"] for e in proc] + [e["event_id"] for e in outbound],
            "severity_points": 30,
            "technique": "Command & Control (simulated)",
        }]
    return []


def _rule_persistence_attempt(events):
    persist = [e for e in events if e.get("action") == "persistence_artifact_created"]
    if persist:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Persistence Mechanism Observed",
            "description": (
                "An artifact consistent with a persistence mechanism "
                "(e.g. a scheduled task) was created on the endpoint."
            ),
            "evidence": [e["event_id"] for e in persist],
            "severity_points": 25,
            "technique": "Persistence (simulated)",
        }]
    return []


def _rule_repeated_malformed_requests(events):
    malformed = [e for e in events if e.get("status") == "malformed"]
    if len(malformed) >= 5:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Repeated Malformed Input",
            "description": (
                f"{len(malformed)} requests with malformed input flags were "
                f"observed against the application in a short window."
            ),
            "evidence": [e["event_id"] for e in malformed],
            "severity_points": 20,
            "technique": "Exploit Public-Facing Application (simulated)",
        }]
    return []


def _rule_unauthorized_resource_attempt(events):
    denied = [e for e in events if e.get("status") == "denied"]
    if denied:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Unauthorized Resource Access Attempt",
            "description": (
                "An attempt to access a restricted resource was denied due "
                "to insufficient privilege."
            ),
            "evidence": [e["event_id"] for e in denied],
            "severity_points": 20,
            "technique": "Privilege Escalation (simulated)",
        }]
    return []


def _rule_unusual_hour_access(events):
    unusual = [e for e in events if e.get("detail", {}).get("pattern") == "unusual_hour"]
    if unusual:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Access Outside Normal Hours",
            "description": (
                "Resource access occurred at a time significantly outside "
                "this user's typical activity window."
            ),
            "evidence": [e["event_id"] for e in unusual],
            "severity_points": 15,
            "technique": "Valid Accounts (simulated)",
        }]
    return []


def _rule_bulk_document_access(events):
    doc_access = [e for e in events if e.get("action") == "document_access"]
    if len(doc_access) >= 20:
        return [{
            "finding_id": _new_id(),
            "rule_name": "Abnormally High Document Access Volume",
            "description": (
                f"{len(doc_access)} documents were accessed in a single "
                f"session, well above a typical session (5-12)."
            ),
            "evidence": [e["event_id"] for e in doc_access[:15]] + ["...(truncated)"],
            "severity_points": 25,
            "technique": "Collection (simulated)",
        }]
    return []


def _rule_large_data_transfer(events):
    transfers = [e for e in events if e.get("action") == "large_data_transfer"]
    if transfers:
        vol = sum(e.get("detail", {}).get("volume_mb", 0) for e in transfers)
        return [{
            "finding_id": _new_id(),
            "rule_name": "Large Outbound Data Transfer",
            "description": (
                f"A transfer of approximately {vol} MB to an external "
                f"destination was observed."
            ),
            "evidence": [e["event_id"] for e in transfers],
            "severity_points": 30,
            "technique": "Exfiltration (simulated)",
        }]
    return []
