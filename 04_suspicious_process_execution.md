# Suspicious Process Execution

## Overview
Suspicious process activity typically involves an unexpected parent-child
process relationship (for example, a document viewer spawning a scripting
or command interpreter process) or a process performing actions outside
its normal function.

## Key Indicators
- A document or email-handling application spawning a child process that
  is not part of its normal behaviour.
- A process making an outbound network connection shortly after being
  spawned, especially to a destination not on a known-good list.
- Process activity immediately following a user opening an email
  attachment.

## Why It Matters
This pattern (deliver -> open -> spawn process -> connect outbound) is a
classic user-execution-triggered chain. Each step alone might be
explainable, but the full chain occurring together in a short window is a
strong indicator of malicious activity requiring investigation.

## Recommended Response
- Isolate the affected endpoint from the network pending investigation.
- Capture and review the process tree and any files it wrote.
- Review outbound connection destinations against threat intelligence and
  known-good lists.
- Check other endpoints for the same indicator (attachment hash, process
  name, destination).
