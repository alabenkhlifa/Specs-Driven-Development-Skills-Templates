---
name: implement-spec
description: Implement and verify one approved Spec-Driven Development slice from requirements.md, design.md, and tasks.md. Use when a user asks to build an approved feature slice, continue its active tasks, or complete its verification gate while preserving scope, stop conditions, progress logs, and specification write-back.
---

# Implement Spec

Implement only the active approved slice and preserve the agreement around it.

## Preconditions

Confirm that expected behavior, design decisions, implementation boundary, task ownership, proof, and project checks are clear. Stop and use `update-spec` when a decision blocks active implementation or required verification, or when a required delivery surface is unmapped or ambiguously owned. A later deployment or release gate is not an implementation stop condition unless the requested work would cross that gate.

## Workflow

1. Read the applicable `AGENTS.md` and all three feature specification files.
2. Inspect relevant existing code and confirm ownership boundaries.
3. Preflight delivery coverage: inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active-slice requirements and design, then confirm that each has one primary task through `Owned surfaces`.
4. Stop and use `update-spec` if any required surface is unmapped or ambiguously owned. A browser check or other proof does not imply ownership of the implementation, and a final end-to-end task must not hide otherwise unassigned pages or behavior.
5. Confirm that unresolved items name the stage they block. Keep explicit deployment-only gates visible without treating them as active implementation blockers.
6. Mark the active task `In Progress`.
7. Implement one task at a time and run its attached proof.
8. Write progress, failures, discoveries, and deferred work into `tasks.md` as state changes.
9. Stop and use `update-spec` when behavior, design, scope, ownership, or blocker classification must change.
10. Run the complete verification gate.
11. Mark the slice `Verified` only when every required check passes, and report release readiness separately.

## Stop Conditions

Stop when work expands beyond the approved boundary, a missing decision affects behavior or architecture required by the active slice, a required delivery surface lacks one clear owning task, implementation conflicts with the specification, a required check fails outside the slice, or ownership overlaps another task or agent.

Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

Use sub-agents only when work separates cleanly by ownership, files, and proof. Reconcile all results and run final verification in one place.

## Boundaries

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit code.
- Do not treat proof as ownership of implementation.
- Do not hide failing checks or unresolved decisions.
- Do not mark work complete without its proof.
- Do not describe verified implementation as deployable or releasable unless its release gates also pass.

## Completion

Finish when approved behavior works, required checks pass, the specification files reflect the final implementation state, and any remaining release gate is reported explicitly.
