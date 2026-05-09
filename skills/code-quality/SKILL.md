---
name: code-quality
description: Use when the user asks to review code quality, find redundant code, audit duplication, or "clean up" a codebase. Also use when the user says "find issues" or "anything worth fixing" after a feature is built. This skill provides a systematic framework for identifying code quality issues, evaluating whether each fix is worth making, and safely applying changes without over-engineering.
---

# Code Quality Reviewer

## Overview

Systematically review a codebase for quality issues, then evaluate each finding against a concrete benefit/side-effect framework before fixing. The goal is not "perfect" code — it's to find changes that reduce code without reducing readability, and fix correctness issues without introducing risk.

**Announce at start:** "I'm using the code quality reviewer to audit the codebase."

## The Core Principle: Benefit Must Outweigh Side Effects

For every potential fix, ask three questions:

1. **Does it reduce code without reducing readability?** Extracting a helper for a 3-line expression used twice is worth it. Extracting a component for 2 consumers that will diverge is not.
2. **Does it fix a real correctness/naming problem?** Unused imports, misleading names, dead code — fix these regardless of line count.
3. **Does the abstraction add more complexity than it removes?** A shared component with 6 props and conditional logic that saves 4 lines of JSX is a net loss.

## Judgment Heuristics

Beyond the three questions, these heuristics help decide edge cases:

### Explicit beats short

- A set of near-identical functions whose shared shape is trivial (call API → invalidate cache) does not justify a factory. Each function is 5-6 lines and reads independently; a factory would add type parameters and argument wiring that obscure what each variant actually does. **Visible repetition is better than invisible intent.**
- Abstract only when the shared logic is *non-trivial* — optimistic updates, rollback on error, retry with backoff. If the extraction doesn't reduce the reader's need to jump elsewhere, it's a net loss.

### Semantic duplication ≠ mechanical duplication

Two pieces of code that look the same aren't necessarily duplicates:

- **Identical types at different layers** — a deserialization type and a public return type may share every field, but they belong to different contracts. Merging them couples the public API to upstream changes. This is *isolation*, not waste.
- **Identical values with different meanings** — two keys mapping to the same value may encode distinct states. Collapsing them loses the explicit signal that "this case was considered and intentionally mapped." **Semantic clarity > eliminating a line.**
- **Sequential `await` in a loop** — lint will flag it, but `for...await` with `break` on first error is intentional control flow, not a mistake. Suppress the rule, don't restructure to `Promise.all()`.

### Don't design for hypotheticals

- No helper functions, abstraction layers, or config switches unless there's a *second caller right now*.
- "We might need this later" is not a valid reason.
- **Three similar lines > one premature abstraction.**

### Match the fix size to the problem size

Don't over-engineer a fix, but don't let rot compound either:

- **A two-line bug doesn't justify restructuring the module.** Patch it and move on. Rewriting the surrounding code for "consistency" is scope creep.
- **A 50-line function that's grown 6 arms over 8 commits** — that's when refactoring pays for itself. The cost of understanding it has already exceeded the cost of cleaning it.
- The test: *if I fix only the problem, will the next person still understand it?* Yes → patch. No → the surrounding code is part of the problem, refactor is fair game.
- **Corollary:** every "while I'm here" cleanup line is a bet that you're the last person to touch this file before it ships. If the cleanup isn't related to the task, it should be a separate commit.

### Follow existing patterns, or fix them all

- A questionable pattern is either a project-wide convention or a project-wide problem. Fixing one instance creates inconsistency; fixing none maintains the status quo.
- If the pattern isn't causing actual bugs, leave it alone. If it is, fix every instance in a dedicated commit — don't mix with feature work.

## Review Criteria

When scanning files, look for these specific patterns:

### Always worth fixing

- **Lint/fmt/typecheck errors** — zero controversy. Fix immediately.
- **Unused imports** — dead code, remove immediately
- **Dead code branches** — ternary with identical arms, unreachable code
- **Misleading names** — e.g., a component named `Lazy` that isn't actually lazy-loaded
- **Duplicate interface/types** — defined identically in two files (note: identical fields across API/public boundaries are *not* duplicates — see semantic duplication above)
- **Imports after component definitions** — move to top
- **Pointless wrappers** — `useCallback` that only forwards to another function, a function whose body is just calling another function with the same arguments

### Worth evaluating (benefit > side effect?)

- **Duplicated logic** — same non-trivial expression in 2+ places
- **Duplicated JSX structure** — same layout pattern repeated
- **Dynamic imports in event handlers** — should be top-level
- **Near-identical functions** — e.g., `useStar`/`useUnstar` with identical structure differing only in a boolean
- **Repeated boilerplate** — same 3-4 line pattern across files

### Usually NOT worth fixing

- **Duplication in 2 files that will diverge** — e.g., card vs. row layouts
- **Duplication of simple HTML shell** — a `<div>` with a className is not meaningful duplication
- **Single-use abstraction opportunities** — "don't build abstractions for single-use paths"
- **Trivial Set toggle** — `const next = new Set(x); next.has(y) ? next.delete(y) : next.add(y)` is clear enough inline
- **Mechanical duplication with semantic difference** — two structs with identical fields but different layer responsibilities, two color keys with same value but different meanings
- **Half-remediating a project-wide pattern** — fixing one instance of a repeated pattern while leaving others untouched creates inconsistency, not improvement. Fix all or fix none.
- **"Extract to a file" that doesn't reduce duplication** — moving one-off code to a separate file is file shuffling, not refactoring. If it's not deduplication AND it's not enabling testing, leave it inline.

## The Workflow

### Step 1: Explore

Spawn parallel Explore agents to list files and identify which ones to review. Skip UI primitives (`components/ui/`), test files, and generated code unless the user asks for them.

### Step 2: Review (parallel, read-only)

Spawn multiple agents in parallel, each reviewing a group of related files. Agents MUST be read-only — they report findings, they do NOT edit. Group files by directory/concern so each agent has context.

Each agent should:
- Read every file in its batch
- Report only issues that match the review criteria
- State whether fixing would reduce code without reducing readability
- Skip files with no issues

### Step 3: Aggregate and Present

Collect findings from all agents. Group by impact (high/medium/low) and type (code reduction vs. correctness). Present a summary table to the user and ask which they want to fix.

### Step 4: Fix (sequential, one at a time)

**CRITICAL: Fix issues sequentially, NOT in parallel.** Two agents editing related files (or the same file) will silently overwrite each other. Parallel fixes to a file edited by multiple agents will lose all but the last write — edits vanish without error.

For each issue the user wants to fix, follow this order strictly:

1. Read the relevant file(s) to get current state
2. **Propose a concrete solution first** — describe exactly what will change: which lines removed, what new code added, where it goes. This grounds the evaluation in reality.
3. **Evaluate the proposal** — now that the solution is concrete, weigh benefit vs. side effect:
   - Benefit: lines saved? clarity gained? correctness fixed?
   - Side effect: added indirection? new file to maintain? coupling between files that should stay separate?
4. **Decide** — if benefit > side effect, apply the change. If not, skip it and report why.
5. If applied, verify (tsc, tests) before moving to the next

Never evaluate without a concrete proposal — "this looks duplicated" is not enough. "Extract a 4-line helper function, saving 3 lines" makes the tradeoff visible.

### Step 5: Final Verification

After all fixes are applied, run the full verification suite: type checking and tests. Report what was changed and what was skipped (with reasons).

## Examples from Practice

### Good fix: merge two nearly identical mutations
An `useStar` and `useUnstar` hook (each ~18 lines) had identical optimistic update and rollback logic, differing only in the API call and a single boolean value. Extracted a parameterized factory function. Saved ~15 lines, no callers changed, tests passed as-is. **Correct: benefit > side effect.**

### Good fix: rename misleading component
A component was named `*Lazy` but used a static top-level import with no lazy loading. Renamed to `*Panel` to reflect reality. Zero line change, fixed misleading name. **Correct: fixes correctness issue.**

### Good skip: types with identical fields but different layer responsibilities
API response type and public command return type had identical fields. Suggested merging into one struct to eliminate a manual `.map()`. Skipped: keeping API shape and public interface separate prevents upstream API changes from cascading into the command layer. **Semantic isolation > mechanical deduplication.**

### Good skip: repeated hook boilerplate
A set of `useMutation` hooks shared the same query client + cache invalidation pattern. Suggested extracting a factory. Skipped: each hook is 5-6 lines with clearly visible mutation function and invalidation target at the call site. A factory would add type parameters and indirection without reducing meaningful complexity. **Explicit > short.**

### Bad fix (correctly skipped): extract shared row component from two dialogs
Two dialogs shared a 6-line JSX shell (a flex row with a label and toggle). But their substantive contents (status badges, disabled conditions, data sources) differed significantly. A shared component would need many props to accommodate the differences, saving ~4 lines of JSX while adding a new file and coupling two unrelated components. **Side effect > benefit.**

### Bad fix (correctly skipped): extract shared card from two settings rows
Two adjacent settings cards shared outer layout structure but differed in icon behavior (one changes icon while pending, one doesn't) and disabled conditions. Extracting a shared component would replace inline JSX with a component definition plus props interface, net lines flat or negative. **Premature abstraction: net zero gain with added indirection.**

## Parallel Editing Warning

When multiple agents edit simultaneously:
- Edits to the **same file** from different agents will silently overwrite each other
- Even edits to **different files** can be lost if agents write to overlapping sets of files
- The first write succeeds, subsequent writes to the same file silently replace it

**Safe pattern:** parallel reads → sequential writes. Use multiple agents to review code simultaneously (read-only), then apply fixes one at a time from the main conversation.

If you must use agents for fixes, dispatch them one at a time and wait for each to complete before dispatching the next. Or better: do the fixes yourself in the main conversation, since you have the full context.
