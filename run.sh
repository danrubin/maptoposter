#!/bin/bash
# Wrapper script to run create_map_poster.py with uv
# This ensures dependencies are available

if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed."
    echo ""
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

# Run the script with uv, passing all arguments
exec uv run create_map_poster.py "$@"
