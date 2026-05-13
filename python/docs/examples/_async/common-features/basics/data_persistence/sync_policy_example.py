#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - RecyclePolicy, Archive Mode & BWList Example

This example demonstrates three SyncPolicy features for controlling
data lifecycle and upload behavior:

1. RecyclePolicy - Automatic data cleanup after specified time periods
2. Archive Mode with Exclude Paths - Compressed upload with selective file exclusion
3. BWList with Regex Patterns - Fine-grained control over which files sync

For a complete list of lifecycle options (1Day/3Days/5Days/10Days/30Days/Forever),
see the data_persistence documentation.

Business Scenario:
An application needs to manage cloud storage with different policies:
- RecyclePolicy: Auto-delete temporary data after 1 day
- Archive mode: Compress bulk data into zip, but keep important files individual
- BWList: Only sync project directories, exclude cache folders
"""

import asyncio
import os
import time
from agentbay import (
    AsyncAgentBay,
    CreateSessionParams,
    ContextSync,
    SyncPolicy,
    RecyclePolicy,
    Lifecycle,
    UploadPolicy,
    UploadMode,
    DownloadPolicy,
    DeletePolicy,
    ExtractPolicy,
    BWList,
    WhiteList,
)


async def collect_all_files(agent_bay, context_id: str, folder_path: str) -> list:
    """Recursively collect all FILE entries under folder_path.

    list_files only returns entries at the current level.
    FOLDER entries must be recursed into to find individual files.
    """
    result = await agent_bay.context.list_files(
        context_id=context_id,
        parent_folder_path=folder_path,
        page_size=200,
    )
    if not result.success or not result.entries:
        return []

    file_paths = []
    for entry in result.entries:
        ftype = (entry.file_type or "").upper()
        last_segment = entry.file_path.rstrip("/").rsplit("/", 1)[-1]
        if ftype in ("FOLDER", "DIR", "DIRECTORY"):
            sub_path = folder_path.rstrip("/") + "/" + last_segment
            file_paths.extend(
                await collect_all_files(agent_bay, context_id, sub_path)
            )
        else:
            file_paths.append(entry.file_path)
    return file_paths


async def example_1_recycle_policy_one_day():
    """Example 1: RecyclePolicy with 1-day lifecycle - data auto-deleted after 1 day"""
    print("\n" + "=" * 70)
    print("Example 1: RecyclePolicy with 1-Day Lifecycle")
    print("=" * 70)

    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)
    context_name = f"recycle-1day-demo-{int(time.time())}"

    # Create context
    context_result = await agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        print(f"  Failed to create context: {context_result.error_message}")
        return

    context = context_result.context
    context_id = context_result.context_id
    print(f"  Context created: {context.id}")

    try:
        # Create RecyclePolicy with 1-day lifecycle
        recycle_policy = RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY,
            paths=[""]  # Apply to all paths in context
        )

        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy.default(),
            download_policy=DownloadPolicy.default(),
            delete_policy=DeletePolicy.default(),
            extract_policy=ExtractPolicy.default(),
            recycle_policy=recycle_policy,
            bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])])
        )

        print(f"  Lifecycle: {sync_policy.recycle_policy.lifecycle.value}")
        print(f"  Paths: {sync_policy.recycle_policy.paths}")
        print(f"  Info: Data will be automatically deleted after 1 day")

        context_sync = ContextSync.new(
            context_id=context_id,
            path="/tmp/oneday_data",
            policy=sync_policy
        )

        # Create session with context sync
        params = CreateSessionParams(context_syncs=[context_sync])
        session_result = await agent_bay.create(params)

        if not session_result.success:
            print(f"  Failed to create session: {session_result.error_message}")
            return

        session = session_result.session
        print(f"  Session created: {session.session_id}")

        try:
            # Write data that will be auto-cleaned
            mkdir_result = await session.file_system.create_directory("/tmp/oneday_data")
            if mkdir_result.success:
                write_result = await session.file_system.write_file(
                    "/tmp/oneday_data/test.txt",
                    "This data will be auto-deleted after 1 day"
                )
                if write_result.success:
                    print("  Data written to /tmp/oneday_data/test.txt")
                else:
                    print(f"  Failed to write: {write_result.error_message}")
        finally:
            # Delete session with sync to persist data to context
            await agent_bay.delete(session, sync_context=True)
            print("  Session deleted (with context sync)")

    finally:
        await agent_bay.context.delete(context)
        print("  Context deleted")


async def example_2_archive_mode_with_exclude_paths():
    """Example 2: Archive upload mode with exclude paths for hybrid storage.

    Archive mode compresses files into a zip archive during upload.
    archive_exclude_paths allows certain files to bypass archiving and
    be stored individually, so they can be accessed directly via presigned URLs.
    """
    print("\n" + "=" * 70)
    print("Example 2: Archive Mode with Exclude Paths")
    print("=" * 70)

    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)
    context_name = f"archive-exclude-demo-{int(time.time())}"

    # Create context
    context_result = await agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        print(f"  Failed to create context: {context_result.error_message}")
        return

    context = context_result.context
    context_id = context_result.context_id
    print(f"  Context created: {context.id}")

    session = None
    try:
        # Create SyncPolicy with Archive mode + exclude paths
        upload_policy = UploadPolicy(
            upload_mode=UploadMode.ARCHIVE,
            archive_exclude_paths=["important/", "config.json"],
        )
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        sync_path = "/tmp/archive-exclude-test"
        context_sync = ContextSync.new(
            context_id=context_id,
            path=sync_path,
            policy=sync_policy,
        )

        print(f"  Upload mode: {sync_policy.upload_policy.upload_mode.value}")
        print(f"  Exclude paths: {sync_policy.upload_policy.archive_exclude_paths}")
        print(f"  Info: Excluded files stored individually, rest archived as zip")

        # Create session
        params = CreateSessionParams(context_syncs=[context_sync])
        session_result = await agent_bay.create(params)

        if not session_result.success:
            print(f"  Failed to create session: {session_result.error_message}")
            return

        session = session_result.session
        print(f"  Session created: {session.session_id}")

        # Create directory structure
        for d in [f"{sync_path}/important", f"{sync_path}/regular"]:
            dir_result = await session.file_system.create_directory(d)
            if dir_result.success:
                print(f"  Directory created: {d}")

        # Write files: some in excluded paths (stored individually), some not (archived)
        test_files = [
            (f"{sync_path}/important/data.txt",
             "Stored individually via FILE mode (excluded from archive)"),
            (f"{sync_path}/config.json",
             '{"key": "value", "setting": true}'),
            (f"{sync_path}/regular/data.txt",
             "This file will be archived with the rest"),
        ]

        for file_path, content in test_files:
            write_result = await session.file_system.write_file(file_path, content, mode="overwrite")
            status = "OK" if write_result.success else write_result.error_message
            print(f"  Written {file_path}: {status}")

        # Delete session with sync to trigger upload
        delete_result = await agent_bay.delete(session, sync_context=True)
        if not delete_result.success:
            print(f"  Failed to delete session: {delete_result.error_message}")
            return
        session = None
        print("  Session deleted (sync_context=True triggers upload)")

        # Verify files via list_files
        print("\n  Verifying uploaded files via context.list_files...")
        await asyncio.sleep(3)  # Wait for indexing

        list_result = await agent_bay.context.list_files(
            context_id, sync_path, page_number=1, page_size=20
        )

        if list_result.success and list_result.entries:
            print(f"  Found {len(list_result.entries)} entries:")
            for entry in list_result.entries:
                print(f"    - {entry.file_path} ({entry.file_type}, {entry.size} bytes)")

            # Check: excluded files should be individual, rest should be in a zip
            has_important = any("important" in e.file_path for e in list_result.entries)
            has_config = any("config.json" in (e.file_name or "") for e in list_result.entries)
            print(f"  Excluded 'important/' stored individually: {has_important}")
            print(f"  Excluded 'config.json' stored individually: {has_config}")
        else:
            print("  No files found or list failed")

    finally:
        if session is not None:
            await agent_bay.delete(session, sync_context=True)
        await agent_bay.context.delete(context)
        print("  Context deleted")


async def example_3_bwlist_with_regex():
    """Example 3: BWList with regex patterns for fine-grained file filtering.

    BWList controls which files are included/excluded during upload:
    - path with is_path_regex=True: Include directories matching the pattern
    - exclude_paths with is_exclude_regex=True: Exclude sub-items matching patterns

    File structure:
        /home/wuying/testdata/project-alpha/main.py       <- included
        /home/wuying/testdata/project-alpha/README.txt     <- included
        /home/wuying/testdata/project-beta/config.json     <- included
        /home/wuying/testdata/project-beta/cache/temp.log  <- EXCLUDED by cache.*
    """
    print("\n" + "=" * 70)
    print("Example 3: BWList with Regex Patterns")
    print("=" * 70)

    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)
    context_name = f"bwlist-regex-demo-{int(time.time())}"

    # Create context
    context_result = await agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        print(f"  Failed to create context: {context_result.error_message}")
        return

    context = context_result.context
    context_id = context_result.context_id
    print(f"  Context created: {context.id}")

    base = "/home/wuying/testdata"
    session = None

    try:
        # Create SyncPolicy with BWList regex patterns
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy.default(),
            download_policy=DownloadPolicy.default(),
            delete_policy=DeletePolicy.default(),
            extract_policy=ExtractPolicy.default(),
            recycle_policy=RecyclePolicy.default(),
            bw_list=BWList(white_lists=[
                WhiteList(
                    path=r"project-.*",        # Include directories matching pattern
                    is_path_regex=True,
                    exclude_paths=[r"cache.*"],  # Exclude sub-directories matching pattern
                    is_exclude_regex=True,
                )
            ]),
        )

        print(f"  Include pattern: project-.* (is_path_regex=True)")
        print(f"  Exclude pattern: cache.* (is_exclude_regex=True)")

        context_sync = ContextSync.new(
            context_id=context_id,
            path=base,
            policy=sync_policy,
        )

        # Create session
        params = CreateSessionParams(context_syncs=[context_sync])
        session_result = await agent_bay.create(params)

        if not session_result.success:
            print(f"  Failed to create session: {session_result.error_message}")
            return

        session = session_result.session
        print(f"  Session created: {session.session_id}")

        # Create directories
        for d in [base, f"{base}/project-alpha", f"{base}/project-beta", f"{base}/project-beta/cache"]:
            dir_result = await session.file_system.create_directory(d)
            if dir_result.success:
                print(f"  Directory created: {d}")

        # Write files
        test_files = [
            (f"{base}/project-alpha/main.py", "# main entry point"),
            (f"{base}/project-alpha/README.txt", "Project Alpha README"),
            (f"{base}/project-beta/config.json", '{"env": "test"}'),
            (f"{base}/project-beta/cache/temp.log", "temporary log"),  # Will be excluded
        ]

        for file_path, content in test_files:
            write_result = await session.file_system.write_file(file_path, content)
            status = "OK" if write_result.success else write_result.error_message
            print(f"  Written {file_path}: {status}")

        # Delete session with sync to trigger filtered upload
        delete_result = await agent_bay.delete(session, sync_context=True)
        if not delete_result.success:
            print(f"  Failed to delete session: {delete_result.error_message}")
            return
        session = None
        print("  Session deleted (sync_context=True triggers filtered upload)")

        # Verify files via list_files (recursive to find files inside subdirectories)
        print("\n  Verifying uploaded files via context.list_files...")
        await asyncio.sleep(3)  # Wait for indexing

        all_paths = await collect_all_files(agent_bay, context_id, base)

        if all_paths:
            print(f"  Found {len(all_paths)} file(s):")
            for p in all_paths:
                print(f"    - {p}")

            # Verify expected files are present
            expected_names = ["main.py", "README.txt", "config.json"]
            for name in expected_names:
                found = any(name in p for p in all_paths)
                print(f"    {'FOUND' if found else 'NOT FOUND'}: {name}")

            # Verify excluded file is absent
            cache_found = any("cache" in p and "temp.log" in p for p in all_paths)
            print(f"    {'FOUND (should be absent!)' if cache_found else 'correctly absent'}: cache/temp.log")
        else:
            print("  No files found")

    finally:
        if session is not None:
            await agent_bay.delete(session, sync_context=True)
        await agent_bay.context.delete(context)
        print("  Context deleted")


async def example_4_error_handling():
    """Example 4: Error handling for invalid policy configurations"""
    print("\n" + "=" * 70)
    print("Example 4: Error Handling for Invalid Policy Configurations")
    print("=" * 70)

    # Test 1: Wildcard in RecyclePolicy path (not supported)
    print("\n  Test 1: Wildcard * in RecyclePolicy path (should fail)")
    try:
        RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/invalid/path/*"])
        print("    ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"    Correctly rejected: {str(e)[:80]}...")

    # Test 2: Invalid lifecycle value
    print("\n  Test 2: Invalid lifecycle value (should fail)")
    try:
        RecyclePolicy(lifecycle="invalid_lifecycle", paths=[""])
        print("    ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"    Correctly rejected: {str(e)[:80]}...")

    # Test 3: Invalid upload mode
    print("\n  Test 3: Invalid upload mode (should fail)")
    try:
        UploadPolicy(upload_mode="InvalidMode")
        print("    ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"    Correctly rejected: {str(e)[:80]}...")

    # Test 4: Correct combined usage
    print("\n  Test 4: Correct combined usage of all three features")
    recycle_policy = RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=["/tmp/cache"])
    upload_policy = UploadPolicy(
        upload_mode=UploadMode.ARCHIVE,
        archive_exclude_paths=["config/"]
    )
    bw_list = BWList(white_lists=[
        WhiteList(path=r"project-.*", is_path_regex=True)
    ])
    sync_policy = SyncPolicy(
        upload_policy=upload_policy,
        recycle_policy=recycle_policy,
        bw_list=bw_list,
    )
    print(f"    RecyclePolicy: lifecycle={sync_policy.recycle_policy.lifecycle.value}, paths={sync_policy.recycle_policy.paths}")
    print(f"    UploadPolicy: mode={sync_policy.upload_policy.upload_mode.value}, exclude={sync_policy.upload_policy.archive_exclude_paths}")
    print(f"    BWList: path={sync_policy.bw_list.white_lists[0].path}, is_regex={sync_policy.bw_list.white_lists[0].is_path_regex}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("RecyclePolicy, Archive Mode & BWList Examples")
    print("=" * 70)

    try:
        await example_1_recycle_policy_one_day()
        await example_2_archive_mode_with_exclude_paths()
        await example_3_bwlist_with_regex()
        await example_4_error_handling()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nExample failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
