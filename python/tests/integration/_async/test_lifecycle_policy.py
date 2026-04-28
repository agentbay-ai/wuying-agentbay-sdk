"""Integration tests for CreateSessionParams.lifecycle_policy (async).

End-to-end against the real API. Requires AGENTBAY_API_KEY.
"""

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams, LifecyclePolicy


@pytest.mark.asyncio
async def test_create_session_with_custom_lifecycle_policy(agent_bay_client: AsyncAgentBay):
    """Create a session with custom idle/max lifecycle (minutes)."""
    params = CreateSessionParams(
        image_id="linux_latest",
        labels={"test": "lifecycle-policy", "sdk": "python-async", "case": "custom"},
        lifecycle_policy=LifecyclePolicy(idle_release_timeout=10, max_runtime=60),
    )
    result = await agent_bay_client.create(params)
    assert result.success, f"create failed: {result.error_message}"
    session = result.session
    assert session is not None
    assert session.session_id
    try:
        cmd_result = await session.command.execute_command("echo hello")
        assert cmd_result.success
        assert cmd_result.output.strip() == "hello"
    finally:
        del_result = await agent_bay_client.delete(session)
        assert del_result.success, del_result.error_message


@pytest.mark.asyncio
async def test_create_session_with_manual_release(agent_bay_client: AsyncAgentBay):
    """Create a session with manual_release; run command then delete."""
    params = CreateSessionParams(
        image_id="linux_latest",
        labels={"test": "lifecycle-policy", "sdk": "python-async", "case": "manual"},
        lifecycle_policy=LifecyclePolicy(manual_release=True),
    )
    result = await agent_bay_client.create(params)
    assert result.success, f"create failed: {result.error_message}"
    session = result.session
    assert session is not None
    assert session.session_id
    try:
        cmd_result = await session.command.execute_command("echo manual")
        assert cmd_result.success
        assert cmd_result.output.strip() == "manual"
    finally:
        del_result = await agent_bay_client.delete(session)
        assert del_result.success, del_result.error_message


@pytest.mark.asyncio
async def test_create_session_with_default_lifecycle_policy(agent_bay_client: AsyncAgentBay):
    """Create a session using default LifecyclePolicy (idle=5, max=30 minutes)."""
    params = CreateSessionParams(
        image_id="linux_latest",
        labels={"test": "lifecycle-policy", "sdk": "python-async", "case": "default"},
        lifecycle_policy=LifecyclePolicy(),
    )
    result = await agent_bay_client.create(params)
    assert result.success, f"create failed: {result.error_message}"
    session = result.session
    assert session is not None
    assert session.session_id
    del_result = await agent_bay_client.delete(session)
    assert del_result.success, del_result.error_message
