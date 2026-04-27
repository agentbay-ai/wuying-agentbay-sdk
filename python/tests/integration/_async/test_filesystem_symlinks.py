"""Integration tests for filesystem symlinks.
ci-stable
"""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_create_symlink(test_session):
    """Test creating a symlink."""
    fs = test_session.file_system
    cmd = test_session.command

    # Create original file
    await fs.write_file("/tmp/original.txt", "original content")

    # Create symlink
    result = await cmd.execute_command("ln -s /tmp/original.txt /tmp/link.txt")
    assert result.success

    # Read through symlink
    read_result = await fs.read_file("/tmp/link.txt")
    assert read_result.success
    assert read_result.content == "original content"
    print("Symlink creation successful")


@pytest.mark.asyncio
async def test_symlink_to_directory(test_session):
    """Test symlink to directory."""
    fs = test_session.file_system
    cmd = test_session.command

    # Create directory with file
    await fs.create_directory("/tmp/orig_dir")
    await fs.write_file("/tmp/orig_dir/file.txt", "dir content")

    # Create symlink to directory
    result = await cmd.execute_command("ln -s /tmp/orig_dir /tmp/link_dir")
    assert result.success

    # Read file through symlink
    read_result = await fs.read_file("/tmp/link_dir/file.txt")
    assert read_result.success
    assert read_result.content == "dir content"
    print("Directory symlink successful")
