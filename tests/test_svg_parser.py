"""Unit tests for SVG Parser module."""

import pytest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from svg_renderer.parser import SVGParser


def test_load_svg():
    """Test loading a valid SVG file."""
    svg_path = Path(__file__).parent / 'fixtures' / 'drawing-example.svg'
    parser = SVGParser(str(svg_path))
    root = parser.load_svg()

    assert root is not None
    assert root.tag.endswith('svg')


def test_get_viewbox():
    """Test extracting viewBox attribute."""
    svg_path = Path(__file__).parent / 'fixtures' / 'drawing-example.svg'
    parser = SVGParser(str(svg_path))
    parser.load_svg()

    viewbox = parser.get_viewbox()

    assert len(viewbox) == 4
    assert viewbox[0] == 0.0
    assert viewbox[1] == 0.0
    assert viewbox[2] > 0
    assert viewbox[3] > 0


def test_get_namespaces():
    """Test extracting namespaces."""
    svg_path = Path(__file__).parent / 'fixtures' / 'drawing-example.svg'
    parser = SVGParser(str(svg_path))
    parser.load_svg()

    namespaces = parser.get_namespaces()

    assert 'svg' in namespaces
    assert 'inkscape' in namespaces
    assert namespaces['svg'] == 'http://www.w3.org/2000/svg'
    assert namespaces['inkscape'] == 'http://www.inkscape.org/namespaces/inkscape'


def test_file_not_found():
    """Test error handling for missing file."""
    parser = SVGParser('nonexistent.svg')

    with pytest.raises((FileNotFoundError, OSError)):
        parser.load_svg()


def test_get_viewbox_before_load():
    """Test error when trying to get viewBox before loading."""
    svg_path = Path(__file__).parent / 'fixtures' / 'drawing-example.svg'
    parser = SVGParser(str(svg_path))

    with pytest.raises(ValueError):
        parser.get_viewbox()
