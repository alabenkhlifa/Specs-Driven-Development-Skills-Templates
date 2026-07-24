# Add Spec

## Purpose

Create an initial specification for one feature and its first executable slice without implementing application code.

## Input

- Feature description supplied by the user
- Relevant existing code, documentation, specifications, and project instructions

## Optional Plan Stage

For complex, ambiguous, or cross-cutting changes:

1. Enter the agent's read-only planning mode.
2. Inspect the existing system and establish the users, prerequisites, workflow, and product boundary.
3. Resolve consequential user-owned questions without creating or editing files.
4. Produce a proposed specification and readiness assessment.
5. Return to a writable mode.
6. Run this workflow with the proposal as input.

Do not claim that specification files were created while the agent is still in a read-only planning mode.

## Workflow

1. Read the project instruction file and related existing specifications.
2. Inspect the current system where the feature will connect.
3. Establish product behavior before architecture:
   - Identify the real users and their expected technical knowledge.
   - Identify entry conditions and prerequisites.
   - Map the primary workflow in the order the user experiences it.
   - Define the outcome, scope, rules, acceptance criteria, and failure behavior.
4. Separate product decisions from technology decisions. When technology is intentionally deferred, describe logical responsibilities, boundaries, interfaces, risks, and implementation blockers without inventing a stack.
5. Ask the user when the answer changes observable behavior, workflow, scope, a business rule, ownership, data handling, risk acceptance, or an acceptance outcome. Keep equivalent implementation mechanisms as engineering decisions.
6. Classify every unresolved decision by the earliest stage it blocks: product requirements, technical design, active-slice implementation, required verification, or deployment and release.
7. Resolve user-owned decisions through the Question Batching Rules below. Stop discovery when there is enough agreement for a useful `Draft`.
8. Create `specs/<feature>/requirements.md`, `design.md`, and `tasks.md` from the bundled templates.
9. Define the full bounded feature in requirements and design. Keep `tasks.md` limited to the first end-to-end executable slice and record later work as deferred.
10. Keep deployment-dependent evidence that is not needed for implementation or local verification in the release boundary.
11. Set status by stage: requirements remain `Draft` while the product agreement is incomplete, and tasks are `Blocked` only when active implementation or required verification cannot proceed.
12. Run available specification checks and report assumptions, unresolved questions with their blocked stages, the active boundary, and readiness for product, design, implementation, verification, and release.

## Question Batching Rules

- Group related, independent questions that share one workflow context and readiness stage into a small batch, usually two to five questions.
- Ask one question by itself only when its answer changes the next questions, it is a foundational product fork, or a previous answer needs clarification.
- Always give one recommended answer and a brief reason for every question. When no product option can be responsibly preferred, recommend the next action, such as deferring the decision, gathering evidence, or asking the accountable owner.
- Format each batch so the user can answer every question individually or accept all recommendations together.
- Apply an answered batch as one decision set. Before asking another batch or ending the session, create or update the `Draft` with the complete batch, then validate once.
- Do not mix product discovery and technical-design questions in the same batch.

## Restrictions

- Do not implement application code.
- Do not create migrations, tests, API behavior, or UI changes.
- Do not resolve consequential product or architecture decisions silently.
- Do not ask the user to choose engineering mechanisms that preserve the accepted product outcome.
- Do not mark requirements `Approved` while the product agreement is incomplete.
- Do not mark active tasks unblocked while design, implementation, or required-verification blockers remain.
- Do not describe the feature as releasable while a release gate remains incomplete.

## Completion

The workflow is complete when all three files agree on the feature and first active slice, available checks pass, and every remaining decision and blocked stage is visible.
