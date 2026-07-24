---
name: update-spec
description: Update an existing Spec-Driven Development specification when a user clarifies or resolves an open question, or when requirements, scope, business rules, architecture decisions, implementation boundaries, acceptance criteria, or verification expectations change. Use during discovery, review, implementation feedback, or failed verification when the agreement must change before coding continues. Do not implement the change.
---

# Update Spec

Activate this skill as the workflow for restoring agreement between requirements, design, tasks, and proof without implementing the change.

## Workflow

1. Read the applicable `AGENTS.md` and the feature's `requirements.md`, `design.md`, and `tasks.md`.
2. Inspect the code, discovery, or failed check that triggered the update.
3. Classify the affected decision, such as user, workflow, scope, business rule, identity, ownership, state, acceptance criterion, architecture, task boundary, or proof. Identify the earliest readiness stage it blocks: product requirements, technical design, active-slice implementation, required verification, or deployment and release. Explain the cross-file impact before editing.
4. Apply a decision-ownership and specificity gate before asking a question:
   - Ask the user when alternatives change observable behavior, workflow, scope, a business rule, ownership, data handling, risk acceptance, or an acceptance outcome.
   - When alternatives preserve the accepted product outcome, treat the mechanism as an engineering decision and consolidate it in design open questions or task blockers instead of asking the user to choose it.
5. Ask one consequential user-owned question at a time when the requested change remains ambiguous. Do not fill a material gap with an implementation assumption.
6. For consequential or complex changes, use Plan mode to approve an update proposal. Return to Default mode before writing files.
7. Trace the decision through every affected surface:
   - `requirements.md`: workflow, scope, rules, acceptance criteria, and open questions.
   - `design.md`: logical approach, domain and access boundaries, interfaces, decisions, tradeoffs, risks, and technical questions.
   - `tasks.md`: active-slice boundary, implementation steps, proof, verification gate, active blockers, release gates, deferred work, and progress state when it materially changes.
8. Remove or replace resolved questions, stale blockers, contradicted wording, and invalid proof. Consolidate obsolete or repetitive discovery checkpoints after confirming their durable decisions live in the current requirements, design, and task state. Preserve a replaced tradeoff by recording the new choice and consequence.
9. Keep technologies deferred when the decision is still product-level. Add technical consequences as open questions instead of selecting a stack implicitly.
10. Set status by the affected stage. Move requirements to `Draft` when the product agreement becomes incomplete, move tasks to `Blocked` only when active implementation or required verification cannot proceed, and remove `Verified` whenever existing proof no longer covers the changed behavior. Keep deployment-only unknowns in an explicit release gate without representing the work as releasable.
11. Run `python3 .agents/scripts/validate_spec.py specs/<feature>` when the project validator exists, then manually confirm that every changed decision agrees across files.
12. Report the changed decisions, newly exposed questions with their blocked stages, invalidated or deferred work, status changes, and product, design, implementation, verification, and release readiness separately.

## Decision Rules

- Distinguish stable domain identity, display labels, ownership scope, and uniqueness constraints.
- Add concrete examples when rules involve naming, allocation, permissions, state transitions, ordering, or recovery.
- Add concurrency, security, or failure implications only when they follow from the decision; keep unselected implementation details open.
- Preserve the abstraction level of an accepted answer. Do not expand a simple business decision into implementation edge cases unless new evidence makes them product-significant.
- Prefer one consolidated engineering question or blocker to enumerating algorithms, normalization rules, storage representations, or exhaustive technical edge cases.
- Keep acceptance criteria representative and observable rather than turning them into a complete technical test matrix.
- Name the earliest blocked stage for every unresolved item. A decision that affects only deployment or release must not block implementation or local verification when their contract is already stable.

## tasks.md State Discipline

- Write every accepted decision back immediately, but place the durable decision in the current requirements, design, active boundary, blockers, or proof rather than relying on chronology.
- Do not append a progress-log entry for every discovery answer or clarification. The progress log is not a conversation transcript and must not duplicate decisions already visible in current-state sections.
- Add or update progress only for meaningful implementation movement, a verification result or invalidation, a specification status transition, or a consolidated discovery checkpoint that materially changes readiness or scope.
- During an active discovery thread, update one current checkpoint in place or omit a progress entry when the changed current-state sections already provide a complete handoff.
- Keep `tasks.md` limited to the current executable slice. Put future work in concise deferred boundaries or a separate specification instead of expanding the active task list.
- Keep deployment-dependent evidence in a release gate when it is not required by the active implementation or verification contract.
- When repetitive discovery history already exists, consolidate it without removing failed-check evidence, completed implementation history, or decisions that are not represented elsewhere.

## Boundaries

- Do not implement application changes.
- Do not rewrite unrelated specification sections.
- Do not erase a tradeoff without recording its replacement.
- Do not weaken acceptance criteria to make failing code pass.
- Do not mark implementation as resumable while an unresolved decision blocks product agreement, technical design, active-slice implementation, or required verification.
- Do not let deployment-only evidence block implementation; preserve it as a release gate and do not claim release readiness.
- Do not transfer engineering decision ownership to the user merely because the specification could contain more detail.
- Do not grow `tasks.md` merely to prove that each conversational turn was written back.

## Completion

Finish when the changed decision and its proof are visible, affected files agree, stale questions and blockers are removed, `tasks.md` remains a concise representation of the current executable state, available mechanical checks pass, and implementation state is accurate.
