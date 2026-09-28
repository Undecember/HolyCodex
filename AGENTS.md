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
- Model names: Sol = `gpt-6-sol`; Terra = `gpt-5.6-terra`; Luna = `gpt-5.6-luna`; Astra = `gpt-6-astra`.
- Configure the root session to use Sol with `medium` reasoning effort for orchestration. This is a configuration prerequisite; AGENTS.md cannot switch the running root model or reasoning effort.
- Use Astra only when the user explicitly requests it. Do not route to Astra automatically for risk, complexity, review, or escalation.

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

**lowest-cost reliable execution + strongest necessary judgment + deterministic verification + independent review**

Do NOT use the strongest model everywhere.

Use:
- **Sol** for orchestration, architecture, high-risk reasoning, escalation, and independent review.
- **Terra** for serious implementation.
- **Luna** for exploration, mechanical work, and well-specified low-risk implementation.
- **Deterministic tools** for verification.

---

## 2. Default Role Assignment

Use these defaults:

| Role | Model | Reasoning |
|---|---|---|
| Root orchestrator | Sol | medium |
| Architecture / decomposition | Sol | medium |
| Repo scout | Luna | low/medium |
| Dependency/test scout | Luna | low/medium |
| Simple implementer | Luna | high |
| Normal implementer | Terra | medium |
| Complex implementer | Terra | high |
| Critical/hard implementer | Sol | medium |
| Test generation | Luna high or Terra medium | adaptive |
| Reviewer | Sol | medium |
| Critical-risk reviewer | Sol | high |

Do NOT use Luna `max` as the default implementer.

Do NOT increase reasoning effort when the real problem is insufficient model capability.

### Runtime routing mechanics

- Apply model and reasoning assignments by creating subagents with explicit `model` and `reasoning_effort` settings supported by the active runtime.
- When using explicit overrides, use `fork_turns: "none"` or a limited number of turns; full-history forks do not accept these overrides. Provide the task contract and relevant evidence explicitly when needed.
- Escalate by creating a new subagent at the required model and reasoning tier and handing over the current state, findings, and verification results. Do not assume an existing agent can change its model or reasoning effort in place.
- Respect the runtime's available models, delegation rules, and concurrency limits. Report any limitation that prevents required routing; do not claim a model assignment that did not occur.
- Treat cost optimization as a heuristic that includes agent startup, context transfer, verification, and review overhead. Apply the trivial-work exception in Section 20 before delegating.

---

## 3. Core Rules

1. Use strong models for **judgment**, not high token volume.
2. Start with the cheapest model likely to succeed reliably.
3. Keep orchestration capability >= implementation capability.
4. Prefer executable verification over model confidence.
5. Review implementation independently.
6. Escalate model capability after substantive failures.
7. Avoid feeding Sol unnecessary repository context.
8. Use fresh reviewer context whenever practical.
9. Treat security, irreversible state, migrations, concurrency, and large blast radius as high risk.
10. Avoid unlimited agent/review loops.

---

## 4. Implementation Router

Before implementation, classify the task.

### Use Luna high

Use Luna when ALL or nearly all are true:
- Task is explicit and narrowly scoped.
- Relevant files are known or easy to identify.
- Existing patterns can be followed mechanically.
- Little architectural judgment is required.
- Blast radius is small.
- Failure is easy to detect deterministically.

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

### Use Terra medium

Use Terra medium when:
- Work spans multiple files/modules.
- Significant codebase understanding is required.
- Some ambiguity exists.
- A feature touches several abstractions.
- Integration behavior matters.
- Regression risk is meaningful but not critical.

This is the default model for serious implementation.

### Use Terra high

Use Terra high when:
- State transitions are complex.
- Refactoring is non-trivial.
- Multiple interacting abstractions change.
- Root cause requires substantial reasoning.
- Cross-module behavior is difficult.
- Regression risk is high.
- The implementation strategy is mostly known but technically difficult.

### Use Sol medium

Use Sol directly when implementation requires stronger reasoning, especially:
- concurrency
- distributed consistency
- synchronization
- transaction semantics
- risky database migrations
- authentication/authorization internals
- security boundaries
- destructive operations
- hard algorithms
- major architectural refactors
- public API compatibility
- recovery/consistency logic
- unresolved architectural ambiguity
- repeated Terra failure

Do NOT use Sol for routine implementation except under the trivial-work exception in Section 20.

---

## 5. Routing Algorithm

Use this decision rule:

```text
if local + explicit + low-risk + mechanically verifiable:
        implement with Luna high

        elif multi-file or moderately ambiguous or substantial codebase reasoning:
            implement with Terra medium

            elif complex state or difficult cross-cutting behavior or high regression risk:
                implement with Terra high

                elif critical correctness or security or concurrency or distributed state
                     or migration risk or destructive behavior or unresolved architecture:
                         implement with Sol medium
```

When uncertain between adjacent tiers:
- Choose the cheaper tier if failure is cheap and strongly detectable.
- Choose the stronger tier if failure is expensive, subtle, or hard to detect.

---

## 6. Escalation

Default escalation path:

```text
Luna high
-> Terra medium
-> Terra high
-> Sol medium
-> Sol high only when justified
```

Escalate when:
- Two substantive attempts fail at the same tier.
- The model repeatedly misunderstands architecture.
- The model cannot establish a stable root cause.
- The task expands beyond its original architectural assumptions.
- Reviewer findings expose a deeper design error.
- New security, migration, concurrency, consistency, or compatibility risk appears.
- Verification failures indicate conceptual rather than mechanical errors.

Do NOT escalate for:
- formatting
- trivial syntax errors
- missing imports
- obvious one-line fixes
- simple test expectation mistakes

Repair mechanical failures at the current tier.

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
repair at current model tier
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
escalate model capability
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
- select implementation model
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

Use Sol high for review when changes involve:
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

Also consider Sol high when:
- reviewer and implementer repeatedly disagree
- a previous review missed a confirmed serious defect
- business/operational impact is unusually high

Do NOT use Sol high routinely.

---

## 15. Repair Loop

For material reviewer findings:

```text
review finding
-> classify severity/root cause
-> choose appropriate implementer
-> repair
-> rerun deterministic verification
-> review changed areas again
```

Use the same implementer for localized fixes.

Escalate if the defect resulted from deeper architectural misunderstanding.

After two substantive failed repair cycles at one tier, escalate.

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
Sol orchestrator         medium
Sol reviewer             medium
Sol critical reviewer    high

Luna scout               low/medium
Luna implementer         high

Terra implementer        medium
Terra complex work       high
```

Avoid `max` by default.

Increase reasoning only when:
- the model tier is already appropriate
- more deliberation is likely to improve the result

If capability is insufficient, escalate the model instead.

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

## 19. High-Risk Override

Ignore normal cost-first routing when an incorrect result could cause:
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
- escalate earlier
- verify more aggressively
- use Sol for key implementation decisions
- use Sol high review where justified
- prefer correctness over inference cost

---

## 20. Fast Path

Skip unnecessary orchestration/review overhead for trivial work only when ALL are true:
- unambiguous
- narrowly local
- low risk
- no architectural decision
- no sensitive/destructive behavior
- small blast radius
- strong deterministic verification exists

Fast path:

```text
Luna high (or the current root under the exception below)
-> tests/lint/typecheck/build as applicable
-> complete
```

When all fast-path conditions above hold and delegation would cost more than completing and verifying the task locally, the current root may perform the work directly. This exception takes precedence over routine implementation routing and cost prohibitions elsewhere in this policy. It does not waive deterministic verification or apply to non-trivial or high-risk work.

Sol review is optional for purely mechanical changes.

---

## 21. Standard End-to-End Workflow

For normal non-trivial work:

```text
1. Sol medium
   Interpret task, classify risk/complexity.

   2. Luna low/medium
      Scout relevant files, tests, dependencies, patterns.

      3. Sol medium
         Create task contract and implementation plan.

         4. Route implementation:
            simple   -> Luna high
               normal   -> Terra medium
                  complex  -> Terra high
                     critical -> Sol medium

                     5. Run deterministic verification.

                     6. Sol medium
                        Review independently in fresh context.

                        7. If defects:
                           repair at appropriate tier
                              escalate when needed

                              8. Run deterministic verification again.

                              9. Finish only when acceptance criteria and verification pass.
```

---

## 22. Compact Decision Rule

When no special rule applies:

```text
ORCHESTRATE
Sol medium

EXPLORE
Luna low/medium

IMPLEMENT
simple   -> Luna high
normal   -> Terra medium
complex  -> Terra high
critical -> Sol medium

VERIFY
deterministic tools

REVIEW
Sol medium

CRITICAL REVIEW
Sol high

ESCALATE
Luna -> Terra medium -> Terra high -> Sol medium
```

---

## 23. Final Enforcement Rule

Always prefer:

```text
cheapest reliable execution
+
strongest necessary judgment
+
deterministic verification
+
independent review
```

Prefer Luna or Terra for work they can reliably perform, accounting for total execution overhead and the trivial-work exception in Section 20.

Do not keep a weaker model on a task after evidence shows the task exceeds its capability.

Do not replace verification with additional reasoning.

Do not allow implementation and review to collapse into the same unchallenged reasoning path.
