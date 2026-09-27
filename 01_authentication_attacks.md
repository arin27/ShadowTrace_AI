# Authentication Attacks

## Overview
Authentication attacks target the process by which a user or system proves
identity. The most common pattern is repeated credential guessing (brute
force or password spraying) against a login endpoint, aiming for one
successful authentication among many failures.

## Key Indicators
- A burst of failed login attempts against the same account in a short
  window (typically under a few minutes).
- A successful authentication immediately following a run of failures.
- Authentication succeeding from a source (IP address, device, or
  geography) not previously associated with the account.
- Login attempts distributed across many accounts from a single source
  (password spraying) rather than many attempts against one account
  (brute force).

## Why It Matters
A successful login after repeated failures suggests the correct credential
was eventually found or guessed, rather than a legitimate user mistyping a
password. Combined with a new source IP, this is a strong signal that the
authenticating party may not be the legitimate account owner.

## Recommended Response
- Verify the account owner actually initiated the successful session.
- Check whether the source IP/geography is consistent with the user's
  normal work pattern.
- Consider forcing a credential reset and re-authentication with a second
  factor if available.
- Review any actions taken during the suspicious session before drawing
  conclusions about intent.
