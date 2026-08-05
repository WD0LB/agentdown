#!/usr/bin/env bash
# Installs agentdown via pipx. Works either:
#   - run from inside a cloned checkout of this repo (installs from local source), or
#   - curled directly (installs straight from GitHub)
set -euo pipefail

REPO_URL="https://github.com/<your-username>/agentdown.git"

if ! command -v pipx >/dev/null 2>&1; then
    echo "pipx not found — installing it with pip..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    echo "You may need to restart your shell (or run 'source ~/.bashrc') for PATH changes to take effect."
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    echo "Installing agentdown from local checkout ($SCRIPT_DIR)..."
    pipx install --force "$SCRIPT_DIR"
else
    echo "Installing agentdown from $REPO_URL..."
    pipx install --force "git+$REPO_URL"
fi

echo "Done. Try: agentdown README.md"
