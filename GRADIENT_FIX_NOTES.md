# Gradient Distortion Fix - Technical Notes

## Problem Diagnosis

The gradient fade effect was causing map distortion on certain maps due to:

1. **Axis Limit Changes**: `ax.imshow()` with `aspect='auto'` can modify axis limits
2. **Aspect Ratio Conflicts**: The gradient overlay interferes with the map's coordinate system
3. **OSMnx Projection Issues**: Different maps have different coordinate systems and aspect ratios

## Primary Fix Applied (v1)

**Location**: `create_map_poster.py` lines 117-158

**Changes**:
- Store axis limits before creating gradient
- Explicitly restore axis limits after `imshow()` using `ax.set_xlim()` and `ax.set_ylim()`
- Added `interpolation='bilinear'` for smoother gradients
- Added inline documentation

**Key Code**:
```python
# Store limits BEFORE gradient
xlim = ax.get_xlim()
ylim = ax.get_ylim()

# ... create gradient ...

# CRITICAL: Restore limits AFTER gradient
ax.set_xlim(xlim)
ax.set_ylim(ylim)
```

## Testing the Fix

Run the test script:
```bash
python test_gradient_fix.py
```

This generates a small Venice map (2000m radius) with gradients enabled.

**What to check in the output**:
- ✓ No stretching or compression of the map
- ✓ Smooth gradient fades at top and bottom (25% coverage each)
- ✓ Roads maintain correct proportions
- ✓ Text positioned correctly at bottom

## Alternative Fix (if v1 doesn't work)

If you still see distortion, try this alternative approach using polygon fills instead of imshow:

```python
def create_gradient_fade_v2(ax, color, location='bottom', zorder=10):
    """
    Alternative gradient using transparent polygons instead of imshow.
    More reliable for preserving axis geometry.
    """
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]

    # Number of gradient steps
    steps = 100

    if location == 'bottom':
        y_start = ylim[0]
        y_end = ylim[0] + y_range * 0.25
    else:
        y_start = ylim[0] + y_range * 0.75
        y_end = ylim[1]

    # Create gradient using stacked rectangles
    rgb = mcolors.to_rgb(color)
    for i in range(steps):
        y = y_start + (y_end - y_start) * i / steps
        height = (y_end - y_start) / steps

        # Calculate alpha
        if location == 'bottom':
            alpha = 1 - (i / steps)
        else:
            alpha = i / steps

        rect = Rectangle((xlim[0], y), x_range, height,
                        facecolor=rgb, edgecolor='none',
                        alpha=alpha, zorder=zorder)
        ax.add_patch(rect)

    # Ensure limits are preserved
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
```

## Common Distortion Patterns

**Pattern 1: Vertical Stretching**
- Map appears taller/narrower than it should
- Cause: Y-axis limits changed by imshow
- Fix: Restore ylim after gradient

**Pattern 2: Horizontal Compression**
- Map appears wider/shorter than it should
- Cause: X-axis limits changed by imshow
- Fix: Restore xlim after gradient

**Pattern 3: Non-uniform Scaling**
- Different distortion in different areas
- Cause: Aspect ratio conflict between data and display coordinates
- Fix: Use alternative polygon-based gradient (v2 above)

## Debugging Commands

Check if gradients are causing issues:

```python
# Add before gradient:
print(f"Before gradient: xlim={ax.get_xlim()}, ylim={ax.get_ylim()}")

# Add after gradient:
print(f"After gradient: xlim={ax.get_xlim()}, ylim={ax.get_ylim()}")
```

If limits change between these prints, the distortion is confirmed.

## OSMnx Coordinate Systems

Different cities use different projections:
- **High latitude cities** (e.g., Stockholm, Anchorage): More aspect ratio distortion
- **Equatorial cities** (e.g., Singapore, Nairobi): Less distortion
- **Coastal vs inland**: Can affect bounding box aspect ratio

The fix should work regardless of coordinate system, but some edge cases may exist.

## Performance Notes

- Current fix adds negligible overhead (~1ms)
- Alternative v2 fix is slower (~50-100ms) but more reliable
- Both fixes maintain visual quality

## If Issues Persist

1. Try the alternative polygon-based gradient (v2)
2. Reduce gradient coverage from 25% to 15%
3. Disable gradients for specific problematic themes
4. Report the issue with specific city/theme combination
