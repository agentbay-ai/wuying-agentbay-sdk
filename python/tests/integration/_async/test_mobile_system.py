"""Integration tests for Mobile system functionality."""
# ci-stable
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

