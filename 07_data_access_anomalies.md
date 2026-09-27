# Data Access Anomalies

## Overview
A data access anomaly is a session or user whose resource access volume,
pattern, or scope differs significantly from an established baseline of
normal behaviour, even if no single access event looks malicious.

## Key Indicators
- Total resource accesses per session well above the typical range for
  that role (commonly on the order of 5-12 for a normal working session
  in many environments).
- Access spanning an unusually broad set of distinct resources within a
  single session.
- Statistical outlier detection (e.g., isolation-based models) flagging
  the session as distant from the bulk of normal sessions across several
  features simultaneously.

## Why It Matters
Volume-based anomalies matter because an attacker or malicious insider
who already has valid access will often be indistinguishable from a
normal user at the level of any single access event — the anomaly only
becomes visible in aggregate.

## Recommended Response
- Review the specific list of resources accessed for sensitivity and
  relevance to the user's role.
- Cross-reference with authentication anomalies (new source, unusual
  time) for corroborating evidence.
- Treat volume anomalies as an investigative trigger, not a confirmed
  verdict — legitimate bulk work (e.g., audits, migrations) can also
  produce high volume.
