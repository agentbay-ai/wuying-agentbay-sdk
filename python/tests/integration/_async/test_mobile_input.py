"""Integration tests for Mobile input operations functionality."""

import pytest
import pytest_asyncio

from agentbay import KeyCode


@pytest_asyncio.fixture
async def session(make_session):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile input testing...")
    lc = await make_session("mobile_latest")
    session = lc._result.session
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_tap(session):
    """Test tap operation."""
    # Arrange
    print("\nTest: Tap operation...")

    # Act - Tap at center of screen
    result = await session.mobile.tap(500, 800)

    # Assert
    assert result.success, f"Tap failed: {result.error_message}"
    assert result.data is True, "Tap should return True"
    print("Tap operation successful")


@pytest.mark.asyncio
async def test_swipe(session):
    """Test swipe operation."""
    # Arrange
    print("\nTest: Swipe operation...")

    # Act - Swipe from bottom to top
    result = await session.mobile.swipe(500, 1500, 500, 500, duration_ms=500)

    # Assert
    assert result.success, f"Swipe failed: {result.error_message}"
    assert result.data is True, "Swipe should return True"
    print("Swipe operation successful")


@pytest.mark.asyncio
async def test_input_text(session):
    """Test text input operation."""
    # Arrange
    print("\nTest: Text input...")
    test_text = "Hello Mobile"

    # Act
    result = await session.mobile.input_text(test_text)

    # Assert
    assert result.success, f"Input text failed: {result.error_message}"
    assert result.data is True, "Input should return True"
    print(f"Text input successful: '{test_text}'")


@pytest.mark.asyncio
async def test_press_key(session):
    """Test key press operation."""
    # Arrange
    print("\nTest: Press HOME key...")

    # Act - Press HOME key
    result = await session.mobile.send_key(KeyCode.KEYCODE_HOME)

    # Assert
    assert result.success, f"Press key failed: {result.error_message}"
    assert result.data is True, "Press key should return True"
    print("Key press successful")
