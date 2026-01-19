#!/usr/bin/env python3
"""
Test script to verify gradient fix works without distortion.
Tests with a small, quick map generation.
"""

import subprocess
import sys

def test_gradient():
    """
    Generate a small test map with gradients enabled to check for distortion.
    Uses a small distance for quick testing.
    """
    print("=" * 60)
    print("Testing Gradient Fix")
    print("=" * 60)
    print("\nGenerating test map with gradients enabled...")
    print("City: Venice (small area, fast test)")
    print("Theme: noir")
    print("Distance: 2000m (for quick testing)\n")

    # Run the map generator with a small distance for quick testing
    cmd = [
        sys.executable,
        "create_map_poster.py",
        "-c", "Venice",
        "-C", "Italy",
        "-t", "noir",
        "-d", "2000"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✓ SUCCESS: Map generated without errors!")
            print("=" * 60)
            print("\nPlease check the generated poster in posters/ directory")
            print("to verify there's no distortion in the gradient areas.")
            print("\nWhat to look for:")
            print("  - Top and bottom gradient fades should be smooth")
            print("  - Map should not appear stretched or compressed")
            print("  - Roads should maintain correct proportions")
            print("  - Text should be properly positioned")
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ FAILED: Error during map generation")
            print("=" * 60)
            print("\nError output:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"\n✗ Error running test: {e}")
        return False

if __name__ == "__main__":
    success = test_gradient()
    sys.exit(0 if success else 1)
