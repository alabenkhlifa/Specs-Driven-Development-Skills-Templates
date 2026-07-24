# Implement Spec

## Purpose

Implement and verify one approved slice from an existing specification.

## Input

- Specification path or feature name
- Approved `requirements.md`
- Approved `design.md`
- Active slice in `tasks.md`

## Preconditions

Confirm before editing code:

- Expected behavior and acceptance criteria are clear.
- No decision blocks active implementation or required verification.
- The active slice has an explicit implementation boundary.
- Each task has defined proof.
- Required project checks are known.

If a precondition is missing, stop and use the update-spec workflow.

A deployment or release gate is not an implementation blocker unless the requested work would cross that gate.

## Workflow

1. Read the project instruction file and all three specification files.
2. Inspect relevant existing code before editing it.
3. Confirm files and responsibilities owned by the active slice.
4. Confirm that unresolved items name the stage they block. Keep deployment-only gates visible without treating them as implementation blockers.
5. Mark task status `In Progress`.
6. Implement one task at a time.
7. Run its attached proof before marking it complete.
8. Record progress, failed checks, discoveries, and deferred work in `tasks.md`.
9. Use the update-spec workflow when a discovery changes expected behavior, design, scope, or blocker classification.
10. Run the full verification gate.
11. Mark the slice `Verified` only when every required check passes and report release readiness separately.

## Stop Conditions

Stop implementation when:

- Work needs to expand beyond the approved boundary.
- A missing decision affects expected behavior or architecture.
- Implementation conflicts with acceptance criteria or the existing system.
- A required check fails for a reason outside the approved slice.
- Another task or agent owns the same files or responsibility.
- Continuing would silently change the specification.

Do not stop implementation only because an explicit deployment or release gate remains incomplete. Do stop before deploying, releasing, or claiming release readiness while that gate remains incomplete.

## Parallel Work

Use sub-agents only when tasks can be separated by ownership, files, and proof. The coordinating agent remains responsible for reconciliation, full verification, and final write-back.

## Restrictions

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit implementation.
- Do not hide failing checks or unresolved decisions.
- Do not mark a task complete without running its proof.
- Do not mark the slice `Verified` while required checks fail.
- Do not describe verified implementation as deployable or releasable unless its release gates also pass.

## Completion

The workflow is complete when approved behavior works, all required checks pass, specification files reflect the implementation state, and any remaining release gate is reported explicitly.
