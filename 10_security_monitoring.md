# Security Monitoring Practices

## Overview
Security monitoring is the continuous collection and analysis of
telemetry (authentication logs, access logs, network logs, endpoint
events) to detect indicators of compromise or policy violation.

## Detection Approaches
- **Rule-based / deterministic detection**: explicit conditions (e.g.,
  "N failed logins followed by success") that are easy to explain and
  audit, but only catch patterns that were anticipated in advance.
- **Statistical / ML-based anomaly detection**: models a baseline of
  normal behaviour and flags sessions or entities that deviate
  significantly, catching patterns that were not explicitly anticipated,
  at the cost of being harder to explain and potentially noisier.
- Combining both approaches gives broader coverage: rules catch known
  patterns reliably, anomaly detection catches the unknown/emerging ones.

## Why Context Matters
A finding in isolation (e.g., "large file transfer") is far less useful
than the same finding placed in the context of the full session (what
preceded it, what account, what resource). Effective monitoring
correlates events into a session or incident view rather than alerting
on isolated events.

## Recommended Practices
- Maintain baselines per role/user where feasible rather than one global
  baseline.
- Tune detection thresholds against real (or realistic synthetic) data
  rather than guessing.
- Review false positives regularly to keep analyst trust in the system.
