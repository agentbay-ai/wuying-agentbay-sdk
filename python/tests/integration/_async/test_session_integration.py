"""Integration tests for Session functionality.
ci-stable
"""

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.mark.asyncio
async def test_create_list_delete(agent_bay_client: AsyncAgentBay):
    """Test create, list, and delete methods."""
    print("Creating a new session...")
    result = await agent_bay_client.create()

    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None, "Session object is None"

    session = result.session
    print(f"Session created with ID: {session.session_id}")

    assert session.session_id is not None
    assert session.session_id != ""

    print("Deleting the session...")
    await agent_bay_client.delete(session)


@pytest.mark.asyncio
async def test_session_properties(make_session):
    """Test session properties and methods."""
    lc = await make_session()
    session = lc._result.session

    assert session.session_id is not None

    api_key = session.agent_bay.api_key
    assert api_key is not None

    client = session.agent_bay.client
    assert client is not None

    session_id = session.session_id
    assert session_id is not None



@pytest.mark.asyncio
async def test_command(make_session):
    """Test command execution."""
    lc = await make_session()
    session = lc._result.session

    if session.command:
        print("Executing command...")
        try:
            response = await session.command.execute_command("ls")
            print(f"Command execution result: {response}")
            assert response is not None
            assert response.success, f"Command failed: {response.error_message}"
            assert (
                "tool not found" not in response.output.lower()
            ), "Command.ExecuteCommand returned 'tool not found'"
        except Exception as e:
            print(f"Note: Command execution failed: {e}")
    else:
        print("Note: Command interface is nil, skipping command test")


@pytest.mark.asyncio
async def test_filesystem(make_session):
    """Test filesystem operations."""
    lc = await make_session()
    session = lc._result.session

    if session.file_system:
        print("Reading file...")
        try:
            result = await session.file_system.read_file("/etc/hosts")
            print(f"ReadFile result: content='{result}'")
            assert result is not None
            assert result.success, f"Read file failed: {result.error_message}"
            assert (
                "tool not found" not in result.content.lower()
            ), "FileSystem.ReadFile returned 'tool not found'"
            print("File read successful")
        except Exception as e:
            print(f"Note: File operation failed: {e}")
    else:
        print("Note: FileSystem interface is nil, skipping file test")
