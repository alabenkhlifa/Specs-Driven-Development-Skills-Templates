# Submit a Training Request Tasks

## Status

Not Started

## Active Slice

Allow a colleague to submit a training request and make the submitted request available to its owner and Office Management without exposing it to another colleague.

## Implementation Boundary

Included:

- Request persistence and submission API
- Owner and Office Management read queries
- Colleague submission form and request list
- Office Management queue entry
- Automated access checks and one browser scenario

Excluded:

- Approval actions and status history
- Notifications, budgets, and payments

Deferred after this slice:

- Approval decisions and status history will be specified as a later executable slice.

Release gates:

- None.

Traceability:

- Deferred criteria: none.
- Release criteria: none.
- Deferred entities: none.
- Release entities: none.

## Tasks

- [ ] Task 1 — Add request persistence.
  - Purpose: Persist the owner, business context, cost, currency, and current status.
  - Owned surfaces: Persistence — the training-request migration, model, constraints, and repository operations.
  - Owns: entity:TrainingRequest
  - Proof: The migration applies and persistence tests pass.

- [ ] Task 2 — Implement the colleague submission workflow.
  - Purpose: Let a colleague submit a valid request and view only requests they own.
  - Owned surfaces: Domain, API, and frontend — draft validation, submission transition, owner-scoped queries, authorization, the colleague form, and the colleague request list.
  - Owns: AC-01, AC-03
  - Proof: API and interface tests cover successful submission, owner visibility, validation, and cross-owner denial.

- [ ] Task 3 — Implement the Office Management review queue.
  - Purpose: Show submitted requests with their business context without exposing drafts.
  - Owned surfaces: Domain, API, and frontend — the submitted-request query, role authorization, queue data contract, and Office Management queue.
  - Owns: AC-02, AC-04
  - Proof: Integration and interface tests cover submitted visibility, business context, authorization, and draft exclusion.

- [ ] Task 4 — Run the complete workflow proof.
  - Purpose: Verify the already-owned colleague and Office Management surfaces together.
  - Owned surfaces: Integration — cross-role navigation and browser scenario orchestration; no first implementation ownership.
  - Owns: none (integration-only proof).
  - Proof: The browser scenario covers submission, owner visibility, review visibility, draft exclusion, and cross-owner denial.

## Verification Gate

- [ ] Acceptance criteria pass
- [ ] Relevant automated tests pass
- [ ] Build and type checks pass
- [ ] Required browser scenario passes
- [ ] New decisions are written back
- [ ] Deferred approval history is recorded

## Blocked Decisions

None.

## Progress Log

No implementation sessions yet.
