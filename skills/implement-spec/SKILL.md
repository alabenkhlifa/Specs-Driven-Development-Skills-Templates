---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, tasks.md, and progress.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, proof evidence, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, cross-specification capabilities, slice size, task size, proof scope, task ownership, traceability, execution order, proof, and project checks are clear. Stop and use `update-spec` when a required capability is missing, ambiguous, cyclic, unavailable, or redefined by the consumer; when an adopted slice or a new or refined task is oversized or has an unjustified exception; when proof scope is missing or unjustifiably broad; when a decision blocks active implementation or required verification; when a required delivery surface is unmapped or ambiguously owned; when an active acceptance criterion or data entity lacks task ownership; or when a task needs a surface first delivered by a later task. A later deployment or release gate is not an implementation stop condition unless the requested work would cross that gate.

## Workflow

1. Read the applicable `AGENTS.md` and the feature's `requirements.md`, `design.md`, and `tasks.md`. Read only the latest entries in `progress.md` that affect the active task, its dependencies, or current blockers.
2. Before broad code exploration, run `python3 .agents/scripts/validate_spec.py specs/<feature>`, `python3 .agents/scripts/validate_spec.py --all specs`, and `python3 .agents/scripts/split_progress_log.py --check` when available. These checks are authoritative for adopted mechanical contracts. An absent Slice Size, Task Size, or Proof Scope gate in a new or materially refined plan is a routing signal, not a pass.
3. Resolve every capability needed by the active task with `python3 .agents/scripts/capability_index.py --capability <name>` when available. Treat `ready` as a navigation result derived from the provider checkbox, not as approval; the global validator remains authoritative. Open the provider task plan only for a pending, missing, ambiguous, or unresolved capability, or when the task would change the provider-owned contract. Stop for a missing or ambiguous provider, malformed edge, cycle, incomplete provider task or proof, or consumer-owned duplicate.
4. Identify the active task as the first incomplete task in listed execution order, not the lowest numeric label. Confirm every named `Depends on:` task is complete. For a legacy task without the declaration, reconstruct its prerequisites and use `update-spec` when the ordering is not explicit enough to trust.
5. Preflight delivery coverage: inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active slice, then confirm each has one primary task through `Owned surfaces`.
6. Preflight traceability: confirm every task has exactly one `Owns:` line, every active `[AC-<n>]` criterion has exactly one owner, that owner delivers or depends only on earlier delivery of every surface needed to prove it, every active data entity has at least one owner, and every deferred or release item is classified without an active owner.
7. Preflight execution order: inspect the active task's purpose, owned surfaces, traceability items, and proof. Confirm every schema, interface, route, service, fixture, earlier result, and external capability it needs exists in the baseline, comes from an available capability, belongs to this task, or was delivered by an earlier completed task.
8. Judge the declarations whose syntax the validator checks but whose truth it cannot. Accept a slice exception only for an indivisible authority, lifecycle, or verification boundary; accept a task exception only for the recorded invalid intermediate state caused by splitting an atomic migration, transaction, or invariant; accept broad proof only when the task owns that broader gate. Confirm `validate_task_command` and its tests cover the project's broad test, build, browser, and release commands before relying on focused-proof enforcement.
9. Confirm unresolved items name the stage they block. Keep deferred and deployment-only coverage visible without treating it as active implementation work.
10. Stop and use `update-spec` if the task combines independently testable behaviors, separable adapter integrations, mixed domain foundation plus UI plus authentication or recovery, source-owned integration from another specification, independently failing proof modalities, or more than one meaningful implementation commit; if a capability, surface, traceability item, or prerequisite is missing, unavailable, unmapped, ambiguous, cyclic, or first delivered later; or if any adopted gate is false or unjustified. Record the corrected agreement and stop before implementation resumes.
11. Inspect relevant existing code and confirm ownership boundaries, scoped to the active task.
12. Preflight the services, runtimes, credentials, ports, databases, build outputs, and other mutable state required by the task proof. Treat an unavailable dependency as an environment blocker: pause the affected proof, continue independent work, surface it to the user, and record the incident in `progress.md` plus any resulting status in `tasks.md`.
13. Mark the active task `In Progress` in `tasks.md`.
14. Implement one task at a time. Run focused proof through `python3 .agents/scripts/run_proof.py task --task <n> -- <command>`; add `--broad` only for a validator-approved broad task. Record the exact successful receipt in the task's newest-first `progress.md` entry. Confirm the real exit status and never treat piped or truncated output as proof.
15. Do not run unscoped full tests, the full browser matrix, dependency installation, production proof, or repository-wide security and quality gates during focused task work unless the task owns an approved broad gate. Keep other broad checks at slice verification.
16. Write progress, failures, discoveries, proof receipts, capability readiness, and deferred work into `progress.md`; write only current task, blocker, and slice state into `tasks.md`. Keep `## Progress Log` in `tasks.md` as exactly `See [progress.md](progress.md).`
17. Stop and use `update-spec` when implementation changes behavior, design, scope, slice size, task size, proof scope, capability ownership, traceability, execution order, or blocker classification, or reveals more than one independently useful commit.
18. Run every complete verification-gate command through `python3 .agents/scripts/run_proof.py slice -- <command>` and preserve each successful receipt in `progress.md`.
19. Mark the slice `Verified` only after every task is complete, every verification item is checked, the broad slice receipt exists, and the validator passes. Report release readiness separately.

## Stop Conditions

Stop when work expands beyond the approved boundary, an adopted slice fails the Slice Size Gate or its exception is unjustified, the active task fails the Task Size Gate or its exception does not preserve an atomic invariant, its proof scope is missing or unjustifiably broad, a required capability is missing, unavailable, ambiguous, cyclic, or redefined, a missing decision affects behavior or architecture required by the active slice, a required delivery surface lacks one clear owning task, the active task depends on a surface first delivered later, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

An unavailable environment dependency, such as a stopped service, missing daemon, or absent credential, is an environment blocker, not an implementation defect. Pause the affected proofs, continue independent work, surface it to the user, and record it as environment-blocked. Verify evidence by real exit status and re-run ambiguous results; do not record a masked or piped exit code as a pass.

When delegation is available and authorized, give each sub-agent a closed brief containing the active task, decided design, hard constraints, owned paths and surfaces, exclusions, proof, and commit boundary; the main thread owns the repository-wide preflight and the sub-agent does not repeat it. Run different tasks in parallel only when dependencies, files, surfaces, proofs, ports, databases, build outputs, and other mutable runtime state are isolated. Never implement two task labels concurrently in one shared worktree; give each parallel task a short-lived branch and isolated worktree. Keep reconciliation, real-exit proof confirmation, specification write-back, and commit decisions in the main thread.

## Boundaries

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit code.
- Do not treat proof as ownership of implementation.
- Do not continue implementation after discovering that task order or an engineering mechanism must change the specification.
- Do not hide failing checks or unresolved decisions.
- Do not record a proof as passing without a verified real exit status, and do not stage another agent's concurrent changes.
- Do not bypass the proof runner when the specification has adopted `## Proof Scope Gate`, and do not use slice scope to evade a focused-task restriction.
- Do not mark work complete without its proof.
- Do not describe verified implementation as deployable or releasable unless its release gates also pass.

## Completion

Finish when approved behavior works, required checks pass, the specification files reflect the final implementation state, and any remaining release gate is reported explicitly.
