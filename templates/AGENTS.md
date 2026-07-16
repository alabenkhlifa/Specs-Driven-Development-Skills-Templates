# Project Instructions

## Source of Truth

Before implementation, read the relevant files under `specs/<feature>/`:

- `requirements.md` defines expected behavior and product boundaries.
- `design.md` defines technical decisions and tradeoffs.
- `tasks.md` defines the active implementation slice and verification state.

Do not replace an explicit project decision with an assumption.

## Implementation Workflow

1. Confirm that requirements and design contain no blocking open questions.
2. Work only from the active slice in `tasks.md`.
3. Keep changes inside its implementation boundary.
4. Run the proof attached to each task before marking it complete.
5. Run the full verification gate before calling the slice complete.
6. Write progress and new decisions back to the spec files.

## Stop Conditions

Stop implementation and report the issue when:

- The requested change expands the approved scope.
- A missing business rule or design decision affects implementation.
- The code, acceptance criteria, and existing system disagree.
- A required check fails and cannot be fixed inside the approved slice.
- Another task or agent is changing the same ownership area.

Do not continue by silently choosing a new product or architecture decision.

## Write-Back Rules

- Update `requirements.md` when expected behavior, scope, or a business rule changes.
- Update `design.md` when a technical decision or tradeoff changes.
- Update `tasks.md` when progress, verification state, or deferred work changes.

Keep decisions in project files, not only in the conversation.

## Project Checks

- Tests: `<test command>`
- Build: `<build command>`
- Type check: `<type-check command>`
- Lint: `<lint command>`
- Manual or browser verification: `<verification instructions>`

Do not mark the slice `Verified` while a required check is failing.

