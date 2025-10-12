"""Example: Export a single layer to SVG

This example demonstrates how to extract a specific layer
from an Inkscape SVG file and save it as a new SVG file.
"""

import sys
from pathlib import Path

# Add parent directory to path to import svg_renderer
sys.path.insert(0, str(Path(__file__).parent.parent))

from svg_renderer import SVGRenderer


def main():
    """Export a layer to SVG."""
    # Path to input SVG file
    svg_file = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'drawing-example.svg'

    if not svg_file.exists():
        print(f"Error: Sample SVG file not found at {svg_file}")
        sys.exit(1)

    # Create renderer instance
    renderer = SVGRenderer(str(svg_file))

    # Export Layer 1 to a new SVG file
    output_file = 'example_layer1.svg'
    renderer.export_layer_to_svg('Layer 1', output_file)
    print(f"Successfully exported to {output_file}")

    # The exported SVG file will contain only the elements from Layer 1
    # and can be opened in Inkscape or other SVG editors


if __name__ == '__main__':
    main()
