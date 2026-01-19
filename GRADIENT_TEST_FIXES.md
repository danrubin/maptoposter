# Gradient Distortion - Alternative Fixes to Test

## Current Issue
Margate with forest theme at 2000m distance still shows distortion with the current fix.

## Root Cause
The original fix used `imshow()` which interacts with matplotlib's data coordinate system. Even with axis limit restoration, `aspect='auto'` can cause distortion depending on the map's aspect ratio.

## New Approach: Fix #1 (ACTIVE)

**Strategy:** Use `transAxes` coordinate system instead of data coordinates

**How it works:**
- Creates 100 thin Rectangle patches
- Uses `transform=ax.transAxes` which is normalized (0-1) coordinates
- Completely independent of xlim/ylim data coordinates
- No interaction with map coordinate system = no distortion

**Code location:** `create_map_poster.py` lines 133-175

**Test with:**
```bash
cd /Users/danrubin/Documents/GitHub/maptoposter
uv run create_map_poster.py --city "Margate" --country "UK" -t forest -d 2000
```

**What to check:**
- ✓ Map should maintain correct proportions
- ✓ Gradients appear smooth at top 25% and bottom 25%
- ✓ No stretching or compression
- ✓ Roads/features maintain natural shapes

---

## Alternative Fix #2 (Commented Out)

**Strategy:** Use `imshow()` but with calculated aspect ratio

**To test this:**
1. Comment out lines 133-175 (Fix #1)
2. Uncomment lines 180-223 (Fix #2)
3. Run the same test command

**Pros:** Uses original imshow approach, potentially smoother
**Cons:** Still uses data coordinates, may have edge cases

---

## Alternative Fix #3 (Commented Out)

**Strategy:** Similar to Fix #1 but with fewer steps

**To test this:**
1. Comment out lines 133-175 (Fix #1)
2. Uncomment lines 228-261 (Fix #3)
3. Run the same test command

**Pros:** Faster rendering (50 vs 100 steps)
**Cons:** Slightly less smooth gradient

---

## Test Matrix

Test each fix with these problematic cases:

### Case 1: Small Distance (Known Issue)
```bash
uv run create_map_poster.py --city "Margate" --country "UK" -t forest -d 2000
```
- **Issue:** Small area, high zoom, prone to distortion
- **Expected:** Natural coastline shape, no oval distortion

### Case 2: Grid Pattern (Easy to Spot Distortion)
```bash
uv run create_map_poster.py --city "Barcelona" --country "Spain" -t warm_beige -d 8000
```
- **Issue:** Eixample grid should be squares, not rectangles
- **Expected:** Perfect square grid blocks

### Case 3: Circular Features
```bash
uv run create_map_poster.py --city "Paris" --country "France" -t noir -d 10000
```
- **Issue:** Arc de Triomphe and roundabouts should be circular
- **Expected:** Round features remain round, not oval

### Case 4: High Latitude
```bash
uv run create_map_poster.py --city "Stockholm" --country "Sweden" -t blueprint -d 10000
```
- **Issue:** High latitude maps have different projection distortion
- **Expected:** Natural shapes, no added distortion from gradients

### Case 5: Waterfront (Venice - Previously Tested)
```bash
uv run create_map_poster.py --city "Venice" --country "Italy" -t noir -d 2000
```
- **Issue:** Canal shapes should be natural
- **Expected:** Organic canal network, not distorted

---

## Performance Comparison

| Fix | Method | Steps | Speed | Quality |
|-----|--------|-------|-------|---------|
| #1  | transAxes patches | 100 | ~50ms | Smooth |
| #2  | imshow + aspect | 1 | ~5ms | Very smooth |
| #3  | transAxes patches | 50 | ~25ms | Good |

---

## If Distortion Persists

If Fix #1 still shows distortion, it means the issue is elsewhere:

1. **Check if gradients are the problem:**
   ```bash
   # Comment out lines 322-323 to disable gradients
   # create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
   # create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)
   ```
   If distortion disappears, gradients are the culprit.
   If distortion remains, the issue is in the map rendering itself.

2. **Check OSMnx graph plotting:**
   The `ox.plot_graph()` call might be causing distortion. Check if `bgcolor` parameter affects aspect ratio.

3. **Check figure setup:**
   Line 281: `fig, ax = plt.subplots(figsize=(12, 16), facecolor=THEME['bg'])`
   The 12x16 aspect ratio might interact badly with certain map aspect ratios.

---

## Reporting Results

When testing, please report:
1. Which fix you tested (1, 2, or 3)
2. Which test case(s) showed distortion
3. Description of distortion (stretched, compressed, which direction)
4. Screenshot if possible

Example:
```
Tested: Fix #1
Case: Margate forest 2000m
Result: Still shows horizontal compression
Notes: Coastline appears squished, canals too narrow
```

---

## Quick Fix Toggle

To quickly disable gradients while testing other features:
```python
# In create_map_poster.py around line 322, change:
create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)

# To:
pass  # Gradients temporarily disabled
# create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
# create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)
```
