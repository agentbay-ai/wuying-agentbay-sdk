"""Integration tests for different session images.
ci-stable
"""

import pytest

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@pytest.mark.asyncio
async def test_ubuntu_session(agent_bay_client: AsyncAgentBay):
    """Test creating Ubuntu session."""
    params = CreateSessionParams(image_id="linux_latest")
    result = await agent_bay_client.create(params)
    assert result.success

    session = result.session
    print(f"Ubuntu session created: {session.session_id}")

    # Test basic command
    cmd_result = await session.command.execute_command("uname -a")
    assert cmd_result.success
    print(f"OS info: {cmd_result.output[:50]}...")

    await session.delete()


@pytest.mark.asyncio
async def test_browser_session(agent_bay_client: AsyncAgentBay):
    """Test creating browser session."""
    params = CreateSessionParams(image_id="browser_latest")
    result = await agent_bay_client.create(params)
    assert result.success

    session = result.session
    print(f"Browser session created: {session.session_id}")

    await session.delete()
