# ci-stable

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def agent_session(make_session):
    """Create a session for Command testing."""
    lc = await make_session(params=CreateSessionParams(image_id="code_latest"))
    return lc._result.session


@pytest.fixture
def command(agent_session):
    """Fixture to get the command object from the session."""
    return agent_session.command


@pytest.mark.asyncio
async def test_execute_command_success(command):
    """Test executing a shell command successfully."""
    cmd = "echo 'Hello, AgentBay!'"
    result = await command.execute_command(cmd)
    print(f"Command execution result: {result.output}")
    assert result.success
    assert result.output.strip() == "Hello, AgentBay!"
    assert result.request_id != ""
    assert result.error_message == ""


@pytest.mark.asyncio
async def test_execute_command_with_timeout(command):
    """Test executing a shell command with a timeout."""
    cmd = "sleep 5"
    timeout_ms = 1000  # 1 second timeout
    result = await command.execute_command(cmd, timeout_ms)
    print(f"Command execution result with timeout: {result}")
    assert not result.success
    assert result.request_id != ""
    assert result.error_message != ""
    assert result.output == ""


@pytest.mark.asyncio
async def test_command_error_handling(command):
    """Test command error handling - should handle command errors and edge cases."""
    # Test invalid command
    invalid_result = await command.execute_command("invalid_command_12345")
    assert not invalid_result.success
    assert invalid_result.error_message is not None

    # Test command with permission issues (trying to write to protected directory)
    permission_result = await command.execute_command(
        'echo "test" > /root/protected.txt'
    )
    # This might succeed or fail depending on the environment, but should not crash
    assert isinstance(permission_result.success, bool)

    # Test long-running command with timeout considerations
    time_command = 'echo "completed"'
    time_result = await command.execute_command(time_command)
    print(f"Command output: {time_result}")
    assert time_result.success
    assert "completed" in time_result.output
