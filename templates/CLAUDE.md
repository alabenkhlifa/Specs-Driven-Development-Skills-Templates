# Project Instructions

## Source Of Truth

Before implementation, read the relevant files under `specs/<feature>/`:

- `requirements.md` defines expected behavior and product boundaries.
- `design.md` defines technical decisions and tradeoffs.
- `tasks.md` defines the active implementation slice and verification state.

Do not replace an explicit project decision with an assumption.

## SDD Workflows

Use the matching installed skill whenever the user's intent triggers it:

- `add-spec`: define a new feature and its first executable slice.
- `update-spec`: record changed requirements, design, scope, ownership, or verification expectations.
- `implement-spec`: implement and verify one approved active slice.
- `review-spec`: independently review implemented work, re-run its proof, and route findings without fixing them.

Execute the canonical `SKILL.md` instead of imitating it. When one request combines a new or changed specification with implementation, complete the specification workflow and stop. Begin implementation only after the agreement and active slice are approved.

## Readiness And Write-Back

- Report product-requirement, technical-design, implementation, verification, and release readiness separately.
- Keep deployment-dependent evidence in a release gate when it is not needed for implementation or local verification.
- Treat an unavailable service, runtime, daemon, credential, or network as an environment blocker for the affected proof. Continue independent work and record the blocker in `tasks.md`.
- Persist accepted decisions, blockers, progress, proof results, and review checkpoints through the matching SDD workflow.
- Do not mark a slice `Verified` while a required established check is failing or unavailable without an explicit accepted exception.

## Traceability

- Give every acceptance criterion a stable `[AC-<n>]` ID.
- Define every data entity as a backticked-name bullet under `## Data and Access Boundaries`.
- Give every task one `Owned surfaces` field and exactly one `Owns:` line.
- Assign every active criterion to exactly one task and every active data entity to at least one task.
- Classify criteria and entities outside the active slice as deferred or release coverage; do not also assign them to an active task.
- Run `python3 .agents/scripts/validate_spec.py specs/<feature>` after a specification or task-boundary change.

## Project Checks

- Tests: `<test command>`
- Build: `<build command>`
- Type check: `<type-check command>`
- Lint: `<lint command>`
- Manual or browser verification: `<verification instructions>`
