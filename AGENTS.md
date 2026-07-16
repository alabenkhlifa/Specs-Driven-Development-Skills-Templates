# Repository Instructions

This repository publishes reusable Spec-Driven Development templates and agent workflows.

## Source Rules

- Treat `commands/` and `templates/` as the human-facing canonical resources.
- Keep `.claude/commands/` synchronized with `commands/`.
- Keep the template copies bundled with `skills/add-spec/assets/` synchronized with `templates/feature-spec/`.
- Keep the three skill workflows consistent with the corresponding command contracts.

## Change Boundaries

- Preserve tool-neutral workflow rules unless a file is explicitly an adapter.
- Do not add private URLs, credentials, customer names, or internal project details.
- Do not weaken stop conditions or verification gates to make a workflow appear easier.
- Keep the example small and anonymized.

## Verification

Run:

```bash
python3 scripts/validate_repo.py
```

Do not commit while validation is failing.

