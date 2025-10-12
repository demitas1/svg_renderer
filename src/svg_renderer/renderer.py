"""Renderer Module

This module provides Cairo-based rendering functionality for SVG elements
to PNG output format.
"""

from typing import List, Tuple, Optional
import cairo
from lxml import etree
from .style import StyleParser
import re


class Renderer:
    """Cairo-based renderer for SVG elements."""

    def __init__(self, width: int, height: int):
        """Initialize the renderer with output dimensions.

        Args:
            width: Width of the output surface in pixels
            height: Height of the output surface in pixels
        """
        self.width = width
        self.height = height
        self.surface: Optional[cairo.ImageSurface] = None
        self.context: Optional[cairo.Context] = None

    def setup_surface(self) -> cairo.Context:
        """Initialize the Cairo surface and context.

        Returns:
            The Cairo context for drawing
        """
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.context = cairo.Context(self.surface)

        # Set white background
        self.context.set_source_rgb(1, 1, 1)
        self.context.paint()

        return self.context

    def render_elements(self, elements: List[etree._Element]) -> None:
        """Render a list of SVG elements.

        Args:
            elements: List of SVG elements to render
        """
        if self.context is None:
            self.setup_surface()

        for element in elements:
            tag = etree.QName(element.tag).localname

            if tag == 'rect':
                self.render_rect(element)
            elif tag == 'path':
                self.render_path(element)
            # Other element types can be added here

    def render_rect(self, element: etree._Element) -> None:
        """Render a rect element.

        Args:
            element: The rect element to render
        """
        if self.context is None:
            return

        # Parse rectangle attributes
        x = float(element.get('x', 0))
        y = float(element.get('y', 0))
        width = float(element.get('width', 0))
        height = float(element.get('height', 0))

        # Parse styles
        style_parser = StyleParser(element)

        # Draw rectangle
        self.context.rectangle(x, y, width, height)

        # Apply fill
        fill_color = style_parser.get_fill()
        if fill_color:
            fill_opacity = style_parser.get_fill_opacity()
            self.context.set_source_rgba(fill_color[0], fill_color[1], fill_color[2], fill_opacity)
            if style_parser.get_stroke():
                self.context.fill_preserve()
            else:
                self.context.fill()

        # Apply stroke
        stroke_color = style_parser.get_stroke()
        if stroke_color:
            stroke_width = style_parser.get_stroke_width_value()
            stroke_opacity = style_parser.get_stroke_opacity()
            self.context.set_source_rgba(stroke_color[0], stroke_color[1], stroke_color[2], stroke_opacity)
            self.context.set_line_width(stroke_width)
            self.context.stroke()

    def render_path(self, element: etree._Element) -> None:
        """Render a path element.

        Currently supports: M (move), L (line), Z (close) commands.

        Args:
            element: The path element to render
        """
        if self.context is None:
            return

        # Get path data
        path_data = element.get('d', '')
        if not path_data:
            return

        # Parse and execute path commands
        self._parse_path_data(path_data)

        # Parse styles
        style_parser = StyleParser(element)

        # Apply fill
        fill_color = style_parser.get_fill()
        if fill_color:
            fill_opacity = style_parser.get_fill_opacity()
            self.context.set_source_rgba(fill_color[0], fill_color[1], fill_color[2], fill_opacity)
            if style_parser.get_stroke():
                self.context.fill_preserve()
            else:
                self.context.fill()

        # Apply stroke
        stroke_color = style_parser.get_stroke()
        if stroke_color:
            stroke_width = style_parser.get_stroke_width_value()
            stroke_opacity = style_parser.get_stroke_opacity()
            self.context.set_source_rgba(stroke_color[0], stroke_color[1], stroke_color[2], stroke_opacity)
            self.context.set_line_width(stroke_width)

            # Set stroke line join if specified
            styles = style_parser.parse_style()
            stroke_linejoin = styles.get('stroke-linejoin', 'miter')
            if stroke_linejoin == 'round':
                self.context.set_line_join(cairo.LINE_JOIN_ROUND)
            elif stroke_linejoin == 'bevel':
                self.context.set_line_join(cairo.LINE_JOIN_BEVEL)
            else:  # miter
                self.context.set_line_join(cairo.LINE_JOIN_MITER)

            # Set miter limit if specified
            stroke_miterlimit = styles.get('stroke-miterlimit')
            if stroke_miterlimit:
                try:
                    self.context.set_miter_limit(float(stroke_miterlimit))
                except ValueError:
                    pass  # Use default

            self.context.stroke()

    def _parse_path_data(self, path_data: str) -> None:
        """Parse SVG path data and execute Cairo commands.

        Currently supports: M/m, L/l, Z/z, C/c commands.

        Args:
            path_data: SVG path data string
        """
        if self.context is None:
            return

        # Tokenize path data
        # Split on command letters, keeping the letters
        tokens = re.findall(r'[MmLlCcZz]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', path_data)

        i = 0
        current_x, current_y = 0.0, 0.0
        current_command = None

        while i < len(tokens):
            token = tokens[i]

            # Check if token is a command
            if token in 'MmLlCcZz':
                current_command = token
                i += 1
                continue

            # Process based on current command
            if current_command in ['M', 'm']:
                # Move command
                x = float(token)
                y = float(tokens[i + 1])

                if current_command == 'M':
                    # Absolute move
                    current_x, current_y = x, y
                else:
                    # Relative move
                    current_x += x
                    current_y += y

                self.context.move_to(current_x, current_y)
                i += 2

                # After first M/m coordinate pair, subsequent pairs are treated as L/l
                current_command = 'L' if current_command == 'M' else 'l'

            elif current_command in ['L', 'l']:
                # Line command
                x = float(token)
                y = float(tokens[i + 1])

                if current_command == 'L':
                    # Absolute line
                    current_x, current_y = x, y
                else:
                    # Relative line
                    current_x += x
                    current_y += y

                self.context.line_to(current_x, current_y)
                i += 2

            elif current_command in ['C', 'c']:
                # Cubic Bezier curve
                x1 = float(token)
                y1 = float(tokens[i + 1])
                x2 = float(tokens[i + 2])
                y2 = float(tokens[i + 3])
                x = float(tokens[i + 4])
                y = float(tokens[i + 5])

                if current_command == 'C':
                    # Absolute curve
                    self.context.curve_to(x1, y1, x2, y2, x, y)
                    current_x, current_y = x, y
                else:
                    # Relative curve
                    self.context.curve_to(
                        current_x + x1, current_y + y1,
                        current_x + x2, current_y + y2,
                        current_x + x, current_y + y
                    )
                    current_x += x
                    current_y += y

                i += 6

            elif current_command in ['Z', 'z']:
                # Close path
                self.context.close_path()
                i += 1
                # Reset command to avoid infinite loop
                current_command = None

            else:
                # Unknown command, skip
                i += 1

    def save_png(self, output_path: str) -> None:
        """Save the rendered surface to a PNG file.

        Args:
            output_path: Path where the PNG file will be saved

        Raises:
            ValueError: If surface has not been initialized
        """
        if self.surface is None:
            raise ValueError("Surface not initialized. Call setup_surface() first.")

        self.surface.write_to_png(output_path)
