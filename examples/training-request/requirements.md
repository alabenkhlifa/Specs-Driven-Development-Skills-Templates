# Submit a Training Request

## Status

Approved

## Outcome

A colleague can submit a training request, see it after submission, and provide Office Management with enough context to review it.

## Users

- Colleague submitting the request
- Office Management reviewer

## In Scope

- Submit a request with title, provider, cost, currency, and business justification.
- Show the submitted request to its owner.
- Show submitted requests in the Office Management review queue.

## Out of Scope

- Approval history and audit events
- Budget reservation or payment processing
- Notifications

## Primary Workflow

1. A colleague opens the training request form.
2. They enter the title, provider, cost, currency, and business justification.
3. They submit the request and see it in their request list while Office Management sees it in the review queue.

## Business Rules

- A colleague can read only requests they own.
- Office Management can read submitted requests.
- A draft request must not appear in the Office Management queue.
- Cost must be greater than zero and include a currency.

## Acceptance Criteria

- [AC-01] Given a valid request, when a colleague submits it, then it appears in their request list with status `Submitted`.
- [AC-02] Given a submitted request, when Office Management opens the review queue, then the request is visible with its business context.
- [AC-03] Given a request owned by another colleague, when a colleague tries to access it, then access is denied.
- [AC-04] Given a draft request, when Office Management opens the review queue, then the draft is not visible.

## Open Questions

None.
