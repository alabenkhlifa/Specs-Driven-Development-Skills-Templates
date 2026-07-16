---
name: update-spec
description: Update an existing Spec-Driven Development specification when requirements, scope, business rules, architecture decisions, implementation boundaries, or verification expectations change. Use when implementation or review reveals a missing or changed decision that must be recorded before coding continues. Do not implement the change.
---

# Update Spec

Restore agreement between requirements, design, tasks, and proof without implementing the change.

## Workflow

1. Read the applicable `AGENTS.md` and the feature's `requirements.md`, `design.md`, and `tasks.md`.
2. Inspect the code, discovery, or failed check that triggered the update.
3. Classify the affected decisions and explain the impact before editing.
4. For consequential or ambiguous changes, use Plan mode to approve an update proposal. Return to Default mode before writing files.
5. Update only affected sections and keep related decisions, tasks, and checks aligned.
6. Move status to `Draft` or `Blocked` when unresolved decisions remain.
7. Remove `Verified` when existing checks no longer prove the changed behavior.
8. Record invalidated or deferred work and report whether implementation can resume.

## Boundaries

- Do not implement application changes.
- Do not rewrite unrelated specification sections.
- Do not erase a tradeoff without recording its replacement.
- Do not weaken acceptance criteria to make failing code pass.

## Completion

Finish when the changed decision is visible, affected files agree, and implementation state is accurate.

