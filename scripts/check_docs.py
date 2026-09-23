"""Check local Markdown links, fences, and Python snippets without dependencies."""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    ".dependency-floor",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}
FENCE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<info>.*)$")
LINK = re.compile(r"!?\[[^\]]*\]\((?P<target><[^>]+>|[^\s)]+)\)")
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(?P<target><[^>]+>|\S+)")
INLINE_CODE = re.compile(r"`[^`]*`")
MERMAID_START = (
    "flowchart ",
    "graph ",
    "sequenceDiagram",
    "stateDiagram",
    "classDiagram",
    "erDiagram",
    "gantt",
    "journey",
    "pie",
)


def markdown_files() -> list[Path]:
    files: list[Path] = []
    for directory, subdirectories, names in os.walk(ROOT):
        subdirectories[:] = sorted(
            name for name in subdirectories if name not in SKIP_DIRS
        )
        files.extend(
            Path(directory) / name for name in sorted(names) if name.endswith(".md")
        )
    return files


def check_link(source: Path, line_number: int, target: str) -> str | None:
    target = target.removeprefix("<").removesuffix(">")
    if target.startswith("#"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or target.startswith("//"):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    resolved = ROOT / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not resolved.exists():
        return f"{source.relative_to(ROOT)}:{line_number}: missing local link {target}"
    return None


def check_file(source: Path) -> list[str]:
    problems: list[str] = []
    opened: tuple[str, int, str] | None = None
    first_mermaid_line: str | None = None
    code_lines: list[str] = []
    for line_number, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        fence = FENCE.match(line)
        if fence:
            marker = fence.group("marker")
            info = fence.group("info").strip()
            if opened is None:
                opened = (marker, line_number, info)
                first_mermaid_line = None
                code_lines = []
            elif (
                marker[0] == opened[0][0] and len(marker) >= len(opened[0]) and not info
            ):
                if opened[2] == "mermaid" and (
                    first_mermaid_line is None
                    or not first_mermaid_line.startswith(MERMAID_START)
                ):
                    problems.append(
                        f"{source.relative_to(ROOT)}:{opened[1]}: Mermaid block "
                        "needs a recognized diagram declaration"
                    )
                if opened[2] in {"python", "py"}:
                    try:
                        compile(
                            "\n".join(code_lines),
                            str(source),
                            "exec",
                            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                        )
                    except SyntaxError as exc:
                        problems.append(
                            f"{source.relative_to(ROOT)}:{opened[1]}: "
                            f"invalid Python snippet: {exc.msg}"
                        )
                opened = None
            continue
        if opened is not None:
            code_lines.append(line)
            if opened[2] == "mermaid" and first_mermaid_line is None and line.strip():
                first_mermaid_line = line.strip()
            continue
        visible = INLINE_CODE.sub("", line)
        targets = [match.group("target") for match in LINK.finditer(visible)]
        definition = REFERENCE.match(visible)
        if definition:
            targets.append(definition.group("target"))
        for target in targets:
            problem = check_link(source, line_number, target)
            if problem:
                problems.append(problem)
    if opened is not None:
        problems.append(f"{source.relative_to(ROOT)}:{opened[1]}: unclosed code fence")
    return problems


def main() -> int:
    files = markdown_files()
    problems = [problem for source in files for problem in check_file(source)]
    for problem in problems:
        print(problem)
    if problems:
        print(f"Documentation check failed: {len(problems)} issue(s).")
        return 1
    print(f"Documentation check passed: {len(files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
