#!/usr/bin/env python3
"""
City Map Poster Generator
Generate beautiful, minimalist map posters for any city in the world.
"""
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
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors
import numpy as np
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
import json
import os
from datetime import datetime
import argparse

THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

# Aspect ratio presets
ASPECT_RATIOS = {
    'poster': (3, 4),      # 3:4 - Classic poster (12x16 default)
    'square': (1, 1),      # 1:1 - Instagram square
    'landscape': (4, 3),   # 4:3 - Landscape orientation
    'wide': (16, 9),       # 16:9 - Widescreen
    'ultra': (21, 9),      # 21:9 - Ultra-wide
    'tall': (9, 16),       # 9:16 - Portrait/Stories
    'a4': (210, 297),      # A4 paper (portrait)
    'letter': (8.5, 11),   # US Letter (portrait)
}

def load_fonts(typeface='Roboto'):
    """
    Load fonts from the fonts directory.

    Args:
        typeface (str): Name of the typeface to use (default: 'Roboto')
                       Available options: 'Roboto' or any custom font family
                       with Bold, Regular, and Light weights in the fonts/ directory.

    Returns:
        dict: Font paths for different weights, or None if fonts not found.

    Usage:
        # Use default Roboto fonts
        fonts = load_fonts()

        # Use a custom typeface (ensure CustomFont-Bold.ttf, etc. are in fonts/)
        fonts = load_fonts('CustomFont')
    """
    fonts = {
        'bold': os.path.join(FONTS_DIR, f'{typeface}-Bold.ttf'),
        'regular': os.path.join(FONTS_DIR, f'{typeface}-Regular.ttf'),
        'light': os.path.join(FONTS_DIR, f'{typeface}-Light.ttf')
    }

    # Verify fonts exist
    for weight, path in fonts.items():
        if not os.path.exists(path):
            print(f"⚠ Font not found: {path}")
            return None

    return fonts

# Default to Roboto fonts (can be changed by modifying the argument below)
# To use a different typeface, replace 'Roboto' with your font name:
# FONTS = load_fonts('YourFontName')
FONTS = load_fonts('Roboto')

def generate_output_filename(city, theme_name):
    """
    Generate unique output filename with city, theme, and datetime.
    """
    if not os.path.exists(POSTERS_DIR):
        os.makedirs(POSTERS_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    city_slug = city.lower().replace(' ', '_')
    filename = f"{city_slug}_{theme_name}_{timestamp}.png"
    return os.path.join(POSTERS_DIR, filename)

def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []
    
    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes

def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")
    
    if not os.path.exists(theme_file):
        print(f"⚠ Theme file '{theme_file}' not found. Using default feature_based theme.")
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
            "bg": "#FFFFFF",
            "text": "#000000",
            "gradient_color": "#FFFFFF",
            "water": "#C0C0C0",
            "parks": "#F0F0F0",
            "road_motorway": "#0A0A0A",
            "road_primary": "#1A1A1A",
            "road_secondary": "#2A2A2A",
            "road_tertiary": "#3A3A3A",
            "road_residential": "#4A4A4A",
            "road_default": "#3A3A3A"
        }
    
    with open(theme_file, 'r') as f:
        theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if 'description' in theme:
            print(f"  {theme['description']}")
        return theme

# Load theme (can be changed via command line or input)
THEME = None  # Will be loaded later

def create_gradient_fade(ax, color, location='bottom', zorder=10):
    """
    Creates a fade effect using transform coordinates to avoid distortion.

    FIX APPROACH 3 (ACTIVE): Rectangle patches with transAxes (50 steps)
    - Same as Fix #1 but with 50 steps instead of 100 for better performance
    - Uses normalized axis coordinates (0-1) independent of data
    - No interaction with xlim/ylim, preventing distortion

    Note: Fix #1 (100 steps) worked but is commented out below.
    """
    from matplotlib.patches import Rectangle

    rgb = mcolors.to_rgb(color)
    steps = 50  # Fewer steps for better performance

    if location == 'bottom':
        y_start = 0
        y_end = 0.15  # Reduced from 0.25 to give text clean space
    else:
        y_start = 0.85  # Adjusted from 0.75 for symmetry
        y_end = 1.0

    # Create gradient using rectangles in axis coordinates
    for i in range(steps):
        y_pos = y_start + (y_end - y_start) * i / steps
        height = (y_end - y_start) / steps

        # Calculate alpha for gradient effect
        if location == 'bottom':
            alpha = 1 - (i / steps)  # Fade from opaque to transparent
        else:
            alpha = i / steps  # Fade from transparent to opaque

        rect = Rectangle((0, y_pos), 1, height,
                        transform=ax.transAxes,  # Use axis coordinates, not data
                        facecolor=rgb, edgecolor='none',
                        alpha=alpha, zorder=zorder)
        ax.add_patch(rect)


# FIX #1 - 100 steps (worked, but commented out in favor of faster 50-step version)
# def create_gradient_fade(ax, color, location='bottom', zorder=10):
#     from matplotlib.patches import Rectangle
#     rgb = mcolors.to_rgb(color)
#     steps = 100
#     if location == 'bottom':
#         y_start = 0
#         y_end = 0.25
#     else:
#         y_start = 0.75
#         y_end = 1.0
#     for i in range(steps):
#         y_pos = y_start + (y_end - y_start) * i / steps
#         height = (y_end - y_start) / steps
#         if location == 'bottom':
#             alpha = 1 - (i / steps)
#         else:
#             alpha = i / steps
#         rect = Rectangle((0, y_pos), 1, height,
#                         transform=ax.transAxes,
#                         facecolor=rgb, edgecolor='none',
#                         alpha=alpha, zorder=zorder,
#                         clip_on=False)
#         ax.add_patch(rect)


# ALTERNATIVE FIX 2: imshow with explicit aspect ratio
# Uncomment to test this approach
# def create_gradient_fade(ax, color, location='bottom', zorder=10):
#     """
#     FIX APPROACH 2: imshow with locked aspect ratio
#     Uses imshow but locks axis aspect ratio before and after
#     """
#     xlim = ax.get_xlim()
#     ylim = ax.get_ylim()
#
#     # Calculate and lock aspect ratio
#     x_range = xlim[1] - xlim[0]
#     y_range = ylim[1] - ylim[0]
#     aspect_ratio = y_range / x_range
#
#     vals = np.linspace(0, 1, 256).reshape(-1, 1)
#     gradient = np.hstack((vals, vals))
#
#     rgb = mcolors.to_rgb(color)
#     my_colors = np.zeros((256, 4))
#     my_colors[:, 0] = rgb[0]
#     my_colors[:, 1] = rgb[1]
#     my_colors[:, 2] = rgb[2]
#
#     if location == 'bottom':
#         my_colors[:, 3] = np.linspace(1, 0, 256)
#         extent_y_start = 0
#         extent_y_end = 0.25
#     else:
#         my_colors[:, 3] = np.linspace(0, 1, 256)
#         extent_y_start = 0.75
#         extent_y_end = 1.0
#
#     custom_cmap = mcolors.ListedColormap(my_colors)
#     y_bottom = ylim[0] + y_range * extent_y_start
#     y_top = ylim[0] + y_range * extent_y_end
#
#     # Use calculated aspect ratio instead of 'auto'
#     im = ax.imshow(gradient, extent=[xlim[0], xlim[1], y_bottom, y_top],
#                    aspect=aspect_ratio * 4,  # Scale aspect for gradient region
#                    cmap=custom_cmap, zorder=zorder, origin='lower',
#                    interpolation='bilinear')
#
#     # Restore limits
#     ax.set_xlim(xlim)
#     ax.set_ylim(ylim)


# ALTERNATIVE FIX 3: FancyBboxPatch with gradient
# Uncomment to test this approach
# def create_gradient_fade(ax, color, location='bottom', zorder=10):
#     """
#     FIX APPROACH 3: Polygon fill with gradient simulation
#     Uses fill_between in axis coordinates
#     """
#     import matplotlib.patches as mpatches
#     from matplotlib.path import Path
#
#     rgb = mcolors.to_rgb(color)
#     steps = 50  # Fewer steps for performance
#
#     if location == 'bottom':
#         y_start = 0
#         y_end = 0.25
#     else:
#         y_start = 0.75
#         y_end = 1.0
#
#     # Create gradient with fill_between
#     for i in range(steps):
#         y_low = y_start + (y_end - y_start) * i / steps
#         y_high = y_start + (y_end - y_start) * (i + 1) / steps
#
#         if location == 'bottom':
#             alpha = 1 - (i / steps)
#         else:
#             alpha = i / steps
#
#         # Create rectangle using axis transform
#         rect = mpatches.Rectangle((0, y_low), 1, y_high - y_low,
#                                   transform=ax.transAxes,
#                                   facecolor=rgb, edgecolor='none',
#                                   alpha=alpha, zorder=zorder)
#         ax.add_patch(rect)

def get_edge_colors_by_type(G):
    """
    Assigns colors to edges based on road type hierarchy.
    Returns a list of colors corresponding to each edge in the graph.
    """
    edge_colors = []
    
    for u, v, data in G.edges(data=True):
        # Get the highway type (can be a list or string)
        highway = data.get('highway', 'unclassified')
        
        # Handle list of highway types (take the first one)
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign color based on road type
        if highway in ['motorway', 'motorway_link']:
            color = THEME['road_motorway']
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            color = THEME['road_primary']
        elif highway in ['secondary', 'secondary_link']:
            color = THEME['road_secondary']
        elif highway in ['tertiary', 'tertiary_link']:
            color = THEME['road_tertiary']
        elif highway in ['residential', 'living_street', 'unclassified']:
            color = THEME['road_residential']
        else:
            color = THEME['road_default']
        
        edge_colors.append(color)
    
    return edge_colors

def get_edge_widths_by_type(G):
    """
    Assigns line widths to edges based on road type.
    Major roads get thicker lines.
    """
    edge_widths = []
    
    for u, v, data in G.edges(data=True):
        highway = data.get('highway', 'unclassified')
        
        if isinstance(highway, list):
            highway = highway[0] if highway else 'unclassified'
        
        # Assign width based on road importance
        if highway in ['motorway', 'motorway_link']:
            width = 1.2
        elif highway in ['trunk', 'trunk_link', 'primary', 'primary_link']:
            width = 1.0
        elif highway in ['secondary', 'secondary_link']:
            width = 0.8
        elif highway in ['tertiary', 'tertiary_link']:
            width = 0.6
        else:
            width = 0.4
        
        edge_widths.append(width)
    
    return edge_widths

def calculate_city_name_font_size(city, base_size=60, min_size=30, max_chars=15):
    """
    Calculate appropriate font size for city name based on length.
    Longer city names get smaller font sizes to prevent cutoff.

    Args:
        city (str): City name
        base_size (int): Font size for short city names (default: 60)
        min_size (int): Minimum font size for very long names (default: 30)
        max_chars (int): Character count at which scaling starts (default: 15)

    Returns:
        int: Calculated font size

    Usage:
        # Automatically scales based on city name length
        font_size = calculate_city_name_font_size("San Francisco")  # Returns ~48
        font_size = calculate_city_name_font_size("NYC")            # Returns 60
    """
    # Account for spacing added between characters
    spaced_length = len(city) * 3 - 2  # Each char + 2 spaces, except last char

    if spaced_length <= max_chars:
        return base_size

    # Linear scaling from base_size to min_size
    # Adjust scaling factor based on how much longer than max_chars
    scale_factor = max(min_size / base_size, 1 - (spaced_length - max_chars) / 50)
    calculated_size = int(base_size * scale_factor)

    return max(min_size, calculated_size)

def parse_aspect_ratio(ratio_str):
    """
    Parse aspect ratio from string format.

    Args:
        ratio_str (str): Ratio as 'preset' or 'width:height' (e.g., 'square', '16:9', '3:4')

    Returns:
        tuple: (width, height) ratio

    Examples:
        parse_aspect_ratio('square') → (1, 1)
        parse_aspect_ratio('16:9') → (16, 9)
        parse_aspect_ratio('poster') → (3, 4)
    """
    # Check if it's a preset
    if ratio_str in ASPECT_RATIOS:
        return ASPECT_RATIOS[ratio_str]

    # Parse custom ratio (e.g., "16:9" or "3:4")
    try:
        parts = ratio_str.split(':')
        if len(parts) == 2:
            width = float(parts[0])
            height = float(parts[1])
            return (width, height)
    except ValueError:
        pass

    raise ValueError(f"Invalid aspect ratio: '{ratio_str}'. Use a preset ({', '.join(ASPECT_RATIOS.keys())}) or format like '16:9'")


def calculate_figure_size(ratio, base_width=12):
    """
    Calculate figure size in inches based on aspect ratio.

    Args:
        ratio (tuple): (width, height) aspect ratio
        base_width (int): Base width in inches (default: 12)

    Returns:
        tuple: (width_inches, height_inches)

    Examples:
        calculate_figure_size((3, 4), 12) → (12, 16)
        calculate_figure_size((16, 9), 12) → (12, 6.75)
    """
    width_ratio, height_ratio = ratio
    height = base_width * (height_ratio / width_ratio)
    return (base_width, height)


def calculate_map_bbox(point, dist, aspect_ratio):
    """
    Calculate appropriate bounding box for map based on aspect ratio.

    For non-square ratios, adjusts the bbox to match the canvas shape,
    ensuring the map doesn't appear stretched or have excessive padding.

    Args:
        point (tuple): (latitude, longitude) center point
        dist (int): Base distance in meters
        aspect_ratio (tuple): (width, height) ratio

    Returns:
        dict: Bounding box parameters for osmnx with dist adjustments

    Examples:
        # Square (1:1) - equal in all directions
        calculate_map_bbox((lat, lon), 10000, (1, 1))

        # Wide (16:9) - extends horizontally
        calculate_map_bbox((lat, lon), 10000, (16, 9))

        # Tall (9:16) - extends vertically
        calculate_map_bbox((lat, lon), 10000, (9, 16))
    """
    width_ratio, height_ratio = aspect_ratio

    # Calculate distance multipliers based on ratio
    if width_ratio > height_ratio:
        # Landscape: extend horizontally
        dist_x = dist
        dist_y = dist * (height_ratio / width_ratio)
    elif height_ratio > width_ratio:
        # Portrait: extend vertically
        dist_x = dist * (width_ratio / height_ratio)
        dist_y = dist
    else:
        # Square: equal in all directions
        dist_x = dist
        dist_y = dist

    # Return custom bbox parameters
    # OSMnx bbox format: (north, south, east, west)
    lat, lon = point

    # Approximate degrees (rough conversion, works for visualization)
    # 1 degree latitude ≈ 111km
    # 1 degree longitude varies by latitude, but we'll use approximate
    lat_delta = (dist_y / 1000) / 111.0
    lon_delta = (dist_x / 1000) / (111.0 * abs(np.cos(np.radians(lat))))

    bbox = {
        'north': lat + lat_delta,
        'south': lat - lat_delta,
        'east': lon + lon_delta,
        'west': lon - lon_delta
    }

    return bbox


def get_coordinates(city, country):
    """
    Fetches coordinates for a given city and country using geopy.
    Includes rate limiting to be respectful to the geocoding service.
    """
    print("Looking up coordinates...")
    geolocator = Nominatim(user_agent="city_map_poster")

    # Add a small delay to respect Nominatim's usage policy
    time.sleep(1)

    location = geolocator.geocode(f"{city}, {country}")

    if location:
        print(f"✓ Found: {location.address}")
        print(f"✓ Coordinates: {location.latitude}, {location.longitude}")
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Could not find coordinates for {city}, {country}")

def create_poster(city, country, point, dist, output_file, aspect_ratio=(3, 4), dpi=300, base_width=12):
    """
    Create a map poster with customizable aspect ratio and resolution.

    Args:
        city (str): City name
        country (str): Country name
        point (tuple): (latitude, longitude) coordinates
        dist (int): Base distance in meters for map coverage
        output_file (str): Output file path
        aspect_ratio (tuple): (width, height) ratio (default: (3, 4) for poster)
        dpi (int): Resolution in dots per inch (default: 300)
        base_width (int): Base width in inches (default: 12)
    """
    print(f"\nGenerating map for {city}, {country}...")
    print(f"Aspect ratio: {aspect_ratio[0]}:{aspect_ratio[1]}")
    print(f"Resolution: {dpi} DPI")

    # Calculate map bounding box based on aspect ratio
    bbox = calculate_map_bbox(point, dist, aspect_ratio)

    # Progress bar for data fetching
    with tqdm(total=3, desc="Fetching map data", unit="step", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        # 1. Fetch Street Network using bbox
        # OSMnx 2.0 API: bbox parameter is (west, south, east, north)
        pbar.set_description("Downloading street network")
        G = ox.graph_from_bbox(
            bbox=(bbox['west'], bbox['south'], bbox['east'], bbox['north']),
            network_type='all'
        )
        pbar.update(1)
        time.sleep(0.5)  # Rate limit between requests

        # 2. Fetch Water Features using bbox
        pbar.set_description("Downloading water features")
        try:
            water = ox.features_from_bbox(
                bbox=(bbox['west'], bbox['south'], bbox['east'], bbox['north']),
                tags={'natural': 'water', 'waterway': 'riverbank'}
            )
        except:
            water = None
        pbar.update(1)
        time.sleep(0.3)

        # 3. Fetch Parks using bbox
        pbar.set_description("Downloading parks/green spaces")
        try:
            parks = ox.features_from_bbox(
                bbox=(bbox['west'], bbox['south'], bbox['east'], bbox['north']),
                tags={'leisure': 'park', 'landuse': 'grass'}
            )
        except:
            parks = None
        pbar.update(1)
    
    print("✓ All data downloaded successfully!")

    # 2. Setup Plot with calculated figure size
    print("Rendering map...")
    figsize = calculate_figure_size(aspect_ratio, base_width)
    print(f"Canvas size: {figsize[0]:.1f}\" × {figsize[1]:.1f}\" ({figsize[0]*dpi:.0f}px × {figsize[1]*dpi:.0f}px)")

    fig, ax = plt.subplots(figsize=figsize, facecolor=THEME['bg'])
    ax.set_facecolor(THEME['bg'])
    ax.set_position([0, 0, 1, 1])
    
    # 3. Plot Layers
    # Layer 1: Polygons
    if water is not None and not water.empty:
        water.plot(ax=ax, facecolor=THEME['water'], edgecolor='none', zorder=1)
    if parks is not None and not parks.empty:
        parks.plot(ax=ax, facecolor=THEME['parks'], edgecolor='none', zorder=2)
    
    # Layer 2: Roads with hierarchy coloring
    print("Applying road hierarchy colors...")
    edge_colors = get_edge_colors_by_type(G)
    edge_widths = get_edge_widths_by_type(G)
    
    ox.plot_graph(
        G, ax=ax, bgcolor=THEME['bg'],
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=edge_widths,
        show=False, close=False
    )
    
    # Layer 3: Gradients (Top and Bottom)
    create_gradient_fade(ax, THEME['gradient_color'], location='bottom', zorder=10)
    create_gradient_fade(ax, THEME['gradient_color'], location='top', zorder=10)

    # 4. Typography with dynamic font sizing
    # Calculate appropriate font size for city name based on length
    city_font_size = calculate_city_name_font_size(city)

    if FONTS:
        font_main = FontProperties(fname=FONTS['bold'], size=city_font_size)
        font_top = FontProperties(fname=FONTS['bold'], size=40)
        font_sub = FontProperties(fname=FONTS['light'], size=22)
        font_coords = FontProperties(fname=FONTS['regular'], size=14)
    else:
        # Fallback to system fonts
        font_main = FontProperties(family='monospace', weight='bold', size=city_font_size)
        font_top = FontProperties(family='monospace', weight='bold', size=40)
        font_sub = FontProperties(family='monospace', weight='normal', size=22)
        font_coords = FontProperties(family='monospace', size=14)

    spaced_city = "  ".join(list(city.upper()))

    # --- BOTTOM TEXT ---
    # Typographic hierarchy with proper leading (line spacing)
    # Based on standard typographic rhythm: 1.5x leading for body, 2x for display
    # Text zorder=15 ensures it appears above gradients (zorder=10)
    #
    # Vertical rhythm (bottom to top):
    # - Coordinates: 14pt text at y=0.07
    # - Country: 22pt text at y=0.10 (spacing: ~0.03 = 2x line height ratio)
    # - Line: decorative element at y=0.125 (0.025 above country)
    # - City: 60pt text at y=0.14 (spacing: 0.015 below city baseline)
    #
    # This maintains ~1.5-2x leading between elements for proper visual rhythm

    ax.text(0.5, 0.14, spaced_city, transform=ax.transAxes,
            color=THEME['text'], ha='center', fontproperties=font_main, zorder=15)

    ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes,
            color=THEME['text'], linewidth=1, zorder=15)

    ax.text(0.5, 0.10, country.upper(), transform=ax.transAxes,
            color=THEME['text'], ha='center', fontproperties=font_sub, zorder=15)

    lat, lon = point
    coords = f"{lat:.4f}° N / {lon:.4f}° E" if lat >= 0 else f"{abs(lat):.4f}° S / {lon:.4f}° E"
    if lon < 0:
        coords = coords.replace("E", "W")

    ax.text(0.5, 0.07, coords, transform=ax.transAxes,
            color=THEME['text'], alpha=0.7, ha='center', fontproperties=font_coords, zorder=15)

    # --- ATTRIBUTION (bottom right) ---
    if FONTS:
        font_attr = FontProperties(fname=FONTS['light'], size=8)
    else:
        font_attr = FontProperties(family='monospace', size=8)

    ax.text(0.98, 0.02, "© OpenStreetMap contributors", transform=ax.transAxes,
            color=THEME['text'], alpha=0.5, ha='right', va='bottom',
            fontproperties=font_attr, zorder=15)

    # 5. Save
    print(f"Saving to {output_file}...")
    plt.savefig(output_file, dpi=dpi, facecolor=THEME['bg'])
    plt.close()
    print(f"✓ Done! Poster saved as {output_file}")
    print(f"Final resolution: {figsize[0]*dpi:.0f}px × {figsize[1]*dpi:.0f}px")

def print_examples():
    """Print usage examples."""
    print("""
City Map Poster Generator
=========================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]

Examples:
  # Iconic grid patterns
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000           # Manhattan grid
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000   # Eixample district grid
  
  # Waterfront & canals
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000       # Canal network
  python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000  # Concentric canals
  python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000     # Palm & coastline
  
  # Radial patterns
  python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000   # Haussmann boulevards
  python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000          # Ring roads
  
  # Organic old cities
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000    # Dense organic streets
  python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000 # Medina maze
  python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000        # Ancient street layout
  
  # Coastal cities
  python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000    # Peninsula grid
  python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000      # Harbor city
  python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000 # Coastal peninsula
  
  # River cities
  python create_map_poster.py -c "London" -C "UK" -t noir -d 15000              # Thames curves
  python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000  # Danube split
  
  # List themes
  python create_map_poster.py --list-themes

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --theme, -t       Theme name (default: feature_based)
  --distance, -d    Map radius in meters (default: 29000)
  --list-themes     List all available themes

Distance guide:
  4000-6000m   Small/dense cities (Venice, Amsterdam old center)
  8000-12000m  Medium cities, focused downtown (Paris, Barcelona)
  15000-20000m Large metros, full city view (Tokyo, Mumbai)

Available themes can be found in the 'themes/' directory.
Generated posters are saved to 'posters/' directory.
""")

def list_themes():
    """List all available themes with descriptions."""
    available_themes = get_available_themes()
    if not available_themes:
        print("No themes found in 'themes/' directory.")
        return

    print("\nAvailable Themes:")
    print("-" * 60)
    for theme_name in available_themes:
        theme_path = os.path.join(THEMES_DIR, f"{theme_name}.json")
        try:
            with open(theme_path, 'r') as f:
                theme_data = json.load(f)
                display_name = theme_data.get('name', theme_name)
                description = theme_data.get('description', '')
        except:
            display_name = theme_name
            description = ''
        print(f"  {theme_name}")
        print(f"    {display_name}")
        if description:
            print(f"    {description}")
        print()


def list_aspect_ratios():
    """List all available aspect ratio presets."""
    print("\nAvailable Aspect Ratio Presets:")
    print("-" * 60)

    for name, (w, h) in ASPECT_RATIOS.items():
        # Calculate example dimensions at 12" width
        figsize = calculate_figure_size((w, h), 12)
        print(f"  {name:<12} {w}:{h:<8} → {figsize[0]:.1f}\" × {figsize[1]:.1f}\" (at 12\" width)")

    print("\nYou can also use custom ratios:")
    print("  Example: --ratio 16:9")
    print("  Example: --ratio 21:9")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate beautiful map posters for any city",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_map_poster.py --city "New York" --country "USA"
  python create_map_poster.py --city Tokyo --country Japan --theme midnight_blue
  python create_map_poster.py --city Paris --country France --theme noir --distance 15000
  python create_map_poster.py --list-themes
        """
    )
    
    parser.add_argument('--city', '-c', type=str, help='City name')
    parser.add_argument('--country', '-C', type=str, help='Country name')
    parser.add_argument('--theme', '-t', type=str, default='feature_based', help='Theme name (default: feature_based)')
    parser.add_argument('--distance', '-d', type=int, default=29000, help='Map radius in meters (default: 29000)')
    parser.add_argument('--ratio', '-r', type=str, default='poster',
                       help=f'Aspect ratio: preset ({", ".join(ASPECT_RATIOS.keys())}) or custom (e.g., 16:9) (default: poster)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='Resolution in dots per inch (default: 300)')
    parser.add_argument('--width', '-w', type=int, default=12,
                       help='Base width in inches (default: 12)')
    parser.add_argument('--list-themes', action='store_true', help='List all available themes')
    parser.add_argument('--list-ratios', action='store_true', help='List all available aspect ratio presets')
    
    args = parser.parse_args()
    
    # If no arguments provided, show examples
    if len(os.sys.argv) == 1:
        print_examples()
        os.sys.exit(0)
    
    # List themes if requested
    if args.list_themes:
        list_themes()
        os.sys.exit(0)

    # List aspect ratios if requested
    if args.list_ratios:
        list_aspect_ratios()
        os.sys.exit(0)

    # Validate required arguments
    if not args.city or not args.country:
        print("Error: --city and --country are required.\n")
        print_examples()
        os.sys.exit(1)

    # Validate theme exists
    available_themes = get_available_themes()
    if args.theme not in available_themes:
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(available_themes)}")
        os.sys.exit(1)

    # Parse aspect ratio
    try:
        aspect_ratio = parse_aspect_ratio(args.ratio)
    except ValueError as e:
        print(f"Error: {e}")
        os.sys.exit(1)

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    # Load theme
    THEME = load_theme(args.theme)

    # Get coordinates and generate poster
    try:
        coords = get_coordinates(args.city, args.country)
        output_file = generate_output_filename(args.city, args.theme)
        create_poster(args.city, args.country, coords, args.distance, output_file,
                     aspect_ratio=aspect_ratio, dpi=args.dpi, base_width=args.width)
        
        print("\n" + "=" * 50)
        print("✓ Poster generation complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        os.sys.exit(1)
