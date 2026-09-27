# Defensive Controls

## Overview
Defensive controls are the mechanisms an organization puts in place to
prevent, detect, or limit the impact of adversarial behaviour. They span
authentication, authorization, network, and monitoring domains.

## Authentication Controls
- Multi-factor authentication reduces the impact of credential-only
  compromise significantly, since a stolen or guessed password alone is
  no longer sufficient.
- Rate limiting and lockout policies reduce the effectiveness of brute
  force and password spraying attempts.
- Alerting on authentication from new sources/geographies for a given
  account adds a detection layer beyond prevention.

## Access Controls
- Least-privilege access limits what an account can reach even if
  compromised.
- Change-managed privilege escalation (approval workflows) makes
  unauthorized escalation attempts stand out.
- Segmentation of sensitive resources limits blast radius.

## Monitoring & Response Controls
- Centralized logging with retention sufficient for investigation.
- Defined severity criteria so response is consistent and evidence
  based rather than ad hoc.
- Tested incident response playbooks per scenario type (credential
  abuse, malware, insider, web abuse).

## Continuous Improvement
- Review incidents after the fact to identify which controls would have
  prevented or shortened the incident, and prioritize those improvements.
