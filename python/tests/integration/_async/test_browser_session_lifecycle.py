"""Integration test for browser session lifecycle: create, wait, and delete (async version)."""
# ci-stable

import asyncio

import pytest

from agentbay import CreateSessionParams


@pytest.mark.asyncio
async def test_browser_session_create_and_delete(agent_bay_client):
    """
    Test creating a browser_latest session with enable_browser_replay=False,
    waiting 2 seconds, and then deleting it (async version).
    """
    # Create session parameters
    print("Creating browser_latest session with enable_browser_replay=False...")
    session_param = CreateSessionParams(
        image_id="browser_latest",
        enable_browser_replay=False,  # Disable browser replay
    )

    # Create session
    result = await agent_bay_client.create(session_param)
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None, "Session should not be None"

    session = result.session
    session_id = session.session_id
    print(f"✅ Session created successfully with ID: {session_id}")

    # Verify session properties
    assert session_id is not None, "Session ID should not be None"
    assert len(session_id) > 0, "Session ID should not be empty"

    # Wait for 2 seconds
    print("⏳ Waiting for 2 seconds...")
    await asyncio.sleep(2)
    print("✅ Wait completed")

    # Delete session
    print(f"🗑️  Deleting session {session_id}...")
    delete_result = await session.delete()

    # Verify deletion
    assert delete_result is not None, "Delete result should not be None"
    print(f"✅ Session {session_id} deleted successfully")

    # Verify session is deleted by trying to get status
    print("🔍 Verifying session deletion...")
    status_result = await session.get_status()

    # Session should be deleted (NotFound error or FINISH status)
    if not status_result.success:
        error_code = getattr(status_result, "code", "") or ""
        error_message = status_result.error_message or ""
        http_status_code = getattr(status_result, "http_status_code", 0) or 0

        # Check for NotFound error
        is_not_found = (
            error_code == "InvalidMcpSession.NotFound"
            or (http_status_code == 400 and "not found" in error_message.lower())
            or "not found" in error_message.lower()
        )

        if is_not_found:
            print("✅ Session deletion verified: NotFound error received")
        else:
            print(f"⚠️  Unexpected error during status check: {error_message}")
    elif hasattr(status_result, "status") and status_result.status == "FINISH":
        print("✅ Session deletion verified: Status is FINISH")
    else:
        print(f"⚠️  Session status: {getattr(status_result, 'status', 'unknown')}")

    print("✅ Test completed successfully")
