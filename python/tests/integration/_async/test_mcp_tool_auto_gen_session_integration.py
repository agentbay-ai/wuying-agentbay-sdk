# ci-stable
import asyncio

import pytest


@pytest.mark.asyncio
async def test_mcp_tool_call_with_active_session(agent_bay_client):
    """Test MCP tool call succeeds when session is active"""
    # Create a session
    print("Creating session for MCP tool call test...")
    result = await agent_bay_client.create()
    assert result.success
    assert result.session is not None
    session = result.session
    print(f"Session created successfully, ID: {session.session_id}")

    # Call MCP tool with active session (auto_gen_session=False)
    print("Calling MCP tool with active session...")
    tool_result = await session.call_mcp_tool(
        tool_name="shell",
        args={"command": "echo 'test'", "timeout_ms": 5000},
        auto_gen_session=False,
    )
    assert tool_result.success, f"MCP tool call failed: {tool_result.error_message}"
    print(f"MCP tool call succeeded (RequestID: {tool_result.request_id})")

    # Clean up
    print("Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success
    print("Session deleted successfully")


@pytest.mark.asyncio
async def test_mcp_tool_call_with_deleted_session_auto_gen_false(agent_bay_client):
    """Test MCP tool call fails when session is deleted and auto_gen_session=False"""
    # Create a session
    print("Creating session for deletion test...")
    result = await agent_bay_client.create()
    assert result.success
    assert result.session is not None
    session = result.session
    session_id = session.session_id
    print(f"Session created successfully, ID: {session_id}")

    # Delete the session
    print("Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success
    print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

    # Wait for deletion to complete
    await asyncio.sleep(2)

    # Verify session is deleted
    list_result = await agent_bay_client.list()
    assert list_result.success
    assert session_id not in list_result.session_ids, \
        f"Session ID {session_id} still exists after deletion"

    # Try to call MCP tool with deleted session (auto_gen_session=False)
    print("Calling MCP tool with deleted session (auto_gen_session=False)...")
    tool_result = await session.call_mcp_tool(
        tool_name="shell",
        args={"command": "echo 'test'", "timeout_ms": 5000},
        auto_gen_session=False,
    )
    # Expect failure
    assert not tool_result.success, "MCP tool call should fail with deleted session"
    assert tool_result.error_message is not None
    assert len(tool_result.error_message) > 0
    print(f"MCP tool call failed as expected: {tool_result.error_message}")