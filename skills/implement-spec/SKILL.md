---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, and tasks.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, progress logs, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, cross-specification capabilities, slice size, task size, proof scope, task ownership, traceability, execution order, proof, and project checks are clear. Stop and use `update-spec` when a required capability is missing, ambiguous, cyclic, unavailable, or redefined by the consumer; when an adopted slice or a new or refined task is oversized or has an unjustified exception; when proof scope is missing or unjustifiably broad; when a decision blocks active implementation or required verification; when a required delivery surface is unmapped or ambiguously owned; when an active acceptance criterion or data entity lacks task ownership; or when a task needs a surface first delivered by a later task. A later deployment or release gate is not an implementation stop condition unless the requested work would cross that gate.

## Workflow

1. Read the applicable `AGENTS.md` and all three feature specification files.
2. Read `## Cross-Specification Dependencies`, inspect every required provider specification and task, and confirm each capability needed by the active task is available. Run the global dependency validator when the repository provides one. Stop for a missing or ambiguous provider, malformed edge, cycle, incomplete provider task or proof, or consumer-owned duplicate of the provider contract.
3. Read `## Slice Size Gate` when present. Confirm a standard slice contains at most 12 tasks and its longest `Depends on:` path contains at most 8; accept an exception only for the recorded indivisible authority, lifecycle, or verification boundary. Route an oversized or unjustified adopted slice to `update-spec`; do not retrofit a legacy active slice solely to add the gate.
4. Read `## Task Size Gate` when present and inspect the active task's `Size:` line. Confirm a standard task has one independently provable outcome, one primary state transition or invariant, normally one adapter or workflow and one task-boundary implementation commit, no more than three acceptance criteria and two entities, and focused proof. Accept an exception only when splitting an atomic migration, transaction, or invariant would create the recorded invalid intermediate state. Route a new or refined plan without this gate to `update-spec`.
5. Read `## Proof Scope Gate` when present. Confirm the active task is covered by its `Applies to:` declaration and has exactly one `Proof scope:` line. Treat `Broad` as an exception that is valid only when the recorded reason shows the task owns that broader gate. Confirm `validate_task_command` and its tests cover the project's broad test, build, browser, and release commands; an unadapted runner is an implementation blocker unless its included policy already covers the stack. Route a missing, malformed, or unjustified declaration to `update-spec`.
6. Identify the active task as the first incomplete task in listed execution order, not the lowest numeric label. Read its `Depends on:` line when present and confirm every named task is complete. For a legacy task without the declaration, reconstruct its prerequisites and use `update-spec` when the ordering is not explicit enough to trust.
7. Preflight delivery coverage: inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active-slice requirements and design, then confirm that each has one primary task through `Owned surfaces`.
8. Preflight traceability: confirm every task has exactly one `Owns:` line, every active `[AC-<n>]` criterion has exactly one task owner, that owner delivers or depends only on earlier delivery of every surface needed to prove the criterion, every active data entity has at least one task owner, and every deferred or release criterion and entity is classified in the implementation boundary without an active owner.
9. Preflight execution order before broad code exploration: inspect the active task's purpose, owned surfaces, traceability items, and proof; identify every schema, interface, route, service, fixture, earlier task output, and external capability it needs; then confirm each prerequisite exists in the baseline, an available named capability, the same task, or an earlier completed task.
10. Stop and use `update-spec` if the active task combines independently testable behaviors, multiple separable adapter integrations, distinct delivery channels, authorization boundaries, lifecycle clocks, mixed domain foundation plus UI plus authentication or recovery, source-owned integration from another specification, independently failing proof modalities, or work expected to need more than one meaningful implementation commit; if any required capability, surface, or active traceability item is missing, unavailable, unmapped, ambiguously owned, or cyclic; or if the active task has a forward dependency. Do not ask the user to choose an implementation mechanism and then continue coding. Complete the specification update and stop; resume implementation only in a later request after the repository contract records the decision. A browser check or other proof does not imply ownership of its implementation.
11. Confirm that unresolved items name the stage they block. Keep explicit deferred and deployment-only coverage visible without treating it as active implementation work.
12. Run the specification validator when the project provides one. Do not begin implementation while its active-slice ownership, slice-size, task-size, proof-scope, traceability, task dependency, or capability graph checks fail.
13. Inspect relevant existing code and confirm ownership boundaries. Keep this exploration scoped to the active task now that the agreement is ready.
14. Preflight environment readiness: confirm the external dependencies, services, runtimes, and credentials the task proofs require are available. When one is unavailable, treat it as an environment blocker, not an implementation defect: pause only the affected proofs, continue independent work, surface it to the user, and record it in `tasks.md` as environment-blocked.
15. Mark the active task `In Progress`.
16. Implement one task at a time. When the proof-scope contract is active, run every focused proof command through `python3 .agents/scripts/run_proof.py task --task <n> -- <command>`; add `--broad` before `--` only for a validator-approved broad task declaration. Paste each successful receipt into the progress log. Otherwise run focused proof plus directly applicable safety checks. In both cases, confirm real exit status and never treat piped or truncated output as proof. Reconciliation does not authorize a full-suite rerun.
17. Do not run unscoped full tests, the full browser matrix, dependency installation, production proof, or repository-wide security and quality gates during a focused task. Use a documented `Broad` proof scope only when the task itself owns that gate. Keep all other broad checks at slice verification.
18. Write progress, failures, discoveries, proof receipts, capability readiness, and deferred work into `tasks.md` as state changes.
19. Stop and use `update-spec` when implementation reveals more than one independently useful commit or behavior, or when behavior, design, scope, slice size, task size, proof scope, capability ownership, traceability, execution order, or blocker classification must change.
20. Run every complete verification-gate command through `python3 .agents/scripts/run_proof.py slice -- <command>` and preserve its successful receipt.
21. Mark the slice `Verified` only when every required check passes, and report release readiness separately.

## Stop Conditions

Stop when work expands beyond the approved boundary, an adopted slice fails the Slice Size Gate or its exception is unjustified, the active task fails the Task Size Gate or its exception does not preserve an atomic invariant, its proof scope is missing or unjustifiably broad, a required capability is missing, unavailable, ambiguous, cyclic, or redefined, a missing decision affects behavior or architecture required by the active slice, a required delivery surface lacks one clear owning task, the active task depends on a surface first delivered later, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

An unavailable environment dependency, such as a stopped service, missing daemon, or absent credential, is an environment blocker, not an implementation defect. Pause the affected proofs, continue independent work, surface it to the user, and record it as environment-blocked. Verify evidence by real exit status and re-run ambiguous results; do not record a masked or piped exit code as a pass.

Delegate task development to a sub-agent by default when the environment supports it, with explicit ownership and a brief containing the decided design and hard constraints. Run sub-agents in parallel only when work separates cleanly by dependencies, files, surfaces, proof, and runtime state. Never implement two task labels concurrently in one shared worktree; give each parallel task a short-lived branch, isolated worktree, and distinct local-server port when needed. Keep orchestration, review, real-exit proof reconciliation, specification write-back, and commit decisions in the main thread. Execute the task commit in its owning worktree, then merge that task branch into the single slice branch.

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
