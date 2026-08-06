# agentdown

The terminal companion for AI coding agents. Tools like Claude Code, Codex, and
Antigravity constantly write markdown — plans, task checklists, reports, docs —
and none of it looks like more than a wall of `#` and `*` characters when you
just `cat` it. agentdown renders it properly: headers, bold/italic, lists,
tables, syntax-highlighted code blocks, blockquotes, links — straight to your
terminal.

```
$ agentdown plan.md
```

No pager, no images, no TUI. Just styled output, same spirit as `cat` — but
built around what agent output actually looks like: task checklists, file
references, and documents that get rewritten while you watch.

## Install

**Via pipx (recommended):**

```sh
pipx install git+https://github.com/WD0LB/agentdown.git
```

**Via the install script:**

```sh
curl -fsSL https://raw.githubusercontent.com/WD0LB/agentdown/main/install.sh | bash
```

Both install an `agentdown` command on your PATH. The script installs `pipx` first if you
don't already have it.

## Usage

```sh
agentdown notes.md              # render a single file
agentdown intro.md chapter1.md  # render multiple files, separated by a divider
cat notes.md | agentdown        # read from stdin
agentdown                       # no args = read from stdin
agentdown -w plan.md            # re-render whenever plan.md changes (Ctrl+C to stop)
```

Exits non-zero if any file couldn't be read. `--watch` requires at least one real
file — it can't watch stdin.

Task-list checkboxes (`- [ ]` / `- [x]`) render as ☐ / ☑, and plain-text
`path/to/file.py:42`-style references get highlighted — handy for the kind of
markdown coding agents write.

### Claude Code shortcuts

The renderer itself works on markdown from any tool. These specific shortcuts,
today, only know Claude Code's on-disk layout — support for other agents
(Codex, Antigravity, ...) is on the roadmap, not yet built. See
[ROADMAP.md](ROADMAP.md).

```sh
agentdown --last-plan        # render the most recently modified plan in ~/.claude/plans/
agentdown --claude-md        # render the nearest CLAUDE.md, searching upward from cwd
agentdown --memory           # render this project's Claude Code memory files
agentdown --last-plan -w     # shortcuts compose with --watch too
```

Only one shortcut can be used at a time, and none of them can be combined with
explicit file arguments.

## Development

```sh
git clone https://github.com/WD0LB/agentdown.git
cd agentdown
pip install -e .
agentdown README.md
```

## License

MIT
