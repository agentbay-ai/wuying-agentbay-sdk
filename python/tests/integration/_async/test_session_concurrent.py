"""Integration tests for concurrent session operations.
ci-stable
"""

import asyncio

import pytest

from agentbay import AsyncAgentBay


@pytest.mark.asyncio
async def test_concurrent_file_operations(agent_bay_client: AsyncAgentBay):
    """Test concurrent file operations in same session."""
    result = await agent_bay_client.create()
    assert result.success
    session = result.session

    fs = session.file_system

    # Concurrent writes
    tasks = [
        fs.write_file(f"/tmp/concurrent_{i}.txt", f"content_{i}") for i in range(5)
    ]
    results = await asyncio.gather(*tasks)

    assert all(r.success for r in results)
    print("Concurrent file operations successful")

    await session.delete()


@pytest.mark.asyncio
async def test_concurrent_commands(agent_bay_client: AsyncAgentBay):
    """Test concurrent command execution."""
    result = await agent_bay_client.create()
    assert result.success
    session = result.session

    cmd = session.command

    # Concurrent commands
    tasks = [cmd.execute_command(f"echo 'test_{i}'") for i in range(3)]
    results = await asyncio.gather(*tasks)

    assert all(r.success for r in results)
    print("Concurrent commands executed successfully")

    await session.delete()
