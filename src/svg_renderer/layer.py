"""Layer Extractor Module

This module provides functionality to extract layers from Inkscape SVG files
and retrieve path and rect elements from those layers.
"""

from typing import List, Optional
from lxml import etree


class LayerExtractor:
    """Extractor for Inkscape layers and their elements."""

    def __init__(self, root: etree._Element, namespaces: dict):
        """Initialize layer extractor.

        Args:
            root: The root element of the SVG document
            namespaces: Dictionary mapping namespace prefixes to URIs
        """
        self.root = root
        self.namespaces = namespaces

    def get_layer_by_name(self, layer_name: str) -> Optional[etree._Element]:
        """Find a layer by its display name (inkscape:label).

        Args:
            layer_name: The display name of the layer

        Returns:
            The layer element, or None if not found
        """
        # Search for g elements with inkscape:groupmode="layer"
        layers = self.root.xpath(
            './/svg:g[@inkscape:groupmode="layer"]',
            namespaces=self.namespaces
        )

        for layer in layers:
            label = layer.get(f'{{{self.namespaces["inkscape"]}}}label')
            if label == layer_name:
                return layer

        return None

    def get_layer_by_id(self, layer_id: str) -> Optional[etree._Element]:
        """Find a layer by its ID attribute.

        Args:
            layer_id: The ID of the layer

        Returns:
            The layer element, or None if not found
        """
        # Search for g elements with inkscape:groupmode="layer" and matching ID
        layers = self.root.xpath(
            f'.//svg:g[@inkscape:groupmode="layer"][@id="{layer_id}"]',
            namespaces=self.namespaces
        )

        return layers[0] if layers else None

    def get_all_layers(self) -> List[etree._Element]:
        """Get all layers in the SVG document.

        Returns:
            List of layer elements
        """
        return self.root.xpath(
            './/svg:g[@inkscape:groupmode="layer"]',
            namespaces=self.namespaces
        )

    def get_layer_names(self) -> List[str]:
        """Get names of all layers in the document.

        Returns:
            List of layer names
        """
        layers = self.get_all_layers()
        names = []

        for layer in layers:
            label = layer.get(f'{{{self.namespaces["inkscape"]}}}label')
            if label:
                names.append(label)
            else:
                # Fallback to ID if no label
                layer_id = layer.get('id')
                if layer_id:
                    names.append(layer_id)

        return names

    def extract_elements(self, layer: etree._Element,
                        element_types: Optional[List[str]] = None) -> List[etree._Element]:
        """Extract specific element types from a layer.

        Args:
            layer: The layer element to extract from
            element_types: List of element types to extract (e.g., ['path', 'rect']).
                          If None, extracts path and rect elements.

        Returns:
            List of elements matching the specified types
        """
        if element_types is None:
            element_types = ['path', 'rect']

        elements = []

        for elem_type in element_types:
            # Find all elements of this type within the layer
            found = layer.xpath(
                f'.//svg:{elem_type}',
                namespaces=self.namespaces
            )
            elements.extend(found)

        return elements

    def extract_paths(self, layer: etree._Element) -> List[etree._Element]:
        """Extract all path elements from a layer.

        Args:
            layer: The layer element to extract from

        Returns:
            List of path elements
        """
        return self.extract_elements(layer, ['path'])

    def extract_rects(self, layer: etree._Element) -> List[etree._Element]:
        """Extract all rect elements from a layer.

        Args:
            layer: The layer element to extract from

        Returns:
            List of rect elements
        """
        return self.extract_elements(layer, ['rect'])

    def get_layer(self, identifier: str) -> etree._Element:
        """Get a layer by name or ID.

        Tries to find the layer by name first, then by ID.

        Args:
            identifier: Layer name or ID

        Returns:
            The layer element

        Raises:
            ValueError: If the layer is not found
        """
        # Try by name first
        layer = self.get_layer_by_name(identifier)

        # If not found, try by ID
        if layer is None:
            layer = self.get_layer_by_id(identifier)

        # If still not found, raise error with helpful message
        if layer is None:
            available_layers = self.get_layer_names()
            raise ValueError(
                f"Layer '{identifier}' not found. "
                f"Available layers: {', '.join(available_layers) if available_layers else 'none'}"
            )

        return layer
