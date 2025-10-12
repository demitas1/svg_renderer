"""Example: Render a single layer to PNG

This example demonstrates how to use the SVGRenderer library
to render a specific layer from an Inkscape SVG file to a PNG image.
"""

import sys
from pathlib import Path

# Add parent directory to path to import svg_renderer
sys.path.insert(0, str(Path(__file__).parent.parent))

from svg_renderer import SVGRenderer


def main():
    """Render a layer to PNG."""
    # Path to input SVG file
    svg_file = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'drawing-example.svg'

    if not svg_file.exists():
        print(f"Error: Sample SVG file not found at {svg_file}")
        sys.exit(1)

    # Create renderer instance
    renderer = SVGRenderer(str(svg_file))

    # List available layers
    print("Available layers:")
    for i, layer_name in enumerate(renderer.list_layers(), 1):
        print(f"  {i}. {layer_name}")

    # Render Layer 1 to PNG
    output_file = 'example_layer1.png'
    renderer.render_layer_to_png('Layer 1', output_file)
    print(f"\nSuccessfully rendered to {output_file}")


if __name__ == '__main__':
    main()
