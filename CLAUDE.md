# Repository Instructions

This repository publishes reusable Spec-Driven Development templates and agent workflows.

## Canonical Resources

- Treat `skills/` as the canonical workflow source.
- Keep each `commands/<name>.md` file identical to its matching `skills/<name>/SKILL.md`.
- Keep `.claude/skills/` linked to the canonical skill folders.
- Keep `.claude/commands/` synchronized with the four command contracts.
- Keep `skills/add-spec/assets/` identical to `templates/feature-spec/`.
- Keep `AGENTS.md` and `CLAUDE.md` identical.
- Keep `templates/AGENTS.md` and `templates/CLAUDE.md` identical.

The four supported workflows are `add-spec`, `update-spec`, `implement-spec`, and `review-spec`.

## Change Boundaries

- Inspect the working tree before editing and preserve unrelated changes.
- Preserve tool-neutral workflow rules unless a file is explicitly an adapter.
- Do not add private URLs, credentials, customer names, or internal project details.
- Do not weaken scope, ownership, traceability, proof, or verification gates to make a workflow appear complete.
- Keep the example small and anonymized.

## Verification

Run:

```bash
python3 scripts/test_validate_spec.py
python3 scripts/validate_repo.py
git diff --check
```

Validate every changed canonical skill with the active skill-authoring environment. Do not commit while validation is failing.
