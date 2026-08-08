---
name: update-spec
description: Update an existing Spec-Driven Development specification when a user clarifies or resolves an open question, or when requirements, scope, business rules, architecture decisions, implementation boundaries, acceptance criteria, or verification expectations change. Use during discovery, review, implementation feedback, or failed verification when the agreement must change before coding continues. Do not implement the change.
---

# Update Spec

Activate this skill as the workflow for restoring agreement between requirements, design, tasks, and proof without implementing the change.

## Workflow

1. Read the applicable `AGENTS.md` and the feature's `requirements.md`, `design.md`, and `tasks.md`. Read only the latest relevant entries from `progress.md`; `## Progress Log` in `tasks.md` must contain only `See [progress.md](progress.md).`
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
   - `tasks.md`: active-slice boundary, implementation steps, proof, verification gate, active blockers, release gates, deferred work, and task and slice status.
   - `progress.md`: a newest-first entry only for meaningful implementation movement, verification evidence or invalidation, a status transition, or a consolidated discovery checkpoint.
10. Remove or replace resolved questions, stale blockers, contradicted wording, and invalid proof. Consolidate obsolete or repetitive discovery checkpoints after confirming their durable decisions live in the current requirements, design, and task state. Preserve a replaced tradeoff by recording the new choice and consequence.
11. Keep technologies deferred when the decision is still product-level. Add technical consequences as open questions instead of selecting a stack implicitly.
12. Run the Cross-Specification Capability Gate, Slice Size Gate, Task Size Gate, Task Proof Gate, and Delivery Coverage and Sequence Gate whenever requirements, design, dependencies, proof expectations, or the active task plan changes.
13. Set status by the affected stage. Move requirements to `Draft` when the product agreement becomes incomplete, move tasks to `Blocked` only when active implementation or required verification cannot proceed, and remove `Verified` whenever existing proof no longer covers the changed behavior. Keep deployment-only unknowns in an explicit release gate without representing the work as releasable.
14. Run `python3 .agents/scripts/validate_spec.py specs/<feature>`, `python3 .agents/scripts/split_progress_log.py --check`, and the repository's global dependency validator once after applying the batch when available, then manually confirm that every changed decision, capability edge, slice-size declaration, task-size declaration, proof-scope declaration, proof, scope classification, delivery-coverage mapping, and task dependency agrees across files.
15. Report the scope classification, capability graph result, slice-size, task-size, and proof-scope results and exceptions, delivery-coverage and sequence result including any missing provider, cycle, oversized slice or task, unmapped, ambiguous, or forward-dependent surface, changed decisions, newly exposed questions with their blocked stages, invalidated or deferred work, status changes, and product, design, implementation, verification, and release readiness separately.

## Question Batching Rules

- Before asking, check the current requirements, design, tasks, and recorded project decisions; do not ask for a decision that is already recorded.
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

## Cross-Specification Capability Gate

- Treat slice numbers as identifiers, not execution order.
- Require `## Cross-Specification Dependencies` after `## Active Slice` in every new or changed `tasks.md`, with `Requires:` and `Provides:` lists.
- Declare a requirement as ``- `capability:<name>` — provider `specs/<feature>#Task <n>` — required before `Task <n>`.`` Declare a provider as ``- `capability:<name>` — ready after `Task <n>`.`` Use `- None.` for an empty list.
- Give each capability one primary provider task and depend on the smallest stable capability instead of a whole slice when possible.
- Inspect provider and consumer contracts together. Reject missing or ambiguous providers, malformed task references, cycles, and consumers that redefine the provider's schema, interface, authoritative data, or lifecycle.
- A capability is ready only after the named provider task, its complete proof, and its readiness write-back are complete. After splitting or reordering tasks, point each requirement at the earliest task that actually consumes the capability and derive slice status from the first incomplete task in listed execution order. Keep that consumer task `Blocked`; keep the slice `Blocked` only when it is the next executable task, so a later unavailable capability does not stop independent earlier work.
- Update both provider and consumer specifications in the same capability-edge change and run the global dependency validator when available.

## Slice Size Gate

- Add `## Slice Size Gate` after `## Cross-Specification Dependencies` and before `## Task Size Gate` for every new task plan. Do not retrofit an active legacy slice only to satisfy the numeric limits.
- Use `Slice size: Standard` only when the active slice has one coherent end-to-end outcome, at most 12 tasks total, and a longest `Depends on:` path of at most 8 tasks.
- Use `Slice size: Exception — <reason>.` only when every smaller boundary duplicates an authoritative contract or creates a concrete invalid lifecycle or verification state; reject complexity, convenience, chronology, a shared release milestone, or one pull request as reasons.
- When an active legacy slice is materially refined and its unfinished work contains independent outcomes, preserve completed history in place and move the unfinished outcomes into focused child specifications that adopt the gate. Update capability edges together.
- Do not make tasks larger to fit the slice limit; re-run the Task Size Gate after every split.

## Task Size Gate

- For a new task plan, add `## Task Size Gate` after `## Slice Size Gate` and before `## Proof Scope Gate`. In a legacy plan that has not adopted the Slice Size Gate, preserve its established position unless unfinished work is moving to a new child specification. Once the task-size contract is adopted, keep exactly one `Size:` line on every task.
- Use `Size: Standard` only for one independently provable outcome with one primary state transition or invariant, normally one adapter or workflow, one task-boundary implementation commit, no more than three acceptance criteria and two entities, and focused proof expected to run in about ten minutes.
- Use 30–45 minutes as a planning target. Expected work beyond 60 minutes, more than one meaningful implementation commit, multiple independent behaviors, multiple adapter integrations, distinct delivery channels, authorization boundaries, lifecycle clocks, mixed domain, UI, authentication or recovery work, another specification's source-owned integration, or independently failing proof modalities requires a split.
- Keep full repository, production, security, and browser-matrix gates at slice verification. Use focused task proof and directly applicable safety checks unless the task owns the broader gate.
- Record `Size: Exception — <reason>.` only when splitting an atomic migration, transaction, or invariant would create a concrete invalid intermediate state. Complexity, convenience, chronology, or test duration does not justify an exception.
- Preserve every existing task label and completed history. Split only unfinished work, give each new task the next unused numeric label, list tasks by executable dependency order rather than numeric label, update affected `Depends on:` and capability provider or consumer task references together, then re-run the individual and global validators.
- Prefer coherent vertical or invariant-preserving tasks; do not create small layer-only tasks that leave unusable or unprovable intermediate states.

## Task Proof Gate

- Add `## Proof Scope Gate` after `## Task Size Gate` and before `## Implementation Boundary` for new plans. Adopt it prospectively on a legacy plan when its next unfinished task or verification boundary is materially refined; do not manufacture receipts for completed history.
- Declare `- Applies to: all tasks.` for a new plan or list the stable unfinished `Task <n>` labels covered by prospective adoption.
- Give every applicable task one `Proof scope:` line. Use `Focused` by default. Permit `Broad — <reason>.` only when the task owns an inseparable repository-wide, browser-matrix, security, production, or release gate.
- Keep focused proof executable through `python3 .agents/scripts/run_proof.py task --task <n> -- <command>` and complete gates executable through `python3 .agents/scripts/run_proof.py slice -- <command>`. Remove duplicated full-suite execution from task proof.

## Delivery Coverage And Sequence Gate

- Inventory every UI, API, domain, persistence, integration, security or privacy, and operational surface named by the active-slice requirements and design.
- Assign every surface to one primary implementation task through its `Owned surfaces` field. Naming a surface only in purpose, proof, acceptance criteria, or the verification gate does not assign implementation ownership.
- Prefer vertical workflow tasks that own user-visible UI and its supporting logic together when one scenario can implement and prove them coherently.
- Keep final end-to-end tasks focused on integration and verification of surfaces already owned elsewhere; do not make them the implicit owner of all pages or behavior.
- After assigning surfaces, simulate the tasks in listed order. For each task, inspect its purpose, owned surfaces, traceability items, and proof, then identify every schema, interface, route, service, fixture, and earlier task output it needs.
- Require every prerequisite to exist in the baseline or be delivered by the same task or an earlier task. When the task itself introduces a prerequisite, name that artifact in `Owned surfaces` and cover it in the task proof. A surface first delivered by a later task is a forward dependency even when eventual ownership and traceability are complete.
- Resolve each forward dependency by moving the foundation to the earliest consumer, defining an explicit stable early contract plus a later additive extension, reordering the tasks, or blocking the affected task. Do not leave the decision for implementation-time clarification.
- Resolve every unmapped or ambiguously owned surface before completion, or mark tasks `Blocked` when the gap prevents active implementation.
- Keep every task's stable `Task <n>` label unchanged. List tasks by executable dependency order, so a newly added higher-numbered task may correctly appear before an older lower-numbered task. Add exactly one `Depends on:` line naming earlier listed task labels or `none`, and update it whenever task order or prerequisites change. Treat this declaration as navigation and validator input, not as a substitute for the semantic sequence simulation.
- Keep every acceptance criterion's `[AC-<n>]` ID stable across edits: assign the next unused integer to a new criterion and never renumber or reuse a retired one. Give each new `## Data and Access Boundaries` entity a backticked-name bullet.
- Require an acceptance criterion's owning task to deliver, or depend only on earlier delivery of, every surface needed to prove that criterion. When a broad criterion spans independently failing split tasks, keep its existing ID for one retained outcome and add the next unused IDs for the other outcomes without changing the approved behavior.
- Update the affected tasks' `Owns:` lines and the implementation boundary's deferred or release classifications whenever a criterion or entity is added, removed, reclassified, or reassigned. Keep every active criterion owned by exactly one task, every active entity by at least one, and every deferred or release item classified without an active owner. `validate_spec.py` enforces this coverage once the spec uses `[AC-<n>]` IDs; re-run it after the change.

## Decision Rules

- Distinguish stable domain identity, display labels, ownership scope, and uniqueness constraints.
- Add concrete examples when rules involve naming, allocation, permissions, state transitions, ordering, or recovery.
- Add concurrency, security, or failure implications only when they follow from the decision; keep unselected implementation details open.
- Preserve the abstraction level of an accepted answer. Do not expand a simple business decision into implementation edge cases unless new evidence makes them product-significant.
- Prefer one consolidated engineering question or blocker to enumerating algorithms, normalization rules, storage representations, or exhaustive technical edge cases.
- Keep acceptance criteria representative and observable rather than turning them into a complete technical test matrix.
- Name the earliest blocked stage for every unresolved item. A decision that affects only deployment or release must not block implementation or local verification when their contract is already stable.

## Specification State Discipline

- Write every accepted decision back immediately, but place the durable decision in the current requirements, design, active boundary, blockers, or proof rather than relying on chronology.
- Do not append a `progress.md` entry for every discovery answer or clarification. The progress journal is not a conversation transcript and must not duplicate decisions already visible in current-state sections.
- Add or update progress only for meaningful implementation movement, a verification result or invalidation, a specification status transition, or a consolidated discovery checkpoint that materially changes readiness or scope.
- During an active discovery thread, update one current checkpoint in place or omit a progress entry when the changed current-state sections already provide a complete handoff.
- Keep `tasks.md` limited to the current executable slice. Put future work in concise deferred boundaries or a separate specification instead of expanding the active task list.
- Keep deployment-dependent evidence in a release gate when it is not required by the active implementation or verification contract.
- When repetitive discovery history already exists, consolidate it in `progress.md` without removing failed-check evidence, completed implementation history, or decisions that are not represented elsewhere.

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

Finish when the scope is classified and healthy, the changed decision and its proof are visible, affected files agree, every required capability has one provider, every adopted slice passes the Slice Size Gate, every new or refined task passes the Task Size Gate and Task Proof Gate or records a justified exception, every required delivery surface has one clear owning task, the capability graph is acyclic, the tasks are executable in their listed order without forward dependencies, stale questions and blockers are removed, `tasks.md` remains a concise current-state plan, `progress.md` preserves the necessary evidence history, available mechanical checks pass, and implementation state is accurate.
