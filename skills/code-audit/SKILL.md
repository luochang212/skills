---
name: code-audit
description: Security audit and code scanning. Use when the user asks to scan code for bugs/vulnerabilities, audit security, run SAST, find code patterns, or review code for security issues. Supports two modes — fast pattern scanning (Semgrep) for quick results and CI gating, and deep AI-powered investigation (deepsec) for thorough reasoning-based analysis. Also use when the user mentions "semgrep", "deepsec", "static analysis", "security scan", "code scanning", "find vulnerabilities", "scan my code", or "security audit".
---

# Code Audit

## Overview

Two complementary security audit approaches, one skill. Pick the right mode for the task.

**Fast scan** — pattern-matching scanner. Finds bugs, security vulnerabilities, and coding standard violations across 30+ languages in seconds. Best for CI gating, quick baselines, and "find all places where X is used with Y."

**Deep audit** — AI-powered investigation. Regex matchers find candidate sites (~15s), then AI agents read full context and reason about exploitability. Best when you need to know "is this actually exploitable?" not just "this line matches a pattern."

The two modes can chain: run a fast scan to surface candidates, then deep-investigate the findings that matter.

## Decision Guide

| User says | Mode | Read |
|-----------|------|------|
| "扫一下" / "find bugs" / "semgrep" / "CI scan" / "find patterns" / "SAST" | Fast scan | `references/semgrep.md` |
| "深度审计" / "deepsec" / "AI scan" / "PR security review" / "is this exploitable" | Deep audit | `references/deepsec.md` |
| "审计" / "security review" (ambiguous) | Ask: quick scan or deep AI investigation? | Both |

If the user provides no clear signal, briefly explain both modes and let them choose. Fast scan takes seconds and is free; deep audit takes minutes and costs money.

## When NOT to use

- General code quality review (duplication, naming, dead code) — this is about security/bug scanning, not code style
- Dependency vulnerability audit — use `npm audit` / `cargo audit` / `pip audit`
- Runtime testing / fuzzing — these tools analyze source code only
- Runtime debugging — static analysis, not runtime inspection

## Workflow

1. Read the decision guide above and pick the right reference file
2. Read the relevant `references/*.md` file and follow its workflow
3. Report findings to the user, offer to fix if appropriate
