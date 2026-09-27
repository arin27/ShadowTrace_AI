# Data Exfiltration Concepts

## Overview
Exfiltration refers to the unauthorized transfer of data out of an
organization's environment. It is typically the final stage of an
incident chain that began with access (credential abuse, insider access,
or malware) and escalated to bulk collection.

## Key Indicators
- A large data transfer (by volume) to an external or unfamiliar
  destination, especially shortly after bulk access to sensitive
  resources.
- Transfer timing that clusters with other suspicious activity in the
  same session rather than being spread evenly over normal work hours.
- Destination endpoints that are not part of the organization's known
  and approved data-sharing services.

## Why It Matters
Exfiltration is frequently the stage at which an incident causes concrete
harm (a data breach), so detecting the precursor pattern (bulk access
followed by transfer) before or immediately as it happens is high value.

## Recommended Response
- Identify exactly what data was included in the transfer.
- Determine the destination and whether it is a known, approved service.
- Contain the transfer path (revoke access, block destination) if still
  in progress.
- Follow data breach notification and legal processes if the transfer is
  confirmed unauthorized.
