"""Integration tests for Computer application management functionality.
ci-stable
"""

import asyncio

import pytest

from agentbay import CreateSessionParams

# Shared state: populated by test_get_installed_apps, consumed by subsequent tests
_shared: dict = {}


@pytest.fixture
async def session(make_session):
    """Create a session for computer apps testing.

    Note: Computer module requires a desktop environment.
    Uses windows_latest (computer use image with Windows desktop).
    """
    lc = await make_session(params=CreateSessionParams(image_id="windows_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_get_installed_apps(session):
    """Test getting list of installed applications."""
    # Arrange
    print("\nTest: Getting installed apps...")

    # Act
    result = await session.computer.get_installed_apps()

    # Assert
    assert result.success, f"Get installed apps failed: {result.error_message}"
    assert result.data is not None, "Apps list should not be None"
    assert isinstance(result.data, list), "Apps should be a list"
    print(f"Found {len(result.data)} installed apps")

    if len(result.data) > 0:
        app = result.data[0]
        assert hasattr(app, "name"), "App should have name"
        assert hasattr(app, "start_cmd"), "App should have start_cmd"
        print(f"First app: {app.name}")

    # Find Google Chrome in installed apps and store for subsequent tests
    chrome_app = None
    for app in result.data:
        if "Google Chrome" in getattr(app, "name", ""):
            chrome_app = app
            print(f"Found Google Chrome: name={app.name}, start_cmd={app.start_cmd}")
            break
    _shared["chrome_app"] = chrome_app
    if chrome_app is None:
        print("Warning: Google Chrome not found in installed apps, subsequent tests will use fallback name")


@pytest.mark.asyncio
async def test_start_app_and_stop_app(session):
    """Test starting an application with parameters."""
    # Arrange
    chrome_app = _shared.get("chrome_app")
    start_cmd = chrome_app.start_cmd if chrome_app else "should skip pytest"
    print(f"\nTest: Starting {start_cmd} with work directory...")
    if start_cmd == "should skip pytest":
        pytest.skip("Google Chrome not found in installed apps")

    # Act
    # Note: 'activity' is for mobile, so we test work_directory here
    result = await session.computer.start_app(start_cmd, "")
    assert result.success, f"Start app with params failed: {result.error_message}"
    pname = result.data[0].pname if result.data else None
    print(f"Started app with pname: {pname} \n")
    print(f"Started app with result.data: {result.data} \n")
    assert pname is not None, "Process name should be set"
    # Assert
    assert result.success, f"Start app with params failed: {result.error_message}"
    assert len(result.data) > 0, "Should have started at least one process"

    # Cleanup
    await session.computer.stop_app_by_pname(pname)


@pytest.mark.asyncio
async def test_app_lifecycle(session):
    """Test full application lifecycle: Find -> Start -> Verify -> Stop -> Verify."""
    print("\nTest: App Lifecycle (Find -> Start -> Verify -> Stop -> Verify)...")

    # 1. Get Installed Apps (use cached result from test_get_installed_apps if available)
    chrome_app = _shared.get("chrome_app")
    if chrome_app:
        start_cmd = chrome_app.start_cmd
        print(f"Using cached Chrome app: name={chrome_app.name}, start_cmd={start_cmd}")
    else:
        # Fallback: query installed apps directly
        installed_apps = await session.computer.get_installed_apps()
        start_cmd = "Google Chrome"
        if installed_apps.success and installed_apps.data:
            for app in installed_apps.data:
                if "Google Chrome" in getattr(app, "name", ""):
                    start_cmd = app.start_cmd
                    print(f"Found app in installed list: {app.name} ({app.start_cmd})")
                    break

    # 2. Start App
    print(f"Starting app with command: {start_cmd}")
    start_result = await session.computer.start_app(start_cmd)
    assert start_result.success, f"Failed to start app: {start_result.error_message}"
    assert len(start_result.data) > 0, "No processes returned"

    pid = start_result.data[0].pid
    print(f"Started app with PID: {pid}")

    # Wait for window
    print("Verifying app visibility (polling)...")
    found_in_visible = False

    # Poll for up to 10 seconds
    for i in range(5):
        visible_apps = await session.computer.list_visible_apps()
        if visible_apps.success and visible_apps.data:
            for p in visible_apps.data:
                if p.pid == pid:
                    found_in_visible = True
                    break

        if found_in_visible:
            print("App found in visible list")
            break

        print(f"App PID {pid} not visible yet, waiting... (attempt {i+1})")
        await asyncio.sleep(2)

    assert found_in_visible, f"Started app (PID {pid}) should be in visible apps list after starting"
    print("Confirmed app is visible")

    # 4. Stop App by PID
    stop_result = await session.computer.stop_app_by_pid(pid)
    assert stop_result.success, f"Failed to stop app: {stop_result.error_message}"
    print(f"Stopped app with PID: {pid}")

    # 5. Verify it's gone
    await asyncio.sleep(2)
    visible_apps_after = await session.computer.list_visible_apps()

    found_after_stop = False
    if visible_apps_after.data:
        for p in visible_apps_after.data:
            if p.pid == pid:
                found_after_stop = True
                break

    assert not found_after_stop, f"App (PID {pid}) should not be in visible apps list after stopping"
    print("Confirmed app is no longer visible")
