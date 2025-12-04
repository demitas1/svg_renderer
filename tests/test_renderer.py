"""Unit tests for Renderer module - bitmap rendering tests."""

import pytest
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from svg_renderer import SVGRenderer

# Pillow is required for image comparison
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def compare_images(img1_path: str, img2_path: str, threshold: float) -> tuple[bool, float]:
    """Compare two images and return whether they match within threshold.

    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        threshold: Maximum allowed difference ratio (0.0-1.0)

    Returns:
        Tuple of (is_match, actual_diff_ratio)
    """
    img1 = Image.open(img1_path).convert('RGBA')
    img2 = Image.open(img2_path).convert('RGBA')

    # Check dimensions
    if img1.size != img2.size:
        return False, 1.0

    # Compare pixels
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    total_pixels = len(pixels1)
    diff_pixels = 0

    for p1, p2 in zip(pixels1, pixels2):
        if p1 != p2:
            diff_pixels += 1

    diff_ratio = diff_pixels / total_pixels
    is_match = diff_ratio <= threshold

    return is_match, diff_ratio


def compare_images_ignore_transparent(
    img1_path: str, img2_path: str, threshold: float
) -> tuple[bool, float, int, int]:
    """Compare two images, ignoring fully transparent pixels in both.

    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        threshold: Maximum allowed difference ratio (0.0-1.0)

    Returns:
        Tuple of (is_match, actual_diff_ratio, compared_count, diff_count)
    """
    img1 = Image.open(img1_path).convert('RGBA')
    img2 = Image.open(img2_path).convert('RGBA')

    # Check dimensions
    if img1.size != img2.size:
        return False, 1.0, 0, 0

    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    compared_count = 0
    diff_count = 0

    for p1, p2 in zip(pixels1, pixels2):
        # Skip if both pixels are fully transparent (alpha == 0)
        if p1[3] == 0 and p2[3] == 0:
            continue

        compared_count += 1
        if p1 != p2:
            diff_count += 1

    if compared_count == 0:
        return True, 0.0, 0, 0

    diff_ratio = diff_count / compared_count
    is_match = diff_ratio <= threshold

    return is_match, diff_ratio, compared_count, diff_count


# =============================================================================
# Cairo Rendering Tests - Tests against expected Cairo output
# =============================================================================

@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow is required for image comparison")
class TestCairoRectRendering:
    """Tests for Cairo rendering of rect elements."""

    def test_render_rect_to_png(self, fixtures_dir, temp_output_dir, image_threshold):
        """Test rendering a rect element matches expected Cairo output."""
        svg_path = fixtures_dir / 'rect-only.svg'
        expected_png = fixtures_dir / 'expected_rect.png'
        output_png = temp_output_dir / 'output_rect.png'

        # Render
        renderer = SVGRenderer(str(svg_path))
        renderer.render_layer_to_png('Layer 1', str(output_png))

        # Verify output file exists
        assert output_png.exists(), f"Output file not created: {output_png}"

        # Compare with expected
        is_match, diff_ratio = compare_images(
            str(expected_png),
            str(output_png),
            image_threshold
        )

        assert is_match, (
            f"Image difference {diff_ratio:.4f} exceeds threshold {image_threshold}. "
            f"Output saved to: {output_png}"
        )


@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow is required for image comparison")
class TestCairoPathRendering:
    """Tests for Cairo rendering of path elements."""

    def test_render_path_to_png(self, fixtures_dir, temp_output_dir, image_threshold):
        """Test rendering a path element matches expected Cairo output."""
        svg_path = fixtures_dir / 'path-only.svg'
        expected_png = fixtures_dir / 'expected_path.png'
        output_png = temp_output_dir / 'output_path.png'

        # Render
        renderer = SVGRenderer(str(svg_path))
        renderer.render_layer_to_png('Layer 1', str(output_png))

        # Verify output file exists
        assert output_png.exists(), f"Output file not created: {output_png}"

        # Compare with expected
        is_match, diff_ratio = compare_images(
            str(expected_png),
            str(output_png),
            image_threshold
        )

        assert is_match, (
            f"Image difference {diff_ratio:.4f} exceeds threshold {image_threshold}. "
            f"Output saved to: {output_png}"
        )


@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow is required for image comparison")
class TestImageDimensions:
    """Tests for verifying output image dimensions."""

    def test_output_dimensions_match_viewbox(self, fixtures_dir, temp_output_dir):
        """Test that output image dimensions match SVG viewBox."""
        svg_path = fixtures_dir / 'rect-only.svg'
        output_png = temp_output_dir / 'output_dimensions.png'

        # Render
        renderer = SVGRenderer(str(svg_path))
        renderer.render_layer_to_png('Layer 1', str(output_png))

        # Check dimensions
        img = Image.open(output_png)
        # viewBox is "0 0 100 100" so output should be 100x100
        assert img.size == (100, 100), f"Expected (100, 100) but got {img.size}"


# =============================================================================
# Inkscape Compatibility Tests - Tests against Inkscape exported PNGs
# =============================================================================

@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow is required for image comparison")
class TestInkscapeCompatibility:
    """Tests comparing renderer output with Inkscape exported PNGs.

    These tests verify that our renderer produces visually similar output
    to Inkscape. Fully transparent pixels are ignored in comparison since
    Cairo and Inkscape may use different RGB values for transparent pixels.

    Note: Some tests may fail due to minor differences in stroke rendering
    and anti-aliasing between Cairo and Inkscape.
    """

    def test_rect_matches_inkscape(self, fixtures_dir, temp_output_dir, image_threshold):
        """Test that rect rendering matches Inkscape output."""
        svg_path = fixtures_dir / 'rect-only.svg'
        inkscape_png = fixtures_dir / 'rect-only-inkscape.png'
        output_png = temp_output_dir / 'output_rect_inkscape_cmp.png'

        # Render
        renderer = SVGRenderer(str(svg_path))
        renderer.render_layer_to_png('Layer 1', str(output_png))

        # Compare with Inkscape output, ignoring transparent pixels
        is_match, diff_ratio, compared, diff = compare_images_ignore_transparent(
            str(inkscape_png),
            str(output_png),
            image_threshold
        )

        assert is_match, (
            f"Inkscape compatibility: {diff}/{compared} pixels differ "
            f"({diff_ratio*100:.2f}%), threshold {image_threshold*100:.2f}%. "
            f"Output saved to: {output_png}"
        )

    def test_path_matches_inkscape(self, fixtures_dir, temp_output_dir, image_threshold):
        """Test that path rendering matches Inkscape output."""
        svg_path = fixtures_dir / 'path-only.svg'
        inkscape_png = fixtures_dir / 'path-only-inkscape.png'
        output_png = temp_output_dir / 'output_path_inkscape_cmp.png'

        # Render
        renderer = SVGRenderer(str(svg_path))
        renderer.render_layer_to_png('Layer 1', str(output_png))

        # Compare with Inkscape output, ignoring transparent pixels
        is_match, diff_ratio, compared, diff = compare_images_ignore_transparent(
            str(inkscape_png),
            str(output_png),
            image_threshold
        )

        assert is_match, (
            f"Inkscape compatibility: {diff}/{compared} pixels differ "
            f"({diff_ratio*100:.2f}%), threshold {image_threshold*100:.2f}%. "
            f"Output saved to: {output_png}"
        )


# =============================================================================
# Inkscape Compatibility Tests with DPI - Tests against Inkscape 300dpi exports
# =============================================================================

# Test cases for DPI-aware rendering
# Format: (svg_name, inkscape_png_name, layer_name, dpi, expected_size, description)
# To add new test cases, simply add entries to this list
DPI_TEST_CASES = [
    (
        'inkscape-drawing-path-1.svg',
        'inkscape-drawing-path-1.png',
        'Layer 1',
        300,
        (2480, 3508),
        'Bezier curve path (C command)'
    ),
    # Add more test cases here as needed:
    # ('new-test.svg', 'new-test.png', 'Layer 1', 300, (width, height), 'description'),
]


def compare_images_rgb_only(
    img1_path: str, img2_path: str, threshold: float
) -> tuple[bool, float, int, int]:
    """Compare two images by RGB values only where both have alpha > 0.

    This comparison ignores alpha channel differences which can occur due to
    different anti-aliasing algorithms between Cairo and Inkscape.

    Args:
        img1_path: Path to first image
        img2_path: Path to second image
        threshold: Maximum allowed difference ratio (0.0-1.0)

    Returns:
        Tuple of (is_match, actual_diff_ratio, compared_count, diff_count)
    """
    img1 = Image.open(img1_path).convert('RGBA')
    img2 = Image.open(img2_path).convert('RGBA')

    # Check dimensions
    if img1.size != img2.size:
        return False, 1.0, 0, 0

    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    compared_count = 0
    diff_count = 0

    for p1, p2 in zip(pixels1, pixels2):
        # Only compare where BOTH pixels have alpha > 0
        if p1[3] > 0 and p2[3] > 0:
            compared_count += 1
            # Compare RGB only (ignore alpha)
            if p1[:3] != p2[:3]:
                diff_count += 1

    if compared_count == 0:
        return True, 0.0, 0, 0

    diff_ratio = diff_count / compared_count
    is_match = diff_ratio <= threshold

    return is_match, diff_ratio, compared_count, diff_count


@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow is required for image comparison")
class TestInkscapeCompatibilityDPI:
    """Tests comparing renderer output with Inkscape exported PNGs at specific DPI.

    These tests verify that:
    1. Output image dimensions match expected size for the given DPI
    2. RGB values match between Cairo and Inkscape output (alpha differences allowed)

    Test cases are defined in DPI_TEST_CASES list for easy extension.
    To add new tests, add SVG and PNG files to tests/fixtures/ and add an entry
    to DPI_TEST_CASES.
    """

    @pytest.mark.parametrize(
        'svg_name,inkscape_png_name,layer_name,dpi,expected_size,description',
        DPI_TEST_CASES,
        ids=[case[5] for case in DPI_TEST_CASES]  # Use description as test ID
    )
    def test_dpi_rendering_matches_inkscape(
        self,
        fixtures_dir,
        temp_output_dir,
        image_threshold,
        svg_name,
        inkscape_png_name,
        layer_name,
        dpi,
        expected_size,
        description
    ):
        """Test that DPI-aware rendering matches Inkscape output."""
        svg_path = fixtures_dir / svg_name
        inkscape_png = fixtures_dir / inkscape_png_name
        output_png = temp_output_dir / f'output_{svg_name.replace(".svg", "")}.png'

        # Skip if fixture files don't exist
        if not svg_path.exists():
            pytest.skip(f"SVG fixture not found: {svg_path}")
        if not inkscape_png.exists():
            pytest.skip(f"Inkscape PNG fixture not found: {inkscape_png}")

        # Render with DPI
        renderer = SVGRenderer(str(svg_path), dpi=dpi)
        renderer.render_layer_to_png(layer_name, str(output_png))

        # Verify output dimensions
        output_img = Image.open(output_png)
        assert output_img.size == expected_size, (
            f"Output size mismatch: expected {expected_size}, got {output_img.size}"
        )

        # Compare RGB values (ignoring alpha differences from anti-aliasing)
        is_match, diff_ratio, compared, diff = compare_images_rgb_only(
            str(inkscape_png),
            str(output_png),
            image_threshold
        )

        assert is_match, (
            f"Inkscape DPI compatibility ({description}): "
            f"{diff}/{compared} pixels differ ({diff_ratio*100:.4f}%), "
            f"threshold {image_threshold*100:.4f}%. "
            f"Output saved to: {output_png}"
        )

    @pytest.mark.parametrize(
        'svg_name,inkscape_png_name,layer_name,dpi,expected_size,description',
        DPI_TEST_CASES,
        ids=[case[5] for case in DPI_TEST_CASES]
    )
    def test_dpi_output_dimensions(
        self,
        fixtures_dir,
        temp_output_dir,
        svg_name,
        inkscape_png_name,
        layer_name,
        dpi,
        expected_size,
        description
    ):
        """Test that output dimensions match expected size at given DPI."""
        svg_path = fixtures_dir / svg_name
        output_png = temp_output_dir / f'output_dim_{svg_name.replace(".svg", "")}.png'

        if not svg_path.exists():
            pytest.skip(f"SVG fixture not found: {svg_path}")

        # Render with DPI
        renderer = SVGRenderer(str(svg_path), dpi=dpi)
        renderer.render_layer_to_png(layer_name, str(output_png))

        # Verify dimensions
        output_img = Image.open(output_png)
        assert output_img.size == expected_size, (
            f"Dimension test ({description}): "
            f"expected {expected_size}, got {output_img.size}"
        )
