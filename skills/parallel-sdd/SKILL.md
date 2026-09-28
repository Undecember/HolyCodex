---
name: parallel-sdd
description: Execute an implementation plan through dependency-aware waves of subagents in isolated Git worktrees, with deterministic verification and independent review. Use when the user selects Parallel SDD or requests parallel subagent-driven implementation; not for ordinary single-task edits or parallel research alone.
---

# Parallel SDD

Inspect dependencies between implementation tasks, generate a task-dependency graph, and execute successive waves of tasks that can run in parallel. Keep one orchestrator responsible for the graph, wave scheduling, ownership, integration, and completion. This skill is self-contained and does not require Superpowers or another execution skill.

## Establish the execution boundary

- Read applicable AGENTS.md instructions, the plan, and existing session approvals. Follow user instructions over this skill and preserve repository-specific Git and model-routing policies.
- If the workflow requires explicit plan approval, confirm it already exists before implementation. Selection of this mode authorizes its local execution mechanics only; it does not authorize commits, merges, pushes, publishing, destructive cleanup, or other separately restricted actions. Do not ask again for authorization already given.
- If no usable plan exists, prepare a compact task graph and acceptance criteria first. Apply the repository's plan-approval rule if present; do not invent an additional approval gate otherwise.
- Inspect Git status, relevant diffs, branches, and `git worktree list --porcelain` before changing files. Preserve pre-existing changes. Identify the development branch and primary working tree; do not assume the current checkout is either.
- Verify that delegation is available. If it is unavailable, disclose that limitation and follow an already-authorized fallback; do not claim parallel execution or independent review took place.

## Build the task graph

Before dispatching implementation, inspect each task's inputs, outputs, relevant source, and shared interfaces. Identify actual prerequisites rather than assuming that plan order expresses dependencies. Give tasks stable IDs and record a reason for each dependency edge.

Generate and present a directed task-dependency graph, preferably as Mermaid: `A --> B` means B requires A's output. Include independent tasks as nodes too. Distinguish prerequisite edges from scheduling constraints such as overlapping file ownership or a shared test database. Check that all referenced tasks exist and that the graph has no cycles. Resolve cycles by revising task boundaries or clarifying the dependency; do not dispatch a cyclic schedule.

Derive and present numbered waves from the graph. Wave 1 contains tasks with no unmet prerequisites; each subsequent wave contains tasks whose prerequisites are satisfied by earlier waves. Tasks within a wave must have no dependency on one another and must be safe to run concurrently. Split otherwise-ready tasks into separate waves when ownership or resource conflicts require it.

Maintain a compact ledger in the existing plan location, or in session context for short runs:

| Task | Dependencies | Wave | Owned files / interfaces | Worktree / branch | State | Verification / review |
| --- | --- | --- | --- | --- | --- | --- |

Use states such as pending, running, verifying, reviewing, ready for integration, complete, and blocked. Record each task's input baseline and output artifacts so a resumed session can reconcile actual state.

Each implementation task needs a contract containing:

- Objective, scope, and non-goals.
- Observable acceptance criteria and relevant constraints.
- Owned files or modules, interface agreements, and dependencies.
- Exact worktree path and baseline revision.
- Required verification commands and important regression risks.
- Allowed Git operations and expected handoff artifacts.

A task is runnable only when its prerequisites are available in its own checkout. An upstream agent saying “done” is insufficient. Shared interfaces, generated files, lockfiles, migrations, and overlapping edits usually require explicit ordering or a single owner. Separate worktrees isolate writes but do not eliminate semantic conflicts.

Run only genuinely independent tasks together. Reserve enough runtime capacity for the orchestrator and review; respect actual concurrency limits. Small or tightly coupled work should remain sequential.

## Execute each wave

Dispatch the current wave's tasks concurrently in their assigned worktrees, within the runtime's agent limit. If the wave exceeds capacity, run it in batches; capacity limits do not create dependency edges.

Collect results, run the required verification and independent review, and resolve material findings before advancing to the next wave. Materialize accepted prerequisite outputs in dependent task checkouts before dispatching them. Keep the wave barrier even when one task finishes early; use spare capacity for review or preparation instead of starting the next wave.

If a task fails, let independent tasks already in its wave finish, then repair or explicitly revise the remaining schedule. Never treat a failed prerequisite as satisfied. When new dependencies or conflicts emerge, update the graph and wave assignments before further dispatch. Report each wave's outcomes and the next runnable wave.

## Isolate implementation

- Follow the repository's branch and worktree conventions. By default, use topic branches from `dev` (or established `develop`) and paths under `<primary-project-root>/.worktrees/`; never nest this directory inside a linked worktree.
- Before creating worktrees, verify `/.worktrees/` is ignored in the primary checkout. Prefer an existing rule; otherwise add it to the repository-local Git exclude file and verify with `git check-ignore`.
- Use unique task branches and paths. Inspect an existing branch or worktree before reusing it; never reset or delete it to make the setup succeed.
- Give each implementer one writable worktree and explicit file ownership. All agents share a filesystem: every command must target the assigned worktree. Do not let agents edit sibling worktrees, shared Git configuration, or the primary checkout.
- Start independent tasks from the agreed baseline. For dependent tasks, first materialize the reviewed prerequisite changes in the new task's checkout using authorized operations. If commits are not authorized, reviewed patches can be applied to a prepared checkout; include untracked files and binary artifacts where needed, and record provenance. Never silently commit to enable scheduling.
- Control shared resources too: give integration tests distinct ports, temporary paths, databases, or serialize tests when isolation is unavailable. A worktree alone does not isolate external state.

## Route and dispatch agents

Use the applicable model-routing policy. In its absence, prefer Luna (`gpt-5.6-luna`) for scouting and narrow mechanical work, Terra (`gpt-5.6-terra`) for normal implementation, and Astra (`gpt-6-astra`) for architecture, critical correctness, and independent review. Use explicit supported overrides with fresh or limited context; report unavailable tiers rather than claiming them. Do not attempt to switch the running root model through this skill.

Send the task contract and minimal relevant source evidence, not the full repository or other agents' reasoning. Implementers must report changed files, verification results, unresolved issues, and their output location. They must not merge, commit, push, or clean up branches unless those exact actions are authorized.

The orchestrator continues useful work while agents run: prepare upcoming contracts, inspect interface compatibility, or validate completed outputs. Reconcile agent messages with files and test results before updating the ledger.

## Verify and review

1. Run meaningful deterministic checks in the task's actual worktree: targeted tests, type checks, lint, build, or a reproduction as appropriate. Capture commands, outcomes, and environmental limitations.
2. Give a fresh reviewer the original contract, raw diff (including new files), relevant surrounding source, and verification results. Avoid passing persuasive implementation reasoning. The reviewer inspects correctness, acceptance criteria, regressions, interfaces, and material risk; style preferences alone do not block unless enforced by the project.
3. Resolve material findings with the appropriate implementer, rerun affected checks, and review the repaired areas. Follow the project's escalation policy; after repeated conceptual failures, increase capability or revisit the design instead of looping indefinitely.
4. Mark output ready for integration only after verification and review. Do not mark the whole feature complete merely because every isolated task passed.

Reviewers must not mutate a checkout while its implementer is working. Freeze the reviewed output or record the reviewed revision/diff; subsequent changes invalidate affected review and checks.

## Integrate without expanding authorization

The orchestrator owns integration. Assemble outputs in dependency order in a designated integration worktree using authorized operations; preserve the source worktrees until the result is verified. Inspect conflicts semantically instead of choosing one side wholesale. Review interface interactions and run the combined acceptance checks: isolated tests do not prove the combined feature works.

Where merges require approval, first make the result concrete and reviewable, then report source branch, target branch, merge strategy, checks, and material risks. Request only the missing approval. Applying a patch must not be used to bypass a branch's release-only role or a required integration approval. If integration is not authorized, leave verified outputs intact and report them as ready for integration, not merged or delivered on the target branch.

Do not commit, push, rewrite history, tag, or publish without applicable authorization. Follow repository cleanup rules only after required integration and checks succeed, and when removal is authorized. Never remove a worktree containing unpreserved work or delete branches after failed integration.

## Wait, recover, and finish

- Track every required agent until its result is collected and reviewed. Do not send the final answer while required agents are active.
- When no useful local work remains, wait for agent updates in bounded intervals compatible with the runtime's communication requirements. After waking, list agents, reconcile outstanding work, and give a concise update.
- If an agent stalls, inspect its status and worktree, send a focused follow-up, and recover in scope. Before reassigning its writable worktree, stop the previous writer and confirm it is no longer running. Preserve partial work and verification evidence.
- If one task fails, continue independent work where useful and keep its dependents pending. If a prerequisite or external decision truly blocks progress, state the concrete blocker and retain recoverable outputs.
- At completion, report implemented behavior, combined verification, independent review, remaining limitations, and exact worktree/branch locations. Distinguish reviewed local changes, committed changes, and merged changes accurately.
