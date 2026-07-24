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

## Tasks

- [ ] Add the request model and persistence migration.
  - Purpose: Persist owner, business context, cost, currency, and status.
  - Proof: Migration applies and persistence tests pass.

- [ ] Implement submission and owner-scoped reads.
  - Purpose: Let a colleague submit and view only their requests.
  - Proof: API tests cover successful submission and cross-owner denial.

- [ ] Implement the Office Management submitted-request query.
  - Purpose: Expose submitted requests without drafts.
  - Proof: Integration tests include submitted and draft requests.

- [ ] Connect the colleague and Office Management interfaces.
  - Purpose: Complete the working behavior across both user roles.
  - Proof: The browser scenario covers submission, owner visibility, review visibility, and cross-owner denial.

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
