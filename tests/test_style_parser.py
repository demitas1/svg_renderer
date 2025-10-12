"""Unit tests for Style Parser module."""

import pytest
from pathlib import Path
import sys
from lxml import etree

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from svg_renderer.style import StyleParser


def test_parse_style_attribute():
    """Test parsing CSS-style attribute."""
    element = etree.Element('path')
    element.set('style', 'fill:#ffffff;stroke:#000000;stroke-width:2')

    parser = StyleParser(element)
    styles = parser.parse_style()

    assert 'fill' in styles
    assert 'stroke' in styles
    assert 'stroke-width' in styles
    assert styles['fill'] == '#ffffff'
    assert styles['stroke'] == '#000000'
    assert styles['stroke-width'] == '2'


def test_parse_individual_attributes():
    """Test parsing individual SVG attributes."""
    element = etree.Element('rect')
    element.set('fill', '#ff0000')
    element.set('stroke', '#0000ff')
    element.set('stroke-width', '5')

    parser = StyleParser(element)
    styles = parser.parse_style()

    assert styles['fill'] == '#ff0000'
    assert styles['stroke'] == '#0000ff'
    assert styles['stroke-width'] == '5'


def test_get_color_hex():
    """Test hex color conversion."""
    element = etree.Element('path')
    parser = StyleParser(element)

    # Test 6-digit hex
    color = parser.get_color('#ff0000')
    assert color == (1.0, 0.0, 0.0)

    # Test 3-digit hex
    color = parser.get_color('#f00')
    assert color[0] == pytest.approx(1.0)
    assert color[1] == pytest.approx(0.0)
    assert color[2] == pytest.approx(0.0)


def test_get_color_named():
    """Test named color conversion."""
    element = etree.Element('path')
    parser = StyleParser(element)

    color = parser.get_color('red')
    assert color == (1.0, 0.0, 0.0)

    color = parser.get_color('white')
    assert color == (1.0, 1.0, 1.0)


def test_get_color_none():
    """Test handling of 'none' color."""
    element = etree.Element('path')
    parser = StyleParser(element)

    color = parser.get_color('none')
    assert color is None


def test_get_stroke_width():
    """Test parsing stroke width."""
    element = etree.Element('path')
    parser = StyleParser(element)

    width = parser.get_stroke_width('5')
    assert width == 5.0

    width = parser.get_stroke_width('2.5px')
    assert width == 2.5


def test_get_opacity():
    """Test parsing opacity values."""
    element = etree.Element('path')
    parser = StyleParser(element)

    opacity = parser.get_opacity('0.5')
    assert opacity == 0.5

    opacity = parser.get_opacity('50%')
    assert opacity == 0.5

    opacity = parser.get_opacity('1.0')
    assert opacity == 1.0
