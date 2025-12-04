"""High-level API for SVG Rendering

This module provides the main SVGRenderer class that integrates
all the components for easy use.
"""

from typing import List, Optional
from .parser import SVGParser
from .layer import LayerExtractor
from .renderer import Renderer
from .writer import SVGWriter


class SVGRenderer:
    """High-level interface for SVG rendering operations."""

    # Default DPI for screen display (CSS standard)
    DEFAULT_DPI = 96.0

    def __init__(self, svg_path: str, dpi: Optional[float] = None):
        """Initialize the renderer with an SVG file.

        Args:
            svg_path: Path to the SVG file
            dpi: DPI for PNG rendering. None uses viewBox size directly (legacy mode),
                 96 for screen display, 300 for print quality.
        """
        self.svg_path = svg_path
        self.dpi = dpi
        self.parser = SVGParser(svg_path)
        self.parser.load_svg()

        self.root = self.parser.get_root()
        self.namespaces = self.parser.get_namespaces()
        self.viewbox = self.parser.get_viewbox()

        self.extractor = LayerExtractor(self.root, self.namespaces)

    def _create_renderer(self) -> Renderer:
        """Create a renderer with appropriate dimensions and scale.

        Returns:
            Configured Renderer instance
        """
        if self.dpi is not None:
            # DPI-aware rendering
            width, height = self.parser.calculate_pixel_size(self.dpi)
            scale = self.parser.calculate_scale(self.dpi)
            return Renderer(width, height, scale)
        else:
            # Legacy mode: use viewBox directly as pixel dimensions
            _, _, width, height = self.viewbox
            return Renderer(int(width), int(height))

    def render_layer_to_png(self, layer_name: str, output_path: str) -> None:
        """Render a specific layer to PNG.

        Args:
            layer_name: Name or ID of the layer to render
            output_path: Path where the PNG will be saved
        """
        # Extract layer
        layer = self.extractor.get_layer(layer_name)

        # Extract elements from layer
        elements = self.extractor.extract_elements(layer)

        if not elements:
            print(f"Warning: Layer '{layer_name}' contains no path or rect elements.")
            return

        # Create renderer with DPI support
        renderer = self._create_renderer()
        renderer.setup_surface()

        # Render elements
        renderer.render_elements(elements)

        # Save PNG
        renderer.save_png(output_path)
        print(f"Rendered layer '{layer_name}' to {output_path}")

    def render_layers_to_png(self, layer_names: List[str], output_path: str) -> None:
        """Render multiple layers to a single PNG.

        Args:
            layer_names: List of layer names or IDs to render
            output_path: Path where the PNG will be saved
        """
        # Collect all elements from all layers
        all_elements = []

        for layer_name in layer_names:
            layer = self.extractor.get_layer(layer_name)
            elements = self.extractor.extract_elements(layer)
            all_elements.extend(elements)

        if not all_elements:
            print(f"Warning: No elements found in specified layers.")
            return

        # Create renderer with DPI support
        renderer = self._create_renderer()
        renderer.setup_surface()

        # Render all elements
        renderer.render_elements(all_elements)

        # Save PNG
        renderer.save_png(output_path)
        print(f"Rendered {len(layer_names)} layer(s) to {output_path}")

    def export_layer_to_svg(self, layer_name: str, output_path: str) -> None:
        """Export a specific layer to a new SVG file.

        Args:
            layer_name: Name or ID of the layer to export
            output_path: Path where the SVG will be saved
        """
        # Extract layer
        layer = self.extractor.get_layer(layer_name)

        # Extract elements from layer
        elements = self.extractor.extract_elements(layer)

        if not elements:
            print(f"Warning: Layer '{layer_name}' contains no path or rect elements.")
            return

        # Create SVG writer
        writer = SVGWriter.copy_layer_to_new_svg(
            elements,
            self.viewbox,
            layer_name=layer_name,
            output_path=output_path
        )

        print(f"Exported layer '{layer_name}' to {output_path}")

    def export_layers_to_svg(self, layer_names: List[str], output_path: str) -> None:
        """Export multiple layers to a new SVG file.

        Args:
            layer_names: List of layer names or IDs to export
            output_path: Path where the SVG will be saved
        """
        writer = SVGWriter(self.viewbox)

        for layer_name in layer_names:
            layer = self.extractor.get_layer(layer_name)
            elements = self.extractor.extract_elements(layer)

            if elements:
                writer.create_layer(layer_name)
                for element in elements:
                    writer.add_element_from_lxml(element, layer_name)

        writer.save(output_path)
        print(f"Exported {len(layer_names)} layer(s) to {output_path}")

    def list_layers(self) -> List[str]:
        """List all layers in the SVG.

        Returns:
            List of layer names
        """
        return self.extractor.get_layer_names()
