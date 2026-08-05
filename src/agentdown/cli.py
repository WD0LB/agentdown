import argparse
import os
import re
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

POLL_INTERVAL = 0.4
CLAUDE_HOME = Path.home() / ".claude"

FENCE_RE = re.compile(r"^(```|~~~)")
CHECKBOX_RE = re.compile(r"^(\s*[-*+]\s+)\[([ xX])\](\s+)")
INLINE_CODE_RE = re.compile(r"(`[^`]*`)")
FILE_LINE_RE = re.compile(r"(?<![\w/.])([\w][\w./-]*\.\w+):(\d+)\b")


def _highlight_file_refs(text: str) -> str:
    return FILE_LINE_RE.sub(lambda m: f"**{m.group(0)}**", text)


def _render_checkbox(match: "re.Match[str]") -> str:
    mark = "☑" if match.group(2).lower() == "x" else "☐"
    return f"{match.group(1)}{mark}{match.group(3)}"


def preprocess(text: str) -> str:
    """Rewrite GFM task-list checkboxes and file:line references before
    handing text to the markdown renderer, leaving fenced code blocks and
    inline code spans untouched."""
    out_lines = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue

        line = CHECKBOX_RE.sub(_render_checkbox, line)

        parts = INLINE_CODE_RE.split(line)
        for i in range(0, len(parts), 2):  # even indices = outside backticks
            parts[i] = _highlight_file_refs(parts[i])
        line = "".join(parts)

        out_lines.append(line)
    return "\n".join(out_lines)


def render(text: str, console: Console) -> None:
    console.print(Markdown(preprocess(text)))


def render_all(sources: list, console: Console) -> bool:
    """Render each source in order, with a divider between multiple sources.
    Returns True if any source failed to read."""
    had_error = False
    for i, source in enumerate(sources):
        if i > 0:
            console.print(Rule(style="dim"))

        if source == "-":
            render(sys.stdin.read(), console)
            continue

        try:
            with open(source, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"agentdown: {source}: {e.strerror}", file=sys.stderr)
            had_error = True
            continue

        render(text, console)

    return had_error


def _snapshot(files: list) -> dict:
    snapshot = {}
    for f in files:
        try:
            snapshot[f] = os.stat(f).st_mtime
        except OSError:
            snapshot[f] = None
    return snapshot


def watch(files: list, console: Console) -> None:
    def render_cycle() -> None:
        console.clear()
        render_all(files, console)
        console.print(Rule(style="dim"))
        console.print("[dim]Watching for changes — Ctrl+C to stop[/]")

    last = _snapshot(files)
    render_cycle()

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current = _snapshot(files)
            if current != last:
                last = current
                render_cycle()
    except KeyboardInterrupt:
        console.print()
        console.print("[dim]Stopped watching.[/]")


def _die(message: str) -> None:
    print(f"agentdown: {message}", file=sys.stderr)
    sys.exit(1)


def resolve_last_plan() -> str:
    plans_dir = CLAUDE_HOME / "plans"
    candidates = sorted(
        plans_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not candidates:
        _die(f"no plan files found in {plans_dir}")
    return str(candidates[0])


def resolve_claude_md() -> str:
    here = Path.cwd()
    for directory in [here, *here.parents]:
        candidate = directory / "CLAUDE.md"
        if candidate.is_file():
            return str(candidate)
    _die("no CLAUDE.md found in this directory or its parents")


def resolve_memory_files() -> list:
    encoded = "-" + str(Path.cwd()).strip("/").replace("/", "-")
    memory_dir = CLAUDE_HOME / "projects" / encoded / "memory"
    files = sorted(memory_dir.glob("*.md"))
    if not files:
        _die(f"no memory files found in {memory_dir}")
    return [str(f) for f in files]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agentdown",
        description="A terminal markdown viewer built for what AI coding agents write.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Markdown file(s) to render. Omit or pass '-' to read from stdin.",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Re-render whenever the given file(s) change. Requires at least one real file (not stdin).",
    )
    parser.add_argument(
        "--last-plan",
        action="store_true",
        help="Render the most recently modified plan in ~/.claude/plans/.",
    )
    parser.add_argument(
        "--claude-md",
        action="store_true",
        help="Render the nearest CLAUDE.md, searching upward from the current directory.",
    )
    parser.add_argument(
        "--memory",
        action="store_true",
        help="Render this project's Claude Code memory files.",
    )
    args = parser.parse_args()

    shortcuts = {
        "--last-plan": args.last_plan,
        "--claude-md": args.claude_md,
        "--memory": args.memory,
    }
    active = [name for name, flag in shortcuts.items() if flag]

    if len(active) > 1:
        _die(f"only one of {', '.join(active)} may be used at a time")
    if active and args.files:
        _die(f"cannot combine {active[0]} with explicit file arguments")

    console = Console()

    if args.last_plan:
        sources = [resolve_last_plan()]
    elif args.claude_md:
        sources = [resolve_claude_md()]
    elif args.memory:
        sources = resolve_memory_files()
    else:
        sources = args.files or ["-"]

    if args.watch:
        if "-" in sources:
            print("agentdown: --watch requires a file, not stdin", file=sys.stderr)
            sys.exit(1)
        watch(sources, console)
        sys.exit(0)

    had_error = render_all(sources, console)
    sys.exit(1 if had_error else 0)


if __name__ == "__main__":
    main()
