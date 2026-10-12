# Global Working Conventions

## Git conventions

- Preserve unrelated and pre-existing changes in the working tree.
- Inspect repository status and relevant diffs before modifying files.
- Keep changes focused on the requested task.
- Do not commit, push, rebase, amend, or otherwise rewrite history unless explicitly requested.
- Avoid destructive Git commands unless the user explicitly authorizes the exact operation.
- When asked to commit, use a concise Conventional Commit message that describes the actual change.
- Before committing, run checks appropriate to the change and review the staged diff.

## Branching and release workflow

### Branch roles

- Prefer `main` as the primary branch name over `master`.
- Do not rename an existing primary branch unless explicitly requested.
- Keep `main` release-only after the repository's initial commit.
- Every release commit on `main` must have a release tag.
- Detect and follow the repository's existing release-tag format. If no convention exists, ask before creating the first tag.
- Use `dev` as the development branch, or `develop` when that is the repository's established name.
- Keep development history on the development branch.
- Create `feat/*` and `fix/*` branches from the development branch.
- Prefer a separate Git worktree for work on `feat/*` and `fix/*` branches.
- By default, create worktrees under `<project-root>/.worktrees/` (for example, `.worktrees/feat-my-task`), unless the user explicitly requests another location.
- Resolve `<project-root>` to the repository's primary working tree, including when already inside a linked worktree; do not nest `.worktrees/` inside another worktree.
- Before creating a worktree, ensure `/.worktrees/` is ignored in the primary working tree. Prefer the repository's existing ignore rule; otherwise add it to the repository-local Git exclude file and verify with `git check-ignore`.
- Create `release/*` branches from the development branch.
- Limit release branches to release preparation, including minor fixes, version updates, release notes, and related validation.

### Merge and release rules

- Never perform any merge without explicit user approval.
- Before requesting approval, report the source branch, target branch, merge strategy, checks performed, and relevant risks.
- Merge `feat/*` and `fix/*` into the development branch with `git merge --no-ff`.
- After a successful feature or fix merge, remove its worktree and delete both the local and remote topic branches.
- Squash-merge `release/*` into `main`, producing one release commit.
- Never merge a release branch into `main` until the user explicitly confirms that the release is ready.
- Tag the resulting release commit using the repository's established tag convention.
- After the release is tagged, synchronize `main` back into the development branch with `git merge --no-ff`; this merge also requires explicit user approval.
- After the release and synchronization succeed, remove its worktree if present and delete both the local and remote release branches.
- Verify merge and tag results before cleanup. Do not delete branches when the merge, tagging, synchronization, or required checks fail.

## Documentation

- Inspect and follow the repository's existing documentation structure, terminology, and style.
- Update documentation when changing behavior, public interfaces, setup, configuration, or operational workflows.
- Keep examples and commands accurate and runnable.
- Explain rationale, constraints, and non-obvious behavior; avoid documenting self-evident implementation details.
- Use code comments primarily to explain why something exists, not to narrate what the code does.
- Do not introduce a new documentation structure when an established location already serves the purpose.
- If no documentation convention exists, update the nearest relevant README or create a focused document under `docs/`.
- Verify affected links, commands, and examples when practical.

## Model selection

- Follow the Global Agent Model Routing Policy below for model selection, reasoning effort, escalation, verification, and review. That policy takes precedence over conflicting conventions in this document.
- Model names: Sol = `gpt-6.1-sol`; Luna = `gpt-6-luna`; Astra = `gpt-6-astra`.
- Configure the root session to use Sol with `medium` reasoning effort for orchestration. This is a configuration prerequisite; AGENTS.md cannot switch the running root model or reasoning effort.
- Use Astra with `low` reasoning effort only for the architectural escalation and critical-review cases defined below. Sol remains the root orchestrator and receives Astra's findings.

## Subagent progress reporting

- Before every subagent spawn, announce its task or role, exact requested model identifier, and reasoning effort in a concise user-visible progress message.
- After a successful spawn, record the returned agent ID or task name, task description, requested model, and reasoning effort in session context. Record runtime-confirmed settings separately when the tool exposes them.
- Before every wait for subagents, show each outstanding agent's task or role, model identifier, and reasoning effort. When several agents are outstanding, group them in one concise message while keeping each agent identifiable.
- After a wait wakes or times out, include those same details in the required status update for outstanding agents.
- Distinguish requested settings from runtime-confirmed settings. Label unconfirmed settings as requested; a successful spawn alone does not prove which model executed the task. If settings are unavailable, say so instead of inferring them from the role or policy defaults.
- Report spawn failures, fallbacks, and model or reasoning-effort changes explicitly. Update the recorded assignment and use it in subsequent wait messages; never announce an agent as running if its spawn failed.
- These rules govern assistant progress messages; they do not configure model labels in the client's built-in subagent cards.

Example messages when runtime settings have not been confirmed:

```text
Spawning implementer — requested gpt-6-luna · max — update installer
Waiting for implementer — requested gpt-6-luna · max — update installer
Spawning reviewer — requested gpt-6.1-sol · medium — review changes
```

## Subagent completion

- Never send a final response while a subagent whose result is required for the current task is still active.
- Continue useful local work while subagents run. When no useful local work remains, call `wait_agent` with a timeout of 300000-600000 milliseconds instead of ending the turn.
- After every `wait_agent` wake or timeout, provide a concise status update, call `list_agents`, and reconcile every outstanding subagent, including any that finished without delivering a result.
- Continue waiting in bounded intervals until all required subagents have completed and their results have been collected and reviewed.
- If a required subagent is stalled or blocked, attempt an in-scope recovery or follow-up. Report the blocker to the user only when further progress genuinely requires user input or an external state change.
- Treat a final response produced with required subagents still active as an invalid completion, not a successful handoff.

## Superpowers plan execution handoff

- After writing a Superpowers implementation plan, save it and ask the user to review and explicitly approve it before offering execution modes.
- Do not begin plan execution before that approval.
- After approval, offer exactly these three choices:
  1. **Subagent-Driven** — use `superpowers:subagent-driven-development` for sequential task implementation with per-task reviews.
  2. **Inline Execution** — use `superpowers:executing-plans` in the active session with checkpoints.
  3. **Parallel SDD** — use `parallel-sdd` for dependency-aware concurrent task waves in isolated worktrees.
- Mode selection authorizes only the local mechanics defined by that execution skill. Preserve separate approval requirements for merges, pushes, publishing, destructive actions, and security-sensitive operations.

---

# Global Agent Model Routing Policy

Apply these rules to all software-engineering tasks unless a higher-priority instruction overrides them.

## 1. Objective

Optimize for:

**lowest expected total cost + strong necessary judgment + deterministic verification + independent review**

Every implementation task starts with a Luna `max` implementation attempt, including complex and high-risk tasks. Sol remains responsible for orchestration and architecture; the orchestrator chooses any repair or retry after verification and independent review.

Use:
- **Sol medium** for orchestration, architecture, material quality or conceptual-capability retries, and independent review.
- **Luna max** for exploration, the first implementation attempt on every task, localized repairs, and routine and integration test generation.
- **Astra low** for architectural escalation and critical review.
- **Deterministic tools** for verification.

Compare expected cost across the whole task, including context and reasoning tokens, retries, review, tool use, latency, and defect risk. A price multiplier `r` compares the cost of comparable billed token work; turn count alone is not a cost measure, and `r` is not a quota of failed attempts. Do not treat a lower per-token price as proof of lower total task cost.

---

## 2. Default Role Assignment

Use these defaults:

| Role | Model | Reasoning |
|---|---|---|
| Root orchestrator | Sol | medium |
| Architecture / decomposition | Sol | medium |
| Repo scout | Luna | max |
| Dependency/test scout | Luna | max |
| First implementation attempt, all tasks | Luna | max |
| Localized repair or revision | Luna | max |
| Material quality/capability retry | Sol | medium |
| Routine/integration test generation | Luna | max |
| Reviewer | Sol | medium |
| Architectural escalation | Astra | low |
| Critical-risk reviewer | Astra | low |

Use Luna `max` for the first implementation attempt on every task. Complexity, risk, or multi-file scope alone do NOT trigger an initial Sol implementation.

Do NOT increase reasoning effort when the real problem is insufficient model capability.

### Runtime routing mechanics

- Apply model and reasoning assignments by creating subagents with explicit `model` and `reasoning_effort` settings supported by the active runtime.
- When using explicit overrides, use `fork_turns: "none"`; full-history forks do not accept these overrides. Provide the task contract and relevant evidence explicitly when needed.
- Escalate by creating a new subagent at the required model and reasoning tier and handing over the current state, findings, and verification results. Do not assume an existing agent can change its model or reasoning effort in place.
- Respect the runtime's available models, delegation rules, and concurrency limits. Report any limitation that prevents required routing; do not claim a model assignment that did not occur.
- Treat cost optimization as a whole-task estimate that includes agent startup, context transfer, reasoning, retries, verification, review, tool use, latency, and defect risk. The fast path in Section 20 may reduce setup overhead, but never bypasses Luna for the first implementation attempt or required verification and review.

---

## 3. Core Rules

1. Use strong models for **judgment**, not high token volume.
2. Start every implementation task with Luna `max`; judge the full task cost and outcome after verification and review.
3. Keep Sol as the root orchestrator; delegate bounded escalations to Astra and return its findings to Sol.
4. Prefer executable verification over model confidence.
5. Review implementation independently.
6. Use Luna for localized, repairable gaps; use Sol for a retry when evidence shows a material quality shortfall or conceptual capability gap.
7. Avoid feeding Sol unnecessary repository context.
8. Use fresh reviewer context whenever practical.
9. Treat security, irreversible state, migrations, concurrency, and large blast radius as high risk.
10. Avoid unlimited agent/review loops.

---

## 4. Implementation Router

Before implementation, Sol classifies the task, establishes acceptance criteria, and provides architecture and constraints appropriate to its risk. Luna `max` makes the first implementation attempt for every task.

### First attempt: Luna max

Use Luna for the first implementation attempt on all work, including simple, normal, complex, and high-risk tasks. Sol's task contract should state the requirements, architecture, invariants, boundaries, and acceptance criteria needed to guide an isolated implementation and its review.

Typical work:
- renames
- boilerplate
- CRUD
- simple endpoint changes
- straightforward bug fixes with known root cause
- tests
- repetitive edits
- local refactors
- config changes
- multi-file features of any complexity
- high-risk changes implemented within Sol-defined boundaries
- integration work within established architecture
- routine and integration test generation

Do not skip Luna's first attempt because of complexity, risk, or expected difficulty. High-risk work keeps Sol's architecture and safety guidance, uses a bounded and isolated implementation, and receives Astra `low` critical review before a change is applied to consequential state.

### Sol medium implementation retry

After deterministic verification and independent review, the orchestrator chooses the next step from the evidence. Use Luna `max` for localized, repairable gaps. Use Sol `medium` for an implementation retry when the result is materially below task requirements or the findings show a conceptual capability gap that Luna is unlikely to repair reliably. Complexity or risk alone is not a reason to skip the Luna first attempt.

For high-risk work, Sol defines architecture and safety constraints before implementation. Keep consequential operations staged or isolated until the change passes deterministic verification and Astra `low` critical review.

### Use Astra low

Use Astra for bounded architectural escalation when:
- Sol cannot resolve architectural ambiguity or establish a stable root cause.
- Two substantive attempts with Sol fail because of conceptual or architectural errors.
- A critical security, concurrency, migration, or recovery decision remains unresolved after Sol's analysis.

Use Astra for critical review under Section 14, including high-risk implementation review before consequential changes are applied. Pass a compact task contract, relevant evidence, and verification results; return findings to the Sol orchestrator.

---

## 5. Routing Algorithm

Use this decision rule:

```text
Sol medium: orchestrate, define task boundaries, architecture, invariants, and risk controls
Luna max: make the first implementation attempt for every task
deterministic tools: verify the implementation
Sol medium / Astra low: independently review (Astra for critical-risk work)

if findings identify a localized, repairable gap:
    revise with Luna max
else if findings show material quality shortfall or conceptual capability gap:
    retry implementation with Sol medium
if critical-risk work is ready to affect consequential state:
    require Astra low critical review before applying it
if Luna is unavailable:
    report the runtime limitation and label any explicit fallback
```

When uncertain between adjacent tiers:
- Keep Luna as the first implementation attempt; use Sol's architecture and constraints to make risky work reviewable.
- After review, choose Luna repair or Sol retry based on the gap's scope and conceptual difficulty, considering expected full-task cost and defect risk.

---

## 6. Escalation

Default implementation and review path:

```text
Sol medium orchestration and architecture
-> Luna max first implementation attempt
-> deterministic verification
-> Sol medium independent review (Astra low for critical-risk review)
-> Luna max for localized repair OR Sol medium for material quality/capability retry
-> repeat verification and review for repaired or retried changes
```

Escalate when:
- Independent review finds a material quality shortfall or a conceptual gap beyond a localized Luna repair.
- Luna repeatedly misunderstands a stated invariant or architecture, and the defect is not a bounded correction.
- The task expands beyond its original architectural assumptions; Sol must re-plan and define the new scope.
- Reviewer findings expose a deeper design error or verification failures indicate a conceptual rather than mechanical issue.
- New security, migration, concurrency, consistency, or compatibility risk appears; strengthen Sol's guidance and use Astra critical review without skipping the Luna first attempt.

Do NOT escalate for:
- formatting
- trivial syntax errors
- missing imports
- obvious one-line fixes
- simple test expectation mistakes

Repair mechanical and localized failures with Luna `max`. Do not use a quoted price multiplier as a retry quota or require a fixed number of Luna failures before a Sol retry; make the decision from the verified gap, expected full-task cost, and defect risk.

Keep reasoning effort at the assigned setting: Luna max, Sol medium, or Astra low. If Luna cannot be assigned or is unavailable, report that runtime limitation before continuing and identify any Sol fallback explicitly; do not claim the required Luna attempt occurred. If Astra cannot resolve an issue, return the evidence to Sol for re-planning. Do not repeat unbounded attempts or silently select another model/effort.

---

## 7. Failure Classification

Classify failure before deciding what to do.

### Mechanical failure
Examples:
- syntax
- import
- formatting
- trivial branch omission
- simple test mismatch

Action:

```text
repair with Luna max when localized; otherwise have the orchestrator assess whether a Sol retry is warranted
```

### Understanding failure
Examples:
- wrong abstraction
- wrong ownership/module
- misunderstood requirement
- incorrect state model
- repeated cross-file inconsistency

Action:

```text
use Luna max for a bounded, localized repair; use Sol medium for a retry when the result is materially below requirements or the gap exceeds Luna's conceptual capability
```

### Architectural failure
Examples:
- current design cannot satisfy requirements
- invariant is missing
- data model is incompatible
- major redesign is necessary

Action:

```text
stop implementation
return to Sol orchestrator
re-plan
```

---

## 8. Orchestrator Responsibilities

Sol medium is the default root orchestrator.

The orchestrator MUST:
- interpret the user request
- identify acceptance criteria
- identify constraints and non-goals
- classify task complexity/risk
- require Luna max for the first implementation attempt; select any retry only after verification and independent review
- decide whether scouting is necessary
- identify relevant verification
- identify likely failure modes
- split independent work when useful
- resolve conflicting agent outputs
- escalate when required
- decide whether reviewer findings require redesign

The orchestrator SHOULD avoid doing repository-wide exploration itself.

---

## 9. Repository Exploration

Prefer Luna scouts before expensive reasoning.

For non-trivial tasks, use one or more Luna scouts to identify:
- relevant files/symbols
- callers/callees
- dependency relationships
- existing implementation patterns
- relevant tests
- architectural conventions
- likely regression surfaces
- unresolved questions

Parallelize independent scouting when useful.

Example:

```text
Scout A: relevant files and symbols
Scout B: tests and expected behavior
Scout C: dependencies and callers
Scout D: regression/security risks
```

Pass Sol a compact evidence package, not the entire repository.

Sol context SHOULD contain only:
- task
- acceptance criteria
- relevant files/symbols
- architecture
- constraints
- relevant tests
- dependency relationships
- risks
- unresolved decisions

Avoid repeatedly resending unchanged large context.

---

## 10. Task Contract

Before non-trivial implementation, create a compact task contract.

Include:

```text
Objective:
Required change.

Scope:
Expected files/modules/behavior.

Non-goals:
What must not change.

Acceptance criteria:
Observable completion conditions.

Constraints:
Architecture, compatibility, security, performance, style.

Verification:
Required commands/tests.

Risk areas:
Likely regressions and edge cases.
```

Implementers MUST optimize against this contract.

Implementers SHOULD NOT reinterpret the entire task from scratch unless the contract is inconsistent with repository evidence.

---

## 11. Parallelism

Use parallel agents when subtasks are independent.

Good uses:
- repository exploration
- independent bug hypotheses
- separate module investigation
- isolated implementation workstreams
- alternative design analysis
- independent review

Avoid parallel writes to heavily overlapping code unless ownership boundaries are explicit.

The orchestrator MUST reconcile parallel outputs before proceeding.

---

## 12. Verification

Run deterministic verification before model review whenever applicable.

Use relevant:
- unit tests
- integration tests
- targeted regression tests
- reproduction tests
- type checking
- linting
- formatting validation
- build/compile
- static analysis
- schema validation
- migration validation

Preferred pipeline:

```text
implement
-> deterministic verification
-> independent review
-> repair if needed
-> deterministic verification again
```

Model confidence is NOT verification.

A reviewer saying "looks correct" is NOT sufficient evidence.

---

## 13. Reviewer

Default reviewer: **Sol medium**.

Use a fresh context when practical.

Reviewer input SHOULD include:
1. original request
2. task contract
3. acceptance criteria
4. raw diff
5. relevant surrounding source
6. test/lint/typecheck/build results
7. known constraints

Do NOT provide implementer reasoning or persuasive self-explanation unless required to understand the code.

The reviewer MUST independently search for:
- correctness defects
- requirement violations
- regressions
- incorrect assumptions
- edge cases
- race conditions
- concurrency defects
- security vulnerabilities
- auth/authz failures
- data integrity risks
- public API breakage
- incomplete error handling
- missing meaningful tests
- weak tests that do not validate intended behavior

Reviewer MUST distinguish material defects from style preferences.

Return `PASS` only if no material defect is found.

Do NOT block solely on aesthetics unless enforced by repository policy/tooling.

---

## 14. Critical Review

Use Astra low for review when changes involve:
- authentication
- authorization
- payments
- cryptography
- security boundaries
- sensitive data
- database migrations
- irreversible mutation
- destructive operations
- concurrency
- distributed consistency
- public API compatibility
- high-blast-radius infrastructure
- recovery logic
- safety-critical business logic

Also consider Astra low when:
- reviewer and implementer repeatedly disagree
- a previous review missed a confirmed serious defect
- business/operational impact is unusually high

Use Sol medium for routine review. Astra critical review returns findings to the Sol orchestrator.

---

## 15. Repair Loop

For material reviewer findings:

```text
review finding
-> classify severity/root cause
-> localized, repairable gap: Luna max repair
-> material quality shortfall or conceptual capability gap: Sol medium implementation retry
-> repair
-> rerun deterministic verification
-> review changed areas again
```

Use Luna `max` for localized fixes. Use Sol `medium` only when the evidence supports a material quality or conceptual capability gap; task complexity or risk alone does not trigger the retry.

Escalate if the defect resulted from deeper architectural misunderstanding.

Do not require a fixed number of repair cycles before routing to Sol. Reassess each verified result and use Sol when findings show a material quality shortfall or conceptual capability gap.

Do NOT create unbounded review/repair loops.

---

## 16. Second Reviewer

A second reviewer from another model family MAY be used for high-value changes when correlated reasoning failure would be costly.

Consider it for:
- security-sensitive changes
- payments/financial state
- irreversible state changes
- complex architecture
- uncertain first review
- exceptionally costly missed defects

Do NOT require multi-model review for routine work.

---

## 17. Reasoning Effort

Treat model tier and reasoning effort as separate controls.

Defaults:

```text
Sol orchestrator          medium
Sol material-gap retry    medium
Sol reviewer              medium

Luna scout                max
Luna first implementation max
Luna localized repair     max
Luna test generation      max

Astra escalation          low
Astra critical reviewer   low
```

Use these fixed reasoning settings for this policy. Luna `max` is required for every first implementation attempt and localized repair; do not lower its effort merely because the work is routine.

If review shows a material quality shortfall or conceptual capability gap, the orchestrator may route an implementation retry to Sol `medium`. If Luna is unavailable, report the runtime fallback explicitly.

---

## 18. Context Cost Policy

Treat context as a costed resource.

For expensive models:
- pass relevant files only
- prefer diffs where sufficient
- preserve exact source when semantic precision matters
- summarize repetitive evidence
- remove irrelevant logs
- avoid duplicate large context
- let cheap agents search before strong agents reason

Default information flow:

```text
cheap models gather evidence
-> strong model decides
-> appropriate model implements
-> deterministic tools verify
-> strong model reviews
```

---

## 19. High-Risk Controls

Strengthen architecture guidance, isolation, verification, and review when an incorrect result could cause:
- security compromise
- privilege escalation
- cross-tenant exposure
- permanent data loss
- financial loss
- irreversible migration damage
- broken cryptographic guarantees
- major production outage
- large-scale compatibility failure

In high-risk work:
- Sol defines architecture, invariants, scope, and safety boundaries before implementation
- Luna `max` makes the first implementation attempt within those boundaries
- verify more aggressively
- use Astra `low` critical review before applying the change to consequential state
- prefer correctness over inference cost

---

## 20. Fast Path

Reduce setup overhead for trivial work only when ALL are true:
- unambiguous
- narrowly local
- low risk
- no architectural decision
- no sensitive/destructive behavior
- small blast radius
- strong deterministic verification exists

Fast path:

```text
Sol sets a brief task boundary when needed
-> Luna max first implementation attempt
-> targeted deterministic verification
-> independent review
-> complete
```

The fast path may omit separate scouting or a lengthy task contract when the change is obvious. It never lets the root implement first, bypasses Luna `max`, or waives deterministic verification and independent review.

---

## 21. Standard End-to-End Workflow

For normal non-trivial work:

```text
1. Sol medium
   Interpret task, classify risk/complexity.
   For high-risk work, define architecture, invariants, isolation, and safety boundaries.

2. Luna max
   Scout relevant files, tests, dependencies, and patterns when useful.

3. Sol medium
   Create task contract and implementation plan.

4. Luna max
   Make the first implementation attempt for every task.

5. Run deterministic verification.

6. Sol medium (Astra low for critical review)
   Review independently in fresh context.

7. Orchestrator routes findings:
   localized, repairable gap -> Luna max repair
   material quality shortfall or conceptual capability gap -> Sol medium retry
   high-risk change -> apply only after Astra low critical review is clear

8. Run deterministic verification again after repairs.
   Independently review repaired or retried changes.

9. Finish only when acceptance criteria and verification pass.
```

---

## 22. Compact Decision Rule

When no special rule applies:

```text
ORCHESTRATE
Sol medium

EXPLORE
Luna max

IMPLEMENT
first attempt, all tasks -> Luna max
localized repair -> Luna max
material quality/capability retry -> Sol medium

VERIFY
deterministic tools

REVIEW
Sol medium

CRITICAL REVIEW
Astra low

AFTER REVIEW
localized repairable gap -> Luna max
material quality/capability gap -> Sol medium retry
critical-risk review -> Astra low before consequential application
Luna unavailable -> report and label runtime fallback
```

---

## 23. Final Enforcement Rule

Always prefer:

```text
lowest expected total task cost
+
strongest necessary judgment
+
deterministic verification
+
independent review
```

Every implementation task starts with Luna `max`, regardless of complexity or risk. Sol `medium` provides orchestration and architecture, reviews independently, and may retry implementation when review finds a material quality shortfall or conceptual capability gap. Luna `max` handles localized repairs. Astra `low` handles defined architectural escalation and critical-risk review before consequential changes are applied. Compare expected cost and risk over the complete task; do not interpret a price multiplier as a retry quota.

Do not keep a weaker model on a task after evidence shows the task exceeds its capability.

Do not replace verification with additional reasoning.

Do not allow implementation and review to collapse into the same unchallenged reasoning path.
