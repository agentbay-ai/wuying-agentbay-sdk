"""Integration tests for Computer keyboard and mouse operations functionality."""
# ci-stable

import pytest

from agentbay import CreateSessionParams
from agentbay import MouseButton


@pytest.fixture
async def session(make_session):
    """Create a session with windows_latest image.

    Note: Computer module requires a desktop environment.
    Uses windows_latest (computer use image with Windows desktop).
    """
    lc = await make_session(params=CreateSessionParams(image_id="windows_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_click_mouse(session):
    """Test mouse click functionality."""
    # Arrange
    print("\nTest: Mouse click...")

    # Act - Click at center of screen
    result = await session.computer.click_mouse(512, 384, MouseButton.LEFT)

    # Assert
    assert result.success, f"Mouse click failed: {result.error_message}"
    assert result.data is True, "Click should return True"
    print("Mouse click successful")


@pytest.mark.asyncio
async def test_move_mouse(session):
    """Test mouse movement functionality."""
    # Arrange
    print("\nTest: Mouse movement...")

    # Act - Move to a specific position
    move_result = await session.computer.move_mouse(400, 300)

    # Assert
    assert move_result.success, f"Mouse move failed: {move_result.error_message}"
    assert move_result.data is True, "Move should return True"

    # Verify position (optional - get_cursor_position may not be available)
    position_result = await session.computer.get_cursor_position()
    if position_result.success:
        import json

        position = (
            json.loads(position_result.data)
            if isinstance(position_result.data, str)
            else position_result.data
        )
        print(f"Mouse moved to position: {position}")

    print("Mouse movement successful")


@pytest.mark.asyncio
async def test_type_text(session):
    """Test keyboard text input functionality."""
    # Arrange
    print("\nTest: Keyboard text input...")
    test_text = "Hello AgentBay"

    # Act - Type text (note: this requires a focused input field)
    result = await session.computer.input_text(test_text)

    # Assert
    assert result.success, f"Text input failed: {result.error_message}"
    assert result.data is True, "Input should return True"
    print(f"Text input successful: '{test_text}'")


@pytest.mark.asyncio
async def test_keyboard_shortcut(session):
    """Test keyboard shortcut functionality."""
    # Arrange
    print("\nTest: Keyboard shortcut...")

    # Act - Press Ctrl+A (select all)
    result = await session.computer.press_keys(["Ctrl", "a"])

    # Assert
    assert result.success, f"Keyboard shortcut failed: {result.error_message}"
    assert result.data is True, "Press keys should return True"
    print("Keyboard shortcut (Ctrl+A) successful")


@pytest.mark.asyncio
async def test_mouse_double_click(session):
    """Test mouse double click functionality."""
    # Arrange
    print("\nTest: Mouse double click...")

    # Act - Double click at center of screen
    result = await session.computer.click_mouse(512, 384, MouseButton.DOUBLE_LEFT)

    # Assert
    assert result.success, f"Mouse double click failed: {result.error_message}"
    assert result.data is True, "Double click should return True"
    print("Mouse double click successful")


@pytest.mark.asyncio
async def test_mouse_right_click(session):
    """Test mouse right click functionality."""
    # Arrange
    print("\nTest: Mouse right click...")

    # Act - Right click at center of screen
    result = await session.computer.click_mouse(512, 384, MouseButton.RIGHT)

    # Assert
    assert result.success, f"Mouse right click failed: {result.error_message}"
    assert result.data is True, "Right click should return True"
    print("Mouse right click successful")
