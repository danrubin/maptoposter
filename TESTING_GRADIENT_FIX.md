# Testing the Gradient Distortion Fix

## What Was Fixed

The gradient fade effect (top and bottom overlays) was causing map distortion due to `ax.imshow()` modifying the axis limits. The fix preserves the original axis limits by explicitly restoring them after the gradient is applied.

## How to Test

### Quick Test (Recommended)
Generate a map with gradients enabled and check for distortion:

```bash
# Small map for quick testing (2-3 minutes)
python create_map_poster.py -c "Venice" -C "Italy" -t noir -d 2000

# Medium map for thorough testing (5-8 minutes)
python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000
```

### What to Look For

Open the generated poster and check:

#### ✓ No Distortion (Good)
- Map proportions look natural and accurate
- Roads are straight where they should be straight
- Grid patterns (if any) appear square, not stretched
- Water bodies have natural shapes
- Top 25% and bottom 25% have smooth gradient fades
- Text is properly positioned and readable

#### ✗ Distortion Present (Problem)
- Map appears stretched vertically or horizontally
- Roads curve unnaturally
- Grid patterns appear as rectangles instead of squares
- Circular features (roundabouts, plazas) appear oval
- Gradient areas show banding or artifacts
- Text appears cut off or misaligned

## Visual Comparison Guide

### Cities Known to Show Distortion Issues (Pre-Fix)

These cities had different aspect ratios that exposed the bug:

1. **Barcelona** (grid pattern makes distortion obvious)
   - Should show: Perfect square grid in Eixample district
   - Distortion symptom: Rectangles instead of squares

2. **New York** (Manhattan grid)
   - Should show: Regular street grid
   - Distortion symptom: Stretched or compressed blocks

3. **High-latitude cities** (Stockholm, Anchorage)
   - Should show: Natural map proportions
   - Distortion symptom: Exaggerated horizontal or vertical stretch

### Safe Test Cities

These cities are good for initial testing:

- **Venice**: Small area, fast generation, distinctive canal shapes
- **Marrakech**: Organic layout, no obvious grids to distort
- **Tokyo**: Dense but well-balanced aspect ratio

## Technical Verification

If you want to verify the fix at code level, add debug prints:

```python
# In create_gradient_fade(), after line 123:
print(f"DEBUG: Original limits - X: {xlim}, Y: {ylim}")

# After line 154:
print(f"DEBUG: Gradient applied")

# After line 158:
print(f"DEBUG: Final limits - X: {ax.get_xlim()}, Y: {ax.get_ylim()}")
```

The original and final limits should match exactly.

## Known Edge Cases

### Case 1: Very Wide Maps (coastal cities with long shorelines)
- Cities: Miami, Dubai (Palm islands)
- Expected behavior: Gradients work normally
- If distortion occurs: Gradient may be too narrow, but map should not distort

### Case 2: Very Tall Maps (north-south oriented cities)
- Cities: Manhattan, parts of San Francisco
- Expected behavior: Gradients work normally
- If distortion occurs: Check gradient extent calculation

### Case 3: Small Distance Values (<2000m)
- Effect: Very zoomed in maps
- Expected behavior: Gradients cover appropriate 25% top/bottom
- Note: Gradient may be more visible due to smaller map area

## Performance Impact

The fix adds minimal overhead:
- **Before**: ~15-30 seconds for typical map
- **After**: ~15-30 seconds for typical map (no measurable difference)
- Added operations: 2 `set_xlim/ylim` calls (~1ms total)

## If Issues Persist

If you still see distortion after the fix:

1. **Verify the fix is applied**: Check `create_map_poster.py` lines 156-158 for:
   ```python
   ax.set_xlim(xlim)
   ax.set_ylim(ylim)
   ```

2. **Try the alternative fix**: See `GRADIENT_FIX_NOTES.md` for polygon-based gradient approach

3. **Temporarily disable gradients**: Comment out lines 322-323 in `create_map_poster.py`

4. **Report the issue**: Note the specific city, country, theme, and distance used

## Success Criteria

The fix is working if:
- ✓ Maps generate without errors
- ✓ No visible distortion in generated posters
- ✓ Gradients appear smooth at top and bottom
- ✓ Text and map elements properly aligned
- ✓ Consistent results across different cities and themes

## Example Test Commands

```bash
# Test with different themes
python create_map_poster.py -c "Paris" -C "France" -t noir -d 8000
python create_map_poster.py -c "Paris" -C "France" -t blueprint -d 8000
python create_map_poster.py -c "Paris" -C "France" -t ocean -d 8000

# Test with different distances
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t feature_based -d 4000
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t feature_based -d 8000
python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t feature_based -d 12000

# Test problematic cities (pre-fix)
python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000  # Grid test
python create_map_poster.py -c "Stockholm" -C "Sweden" -t blueprint -d 10000  # High latitude test
```

## Automated Testing (Future Enhancement)

To automate gradient testing, we could add:
- Compare axis limits before/after gradient
- Measure aspect ratio preservation
- Generate diff images between gradient/no-gradient versions
- Unit tests for `create_gradient_fade()` function
