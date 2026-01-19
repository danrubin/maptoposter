# Changelog

## [Unreleased] - 2026-01-19

### Added
- **Dynamic text scaling for city names** - Long city names now automatically scale down to prevent cutoff while short names use full size (create_map_poster.py:196-226)
- **Custom typeface support** - Can now use any typeface by placing font files in `fonts/` directory and updating one line of code (create_map_poster.py:23-69)
- **Inline script dependencies (PEP 723)** - Script now manages its own dependencies automatically when run with `uv run` (create_map_poster.py:6-16)
- **Wrapper script** - Added `run.sh` for convenient execution
- **Setup script** - Added `setup.sh` to check uv installation
- **Comprehensive documentation**:
  - `SETUP_GUIDE.md` - Complete setup and troubleshooting guide
  - `GRADIENT_FIX_NOTES.md` - Technical documentation for gradient fix
  - `TESTING_GRADIENT_FIX.md` - Testing procedures for gradient distortion
- **Shebang line** - Script now has proper `#!/usr/bin/env python3` header
- **Module docstring** - Added description at top of script

### Fixed
- **Gradient distortion bug** - Fixed map distortion caused by gradient overlays by explicitly restoring axis limits after gradient application (create_map_poster.py:100-141)
  - Root cause: `ax.imshow()` was modifying axis limits
  - Solution: Store limits before gradient, restore after
  - Impact: Gradients can now be safely enabled without map distortion
- **macOS execution issue** - Script can now be run with `uv run` instead of requiring workarounds
  - Added inline dependency metadata for automatic environment management
  - No longer requires manual virtual environment setup

### Changed
- **README.md** - Updated with:
  - Simplified installation using uv
  - Updated all command examples to use `uv run`
  - Added custom typeface documentation section
  - Added dynamic text scaling documentation
  - Updated Hacker's Guide function table
  - Corrected line number reference for font loading (line 69)
- **Font loading function** - Now accepts `typeface` parameter with inline usage examples (create_map_poster.py:23-69)
- **Typography section** - Now uses dynamic font sizing instead of fixed 60pt (create_map_poster.py:276-296)
- **Gradient function** - Enhanced with better comments and bilinear interpolation (create_map_poster.py:100-141)

### Technical Details

#### Dynamic Text Scaling Algorithm
- Base size: 60pt for short names
- Minimum size: 30pt for very long names
- Threshold: 15 characters (accounting for spacing)
- Scaling: Linear interpolation based on length
- Formula: Accounts for "  ".join() character spacing

#### Gradient Fix Implementation
```python
# Store limits before gradient
xlim = ax.get_xlim()
ylim = ax.get_ylim()

# ... apply gradient with imshow() ...

# Critical fix: Restore limits after gradient
ax.set_xlim(xlim)
ax.set_ylim(ylim)
```

#### Inline Dependencies (PEP 723)
```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "osmnx>=2.0.7",
#   "matplotlib>=3.10.8",
#   ...
# ]
# ///
```

### Dependencies
- Python 3.11+ (was 3.9+, updated for numpy 2.4.0 compatibility)
- osmnx >= 2.0.7
- matplotlib >= 3.10.8
- geopandas >= 1.1.2
- geopy >= 2.4.1
- tqdm >= 4.67.1
- numpy >= 2.4.0

### Files Modified
- `create_map_poster.py` - Core script with all improvements
- `README.md` - Updated documentation
- `setup.sh` - Setup verification script
- `run.sh` - Wrapper for convenient execution (new)

### Files Added
- `SETUP_GUIDE.md` - Complete setup documentation
- `GRADIENT_FIX_NOTES.md` - Technical gradient fix documentation
- `TESTING_GRADIENT_FIX.md` - Testing procedures
- `CHANGELOG.md` - This file
- `test_gradient_fix.py` - Automated test script

### Breaking Changes
None - all changes are backward compatible. Existing command-line usage remains the same, just use `uv run` prefix.

### Migration Guide

**From `python create_map_poster.py` to `uv run create_map_poster.py`:**

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Replace `python` with `uv run` in all commands
3. First run will install dependencies automatically
4. Subsequent runs are instant

**Old way:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_map_poster.py -c "Paris" -C "France" -t noir
```

**New way:**
```bash
uv run create_map_poster.py -c "Paris" -C "France" -t noir
```

### Testing Notes
- Gradient fix tested successfully with `uv run --help`
- Dynamic scaling algorithm handles cities from 3 to 30+ characters
- Inline dependencies work on macOS with Python 3.13.5
- All wrapper scripts tested and functional

### Known Issues
None currently identified.

### Future Improvements
- Add command-line flag for custom typeface selection
- Add font size override option
- Consider polygon-based gradient as alternative (see GRADIENT_FIX_NOTES.md)
- Add automated tests for text scaling
- Add visual regression tests for gradient distortion
