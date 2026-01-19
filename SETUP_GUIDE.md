# Setup Guide - Map Poster Generator

## Overview

This project uses **inline script dependencies** (PEP 723) with **uv** for automatic dependency management. This means:
- ✅ No manual `pip install` required
- ✅ No virtual environment setup needed
- ✅ Dependencies automatically managed
- ✅ Works consistently across all platforms

## Quick Start

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Run the Script

That's it! Just use `uv run`:

```bash
uv run create_map_poster.py -c "Paris" -C "France" -t noir
```

The first time you run it, uv will automatically:
1. Create an isolated environment
2. Install all required packages
3. Run the script

Subsequent runs are instant.

## How It Works

### Inline Script Dependencies (PEP 723)

The script includes its dependencies at the top:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "osmnx>=2.0.7",
#   "matplotlib>=3.10.8",
#   "geopandas>=1.1.2",
#   "geopy>=2.4.1",
#   "tqdm>=4.67.1",
#   "numpy>=2.4.0",
# ]
# ///
```

When you run `uv run create_map_poster.py`, uv:
1. Reads these inline dependencies
2. Creates a cached environment (first run only)
3. Installs the exact versions needed
4. Runs the script with those dependencies

## Different Ways to Run

### Method 1: Direct uv run (Recommended)

```bash
uv run create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink
```

**Pros:**
- Always works
- Automatic dependency management
- Clean and simple

### Method 2: Wrapper Script

```bash
./run.sh -c "Barcelona" -C "Spain" -t warm_beige -d 8000
```

**Pros:**
- Shorter command
- Same benefits as Method 1

### Method 3: Make it executable

```bash
./create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
```

**Note:** This still requires uv to be in your PATH for the shebang to work with inline dependencies.

## Why Not Just `python`?

Running `python create_map_poster.py` directly won't work because:

1. **Missing dependencies**: Your system Python doesn't have the required packages
2. **Version conflicts**: Different projects need different package versions
3. **Isolation issues**: Installing everything globally creates conflicts

Using `uv run` solves all these problems automatically.

## Troubleshooting

### "Command not found: uv"

You need to install uv first. See step 1 above.

### "ModuleNotFoundError: No module named 'osmnx'"

You're trying to run with `python` directly instead of `uv run`. Use:
```bash
uv run create_map_poster.py [options]
```

### First run is slow

The first time you run the script, uv needs to:
- Download all dependencies (~50MB)
- Set up the environment
- Cache everything for future use

This takes 30-60 seconds. Subsequent runs start instantly.

### Cache location

uv caches environments in:
- macOS/Linux: `~/.cache/uv/`
- Windows: `%LOCALAPPDATA%\uv\cache\`

To clear the cache:
```bash
uv cache clean
```

## Traditional Virtual Environment (Alternative)

If you prefer the traditional approach, you can still use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run normally
python create_map_poster.py -c "Paris" -C "France" -t noir
```

However, using `uv run` is simpler and doesn't require activation/deactivation.

## Requirements

- **Python**: 3.11 or higher
- **uv**: Latest version recommended
- **Operating System**: macOS, Linux, or Windows
- **Internet**: Required for downloading map data from OpenStreetMap

## What Gets Installed

When you run `uv run create_map_poster.py`, these packages are installed:

| Package | Purpose |
|---------|---------|
| osmnx | Download street network data from OpenStreetMap |
| matplotlib | Create and render the map visualizations |
| geopandas | Handle geographic data and shapefiles |
| geopy | Geocoding (city name → coordinates) |
| tqdm | Progress bars during data download |
| numpy | Numerical operations for gradients |

Plus their dependencies (~28 packages total, ~150MB).

## Pro Tips

1. **Alias for convenience**:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   alias mapgen="uv run create_map_poster.py"

   # Then use:
   mapgen -c "Tokyo" -C "Japan" -t noir
   ```

2. **Check themes without generating**:
   ```bash
   uv run create_map_poster.py --list-themes
   ```

3. **Test with small distance first**:
   ```bash
   # Fast test (2-3 minutes)
   uv run create_map_poster.py -c "Venice" -C "Italy" -t noir -d 2000

   # Full size after confirming it works
   uv run create_map_poster.py -c "Venice" -C "Italy" -t noir -d 8000
   ```

4. **Wrapper script for repeated use**:
   ```bash
   ./run.sh -c "Amsterdam" -C "Netherlands" -t ocean -d 6000
   ```

## Next Steps

- Read the main [README.md](README.md) for usage examples
- Browse available themes: `uv run create_map_poster.py --list-themes`
- Check out the [Hacker's Guide](README.md#hackers-guide) for customization

## Support

If you encounter issues:
1. Check that uv is installed: `uv --version`
2. Try clearing the cache: `uv cache clean`
3. Verify Python version: `python3 --version` (should be ≥3.11)
4. Make sure you're using `uv run`, not `python` directly
