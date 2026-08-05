# agentdown — ideas / not yet built

Things discussed, some now implemented, some intentionally deferred.

## Done

- **`file:line` reference highlighting** — plain-text references like
  `src/cli.py:42` are bolded before rendering. Refs already inside inline
  code spans or fenced code blocks are left untouched (rich's own code
  styling applies instead), and a lookbehind guard keeps it from
  false-triggering on `scheme://host:port` URLs. Implemented as a text
  preprocessing pass in `preprocess()` (`src/agentdown/cli.py`) — reuses
  markdown's own `**bold**` emphasis rather than touching rich's rendering
  internals. Heuristic, not perfect (e.g. `1.2:3`-shaped false positives
  are possible), but works well for the common code-reference case.
- **Real checkbox rendering** — `- [ ]` / `- [x]` (and `*`/`+` bullets,
  any nesting depth) are rewritten to ☐/☑ in the same preprocessing pass,
  before rich ever sees them. rich previously printed these as literal
  bracket text (confirmed by testing).
- **Watch / live-reload mode** — `agentdown -w file.md ...` re-renders whenever
  the given file(s) change. Implemented via mtime polling every 0.4s
  (`_snapshot()`/`watch()` in `src/agentdown/cli.py`) rather than a file-watching
  dependency, to keep the tool dependency-free. Clears the screen and
  re-runs the normal render path on change; Ctrl+C exits with a short
  "Stopped watching." message instead of a traceback. Rejects stdin (`-w -`
  or no file args) with a clear error since there's nothing to poll.
  Verified end-to-end: initial render, detects an on-disk change and
  re-renders the new content, and handles SIGINT gracefully.
- **Ecosystem-aware shortcuts** — `--last-plan` (most recently modified file
  in `~/.claude/plans/`), `--claude-md` (nearest `CLAUDE.md`, walking up from
  cwd), and `--memory` (this project's memory `.md` files, resolved via
  Claude Code's `-`-joined project-path encoding under
  `~/.claude/projects/<encoded-cwd>/memory/`). Implemented in
  `resolve_last_plan()` / `resolve_claude_md()` / `resolve_memory_files()`
  (`src/agentdown/cli.py`); all three feed the same `sources` list used by
  normal rendering and `--watch`, so e.g. `agentdown --last-plan -w` works.
  Mutually exclusive with each other and with explicit file arguments.
  The project-path encoding is Claude Code's internal convention (observed,
  not a documented API) — same fragility caveat as the JSONL schema below,
  though the blast radius here is just "shortcut stops resolving," not
  a broken parse.

## Bigger, generalized: AI conversation-history viewer

Idea: a viewer for AI coding tools' stored conversation history, not scoped
to Claude Code alone. Deliberately parked — this is architecturally a
different problem (parsing each tool's storage format, not rendering
markdown a user already has) and needs to be designed as **pluggable
adapters** feeding one common renderer, since every tool stores history
differently:

- **Claude Code** — confirmed by direct inspection: `.jsonl` at
  `~/.claude/projects/<project-path>/<session-id>.jsonl`. Internal,
  undocumented, versioned schema (`user`/`assistant`/`tool_use`/
  `tool_result`/`thinking` blocks, parent/child UUID threading for
  subagent branches, plus bookkeeping events). Can change across
  Claude Code releases without notice — a real fragility risk for
  any parser built against it.
- **Aider** — believed to store history as a literal markdown file
  (`.aider.chat.history.md`) in the project root. *Unconfirmed —
  needs verification against an actual Aider install before relying
  on it.*
- **Cursor / Windsurf / other VS Code–based tools** — believed to store
  chat state inside a SQLite `state.vscdb` in `workspaceStorage`, as
  serialized JSON blobs. *Unconfirmed, likely to vary by version.*
- **Others** (Codex CLI, GitHub Copilot Chat, etc.) — format unknown,
  not yet investigated.

Shape for later: each adapter normalizes its source into a common
"turn" model (role, text, tool calls, timestamp), and a single
rich-based renderer displays any of them the same way — tool calls
collapsed to one-liners, user/assistant turns visually distinct,
code blocks syntax-highlighted.

Open question for when this gets picked up: does it live inside `agentdown`
as a subcommand, or as a separate sibling tool sharing the rendering
engine? (Leaning separate, to keep `agentdown` itself simple and insulated
from schema breakage — see prior discussion.)
