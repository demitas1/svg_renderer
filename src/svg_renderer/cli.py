"""Command-line Interface

This module provides the CLI implementation for the SVG renderer.
"""

import argparse
import sys
from pathlib import Path

from .api import SVGRenderer


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog='svg-renderer',
        description='Render Inkscape SVG layers to PNG or extract to new SVG files.'
    )

    parser.add_argument('input', help='Input SVG file path')
    parser.add_argument('--list-layers', action='store_true',
                       help='List all layers in the SVG file')
    parser.add_argument('--layer', '-l', action='append', dest='layers',
                       help='Layer name or ID to process (can be specified multiple times)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['png', 'svg'], default='png',
                       help='Output format (default: png)')
    parser.add_argument('--dpi', type=float, default=None,
                       help='DPI for PNG rendering (e.g., 96 for screen, 300 for print). '
                            'If not specified, uses viewBox dimensions directly.')

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        renderer = SVGRenderer(args.input, dpi=args.dpi)

        # List layers mode
        if args.list_layers:
            layers = renderer.list_layers()
            print(f"Layers in {args.input}:")
            for i, layer_name in enumerate(layers, 1):
                print(f"  {i}. {layer_name}")
            return

        # Rendering mode
        if not args.layers:
            print("Error: No layers specified. Use --layer or --list-layers.", file=sys.stderr)
            sys.exit(1)

        if not args.output:
            print("Error: No output file specified. Use --output.", file=sys.stderr)
            sys.exit(1)

        # Render or export
        if args.format == 'png':
            if len(args.layers) == 1:
                renderer.render_layer_to_png(args.layers[0], args.output)
            else:
                renderer.render_layers_to_png(args.layers, args.output)
        else:  # svg
            if len(args.layers) == 1:
                renderer.export_layer_to_svg(args.layers[0], args.output)
            else:
                renderer.export_layers_to_svg(args.layers, args.output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
