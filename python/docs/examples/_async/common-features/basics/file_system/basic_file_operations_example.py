#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - File System Operations Example

This example demonstrates all file system operations within a session:

Basic Operations:
- Write a file (overwrite / append mode)
- Read a file
- Get file metadata
- Edit a file (find & replace)
- Delete a file and verify removal

Directory Operations:
- Create a directory
- List directory contents

Advanced Operations:
- Move a file
- Search for files by pattern
- Read multiple files at once
- Large file operations (automatic chunking)
"""

import asyncio
import os
import time

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)
    session_result = await agent_bay.create(
        CreateSessionParams(image_id="linux_latest")
    )
    if not session_result.success or not session_result.session:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    fs = session.file_system
    test_file = f"/tmp/agentbay_file_example_{int(time.time())}.txt"

    try:
        # =====================================================================
        # Basic File Operations
        # =====================================================================

        # Step 1: Write file (overwrite mode)
        print("\n[Step 1] Writing file (overwrite mode)...")
        write_result = await fs.write_file(
            test_file, "Hello, AgentBay!\nLine 2\nLine 3", "overwrite"
        )
        if write_result.success:
            print(f"  File written: {test_file}")
        else:
            print(f"  Write failed: {write_result.error_message}")

        # Step 2: Read file
        print("\n[Step 2] Reading file...")
        read_result = await fs.read_file(test_file)
        if read_result.success:
            print(f"  Content: {read_result.content}")
        else:
            print(f"  Read failed: {read_result.error_message}")

        # Step 3: Append to file
        print("\n[Step 3] Appending to file...")
        append_result = await fs.write_file(
            test_file, "\nAppended line", "append"
        )
        if append_result.success:
            print("  Append successful")
            # Verify
            read_result2 = await fs.read_file(test_file)
            if read_result2.success:
                print(f"  Content after append: {read_result2.content}")
        else:
            print(f"  Append failed: {append_result.error_message}")

        # Step 4: Get file info
        print("\n[Step 4] Getting file info...")
        info_result = await fs.get_file_info(test_file)
        if info_result.success:
            file_info = info_result.file_info
            print(f"  File info retrieved:")
            for key, value in file_info.items():
                print(f"    {key}: {value}")
        else:
            print(f"  Get info failed: {info_result.error_message}")

        # Step 5: Edit file (find & replace)
        print("\n[Step 5] Editing file (find & replace)...")
        edits = [
            {"oldText": "Line 3", "newText": "Edited line 3"}
        ]
        edit_result = await fs.edit_file(test_file, edits)
        if edit_result.success:
            print("  Edit successful")
            read_result3 = await fs.read_file(test_file)
            if read_result3.success:
                print(f"  Content after edit: {read_result3.content}")
        else:
            print(f"  Edit failed: {edit_result.error_message}")

        # =====================================================================
        # Directory Operations
        # =====================================================================

        # Step 6: Create directory
        print("\n[Step 6] Creating directory...")
        test_dir = f"/tmp/agentbay_dir_{int(time.time())}"
        dir_result = await fs.create_directory(test_dir)
        if dir_result.success:
            print(f"  Directory created: {test_dir}")
        else:
            print(f"  Create directory failed: {dir_result.error_message}")

        # Step 7: List directory contents
        print("\n[Step 7] Listing directory contents...")
        list_result = await fs.list_directory("/tmp")
        if list_result.success:
            entries = list_result.entries
            print(f"  Found {len(entries)} entries in /tmp:")
            for entry in entries:
                entry_type = "Dir" if entry.is_directory else "File"
                print(f"    - {entry.name} ({entry_type})")
        else:
            print(f"  List directory failed: {list_result.error_message}")

        # =====================================================================
        # Advanced Operations
        # =====================================================================

        # Step 8: Move file
        print("\n[Step 8] Moving file...")
        moved_path = f"{test_dir}/moved_file.txt"
        move_result = await fs.move_file(test_file, moved_path)
        if move_result.success:
            print(f"  File moved: {test_file} -> {moved_path}")
        else:
            print(f"  Move failed: {move_result.error_message}")

        # Step 9: Search files
        print("\n[Step 9] Searching for files...")
        # Create some files for searching
        await fs.write_file(f"{test_dir}/report_jan.txt", "January report", "overwrite")
        await fs.write_file(f"{test_dir}/report_feb.txt", "February report", "overwrite")
        await fs.write_file(f"{test_dir}/data.csv", "Some CSV data", "overwrite")

        search_result = await fs.search_files(test_dir, "*report*")
        if search_result.success:
            print(f"  Search '*report*' found {len(search_result.matches)} files:")
            for f in search_result.matches:
                print(f"    - {f}")
        else:
            print(f"  Search failed: {search_result.error_message}")

        # Step 10: Read multiple files
        print("\n[Step 10] Reading multiple files...")
        file_paths = [
            f"{test_dir}/report_jan.txt",
            f"{test_dir}/report_feb.txt",
        ]
        multi_result = await fs.read_multiple_files(file_paths)
        if multi_result.success:
            print(f"  Read {len(multi_result.contents)} files:")
            for path, content in multi_result.contents.items():
                print(f"    - {path}: {len(content)} bytes")
        else:
            print(f"  Read multiple files failed: {multi_result.error_message}")

        # Step 11: Large file operations (automatic chunking)
        print("\n[Step 11] Large file operations...")
        large_path = f"{test_dir}/large_file.txt"
        line_content = "This is a line of test content for large file testing. " * 20
        large_content = line_content * 500  # ~1MB
        print(f"  Generated test content: {len(large_content)} bytes")

        start_time = time.time()
        large_write_result = await fs.write_file(large_path, large_content, "overwrite")
        write_time = time.time() - start_time
        if large_write_result.success:
            print(f"  Large file written in {write_time:.2f}s")
        else:
            print(f"  Large write failed: {large_write_result.error_message}")

        start_time = time.time()
        large_read_result = await fs.read_file(large_path)
        read_time = time.time() - start_time
        if large_read_result.success:
            matches = large_read_result.content == large_content
            print(f"  Large file read in {read_time:.2f}s, content matches: {matches}")
        else:
            print(f"  Large read failed: {large_read_result.error_message}")

        # Step 12: Delete file and verify
        print("\n[Step 12] Deleting file and verifying...")
        delete_result = await fs.delete_file(moved_path)
        if delete_result.success:
            print(f"  File deleted: {moved_path}")
        else:
            print(f"  Delete failed: {delete_result.error_message}")

        info_after = await fs.get_file_info(moved_path)
        if not info_after.success:
            print("  File no longer exists (as expected)")
        else:
            print("  File still exists (unexpected)")

        print("\n=== File System Operations Example Completed ===")

    finally:
        await agent_bay.delete(session)
        print("Session deleted")


if __name__ == "__main__":
    asyncio.run(main())
