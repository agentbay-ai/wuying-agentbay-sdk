"""
ci-stable
Integration tests for the FileTransfer functionality.
These tests verify the complete functionality of the FileTransfer class
with real sessions and actual file transfers.
"""

import os
import tempfile

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def filetransfer_session(make_session):
    lc = await make_session("linux_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_file_upload_integration(filetransfer_session):
    """Test complete file upload workflow with real session and verification."""
    session = filetransfer_session
    print(f"Session created with ID: {session.session_id}")

    print("Testing file upload...")
    # Create a temporary file for upload
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt"
    ) as temp_file:
        test_content = (
            "This is a test file for AgentBay FileTransfer upload integration test.\n"
            * 10
        )
        temp_file.write(test_content)
        temp_file.flush()  # Ensure content is written to disk
        temp_file_path = temp_file.name

    try:
        # Upload the file - use path that matches the auto-created file_transfer context
        context_path = await session.file_system.get_file_transfer_context_path()
        if context_path:
            remote_path = f"{context_path}/upload_test.txt"
        else:
            # If no context path is available, skip the test
            print("❌ No context path available, skipping upload test")
            pytest.skip("No file transfer context path available")

        upload_result = await session.file_system.upload_file(
            local_path=temp_file_path,
            remote_path=remote_path,
        )

        # Verify upload result
        assert upload_result.success, f"Upload failed: {upload_result.error}"
        assert upload_result.bytes_sent > 0
        assert upload_result.request_id_upload_url is not None
        assert upload_result.request_id_sync is not None

        ls_result = await session.command.execute_command(
            "ls -la /tmp/file-transfer/"
        )
        if not ls_result.success:
            print("    ❌ fileTransfer directory not found")
            assert False

        print(f"    ✅ fileTransfer directory exists: /tmp/file-transfer/")
        print(f"    Directory content:\n{ls_result.output}")

        # Verify file exists in remote location by listing directory
        list_result = await session.file_system.list_directory("/tmp/file-transfer/")
        print(f"    Directory listing: {list_result.entries}")
        assert (
            list_result.success
        ), f"Failed to list directory: {list_result.error_message}"

        # Check if our uploaded file is in the directory listing
        file_found = False
        for entry in list_result.entries:
            if entry.name == "upload_test.txt":
                file_found = True
                break

        assert file_found, "Uploaded file not found in remote directory"

        # Verify file content by reading it back
        print(f"Testing file read...{remote_path}")
        read_result = await session.file_system.read_file(remote_path)
        assert (
            read_result.success
        ), f"Failed to read uploaded file: {read_result.error_message}"
        assert read_result.content is not None

    finally:
        # Clean up local temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_file_download_integration(filetransfer_session):
    """Test complete file download workflow with real session and verification."""
    session = filetransfer_session
    print(f"Session created with ID: {session.session_id}")

    # First, create a file in the remote location
    context_path = await session.file_system.get_file_transfer_context_path()
    if context_path:
        remote_path = f"{context_path}/download_test.txt"
    else:
        # Fallback to default path if context path is not available
        remote_path = "/tmp/file-transfer/download_test.txt"
    test_content = (
        "This is a test file for AgentBay FileTransfer download integration test.\n"
        * 15
    )
    print("\n Creating test directory...")

    create_dir_result = await session.file_system.create_directory(
        "/tmp/file-transfer/"
    )
    print(f"Create directory result: {create_dir_result.success}")
    assert create_dir_result.success
    write_result = await session.file_system.write_file(remote_path, test_content)
    assert (
        write_result.success
    ), f"Failed to create remote file: {write_result.error_message}"

    ls_result = await session.command.execute_command("ls -la /tmp/file-transfer/")
    if not ls_result.success:
        print("    ❌ fileTransfer directory not found")
        return False

    print(f"    ✅ fileTransfer directory exists: /tmp/file-transfer/")
    print(f"    Directory content:\n{ls_result.output}")
    # Create a temporary file path for download
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file_path = temp_file.name

    try:
        # Download the file
        download_result = await session.file_system.download_file(
            remote_path=remote_path,
            local_path=temp_file_path,
        )

        # Verify download result
        assert download_result.success, f"Download failed: {download_result.error_message}"
        assert download_result.bytes_received > 0
        assert download_result.request_id_download_url is not None
        assert download_result.request_id_sync is not None
        assert download_result.local_path == temp_file_path

        # Verify downloaded file content
        with open(temp_file_path, "r") as f:
            downloaded_content = f.read()

        print(f"Downloaded file content length: {len(downloaded_content)} bytes")
        assert downloaded_content == test_content

    finally:
        # Clean up temporary files
        for path in [temp_file_path]:
            if os.path.exists(path):
                print(f"Deleting temporary file: {path}")
                os.unlink(path)
