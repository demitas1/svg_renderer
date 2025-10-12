"""SVG Parser Module

This module provides functionality to load and parse SVG files,
extract viewBox information, and manage XML namespaces.
"""

from typing import Dict, Tuple, Optional
from lxml import etree


class SVGParser:
    """Parser for SVG files with support for Inkscape namespaces."""

    # Common SVG/Inkscape namespaces
    NAMESPACES = {
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    }

    def __init__(self, filepath: str):
        """Initialize SVG parser with a file path.

        Args:
            filepath: Path to the SVG file

        Raises:
            FileNotFoundError: If the SVG file does not exist
            etree.ParseError: If the SVG file is malformed
        """
        self.filepath = filepath
        self.tree: Optional[etree._ElementTree] = None
        self.root: Optional[etree._Element] = None
        self.namespaces: Dict[str, str] = {}

    def load_svg(self) -> etree._Element:
        """Load and parse the SVG file.

        Returns:
            The root element of the SVG document

        Raises:
            FileNotFoundError: If the file does not exist
            etree.ParseError: If the XML is malformed
        """
        try:
            self.tree = etree.parse(self.filepath)
            self.root = self.tree.getroot()
            self.namespaces = self._extract_namespaces()
            return self.root
        except FileNotFoundError as e:
            raise FileNotFoundError(f"SVG file not found: {self.filepath}") from e
        except etree.ParseError as e:
            raise etree.ParseError(f"Invalid SVG format in {self.filepath}: {e}")

    def _extract_namespaces(self) -> Dict[str, str]:
        """Extract namespaces from the SVG document.

        Returns:
            Dictionary mapping namespace prefixes to URIs
        """
        if self.root is None:
            return {}

        # Get namespaces from the root element
        ns_map = self.root.nsmap.copy() if self.root.nsmap else {}

        # Merge with standard namespaces
        result = self.NAMESPACES.copy()
        result.update(ns_map)

        # Handle default namespace (None key)
        if None in result:
            result['svg'] = result[None]
            del result[None]

        return result

    def get_viewbox(self) -> Tuple[float, float, float, float]:
        """Extract and parse the viewBox attribute.

        Returns:
            Tuple of (x, y, width, height) as floats

        Raises:
            ValueError: If viewBox is missing or invalid
        """
        if self.root is None:
            raise ValueError("SVG not loaded. Call load_svg() first.")

        viewbox_str = self.root.get('viewBox')
        if not viewbox_str:
            # Try to use width/height as fallback
            width = self.root.get('width')
            height = self.root.get('height')
            if width and height:
                # Remove units if present (e.g., "210mm" -> "210")
                width = self._parse_dimension(width)
                height = self._parse_dimension(height)
                return (0.0, 0.0, width, height)
            else:
                raise ValueError(
                    f"No viewBox attribute found in {self.filepath} "
                    "and no width/height fallback available"
                )

        try:
            parts = viewbox_str.split()
            if len(parts) != 4:
                raise ValueError(f"Invalid viewBox format: {viewbox_str}")

            x, y, width, height = map(float, parts)
            return (x, y, width, height)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid viewBox values: {viewbox_str}") from e

    def _parse_dimension(self, value: str) -> float:
        """Parse a dimension value, removing units.

        Args:
            value: Dimension string (e.g., "210mm", "100px", "50")

        Returns:
            Numeric value as float
        """
        # Remove common units
        for unit in ['px', 'pt', 'mm', 'cm', 'in', 'pc', 'em', 'ex', '%']:
            if value.endswith(unit):
                value = value[:-len(unit)]
                break

        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot parse dimension: {value}")

    def get_namespaces(self) -> Dict[str, str]:
        """Get the namespace mapping for this SVG document.

        Returns:
            Dictionary mapping namespace prefixes to URIs
        """
        return self.namespaces.copy()

    def get_root(self) -> etree._Element:
        """Get the root element of the SVG document.

        Returns:
            The root element

        Raises:
            ValueError: If SVG not loaded yet
        """
        if self.root is None:
            raise ValueError("SVG not loaded. Call load_svg() first.")
        return self.root
