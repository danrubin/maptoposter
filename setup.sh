#!/bin/bash
# Setup script for Map Poster Generator

set -e

echo "======================================================"
echo "Map Poster Generator - Setup"
echo "======================================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' is not installed."
    echo ""
    echo "Please install uv first:"
    echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Windows:     powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    echo ""
    exit 1
fi

echo "✓ Found uv: $(which uv)"
echo "✓ Script uses inline dependency management (PEP 723)"
echo ""
echo "======================================================"
echo "✓ Setup Complete!"
echo "======================================================"
echo ""
echo "The script automatically manages its dependencies using 'uv run'."
echo "No additional setup required!"
echo ""
echo "Run the script using:"
echo "  uv run create_map_poster.py [options]"
echo ""
echo "Or use the convenient wrapper:"
echo "  ./run.sh [options]"
echo ""
echo "Example:"
echo "  uv run create_map_poster.py -c \"Paris\" -C \"France\" -t noir"
echo "  ./run.sh -c \"Venice\" -C \"Italy\" -t blueprint -d 4000"
echo ""
