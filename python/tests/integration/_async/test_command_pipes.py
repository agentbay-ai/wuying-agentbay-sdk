"""Integration tests for command pipes and redirects."""
# ci-stable

import pytest


@pytest.fixture
async def test_session(make_session):
    lc = await make_session()
    return lc._result.session


@pytest.mark.asyncio
async def test_command_pipe(test_session):
    """Test command with pipe."""
    cmd = test_session.command
    result = await cmd.execute_command("echo 'hello world' | grep 'hello'")
    assert result.success
    assert "hello" in result.output
    print("Command with pipe executed successfully")


@pytest.mark.asyncio
async def test_command_redirect(test_session):
    """Test command with redirect."""
    cmd = test_session.command
    fs = test_session.file_system

    # Write to file using redirect
    result = await cmd.execute_command("echo 'test content' > /tmp/redirect_test.txt")
    assert result.success

    # Read file to verify
    read_result = await fs.read_file("/tmp/redirect_test.txt")
    assert read_result.success
    assert "test content" in read_result.content
    print("Command with redirect executed successfully")


@pytest.mark.asyncio
async def test_command_append(test_session):
    """Test command with append redirect."""
    cmd = test_session.command
    fs = test_session.file_system

    # Write initial content
    await cmd.execute_command("echo 'line1' > /tmp/append_test.txt")

    # Append content
    result = await cmd.execute_command("echo 'line2' >> /tmp/append_test.txt")
    assert result.success

    # Read file to verify
    read_result = await fs.read_file("/tmp/append_test.txt")
    assert read_result.success
    assert "line1" in read_result.content
    assert "line2" in read_result.content
    print("Command with append executed successfully")
