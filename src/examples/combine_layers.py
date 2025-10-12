"""Example: Combine multiple layers

This example demonstrates how to combine multiple layers
from an Inkscape SVG file into a single output.
"""

import sys
from pathlib import Path

# Add parent directory to path to import svg_renderer
sys.path.insert(0, str(Path(__file__).parent.parent))

from svg_renderer import SVGRenderer


def main():
    """Combine multiple layers."""
    # Path to input SVG file
    svg_file = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'drawing-example.svg'

    if not svg_file.exists():
        print(f"Error: Sample SVG file not found at {svg_file}")
        sys.exit(1)

    # Create renderer instance
    renderer = SVGRenderer(str(svg_file))

    # List available layers
    layers = renderer.list_layers()
    print(f"Combining {len(layers)} layers: {', '.join(layers)}")

    # Render all layers to a single PNG
    png_output = 'example_combined.png'
    renderer.render_layers_to_png(layers, png_output)
    print(f"Rendered combined PNG to {png_output}")

    # Export all layers to a single SVG
    svg_output = 'example_combined.svg'
    renderer.export_layers_to_svg(layers, svg_output)
    print(f"Exported combined SVG to {svg_output}")


if __name__ == '__main__':
    main()
