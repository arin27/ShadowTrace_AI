"""
Scenario definitions for ShadowTrace AI.

Every scenario is a deterministic *stage chain* (the attack chain shown in
the UI) plus generation parameters that the event_generator uses to produce
randomized-but-plausible synthetic events. Nothing here touches real systems:
all users, IPs, and resources are synthetic or drawn from documentation
ranges (RFC 5737 TEST-NET blocks for IPv4).

Each stage has:
- key: stable identifier used by the detection engine to reason about order
- label: human-readable name shown in the timeline / attack chain
- event_type: category used for charts
- technique: an ATT&CK-style label (illustrative, not a real live mapping)
"""

from __future__ import annotations

SCENARIOS = {
    "credential_abuse": {
        "name": "Credential Abuse",
        "description": (
            "A sequence of failed authentication attempts followed by a "
            "successful login from an unusual source, escalating to a "
            "privilege request and access to a sensitive resource."
        ),
        "stages": [
            {"key": "failed_login", "label": "Multiple Failed Logins",
             "event_type": "authentication", "technique": "Brute Force (simulated)"},
            {"key": "success_login", "label": "Successful Authentication",
             "event_type": "authentication", "technique": "Valid Accounts (simulated)"},
            {"key": "unusual_source", "label": "Unusual Source",
             "event_type": "authentication", "technique": "Valid Accounts (simulated)"},
            {"key": "new_resource", "label": "Previously Unused Resource Accessed",
             "event_type": "access", "technique": "Discovery (simulated)"},
            {"key": "priv_request", "label": "Privilege Request",
             "event_type": "privilege", "technique": "Privilege Escalation (simulated)"},
            {"key": "sensitive_access", "label": "Sensitive Resource Accessed",
             "event_type": "access", "technique": "Collection (simulated)"},
        ],
    },
    "malicious_file": {
        "name": "Malicious File",
        "description": (
            "A user receives and opens a suspicious attachment, a suspicious "
            "process event follows, an unexpected outbound connection is "
            "observed, and a persistence attempt is logged."
        ),
        "stages": [
            {"key": "attachment_received", "label": "Suspicious Attachment Received",
             "event_type": "email", "technique": "Phishing (simulated)"},
            {"key": "attachment_opened", "label": "User Opens Attachment",
             "event_type": "endpoint", "technique": "User Execution (simulated)"},
            {"key": "process_event", "label": "Suspicious Process Event",
             "event_type": "process", "technique": "Execution (simulated)"},
            {"key": "outbound_conn", "label": "Unexpected Outbound Connection",
             "event_type": "network", "technique": "Command & Control (simulated)"},
            {"key": "persistence", "label": "Persistence Attempt",
             "event_type": "endpoint", "technique": "Persistence (simulated)"},
        ],
    },
    "web_abuse": {
        "name": "Web Application Abuse",
        "description": (
            "Repeated malformed requests against a web application trigger "
            "application errors, followed by an unauthorized resource "
            "attempt and continued suspicious request activity."
        ),
        "stages": [
            {"key": "suspicious_request", "label": "Suspicious Request",
             "event_type": "web", "technique": "Exploit Public-Facing App (simulated)"},
            {"key": "malformed_input", "label": "Repeated Malformed Input",
             "event_type": "web", "technique": "Exploit Public-Facing App (simulated)"},
            {"key": "app_error", "label": "Application Error",
             "event_type": "web", "technique": "Defense Evasion (simulated)"},
            {"key": "unauthorized_attempt", "label": "Unauthorized Resource Attempt",
             "event_type": "web", "technique": "Privilege Escalation (simulated)"},
            {"key": "repeated_suspicious", "label": "Repeated Suspicious Requests",
             "event_type": "web", "technique": "Discovery (simulated)"},
        ],
    },
    "insider_threat": {
        "name": "Insider Threat",
        "description": (
            "A normal employee session drifts into unusual-hour access, an "
            "abnormally large number of documents are opened, a sensitive "
            "resource is reached, and a large data transfer follows."
        ),
        "stages": [
            {"key": "normal_activity", "label": "Normal Employee Activity",
             "event_type": "access", "technique": "n/a"},
            {"key": "unusual_time", "label": "Unusual Access Time",
             "event_type": "access", "technique": "Valid Accounts (simulated)"},
            {"key": "bulk_access", "label": "Large Number of Documents Accessed",
             "event_type": "access", "technique": "Collection (simulated)"},
            {"key": "sensitive_access", "label": "Sensitive Resource Access",
             "event_type": "access", "technique": "Collection (simulated)"},
            {"key": "large_transfer", "label": "Large Transfer",
             "event_type": "exfiltration", "technique": "Exfiltration (simulated)"},
        ],
    },
}

# Next-stage behaviour shown as "Potential Next-Stage Behaviour" — clearly
# labeled in the UI as not-confirmed. This is scenario logic, not generated
# attack instructions.
NEXT_STAGE_BEHAVIOUR = {
    "credential_abuse": [
        "Additional account access attempts using the same source",
        "Privileged resource access attempt",
        "Access to additional sensitive data stores",
        "Attempt to establish a persistent session or token",
    ],
    "malicious_file": [
        "Additional outbound connections to new destinations",
        "Lateral movement toward adjacent endpoints",
        "Attempt to access credential stores on the endpoint",
        "Further persistence mechanisms",
    ],
    "web_abuse": [
        "Continued probing of additional application endpoints",
        "Attempt to access administrative functionality",
        "Attempt to enumerate additional resources or accounts",
        "Escalation to data access attempts if probing succeeds",
    ],
    "insider_threat": [
        "Continued bulk access to additional repositories",
        "Attempt to move data to external or personal storage",
        "Access outside of normal working pattern continues",
        "Attempt to access resources outside assigned role",
    ],
}

SYNTHETIC_USERS = [f"employee_{n}" for n in (101, 104, 110, 118, 123, 130, 142, 157)]

SYNTHETIC_RESOURCES = {
    "credential_abuse": ["internal_portal", "employee_documents", "hr_records", "finance_reports"],
    "malicious_file": ["endpoint_workstation_12", "shared_drive", "mail_gateway"],
    "web_abuse": ["/app/login", "/app/search", "/app/admin", "/app/api/v1/orders"],
    "insider_threat": ["document_repository", "customer_database", "finance_reports", "hr_records"],
}

# Documentation/example ranges only (RFC 5737): 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24
SYNTHETIC_IP_POOL = {
    "known": ["192.0.2.10", "192.0.2.11", "192.0.2.12", "192.0.2.15"],
    "unusual": ["198.51.100.23", "198.51.100.77", "203.0.113.44", "203.0.113.91"],
}
