# Project Instructions

## Source Of Truth

Before implementation, read the relevant files under `specs/<feature>/`:

- `requirements.md` defines expected behavior and product boundaries.
- `design.md` defines technical decisions and tradeoffs.
- `tasks.md` defines the active implementation slice and verification state.

Do not replace an explicit project decision with an assumption.

## SDD Workflows

Use the matching installed skill or command whenever the user's intent triggers it:

- `add-spec`: define a new feature and its first executable slice.
- `update-spec`: record a changed decision across an existing specification.
- `implement-spec`: implement and verify one approved active slice.

When one request combines specification changes with implementation, complete the specification workflow and stop. Start implementation only after the changed agreement and active slice are approved.

Spec-only work must not continue into code, migrations, tests, dependencies, or runtime configuration.

## Decision Ownership

- Ask users about observable behavior, workflow, scope, business rules, ownership, data handling, risk acceptance, and acceptance outcomes.
- Keep implementation mechanisms, algorithms, normalization rules, storage representations, library choices, and exhaustive technical edge cases with engineering when alternatives preserve the accepted product outcome.
- Ask about a technical alternative only when it changes observable behavior or requires explicit security, privacy, cost, or operational risk acceptance.
- Use representative acceptance criteria. Do not duplicate a complete technical test matrix across requirements, design, and tasks.

## Specification Question Batches

- Before asking, search the current requirements, design, tasks, and recorded project decisions. Do not ask for a decision that is already recorded.
- Group related, independent user-owned questions that share one workflow context and readiness stage into a small batch, usually two to five questions.
- Ask one question by itself only when its answer changes the next questions, it is a foundational product fork, or a previous answer needs clarification.
- Always provide one recommended answer and a brief reason for every question. When no product option can be responsibly preferred, recommend the next action, such as deferring the decision, gathering evidence, or asking the accountable owner.
- Format each batch so the user can answer every question individually or accept all recommendations together.
- Do not mix product-discovery and technical-design questions in one batch.
- After the user answers, apply the complete batch through one `update-spec` write-back and one validation pass before asking another batch or ending the session.

## Product-First Sequence

- Complete product requirements before asking technical-design or implementation questions.
- During product discovery, do not ask about frameworks, libraries, architecture, protocols, data models, deployment, or test commands.
- Record unresolved engineering decisions in `design.md` or `tasks.md` without presenting them as missing product requirements.
- When product requirements are complete, state that explicitly and transition to technical design.
- During technical design, make engineering-owned decisions from approved requirements, project constraints, official documentation, and existing repository patterns.
- Do not begin implementation until the technical design and active slice are approved.

## Readiness And Blocker Scope

- Report product-requirement readiness, technical-design readiness, implementation state, verification state, and release readiness separately.
- Every unresolved decision must name the earliest stage it blocks. A later-stage unknown must not make an earlier ready stage appear blocked.
- Requirements may be `Approved` while technical design, implementation, verification, or release work remains.
- Mark `tasks.md` as `Blocked` only when a decision prevents the active slice from starting, continuing, or completing required verification.
- Keep deployment-dependent evidence in an explicit release gate. It blocks deployment and release claims without blocking implementation or local verification when the implementation contract is already approved.

## Implementation Workflow

1. Confirm that requirements and design contain no blocking open questions.
2. Work only from the active slice in `tasks.md`.
3. Keep changes inside its implementation boundary.
4. Implement one task at a time.
5. Run the proof attached to each task before marking it complete.
6. Run the full verification gate before calling the slice complete.
7. Write progress and new decisions back to the spec files.

## Stop Conditions

Stop implementation and report the issue when:

- The requested change expands the approved scope.
- A missing business rule or design decision affects implementation.
- The code, acceptance criteria, and existing system disagree.
- A required check fails and cannot be fixed inside the approved slice.
- Another task or agent is changing the same ownership area.

Do not continue by silently choosing a new product or architecture decision.
Do not stop implementation only because a recorded deployment or release gate remains incomplete. Do stop before crossing that gate.

## Write-Back Rules

- During discussion of an existing specification, write every accepted decision through `update-spec`.
- After the user answers a specification question or related question batch, update every affected spec file before asking the next batch or ending the session.
- Do not leave resolved questions, blockers, status changes, or progress only in the conversation.
- A new conversation should recover state from the repository and need only the user's next intent.
- Update `requirements.md` when expected behavior, scope, or a business rule changes.
- Update `design.md` when a technical decision or tradeoff changes.
- Update `tasks.md` when progress, verification state, blockers, release gates, or deferred work changes.

Keep decisions in project files, not only in the conversation.

## Project Checks

- Tests: `<test command>`
- Build: `<build command>`
- Type check: `<type-check command>`
- Lint: `<lint command>`
- Manual or browser verification: `<verification instructions>`

Do not mark the slice `Verified` while a required check is failing.
