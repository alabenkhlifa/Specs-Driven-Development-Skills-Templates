# Add Spec

## Purpose

Create an initial specification for one feature or implementation slice without implementing application code.

## Input

- Feature description supplied by the user
- Relevant existing code, documentation, specifications, and project instructions

## Optional Plan Stage

For complex, ambiguous, or cross-cutting changes:

1. Enter the agent's read-only planning mode.
2. Inspect the existing system and produce a proposed specification.
3. Resolve blocking questions without creating or editing files.
4. Ask the engineer to approve the proposed scope and design.
5. Return to a writable mode.
6. Run this workflow with the approved proposal as input.

Do not claim that specification files were created while the agent is still in a read-only planning mode.

## Workflow

1. Read the project instruction file and related existing specifications.
2. Inspect the current system where the feature will connect.
3. Identify the intended outcome, users, boundaries, business rules, and expected proof.
4. Identify technical constraints, affected components, interfaces, risks, and tradeoffs.
5. Ask for decisions when missing information would materially change the product or design.
6. Create `specs/<feature>/requirements.md`, `design.md`, and `tasks.md` from the bundled templates.
7. Keep the first task file limited to one executable slice.
8. Report unresolved questions, assumptions, and files created.

## Restrictions

- Do not implement application code.
- Do not create migrations, tests, API behavior, or UI changes.
- Do not resolve consequential product or architecture decisions silently.
- Do not mark the specification `Approved` while blocking questions remain.

## Completion

The workflow is complete when the initial specification files exist, their assumptions are visible, and the next required decision is clear.

