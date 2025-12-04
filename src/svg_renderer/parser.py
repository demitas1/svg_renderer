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

    def get_document_unit(self) -> str:
        """Detect the unit used in the SVG document.

        Checks width/height attributes for units.
        Common units: mm, px, pt, cm, in

        Returns:
            Unit string (e.g., 'mm', 'px') or 'px' as default
        """
        if self.root is None:
            raise ValueError("SVG not loaded. Call load_svg() first.")

        width_str = self.root.get('width', '')

        # Check for units in width attribute
        for unit in ['mm', 'cm', 'in', 'pt', 'pc']:
            if width_str.endswith(unit):
                return unit

        # Default to px (unitless is treated as px in SVG)
        return 'px'

    def calculate_pixel_size(self, dpi: float = 96.0) -> Tuple[int, int]:
        """Calculate the pixel size for rendering at the specified DPI.

        Args:
            dpi: Dots per inch for rendering (default 96, standard screen DPI)

        Returns:
            Tuple of (width, height) in pixels
        """
        _, _, vb_width, vb_height = self.get_viewbox()
        unit = self.get_document_unit()

        # Conversion factors to inches
        unit_to_inches = {
            'px': 1.0 / 96.0,  # CSS px is 1/96 inch
            'pt': 1.0 / 72.0,  # Point is 1/72 inch
            'pc': 1.0 / 6.0,   # Pica is 1/6 inch
            'mm': 1.0 / 25.4,  # mm to inches
            'cm': 1.0 / 2.54,  # cm to inches
            'in': 1.0,         # inches
        }

        inches_per_unit = unit_to_inches.get(unit, 1.0 / 96.0)

        # Calculate pixel dimensions
        width_px = int(round(vb_width * inches_per_unit * dpi))
        height_px = int(round(vb_height * inches_per_unit * dpi))

        return (width_px, height_px)

    def calculate_scale(self, dpi: float = 96.0) -> float:
        """Calculate the scale factor from viewBox units to pixels.

        Args:
            dpi: Dots per inch for rendering

        Returns:
            Scale factor to multiply viewBox coordinates by
        """
        _, _, vb_width, _ = self.get_viewbox()
        pixel_width, _ = self.calculate_pixel_size(dpi)

        if vb_width == 0:
            return 1.0

        return pixel_width / vb_width

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
