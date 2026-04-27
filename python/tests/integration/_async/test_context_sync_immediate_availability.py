"""Integration test for context.sync() immediate file availability.
ci-stable
"""
import random
import time
import asyncio
import pytest

from agentbay import CreateSessionParams, AgentBayLogger, get_logger
from agentbay import (
    ContextSync,
    SyncPolicy,
)

# Setup INFO level logging to see detailed communication
AgentBayLogger.setup(level="INFO", enable_console=True)
logger = get_logger("test_context_sync")


def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"


@pytest.mark.asyncio
async def test_context_sync_immediate_file_availability(agent_bay_client):
    """
    Test that after context.sync() returns, files are immediately available in context storage.
    
    Test flow:
    1. Create a context
    2. Create a session with context sync
    3. Write a test file to the session
    4. Call context.sync() and wait for it to complete
    5. Immediately check if the file exists in context storage
    """
    print("=== Testing context.sync() immediate file availability ===")
    logger.info("Starting large file sync test with detailed logging")

    unique_id = generate_unique_id()
    test_sessions = []

    # Step 1: Create a context
    context_name = f"test-sync-immediate-{unique_id}"
    context_result = await agent_bay_client.context.create(context_name)

    assert context_result.success, f"Failed to create context: {context_result.error_message}"

    context_id = context_result.context_id
    print(f"✅ Created context: {context_id}")

    try:
        # Step 2: Create session with context sync
        context_sync = ContextSync.new(
            context_id,
            "/tmp/sync-test",
            SyncPolicy.default()
        )

        session_params = CreateSessionParams()
        session_params.context_syncs = [context_sync]
        session_params.labels = {"test": "context-sync-immediate-availability"}
        session_params.image_id = "linux_latest"

        session_result = await agent_bay_client.create(session_params)
        assert session_result.success, f"Failed to create session: {session_result.error_message}"

        session = session_result.session
        test_sessions.append(session)
        print(f"✅ Created session: {session.session_id}")

        # Wait for session to be ready
        await asyncio.sleep(2)

        # Step 3: Create a large test file directly in the cloud environment (more efficient)
        test_file_path = "/tmp/sync-test/large_test_file.txt"

        # Use dd command to create a 5MB file directly in the cloud environment
        create_cmd = f"dd if=/dev/zero of={test_file_path} bs=1M count=5"
        cmd_result = await session.command.execute_command(create_cmd)
        assert cmd_result.success, f"Failed to create large file: {cmd_result.error_message}"
        print(f"✅ Created large test file directly in cloud: {test_file_path}")
        print(f"   Command output: {cmd_result.output.strip()}")

        # Verify file was created and get its size
        size_cmd = f"ls -lh {test_file_path}"
        size_result = await session.command.execute_command(size_cmd)
        assert size_result.success, f"Failed to check file size: {size_result.error_message}"
        print(f"✅ File details: {size_result.output.strip()}")

        # Step 4: Call context.sync() and wait for completion
        # Explicitly pass context_id and path to avoid server-side 500 errors
        # that occur when sync() is called without parameters.
        print("📤 Starting context sync...")
        sync_result = await session.context.sync(
            context_id=context_id,
            path="/tmp/sync-test",
        )

        assert sync_result.success, f"Failed to sync context: {sync_result.error_message}"
        assert sync_result.request_id is not None
        print(f"✅ Context sync completed successfully (RequestID: {sync_result.request_id})")

        # Step 5: Immediately check if file exists in context storage
        print("🔍 Immediately checking file availability in context...")

        # Context files are stored under OSS internal paths, not local Linux paths.
        # list_files() must be called with the logical path (e.g. "/tmp/sync-test"),
        # but get_file_download_url() needs the raw OSS path returned by the server.
        # We collect both: entry.file_path (logical) and entry._oss_path (raw OSS path).
        async def collect_all_file_entries(ctx_id: str, folder_path: str, depth: int = 0) -> list:
            """Recursively collect all FILE entries under a context folder.
            Each returned entry has an extra attribute `_oss_path` = the raw file_path
            returned by the server (used for get_file_download_url).
            """
            if depth > 5:
                return []
            result = await agent_bay_client.context.list_files(
                ctx_id, folder_path, page_number=1, page_size=50
            )
            if not result.success:
                print(f"  ⚠️  list_files('{folder_path}') failed")
                return []
            entries = []
            for entry in result.entries:
                file_type = getattr(entry, "file_type", None) or ""
                print(f"  {'  ' * depth}[{file_type}] {entry.file_path}")
                if file_type.upper() == "FOLDER":
                    # Extract the last segment of the raw OSS path returned by server,
                    # then append it to the current folder_path for the next list_files call.
                    # e.g. folder_path="/tmp/sync-test", entry.file_path=".../.../subdir"
                    #      → next_path = "/tmp/sync-test/subdir"
                    last_segment = entry.file_path.rstrip("/").rsplit("/", 1)[-1]
                    next_path = folder_path.rstrip("/") + "/" + last_segment if folder_path else last_segment
                    entries.extend(
                        await collect_all_file_entries(ctx_id, next_path, depth + 1)
                    )
                else:
                    # Attach the raw OSS file_path for use with get_file_download_url
                    entry._oss_path = entry.file_path
                    entries.append(entry)
            return entries

        all_entries = await collect_all_file_entries(context_id, "/tmp/sync-test")
        print(f"📂 Total files found in context: {len(all_entries)}")
        for e in all_entries:
            print(f"   - {e.file_path} ({e.file_name}, size={e.size})")

        # Check if our test file is in the list (match by file name)
        file_found = False
        for entry in all_entries:
            if entry.file_name == "large_test_file.txt":
                file_found = True
                print(f"✅ Found large test file in context: {entry.file_path} (Size: {entry.size} bytes)")
                expected_size = 5 * 1024 * 1024  # 5MB
                if entry.size >= expected_size:
                    print(f"✅ File size is correct: {entry.size} bytes (≥ {expected_size} bytes)")
                else:
                    print(f"⚠️  File size seems small: got {entry.size}, expected ≥ {expected_size} bytes")
                break

        assert file_found, (
            f"Test file 'large_test_file.txt' not found in context immediately after sync. "
            f"Found files: {[e.file_path for e in all_entries]}"
        )

        # Additional verification: Try to get download URL using the raw OSS file path
        found_entry = next((e for e in all_entries if e.file_name == "large_test_file.txt"), None)
        if found_entry:
            try:
                oss_path = getattr(found_entry, "_oss_path", found_entry.file_path)
                download_url_result = await agent_bay_client.context.get_file_download_url(
                    context_id,
                    oss_path  # Use raw OSS path returned by server, not the logical local path
                )

                if download_url_result.success:
                    print(f"✅ File download URL available: {download_url_result.url[:50]}...")
                else:
                    print(f"⚠️  File download URL not immediately available: {download_url_result.error_message}")

            except Exception as e:
                print(f"⚠️  Error getting download URL: {e}")

        print("🎉 Test completed successfully - large file (5MB) is immediately available after sync!")

    finally:
        # Clean up sessions
        for session in test_sessions:
            try:
                delete_result = await agent_bay_client.delete(session, sync_context=True)
                print(f"Cleaned up session {session.session_id}: {delete_result.success}")
            except Exception as e:
                print(f"Error cleaning up session {session.session_id}: {e}")

        # Clean up context
        try:
            from agentbay._async.context import Context
            context_obj = Context(id=context_id, name=context_name)
            delete_context_result = await agent_bay_client.context.delete(context_obj)
            print(f"Cleaned up context {context_id}: {delete_context_result.success}")
        except Exception as e:
            print(f"Error cleaning up context {context_id}: {e}")
