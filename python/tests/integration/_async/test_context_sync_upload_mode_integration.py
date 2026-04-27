# ci-stable
import random
import time

import pytest

from agentbay import CreateSessionParams
from agentbay import (
    ContextSync,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    SyncPolicy,
    UploadMode,
    UploadPolicy,
)


def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"


@pytest.fixture
def unique_id():
    """Generate a unique ID shared across tests in this module."""
    uid = generate_unique_id()
    print(f"Using unique ID for test: {uid}")
    return uid


@pytest.mark.asyncio
async def test_create_session_with_default_file_upload_mode(agent_bay_client, unique_id):
    """Test creating session with default File upload mode and write file."""
    print("\n=== Testing basic functionality with default File upload mode ===")

    # Step 1: Use context.get method to generate contextId
    context_name = f"test-context-{unique_id}"
    print(f"Creating context with name: {context_name}")

    context_result = await agent_bay_client.context.get(context_name, True)
    assert context_result.success, f"Failed to create context: {context_result.error_message}"
    assert context_result.context_id is not None
    assert context_result.context_id != ""

    print(f"Generated contextId: {context_result.context_id}")
    print(f"Context get request ID: {context_result.request_id}")

    # Step 2: Create session with contextSync using default File uploadMode
    sync_policy = SyncPolicy.default()  # Uses default uploadMode "File"

    context_sync = ContextSync(
        context_id=context_result.context_id, path="/tmp/test", policy=sync_policy
    )

    session_params = CreateSessionParams(
        labels={
            "test": f"upload-mode-{unique_id}",
            "type": "basic-functionality",
        },
        context_syncs=[context_sync],
    )

    print("Creating session with default File upload mode...")
    session_result = await agent_bay_client.create(session_params)
    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    assert session_result.session is not None
    assert session_result.request_id is not None
    assert session_result.request_id != ""

    session = session_result.session

    print(f"✅ Session created successfully!")
    print(f"Session ID: {session.session_id}")
    print(f"Session creation request ID: {session_result.request_id}")

    # Get session status (status only)
    status_result = await session.get_status()
    assert status_result.status == "RUNNING"
    assert status_result.success, f"Failed to get session status: {status_result.error_message}"
    assert status_result.status
    print(f"Status: {status_result.status}")
    print(f"Get status request ID: {status_result.request_id}")

    print("✅ All basic functionality tests passed!")

    # Cleanup
    print("Cleaning up: Deleting the session...")
    delete_result = await agent_bay_client.delete(session, sync_context=True)
    assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
    print(f"Session {session.session_id} deleted successfully")


@pytest.mark.asyncio
async def test_context_sync_with_archive_mode_and_file_operations(agent_bay_client, unique_id):
    """Test contextId and path usage with Archive mode and file operations."""
    print(
        "\n=== Testing contextId and path usage with Archive mode and file operations ==="
    )

    context_name = f"archive-mode-context-{unique_id}"
    context_result = await agent_bay_client.context.get(context_name, True)

    assert context_result.success, f"Failed to create context: {context_result.error_message}"
    assert context_result.context_id is not None
    assert context_result.context_id != ""

    print(f"Generated contextId: {context_result.context_id}")

    # Create sync policy with Archive upload mode
    upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
    sync_policy = SyncPolicy(upload_policy=upload_policy)

    context_sync = ContextSync.new(
        context_id=context_result.context_id,
        path="/tmp/archive-mode-test",
        policy=sync_policy,
    )

    assert context_sync.context_id == context_result.context_id
    assert context_sync.path == "/tmp/archive-mode-test"
    assert context_sync.policy.upload_policy.upload_mode == UploadMode.ARCHIVE

    print(
        "✅ ContextSync.new works correctly with contextId and path using Archive mode"
    )

    # Create session with the contextSync
    session_params = CreateSessionParams(
        labels={
            "test": f"archive-mode-{unique_id}",
            "type": "contextId-path-validation",
        },
        context_syncs=[context_sync],
    )

    print("Creating session with Archive mode contextSync...")
    session_result = await agent_bay_client.create(session_params)

    assert session_result.success, f"Failed to create session: {session_result.error_message}"
    assert session_result.session is not None
    assert session_result.request_id is not None

    session = session_result.session

    # Get session status (status only)
    status_result = await session.get_status()
    assert status_result.success, f"Failed to get session status: {status_result.error_message}"
    assert status_result.status
    assert status_result.status == "RUNNING", f"Session status should be RUNNING"
    print(f"Status: {status_result.status}")

    print(f"✅ Session created successfully with ID: {session.session_id}")
    print(f"Session creation request ID: {session_result.request_id}")

    # Write a 5KB file using FileSystem
    print("Writing 5KB file using FileSystem...")

    # Generate 5KB content (approximately 5120 bytes)
    content_size = 5 * 1024  # 5KB
    base_content = "Archive mode test successful! This is a test file created in the session path. "
    repeated_content = base_content * (content_size // len(base_content) + 1)
    file_content = repeated_content[:content_size]

    # Create file path in the session path directory
    file_path = "/tmp/archive-mode-test/test-file-5kb.txt"

    print(f"Creating file: {file_path}")
    print(f"File content size: {len(file_content)} bytes")
    # 创建/tmp/archive-mode-test/目录
    direction_result =  await session.file_system.create_directory("/tmp/archive-mode-test")
    assert direction_result.success, f"Failed to create directory: {direction_result.error_message}"
    print(f"Directory created successfully!")
    write_result = await session.file_system.write_file(
        file_path, file_content, "overwrite"
    )

    # Verify file write success
    assert write_result.success, f"Failed to write file: {write_result.error_message}"
    assert write_result.request_id is not None
    assert write_result.request_id != ""

    print(f"✅ File write successful!")
    print(f"Write file request ID: {write_result.request_id}")

    delete_result = await agent_bay_client.delete(session, sync_context=True)
    assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
    print(f"Session {session.session_id} deleted successfully")
    # List files in context sync directory
    print("Listing files in context sync directory...")

    sync_dir_path = "/tmp/archive-mode-test"

    list_result = await agent_bay_client.context.list_files(
        context_result.context_id, sync_dir_path, page_number=1, page_size=10
    )

    # Verify ListFiles success
    assert list_result.success, \
        f"Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}"
    assert list_result.request_id is not None
    assert list_result.request_id != ""

    print(f"✅ List files successful!")
    print(f"List files request ID: {list_result.request_id}")
    print(f"Total files found: {len(list_result.entries)}")

    if list_result.entries:
        print("📋 Files in context sync directory:")
        for index, entry in enumerate(list_result.entries):
            print(f"  [{index}] FilePath: {entry.file_path}")
            print(f"      FileType: {entry.file_type}")
            print(f"      FileName: {entry.file_name}")
            print(f"      Size: {entry.size} bytes")

        # Check if any file contains 'zip' in fileName (for Archive mode)
        has_zip_file = any(
            "zip" in entry.file_name.lower()
            for entry in list_result.entries
            if entry.file_name
        )
        if has_zip_file:
            print(
                "✅ Found zip file in Archive mode - this indicates successful archive compression"
            )
        else:
            print("ℹ️  No zip file found - files may be stored individually")
    else:
        print("No files found in context sync directory")

    print(
        "✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully"
    )

    # Cleanup
    print("Cleaning up: Deleting the session...")
    


@pytest.mark.asyncio
async def test_invalid_upload_mode_with_policy_assignment(agent_bay_client, unique_id):
    """Test error handling when using invalid uploadMode with policy assignment."""
    print("\n=== Testing invalid uploadMode with policy assignment ===")

    context_name = f"invalid-policy-context-{unique_id}"
    context_result = await agent_bay_client.context.get(context_name, True)
    assert context_result.success, f"Failed to create context: {context_result.error_message}"

    # Test 1: Invalid upload mode through SyncPolicy creation (new test for agentbay.create scenario)
    print(
        "Testing invalid uploadMode through SyncPolicy instantiation (agentbay.create scenario)..."
    )

    with pytest.raises(ValueError) as exc_info:
        # This simulates what happens when user passes invalid uploadMode in agentbay.create
        invalid_upload_policy = UploadPolicy(upload_mode="InvalidMode")
        SyncPolicy(upload_policy=invalid_upload_policy)

    assert "Invalid upload_mode value: InvalidMode" in str(exc_info.value)
    assert "Valid values are: File, Archive" in str(exc_info.value)

    print(
        "✅ SyncPolicy correctly threw error for invalid uploadMode during instantiation"
    )

    # Test 2: Test the complete flow with ContextSync (most realistic scenario)
    print("Testing invalid uploadMode through complete ContextSync flow...")

    with pytest.raises(ValueError) as exc_info:
        # This is the most realistic scenario - user creates ContextSync with invalid policy
        invalid_upload_policy = UploadPolicy(upload_mode="BadValue")
        sync_policy = SyncPolicy(upload_policy=invalid_upload_policy)

        # This would be used in agentbay.create(CreateSessionParams(context_syncs=[context_sync]))
        ContextSync.new(
            context_id=context_result.context_id,
            path="/tmp/test-invalid",
            policy=sync_policy,
        )

    assert "Invalid upload_mode value: BadValue" in str(exc_info.value)
    assert "Valid values are: File, Archive" in str(exc_info.value)

    print(
        "✅ Complete ContextSync flow correctly threw error for invalid uploadMode"
    )


@pytest.mark.asyncio
async def test_valid_upload_mode_values(agent_bay_client, unique_id):
    """Test that valid uploadMode values are accepted."""
    print("\n=== Testing valid uploadMode values ===")

    context_name = f"valid-context-{unique_id}"
    context_result = await agent_bay_client.context.get(context_name, True)
    assert context_result.success, f"Failed to create context: {context_result.error_message}"

    # Test "File" mode
    file_upload_policy = UploadPolicy(upload_mode=UploadMode.FILE)
    file_sync_policy = SyncPolicy(upload_policy=file_upload_policy)

    # Should not raise any exception
    file_context_sync = ContextSync.new(
        context_id=context_result.context_id,
        path="/tmp/test-file",
        policy=file_sync_policy,
    )

    assert file_context_sync.policy.upload_policy.upload_mode == UploadMode.FILE
    print("✅ 'File' uploadMode accepted successfully")

    # Test "Archive" mode
    archive_upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
    archive_sync_policy = SyncPolicy(upload_policy=archive_upload_policy)

    # Should not raise any exception
    archive_context_sync = ContextSync.new(
        context_id=context_result.context_id,
        path="/tmp/test-archive",
        policy=archive_sync_policy,
    )

    assert archive_context_sync.policy.upload_policy.upload_mode == UploadMode.ARCHIVE
    print("✅ 'Archive' uploadMode accepted successfully")


def test_upload_policy_serialization():
    """Test that UploadPolicy serializes uploadMode correctly."""
    print("\n=== Testing UploadPolicy serialization ===")

    # Test File mode serialization
    file_policy = UploadPolicy(upload_mode=UploadMode.FILE)
    file_dict = file_policy.__dict__()

    assert "uploadMode" in file_dict
    assert file_dict["uploadMode"] == "File"
    print("✅ File mode serialization works correctly")

    # Test Archive mode serialization
    archive_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
    archive_dict = archive_policy.__dict__()

    assert "uploadMode" in archive_dict
    assert archive_dict["uploadMode"] == "Archive"
    print("✅ Archive mode serialization works correctly")

    # Test default policy serialization
    default_policy = UploadPolicy.default()
    default_dict = default_policy.__dict__()

    assert "uploadMode" in default_dict
    assert default_dict["uploadMode"] == "File"  # Default should be File
    print("✅ Default policy serialization works correctly")


@pytest.mark.asyncio
async def test_archive_mode_with_exclude_paths(agent_bay_client, unique_id):
    """Test Archive mode with archiveExcludePaths for hybrid storage.

    Verifies that when archiveExcludePaths is set:
    1. Session creation succeeds with the policy
    2. Files can be written to both excluded and non-excluded paths
    3. After sync, files are stored (excluded files individually, rest archived)
    4. Excluded files should be accessible individually via list_files

    NOTE: This test is skipped in production environment.
    The feature works correctly in pre-release environment, but has not been
    deployed to production yet. Remove this skip after production deployment.
    """
    pytest.skip(
        "archiveExcludePaths works in pre-release but not deployed to production yet. "
        "Remove this skip after production environment is updated."
    )

    print("\n=== Testing Archive mode with archiveExcludePaths ===")

    context_name = f"archive-exclude-context-{unique_id}"
    context_result = await agent_bay_client.context.get(context_name, True)
    assert context_result.success, f"Failed to create context: {context_result.error_message}"
    assert context_result.context_id is not None

    upload_policy = UploadPolicy(
        upload_mode=UploadMode.ARCHIVE,
        archive_exclude_paths=["important/", "config.json"],
    )
    sync_policy = SyncPolicy(upload_policy=upload_policy)

    sync_path = "/tmp/archive-exclude-test"
    context_sync = ContextSync.new(
        context_id=context_result.context_id,
        path=sync_path,
        policy=sync_policy,
    )

    assert context_sync.policy.upload_policy.upload_mode == UploadMode.ARCHIVE
    assert context_sync.policy.upload_policy.archive_exclude_paths == [
        "important/",
        "config.json",
    ]

    session_params = CreateSessionParams(
        labels={
            "test": f"archive-exclude-{unique_id}",
            "type": "archive-exclude-paths",
        },
        context_syncs=[context_sync],
    )

    print("Creating session with Archive mode + exclude paths...")
    session_result = await agent_bay_client.create(session_params)
    assert (
        session_result.success
    ), f"Failed to create session: {session_result.error_message}"
    session = session_result.session

    try:
        # Create directory structure
        dir_result = await session.file_system.create_directory(
            f"{sync_path}/important"
        )
        assert dir_result.success
        dir_result = await session.file_system.create_directory(
            f"{sync_path}/regular"
        )
        assert dir_result.success

        # Write files: some in excluded paths, some not
        write_result = await session.file_system.write_file(
            f"{sync_path}/important/data.txt",
            "This file should be stored individually via FILE mode",
            mode="overwrite",
        )
        assert write_result.success

        write_result = await session.file_system.write_file(
            f"{sync_path}/config.json",
            '{"key": "value", "setting": true}',
            mode="overwrite",
        )
        assert write_result.success

        write_result = await session.file_system.write_file(
            f"{sync_path}/regular/data.txt",
            "This file should be archived with the rest",
            mode="overwrite",
        )
        assert write_result.success

        print("All files written successfully")

        # Delete session with sync to trigger upload
        delete_result = await agent_bay_client.delete(session, sync_context=True)
        assert (
            delete_result.success
        ), f"Failed to delete session: {delete_result.error_message}"
        session = None
        print("Session deleted with sync_context=True")

        # Verify files via list_files
        list_result = await agent_bay_client.context.list_files(
            context_result.context_id, sync_path, page_number=1, page_size=20
        )
        assert list_result.success, (
            f"Failed to list files: "
            f"{getattr(list_result, 'error_message', 'Unknown error')}"
        )
        assert len(list_result.entries) > 0, "Should have files after sync"

        print(f"Total files found: {len(list_result.entries)}")
        for entry in list_result.entries:
            print(
                f"  {entry.file_path} | {entry.file_name} "
                f"({entry.file_type}, {entry.size} bytes)"
            )

        # Verify excluded files exist as individual entries
        file_paths = [entry.file_path for entry in list_result.entries]
        file_names = [entry.file_name for entry in list_result.entries]

        has_important = any("important" in p for p in file_paths)
        has_config = any("config.json" in n for n in file_names)

        print(f"Has excluded 'important/' files individually: {has_important}")
        print(f"Has excluded 'config.json' individually: {has_config}")

        assert has_important, (
            "Expected excluded path 'important/' files to be stored individually "
            f"(archiveExcludePaths), but got: {file_names}"
        )
        assert has_config, (
            "Expected excluded file 'config.json' to be stored individually "
            f"(archiveExcludePaths), but got: {file_names}"
        )

        # Check for Presigned URL accessibility on excluded files
        for entry in list_result.entries:
            if "important" in entry.file_path or "config.json" in entry.file_name:
                presigned_url = getattr(entry, "presigned_url", None) or getattr(
                    entry, "download_url", None
                )
                if presigned_url:
                    print(
                        f"  Excluded file '{entry.file_name}' has "
                        f"Presigned URL: {presigned_url[:80]}..."
                    )

        print("Archive mode with exclude paths test completed successfully")

    finally:
        if session is not None:
            await agent_bay_client.delete(session, sync_context=True)
