# Incident Response Fundamentals

## Overview
Incident response is the structured process of detecting, investigating,
containing, and recovering from a security incident, typically following
phases such as: identification, containment, eradication, recovery, and
lessons learned.

## Investigation Best Practices
- Establish a clear timeline of events before drawing conclusions.
- Separate OBSERVED facts (what the logs show) from INTERPRETATION (what
  the behaviour might mean) — conflating the two leads to overconfident
  or incorrect conclusions.
- Corroborate automated findings with additional context (asset owner,
  business process, prior history) before escalating.
- Document evidence and reasoning as you go so severity and response
  decisions are defensible after the fact.

## Common Pitfalls
- Treating every anomaly as a confirmed compromise.
- Taking irreversible response actions before containment/verification.
- Failing to check whether similar behaviour has a benign explanation
  elsewhere in the organization.

## Recommended Response Structure
1. Confirm what happened using evidence.
2. Assess severity based on the evidence, not assumption.
3. Contain if there is credible risk of ongoing harm.
4. Investigate root cause and scope.
5. Remediate and document lessons learned.
