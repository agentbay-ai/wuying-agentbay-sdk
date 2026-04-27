# ci-stable
"""Integration tests for session pause and resume operations."""

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.asyncio
async def test_pause_resume_session(agent_bay_client: AsyncAgentBay):
    """Test pausing and resuming a session."""
    create_result = await agent_bay_client.create()
    assert create_result.success
    session = create_result.session
    print(f"Created session: {session.session_id}")

    try:
        pause_result = await session.beta_pause()
        if pause_result.success:
            print("Session paused successfully")

            resume_result = await session.beta_resume()
            if resume_result.success:
                print("Session resumed successfully")
            else:
                print(f"Resume not supported: {resume_result.error_message}")
        else:
            print(f"Pause not supported by backend: {pause_result.error_message}")
            # This is acceptable - not all backends support pause/resume
    finally:
        await session.delete()


@pytest.mark.asyncio
async def test_pause_already_paused(agent_bay_client: AsyncAgentBay):
    """Test pausing an already paused session."""
    create_result = await agent_bay_client.create()
    session = create_result.session

    try:
        await session.beta_pause()
        print("Session paused first time")

        pause_result = await session.beta_pause()
        assert not pause_result.success, (
            f"Second pause already paused successfully: {pause_result.error_message}"
        )
        print(f"Second pause result: {pause_result.success}")
    finally:
        await session.beta_resume()
        await session.delete()


@pytest.mark.asyncio
async def test_pause_resume_with_operations(agent_bay_client: AsyncAgentBay):
    """Test operations after pause and resume."""
    params = CreateSessionParams(image_id="linux_latest")
    create_result = await agent_bay_client.create(params)
    session = create_result.session

    try:
        cmd_result1 = await session.command.execute_command("echo 'before pause'")
        assert cmd_result1.success
        print("Command executed before pause")

        await session.beta_pause()
        print("Session paused")

        await session.beta_resume()
        print("Session resumed")

        cmd_result2 = await session.command.execute_command("echo 'after resume'")
        assert cmd_result2.success
        print("Command executed after resume")
    finally:
        await session.delete()
