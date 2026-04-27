import typing

import pytest
import pytest_asyncio

from agentbay import AdbUrlResult
from agentbay import CreateSessionParams
from agentbay import AsyncSession


@pytest_asyncio.fixture
async def mobile_session(make_session):
    """Create a mobile session for ADB URL testing."""
    print("Creating a new session for mobile ADB URL testing...")
    params = CreateSessionParams(image_id="mobile_latest")
    lc = await make_session(params=params)
    session = lc._result.session
    assert session is not None, "Session was not created successfully."
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_get_adb_url_e2e_with_valid_key(mobile_session):
    """Test session.mobile.get_adb_url() returns AdbUrlResult with valid adbkey_pub."""
    session: AsyncSession = typing.cast(AsyncSession, mobile_session)

    adbkey_pub = "test_adb_key_123"
    print("Calling session.mobile.get_adb_url() with adbkey_pub...")
    result = session.mobile.get_adb_url(adbkey_pub)

    assert result.success, f"session.mobile.get_adb_url() did not succeed: {result.error_message}"
    assert isinstance(result, AdbUrlResult), "Result should be AdbUrlResult instance"

    adb_url = result.data
    print(f"ADB URL: {adb_url}")
    assert isinstance(adb_url, str)
    assert adb_url.startswith("adb connect"), \
        f"Returned ADB URL should start with 'adb connect', got: {adb_url}"


@pytest.mark.asyncio
async def test_get_adb_url_returns_valid_adb_url(mobile_session):
    """Test session.mobile.get_adb_url() returns properly formatted URL."""
    session: AsyncSession = typing.cast(AsyncSession, mobile_session)

    adbkey_pub = "test_key_123"
    print("Calling session.mobile.get_adb_url()...")
    result = session.mobile.get_adb_url(adbkey_pub)

    assert result.success
    adb_url = result.data
    print(f"ADB URL: {adb_url}")

    # Verify URL format: "adb connect <IP>:<Port>"
    parts = adb_url.split()
    assert len(parts) == 3, f"URL should have format 'adb connect <address>', got: {adb_url}"
    assert parts[0] == "adb"
    assert parts[1] == "connect"

    # Extract and verify IP:Port part
    address_parts = parts[2].split(":")
    assert len(address_parts) == 2, f"Address should be <IP>:<Port>, got: {parts[2]}"


@pytest.mark.asyncio
async def test_get_adb_url_request_id_exists(mobile_session):
    """Test session.mobile.get_adb_url() result has valid request_id."""
    session: AsyncSession = typing.cast(AsyncSession, mobile_session)

    adbkey_pub = "test_key_xyz"
    print("Calling session.mobile.get_adb_url()...")
    result = session.mobile.get_adb_url(adbkey_pub)

    assert result.success
    assert result.request_id is not None, "Request ID should not be None"
    assert len(result.request_id) > 0, "Request ID should not be empty"
    print(f"Request ID: {result.request_id}")


@pytest.mark.asyncio
async def test_get_adb_url_fails_on_non_mobile_image(agent_bay_client):
    """Test session.mobile.get_adb_url() fails when session uses non-mobile image."""
    print("Creating browser session for negative test...")
    params = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay_client.create(params=params)
    browser_session = result.session
    assert browser_session is not None, "Browser session was not created successfully."

    try:
        adbkey_pub = "test_key_456"
        print("Calling session.mobile.get_adb_url() on browser session...")
        tool_result = await browser_session.mobile.get_adb_url(adbkey_pub)
        # Should fail because this is not a mobile environment
        assert not tool_result.success, "get_adb_url() should fail on non-mobile image"
        assert "mobile" in tool_result.error_message.lower(), \
            "Error message should mention mobile environment"
        print(f"Expected error: {tool_result.error_message}")
    finally:
        try:
            await agent_bay_client.delete(browser_session)
        except Exception as e:
            print(f"Warning: Error deleting browser session: {e}")