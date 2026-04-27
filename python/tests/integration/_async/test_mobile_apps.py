"""Integration tests for Mobile application management functionality."""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def session(make_session):
    """Create a session with mobile_latest image."""
    print("\nCreating session for mobile apps testing...")
    lc = await make_session("mobile_latest")
    session = lc._result.session
    print(f"Session created with ID: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_get_installed_packages(session):
    """Test getting installed packages."""
    # Arrange
    print("\nTest: Getting installed packages...")

    # Act - Use command to list packages
    result = await session.command.execute_command("pm list packages | head -10")

    # Assert
    assert result.success, f"List packages failed: {result.error_message}"
    assert result.output is not None, "Package list should not be None"
    print(f"Packages (first 10):\n{result.output}")


@pytest.mark.asyncio
async def test_start_app(session):
    """Test starting a mobile app."""
    # Arrange
    print("\nTest: Starting Settings app...")

    # Act - Start Settings app
    result = await session.mobile.start_app("monkey -p com.android.settings 1")

    # Assert
    assert result.success, f"Start app failed: {result.error_message}"
    assert result.data is not None, "Process list should not be None"
    print(f"Started {len(result.data)} process(es)")


@pytest.mark.asyncio
async def test_get_adb_url(session):
    """Test getting ADB connection URL."""
    # Arrange
    print("\nTest: Getting ADB URL...")

    # Note: This test requires an ADB public key
    # For now, we'll skip if not available
    pytest.skip("ADB URL test requires ADB public key configuration")
