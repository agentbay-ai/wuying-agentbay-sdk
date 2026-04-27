"""Integration tests for filesystem permissions.
ci-stable
"""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_file_permissions(test_session):
    """Test file permissions."""
    fs = test_session.file_system
    cmd = test_session.command

    # Create file
    await fs.write_file("/tmp/perm_test.txt", "test content")

    # Check permissions
    result = await cmd.execute_command("ls -l /tmp/perm_test.txt")
    assert result.success
    print(f"File permissions: {result.output}")


@pytest.mark.asyncio
async def test_directory_permissions(test_session):
    """Test directory permissions."""
    fs = test_session.file_system
    cmd = test_session.command

    # Create directory
    dir_result = await fs.create_directory("/tmp/perm_dir")
    assert dir_result.success

    # Check permissions
    result = await cmd.execute_command("ls -ld /tmp/perm_dir")
    assert result.success
    print(f"Directory permissions: {result.output}")


@pytest.mark.asyncio
async def test_executable_file(test_session):
    """Test executable file creation."""
    fs = test_session.file_system
    cmd = test_session.command

    # Create script
    script_content = "#!/bin/bash\necho 'executable test'"
    await fs.write_file("/tmp/test_script.sh", script_content)

    # Make executable
    await cmd.execute_command("chmod +x /tmp/test_script.sh")

    # Execute script
    result = await cmd.execute_command("/tmp/test_script.sh")
    assert result.success
    assert "executable test" in result.output
    print("Executable file test successful")
