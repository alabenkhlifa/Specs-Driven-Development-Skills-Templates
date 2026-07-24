---
name: review-spec
description: Independently review the implementation of one Spec-Driven Development slice against its approved requirements.md, design.md, and tasks.md, re-running each completed task's proof and the verification gate, then reporting evidence-based findings and routing fixes without changing the implementation or the agreement. Use when a user asks to review, audit, verify, or second-check a slice another agent implemented, or to check for missed behavior, scope drift, privacy or security gaps, or needed refactoring before the slice is trusted.
---

# Review Spec

Activate this skill to review an implemented slice against its specification as an independent second agent. Report and route; do not implement fixes or rewrite the agreement.

## Preconditions

- Confirm the target `specs/<feature>/` exists, then identify the active slice, its task-owned acceptance criteria and data entities, its deferred and release classifications, and the tasks it claims complete.
- Prefer running as a different agent than the one that implemented the slice. Self-review is allowed but must apply the same evidence standard.
- Confirm the canonical project checks are available. When a required proof cannot run in this environment, report it as unverified rather than assume it passes.
- Inspect the working tree first. Treat existing uncommitted changes as intentional work from the user or another agent and do not modify or revert them.

## Workflow

1. Read the applicable `AGENTS.md` and all three specification files for the target slice.
2. Establish the contract under review: the active-slice boundary, each task's purpose, `Owned surfaces`, `Owns:` traceability items, and proof; the verification gate; and the privacy, security, and no-analytics commitments. Keep deferred criteria and entities outside the implementation verdict, and assess release-classified items only against their release gate.
3. Inspect the actual implementation for every task claimed complete: code, tests, migrations, configuration, and generated assets. Map each task-owned acceptance criterion, data entity, and owned surface to the code that satisfies it.
4. Verify by re-running evidence, not by trusting claims: re-run each completed task's attached proof and the verification-gate commands. Record the exact command, its result, and any environment-only gaps.
5. Assess every Review Dimension below and collect findings.
6. Classify and report findings by severity, each mapped to its acceptance criterion, task, or owned surface, with `file:line` and one recommended action and route.
7. Route, do not resolve: send implementation defects back to the implementer or to `implement-spec`, and send agreement changes to `update-spec`. Do not edit application code, tests, or the specification's agreement to make the review pass.
8. Write back the outcome: append a dated `Review checkpoint` to the target `tasks.md` progress log with the verdict, the re-run evidence, and required follow-ups, and record genuine blockers under `Blocked Decisions`. Do not flip task checkboxes or the slice status; the owning workflow or the user acts on the findings.
9. Report the verdict, the re-run evidence, the findings by severity, and product, implementation, verification, and release readiness separately.

## Review Dimensions

- Correctness: the implementation does what the requirements and design specify, including the failure behavior and edge cases the spec names.
- Completeness: every task-owned acceptance criterion, data entity, and owned surface for the reviewed tasks is implemented and proved; nothing claimed complete is partial, and deferred or release coverage is not misreported as active work.
- Scope adherence: nothing is built outside the active-slice boundary, and nothing inside the boundary was silently skipped or deferred without record.
- Proof and gate integrity: each completed task's proof and the verification gate actually reproduce; claimed-passing checks are not stale, skipped, weakened, or falsely reported.
- Privacy and security: schemas, logs, caches, backups, exports, workers, and processors honor the GDPR data contract, minimization, retention, least privilege, secret isolation, and the no-analytics rule.
- Spec-to-code drift: the code, acceptance criteria, and existing system agree; where they disagree, the disagreement is reported, not silently reconciled.
- Quality and maintainability: boundaries, naming, duplication, and structure are sound; record refactoring that materially reduces risk, and mark optional polish as such.

## Findings And Severity

- Blocker: violates an acceptance criterion, the scope boundary, a privacy or security commitment, or a completed task whose proof does not reproduce.
- Major: a real defect, missing required coverage, or drift that must be fixed before the slice is trusted, even when no gate currently fails.
- Minor: maintainability, clarity, or refactoring that should be addressed but does not block.
- Nit: optional polish with no correctness or risk impact.
- Give every finding a concrete failure or gap, its location, and one recommended action with its route.

## Stop Conditions

- Stop and route to `update-spec` when the code and the agreement disagree and the correct resolution would change requirements, scope, a business rule, design, or an acceptance criterion.
- Stop and route to the implementer or `implement-spec` when a fix requires writing or changing application code, tests, migrations, or configuration.
- Stop when the review needs a product, security, or privacy decision the user owns.
- Do not resolve a disagreement between agents unilaterally; report it with a recommendation and let the owning workflow or the user decide.

## Boundaries

- Do not implement or edit application code, tests, migrations, or configuration.
- Do not change requirements, design, acceptance criteria, or task scope to make the implementation pass.
- Do not mark the slice `Verified`, unblock tasks, or claim release readiness.
- Do not accept a check as passing without evidence; report unrunnable proofs as unverified.
- Keep deployment-only gates as release blockers without treating them as active implementation defects.
- Do not create new Markdown files unless the user requests them; record the review in the existing `tasks.md`.

## Completion

Finish when every reviewed task and its task-owned acceptance criteria, data entities, and surfaces have been checked against the implementation with re-run evidence, findings are classified and routed, the `Review checkpoint` and any blockers are written to `tasks.md`, and the verdict and separate readiness states are reported.
