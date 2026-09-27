# Privilege Escalation

## Overview
Privilege escalation refers to obtaining a higher level of access than
originally granted. This can happen through legitimate-looking requests
(e.g., asking for elevated role membership) or, in more severe cases,
through exploiting a flaw in access control logic.

## Key Indicators
- A privilege or role-elevation request that follows shortly after
  first-time access to an unfamiliar resource.
- Escalation requests outside of a documented change-management or
  approval process.
- Elevated access being used to reach sensitive resources shortly after
  being granted.

## Why It Matters
Privilege escalation is frequently a *pivot point* in an incident: it
converts limited initial access into broader capability. An escalation
request that is unapproved or unusual in timing should be treated as a
high-priority signal, especially when paired with other suspicious
behaviour in the same session.

## Recommended Response
- Verify the escalation request against approved change-management
  records.
- Review what the elevated privilege was subsequently used for.
- Temporarily constrain or review the granted privilege if the request
  cannot be verified as legitimate.
