# <Feature or Slice Name> Tasks

## Status

Not Started | In Progress | Blocked | Verified

## Active Slice

<The working behavior this task file is expected to deliver>

## Implementation Boundary

Included:

- <Work allowed in this slice>
- <Another allowed change>

Excluded:

- <Related work that must remain separate>

Deferred after this slice:

- <Required behavior planned for a later executable slice>

Release gates:

- <Deployment or release evidence that is not required for active implementation, or None>

## Tasks

- [ ] <First implementation step>
  - Purpose: <Why this step is needed>
  - Owned surfaces: <UI, API, domain, persistence, integration, security or privacy, and operational surfaces for which this task is the primary owner>
  - Proof: <Check that shows this step works>

- [ ] <Next implementation step>
  - Purpose: <Why this step is needed>
  - Owned surfaces: <Surfaces for which this task is the primary owner>
  - Proof: <Check that shows this step works>

## Verification Gate

- [ ] Acceptance criteria pass
- [ ] Relevant automated tests pass
- [ ] Build and type checks pass
- [ ] Required manual scenario passes
- [ ] New decisions are written back
- [ ] Deferred work is recorded

## Blocked Decisions

- <Decision that blocks the active slice and the earliest stage it blocks, or None>

## Progress Log

### <Date or session>

- Completed: <What changed>
- Remaining: <What is still open>
- Failed checks: <Failure that still blocks completion>
- Spec updates: <Requirements or design decisions written back>
