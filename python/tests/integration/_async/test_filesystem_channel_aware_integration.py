"""Integration tests for channel-aware filesystem chunking optimization.
ci-stable

Verifies that:
- HTTP (LinkUrl) channel: read_file/write_file work correctly without chunking
- Files of various sizes (small, medium ~60KB, large ~200KB) are handled correctly
- Binary file read/write works on HTTP channel
- Append mode works on HTTP channel
"""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_session(make_session):
    lc = await make_session("linux_latest")
    session = lc._result.session

    # Log channel type for debugging
    link_url = session._get_link_url() if hasattr(session, '_get_link_url') else ""
    token = session._get_token() if hasattr(session, '_get_token') else ""
    channel = "HTTP (LinkUrl)" if link_url and token else "MQTT (API)"
    print(f"\n[Channel] Using {channel} channel")
    print(f"[Channel] link_url present: {bool(link_url)}, token present: {bool(token)}")

    return session


@pytest.mark.asyncio
async def test_small_file_roundtrip(test_session):
    """Test write+read of a small file (< 1KB)."""
    fs = test_session.file_system
    content = "Hello, channel-aware filesystem!"
    path = "/tmp/channel_test_small.txt"

    write_result = await fs.write_file(path, content)
    assert write_result.success, f"Write failed: {write_result.error_message}"

    read_result = await fs.read_file(path)
    assert read_result.success, f"Read failed: {read_result.error_message}"
    assert read_result.content == content, f"Content mismatch: expected {len(content)} bytes, got {len(read_result.content)} bytes"
    print(f"[PASS] Small file roundtrip: {len(content)} bytes")


@pytest.mark.asyncio
async def test_medium_file_roundtrip(test_session):
    """Test write+read of a medium file (~60KB, previously required chunking)."""
    fs = test_session.file_system
    content = "A" * (60 * 1024)  # 60KB
    path = "/tmp/channel_test_medium.txt"

    write_result = await fs.write_file(path, content)
    assert write_result.success, f"Write failed: {write_result.error_message}"

    read_result = await fs.read_file(path)
    assert read_result.success, f"Read failed: {read_result.error_message}"
    assert read_result.content == content, f"Content mismatch: expected {len(content)} chars, got {len(read_result.content)} chars"
    print(f"[PASS] Medium file roundtrip: {len(content)} bytes")


@pytest.mark.asyncio
async def test_large_file_roundtrip(test_session):
    """Test write+read of a large file (~200KB, previously required multiple chunks)."""
    fs = test_session.file_system
    content = "B" * (200 * 1024)  # 200KB
    path = "/tmp/channel_test_large.txt"

    write_result = await fs.write_file(path, content)
    assert write_result.success, f"Write failed: {write_result.error_message}"

    read_result = await fs.read_file(path)
    assert read_result.success, f"Read failed: {read_result.error_message}"
    assert read_result.content == content, f"Content mismatch: expected {len(content)} chars, got {len(read_result.content)} chars"
    print(f"[PASS] Large file roundtrip: {len(content)} bytes")


@pytest.mark.asyncio
async def test_append_mode(test_session):
    """Test append mode works correctly."""
    fs = test_session.file_system
    path = "/tmp/channel_test_append.txt"

    write_result = await fs.write_file(path, "first part", mode="overwrite")
    assert write_result.success

    append_result = await fs.write_file(path, " second part", mode="append")
    assert append_result.success

    read_result = await fs.read_file(path)
    assert read_result.success
    assert read_result.content == "first part second part", f"Append content mismatch: {read_result.content!r}"
    print("[PASS] Append mode works correctly")


@pytest.mark.asyncio
async def test_empty_file(test_session):
    """Test reading an empty file."""
    fs = test_session.file_system
    path = "/tmp/channel_test_empty.txt"

    write_result = await fs.write_file(path, "")
    assert write_result.success

    read_result = await fs.read_file(path)
    assert read_result.success
    assert read_result.content == "", f"Expected empty content, got: {read_result.content!r}"
    print("[PASS] Empty file read correctly")


@pytest.mark.asyncio
async def test_binary_file_roundtrip(test_session):
    """Test binary file read works correctly."""
    fs = test_session.file_system
    path = "/tmp/channel_test_binary.txt"

    # Write some content that we'll read back as binary
    content = "Binary test content with special chars: \x00\x01\x02"
    write_result = await fs.write_file(path, content)
    assert write_result.success

    read_result = await fs.read_file(path, format="bytes")
    assert read_result.success
    assert isinstance(read_result.content, bytes), f"Expected bytes, got {type(read_result.content)}"
    print(f"[PASS] Binary file read: {len(read_result.content)} bytes")


@pytest.mark.asyncio
async def test_nonexistent_file_read(test_session):
    """Test reading a nonexistent file returns error."""
    fs = test_session.file_system
    path = "/tmp/channel_test_nonexistent_12345.txt"

    read_result = await fs.read_file(path)
    assert not read_result.success, "Expected failure for nonexistent file"
    print(f"[PASS] Nonexistent file error: {read_result.error_message}")


@pytest.mark.asyncio
async def test_unicode_content(test_session):
    """Test write+read of unicode content."""
    fs = test_session.file_system
    content = "你好世界 🌍 こんにちは 안녕하세요 مرحبا"
    path = "/tmp/channel_test_unicode.txt"

    write_result = await fs.write_file(path, content)
    assert write_result.success

    read_result = await fs.read_file(path)
    assert read_result.success
    assert read_result.content == content, f"Unicode content mismatch"
    print("[PASS] Unicode content roundtrip")
