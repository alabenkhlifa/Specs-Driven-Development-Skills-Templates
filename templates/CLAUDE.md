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

## Cross-Specification Capabilities

- Treat slice numbers as identifiers, not execution order.
- Give every new or changed `tasks.md` a `## Cross-Specification Dependencies` section after `## Active Slice`, with `Requires:` and `Provides:` lists.
- Declare a requirement as ``- `capability:<name>` — provider `specs/<feature>#Task <n>` — required before `Task <n>`.`` Declare a provider as ``- `capability:<name>` — ready after `Task <n>`.`` Use `- None.` for an empty list.
- Give each capability one primary provider task and name its readiness write-back in that task's `Owned surfaces`.
- Depend on the smallest stable capability instead of an entire slice. Do not redefine the provider's schema, interface, authoritative data, or lifecycle in a consumer.
- A capability is available only after its provider task, proof, and readiness write-back are complete.
- Keep the earliest affected consumer task blocked while its capability is unavailable. Keep the slice blocked only when its next executable task is blocked.
- Update provider and consumer specifications together when a capability edge changes.
- Run `python3 .agents/scripts/validate_spec.py --all specs` after dependency changes.

## Task Size Gate

- Give every new or refined `tasks.md` a `## Task Size Gate` section after `## Cross-Specification Dependencies` and before `## Implementation Boundary`.
- Give each task exactly one size declaration: `Size: Standard` or `Size: Exception — <why splitting creates an invalid intermediate state>.`
- A standard task delivers one independently provable outcome, owns one primary state transition or invariant and normally one adapter or workflow, produces one task-boundary implementation commit, owns at most three acceptance criteria and two entities, and has focused proof expected to run in about ten minutes.
- Use 30–45 minutes as a planning target, not a promise. Expected work beyond 60 minutes or more than one meaningful implementation commit is a split signal.
- Split tasks that combine independently testable behaviors, multiple adapter integrations, domain foundation plus UI plus authentication or recovery, source-owned integration from another specification, or proof modalities that can fail independently.
- Keep full repository, production, security, and browser-matrix gates at slice verification. Use focused task proof and directly applicable safety checks unless the task owns a broader gate.
- Allow an exception only when splitting an atomic migration, transaction, or invariant would create a concrete invalid intermediate state. Complexity, convenience, chronology, or test duration is not an exception.
- Preserve completed task labels and history. When splitting unfinished work, update affected dependencies and capability references together and re-run the individual and global validators.

## Readiness And Write-Back

- Report product-requirement, technical-design, implementation, verification, and release readiness separately.
- Keep deployment-dependent evidence in a release gate when it is not needed for implementation or local verification.
- Treat an unavailable service, runtime, daemon, credential, or network as an environment blocker for the affected proof. Continue independent work and record the blocker in `tasks.md`.
- Persist accepted decisions, blockers, progress, proof results, and review checkpoints through the matching SDD workflow.
- Do not mark a slice `Verified` while a required established check is failing or unavailable without an explicit accepted exception.

## Task Planning And Traceability

- Give every acceptance criterion a stable `[AC-<n>]` ID.
- Define every data entity as a backticked-name bullet under `## Data and Access Boundaries`.
- Give every task a stable `Task <n>` label and exactly one `Depends on:` line naming earlier tasks or `none`.
- Simulate tasks in listed order before approval. Resolve every schema, interface, route, service, fixture, or earlier output first owned by a later task.
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
