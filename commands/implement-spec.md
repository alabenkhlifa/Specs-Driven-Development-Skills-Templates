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
- No blocking product or technical questions remain.
- The active slice has an explicit implementation boundary.
- Each task has defined proof.
- Required project checks are known.

If a precondition is missing, stop and use the update-spec workflow.

## Workflow

1. Read the project instruction file and all three specification files.
2. Inspect relevant existing code before editing it.
3. Confirm files and responsibilities owned by the active slice.
4. Mark task status `In Progress`.
5. Implement one task at a time.
6. Run its attached proof before marking it complete.
7. Record progress, failed checks, discoveries, and deferred work in `tasks.md`.
8. Use the update-spec workflow when a discovery changes expected behavior, design, or scope.
9. Run the full verification gate.
10. Mark the slice `Verified` only when every required check passes.

## Stop Conditions

Stop implementation when:

- Work needs to expand beyond the approved boundary.
- A missing decision affects expected behavior or architecture.
- Implementation conflicts with acceptance criteria or the existing system.
- A required check fails for a reason outside the approved slice.
- Another task or agent owns the same files or responsibility.
- Continuing would silently change the specification.

## Parallel Work

Use sub-agents only when tasks can be separated by ownership, files, and proof. The coordinating agent remains responsible for reconciliation, full verification, and final write-back.

## Restrictions

- Do not implement unapproved scope.
- Do not change acceptance criteria to fit implementation.
- Do not hide failing checks or unresolved decisions.
- Do not mark a task complete without running its proof.
- Do not mark the slice `Verified` while required checks fail.

## Completion

The workflow is complete when approved behavior works, all required checks pass, and specification files reflect the final state.

