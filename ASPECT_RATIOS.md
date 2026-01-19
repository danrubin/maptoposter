# Aspect Ratios & Resolutions Guide

## Overview

The map poster generator supports customizable aspect ratios and resolutions, allowing you to create posters optimized for any use case - from social media posts to large-format prints.

## Quick Start

```bash
# List available aspect ratio presets
uv run create_map_poster.py --list-ratios

# Use a preset
uv run create_map_poster.py -c "Paris" -C "France" --ratio square

# Use a custom ratio
uv run create_map_poster.py -c "Tokyo" -C "Japan" --ratio 16:9

# High-resolution for printing
uv run create_map_poster.py -c "Barcelona" -C "Spain" --ratio poster --dpi 600
```

## Aspect Ratio Presets

| Preset | Ratio | Dimensions (12" width) | Best For |
|--------|-------|------------------------|----------|
| `poster` | 3:4 | 12" × 16" (3600×4800px @ 300 DPI) | **Default** - Classic poster, wall art |
| `square` | 1:1 | 12" × 12" (3600×3600px) | Instagram posts, profile pictures |
| `landscape` | 4:3 | 12" × 9" (3600×2700px) | Standard landscape orientation |
| `wide` | 16:9 | 12" × 6.75" (3600×2025px) | Desktop wallpapers, presentations |
| `ultra` | 21:9 | 12" × 5.14" (3600×1543px) | Ultra-wide monitors |
| `tall` | 9:16 | 12" × 21.33" (3600×6400px) | Phone wallpapers, Stories |
| `a4` | 210:297 | 12" × 17" (3600×5091px) | A4 paper (portrait) |
| `letter` | 8.5:11 | 12" × 15.53" (3600×4659px) | US Letter (portrait) |

## Custom Ratios

Use the format `width:height` to specify any custom aspect ratio:

```bash
# Golden ratio (1.618:1)
uv run create_map_poster.py -c London -C UK --ratio 1.618:1

# Custom social media size
uv run create_map_poster.py -c NYC -C USA --ratio 4:5

# Panoramic
uv run create_map_poster.py -c "San Francisco" -C USA --ratio 3:1
```

## Resolution Control

### DPI (Dots Per Inch)

Control the output resolution with `--dpi`:

| DPI | Quality | Use Case | File Size |
|-----|---------|----------|-----------|
| 72 | Low | Quick preview, web thumbnails | Small (~1MB) |
| 150 | Medium | Web use, digital display | Medium (~5MB) |
| 300 | **High** | **Default** - Professional printing | Large (~15MB) |
| 600 | Very High | Large format prints, gallery quality | Very large (~60MB) |

```bash
# Web preview (fast generation)
uv run create_map_poster.py -c Paris -C France --ratio square --dpi 150

# Professional print
uv run create_map_poster.py -c Tokyo -C Japan --ratio poster --dpi 600

# Gallery quality large format
uv run create_map_poster.py -c Venice -C Italy --ratio wide --dpi 600
```

### Width Control

Adjust the base width in inches with `--width`:

```bash
# Small print (8" width)
uv run create_map_poster.py -c Barcelona -C Spain --ratio poster --width 8

# Large print (24" width)
uv run create_map_poster.py -c Mumbai -C India --ratio wide --width 24

# Custom size (16" width)
uv run create_map_poster.py -c Moscow -C Russia --ratio square --width 16
```

## How It Works

### Intelligent Map Centering

The system automatically adjusts the map bounding box based on your chosen aspect ratio:

```
Square (1:1)          Wide (16:9)         Tall (9:16)
┌──────────┐         ┌────────────────┐   ┌──────┐
│          │         │                │   │      │
│   Map    │         │      Map       │   │      │
│          │         │                │   │ Map  │
└──────────┘         └────────────────┘   │      │
                                           │      │
                                           └──────┘
```

- **Square ratios** (1:1): Equal coverage in all directions
- **Wide ratios** (16:9, 21:9): Extends horizontally to fill canvas
- **Tall ratios** (9:16, 3:4): Extends vertically to fill canvas

No stretching or distortion - the map data itself is fetched to match your canvas shape!

## Output Calculations

The system displays precise output dimensions:

```
Aspect ratio: 16:9
Resolution: 300 DPI
Canvas size: 12.0" × 6.8" (3600px × 2025px)
```

Formula:
- **Pixels** = `Width (inches) × DPI`
- **Height (inches)** = `Width × (Height Ratio / Width Ratio)`

## Common Use Cases

### Social Media

```bash
# Instagram post (square)
uv run create_map_poster.py -c Paris -C France --ratio 1:1 --width 10

# Instagram/Facebook post (4:5)
uv run create_map_poster.py -c NYC -C USA --ratio 4:5 --width 8

# Instagram/TikTok Stories (9:16)
uv run create_map_poster.py -c Tokyo -C Japan --ratio 9:16 --width 10

# Twitter/X header (3:1)
uv run create_map_poster.py -c London -C UK --ratio 3:1 --width 15
```

### Desktop Wallpapers

```bash
# Standard HD (16:9)
uv run create_map_poster.py -c Barcelona -C Spain --ratio 16:9 --width 16

# 4K display (16:9 at high DPI)
uv run create_map_poster.py -c Mumbai -C India --ratio 16:9 --width 32 --dpi 300

# Ultra-wide monitor (21:9)
uv run create_map_poster.py -c Dubai -C UAE --ratio 21:9 --width 21
```

### Printing

```bash
# Standard poster (18" × 24")
uv run create_map_poster.py -c Venice -C Italy --ratio 3:4 --width 18 --dpi 300

# Large format (24" × 36")
uv run create_map_poster.py -c Amsterdam -C Netherlands --ratio 2:3 --width 24 --dpi 300

# Gallery quality (36" × 48")
uv run create_map_poster.py -c Singapore -C Singapore --ratio 3:4 --width 36 --dpi 600

# A4 document print
uv run create_map_poster.py -c Rome -C Italy --ratio a4 --dpi 300

# Letter size print
uv run create_map_poster.py -c Chicago -C USA --ratio letter --dpi 300
```

### Mobile Devices

```bash
# iPhone wallpaper (9:19.5 approximate)
uv run create_map_poster.py -c Seoul -C "South Korea" --ratio 9:19.5 --width 6

# iPad wallpaper (3:4)
uv run create_map_poster.py -c Sydney -C Australia --ratio 3:4 --width 8
```

## Tips & Best Practices

### Choosing the Right Ratio

1. **Portrait cities** (tall buildings, skyscrapers): Use tall ratios (3:4, 9:16)
2. **Landscape cities** (coastlines, rivers): Use wide ratios (16:9, 21:9)
3. **Compact cities** (historic centers): Use square ratios (1:1)
4. **Mixed**: Use poster (3:4) as safe default

### Optimizing Distance

The `--distance` parameter works with aspect ratios:

```bash
# Wide ratio - increase distance to fill horizontal space
uv run create_map_poster.py -c Paris -C France --ratio 21:9 -d 15000

# Tall ratio - distance covers vertical space naturally
uv run create_map_poster.py -c NYC -C USA --ratio 9:16 -d 10000

# Square - balanced coverage
uv run create_map_poster.py -c Tokyo -C Japan --ratio 1:1 -d 12000
```

### Performance Considerations

| Resolution | Generation Time | Use When |
|------------|----------------|----------|
| 72 DPI | ~30 seconds | Testing themes/layouts |
| 150 DPI | ~60 seconds | Digital use, previews |
| 300 DPI | ~90 seconds | Most printing needs |
| 600 DPI | ~2-3 minutes | Gallery quality only |

Larger `--width` values don't significantly impact generation time, but higher DPI does.

### File Size Estimates

At 300 DPI:
- **Square (12×12")**: ~15MB
- **Wide (12×6.75")**: ~8MB
- **Tall (12×21")**: ~25MB
- **Poster (12×16")**: ~20MB

At 600 DPI, multiply by ~4x.

## Examples Gallery

### Same City, Different Ratios

```bash
# Paris in different formats
uv run create_map_poster.py -c Paris -C France --ratio poster -t noir        # Wall art
uv run create_map_poster.py -c Paris -C France --ratio square -t pastel_dream # Instagram
uv run create_map_poster.py -c Paris -C France --ratio 16:9 -t blueprint      # Desktop
uv run create_map_poster.py -c Paris -C France --ratio 9:16 -t warm_beige     # Phone
```

### Thematic Combinations

```bash
# Coastal city + wide ratio
uv run create_map_poster.py -c "San Francisco" -C USA --ratio 21:9 -t ocean -d 12000

# Dense urban + square
uv run create_map_poster.py -c Tokyo -C Japan --ratio 1:1 -t japanese_ink -d 15000

# Historic center + portrait
uv run create_map_poster.py -c Rome -C Italy --ratio 3:4 -t warm_beige -d 8000
```

## Troubleshooting

**Map looks empty or too zoomed out:**
- Reduce `--distance` value
- Wide ratios may need less distance

**Map is too zoomed in:**
- Increase `--distance` value
- Tall ratios may need more distance

**File size too large:**
- Reduce `--dpi` (300 is usually sufficient for prints up to 24")
- Reduce `--width` if you don't need such large dimensions

**Generation too slow:**
- Use `--dpi 150` for previews
- Test with smaller `--distance` first
- Use `--dpi 300` only for final output

## Advanced: Pixel-Perfect Sizing

For exact pixel dimensions, use this formula:

```
Width (px) = Width (inches) × DPI
Height (px) = Width (px) × (Height Ratio / Width Ratio)
```

Example for 1920×1080 desktop wallpaper:
```bash
# 1920px ÷ 300 DPI = 6.4"
# 16:9 ratio
uv run create_map_poster.py -c Barcelona -C Spain --ratio 16:9 --width 6.4 --dpi 300
# Output: 1920px × 1080px
```

Example for 3600×3600 Instagram post:
```bash
# 3600px ÷ 300 DPI = 12"
# 1:1 ratio
uv run create_map_poster.py -c London -C UK --ratio 1:1 --width 12 --dpi 300
# Output: 3600px × 3600px
```
