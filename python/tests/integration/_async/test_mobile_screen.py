"""Integration tests for Mobile screen operations functionality."""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def session(make_session):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile screen testing...")
    lc = await make_session("mobile_latest")
    session = lc._result.session
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_take_screenshot(session):
    """Test mobile screenshot functionality."""
    # Arrange
    print("\nTest: Taking mobile screenshot...")

    # Act
    result = await session.mobile.screenshot()

    # Assert
    assert result.success, f"Screenshot failed: {result.error_message}"
    assert result.data is not None, "Screenshot data should not be None"
    assert isinstance(result.data, str), "Screenshot data should be a string (URL)"
    assert len(result.data) > 0, "Screenshot URL should not be empty"
    print(f"Screenshot taken successfully: {result.data}")


@pytest.mark.asyncio
async def test_get_device_info(session):
    """Test getting mobile device information."""
    # Arrange
    print("\nTest: Getting device info...")

    # Act - Use command to get device info
    result = await session.command.execute_command("getprop ro.product.model")

    # Assert
    assert result.success, f"Get device info failed: {result.error_message}"
    assert result.output is not None, "Device info should not be None"
    print(f"Device model: {result.output.strip()}")
