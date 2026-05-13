#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - Context File Operations & Lifecycle Management Example

This example demonstrates comprehensive file management within contexts:
- Uploading files using presigned URLs
- Downloading files using presigned URLs
- Listing files in a context with storage statistics
- Content verification between uploaded and downloaded files
- Data lifecycle management with cleanup strategies
- Selective and batch file deletion
- Error handling and edge cases

Business Scenario:
An application uses Context storage for various file types with different lifecycle requirements:
- Temporary files (temp/): Processing files, cleaned after 1 hour
- Cache files (cache/): API responses, cleaned when > 100MB or > 7 days old
- Log files (logs/): Application logs, kept for 30 days
- Important data (data/): User data, permanently retained
"""

import asyncio
import os
import shutil
import tempfile
import time
import httpx
from datetime import datetime
from typing import Dict, List
from agentbay import AsyncAgentBay


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


async def upload_file_to_context(
    agentbay: AsyncAgentBay,
    context_id: str,
    file_path: str,
    content: str
) -> bool:
    """Upload a file to Context storage using presigned URL"""
    try:
        url_result = await agentbay.context.get_file_upload_url(context_id, file_path)
        if not url_result.success:
            print(f"  ✗ Failed to get upload URL for {file_path}: {url_result.error_message}")
            return False

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url_result.url,
                content=content.encode('utf-8'),
                timeout=30.0
            )

            if response.status_code in (200, 201, 204):
                return True
            else:
                print(f"  ✗ Upload failed with status {response.status_code}")
                return False

    except Exception as e:
        print(f"  ✗ Error uploading {file_path}: {e}")
        return False


async def download_file_from_context(
    agentbay: AsyncAgentBay,
    context_id: str,
    file_path: str,
    download_dir: str
) -> str | None:
    """Download a file from Context storage using presigned URL.
    Returns the local download path on success, or None on failure.
    """
    try:
        url_result = await agentbay.context.get_file_download_url(context_id, file_path)
        if not url_result.success:
            print(f"  ✗ Failed to get download URL for {file_path}: {url_result.error_message}")
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(url_result.url, timeout=30.0)
            if response.status_code == 200:
                file_name = file_path.rsplit('/', 1)[-1]
                download_path = os.path.join(download_dir, file_name)
                with open(download_path, 'wb') as f:
                    f.write(response.content)
                return download_path
            else:
                print(f"  ✗ Download failed for {file_path}: HTTP {response.status_code}")
                return None

    except Exception as e:
        print(f"  ✗ Error downloading {file_path}: {e}")
        return None


def normalize_content(text: str) -> str:
    """Normalize text for comparison: strip trailing whitespace per line
    and collapse consecutive blank lines, to tolerate server-side
    newline insertion on download.
    """
    return "\n".join(l.rstrip() for l in text.splitlines() if l.strip())


async def file_operations_and_lifecycle_demonstration():
    """Complete file operations and lifecycle management demonstration"""

    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agentbay = AsyncAgentBay(api_key=api_key)
    context = None
    download_dir = None

    try:
        print("=" * 60)
        print("Context File Operations & Lifecycle Management Example")
        print("=" * 60)

        # Step 1: Create a working Context
        print("\n[Step 1] Creating working Context...")
        context_name = f"file-lifecycle-demo-{int(datetime.now().timestamp())}"
        create_result = await agentbay.context.create(context_name)

        if not create_result.success:
            print(f"Failed to create Context: {create_result.error_message}")
            return

        context = create_result.context
        context_id = create_result.context_id
        print(f"✓ Context created: {context_id}")

        # Step 2: Upload different types of files
        print("\n[Step 2] Uploading files to Context...")

        files_to_upload = [
            # Temporary files
            ("/temp/processing_job_1.tmp", f"Temporary processing data\nCreated: {datetime.now()}", "temporary"),
            ("/temp/processing_job_2.tmp", f"Another temp file\nCreated: {datetime.now()}", "temporary"),

            # Cache files
            ("/cache/api_response_1.json", '{"data": "API response 1", "cached_at": "2024-11-20"}', "cache"),
            ("/cache/api_response_2.json", '{"data": "API response 2", "cached_at": "2024-11-25"}', "cache"),
            ("/cache/api_response_3.json", '{"data": "Large API response 3" * 1000}', "cache"),

            # Log files
            ("/logs/app.log", f"Application log\n{datetime.now()}: System started\n{datetime.now()}: Processing request", "logs"),
            ("/logs/error.log", f"Error log\n{datetime.now()}: Minor error occurred", "logs"),

            # Important data
            ("/data/user_profile.json", '{"user_id": 123, "name": "Test User", "email": "test@example.com"}', "data"),
            ("/data/user_settings.json", '{"theme": "dark", "language": "en"}', "data"),
        ]

        # Store content for later verification
        uploaded_content: Dict[str, str] = {}
        uploaded_count = 0
        for file_path, content, file_type in files_to_upload:
            success = await upload_file_to_context(agentbay, context_id, file_path, content)
            if success:
                uploaded_content[file_path] = content
                print(f"  ✓ Uploaded: {file_path} ({file_type})")
                uploaded_count += 1
            await asyncio.sleep(0.1)  # Small delay to avoid rate limiting

        print(f"\n✓ Successfully uploaded {uploaded_count}/{len(files_to_upload)} files")

        # Step 3: Wait for files to be indexed
        print("\n[Step 3] Waiting for files to be indexed...")
        files_check = ["/temp", "/cache", "/data", "/logs"]
        all_files: List = []
        for folder_path in files_check:
            await asyncio.sleep(3)
            list_result = await agentbay.context.list_files(context_id, folder_path)
            if list_result.success and len(list_result.entries) > 0:
                all_files.extend(list_result.entries)
                print(f"  ✓ Found {len(list_result.entries)} files in {folder_path}")

        if len(all_files) == len(files_to_upload):
            print(f"✓ All {len(all_files)} files indexed successfully")
        else:
            print(f"⚠ Found {len(all_files)}/{len(files_to_upload)} files (may need more time to index)")

        # Step 4: File listing and initial storage statistics
        print("\n[Step 4] Initial Storage Statistics")
        print("=" * 60)
        total_size = sum(entry.size or 0 for entry in all_files)

        print(f"Total Files: {len(all_files)}")
        print(f"Total Size: {format_size(total_size)}")
        print(f"\nFiles by Type:")

        by_type: Dict[str, List] = {}
        for entry in all_files:
            # Path like "/temp/file.tmp" -> split gives ['', 'temp', 'file.tmp'] -> [1] = 'temp'
            parts = entry.file_path.split('/')
            file_type = parts[1] if len(parts) >= 2 else 'root'
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(entry)

        for file_type, entries in sorted(by_type.items()):
            type_size = sum(e.size or 0 for e in entries)
            print(f"  {file_type:10s}: {len(entries):2d} files, {format_size(type_size):>10s}")

        # Step 5: File download operations
        print("\n[Step 5] Downloading files from Context...")
        download_dir = tempfile.mkdtemp(prefix="agentbay_downloads_")
        downloaded_files: Dict[str, str] = {}
        download_count = 0

        for file_path in uploaded_content:
            local_path = await download_file_from_context(agentbay, context_id, file_path, download_dir)
            if local_path:
                downloaded_files[file_path] = local_path
                download_count += 1
                print(f"  ✓ Downloaded: {file_path}")

        print(f"\n✓ Downloaded {download_count}/{len(uploaded_content)} files")

        # Step 6: Content verification
        print("\n[Step 6] Verifying downloaded content...")
        verified = 0

        for file_path, original_content in uploaded_content.items():
            if file_path not in downloaded_files:
                print(f"  ⚠ Skipped (not downloaded): {file_path}")
                continue

            with open(downloaded_files[file_path], 'r', encoding='utf-8') as f:
                dl_content = f.read()

            if normalize_content(original_content) == normalize_content(dl_content):
                verified += 1
                print(f"  ✓ Verified: {file_path}")
            else:
                print(f"  ✗ Mismatch: {file_path}")

        print(f"\n✓ Content verification: {verified}/{len(uploaded_content)} files verified")

        # Step 7: Apply cleanup strategies
        print("\n[Step 7] Applying Cleanup Strategies...")
        files_to_delete = []

        # Strategy 1: Time-based cleanup (simulate old temporary files)
        print("\n  Strategy 1: Time-based cleanup")
        temp_files = [f for f in all_files if f.file_path.startswith('/temp/')]
        for file in temp_files:
            if 'job_1' in file.file_path:
                files_to_delete.append(file)
                print(f"    → {file.file_path}: Temporary file (simulated old)")

        # Strategy 2: Clean old cache files
        cache_files = [f for f in all_files if f.file_path.startswith('/cache/')]
        for file in cache_files:
            if 'response_1' in file.file_path or 'response_3' in file.file_path:
                files_to_delete.append(file)
                print(f"    → {file.file_path}: Old cache file (simulated)")

        # Strategy 3: Protect important data
        print("\n  Strategy 2: Type-based protection")
        data_files = [f for f in all_files if f.file_path.startswith('/data/')]
        print(f"    ✓ Protecting {len(data_files)} important data files from cleanup")

        # Step 8: Execute cleanup
        print("\n[Step 8] Executing Cleanup...")
        deleted_count = 0

        for file in files_to_delete:
            delete_result = await agentbay.context.delete_file(context_id, file.file_path)
            if delete_result.success:
                print(f"  ✓ Deleted: {file.file_path}")
                deleted_count += 1
            else:
                print(f"  ✗ Failed to delete: {file.file_path}")
            await asyncio.sleep(0.1)

        print(f"\n✓ Cleanup completed: {deleted_count} files removed")

        # Small delay to ensure deletions are processed
        await asyncio.sleep(2)

        # Step 9: Post-cleanup statistics
        print("\n[Step 9] Post-Cleanup Storage Statistics")
        print("=" * 60)

        final_all_files: List = []
        for folder_path in files_check:
            list_result = await agentbay.context.list_files(context_id, folder_path)
            if list_result.success and list_result.entries:
                final_all_files.extend(list_result.entries)

        final_total_size = sum(entry.size or 0 for entry in final_all_files)

        print(f"Total Files: {len(final_all_files)}")
        print(f"Total Size: {format_size(final_total_size)}")

        # Step 10: Cleanup impact analysis
        print("\n[Step 10] Cleanup Impact Analysis")
        print("=" * 60)

        space_saved = total_size - final_total_size
        files_removed = len(all_files) - len(final_all_files)

        print(f"Files Removed: {files_removed}")
        print(f"Space Saved: {format_size(space_saved)}")
        if total_size > 0:
            reduction_pct = (space_saved / total_size * 100)
            print(f"Space Reduction: {reduction_pct:.1f}%")

        print(f"\nRemaining Files:")
        for entry in final_all_files:
            size_str = format_size(entry.size or 0)
            print(f"  - {entry.file_path:40s} {size_str:>10s}")

        # Step 11: Error handling examples
        print("\n[Step 11] Error Handling Examples")
        print("=" * 60)

        # Test 1: Invalid context ID
        print("\n  Test 1: Invalid context ID")
        try:
            result = await agentbay.context.get_file_upload_url("invalid-context-id", "/test.txt")
            if not result.success:
                print(f"  ✓ Correctly rejected invalid context ID")
            else:
                print(f"  ⚠ Invalid context ID was accepted (unexpected)")
        except Exception as e:
            print(f"  ✓ Exception caught for invalid context ID: {str(e)[:50]}...")

        # Test 2: Non-existent file download
        print("\n  Test 2: Non-existent file download")
        try:
            result = await agentbay.context.get_file_download_url(context_id, "/nonexistent.txt")
            if not result.success:
                print(f"  ✓ Correctly rejected non-existent file")
            else:
                print(f"  ⚠ Non-existent file was accepted (unexpected)")
        except Exception as e:
            print(f"  ✓ Exception for non-existent file: {str(e)[:50]}...")

        # Test 3: Delete non-existent file
        print("\n  Test 3: Delete non-existent file")
        try:
            delete_result = await agentbay.context.delete_file(context_id, "/nonexistent.txt")
            if not delete_result.success:
                print(f"  ✓ Correctly failed to delete non-existent file")
            else:
                print(f"  ⚠ Non-existent file deletion unexpectedly succeeded")
        except Exception as e:
            print(f"  ✓ Exception for non-existent file deletion: {str(e)[:50]}...")

        # Step 12: Best practices summary
        print("\n[Step 12] Best Practices Summary")
        print("=" * 60)
        print("✓ Upload files with organized directory structure")
        print("✓ Download and verify file contents after upload")
        print("✓ Monitor storage usage regularly with list_files API")
        print("✓ Implement cleanup policies based on file type and age")
        print("✓ Protect critical data from automatic cleanup")
        print("✓ Use delete_file API to remove obsolete data")
        print("✓ Handle errors gracefully for invalid operations")
        print("✓ Verify cleanup impact before and after operations")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        # Cleanup: Delete the test Context
        if context:
            print(f"\n[Cleanup] Deleting test Context...")
            try:
                delete_result = await agentbay.context.delete(context)
                if delete_result.success:
                    print(f"✓ Context deleted: {context.id}")
                else:
                    print(f"⚠ Failed to delete Context: {delete_result.error_message}")
            except Exception as e:
                print(f"⚠ Error deleting Context: {e}")

        # Clean up download directory
        if download_dir and os.path.exists(download_dir):
            try:
                shutil.rmtree(download_dir)
            except Exception:
                pass

        print("\n" + "=" * 60)
        print("Context File Operations & Lifecycle Management Example Completed")
        print("=" * 60)


async def main():
    """Run the file operations and lifecycle management demonstration"""
    await file_operations_and_lifecycle_demonstration()


if __name__ == "__main__":
    asyncio.run(main())

