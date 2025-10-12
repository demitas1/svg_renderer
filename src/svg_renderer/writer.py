"""SVG Writer Module

This module provides functionality to create and write SVG files,
preserving Inkscape namespaces and layer structure.
"""

from typing import List, Tuple, Dict, Optional
from lxml import etree


class SVGWriter:
    """Writer for creating SVG files with Inkscape layer support."""

    NAMESPACES = {
        None: 'http://www.w3.org/2000/svg',
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    }

    def __init__(self, viewbox: Tuple[float, float, float, float],
                 width: Optional[str] = None,
                 height: Optional[str] = None):
        """Initialize SVG writer.

        Args:
            viewbox: Tuple of (x, y, width, height) for viewBox attribute
            width: Optional width with units (e.g., "210mm")
            height: Optional height with units (e.g., "297mm")
        """
        self.viewbox = viewbox
        self.width = width
        self.height = height

        # Calculate default dimensions from viewBox if not provided
        if self.width is None:
            self.width = f"{viewbox[2]}px"
        if self.height is None:
            self.height = f"{viewbox[3]}px"

        # Create SVG root element using lxml
        self.root = etree.Element(
            '{http://www.w3.org/2000/svg}svg',
            nsmap=self.NAMESPACES
        )
        self.root.set('width', self.width)
        self.root.set('height', self.height)
        self.root.set('viewBox', f"{viewbox[0]} {viewbox[1]} {viewbox[2]} {viewbox[3]}")
        self.root.set('version', '1.1')

        self.layers: Dict[str, etree._Element] = {}

    def create_layer(self, layer_name: str, layer_id: Optional[str] = None) -> etree._Element:
        """Create a new layer (g element with Inkscape attributes).

        Args:
            layer_name: Display name for the layer
            layer_id: Optional ID for the layer (auto-generated if not provided)

        Returns:
            The created group element representing the layer
        """
        if layer_id is None:
            # Generate layer ID from name
            layer_id = layer_name.lower().replace(' ', '_')

        # Create group element
        layer = etree.SubElement(self.root, '{http://www.w3.org/2000/svg}g')
        layer.set('id', layer_id)
        layer.set('{http://www.inkscape.org/namespaces/inkscape}groupmode', 'layer')
        layer.set('{http://www.inkscape.org/namespaces/inkscape}label', layer_name)

        self.layers[layer_name] = layer

        return layer

    def add_path(self, path_data: str, style: str,
                 layer_name: Optional[str] = None,
                 element_id: Optional[str] = None) -> None:
        """Add a path element to the SVG.

        Args:
            path_data: SVG path data (d attribute)
            style: Style string (CSS format)
            layer_name: Name of the layer to add to (creates if doesn't exist)
            element_id: Optional ID for the path element
        """
        # Get or create layer
        if layer_name:
            if layer_name not in self.layers:
                self.create_layer(layer_name)
            parent = self.layers[layer_name]
        else:
            parent = self.root

        # Create path element
        path = etree.SubElement(parent, '{http://www.w3.org/2000/svg}path')
        path.set('d', path_data)
        if style:
            path.set('style', style)
        if element_id:
            path.set('id', element_id)

    def add_rect(self, x: float, y: float, width: float, height: float,
                 style: str,
                 layer_name: Optional[str] = None,
                 element_id: Optional[str] = None) -> None:
        """Add a rect element to the SVG.

        Args:
            x: X coordinate
            y: Y coordinate
            width: Width of rectangle
            height: Height of rectangle
            style: Style string (CSS format)
            layer_name: Name of the layer to add to (creates if doesn't exist)
            element_id: Optional ID for the rect element
        """
        # Get or create layer
        if layer_name:
            if layer_name not in self.layers:
                self.create_layer(layer_name)
            parent = self.layers[layer_name]
        else:
            parent = self.root

        # Create rect element
        rect = etree.SubElement(parent, '{http://www.w3.org/2000/svg}rect')
        rect.set('x', str(x))
        rect.set('y', str(y))
        rect.set('width', str(width))
        rect.set('height', str(height))
        if style:
            rect.set('style', style)
        if element_id:
            rect.set('id', element_id)

    def add_element_from_lxml(self, element: etree._Element,
                              layer_name: Optional[str] = None) -> None:
        """Add an element from lxml to the SVG.

        This method copies an element from a parsed SVG to the new document.

        Args:
            element: The lxml element to copy
            layer_name: Name of the layer to add to
        """
        tag = etree.QName(element.tag).localname

        if tag == 'path':
            path_data = element.get('d', '')
            style = self._build_style_string(element)
            element_id = element.get('id')
            self.add_path(path_data, style, layer_name, element_id)

        elif tag == 'rect':
            x = float(element.get('x', 0))
            y = float(element.get('y', 0))
            width = float(element.get('width', 0))
            height = float(element.get('height', 0))
            style = self._build_style_string(element)
            element_id = element.get('id')
            self.add_rect(x, y, width, height, style, layer_name, element_id)

    def _build_style_string(self, element: etree._Element) -> str:
        """Build a CSS style string from an element's attributes.

        Args:
            element: The element to extract style from

        Returns:
            CSS style string
        """
        # First, get the style attribute if it exists
        style_attr = element.get('style', '')
        style_parts = []

        if style_attr:
            style_parts.append(style_attr)

        # Add individual SVG attributes
        svg_style_attrs = [
            'fill', 'fill-opacity', 'stroke', 'stroke-width',
            'stroke-opacity', 'stroke-linejoin', 'stroke-linecap',
            'stroke-miterlimit', 'stroke-dasharray', 'opacity'
        ]

        for attr in svg_style_attrs:
            value = element.get(attr)
            if value is not None and attr not in style_attr:
                style_parts.append(f"{attr}:{value}")

        return ';'.join(style_parts)

    def save(self, output_path: str) -> None:
        """Save the SVG to a file.

        Args:
            output_path: Path where the SVG file will be saved
        """
        tree = etree.ElementTree(self.root)
        tree.write(
            output_path,
            encoding='UTF-8',
            xml_declaration=True,
            pretty_print=True
        )

    @staticmethod
    def copy_layer_to_new_svg(elements: List[etree._Element],
                              viewbox: Tuple[float, float, float, float],
                              layer_name: str = "Layer 1",
                              output_path: Optional[str] = None) -> 'SVGWriter':
        """Create a new SVG from a list of elements.

        Args:
            elements: List of elements to include
            viewbox: ViewBox for the new SVG
            layer_name: Name for the layer containing the elements
            output_path: Optional path to save the SVG immediately

        Returns:
            The SVGWriter instance
        """
        writer = SVGWriter(viewbox)
        writer.create_layer(layer_name)

        for element in elements:
            writer.add_element_from_lxml(element, layer_name)

        if output_path:
            writer.save(output_path)

        return writer
