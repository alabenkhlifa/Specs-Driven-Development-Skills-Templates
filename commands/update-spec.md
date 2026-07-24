# Update Spec

## Purpose

Update an existing specification while preserving decisions that are still valid. Do not implement the change.

## Input

- Specification path or feature name
- New requirement, discovery, constraint, or decision
- Relevant current code and verification results

## Optional Plan Stage

Use a read-only planning mode when the update changes approved behavior, crosses components, invalidates an architecture decision, or has unclear consequences.

1. Read the current specification and inspect the affected system.
2. Identify which requirements, design decisions, active tasks, release gates, and checks would change.
3. Compare options and their consequences.
4. Resolve consequential user-owned decisions.
5. Produce an approved update proposal without editing files.
6. Return to a writable mode and run this workflow with the approved proposal.

Do not edit the specification or implementation while still in a read-only planning mode.

## Workflow

1. Read the current `requirements.md`, `design.md`, and `tasks.md`.
2. Inspect the code or failed check that triggered the update.
3. Classify the decision and the earliest stage it blocks: product requirements, technical design, active-slice implementation, required verification, or deployment and release.
4. Ask the user only when alternatives change observable behavior, workflow, scope, a business rule, ownership, data handling, risk acceptance, or an acceptance outcome. Keep equivalent mechanisms as engineering decisions.
5. Resolve user-owned decisions through the Question Batching Rules below.
6. After the user answers a batch, apply all accepted answers as one specification update before asking another batch or ending the session.
7. Explain the cross-file impact before editing.
8. Trace the decision through every affected surface:
   - `requirements.md`: workflow, scope, rules, acceptance criteria, and product questions.
   - `design.md`: approach, boundaries, interfaces, tradeoffs, risks, and technical questions.
   - `tasks.md`: active boundary, implementation steps, proof, verification, active blockers, release gates, deferred work, and meaningful progress state.
9. Remove resolved questions, stale blockers, contradicted wording, and invalid proof.
10. Preserve the abstraction level of the accepted answer. Do not expand a simple product decision into exhaustive implementation details.
11. Keep `tasks.md` focused on the current executable slice. Do not append a progress entry for every discovery answer when current-state sections already preserve the decision.
12. Set status by stage. Use `Draft` when the product agreement is incomplete, `Blocked` only when active implementation or verification cannot proceed, and remove `Verified` when existing proof is invalid.
13. Run available specification checks once after applying the batch and report changed decisions, blocked stages, invalidated work, and product, design, implementation, verification, and release readiness.

## Question Batching Rules

- Group related, independent questions that share one workflow context and readiness stage into a small batch, usually two to five questions.
- Ask one question by itself only when its answer changes the next questions, it is a foundational product fork, or a previous answer needs clarification.
- Always give one recommended answer and a brief reason for every question. When no product option can be responsibly preferred, recommend the next action, such as deferring the decision, gathering evidence, or asking the accountable owner.
- Format each batch so the user can answer every question individually or accept all recommendations together.
- Apply and validate the answered batch once before presenting another batch. Do not perform a separate read, write, validation, or progress-log update for each answer in the same batch.
- Do not mix product discovery and technical-design questions in the same batch.

## Status Rules

- Move requirements back to `Draft` when the product agreement becomes incomplete.
- Move tasks to `Blocked` only when an unresolved decision prevents active implementation or required verification.
- Keep deployment-only unknowns in a release gate without representing the work as releasable.
- Remove `Verified` when changed behavior is not proven by existing checks.

## Restrictions

- Do not implement the change.
- Do not rewrite unrelated parts of the specification.
- Do not remove a tradeoff without recording what replaced it.
- Do not change acceptance criteria only to make a failing implementation pass.
- Do not transfer engineering decision ownership to the user.
- Do not continue implementation while an active implementation or verification blocker remains.
- Do not let deployment-only evidence block implementation; keep it as a release gate.
- Do not grow the progress log into a transcript of the discovery conversation.

## Completion

The workflow is complete when the changed decision and proof are visible, affected files agree, stale questions are removed, `tasks.md` remains concise, available checks pass, and every readiness state is accurate.
