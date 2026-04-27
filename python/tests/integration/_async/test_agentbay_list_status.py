"""Integration tests for Session pause and resume operations."""
# ci-stable

import asyncio
import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import SessionPauseResult, SessionResumeResult
from agentbay import Config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def agent_bay_client():
    """Constructs AsyncAgentBay without creating a session."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable is not set")

    endpoint = os.environ.get("AGENTBAY_ENDPOINT")
    if endpoint:
        config = Config(endpoint=endpoint, timeout_ms=60000)
        client = AsyncAgentBay(api_key=api_key, cfg=config)
        print(f"Using endpoint: {endpoint}")
    else:
        client = AsyncAgentBay(api_key=api_key)
        print("Using default endpoint")

    return client


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


async def _create_test_session(agent_bay: AsyncAgentBay):
    """Create a test session with standard labels."""
    params = CreateSessionParams(
        labels={"project": "piaoyun-demo", "environment": "testing"},
    )
    result = await agent_bay.create(params)
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None
    session = result.session
    print(f"  ✓ Session created: {session.session_id}")
    return session


async def _cleanup_session(agent_bay: AsyncAgentBay, session):
    """Resume if paused, then delete the session."""
    try:
        status_result = await session.get_status()
        print(f"  Session status before cleanup: {status_result.status}")
        if status_result.status in ["PAUSED"]:
            await session.beta_resume()
            print(f"  ✓ Resumed session: {session.session_id}")
        if status_result.status not in ["DELETING", "DELETED", "RESUMING", "PAUSING"]:
            delete_result = await agent_bay.delete(session)
            if delete_result.success:
                print(f"  ✓ Deleted session: {session.session_id}")
            else:
                print(f"  ✗ Failed to delete session: {session.session_id}")
    except Exception as e:
        print(f"  ⚠ Cleanup error for session {session.session_id}: {e}")


async def _verify_session_status_and_list(agent_bay: AsyncAgentBay, session, expected_statuses, operation_name="operation"):
    """
    Verify session status via get_status and _get_session, then confirm the
    session appears in the list API with the expected status.

    Args:
        agent_bay: AsyncAgentBay client instance.
        session: The session to verify.
        expected_statuses: List of acceptable status strings.
        operation_name: Label used in log output.

    Returns:
        The current status string (or None when status is FINISH).
    """
    print(f"\nVerifying session status after {operation_name}...")

    # 1. Check current status via get_status
    status_result = await session.get_status()
    assert status_result.success, f"Failed to get session status: {status_result.error_message}"

    initial_status = status_result.status if status_result.status else "UNKNOWN"
    print(f"  ✓ Session status from get_status: {initial_status}")
    assert initial_status in expected_statuses, (
        f"Unexpected status {initial_status}, expected one of {expected_statuses}"
    )

    if initial_status == "FINISH":
        return None

    # 2. Cross-check via _get_session
    session_info = await agent_bay._get_session(session.session_id)
    assert session_info.success, f"Failed to get session info: {session_info.error_message}"

    current_status = session_info.data.status if session_info.data else "UNKNOWN"
    assert current_status == initial_status, (
        f"Session status mismatch: expected {initial_status}, got {current_status}"
    )
    print(f"  ✓ Session status from _get_session: {current_status}")

    # 3. Verify the session appears in the list with this status
    list_result = await agent_bay.list(status=current_status)
    assert list_result.success, f"Failed to list sessions: {list_result.error_message}"

    session_found = False
    for session_data in list_result.session_ids:
        if isinstance(session_data, dict):
            if session_data.get("sessionId") == session.session_id:
                session_found = True
                assert "sessionStatus" in session_data, "sessionStatus field missing in list result"
                assert "sessionId" in session_data, "sessionId field missing in list result"
                assert session_data["sessionStatus"] == current_status
                break
        else:
            print("  ✗ Invalid session data in list result")
            break

    assert session_found, f"Session {session.session_id} not found in list with status {current_status}"
    print(f"  ✓ Session found in list with status {current_status}")
    print(f"  ✓ Session status verification completed for {operation_name}")

    return current_status


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pause_and_resume_session_success(agent_bay_client: AsyncAgentBay):
    """Test successful pause and resume operations on a session."""
    print("\n" + "=" * 60)
    print("TEST: Pause and Resume Session Success")
    print("=" * 60)

    session = await _create_test_session(agent_bay_client)
    try:
        # Verify session is initially in RUNNING state
        status_result = await session.get_status()
        assert status_result.success, f"Failed to get session status: {status_result.error_message}"
        initial_status = status_result.status if status_result.status else "UNKNOWN"
        print(f"  ✓ Session status from get_status: {initial_status}")
        assert initial_status in ["RUNNING"], (
            f"Unexpected status {initial_status}, expected RUNNING"
        )

        # Pause the session
        print("\nStep 2: Pausing session...")
        pause_result = await agent_bay_client.beta_pause(session)
        assert isinstance(pause_result, SessionPauseResult)
        assert pause_result.success, f"Pause failed: {pause_result.error_message}"
        print(f"  ✓ Session pause initiated successfully")
        print(f"    Request ID: {pause_result.request_id}")

        # Wait a bit for pause to complete
        print("\nStep 3: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Verify session status after pause
        await _verify_session_status_and_list(agent_bay_client, session, ["PAUSED", "PAUSING"], "pause")
    finally:
        await _cleanup_session(agent_bay_client, session)


@pytest.mark.asyncio
async def test_resume_async_session_success(agent_bay_client: AsyncAgentBay):
    """Test successful async resume operation on a session."""
    print("\n" + "=" * 60)
    print("TEST: Async Resume Session Success")
    print("=" * 60)

    session = await _create_test_session(agent_bay_client)
    try:
        # Pause the session first
        print("\nStep 1: Pausing session...")
        pause_result = await agent_bay_client.beta_pause(session)
        assert pause_result.success, f"Pause failed: {pause_result.error_message}"
        print(f"  ✓ Session pause initiated successfully")

        # Wait for pause to complete
        print("\nStep 2: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Verify paused status
        status_result = await session.get_status()
        assert status_result.success, f"Failed to get session status: {status_result.error_message}"
        initial_status = status_result.status if status_result.status else "UNKNOWN"
        print(f"  ✓ Session status from get_status: {initial_status}")
        assert initial_status in ["PAUSED", "PAUSING"], (
            f"Unexpected status {initial_status}, expected one of PAUSED or PAUSING"
        )
        print(f"  ✓ Session status checked")

        # Resume the session (asynchronous)
        print("\nStep 3: Resuming session asynchronously...")
        resume_result = await agent_bay_client.beta_resume(session)
        assert isinstance(resume_result, SessionResumeResult)
        assert resume_result.success, f"Async resume failed: {resume_result.error_message}"
        print(f"  ✓ Session resume initiated successfully")
        print(f"    Request ID: {resume_result.request_id}")

        # Wait a bit for resume to complete
        print("\nStep 4: Waiting for session to resume...")
        await asyncio.sleep(2)

        # Verify session status after resume
        await _verify_session_status_and_list(agent_bay_client, session, ["RUNNING", "RESUMING"], "async resume")
    finally:
        await _cleanup_session(agent_bay_client, session)


@pytest.mark.asyncio
async def test_pause_and_delete_session_success(agent_bay_client: AsyncAgentBay):
    """Test successful pause and delete operations on a session."""
    print("\n" + "=" * 60)
    print("TEST: Pause and Delete Session Success")
    print("=" * 60)

    print("\nStep 1: Creating test session...")
    session = await _create_test_session(agent_bay_client)

    # Pause the session
    print("\nStep 2: Pausing session...")
    pause_result = await agent_bay_client.beta_pause(session)
    assert isinstance(pause_result, SessionPauseResult)
    assert pause_result.success, f"Pause failed: {pause_result.error_message}"
    print(f"  ✓ Session pause initiated successfully")
    print(f"    Request ID: {pause_result.request_id}")

    # Wait a bit for pause to complete
    print("\nStep 3: Waiting for session to pause...")
    await asyncio.sleep(2)

    print(f"  ✓ Checking session status before resuming")
    await session.beta_resume()
    print(f"  ✓ Session resumed")

    # Delete the session
    print("\nStep 4: Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    if delete_result.success:
        print("  ✓ Session deleted successfully")

    # Verify session status after delete
    await _verify_session_status_and_list(agent_bay_client, session, ["DELETING", "DELETED", "FINISH"], "delete")
