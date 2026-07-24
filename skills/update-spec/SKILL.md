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
4. Run the Scope Health Gate whenever the update adds or broadens an outcome, workflow, integration, trust boundary, data lifecycle, implementation boundary, or verification gate. Do not append independent work merely because the existing specification is related.
5. Apply a decision-ownership and specificity gate before asking a question:
   - Ask the user when alternatives change observable behavior, workflow, scope, a business rule, ownership, data handling, risk acceptance, or an acceptance outcome.
   - When alternatives preserve the accepted product outcome, treat the mechanism as an engineering decision and consolidate it in design open questions or task blockers instead of asking the user to choose it.
6. Resolve user-owned decisions through the Question Batching Rules below. Do not fill a material gap with an implementation assumption.
7. After the user answers a batch, apply all accepted answers as one specification update before asking another batch or ending the session.
8. For consequential or complex changes, use Plan mode to approve an update proposal. Return to Default mode before writing files.
9. Trace the decision through every affected surface:
   - `requirements.md`: workflow, scope, rules, acceptance criteria, and open questions.
   - `design.md`: logical approach, domain and access boundaries, interfaces, decisions, tradeoffs, risks, and technical questions.
   - `tasks.md`: active-slice boundary, implementation steps, proof, verification gate, active blockers, release gates, deferred work, and progress state when it materially changes.
10. Remove or replace resolved questions, stale blockers, contradicted wording, and invalid proof. Consolidate obsolete or repetitive discovery checkpoints after confirming their durable decisions live in the current requirements, design, and task state. Preserve a replaced tradeoff by recording the new choice and consequence.
11. Keep technologies deferred when the decision is still product-level. Add technical consequences as open questions instead of selecting a stack implicitly.
12. Set status by the affected stage. Move requirements to `Draft` when the product agreement becomes incomplete, move tasks to `Blocked` only when active implementation or required verification cannot proceed, and remove `Verified` whenever existing proof no longer covers the changed behavior. Keep deployment-only unknowns in an explicit release gate without representing the work as releasable.
13. Run `python3 .agents/scripts/validate_spec.py specs/<feature>` once after applying the batch when the project validator exists, then manually confirm that every changed decision, proof, and scope classification agrees across files.
14. Report the scope classification, changed decisions, newly exposed questions with their blocked stages, invalidated or deferred work, status changes, and product, design, implementation, verification, and release readiness separately.

## Question Batching Rules

- Group related, independent questions that share one workflow context and readiness stage into a small batch, usually two to five questions.
- Ask one question by itself only when its answer changes the next questions, it is a foundational product fork, or a previous answer needs clarification.
- Always give one recommended answer and a brief reason for every question. When no product option can be responsibly preferred, recommend the next action, such as deferring the decision, gathering evidence, or asking the accountable owner.
- Format each batch so the user can answer every question individually or accept all recommendations together.
- Apply and validate the answered batch once before presenting another batch. Do not perform a separate read, write, validation, or progress-log update for each answer in the same batch.
- Do not mix product discovery and technical-design questions in the same batch.

## Scope Health Gate

- Reassess semantic cohesion, not just file size. The specification remains focused only while its behavior supports one primary outcome and coherent workflow with compatible ownership, data, implementation, and verification boundaries.
- Keep required prerequisites and handoffs together when they have no useful independent outcome. Do not split completed work merely to reduce line count.
- Narrow or split when an update introduces an independently valuable workflow, a separately implementable or verifiable outcome, an unrelated integration or trust boundary, an independent data lifecycle, or a separate release and failure path.
- A shared page, actor, repository, release milestone, or broad product theme does not justify appending independent work to the same specification.
- Treat unusual growth in acceptance criteria, design decisions, components, or tasks compared with neighboring specifications as a review signal. Counts trigger inspection; they are not hard limits.
- If an existing specification has become an umbrella, retain only its shared rules, dependencies, completed history, and release coordination. Use `update-spec` to narrow its active boundary, then use `add-spec` for each unfinished independently executable child. Do not duplicate tasks or rewrite verified history.
- Classify the result as `focused specification`, `umbrella with child specifications`, or `split required`. A `split required` result blocks new implementation until the unfinished work has a focused active slice.

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
- Do not grow a specification across a scope-health split trigger merely because the new behavior is related to the existing feature.

## Completion

Finish when the scope is classified and healthy, the changed decision and its proof are visible, affected files agree, stale questions and blockers are removed, `tasks.md` remains a concise representation of the current executable state, available mechanical checks pass, and implementation state is accurate.
