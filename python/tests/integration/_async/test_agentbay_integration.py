"""Integration tests for AgentBay API — uses AgentBay client directly.

Tests in this file call AgentBay APIs directly (init, get, list, parameter
validation, etc.) without relying on the make_session factory fixture.
Sessions are created via agent_bay_client.create() when needed and cleaned
up explicitly within each test.
ci-stable
"""

import os

import pytest

from agentbay import (
    AsyncAgentBay,
    AsyncSession,
    BWList,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)


@pytest.fixture(scope="module")
def agent_bay_client():
    """Lightweight fixture: constructs AsyncAgentBay without creating a session."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable is not set")
    return AsyncAgentBay(api_key=api_key)


# ---------------------------------------------------------------------------
# AsyncAgentBay – initialization (no network)
# ---------------------------------------------------------------------------


def test_init_with_api_key():
    """Test initialization with API key."""
    api_key = os.environ.get("AGENTBAY_API_KEY", "akm-test")
    ab = AsyncAgentBay(api_key=api_key)
    assert ab.api_key == api_key
    assert ab.client is not None


def test_init_without_api_key_uses_env():
    """Test initialization without explicit API key falls back to env var."""
    original_key = os.environ.get("AGENTBAY_API_KEY")
    os.environ["AGENTBAY_API_KEY"] = "env_api_key"
    try:
        ab = AsyncAgentBay()
        assert ab.api_key == "env_api_key"
    finally:
        if original_key is not None:
            os.environ["AGENTBAY_API_KEY"] = original_key
        else:
            del os.environ["AGENTBAY_API_KEY"]


def test_init_without_api_key_raises_error():
    """Test initialization without API key raises ValueError."""
    original_key = os.environ.get("AGENTBAY_API_KEY")
    try:
        if "AGENTBAY_API_KEY" in os.environ:
            del os.environ["AGENTBAY_API_KEY"]
        with pytest.raises(ValueError):
            AsyncAgentBay()
    finally:
        if original_key is not None:
            os.environ["AGENTBAY_API_KEY"] = original_key


# ---------------------------------------------------------------------------
# Get API – parameter validation (no session creation)
# ---------------------------------------------------------------------------


async def test_get_empty_session_id(agent_bay_client: AsyncAgentBay):
    """Test Get API with empty session ID - no real session needed."""
    print("Testing Get API with empty session ID...")
    result = await agent_bay_client.get("")
    assert not result.success, "Expected get() to fail for empty session ID"
    assert "session_id is required" in result.error_message
    print(f"Correctly received error for empty session ID: {result.error_message}")


async def test_get_whitespace_session_id(agent_bay_client: AsyncAgentBay):
    """Test Get API with whitespace-only session ID - no real session needed."""
    print("Testing Get API with whitespace session ID...")
    result = await agent_bay_client.get("   ")
    assert not result.success, "Expected get() to fail for whitespace session ID"
    assert "session_id is required" in result.error_message
    print(f"Correctly received error for whitespace session ID: {result.error_message}")


async def test_get_non_existent_session(agent_bay_client: AsyncAgentBay):
    """Test Get API with a non-existent session ID."""
    print("Testing Get API with non-existent session ID...")
    result = await agent_bay_client.get("session-nonexistent-12345")
    assert not result.success, "Expected get() to fail for non-existent session"
    assert "Failed to get session" in result.error_message
    print(f"Correctly received error for non-existent session: {result.error_message}")


async def test_get_api(agent_bay_client: AsyncAgentBay):
    """Test Get API with a real session created via agent_bay_client.create()."""
    print("Creating session via agent_bay_client.create()...")
    create_result = await agent_bay_client.create()
    assert create_result.success, f"Failed to create session: {create_result.error_message}"
    created_session = create_result.session
    session_id = created_session.session_id
    print(f"Session created with ID: {session_id}")

    try:
        print("Testing Get API...")
        result = await agent_bay_client.get(session_id)

        assert result is not None, "Get returned None result"
        assert result.success, f"Failed to get session: {result.error_message}"
        session = result.session
        assert session is not None, "Get returned None session"
        assert isinstance(
            session, AsyncSession
        ), f"Expected AsyncSession instance, got {type(session)}"
        assert (
            session.session_id == session_id
        ), f"Expected SessionID {session_id}, got {session.session_id}"
        assert session.agent_bay is not None, "Session agent_bay reference is None"
        print(f"Successfully retrieved session with ID: {session.session_id}")
    finally:
        delete_result = await created_session.delete()
        assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
        print(f"Session {session_id} deleted successfully")


# ---------------------------------------------------------------------------
# RecyclePolicy – parameter validation (no network)
# ---------------------------------------------------------------------------


def test_context_sync_with_invalid_recycle_policy_path():
    """Test that RecyclePolicy raises error for invalid path with wildcard."""
    print("Testing ContextSync creation with invalid recyclePolicy path...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/invalid/path/*"],
        )
    assert "Wildcard patterns are not supported in recycle policy paths" in str(exc_info.value)
    assert "/invalid/path/*" in str(exc_info.value)
    print("RecyclePolicy correctly raised error for invalid path")

    with pytest.raises(ValueError):
        RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=["/valid/path", "/invalid/path?", "/another/invalid/*"],
        )
    print("RecyclePolicy correctly raised error for multiple invalid paths")


def test_recycle_policy_invalid_lifecycle():
    """Test invalid Lifecycle values."""
    print("Testing invalid Lifecycle values...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle="invalid_lifecycle", paths=[""])
    error_message = str(exc_info.value)
    assert "Invalid lifecycle value" in error_message
    assert "invalid_lifecycle" in error_message
    assert "Valid values are:" in error_message
    print(f"Invalid lifecycle correctly failed: {error_message}")


def test_recycle_policy_combined_invalid():
    """Test combination of invalid Lifecycle and invalid path."""
    print("Testing combination of invalid Lifecycle and invalid paths...")

    with pytest.raises(ValueError) as exc_info:
        RecyclePolicy(lifecycle="invalid_lifecycle", paths=["/invalid/path/*"])
    # Lifecycle validation runs first
    assert "Invalid lifecycle value" in str(exc_info.value)
    print("Policy with both invalid lifecycle and path correctly failed")
