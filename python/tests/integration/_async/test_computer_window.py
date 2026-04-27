"""Integration tests for Computer window management functionality."""

import asyncio
import aiohttp
from pathlib import Path

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


async def save_screenshot_from_url(screenshot_url: str, filename: str) -> None:
    """Download screenshot from URL and save as PNG file in python/screenshots directory."""
    # Get the current file's directory and navigate to python root
    current_dir = Path(__file__).parent
    python_root = current_dir.parent.parent.parent  # Go up from tests/integration/_async to python root
    screenshots_dir = python_root / "screenshots"

    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)

    print(f"DEBUG: Downloading screenshot from URL: {screenshot_url}")

    # Download the screenshot from URL using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(screenshot_url) as response:
            response.raise_for_status()
            image_data = await response.read()

    # Validate that we have some image data
    if len(image_data) == 0:
        raise ValueError("Downloaded image data is empty")

    print(f"DEBUG: Downloaded image data length: {len(image_data)} bytes")

    # Write to file
    file_path = screenshots_dir / filename
    with open(file_path, 'wb') as f:
        f.write(image_data)

    print(f"DEBUG: Successfully saved screenshot to {file_path}")


@pytest.mark.asyncio
async def test_window_management_lifecycle(session):
    """Test complete window management lifecycle with Calculator."""
    print("\nTest: Window Management Lifecycle...")

    # Start Calculator app
    print("Starting Calculator app...")
    installed_apps_result = await session.computer.get_installed_apps()
    if installed_apps_result.success and len(installed_apps_result.data) > 0:
        print(f"  ✅ Found {len(installed_apps_result.data)} installed applications")

        # Find a suitable app to work with (prefer Calculator, fallback to first app)
        target_app = None
        for app in installed_apps_result.data:
            if hasattr(app, 'name') and ("calculator" in app.name.lower() or "计算器" in app.name.lower()):
                target_app = app
                print(f"  🎯 Selected Calculator for demonstration")
                break

        if target_app is None:
            target_app = installed_apps_result.data[0]
            app_name = getattr(target_app, 'name', 'Unknown App')
            print(f"  🎯 Selected {app_name} for demonstration")

        start_cmd = target_app.start_cmd
        print(f"  Starting start_cmd {start_cmd}...")
        app_name = getattr(target_app, 'name', 'Unknown App')
    else:
        pytest.fail(f"Failed to get installed apps: {installed_apps_result.error_message}")
    assert installed_apps_result.success, f"Failed to start Calculator: {installed_apps_result.error_message}"
    assert len(installed_apps_result.data) > 0, "No processes returned"

    # Wait for app to be fully loaded
    await asyncio.sleep(3)

    # Start the application
    print(f"  Starting {app_name}...")
    app_pname = None
    start_result = await session.computer.start_app(start_cmd)
    if start_result.success and len(start_result.data) > 0:
        print(f"  ✅ Application started successfully")

        # Get process information for cleanup
        first_process = start_result.data[0]
        app_pname = getattr(first_process, 'pname', None)

        # Wait for app to fully start
        await asyncio.sleep(3)
    else:
        pytest.fail(f"Failed to start application: {start_result.error_message}")
    calculator_window_id = None

    # Test ListRootWindows
    print("Testing list_root_windows...")
    windows_result = await session.computer.list_root_windows()
    assert windows_result.success, f"List root windows failed: {windows_result.error_message}"
    assert windows_result.windows is not None, "Windows list should not be None"
    assert isinstance(windows_result.windows, list), "Windows should be a list"

    # Find Calculator window
    for window in windows_result.windows:
        print(f"Found window: {window.title} (ID: {window.window_id})")

    target_window = windows_result.windows[0]
    calculator_window_id = target_window.window_id
    window_title = target_window.title
    print(f"  🎯 Selected window: ID={calculator_window_id}, Title='{window_title}'")

    assert calculator_window_id is not None, "Calculator window should be found in root windows list"
    assert calculator_window_id > 0, "Calculator window ID should be valid"

    # Test ActivateWindow
    print("Testing activate_window...")
    activate_result = await session.computer.activate_window(calculator_window_id)
    assert activate_result.success, f"Activate window failed: {activate_result.error_message}"
    print(f"Successfully activated Calculator window (ID: {calculator_window_id})")
    await asyncio.sleep(1)

    # Test GetActiveWindow
    print("Testing get_active_window...")
    active_result = await session.computer.get_active_window()
    assert active_result.success, f"Get active window failed: {active_result.error_message}"
    assert active_result.window is not None, "Active window should not be None"

    if active_result.window:
        print(f"Active window: {active_result.window.title} (ID: {active_result.window.window_id})({calculator_window_id})")

    # Test FocusMode
    print("Testing focus_mode...")
    focus_on_result = await session.computer.focus_mode(True)
    assert focus_on_result.success, f"Focus mode on failed: {focus_on_result.error_message}"
    print("Focus mode enabled successfully")
    await asyncio.sleep(1)

    focus_off_result = await session.computer.focus_mode(False)
    assert focus_off_result.success, f"Focus mode off failed: {focus_off_result.error_message}"
    print("Focus mode disabled successfully")

    # Test MaximizeWindow
    print("Testing maximize_window...")
    maximize_result = await session.computer.maximize_window(calculator_window_id)
    assert maximize_result.success, f"Maximize window failed: {maximize_result.error_message}"
    print("Calculator window maximized successfully")
    await asyncio.sleep(2)

    # Take screenshot after maximize
    print("Taking screenshot after maximize...")
    screenshot_result = await session.computer.screenshot()
    if screenshot_result.success and screenshot_result.data:
        try:
            await save_screenshot_from_url(screenshot_result.data, "calculator_maximized.png")
            print("Maximized screenshot saved as calculator_maximized.png")
        except Exception as e:
            print(f"Warning: Failed to save maximized screenshot: {e}")
    else:
        print(f"Screenshot failed or returned empty data: {screenshot_result.error_message}")

    # Test MinimizeWindow
    print("Testing minimize_window...")
    minimize_result = await session.computer.minimize_window(calculator_window_id)
    assert minimize_result.success, f"Minimize window failed: {minimize_result.error_message}"
    print("Calculator window minimized successfully")
    await asyncio.sleep(2)

    # Take screenshot after minimize
    print("Taking screenshot after minimize...")
    screenshot_result = await session.computer.screenshot()
    if screenshot_result.success and screenshot_result.data:
        try:
            await save_screenshot_from_url(screenshot_result.data, "calculator_minimized.png")
            print("Minimized screenshot saved as calculator_minimized.png")
        except Exception as e:
            print(f"Warning: Failed to save minimized screenshot: {e}")
    else:
        print(f"Screenshot failed or returned empty data: {screenshot_result.error_message}")

    # Test RestoreWindow
    print("Testing restore_window...")
    restore_result = await session.computer.restore_window(calculator_window_id)
    assert restore_result.success, f"Restore window failed: {restore_result.error_message}"
    print("Calculator window restored successfully")
    await asyncio.sleep(2)

    # Take screenshot after restore
    print("Taking screenshot after restore...")
    screenshot_result = await session.computer.screenshot()
    if screenshot_result.success and screenshot_result.data:
        try:
            await save_screenshot_from_url(screenshot_result.data, "calculator_restored.png")
            print("Restored screenshot saved as calculator_restored.png")
        except Exception as e:
            print(f"Warning: Failed to save restored screenshot: {e}")
    else:
        print(f"Screenshot failed or returned empty data: {screenshot_result.error_message}")

    # Test ResizeWindow
    print("Testing resize_window...")
    resize_result = await session.computer.resize_window(calculator_window_id, 600, 400)
    assert resize_result.success, f"Resize window failed: {resize_result.error_message}"
    print("Calculator window resized to 600x400 successfully")
    await asyncio.sleep(2)

    # Take screenshot after resize
    print("Taking screenshot after resize...")
    screenshot_result = await session.computer.screenshot()
    if screenshot_result.success and screenshot_result.data:
        try:
            await save_screenshot_from_url(screenshot_result.data, "calculator_resized.png")
            print("Resized screenshot saved as calculator_resized.png")
        except Exception as e:
            print(f"Warning: Failed to save resized screenshot: {e}")
    else:
        print(f"Screenshot failed or returned empty data: {screenshot_result.error_message}")

    # Test FullscreenWindow
    print("Testing fullscreen_window...")
    fullscreen_result = await session.computer.fullscreen_window(calculator_window_id)
    assert fullscreen_result.success, f"Fullscreen window failed: {fullscreen_result.error_message}"
    print("Calculator window set to fullscreen successfully")
    await asyncio.sleep(2)

    # Take screenshot after fullscreen
    print("Taking screenshot after fullscreen...")
    screenshot_result = await session.computer.screenshot()
    if screenshot_result.success and screenshot_result.data:
        try:
            await save_screenshot_from_url(screenshot_result.data, "calculator_fullscreen.png")
            print("Fullscreen screenshot saved as calculator_fullscreen.png")
        except Exception as e:
            print(f"Warning: Failed to save fullscreen screenshot: {e}")
    else:
        print(f"Screenshot failed or returned empty data: {screenshot_result.error_message}")

    # Cleanup - CloseWindow
    print("Cleaning up: Closing Calculator window...")
    close_result = await session.computer.close_window(calculator_window_id)
    if close_result.success:
        print("Calculator window closed successfully")
    else:
        print(f"Warning: Failed to close Calculator window: {close_result.error_message}")


@pytest.mark.asyncio
async def test_list_root_windows(session):
    """Test listing root windows."""
    print("\nTest: Listing root windows...")

    # Act
    result = await session.computer.list_root_windows()

    # Assert
    assert result.success, f"List root windows failed: {result.error_message}"
    assert result.windows is not None, "Windows list should not be None"
    assert isinstance(result.windows, list), "Windows should be a list"
    print(f"Found {len(result.windows)} root windows")

    if len(result.windows) > 0:
        window = result.windows[0]
        assert hasattr(window, "title"), "Window should have title"
        assert hasattr(window, "window_id"), "Window should have window_id"
        print(f"First window: {window.title} (ID: {window.window_id})")


@pytest.mark.asyncio
async def test_get_active_window(session):
    """Test getting the active window."""
    print("\nTest: Getting active window...")

    # Act
    result = await session.computer.get_active_window()

    # Assert
    assert result.success, f"Get active window failed: {result.error_message}"
    # Note: active window might be None if no window is active
    if result.window:
        assert hasattr(result.window, "title"), "Active window should have title"
        assert hasattr(result.window, "window_id"), "Active window should have window_id"
        print(f"Active window: {result.window.title} (ID: {result.window.window_id})")
    else:
        print("No active window found")


@pytest.mark.asyncio
async def test_focus_mode(session):
    """Test focus mode functionality."""
    print("\nTest: Focus mode...")

    # Test enabling focus mode
    result_on = await session.computer.focus_mode(True)
    assert result_on.success, f"Focus mode on failed: {result_on.error_message}"
    print("Focus mode enabled successfully")

    await asyncio.sleep(1)

    # Test disabling focus mode
    result_off = await session.computer.focus_mode(False)
    assert result_off.success, f"Focus mode off failed: {result_off.error_message}"
    print("Focus mode disabled successfully")


@pytest.mark.asyncio
async def test_screenshot(session):
    """Test screenshot functionality."""
    print("\nTest: Screenshot...")
    if session.get_link_url():
        pytest.skip("This cloud environment does not support `screenshot()`")

    # Take a screenshot
    result = await session.computer.screenshot()

    # Assert
    assert result.success, f"Screenshot failed: {result.error_message}"
    assert result.data is not None, "Screenshot data should not be None"
    assert isinstance(result.data, str), "Screenshot data should be a string (URL)"
    assert len(result.data) > 0, "Screenshot data should not be empty"
    print(f"Screenshot taken successfully: {result.data}")

    # Save screenshot to file
    if result.success and result.data:
        try:
            await save_screenshot_from_url(result.data, "test_screenshot.png")
            print("Test screenshot saved as test_screenshot.png")
        except Exception as e:
            print(f"Warning: Failed to save test screenshot: {e}")
