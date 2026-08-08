#!/usr/bin/env python3
"""Move a specification's progress log out of tasks.md into progress.md.

`tasks.md` is the task plan an agent must read on every task. The progress log
is an append-only compliance journal that grows forever, so keeping both in one
file makes every preflight read the full history of every completed task. This
tool keeps `## Progress Log` in `tasks.md` as a one-line pointer and stores the
entries in a sibling `progress.md`.

The tool is permanent, deterministic, and idempotent rather than a one-shot
migration: slice branches carry `tasks.md` edits in the legacy inline shape, so
a rebase onto the restructured default branch resolves each `tasks.md` conflict
by taking the branch version and re-running this tool. Entries already present
in `progress.md` are matched by their exact `### ` heading line and are never
duplicated, reordered, or rewritten.

Entry text is copied byte for byte. Proof receipts, resolved mechanisms, failed
checks, and environment incidents are compliance evidence, so an unrecognized
progress-log shape stops the run instead of being reformatted or guessed at.

Usage:
    python3 .agents/scripts/split_progress_log.py [SPEC ...] [--check]

With no SPEC argument every specification directory under `specs/` is
processed. `--check` reports the same work without writing and exits nonzero
when any file would change.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_SPECS_ROOT = Path("specs")
TASKS_FILENAME = "tasks.md"
PROGRESS_FILENAME = "progress.md"
PROGRESS_HEADING = "## Progress Log"
POINTER_LINE = "See [progress.md](progress.md)."
TASKS_TITLE_SUFFIX = "Tasks"
PROGRESS_TITLE_SUFFIX = "Progress Log"

ENTRY_SPLIT_RE = re.compile(r"(?m)^(?=### )")
ENTRY_HEADING_RE = re.compile(r"^### .*$")
H1_RE = re.compile(r"^# (?P<title>.+)$")


class SplitError(Exception):
    """A progress log could not be parsed without risking evidence loss."""


class Entry:
    """One progress-log entry identified by its exact `### ` heading line."""

    def __init__(self, text: str) -> None:
        self.text = text.rstrip("\n")
        self.heading = self.text.splitlines()[0]

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Entry({self.heading!r})"


def split_entries(body: str) -> tuple[str, list[Entry]]:
    """Split a log body into the text before the first entry and the entries."""
    parts = ENTRY_SPLIT_RE.split(body)
    preamble = parts[0]
    entries = [Entry(part) for part in parts[1:] if part.strip()]
    return preamble, entries


def render_entries(entries: list[Entry]) -> str:
    """Render entries newest-first with exactly one blank line between them."""
    if not entries:
        return ""
    return "\n\n".join(entry.text for entry in entries) + "\n"


def locate_progress_section(tasks_text: str) -> tuple[int, int, int] | None:
    """Return the heading, body, and section end offsets of `## Progress Log`.

    Returns None when the specification has no progress-log section at all.
    """
    lines = tasks_text.splitlines(keepends=True)
    heading_index: int | None = None
    for index, line in enumerate(lines):
        if line.rstrip("\n") == PROGRESS_HEADING:
            if heading_index is not None:
                raise SplitError(f"multiple {PROGRESS_HEADING} sections")
            heading_index = index
    if heading_index is None:
        return None

    heading_start = sum(len(line) for line in lines[:heading_index])
    body_start = heading_start + len(lines[heading_index])
    end = len(tasks_text)
    offset = body_start
    for line in lines[heading_index + 1 :]:
        if line.startswith("## "):
            end = offset
            break
        offset += len(line)
    return heading_start, body_start, end


def progress_title(tasks_text: str, spec_dir: Path) -> str:
    """Derive the progress-log H1 from the task plan's H1."""
    first_line = tasks_text.splitlines()[0] if tasks_text else ""
    match = H1_RE.fullmatch(first_line)
    if match is None:
        raise SplitError(f"{spec_dir / TASKS_FILENAME}: first line must be an H1 title")
    title = match.group("title").strip()
    if title.endswith(TASKS_TITLE_SUFFIX):
        stem = title[: -len(TASKS_TITLE_SUFFIX)].rstrip()
        return f"{stem} {PROGRESS_TITLE_SUFFIX}".strip()
    return f"{title} {PROGRESS_TITLE_SUFFIX}"


def parse_progress_file(text: str, path: Path) -> tuple[str, list[Entry]]:
    """Parse an existing progress.md into its H1 title line and its entries."""
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise SplitError(f"{path}: first line must be an H1 title")
    title_line = lines[0]
    body = text[len(title_line) :].lstrip("\n")
    preamble, entries = split_entries(body)
    if preamble.strip():
        raise SplitError(
            f"{path}: unrecognized content before the first '### ' entry; "
            "move it into an entry by hand"
        )
    seen: set[str] = set()
    for entry in entries:
        if entry.heading in seen:
            raise SplitError(f"{path}: duplicate entry heading {entry.heading!r}")
        seen.add(entry.heading)
    return title_line, entries


def merge_entries(existing: list[Entry], incoming: list[Entry]) -> list[Entry]:
    """Merge inline entries into stored entries without duplicating any entry.

    Identity is the exact `### ` heading line. Both inputs are newest-first, so
    walking the incoming list while advancing a cursor through the stored list
    places branch-only entries above the newest shared entry and keeps every
    stored entry. A shared entry keeps its stored text; progress.md is the
    established record and is never rewritten from the task plan.
    """
    positions: dict[str, int] = {}
    for index, entry in enumerate(existing):
        positions.setdefault(entry.heading, index)

    merged: list[Entry] = []
    cursor = 0
    for entry in incoming:
        position = positions.get(entry.heading)
        if position is None:
            merged.append(entry)
            continue
        if position < cursor:
            # Already emitted from the stored list; never duplicate it.
            continue
        merged.extend(existing[cursor : position + 1])
        cursor = position + 1
    merged.extend(existing[cursor:])
    return merged


def plan_spec(spec_dir: Path) -> dict[Path, str]:
    """Return the files that must change for one specification directory.

    An empty mapping means the specification is already split, has no progress
    log, or is not a specification directory.
    """
    tasks_path = spec_dir / TASKS_FILENAME
    if not tasks_path.is_file():
        return {}

    tasks_text = tasks_path.read_text(encoding="utf-8")
    located = locate_progress_section(tasks_text)
    if located is None:
        # No progress log at all: leave the file alone and create nothing.
        return {}
    heading_start, body_start, section_end = located

    body = tasks_text[body_start:section_end]
    preamble, inline_entries = split_entries(body)
    stripped_preamble = preamble.strip()
    if stripped_preamble and stripped_preamble != POINTER_LINE:
        raise SplitError(
            f"{tasks_path}: unrecognized {PROGRESS_HEADING} content "
            f"{stripped_preamble[:60]!r}; move it into a '### ' entry by hand"
        )

    inline_headings: set[str] = set()
    for entry in inline_entries:
        if entry.heading in inline_headings:
            raise SplitError(
                f"{tasks_path}: duplicate entry heading {entry.heading!r}"
            )
        inline_headings.add(entry.heading)

    progress_path = spec_dir / PROGRESS_FILENAME
    if progress_path.is_file():
        title_line, stored_entries = parse_progress_file(
            progress_path.read_text(encoding="utf-8"), progress_path
        )
        merged = merge_entries(stored_entries, inline_entries)
    else:
        if not inline_entries:
            # Nothing to store yet; do not create an empty progress log.
            return {}
        title_line = f"# {progress_title(tasks_text, spec_dir)}"
        merged = inline_entries

    changes: dict[Path, str] = {}

    progress_text = f"{title_line}\n\n{render_entries(merged)}"
    if not progress_path.is_file() or progress_path.read_text(encoding="utf-8") != progress_text:
        changes[progress_path] = progress_text

    tail = tasks_text[section_end:]
    separator = "\n" if tail else ""
    new_tasks_text = (
        tasks_text[:heading_start]
        + f"{PROGRESS_HEADING}\n\n{POINTER_LINE}\n"
        + separator
        + tail
    )
    if new_tasks_text != tasks_text:
        changes[tasks_path] = new_tasks_text

    return changes


def spec_directories(targets: list[Path]) -> list[Path]:
    """Resolve command-line targets to specification directories."""
    if not targets:
        targets = [DEFAULT_SPECS_ROOT]

    resolved: list[Path] = []
    for target in targets:
        if not target.is_dir():
            raise SplitError(f"{target}: not a directory")
        if (target / TASKS_FILENAME).is_file():
            resolved.append(target)
            continue
        children = sorted(
            child
            for child in target.iterdir()
            if child.is_dir() and (child / TASKS_FILENAME).is_file()
        )
        if not children:
            raise SplitError(f"{target}: no specification directory with {TASKS_FILENAME}")
        resolved.extend(children)
    return resolved


def run(targets: list[Path], *, check: bool) -> tuple[int, list[str]]:
    """Split or check every resolved specification and report the work done."""
    reports: list[str] = []
    changed_files = 0
    for spec_dir in spec_directories(targets):
        changes = plan_spec(spec_dir)
        for path in sorted(changes):
            changed_files += 1
            action = "would update" if check else "updated"
            if not path.exists():
                action = "would create" if check else "created"
            reports.append(f"{action} {path}")
            if not check:
                path.write_text(changes[path], encoding="utf-8")
    return changed_files, reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "targets",
        nargs="*",
        type=Path,
        help=(
            "Specification directory, or a root containing them "
            f"(default: {DEFAULT_SPECS_ROOT})"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report what would change and exit nonzero without writing",
    )
    args = parser.parse_args()

    try:
        changed_files, reports = run(args.targets, check=args.check)
    except SplitError as error:
        print(f"Progress log split failed: {error}", file=sys.stderr)
        return 2

    for report in reports:
        print(report)

    if args.check:
        if changed_files:
            print(
                f"Progress log split check failed: {changed_files} file(s) need "
                "python3 .agents/scripts/split_progress_log.py",
                file=sys.stderr,
            )
            return 1
        print("Progress log split check passed: every specification is split")
        return 0

    if changed_files:
        print(f"Progress log split complete: {changed_files} file(s) written")
    else:
        print("Progress log split complete: nothing to change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
