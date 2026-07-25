---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, and tasks.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, progress logs, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, task ownership, traceability, execution order, proof, and project checks are clear. Stop and use `update-spec` when a decision blocks active implementation or required verification, when a required delivery surface is unmapped or ambiguously owned, when an active acceptance criterion or data entity lacks task ownership, or when a task needs a surface first delivered by a later task. A later deployment or release gate is not an implementation stop condition unless the requested work would cross that gate.

## Workflow

1. Read the applicable `AGENTS.md` and all three feature specification files.
2. Identify the active task. Read its `Depends on:` line when present and confirm every named task is complete. For a legacy task without the declaration, reconstruct its prerequisites and use `update-spec` when the ordering is not explicit enough to trust.
3. Preflight delivery coverage: inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active-slice requirements and design, then confirm that each has one primary task through `Owned surfaces`.
4. Preflight traceability: confirm every task has exactly one `Owns:` line, every active `[AC-<n>]` criterion has exactly one task owner, every active data entity has at least one task owner, and every deferred or release criterion and entity is classified in the implementation boundary without an active owner.
5. Preflight execution order before broad code exploration: inspect the active task's purpose, owned surfaces, traceability items, and proof; identify every schema, interface, route, service, fixture, and prior task output it needs; then confirm each prerequisite exists in the baseline or is delivered by the same task or an earlier completed task.
6. Stop and use `update-spec` if any required surface or active traceability item is unmapped or ambiguously owned, or if the active task has a forward dependency. Do not ask the user to choose an implementation mechanism and then continue coding. Complete the specification update and stop; resume implementation only in a later request after the repository contract records the decision. A browser check or other proof does not imply ownership of the implementation, and a final end-to-end task must not hide otherwise unassigned pages or behavior.
7. Confirm that unresolved items name the stage they block. Keep explicit deferred and deployment-only coverage visible without treating it as active implementation work.
8. Run the specification validator when the project provides one. Do not begin implementation while its active-slice ownership, traceability, or dependency checks fail.
9. Inspect relevant existing code and confirm ownership boundaries. Keep this exploration scoped to the active task now that the agreement is ready.
10. Preflight environment readiness: confirm the external dependencies, services, runtimes, and credentials the task proofs require are available. When one is unavailable, treat it as an environment blocker, not an implementation defect: pause only the affected proofs, continue independent work, surface it to the user, and record it in `tasks.md` as environment-blocked.
11. Mark the active task `In Progress`.
12. Implement one task at a time and run its attached proof. Check each proof's real exit status; do not trust output piped through `tail`, `head`, or `grep`, which mask the command's exit code, and re-run any ambiguous result before recording pass or fail. Record a multi-command proof per sub-proof, distinguishing passed from environment-blocked, and mark a task complete only when every sub-proof passes.
13. Write progress, failures, discoveries, and deferred work into `tasks.md` as state changes.
14. Stop and use `update-spec` when behavior, design, scope, ownership, traceability, execution order, or blocker classification must change.
15. Run the complete verification gate.
16. Mark the slice `Verified` only when every required check passes, and report release readiness separately.

## Stop Conditions

Stop when work expands beyond the approved boundary, a missing decision affects behavior or architecture required by the active slice, a required delivery surface lacks one clear owning task, the active task depends on a surface first delivered later, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

An unavailable environment dependency, such as a stopped service, missing daemon, or absent credential, is an environment blocker, not an implementation defect. Pause the affected proofs, continue independent work, surface it to the user, and record it as environment-blocked. Verify evidence by real exit status and re-run ambiguous results; do not record a masked or piped exit code as a pass.

Use sub-agents only when work separates cleanly by ownership, files, and proof. Reconcile all results and run final verification in one place.

## Boundaries

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit code.
- Do not treat proof as ownership of implementation.
- Do not continue implementation after discovering that task order or an engineering mechanism must change the specification.
- Do not hide failing checks or unresolved decisions.
- Do not record a proof as passing without a verified real exit status, and do not stage another agent's concurrent changes.
- Do not mark work complete without its proof.
- Do not describe verified implementation as deployable or releasable unless its release gates also pass.

## Completion

Finish when approved behavior works, required checks pass, the specification files reflect the final implementation state, and any remaining release gate is reported explicitly.
