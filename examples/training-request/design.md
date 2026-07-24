# Submit a Training Request Design

## Context

The application already has colleague and Office Management roles. Requests are persisted in the project database, and the current API uses role-based authorization at the controller boundary.

## Proposed Approach

Add a training-request resource with separate owner and Office Management queries. Submission changes a request from `Draft` to `Submitted`. Authorization is enforced in the service layer as well as the API boundary.

## Components Affected

- Training request API and service
- Request persistence model
- Colleague request form and list
- Office Management review queue

## Data and Access Boundaries

- `TrainingRequest`: stores its owner identifier, title, provider, cost, currency, business justification, and current status.
- Colleague queries always filter by the authenticated owner.
- Office Management queries include only `Submitted` requests.
- Authorization does not depend on client-side filtering.

## Interfaces

- Add an endpoint to create or update the current colleague's draft.
- Add an endpoint to submit the current colleague's request.
- Add owner-scoped and Office Management review queries.
- Preserve the project's existing error response format.

## Decisions and Tradeoffs

### Store only the current status

- Choice: Store `Draft` and `Submitted` as the current request status.
- Reason: The first slice needs submission and review visibility, not a complete approval workflow.
- Consequence: Status history and auditability require a later design change.

## Risks

- Owner filtering could be missed in one query. Integration tests will cover cross-owner access.
- Drafts could leak into the review queue. The queue query and browser scenario will verify status filtering.

## Open Questions

None.
