# Spec-Driven Development Skills and Templates

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Codex Skills](https://img.shields.io/badge/Codex-skills-blue.svg)](skills/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-commands-orange.svg)](.claude/commands/)

A practical foundation for guiding AI coding agents with explicit requirements, technical decisions, small implementation slices, verification gates, and durable project memory.

The ideas and workflow behind this repository are explained in the [Spec-Driven AI-Assisted Development article series](https://alabenkhalifa.dev/blog/series/spec-driven-ai-assisted-development/).

Use the repository as a template to start with the complete structure, or copy only the skills and files your project needs.

[Use this template](https://github.com/alabenkhlifa/Specs-Driven-Development-Skills-Templates/generate)

The repository contains reusable templates and workflows for three operations:

- `add-spec`: turn a feature request into an initial specification and first executable slice without implementing it.
- `update-spec`: update a specification when product or technical decisions change.
- `implement-spec`: implement and verify one approved slice without silently changing the agreement.

## Repository Structure

```text
.
├── templates/               Copyable project and feature templates
├── commands/                Tool-neutral workflow contracts
├── skills/                  Installable Codex skills
├── .claude/commands/        Claude Code slash commands
├── examples/                Completed training-request example
└── scripts/validate_repo.py Repository consistency checks
```

## Start a Project

1. Copy `templates/AGENTS.md` to the target project when using Codex or another agent that reads `AGENTS.md`.
2. Copy `templates/CLAUDE.md` when using Claude Code. Keep both files aligned if the project uses both tools.
3. Create `specs/<feature>/` and copy the three files from `templates/feature-spec/` into it.
4. Replace every placeholder and configure the real project checks.
5. Keep the first `tasks.md` limited to one executable slice.

Requirements can be `Approved` while design, implementation, verification, or release work remains. Mark tasks `Blocked` only when a decision prevents active implementation or required verification. Keep deployment-only evidence in a release gate, and do not mark a slice `Verified` while a required check is failing.

## Use with Codex

The folders under `skills/` are self-contained Codex skills. Copy the skills you want into your Codex skills directory, then start a new task so they can be discovered.

Example invocations:

```text
Use $add-spec to specify the account export feature.
Use $update-spec to record the new retention requirement.
Use $implement-spec to implement the active approved slice.
```

For complex or ambiguous spec work, use Plan mode for investigation and decision-making. Return to Default mode before creating or editing spec files.

## Use with Claude Code

Copy both `commands/` and `.claude/commands/` into the target repository. The `.claude` files are small adapters that load the canonical contracts from `commands/`. The commands become:

```text
/add-spec
/update-spec
/implement-spec
```

Copy `templates/CLAUDE.md` to the project root and replace the project-check placeholders.

## Tool-Neutral Use

The Markdown contracts under `commands/` can be adapted to another coding agent. Preserve their boundaries:

- Spec commands may inspect code but do not implement application changes.
- Implementation works only from an approved active slice.
- Every unresolved decision names the earliest stage it blocks.
- Product requirements, technical design, implementation, verification, and release readiness are reported separately.
- Missing active-slice decisions and boundary changes stop implementation; deployment-only gates stop deployment and release claims.
- Progress, failures, and new decisions are written back to project files.

## Validate Changes

```bash
python3 scripts/validate_repo.py
```

The validator checks required files, skill metadata, command adapters, placeholders in the completed example, and the synchronization of duplicated templates.

## Example

`examples/training-request/` contains a completed specification for a colleague submitting a training request for Office Management review.

## License

MIT
