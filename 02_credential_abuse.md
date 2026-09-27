# Credential Abuse and Valid Accounts

## Overview
"Valid Accounts" abuse (as categorized in adversary behaviour frameworks)
occurs when an attacker uses legitimate, working credentials rather than
exploiting a software vulnerability. Because the credentials are valid,
this activity can blend in with normal usage and is often only visible
through behavioural anomalies rather than a single alarming event.

## Key Indicators
- Use of an account outside its normal access pattern (new resource,
  new time of day, new source).
- A privilege escalation or role-elevation request shortly after the
  account authenticates from an unusual source.
- Access to resources the account has never previously touched.

## Distinguishing From Legitimate Use
Not every unusual login is malicious — travel, new devices, or role
changes can explain some of these signals. The distinguishing factor is
typically a *combination* of signals (new source + new resource +
privilege request) rather than any single one in isolation.

## Recommended Response
- Correlate the account's authentication history over a longer baseline
  window, not just the current session.
- Confirm with the account owner (out of band) whether the session was
  legitimate.
- Review what the account did after authenticating, focusing on
  privilege changes and sensitive resource access.
