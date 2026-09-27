# Web Application Abuse

## Overview
Web application abuse covers attempts to manipulate a web application
through malformed, malicious, or unexpected input, or by attempting to
reach functionality or resources the requester is not authorized to use.

## Key Indicators
- Repeated requests containing malformed or unusual input patterns
  against the same or related endpoints.
- Application errors correlated in time with malformed input, suggesting
  the input is triggering unexpected code paths.
- Requests to administrative or privileged endpoints from a session that
  has not authenticated with sufficient privilege.
- A high rate of requests from a single source in a short window.

## Why It Matters
Repeated malformed input followed by application errors often indicates
probing behaviour — the requester is testing how the application responds
to different payloads, which is a precursor to attempting exploitation of
an actual weakness if one exists.

## Recommended Response
- Rate-limit or block the offending source pending review.
- Review application logs and error details for any sign that unintended
  code paths were reached.
- Confirm authorization checks correctly blocked the unauthorized
  resource attempt.
- Patch or harden any input validation gaps discovered during review.
