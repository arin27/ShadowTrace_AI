# Insider Threat Indicators

## Overview
Insider threat activity is performed by someone with legitimate access
(an employee or contractor) but who uses that access in a way that is
harmful or against policy. Because the access itself is authorized,
detection relies heavily on behavioural baselining rather than
signature-based detection.

## Key Indicators
- Access occurring at times significantly outside the individual's
  normal working pattern.
- A sharp increase in the volume of documents or records accessed
  compared to the individual's typical session.
- Access to sensitive resources not required for the person's normal
  role or current task.
- A large data transfer or export following broad access to sensitive
  repositories.

## Why It Matters
Insider activity is often "low and slow" or disguised as normal work.
The combination of unusual timing, unusual volume, and a subsequent
transfer is a much stronger signal than any single factor, and is the
pattern most consistently associated with data exfiltration by an
authorized user.

## Recommended Response
- Correlate with HR/business context where appropriate (e.g., role
  change, departure) through proper process, not through inference alone.
- Review exactly which resources were accessed and whether they relate
  to the person's job function.
- Review destination of any data transfer for legitimacy.
- Escalate to management and legal/HR per organizational policy before
  taking action against an individual.
