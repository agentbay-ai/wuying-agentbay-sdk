"""Integration tests for command timeout."""
# ci-stable

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def test_session(make_session):
    lc = await make_session(params=CreateSessionParams(image_id="code_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_command_with_timeout(test_session):
    """Test command execution with timeout."""
    cmd = test_session.command
    result = await cmd.execute_command(
        "echo 'test' && sleep 1 && echo 'done'", timeout_ms=5000
    )
    assert result.success
    assert "test" in result.output
    assert "done" in result.output
    print("Command with timeout executed successfully")


@pytest.mark.asyncio
async def test_command_quick_execution(test_session):
    """Test quick command execution."""
    cmd = test_session.command
    result = await cmd.execute_command("echo 'quick'", timeout_ms=1000)
    assert result.success
    assert "quick" in result.output
    print("Quick command executed successfully")
