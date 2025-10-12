"""Unit tests for Layer Extractor module."""

import pytest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from svg_renderer.parser import SVGParser
from svg_renderer.layer import LayerExtractor


@pytest.fixture
def extractor():
    """Create a LayerExtractor instance from the test SVG."""
    svg_path = Path(__file__).parent / 'fixtures' / 'drawing-example.svg'
    parser = SVGParser(str(svg_path))
    parser.load_svg()

    root = parser.get_root()
    namespaces = parser.get_namespaces()

    return LayerExtractor(root, namespaces)


def test_get_all_layers(extractor):
    """Test getting all layers."""
    layers = extractor.get_all_layers()

    assert len(layers) >= 2  # At least Layer 1 and Layer 2


def test_get_layer_names(extractor):
    """Test getting layer names."""
    names = extractor.get_layer_names()

    assert 'Layer 1' in names
    assert 'Layer 2' in names


def test_get_layer_by_name(extractor):
    """Test finding a layer by name."""
    layer = extractor.get_layer_by_name('Layer 1')

    assert layer is not None
    assert layer.tag.endswith('g')


def test_get_layer_not_found(extractor):
    """Test handling of non-existent layer."""
    with pytest.raises(ValueError) as exc_info:
        extractor.get_layer('NonexistentLayer')

    assert 'not found' in str(exc_info.value).lower()
    assert 'available layers' in str(exc_info.value).lower()


def test_extract_elements(extractor):
    """Test extracting elements from a layer."""
    layer = extractor.get_layer_by_name('Layer 1')
    elements = extractor.extract_elements(layer)

    assert len(elements) > 0
    # Layer 1 should have at least one path or rect


def test_extract_paths(extractor):
    """Test extracting only path elements."""
    layer = extractor.get_layer_by_name('Layer 1')
    paths = extractor.extract_paths(layer)

    assert len(paths) > 0
    for path in paths:
        assert path.tag.endswith('path')


def test_extract_rects(extractor):
    """Test extracting only rect elements."""
    layer = extractor.get_layer_by_name('Layer 1')
    rects = extractor.extract_rects(layer)

    # Layer 1 has at least one rect
    for rect in rects:
        assert rect.tag.endswith('rect')
