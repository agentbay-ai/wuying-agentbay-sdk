"""Integration tests for large file operations.
ci-stable
"""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_write_large_file(test_session):
    """Test writing a large file."""
    fs = test_session.file_system

    # Create large content (1MB)
    large_content = "x" * (1024 * 1024)

    result = await fs.write_file("/tmp/large_file.txt", large_content)
    assert result.success

    # Verify file info
    info = await fs.get_file_info("/tmp/large_file.txt")
    assert info.success
    size = int(info.file_info["size"])
    print(f"Large file created, size: {size} bytes")


@pytest.mark.asyncio
async def test_read_large_file(test_session):
    """Test reading a large file."""
    fs = test_session.file_system

    # Create large content (500KB)
    content = "y" * (512 * 1024)
    await fs.write_file("/tmp/read_large.txt", content)

    # Read file
    result = await fs.read_file("/tmp/read_large.txt")
    assert result.success
    assert len(result.content) == len(content)
    print(f"Large file read successfully, size: {len(result.content)} bytes")
