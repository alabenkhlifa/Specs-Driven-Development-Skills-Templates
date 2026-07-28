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
12. Run the Cross-Specification Capability Gate, Task Size Gate, then the Delivery Coverage and Sequence Gate before completing the task plan.
13. For complex work, use Plan mode to produce and approve the proposal. Return to Default mode before writing files.
14. Copy the bundled templates from `assets/` into `specs/<feature>/` and replace every placeholder.
15. Set status by stage: keep requirements `Draft` while the product agreement is incomplete, and mark tasks `Blocked` while an unavailable required capability, decision, or design gap prevents active implementation or required verification. Never present incomplete release gates as release-ready.
16. Run `python3 .agents/scripts/validate_spec.py specs/<feature>` and the repository's global dependency validator when available, then manually confirm that requirements, design, tasks, proof, scope classification, capability ownership, task size, delivery coverage, and task sequence agree.
17. Report the scope classification, capability graph result, task-size result and exceptions, delivery-coverage and sequence result including any missing provider, cycle, oversized task, unmapped, ambiguous, or forward-dependent surface, files created, assumptions, unresolved questions with their blocked stages, active-slice boundary, and product, design, implementation, verification, and release readiness separately.

## Question Batching Rules

- Before asking, check the existing specifications and recorded project decisions; do not ask for a decision that is already recorded.
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

## Cross-Specification Capability Gate

- Treat slice numbers as identifiers, not execution order.
- Add `## Cross-Specification Dependencies` after `## Active Slice` with `Requires:` and `Provides:` lists.
- Declare a requirement as ``- `capability:<name>` — provider `specs/<feature>#Task <n>` — required before `Task <n>`.`` Declare a provider as ``- `capability:<name>` — ready after `Task <n>`.`` Use `- None.` for an empty list.
- Give each capability one primary provider task. Depend on the smallest stable capability instead of a whole slice when possible.
- Inspect every named provider and consumer contract. Reject missing or ambiguous providers, malformed task references, cycles, and consumers that redefine the provider's schema, interface, authoritative data, or lifecycle.
- Keep the earliest affected task `Blocked` while a required provider task is incomplete. Keep the slice `Blocked` only when its next executable task is blocked; later unavailable capabilities do not block independent earlier tasks. A capability is ready only after the named provider task, its proof, and its readiness write-back are complete.
- Run the repository's global dependency validator when available. When an edge changes, update provider and consumer specifications together.

## Task Size Gate

- Add `## Task Size Gate` after `## Cross-Specification Dependencies` and before `## Implementation Boundary`. Give every task exactly one `Size:` line: `Size: Standard` or `Size: Exception — <why splitting creates an invalid intermediate state>.`
- A standard task delivers one independently provable outcome, owns one primary state transition or invariant and normally one adapter or workflow, produces one task-boundary implementation commit, owns at most three acceptance criteria and two entities, and has focused proof expected to run in about ten minutes.
- Use 30–45 minutes as a planning target, not a promise. Treat expected work beyond 60 minutes or more than one meaningful implementation commit as a split signal.
- Split when a task combines independently testable behaviors, multiple adapter integrations, domain foundation plus UI plus authentication or recovery, source-owned integration from another specification, or several proof modalities that can fail independently.
- Keep full repository, production, security, and browser-matrix gates at slice verification. Attach only focused proof and directly applicable safety checks to an implementation task unless that task specifically owns the broader gate.
- Allow an exception only when splitting an atomic migration, transaction, or invariant would create an invalid intermediate state. Complexity, convenience, or a long test suite is not an exception. Record the concrete invalid state in the task's `Size:` line.
- Do not split by technical layer when doing so would leave an unusable or unprovable intermediate result. Prefer the smallest coherent vertical or invariant-preserving unit.

## Delivery Coverage And Sequence Gate

- Inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active-slice requirements and design.
- Assign every surface to one primary implementation task through its `Owned surfaces` field. A surface is not covered when it appears only in purpose, proof, acceptance criteria, or the verification gate.
- Prefer vertical workflow tasks that own user-visible UI and its supporting logic together when they can be implemented and proved through one coherent scenario.
- A final end-to-end task integrates and verifies surfaces already owned elsewhere; it must not silently own all otherwise unassigned pages or behavior.
- After assigning surfaces, simulate the tasks in listed order. For each task, inspect its purpose, owned surfaces, traceability items, and proof, then identify every schema, interface, route, service, fixture, and earlier task output it needs.
- Require every prerequisite to exist in the baseline or be delivered by the same task or an earlier task. When the task itself introduces a prerequisite, name that artifact in `Owned surfaces` and cover it in the task proof. A surface first delivered by a later task is a forward dependency even when eventual ownership and traceability are complete.
- Resolve each forward dependency by moving the foundation to the earliest consumer, defining an explicit stable early contract plus a later additive extension, reordering the tasks, or blocking the affected task. Do not leave the decision for implementation-time clarification.
- Prefer decomposing a large foundational or bootstrap task into smaller provable units, and give each task a proof whose sub-proofs can be recorded and verified independently, so partial and environment-blocked progress stays trackable.
- Resolve every unmapped or ambiguously owned surface before completion, or record it as an active implementation blocker.
- Give every task a stable `Task <n>` label and never renumber or reuse it. Add exactly one `Depends on:` line naming earlier task labels or `none`. Treat this declaration as navigation and validator input, not as a substitute for the semantic sequence simulation.
- Give every acceptance criterion a stable `[AC-<n>]` ID and never renumber or reuse it; a new criterion takes the next unused integer. List every `## Data and Access Boundaries` data entity as a bullet that begins with its backticked name and a colon (`` - `EntityName`: ... ``); that name is its traceability ID.
- Declare active coverage on every task with exactly one `Owns:` line naming the `AC-<n>` IDs and `entity:<Name>` items it is accountable for, or `Owns: none` when it owns neither. Every active acceptance criterion must have exactly one task owner and every active data entity at least one.
- Classify every criterion and entity outside the active slice under `Deferred criteria`, `Release criteria`, `Deferred entities`, or `Release entities` in the implementation boundary. A criterion or entity must be either task-owned or classified, never both.
- `validate_spec.py` enforces this coverage once a spec adopts `[AC-<n>]` IDs, so a fresh agent resuming the slice reads the `Owns:` lines to see what each task delivers and what is still unowned instead of re-deriving the map from prose.

## Discovery Rules

- Do not assume the primary user is a developer because the product concerns software or AI agents.
- Do not start from the most technically interesting capability. Follow prerequisites and the user's operational order.
- Write rules with concrete examples when naming, allocation, ownership, permissions, state transitions, or failure recovery could be interpreted more than one way.
- Distinguish stable domain identity, display labels, ownership scope, and uniqueness constraints.
- Match specificity to decision ownership. Be exact about outcomes and constraints without making requirements exhaustive about implementation mechanics.
- Use representative examples and acceptance criteria when they establish the rule. Do not expand them into a combinatorial technical test matrix.
- Consolidate related engineering unknowns into one design gate instead of asking a sequence of implementation-level questions.
- Do not ask about frameworks, libraries, architecture, storage, deployment, or other implementation mechanics while product requirements remain unresolved. When product requirements are complete, state that explicitly before moving to technical-design decisions.

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

Finish when the scope is classified and healthy, all three files exist, agree on the full feature and first active slice, every required capability has one provider, every task passes the Task Size Gate or records a justified atomic exception, every required delivery surface has one clear owning task, the capability graph is acyclic, the tasks are executable in their listed order without forward dependencies, available mechanical checks pass, and the next required decision is visible.
