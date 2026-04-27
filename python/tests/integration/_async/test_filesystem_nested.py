"""Integration tests for nested directory operations.
ci-stable
"""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_nested_directory_creation(test_session):
    """Test creating nested directories."""
    fs = test_session.file_system

    # Create nested structure
    await fs.create_directory("/tmp/level1")
    await fs.create_directory("/tmp/level1/level2")
    await fs.create_directory("/tmp/level1/level2/level3")

    # Verify structure
    info = await fs.get_file_info("/tmp/level1/level2/level3")
    assert info.success
    assert info.file_info["isDirectory"]
    print("Nested directories created successfully")


@pytest.mark.asyncio
async def test_nested_file_operations(test_session):
    """Test file operations in nested directories."""
    fs = test_session.file_system

    # Create nested structure
    await fs.create_directory("/tmp/nest1/nest2")

    # Write file in nested directory
    result = await fs.write_file("/tmp/nest1/nest2/deep_file.txt", "deep content")
    assert result.success

    # Read file
    read_result = await fs.read_file("/tmp/nest1/nest2/deep_file.txt")
    assert read_result.success
    assert read_result.content == "deep content"
    print("Nested file operations successful")


@pytest.mark.asyncio
async def test_list_nested_directory(test_session):
    """Test listing nested directory contents."""
    fs = test_session.file_system

    # Create structure with files
    await fs.create_directory("/tmp/list_nest")
    await fs.write_file("/tmp/list_nest/file1.txt", "content1")
    await fs.create_directory("/tmp/list_nest/subdir")
    await fs.write_file("/tmp/list_nest/subdir/file2.txt", "content2")

    # List parent directory
    result = await fs.list_directory("/tmp/list_nest")
    assert result.success
    assert len(result.entries) == 2

    names = {f.name for f in result.entries}
    assert "file1.txt" in names
    assert "subdir" in names
    print("Nested directory listing successful")
