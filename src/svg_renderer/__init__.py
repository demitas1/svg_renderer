"""SVG Renderer Package

A Python package for rendering Inkscape SVG layers to PNG or extracting them to new SVG files.
"""

from .api import SVGRenderer
from .parser import SVGParser
from .style import StyleParser
from .layer import LayerExtractor
from .renderer import Renderer
from .writer import SVGWriter

__version__ = '0.1.0'

__all__ = [
    'SVGRenderer',
    'SVGParser',
    'StyleParser',
    'LayerExtractor',
    'Renderer',
    'SVGWriter',
]
