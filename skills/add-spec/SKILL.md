---
name: add-spec
description: Create an initial Spec-Driven Development feature specification by inspecting the project, discovering the real users and workflow, resolving consequential product questions, and writing requirements.md, design.md, and tasks.md without implementing code. Use when a user asks to define, brainstorm, specify, plan, scope, or prepare a new feature or implementation slice, including product discovery before technologies are selected.
---

# Add Spec

Activate this skill as the workflow for creating one feature specification without implementing application code.

## Workflow

1. Read the applicable `AGENTS.md` and existing specifications.
2. Inspect the code and documentation where the feature connects.
3. Establish product behavior before architecture:
   - Identify the real user roles and their expected technical knowledge.
   - Identify entry conditions and prerequisites.
   - Map the primary workflow in the order the user experiences it.
   - Define the outcome, scope, rules, acceptance criteria, and failure behavior.
4. Separate product decisions from technology decisions. When technology is intentionally deferred, describe logical responsibilities, boundaries, interfaces, risks, and the decisions that block implementation without inventing a stack.
5. Apply a decision-ownership gate before asking a question:
   - Ask the user when the answer changes observable behavior, workflow, scope, a business rule, ownership, data handling, risk acceptance, or an acceptance outcome.
   - When alternatives preserve the accepted product outcome, record the implementation mechanism as a consolidated design question or task blocker for engineering instead of asking the user to choose it.
6. Classify every unresolved decision by the earliest readiness stage it blocks: product requirements, technical design, active-slice implementation, required verification, or deployment and release. Do not let a later-stage unknown block an earlier ready stage.
7. Resolve user-owned decisions through the Question Batching Rules below.
8. Run the Scope Health Gate before writing the specification and repeat it if discovery or design adds another workflow, integration, trust boundary, or independently verifiable outcome.
9. Stop discovery once there is enough agreement to write a useful `Draft`. Record remaining decisions under `Open Questions` instead of extending the conversation indefinitely.
10. Define the bounded feature in `requirements.md` and `design.md`, then limit `tasks.md` to the first end-to-end executable slice. Record required later behavior as deferred after the active slice, not as part of its implementation boundary.
11. Put deployment-dependent decisions and evidence that do not affect implementation or local verification in the release boundary. Keep them visible without marking the active slice `Blocked`.
12. For complex work, use Plan mode to produce and approve the proposal. Return to Default mode before writing files.
13. Copy the bundled templates from `assets/` into `specs/<feature>/` and replace every placeholder.
14. Set status by stage: keep requirements `Draft` while the product agreement is incomplete, and mark tasks `Blocked` only while a decision prevents active implementation or required verification. Never present incomplete release gates as release-ready.
15. Run `python3 .agents/scripts/validate_spec.py specs/<feature>` when the project validator exists, then manually confirm that requirements, design, tasks, proof, and scope classification agree.
16. Report the scope classification, files created, assumptions, unresolved questions with their blocked stages, active-slice boundary, and product, design, implementation, verification, and release readiness separately.

## Question Batching Rules

- Group related, independent questions that share one workflow context and readiness stage into a small batch, usually two to five questions.
- Ask one question by itself only when its answer changes the next questions, it is a foundational product fork, or a previous answer needs clarification.
- Always give one recommended answer and a brief reason for every question. When no product option can be responsibly preferred, recommend the next action, such as deferring the decision, gathering evidence, or asking the accountable owner.
- Format each batch so the user can answer every question individually or accept all recommendations together.
- Apply an answered batch as one decision set. Before asking another batch or ending the session, create or update the `Draft` with the complete batch, then validate once.
- Do not mix product discovery and technical-design questions in the same batch.

## Scope Health Gate

- Judge scope by semantic cohesion, not line count. A focused specification has one primary user or business outcome, one coherent entry-to-completion workflow, compatible ownership and data boundaries, and one executable slice that can be verified without unrelated work.
- Keep required prerequisites and handoffs together when they have no useful independent outcome. Do not split only to make files shorter.
- Split before approval when any of these are true:
  - The specification contains multiple independently valuable user outcomes or primary workflows.
  - One part can be implemented, verified, or released without the others and is not merely a prerequisite or handoff.
  - The requirements combine integrations, trust boundaries, data lifecycles, or operational responsibilities with independent failure and verification paths.
  - The document is becoming both a product feature contract and a general application-foundation, deployment, or platform handbook.
  - The active slice would require separate independent verification gates rather than one end-to-end proof.
- A shared page, actor, repository, release milestone, or broad product theme is not sufficient reason to keep independent behavior in one specification.
- Treat unusual growth in acceptance criteria, design decisions, components, or tasks compared with neighboring specifications as a review signal, not an automatic failure or numeric limit.
- When shared behavior needs an umbrella specification, keep only cross-slice rules, dependencies, and release coordination there. Create child specifications for independently executable outcomes, and do not duplicate their implementation tasks in the umbrella.
- Before writing or approving, classify the result as `focused specification`, `umbrella with child specifications`, or `split required`, and record the rationale in the report. Resolve `split required` before implementation begins.

## Discovery Rules

- Do not assume the primary user is a developer because the product concerns software or AI agents.
- Do not start from the most technically interesting capability. Follow prerequisites and the user's operational order.
- Write rules with concrete examples when naming, allocation, ownership, permissions, state transitions, or failure recovery could be interpreted more than one way.
- Distinguish stable domain identity, display labels, ownership scope, and uniqueness constraints.
- Match specificity to decision ownership. Be exact about outcomes and constraints without making requirements exhaustive about implementation mechanics.
- Use representative examples and acceptance criteria when they establish the rule. Do not expand them into a combinatorial technical test matrix.
- Consolidate related engineering unknowns into one design gate instead of asking a sequence of implementation-level questions.

## Boundaries

- Do not implement code, migrations, tests, APIs, or UI behavior.
- Do not silently decide consequential product or architecture questions.
- Do not select technologies the user intentionally deferred.
- Do not transfer engineering decision ownership to the user merely because the specification could contain more detail.
- Do not mark requirements `Approved` while the product agreement is incomplete.
- Do not mark active tasks unblocked while design, implementation, or required-verification blockers remain.
- Do not describe a feature as releasable while a release gate remains incomplete.
- Keep real specification files free of teaching labels or unexplained placeholders.

## Completion

Finish when the scope is classified and healthy, all three files exist, agree on the full feature and first active slice, pass available mechanical checks, and make the next required decision visible.
