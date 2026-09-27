"""
Event generator — turns a scenario definition into a concrete sequence of
structured synthetic events with randomized variation (counts, timing
jitter, source selection) so repeated simulations of the same scenario
don't look identical.

This module NEVER performs any real network, filesystem, or auth action.
It only produces dict/JSON records describing a fictional sequence of
events, stored in SQLite for the detection engine to analyze.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone

from simulation.scenarios import (
    SCENARIOS, SYNTHETIC_USERS, SYNTHETIC_RESOURCES, SYNTHETIC_IP_POOL,
)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def generate_simulation(scenario_key: str, seed: int | None = None) -> dict:
    """Generate a full simulation: metadata + ordered event list.

    Returns a dict: {sim_id, scenario, started_at, ended_at, affected_user,
    affected_resources, events: [...]}
    """
    if scenario_key not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_key}")

    rng = random.Random(seed)
    scenario = SCENARIOS[scenario_key]
    user = rng.choice(SYNTHETIC_USERS)
    resources_pool = SYNTHETIC_RESOURCES[scenario_key]
    known_ip = rng.choice(SYNTHETIC_IP_POOL["known"])
    unusual_ip = rng.choice(SYNTHETIC_IP_POOL["unusual"])

    sim_id = _new_id("SIM")
    t = datetime.now(timezone.utc) - timedelta(minutes=rng.randint(5, 90))
    events: list[dict] = []
    seq = 0
    affected_resources: set[str] = set()

    def add_event(event_type, action, status, resource=None, source_ip=None,
                   detail=None, jitter=(20, 90)):
        nonlocal t, seq
        t = t + timedelta(seconds=rng.randint(*jitter))
        seq += 1
        ev = {
            "event_id": _new_id("EVT"),
            "seq": seq,
            "timestamp": _iso(t),
            "event_type": event_type,
            "user": user,
            "source_ip": source_ip or known_ip,
            "resource": resource,
            "action": action,
            "status": status,
            "detail": detail or {},
        }
        if resource:
            affected_resources.add(resource)
        events.append(ev)
        return ev

    if scenario_key == "credential_abuse":
        n_failed = rng.randint(5, 9)
        for i in range(n_failed):
            add_event("authentication", "login_failed", "failed",
                       resource="internal_portal", source_ip=known_ip,
                       detail={"attempt": i + 1, "reason": "invalid_credentials"},
                       jitter=(15, 45))
        add_event("authentication", "login_success", "success",
                   resource="internal_portal", source_ip=unusual_ip,
                   detail={"note": "authenticated after repeated failures"})
        add_event("authentication", "session_source_flagged", "flagged",
                   resource="internal_portal", source_ip=unusual_ip,
                   detail={"reason": "source_ip_not_previously_seen_for_user"})
        new_resource = rng.choice(resources_pool)
        add_event("access", "resource_access", "success",
                   resource=new_resource, source_ip=unusual_ip,
                   detail={"first_time_access": True})
        add_event("privilege", "privilege_request", "requested",
                   resource=new_resource, source_ip=unusual_ip,
                   detail={"requested_level": "elevated"})
        sensitive = "hr_records" if "hr_records" in resources_pool else rng.choice(resources_pool)
        add_event("access", "resource_access", "success",
                   resource=sensitive, source_ip=unusual_ip,
                   detail={"classification": "sensitive"})

    elif scenario_key == "malicious_file":
        add_event("email", "attachment_received", "delivered",
                   resource="mail_gateway", detail={"attachment": "invoice_2024.docm"})
        add_event("endpoint", "attachment_opened", "executed",
                   resource="endpoint_workstation_12",
                   detail={"attachment": "invoice_2024.docm"})
        add_event("process", "child_process_spawned", "observed",
                   resource="endpoint_workstation_12",
                   detail={"parent": "winword.exe", "child": "script_host.exe (simulated)"})
        add_event("network", "outbound_connection", "observed",
                   resource="endpoint_workstation_12", source_ip=unusual_ip,
                   detail={"destination": unusual_ip, "port": 443,
                           "note": "destination not in known-good list"})
        add_event("endpoint", "persistence_artifact_created", "observed",
                   resource="endpoint_workstation_12",
                   detail={"mechanism": "scheduled_task (simulated)"})

    elif scenario_key == "web_abuse":
        add_event("web", "http_request", "suspicious",
                   resource="/app/login", source_ip=unusual_ip,
                   detail={"payload_flag": "unusual_characters"})
        n_malformed = rng.randint(6, 14)
        for i in range(n_malformed):
            add_event("web", "http_request", "malformed",
                       resource=rng.choice(resources_pool), source_ip=unusual_ip,
                       detail={"attempt": i + 1, "payload_flag": "malformed_input"},
                       jitter=(5, 20))
        add_event("web", "application_error", "error",
                   resource="/app/search", source_ip=unusual_ip,
                   detail={"error_code": 500})
        add_event("web", "resource_access_attempt", "denied",
                   resource="/app/admin", source_ip=unusual_ip,
                   detail={"reason": "insufficient_privilege"})
        n_more = rng.randint(4, 9)
        for i in range(n_more):
            add_event("web", "http_request", "suspicious",
                       resource=rng.choice(resources_pool), source_ip=unusual_ip,
                       detail={"attempt": i + 1}, jitter=(5, 15))

    elif scenario_key == "insider_threat":
        for _ in range(rng.randint(3, 5)):
            add_event("access", "resource_access", "success",
                       resource=rng.choice(resources_pool), source_ip=known_ip,
                       detail={"pattern": "normal"}, jitter=(300, 900))
        # push timestamp into unusual hours for the remaining events
        t = t.replace(hour=rng.choice([1, 2, 3, 23]))
        add_event("access", "resource_access", "success",
                  resource=rng.choice(resources_pool), source_ip=known_ip,
                  detail={"pattern": "unusual_hour"})
        n_docs = rng.randint(35, 60)
        for i in range(n_docs):
            add_event("access", "document_access", "success",
                       resource="document_repository", source_ip=known_ip,
                       detail={"doc_index": i + 1}, jitter=(2, 8))
        add_event("access", "resource_access", "success",
                   resource="hr_records" if "hr_records" in resources_pool else resources_pool[0],
                   source_ip=known_ip, detail={"classification": "sensitive"})
        add_event("exfiltration", "large_data_transfer", "observed",
                   resource="customer_database" if "customer_database" in resources_pool else resources_pool[-1],
                   source_ip=known_ip,
                   detail={"volume_mb": rng.randint(800, 3000), "destination": "external_storage (simulated)"})

    return {
        "sim_id": sim_id,
        "scenario": scenario_key,
        "scenario_name": scenario["name"],
        "started_at": events[0]["timestamp"],
        "ended_at": _iso(datetime.fromisoformat(events[-1]["timestamp"])),
        "affected_user": user,
        "affected_resources": sorted(affected_resources),
        "status": "completed",
        "events": events,
    }
