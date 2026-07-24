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

Traceability:

- Deferred criteria: <AC-<n> IDs outside the active slice, or none>
- Release criteria: <AC-<n> IDs proved only at release, or none>
- Deferred entities: <entity:<Name> items outside the active slice, or none>
- Release entities: <entity:<Name> items introduced only for release, or none>

## Tasks

- [ ] <First implementation step>
  - Purpose: <Why this step is needed>
  - Owned surfaces: <UI, API, domain, persistence, integration, security or privacy, and operational surfaces for which this task is the primary owner>
  - Owns: <AC-<n> IDs and entity:<Name> items this task is the primary owner of, or none>
  - Proof: <Check that shows this step works>

- [ ] <Next implementation step>
  - Purpose: <Why this step is needed>
  - Owned surfaces: <Surfaces for which this task is the primary owner>
  - Owns: <AC-<n> IDs and entity:<Name> items this task is the primary owner of, or none>
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
