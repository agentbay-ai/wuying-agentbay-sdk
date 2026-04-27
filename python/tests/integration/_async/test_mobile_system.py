"""Integration tests for Mobile system functionality."""

import pytest
import pytest_asyncio

from agentbay import AgentBayError
from agentbay import BoolResult, OperationResult
from agentbay import InstalledAppListResult, ProcessListResult
from agentbay import KeyCode, UIElementListResult


@pytest_asyncio.fixture
async def session(make_session):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile system testing...")
    lc = await make_session("mobile_latest")
    session = lc._result.session
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_get_installed_apps(session):
    """Test retrieving installed applications."""
    try:
        result = await session.mobile.get_installed_apps(
            start_menu=True, desktop=False, ignore_system_apps=True
        )
        assert isinstance(result, InstalledAppListResult)
        assert result.success, f"Failed to get installed apps: {result.error_message}"

        installed_apps = result.data
        print("\nInstalled Applications:")
        for app in installed_apps:
            print(f"Name: {app.name}, Start Command: {app.start_cmd}")
    except AgentBayError as e:
        pytest.fail(f"get_installed_apps failed with error: {e}")


@pytest.mark.asyncio
async def test_start_and_stop_app(session):
    """Test starting and stopping an application."""
    try:
        # Start an application (using Android Settings which should be available)
        start_cmd = (
            "monkey -p com.android.settings -c android.intent.category.LAUNCHER 1"
        )
        start_result = await session.mobile.start_app(start_cmd)
        assert isinstance(start_result, ProcessListResult)
        assert start_result.success, f"Failed to start app: {start_result.error_message}"

        processes = start_result.data
        print("\nStart App Result:", processes)

        # Stop the application
        stop_cmd = "am force-stop com.android.settings"
        stop_result = await session.mobile.stop_app_by_cmd(stop_cmd)
        assert stop_result.success, f"Failed to stop app: {stop_result.error_message}"
        print("\nApplication stopped successfully.")
    except AgentBayError as e:
        pytest.fail(f"start_and_stop_app failed with error: {e}")


@pytest.mark.asyncio
async def test_get_clickable_ui_elements(session):
    """Test retrieving clickable UI elements."""
    try:
        result = await session.mobile.get_clickable_ui_elements(timeout_ms=10000)
        assert isinstance(result, UIElementListResult)
        assert result.success, f"Failed to get clickable UI elements: {result.error_message}"

        clickable_elements = result.elements
        print("\nClickable UI Elements:")
        for element in clickable_elements:
            print(element)
    except AgentBayError as e:
        pytest.fail(f"get_clickable_ui_elements failed with error: {e}")


@pytest.mark.asyncio
async def test_tap(session):
    """Test tapping on a specific coordinate."""
    try:
        x, y = 100, 200
        result = await session.mobile.tap(x, y)
        assert isinstance(result, BoolResult)
        assert result.success, f"Failed to tap: {result.error_message}"
        print(f"\nTapped on coordinates ({x}, {y}) successfully.")
    except AgentBayError as e:
        pytest.fail(f"tap failed with error: {e}")


@pytest.mark.asyncio
async def test_send_key(session):
    """Test sending a key press event."""
    try:
        result = await session.mobile.send_key(KeyCode.KEYCODE_HOME)
        assert isinstance(result, BoolResult)
        assert result.success, f"Failed to send key: {result.error_message}"
        print("\nSent HOME key successfully.")
    except AgentBayError as e:
        pytest.fail(f"send_key failed with error: {e}")


@pytest.mark.asyncio
async def test_swipe(session):
    """Test performing a swipe gesture."""
    try:
        start_x, start_y, end_x, end_y, duration_ms = 100, 200, 300, 400, 500
        result = await session.mobile.swipe(
            start_x, start_y, end_x, end_y, duration_ms
        )
        assert isinstance(result, BoolResult)
        assert result.success, f"Failed to swipe: {result.error_message}"
        print(
            f"\nSwipe performed successfully from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {duration_ms}ms."
        )
    except AgentBayError as e:
        pytest.fail(f"swipe failed with error: {e}")


@pytest.mark.asyncio
async def test_input_text(session):
    """Test inputting text into the active field."""
    try:
        text = "Hello, world!"
        result = await session.mobile.input_text(text)
        assert isinstance(result, BoolResult)
        assert result.success, f"Failed to input text: {result.error_message}"
        print(f"\nInput text '{text}' successfully.")
    except AgentBayError as e:
        pytest.fail(f"input_text failed with error: {e}")


@pytest.mark.asyncio
async def test_get_all_ui_elements(session):
    """Test retrieving all UI elements."""
    try:
        result = await session.mobile.get_all_ui_elements(timeout_ms=10000)
        assert isinstance(result, UIElementListResult)
        assert result.success, f"Failed to get all UI elements: {result.error_message}"

        ui_elements = result.elements
        print("\nAll UI Elements:")
        for element in ui_elements:
            print(element)
    except AgentBayError as e:
        pytest.fail(f"get_all_ui_elements failed with error: {e}")


@pytest.mark.asyncio
async def test_screenshot(session):
    """Test taking a screenshot."""
    try:
        result = await session.mobile.screenshot()
        assert isinstance(result, OperationResult)
        assert result.success, f"Failed to take screenshot: {result.error_message}"
        screenshot_path = result.data
        assert isinstance(screenshot_path, str)
        print(f"\nScreenshot saved to: {screenshot_path}")
    except AgentBayError as e:
        pytest.fail(f"screenshot failed with error: {e}")
