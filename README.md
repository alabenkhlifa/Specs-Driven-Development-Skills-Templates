# Spec-Driven Development Skills and Templates

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Codex Skills](https://img.shields.io/badge/Codex-skills-blue.svg)](skills/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skills_and_commands-orange.svg)](.claude/)

A reusable Spec-Driven Development harness for defining, updating, implementing, and independently reviewing one approved implementation slice at a time.

The workflow is explained in the [Spec-Driven AI-Assisted Development article series](https://alabenkhalifa.dev/blog/series/spec-driven-ai-assisted-development/).

[Use this template](https://github.com/alabenkhlifa/Specs-Driven-Development-Skills-Templates/generate)

## Workflows

- `add-spec`: define a bounded feature and its first executable slice without implementing it.
- `update-spec`: restore agreement when requirements, design, task boundaries, or verification expectations change.
- `implement-spec`: implement and verify one approved active slice.
- `review-spec`: independently re-run task proofs and the verification gate, report findings, and route fixes without changing code or the agreement.

Specification changes stop before implementation. Review reports and routes findings; fixes return to `implement-spec`, while agreement changes return to `update-spec`.

## Repository Structure

```text
.
├── skills/                  Canonical Agent Skills
├── commands/                Tool-neutral mirrors of the skill contracts
├── .claude/skills/          Links to the canonical skills
├── .claude/commands/        Claude Code slash-command adapters
├── templates/               Project instructions and feature-spec templates
├── examples/                Completed training-request specification
└── scripts/
    ├── validate_spec.py     Mechanical validation for one specification
    ├── test_validate_spec.py
    └── validate_repo.py     Repository consistency checks
```

The skill folders are canonical. `commands/` contains exact mirrors for tools that load standalone command files. The repository validator rejects drift between them.

## Start a Project

1. Copy `templates/AGENTS.md` to the project root. Also copy it as `CLAUDE.md` when both tools are used, and keep the two files identical.
2. Copy the four folders under `skills/` into the project's `.agents/skills/`.
3. Copy `scripts/validate_spec.py` and `scripts/test_validate_spec.py` into `.agents/scripts/`.
4. For Claude Code 2.1.203 or newer, link each `.claude/skills/<name>` folder to `../../.agents/skills/<name>` so Claude and Codex execute the same skill files.
5. Create `specs/<feature>/` from `templates/feature-spec/` and replace every placeholder.
6. Configure the real project checks in the root instruction files.

The slash-command adapters remain available for projects that use `.claude/commands/`: copy both `commands/` and `.claude/commands/` to the project.

## Traceability Contract

The templates make the active slice recoverable without re-reading the full conversation:

- Requirements give every acceptance criterion a stable ID such as `[AC-01]`.
- Design defines each data entity with a bullet such as ``- `TrainingRequest`: ...``.
- `Owned surfaces` maps concrete UI, API, domain, persistence, integration, privacy, security, and operational surfaces to one primary implementation task.
- Every task has exactly one `Owns:` line. Active criteria have exactly one task owner, and active data entities have at least one.
- Criteria and entities outside the active slice are classified as deferred or release coverage in the implementation boundary. An item cannot be both task-owned and classified.

Run the specification validator after every agreement or task-boundary change:

```bash
python3 .agents/scripts/validate_spec.py specs/<feature>
```

## Use with Codex

Codex discovers repository-local skills under `.agents/skills/`. Example requests:

```text
Use $add-spec to specify the account export feature.
Use $update-spec to record the new retention requirement.
Use $implement-spec to implement the active approved slice.
Use $review-spec to independently review the completed slice.
```

## Use with Claude Code

Claude Code can discover the linked canonical skills under `.claude/skills/`. The optional slash commands are:

```text
/add-spec
/update-spec
/implement-spec
/review-spec
```

## Readiness Rules

Report product requirements, technical design, implementation, verification, and release readiness separately. A deployment-only gate blocks release, not local implementation or verification. An unavailable service, runtime, daemon, credential, or network is an environment blocker for the affected proof, not automatically an implementation defect.

Never mark a slice `Verified` while a required established check is failing or unavailable without an explicit accepted exception.

## Validate This Repository

```bash
python3 scripts/test_validate_spec.py
python3 scripts/validate_repo.py
```

The repository validator checks required files, skill metadata, skill-command synchronization, Claude adapters and links, duplicated templates, unresolved example placeholders, the completed example specification, and instruction-file synchronization.

## Example

`examples/training-request/` contains a complete specification for a colleague submitting a training request for Office Management review.

## License

MIT
