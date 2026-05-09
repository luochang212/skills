# deepsec — Deep AI Investigation

> 适配 deepsec 2.x

## Overview

deepsec is an agent-powered vulnerability scanner. It has two stages:

1. **scan** — 110+ regex matchers find candidate sites (~15s, free)
2. **process** — AI agents (Claude or Codex) investigate each candidate with full code-reading context and produce findings (expensive, thorough)

It also has a **PR review mode** that collapses both into a single `--diff`-scoped invocation — fast, targeted, and CI-friendly.

deepsec is complementary to pattern-based scanners. A pattern scanner tells you "this line matches CWE-79". deepsec reads the surrounding 200 lines and tells you "this is exploitable because the input flows from `req.query.q` through the parser unescaped and reaches the DOM here."

**Announce at start:** "I'm using the Code Audit skill — deep audit mode."

## When to Use

**Use when:**
- User asks to "audit my codebase for vulnerabilities" or "find security issues"
- User mentions "deepsec", "AI-powered scan", or "agent security audit"
- User wants deeper investigation than static analysis can provide
- User asks to "review this PR for security" or "scan my changes for vulns"
- User has run a pattern-based scanner and wants to dig deeper on findings

**Don't use this mode for:**
- Quick grep/pattern search — deepsec's AI investigation is too heavy for simple keyword matching; use the fast scan mode instead
- Dependency vulnerability audit — use `npm audit` / `cargo audit`
- Runtime testing / fuzzing — deepsec analyzes source code only

## Two Operating Modes

### Mode A — Full Audit (scan → process → revalidate)

For auditing an entire codebase. Scan first, then AI investigates the candidates, then revalidate to cut false positives.

```
npx deepsec init → pnpm install → INFO.md → scan → process → revalidate → export
```

### Mode B — PR Review (process --diff)

For reviewing changed files in a PR. Collapses scan + process into one step, scoped to `git diff`. Exit code 1 when it finds something new — drop-in CI gate.

```bash
pnpm deepsec process --diff origin/main --agent claude
```

See the PR Review section below for full CI integration.

## Full Audit Walkthrough

### Step 1 — Initialize

Run in the **root of the target repo** (not inside `.deepsec/`):

```bash
npx deepsec init       # creates .deepsec/ scaffold
cd .deepsec
pnpm install           # installs deepsec from npm
```

`.deepsec/` is self-contained — it has its own `package.json` and `node_modules/`, independent of the parent repo's tooling. The parent repo doesn't need to be a Node project; deepsec is polyglot.

### Step 2 — API Configuration

deepsec reads `.env.local` in `.deepsec/`. Check what the user has:

```bash
echo "ANTHROPIC_AUTH_TOKEN=${ANTHROPIC_AUTH_TOKEN:+SET}"; echo "AI_GATEWAY_API_KEY=${AI_GATEWAY_API_KEY:+SET}"
```

If `claude` or `codex` is already logged in on the machine, non-sandbox runs reuse that subscription — no explicit API key needed. Otherwise, pick one:
- **Direct Anthropic**: `ANTHROPIC_AUTH_TOKEN=sk-ant-...` + `ANTHROPIC_BASE_URL=https://api.anthropic.com`
- **AI Gateway** (recommended for orgs): `ANTHROPIC_AUTH_TOKEN=vck_...` + `ANTHROPIC_BASE_URL=https://ai-gateway.vercel.sh` — one token covers both Claude and Codex

If using a non-Anthropic endpoint (e.g., DeepSeek's Anthropic-compatible API), always use `--agent claude` — the Codex backend won't work with those endpoints.

### Step 3 — Fill in INFO.md

`data/<project-id>/INFO.md` is injected into every AI scan batch. A vague INFO.md means vague findings. **Replace every section** of the template with project-specific content:

1. **What this codebase does** — stack, users, purpose (1 paragraph)
2. **Auth shape** — the 3–5 most important auth primitives BY NAME (e.g., `withAuth`, `requirePermission`, `auth.can()`)
3. **Threat model** — what an attacker would want, ranked by impact (2–4 sentences)
4. **Project-specific patterns to flag** — 3–5 patterns unique to THIS codebase, one example each. Skip generic CWE categories
5. **Known false-positives** — paths/patterns that look risky but are intentional (dev fixtures, one-shot migrations, internal health endpoints)

**Length budget: 50–100 lines total.** Verbose context dilutes signal. Pick 3–5 representative items per section. Name primitives by their public name, no line numbers. A good INFO.md looks like [the webapp sample](https://github.com/vercel-labs/deepsec/blob/main/samples/webapp/INFO.md).

**How to fill it in:** skim the repo's README, CLAUDE.md/AGENTS.md, package.json (or go.mod / Cargo.toml / pyproject.toml), and 5–10 representative code files (entry points, auth helpers). Stop when you have enough — don't do a full code tour.

### Step 4 — Scan (regex phase, free)

```bash
pnpm deepsec scan
```

Runs ~110 regex matchers, auto-detects frameworks (Next.js, Express, FastAPI, Rails, Gin, etc.), writes candidates to `data/<id>/files/`. ~15s for 2k files. Zero AI cost.

After scan, check coverage:
```bash
pnpm deepsec status     # how many files pending?
pnpm deepsec report     # see matchers that fired and coverage by language
```

**Rust/Go/Python repos:** deepsec's matchers are tilted toward TypeScript/Next.js. Expect fewer regex hits on non-TS repos. The AI processor is language-agnostic and will still investigate — the thinner the regex layer, the more `process` carries.

### Step 5 — AI Investigation (costs money)

**Always run a calibration pass first:**

```bash
pnpm deepsec process --agent claude --concurrency 2 --limit 20
```

This processes 20 files and lets you gauge cost per file before committing to the full pass.

**Cost guide** (Claude Opus, default settings):

| Files | Approx cost | Approx time |
|-------|-------------|-------------|
| 100 | $25–60 | 5–15 min |
| 500 | $130–300 | 25–60 min |
| 2,000 | $500–1200 | 1.5–4 hr |

Costs swing 2–3x based on file complexity. **Tell the user the estimate before running the full scan.**

**Model selection:**

| Use case | Flag | Cost vs Opus |
|----------|------|-------------|
| Default (best precision) | `--agent claude --model claude-opus-4-7` | 1× |
| Cheaper (10-20% higher FP) | `--agent claude --model claude-sonnet-4-6` | ~3× cheaper |
| Codex (sandboxed, fast) | `--agent codex --model gpt-5.5` | varies |
| Triage classification | default is sonnet-4-6 | ~1¢/finding |

**Mix backends for second opinions:**
```bash
# First pass with Claude
pnpm deepsec process --agent claude --concurrency 3

# Re-investigate unconvincing findings with Codex for a second opinion
pnpm deepsec process --agent codex --model gpt-5.4 --concurrency 5 --reinvestigate 1
```

Findings dedupe across agents. The `--reinvestigate <N>` wave marker tags the new analysis without losing the old one. This is also how you evaluate a new model — re-run with the new model and see if it overturns verdicts.

**Incremental behavior:** `process` only touches files with `status: "pending"`. Interrupted runs resume — just re-run the same command. The merge model is additive: re-running appends to `analysisHistory`, never overwrites.

### Step 6 — Revalidate and Export

```bash
# Revalidate findings — re-reads code + git history to cut false positives
# Empirically reduces FP rate by 50%+. Comparable cost to process.
pnpm deepsec revalidate --agent claude --min-severity MEDIUM

# Triage: classify findings P0/P1/P2 without re-reading code (~1¢/finding)
pnpm deepsec triage --severity HIGH

# Export to individual markdown files per finding
pnpm deepsec export --format md-dir --out ./findings

# Or export as single JSON array for piping to issue trackers
pnpm deepsec export --format json --out findings.json
```

Revalidation verdicts: `true-positive`, `false-positive`, `fixed`, `uncertain`. After revalidation, `pnpm deepsec report` shows the TP/FP breakdown.

### Querying findings with jq

```bash
# All TP HIGH+ findings across a project
jq -r '. as $r | $r.findings[] | select(.revalidation.verdict=="true-positive") | select(.severity=="HIGH" or .severity=="CRITICAL") | [$r.filePath, .severity, .title] | @tsv' data/<id>/files/**/*.json

# Total spend on a project
jq -s 'map(.analysisHistory[].costUsd // 0) | add' data/<id>/files/**/*.json

# Files still pending
jq -r 'select(.status=="pending") | .filePath' data/<id>/files/**/*.json
```

### Step 7 — Present Results

Read the exported markdown files and present findings grouped by severity. For each:
- What the issue is in plain language
- Where it is (file, lines)
- What the fix looks like

Don't dump raw output. Offer to fix after presenting — only fix if the user explicitly agrees.

## PR Review Mode

For reviewing changed files in a PR. Collapses scan + process into one step.

### Basic usage

```bash
# Review diff against main
pnpm deepsec process --diff origin/main --agent claude

# Review uncommitted changes
pnpm deepsec process --diff-working --agent claude

# Review specific files
pnpm deepsec process --files "src/api/auth.ts,src/middleware/session.ts" --agent claude
```

### Exit codes (CI gating)

| Code | Meaning |
|------|---------|
| 0 | No findings — clean pass |
| 1 | At least one **net-new** finding — gate fails |
| ≠1 | Runtime error |

Only net-new findings count — pre-existing findings on touched files don't fail the build.

### CI workflow (GitHub Actions)

The recommended pattern uses a **two-job split** for security: `analyze` runs PR code with AI gateway secret but **no write permissions**. `comment` has `pull-requests: write` but never runs PR code.

```yaml
name: deepsec
on: pull_request
permissions:
  contents: read

jobs:
  analyze:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24, cache: pnpm }

      - run: pnpm install --frozen-lockfile
      - run: npm install -g @anthropic-ai/claude-code

      - id: deepsec
        env:
          AI_GATEWAY_API_KEY: ${{ secrets.AI_GATEWAY_API_KEY }}
          CLAUDE_CODE_EXECUTABLE: claude
        run: |
          pnpm deepsec process \
            --diff origin/${{ github.event.pull_request.base.ref }} \
            --comment-out comment.md

      - if: always() && hashFiles('comment.md') != ''
        uses: actions/upload-artifact@v4
        with:
          name: deepsec-comment
          path: comment.md
          retention-days: 1

  comment:
    needs: analyze
    if: always() && needs.analyze.result == 'failure'
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/download-artifact@v4
        with: { name: deepsec-comment }
        continue-on-error: true
      - uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: fs.readFileSync('comment.md', 'utf8'),
            });
```

Key security decisions in this workflow:
- **Don't grant `pull-requests: write` to a job that runs PR code** — PRs can add arbitrary code to `package.json` postinstall scripts. The two-job split keeps write permissions isolated.
- **Same-repo-only gate** — fork PRs skip `analyze` (they don't receive repo secrets under `pull_request` anyway).
- **`fetch-depth: 0`** — needed for `git diff origin/<base>` to resolve the merge base.
- **Pin actions to commit SHAs in production** — the example uses `@v4` for readability.

### When to use PR mode vs full audit

| Scenario | Use |
|----------|-----|
| First scan of a large repo | Full audit (`scan` + `process`) |
| Daily PR review | `process --diff origin/main` |
| Re-checking existing findings | `revalidate` |
| Weekly cron sweep | Full audit |

## Custom Matchers

When revalidated TPs reveal patterns deepsec's built-in matchers miss, add custom matchers. The loop is:

```
scan → process → revalidate → identify TP patterns → write custom matchers → scan again
```

### When to write one

- A revalidated TP needs a matcher to catch siblings on future scans
- A cluster of `other-*` slugs in metrics points at a real category deepsec has no name for
- The repo has entry points the default matchers don't see (check `supported-tech.md` first)
- You have an org-specific pattern (internal auth helper, internal SDK, custom middleware)

### Noise tiers

| Tier | When | Sweet spot |
|------|------|-----------|
| `precise` | Pattern is unambiguous | 1–20 hits per 1k files |
| `normal` | Broader pattern; AI disambiguates | 5–100 hits per 1k files |
| `noisy` | Every file matching a glob should be AI-reviewed | ~entry-point count |

`precise` candidates process first (highest signal per token).

### Matcher structure

Place matchers in `.deepsec/matchers/<slug>.ts`, wire them through an inline plugin in `deepsec.config.ts`:

```ts
// .deepsec/matchers/my-route-no-auth.ts
import type { MatcherPlugin, CandidateMatch } from "deepsec/config";
import { regexMatcher } from "deepsec/config";

export const myRouteNoAuth: MatcherPlugin = {
  slug: "my-route-no-auth",
  description: "API route handlers without auth wrapper",
  noiseTier: "normal",
  filePatterns: ["src/api/**/*.ts"],
  match(content, filePath) {
    if (/\.(test|spec)\.tsx?$/.test(filePath)) return [];
    if (/\/__tests__\//.test(filePath)) return [];
    // ... match logic
    return regexMatcher("my-route-no-auth", [
      { regex: /export\s+async\s+function\s+(GET|POST)\b/, label: "no-auth-handler" },
    ], content);
  },
};
```

Reference examples ship in `node_modules/deepsec/dist/samples/webapp/matchers/` — study those for the full pattern.

To grow the matcher set with a coding agent, point it at `.deepsec/data/` + the target repo with the prompt in `node_modules/deepsec/dist/docs/writing-matchers.md`.

## Multi-Project Setup

One `.deepsec/` workspace can scan multiple codebases:

```bash
pnpm deepsec init-project ../another-service
pnpm deepsec scan --project-id another-service
pnpm deepsec process --project-id another-service --agent claude
```

Or declare them in `deepsec.config.ts`:
```ts
export default defineConfig({
  projects: [
    { id: "webapp", root: "../webapp" },
    { id: "api", root: "../api", githubUrl: "https://github.com/me/api/blob/main" },
  ],
});
```

When there's only one project, `--project-id` auto-resolves.

## Project Configuration

Optional `data/<id>/config.json` for per-project overrides:

```json
{
  "priorityPaths": ["src/api/admin/", "src/api/billing/", "src/lib/auth/"],
  "promptAppend": "Pay extra attention to the admin and billing surfaces.",
  "ignorePaths": ["**/legacy/**", "**/generated/**", "**/fixtures/**"]
}
```

- `priorityPaths` — processed first (highest-value files)
- `promptAppend` — appended to the system prompt for every batch
- `ignorePaths` — glob patterns to skip during scan

## Common Issues

### "pnpm not found"
```bash
npm install -g pnpm
```

### Codex backend fails with 404
`ANTHROPIC_BASE_URL` points to a non-Anthropic API (e.g., DeepSeek). Switch to `--agent claude`.

### "missing YAML frontmatter" errors
Non-critical. deepsec loads agent skills from `~/.agents/skills/` at startup. Malformed SKILL.md files produce warnings but don't affect scanning.

### Rust files get 0 scan hits
Built-in matchers focus on TS/JS/Python. Rust detection exists (`actix`, `axum`, etc.) but dedicated matchers are on the roadmap. The AI processor can still read Rust files when they're referenced by frontend code. For Rust-heavy repos, write custom matchers.

### INFO.md is too verbose
If findings are vague or miss obvious patterns, trim INFO.md. Target 50–100 lines. Focus on what a reviewer would miss if they didn't read it.

### A file keeps triggering refusals (>5% of batches)
Usually contains a hard-to-disambiguate exploit pattern. Add it to `config.json:ignorePaths`, or run that file alone with `--batch-size 1` so a refusal doesn't take down the whole batch.

### Batch failed with "no result after 3 attempts"
The agent crashed mid-investigation. Affected files are marked `status: "error"`. Re-running `process` retries them automatically.

## Tips

- deepsec is designed for **on-demand review**, not CI gating (PR mode has CI gating, but you don't gate merges on the full audit). For scheduled scanning, run a cron job that does `scan → process → revalidate → export`.
- The regex scan finds candidate sites, not every line. For better coverage of non-TS languages, write custom matchers.
- Findings persist across runs. Nothing is overwritten — the merge model is additive.
- `.deepsec/` is meant to be checked into git (config, custom matchers, INFO.md). Scan output (`data/*/files/`, `data/*/runs/`, `data/*/reports/`) is gitignored.
- Be upfront about costs. Always run a calibration pass (`--limit 20`) before the full scan.
- For large repos (>5k files), consider `deepsec sandbox process` to fan work across Vercel Sandbox microVMs in parallel.
- FP rate after revalidation on HIGH+ findings: ~10–29%.
