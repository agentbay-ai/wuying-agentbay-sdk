"""Integration tests for Computer screen operations functionality."""

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def session(make_session):
    """Create a session with windows_latest image.

    Note: Computer module requires a desktop environment.
    Uses windows_latest (computer use image with Windows desktop).
    """
    lc = await make_session(params=CreateSessionParams(image_id="windows_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_take_screenshot(session):
    """Test screenshot functionality."""
    # Arrange
    print("\nTest: Taking screenshot...")

    # Act
    result = await session.computer.screenshot()

    # Assert
    assert result.success, f"Screenshot failed: {result.error_message}"
    assert result.data is not None, "Screenshot data should not be None"
    assert isinstance(result.data, str), "Screenshot data should be a string (URL)"
    assert len(result.data) > 0, "Screenshot URL should not be empty"
    print(f"Screenshot taken successfully: {result.data}")


@pytest.mark.asyncio
async def test_get_screen_size(session):
    """Test getting screen size and DPI information."""
    # Arrange
    print("\nTest: Getting screen size...")

    # Act
    result = await session.computer.get_screen_size()

    # Assert
    assert result.success, f"Get screen size failed: {result.error_message}"
    assert result.data is not None, "Screen size data should not be None"

    # Parse JSON if data is a string
    import json

    if isinstance(result.data, str):
        data = json.loads(result.data)
    else:
        data = result.data

    assert "width" in data, "Screen size should contain width"
    assert "height" in data, "Screen size should contain height"
    assert isinstance(data["width"], (int, float)), "Width should be numeric"
    assert isinstance(data["height"], (int, float)), "Height should be numeric"
    assert data["width"] > 0, "Width should be positive"
    assert data["height"] > 0, "Height should be positive"

    # DPI scaling factor is optional but should be present
    if "dpiScalingFactor" in data:
        assert isinstance(
            data["dpiScalingFactor"], (int, float)
        ), "DPI scaling factor should be numeric"
        assert data["dpiScalingFactor"] > 0, "DPI scaling factor should be positive"

    print(f"Screen size: {data['width']}x{data['height']}")
    if "dpiScalingFactor" in data:
        print(f"DPI scaling factor: {data['dpiScalingFactor']}")


@pytest.mark.asyncio
async def test_screen_info_consistency(session):
    """Test that screen information is consistent across multiple calls."""
    # Arrange
    print("\nTest: Checking screen info consistency...")

    # Act
    result1 = await session.computer.get_screen_size()
    result2 = await session.computer.get_screen_size()

    # Assert
    assert result1.success, f"First call failed: {result1.error_message}"
    assert result2.success, f"Second call failed: {result2.error_message}"

    # Parse JSON if data is a string
    import json

    data1 = json.loads(result1.data) if isinstance(result1.data, str) else result1.data
    data2 = json.loads(result2.data) if isinstance(result2.data, str) else result2.data

    assert data1["width"] == data2["width"], "Width should be consistent"
    assert data1["height"] == data2["height"], "Height should be consistent"
    print("Screen info is consistent across multiple calls")
