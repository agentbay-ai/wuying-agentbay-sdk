"""Integration tests for Session delete operations.
ci-stable
"""

import pytest


@pytest.mark.asyncio
async def test_delete_session_basic(agent_bay_client):
    """Test basic session deletion."""
    result = await agent_bay_client.create()
    assert result.success is True
    session = result.session

    delete_result = await session.delete()
    assert delete_result.success is True
    print(f"Session deleted: {session.session_id}")


@pytest.mark.asyncio
async def test_delete_session_with_sync_context(agent_bay_client):
    """Test session deletion with context sync."""
    result = await agent_bay_client.create()
    assert result.success is True
    session = result.session

    delete_result = await session.delete(sync_context=True)
    assert delete_result.success is True
    print(f"Session deleted with context sync: {session.session_id}")


@pytest.mark.asyncio
async def test_delete_multiple_sessions(agent_bay_client):
    """Test deleting multiple sessions."""
    sessions = []
    for i in range(3):
        result = await agent_bay_client.create()
        assert result.success is True
        sessions.append(result.session)

    for session in sessions:
        delete_result = await session.delete()
        assert delete_result.success is True
        print(f"Session {session.session_id} deleted")

    print(f"Deleted {len(sessions)} sessions")


@pytest.mark.asyncio
async def test_delete_using_agent_bay(agent_bay_client):
    """Test deleting session using AgentBay.delete()."""
    result = await agent_bay_client.create()
    assert result.success is True
    session = result.session

    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success is True
    print(f"Session deleted via AgentBay: {session.session_id}")
