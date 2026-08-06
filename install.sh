#!/usr/bin/env bash
# Installs agentdown via pipx. Works either:
#   - run from inside a cloned checkout of this repo (installs from local source), or
#   - curled directly (installs straight from GitHub)
set -euo pipefail

REPO_URL="https://github.com/WD0LB/agentdown.git"

if ! command -v pipx >/dev/null 2>&1; then
    echo "pipx not found — installing it with pip..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    echo "You may need to restart your shell (or run 'source ~/.bashrc') for PATH changes to take effect."
fi

# BASH_SOURCE[0] is only set when this script runs from a real file
# (e.g. `bash install.sh` or `./install.sh`). When piped via `curl | bash`,
# it's empty and $0 is just "bash" — falling back to $0 would resolve
# SCRIPT_DIR to the caller's unrelated cwd, so don't.
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR=""
fi

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    echo "Installing agentdown from local checkout ($SCRIPT_DIR)..."
    pipx install --force "$SCRIPT_DIR"
else
    echo "Installing agentdown from $REPO_URL..."
    pipx install --force "git+$REPO_URL"
fi

echo "Done. Try: agentdown README.md"
