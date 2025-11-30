"""Pytest configuration and fixtures for SVG renderer tests."""

import pytest
from pathlib import Path


def pytest_addoption(parser):
    """Add custom command line options and ini options."""
    parser.addoption(
        '--image-threshold',
        action='store',
        default=None,
        type=float,
        help='Maximum allowed image difference ratio (0.0-1.0). Overrides config file setting.'
    )
    # Register custom ini option
    parser.addini(
        'image_diff_threshold',
        default='0.01',
        help='Maximum allowed image difference ratio (0.0-1.0)'
    )


@pytest.fixture
def image_threshold(request):
    """Get image difference threshold from command line or config.

    Priority:
    1. Command line option (--image-threshold)
    2. Config file (pyproject.toml or pytest.ini)
    3. Default value (0.01)
    """
    # Check command line option first
    cli_value = request.config.getoption('--image-threshold')
    if cli_value is not None:
        return cli_value

    # Check config file
    ini_value = request.config.getini('image_diff_threshold')
    if ini_value:
        return float(ini_value)

    # Default value
    return 0.01


@pytest.fixture
def fixtures_dir():
    """Return the path to test fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def temp_output_dir(tmp_path):
    """Return a temporary directory for test outputs."""
    return tmp_path
