#!/usr/bin/env python
"""Generate expected PNG files for rendering tests.

This script generates the expected PNG output files that will be used
as reference images in the rendering tests.

Run this script only when:
1. Setting up tests for the first time
2. Intentionally changing the rendering behavior

Usage:
    python generate_expected_pngs.py
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from svg_renderer import SVGRenderer


def main():
    fixtures_dir = Path(__file__).parent

    # Generate expected PNG for rect-only.svg
    rect_svg = fixtures_dir / 'rect-only.svg'
    rect_png = fixtures_dir / 'expected_rect.png'
    renderer = SVGRenderer(str(rect_svg))
    renderer.render_layer_to_png('Layer 1', str(rect_png))
    print(f"Generated: {rect_png}")

    # Generate expected PNG for path-only.svg
    path_svg = fixtures_dir / 'path-only.svg'
    path_png = fixtures_dir / 'expected_path.png'
    renderer = SVGRenderer(str(path_svg))
    renderer.render_layer_to_png('Layer 1', str(path_png))
    print(f"Generated: {path_png}")


if __name__ == '__main__':
    main()
