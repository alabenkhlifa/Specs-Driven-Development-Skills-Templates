---
name: add-spec
description: Create an initial Spec-Driven Development feature specification from a request by inspecting the existing project, resolving consequential questions, and writing requirements.md, design.md, and tasks.md without implementing code. Use when a user asks to specify, plan, scope, or prepare a new feature or implementation slice before coding.
---

# Add Spec

Create one feature specification without implementing application code.

## Workflow

1. Read the applicable `AGENTS.md` and existing specifications.
2. Inspect the code and documentation where the feature connects.
3. Identify outcome, users, scope, business rules, acceptance criteria, technical constraints, affected components, risks, and tradeoffs.
4. Ask for input when a missing decision would materially change product behavior or architecture.
5. For complex work, use Plan mode to produce and approve the proposal. Return to Default mode before writing files.
6. Copy the bundled templates from `assets/` into `specs/<feature>/` and replace every placeholder.
7. Keep `tasks.md` limited to the first executable slice.
8. Report files created, assumptions, unresolved questions, and approval status.

## Boundaries

- Do not implement code, migrations, tests, APIs, or UI behavior.
- Do not silently decide consequential product or architecture questions.
- Do not mark a specification `Approved` while blocking questions remain.
- Keep real specification files free of teaching labels or unexplained placeholders.

## Completion

Finish when all three files exist, agree with each other, and make the next required decision visible.

