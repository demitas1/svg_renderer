"""Style Parser Module

This module provides functionality to parse SVG style attributes,
convert color values, and extract styling information.
"""

from typing import Dict, Tuple, Optional
from lxml import etree
import re


class StyleParser:
    """Parser for SVG style attributes and properties."""

    # Named colors (subset of SVG named colors)
    NAMED_COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'silver': (192, 192, 192),
        'maroon': (128, 0, 0),
        'olive': (128, 128, 0),
        'lime': (0, 255, 0),
        'aqua': (0, 255, 255),
        'teal': (0, 128, 128),
        'navy': (0, 0, 128),
        'fuchsia': (255, 0, 255),
        'purple': (128, 0, 128),
    }

    def __init__(self, element: etree._Element):
        """Initialize style parser for an SVG element.

        Args:
            element: The SVG element to parse styles from
        """
        self.element = element
        self._style_dict: Optional[Dict[str, str]] = None

    def parse_style(self) -> Dict[str, str]:
        """Parse style attributes from the element.

        Combines both the style attribute (CSS-like) and individual
        SVG attributes (e.g., fill, stroke) into a single dictionary.

        Returns:
            Dictionary mapping style property names to values
        """
        if self._style_dict is not None:
            return self._style_dict

        styles = {}

        # Parse the style attribute (e.g., "fill:#ffffff;stroke:#000000")
        style_attr = self.element.get('style', '')
        if style_attr:
            for declaration in style_attr.split(';'):
                declaration = declaration.strip()
                if ':' in declaration:
                    prop, value = declaration.split(':', 1)
                    styles[prop.strip()] = value.strip()

        # Parse individual SVG attributes
        # These have lower priority than style attribute
        svg_style_attrs = [
            'fill', 'fill-opacity', 'stroke', 'stroke-width',
            'stroke-opacity', 'stroke-linejoin', 'stroke-linecap',
            'stroke-miterlimit', 'stroke-dasharray', 'opacity'
        ]

        for attr in svg_style_attrs:
            if attr not in styles:  # Don't override style attribute values
                value = self.element.get(attr)
                if value is not None:
                    styles[attr] = value

        self._style_dict = styles
        return styles

    def get_color(self, color_str: str) -> Optional[Tuple[float, float, float]]:
        """Convert a color string to RGB values (0.0-1.0 range).

        Supports:
        - Hex colors: #RGB, #RRGGBB
        - Named colors: red, blue, etc.
        - Special values: none (returns None)

        Args:
            color_str: Color value as string

        Returns:
            Tuple of (r, g, b) as floats in 0.0-1.0 range, or None for 'none'

        Raises:
            ValueError: If color format is not recognized
        """
        if not color_str or color_str.lower() == 'none':
            return None

        color_str = color_str.strip().lower()

        # Handle hex colors
        if color_str.startswith('#'):
            hex_color = color_str[1:]

            # Handle short form (#RGB)
            if len(hex_color) == 3:
                hex_color = ''.join([c * 2 for c in hex_color])

            # Handle long form (#RRGGBB)
            if len(hex_color) == 6:
                try:
                    r = int(hex_color[0:2], 16) / 255.0
                    g = int(hex_color[2:4], 16) / 255.0
                    b = int(hex_color[4:6], 16) / 255.0
                    return (r, g, b)
                except ValueError as e:
                    raise ValueError(f"Invalid hex color: {color_str}") from e

        # Handle named colors
        if color_str in self.NAMED_COLORS:
            r, g, b = self.NAMED_COLORS[color_str]
            return (r / 255.0, g / 255.0, b / 255.0)

        # Handle rgb() format
        rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return (r / 255.0, g / 255.0, b / 255.0)

        raise ValueError(f"Unsupported color format: {color_str}")

    def get_stroke_width(self, width_str: str) -> float:
        """Parse stroke width value.

        Args:
            width_str: Stroke width as string (e.g., "2", "2px", "1.5")

        Returns:
            Stroke width as float

        Raises:
            ValueError: If the value cannot be parsed
        """
        if not width_str:
            return 1.0  # Default stroke width

        # Remove units
        width_str = width_str.strip()
        for unit in ['px', 'pt', 'mm', 'cm', 'in', 'pc', 'em', 'ex']:
            if width_str.endswith(unit):
                width_str = width_str[:-len(unit)]
                break

        try:
            return float(width_str)
        except ValueError as e:
            raise ValueError(f"Invalid stroke width: {width_str}") from e

    def get_opacity(self, opacity_str: str) -> float:
        """Parse opacity value.

        Args:
            opacity_str: Opacity as string (0-1 range or percentage)

        Returns:
            Opacity as float in 0.0-1.0 range

        Raises:
            ValueError: If the value cannot be parsed
        """
        if not opacity_str:
            return 1.0  # Default opacity

        opacity_str = opacity_str.strip()

        # Handle percentage
        if opacity_str.endswith('%'):
            try:
                return float(opacity_str[:-1]) / 100.0
            except ValueError as e:
                raise ValueError(f"Invalid opacity percentage: {opacity_str}") from e

        # Handle decimal
        try:
            opacity = float(opacity_str)
            return max(0.0, min(1.0, opacity))  # Clamp to 0-1 range
        except ValueError as e:
            raise ValueError(f"Invalid opacity value: {opacity_str}") from e

    def get_fill(self) -> Optional[Tuple[float, float, float]]:
        """Get the fill color for this element.

        Returns:
            RGB tuple (0.0-1.0 range) or None for no fill
        """
        styles = self.parse_style()
        fill = styles.get('fill')
        if fill:
            return self.get_color(fill)
        return None

    def get_stroke(self) -> Optional[Tuple[float, float, float]]:
        """Get the stroke color for this element.

        Returns:
            RGB tuple (0.0-1.0 range) or None for no stroke
        """
        styles = self.parse_style()
        stroke = styles.get('stroke')
        if stroke:
            return self.get_color(stroke)
        return None

    def get_fill_opacity(self) -> float:
        """Get the fill opacity for this element.

        Returns:
            Opacity value in 0.0-1.0 range
        """
        styles = self.parse_style()
        fill_opacity = styles.get('fill-opacity', '1.0')
        return self.get_opacity(fill_opacity)

    def get_stroke_opacity(self) -> float:
        """Get the stroke opacity for this element.

        Returns:
            Opacity value in 0.0-1.0 range
        """
        styles = self.parse_style()
        stroke_opacity = styles.get('stroke-opacity', '1.0')
        return self.get_opacity(stroke_opacity)

    def get_stroke_width_value(self) -> float:
        """Get the stroke width for this element.

        Returns:
            Stroke width as float
        """
        styles = self.parse_style()
        stroke_width = styles.get('stroke-width', '1')
        return self.get_stroke_width(stroke_width)
