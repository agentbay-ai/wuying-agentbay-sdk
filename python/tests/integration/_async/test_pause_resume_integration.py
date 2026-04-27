"""Integration tests for beta pause and beta resume operations (pytest style).
ci-stable
"""

from uuid import uuid4

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay, CreateSessionParams


async def _create_test_session(agent_bay: AsyncAgentBay) -> object:
    session_name = f"test-beta-pause-resume-{uuid4().hex[:8]}"
    params = CreateSessionParams(
        image_id="linux_latest",
        labels={"project": "piaoyun-demo", "environment": "testing", "name": session_name},
    )
    result = await agent_bay.create(params)
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None, "Session object is None"
    return result.session


async def _safe_cleanup_session(agent_bay: AsyncAgentBay, session) -> None:
    if session is None:
        return

    try:
        status_result = await session.get_status()
        if (status_result.success and status_result.status == "FINISH"):
            print(f"Session {session.session_id} is already finished, skipping cleanup.")
            return
        if status_result.success and status_result.status == "PAUSED":
            await session.beta_resume(timeout=180, poll_interval=3)
    except Exception:
        pass

    try:
        await agent_bay.delete(session)
    except Exception:
        pass


@pytest_asyncio.fixture
async def session(agent_bay_client: AsyncAgentBay):
    s = await _create_test_session(agent_bay_client)
    try:
        yield s
    finally:
        await _safe_cleanup_session(agent_bay_client, s)


@pytest.mark.asyncio
async def test_beta_pause_and_resume_session_success(session) -> None:
    status_result = await session.get_status()
    assert status_result.success, f"Failed to get session status: {status_result.error_message}"
    assert status_result.status == "RUNNING", f"Expected RUNNING, got {status_result.status}"

    pause_result = await session.beta_pause(timeout=600, poll_interval=2.0)
    assert pause_result.success, f"beta_pause failed: {pause_result.error_message}"
    assert pause_result.status == "PAUSED", f"Expected PAUSED, got {pause_result.status}"

    resume_result = await session.beta_resume(timeout=600, poll_interval=2.0)
    assert resume_result.success, f"beta_resume failed: {resume_result.error_message}"
    assert resume_result.status == "RUNNING", f"Expected RUNNING, got {resume_result.status}"


@pytest.mark.asyncio
async def test_beta_pause_and_delete_session_success(agent_bay_client: AsyncAgentBay):
    agent_bay = agent_bay_client
    s = await _create_test_session(agent_bay)
    try:
        pause_result = await s.beta_pause(timeout=600, poll_interval=2.0)
        assert pause_result.success, f"beta_pause failed: {pause_result.error_message}"

        resume_result = await s.beta_resume(timeout=600, poll_interval=2.0)
        assert resume_result.success, f"beta_resume failed: {resume_result.error_message}"

        delete_result = await agent_bay.delete(s)
        assert delete_result.success, f"delete failed: {delete_result.error_message}"
    finally:
        await _safe_cleanup_session(agent_bay, s)


@pytest.mark.asyncio
async def test_beta_pause_nonexistent_session(agent_bay_client: AsyncAgentBay):
    agent_bay = agent_bay_client
    fake_session_id = f"session-nonexistent-{uuid4().hex[:8]}"
    get_result = await agent_bay.get(fake_session_id)
    assert not get_result.success, f"Expected get() to fail for nonexistent session {get_result.error_message}"
