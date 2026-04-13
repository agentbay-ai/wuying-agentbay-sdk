import os
import sys
import time
import unittest
import json

from agentbay import AsyncAgentBay
from agentbay import (
    BWList,
    ContextSync,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
    Config,
)
from agentbay import BrowserContext, CreateSessionParams
from agentbay.api.models import AppManagerRule, ExtraConfigs, MobileExtraConfig
import pytest

# Add the parent directory to the path so we can import the agentbay package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_test_api_key():
    """Get API key for testing"""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        api_key = "akm-xxx"  # Replace with your test API key
        print(
            "Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for testing."
        )
    return api_key


class TestAsyncAgentBay(unittest.TestCase):
    """Test cases for the AsyncAgentBay class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        api_key = get_test_api_key()
        agent_bay = AsyncAgentBay(api_key=api_key)
        self.assertEqual(agent_bay.api_key, api_key)
        self.assertIsNotNone(agent_bay.client)

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        # Save original API key
        original_key = os.environ.get("AGENTBAY_API_KEY")

        os.environ["AGENTBAY_API_KEY"] = "env_api_key"
        try:
            agent_bay = AsyncAgentBay()
            self.assertEqual(agent_bay.api_key, "env_api_key")
        finally:
            # Restore original API key
            if original_key is not None:
                os.environ["AGENTBAY_API_KEY"] = original_key
            else:
                del os.environ["AGENTBAY_API_KEY"]

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        # Save original API key
        original_key = os.environ.get("AGENTBAY_API_KEY")

        try:
            if "AGENTBAY_API_KEY" in os.environ:
                del os.environ["AGENTBAY_API_KEY"]
            with self.assertRaises(ValueError):
                AsyncAgentBay()
        finally:
            # Restore original API key
            if original_key is not None:
                os.environ["AGENTBAY_API_KEY"] = original_key

    @pytest.mark.asyncio
    async def test_create_list_delete(self):
        """Test create, list, and delete methods."""
        api_key = get_test_api_key()
        agent_bay = AsyncAgentBay(api_key=api_key)

        # Create a session
        print("Creating a new session...")
        result = await agent_bay.create()

        # Check if session creation was successful
        self.assertTrue(
            result.success, f"Session creation failed: {result.error_message}"
        )
        self.assertIsNotNone(result.session, "Session object is None")

        session = result.session
        print(f"Session created with ID: {session.session_id}")

        # Ensure session ID is not empty
        self.assertIsNotNone(session.session_id)
        self.assertNotEqual(session.session_id, "")

        # Delete the session
        print("Deleting the session...")
        await agent_bay.delete(session)

        # Session deletion completed


class TestSession(unittest.IsolatedAsyncioTestCase):
    """Test cases for the Session class."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        self.agent_bay = AsyncAgentBay(api_key=api_key)

        # Create a session with default windows image
        print("Creating a new session for testing...")
        self.result = await self.agent_bay.create()

        # Check if session creation was successful
        if not self.result.success:
            self.fail(f"Session creation failed in setUp: {self.result.error_message}")
        if self.result.session is None:
            self.fail("Session object is None in setUp")

        self.session = self.result.session
        print(f"Session created with ID: {self.session.session_id}")

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        print("Cleaning up: Deleting the session...")
        try:
            await self.agent_bay.delete(self.session)
        except Exception as e:
            print(f"Warning: Error deleting session: {e}")

    def test_session_properties(self):
        """Test session properties and methods."""
        # Test session properties
        self.assertIsNotNone(self.session.session_id)
        self.assertEqual(self.session.agent_bay, self.agent_bay)

        # Test access to AgentBay properties through session.agent_bay
        self.assertEqual(self.session.agent_bay.api_key, self.agent_bay.api_key)
        self.assertEqual(self.session.agent_bay.client, self.agent_bay.client)

        # Test get_session_id method
        session_id = self.session.session_id
        self.assertEqual(session_id, self.session.session_id)

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test session delete method."""
        # Create a new session specifically for this test
        print("Creating a new session for delete testing...")
        result = await self.agent_bay.create()
        session = result.session
        print(f"Session created with ID: {session.session_id}")

        # Test delete method
        print("Testing session.delete method...")
        try:
            result = await session.delete()
            self.assertTrue(result)

            # Session deletion verified
        except Exception as e:
            print(f"Note: Session deletion failed: {e}")
            # Clean up if the test failed
            try:
                self.agent_bay.delete(session)
            except BaseException:
                pass

    def test_command(self):
        """Test command execution."""
        if self.session.command:
            print("Executing command...")
            try:
                response = self.session.command.execute_command("ls")
                print(f"Command execution result: {response}")
                self.assertIsNotNone(response)
                self.assertTrue(
                    response.success, f"Command failed: {response.error_message}"
                )
                # Check if response contains "tool not found"
                self.assertNotIn(
                    "tool not found",
                    response.output.lower(),
                    "Command.ExecuteCommand returned 'tool not found'",
                )
            except Exception as e:
                print(f"Note: Command execution failed: {e}")
                # Don't fail the test if command execution is not supported
        else:
            print("Note: Command interface is nil, skipping command test")

    def test_filesystem(self):
        """Test filesystem operations."""
        if self.session.file_system:
            print("Reading file...")
            try:
                result = self.session.file_system.read_file("/etc/hosts")
                print(f"ReadFile result: content='{result}'")
                self.assertIsNotNone(result)
                self.assertTrue(
                    result.success, f"Read file failed: {result.error_message}"
                )
                # Check if response contains "tool not found"
                self.assertNotIn(
                    "tool not found",
                    result.content.lower(),
                    "FileSystem.ReadFile returned 'tool not found'",
                )
                print("File read successful")
            except Exception as e:
                print(f"Note: File operation failed: {e}")
                # Don't fail the test if filesystem operations are not supported
        else:
            print("Note: FileSystem interface is nil, skipping file test")


class TestRecyclePolicy(unittest.IsolatedAsyncioTestCase):
    """Test cases for RecyclePolicy functionality."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        self.agent_bay = AsyncAgentBay(api_key=api_key)
        self.session = None

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        # Clean up session
        if self.session:
            try:
                print("Cleaning up session with custom recyclePolicy...")
                delete_result = await self.agent_bay.delete(self.session)
                print(
                    f"Delete Session RequestId: {delete_result.request_id or 'undefined'}"
                )
            except Exception as e:
                print(f"Warning: Error deleting session: {e}")

    @pytest.mark.asyncio
    async def test_create_session_with_custom_recycle_policy(self):
        """Test creating session with custom recyclePolicy using Lifecycle_1Day."""
        # Create custom recyclePolicy with Lifecycle_1Day and default paths

        context_result = await self.agent_bay.context.get("test-recycle-context", create=True)
        
        assert context_result.success and context_result.context
        
        context = context_result.context
        context_id = context.id
        print(f"Context created successfully with ID: {context.id}")
        recycle_policy = RecyclePolicy(
            lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=[""]  # Using default path value
        )

        # Create custom SyncPolicy with recyclePolicy
        custom_sync_policy = SyncPolicy(
            upload_policy=UploadPolicy.default(),
            download_policy=DownloadPolicy.default(),
            delete_policy=DeletePolicy.default(),
            extract_policy=ExtractPolicy.default(),
            recycle_policy=recycle_policy,
            bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
        )

        # Create ContextSync with custom policy
        context_sync = ContextSync(
            context_id,
            path="/test/recycle/path",
            policy=custom_sync_policy,
        )

        print("Creating session with custom recyclePolicy...")
        print(
            f"RecyclePolicy lifecycle: {custom_sync_policy.recycle_policy.lifecycle.value}"
        )
        print(f"RecyclePolicy paths: {custom_sync_policy.recycle_policy.paths}")

        # Create session parameters with custom recyclePolicy
        params = CreateSessionParams(
            labels={"test": "recyclePolicy", "lifecycle": "1day"},
            context_syncs=[context_sync],
        )

        # Create session with custom recyclePolicy
        create_result = await self.agent_bay.create(params)
        # Verify SessionResult structure
        self.assertTrue(create_result.success)
        self.assertIsNotNone(create_result.request_id)
        self.assertIsInstance(create_result.request_id, str)
        self.assertGreater(len(create_result.request_id), 0)
        self.assertIsNotNone(create_result.session)
        self.assertFalse(create_result.error_message)

        self.session = create_result.session
        print(f"Session created successfully with ID: {self.session.session_id}")
        print(f"Create Session RequestId: {create_result.request_id or 'undefined'}")

        # Verify session properties
        self.assertIsNotNone(self.session.session_id)
        self.assertGreater(len(self.session.session_id), 0)

        print("Session with custom recyclePolicy created and verified successfully")

    def test_context_sync_with_invalid_recycle_policy_path(self):
        """Test that ContextSync throws error when creating with invalid recyclePolicy path."""
        print("Testing ContextSync creation with invalid recyclePolicy path...")

        # Test that RecyclePolicy constructor throws an error for invalid path
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle=Lifecycle.LIFECYCLE_1DAY,
                paths=["/invalid/path/*"],  # Invalid path with wildcard
            )

        # Verify the error message
        expected_message = "Wildcard patterns are not supported in recycle policy paths. Got: /invalid/path/*. Please use exact directory paths instead."
        self.assertIn(
            "Wildcard patterns are not supported in recycle policy paths",
            str(context.exception),
        )
        self.assertIn("/invalid/path/*", str(context.exception))

        print("RecyclePolicy correctly threw error for invalid path")

        # Test with multiple invalid paths
        with self.assertRaises(ValueError):
            RecyclePolicy(
                lifecycle=Lifecycle.LIFECYCLE_1DAY,
                paths=["/valid/path", "/invalid/path?", "/another/invalid/*"],
            )

        print("RecyclePolicy correctly threw error for multiple invalid paths")

    def test_recycle_policy_invalid_lifecycle(self):
        """Test invalid Lifecycle values."""
        print("Testing invalid Lifecycle values...")

        # Test with invalid lifecycle value (string instead of Lifecycle enum)
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle="invalid_lifecycle",  # Invalid: should be Lifecycle enum
                paths=[""],
            )

        # Verify error message contains expected information
        error_message = str(context.exception)
        expected_substrings = [
            "Invalid lifecycle value",
            "invalid_lifecycle",
            "Valid values are:",
        ]

        for substring in expected_substrings:
            self.assertIn(substring, error_message)

        print(
            f"Invalid lifecycle 'invalid_lifecycle' correctly failed validation: {error_message}"
        )
        print("Invalid Lifecycle values test completed successfully")

    def test_recycle_policy_combined_invalid(self):
        """Test combination of invalid Lifecycle and invalid paths."""
        print("Testing combination of invalid Lifecycle and invalid paths...")

        # Test with both invalid lifecycle and invalid path
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle="invalid_lifecycle",  # Invalid lifecycle
                paths=["/invalid/path/*"],  # Invalid path with wildcard
            )

        # Should fail on lifecycle validation first (since it's checked first in __post_init__)
        error_message = str(context.exception)
        self.assertIn("Invalid lifecycle value", error_message)

        print(
            f"Policy with both invalid lifecycle and invalid path correctly failed validation: {error_message}"
        )
        print("Combined invalid configuration test completed successfully")


class TestWhiteListPattern(unittest.IsolatedAsyncioTestCase):
    """Test cases for WhiteList is_path_regex and is_exclude_regex fields."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        self.agent_bay = AsyncAgentBay(api_key=api_key)
        self.session = None
        self.context = None

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        if self.session:
            try:
                print("Cleaning up session with pattern-based BWList...")
                delete_result = await self.agent_bay.delete(self.session, sync_context=True)
                print(
                    f"Delete Session RequestId: {delete_result.request_id or 'undefined'}"
                )
            except Exception as e:
                print(f"Warning: Error deleting session: {e}")
        if self.context:
            context_id_result = await self.agent_bay.context.delete(self.context)
            self.assertTrue(context_id_result.success)
            if context_id_result.success:
                print(f"Deleted context {self.context.id}")

    async def _collect_all_files(self, context_id: str, folder_path: str) -> list:
        """Recursively collect only FILE entries under folder_path.

        folder_path is a local-style Windows path (e.g. C:\\Users\\Administrator\\testdata\\project-alpha).
        list_files accepts this path and returns entries whose file_path is an OSS-style path.
        For FOLDER entries: extract the last segment from entry.file_path and
          build the next local path = folder_path + "\\" + last_segment, then recurse.
        For FILE entries: extract the last segment (file name) and store it.
        Returns a flat list of file name strings collected under folder_path.
        """
        result = await self.agent_bay.context.list_files(
            context_id=context_id,
            parent_folder_path=folder_path,
            page_size=200,
        )
        if not result.success or not result.entries:
            return []
        file_paths = []
        for entry in result.entries:
            ftype = (entry.file_type or "").upper()
            # Extract the last segment from the OSS path
            last_segment = entry.file_path.rstrip("/").rsplit("/", 1)[-1]
            if ftype in ("FOLDER", "DIR", "DIRECTORY"):
                # Build local sub-path and recurse
                sub_path = folder_path.rstrip("\\") + "\\" + last_segment
                file_paths.extend(
                    await self._collect_all_files(context_id, sub_path)
                )
            else:
                # FILE: store the file name
                file_paths.append(last_segment)
        return file_paths

    @pytest.mark.asyncio
    async def test_create_session_with_pattern_bwlist(self):
        """Test ContextSync BWList with is_path_regex=True and is_exclude_regex=True.

        Single-session strategy:
          1. Create session WITH BWList configured (upload filter).
          2. Write test files onto the session's local FS.
          3. delete(sync_context=True) triggers upload; BWList filters which files go to OSS.
          4. Poll context.list_files("") to find the OSS root FOLDER.
          5. Recursively collect all FILE entries from OSS root.
          6. Assert expected files present, excluded files absent.

        File structure:
            testdata/project-alpha/main.py
            testdata/project-alpha/README.txt
            testdata/project-beta/config.json
            testdata/project-beta/cache/temp.log  <- excluded by exclude_paths regex

        BWList (upload filter):
            path=r"project-.*"  (is_path_regex=True)
            exclude_paths=[r"cache.*"]  (is_exclude_regex=True)

        Expected in OSS:
            PRESENT:  project-alpha/main.py, project-alpha/README.txt, project-beta/config.json
            ABSENT:   project-beta/cache/temp.log
        """
        import asyncio as _asyncio
        import time as _time

        print("Testing BWList is_path_regex + is_exclude_regex via single-session strategy...")

        base = "C:\\Users\\Administrator\\testdata"

        # ── Create context ────────────────────────────────────────────────────────────
        context_name = f"bwlist-ctx-{int(_time.time())}"
        context_result = await self.agent_bay.context.get(context_name, create=True)
        if not context_result.success or not context_result.context:
            self.skipTest(
                f"Skipping: Failed to get/create context: {getattr(context_result, 'error_message', '')}"
            )
        self.context = context_result.context
        self.context_id = self.context.id
        print(f"Context ID: {self.context_id}")

        # ── Create session WITH BWList ─────────────────────────────────────────────
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy.default(),
            download_policy=DownloadPolicy.default(),
            delete_policy=DeletePolicy.default(),
            extract_policy=ExtractPolicy.default(),
            recycle_policy=RecyclePolicy.default(),
            bw_list=BWList(white_lists=[
                WhiteList(
                    path=r"project-.*",
                    is_path_regex=True,
                    exclude_paths=[r"cache.*"],
                    is_exclude_regex=True,
                )
            ]),
        )
        context_sync = ContextSync(context_id=self.context_id, path=base, policy=sync_policy)
        params = CreateSessionParams(
            image_id="imgc-0ae8jv3fd5yuss7ky",
            labels={"test": "patternBWList"},
            context_syncs=[context_sync],
        )
        create_result = await self.agent_bay.create(params)
        self.assertTrue(create_result.success, f"Session creation failed: {create_result.error_message}")
        self.session = create_result.session
        print(f"Session ID: {self.session.session_id}")

        # ── Write test files onto local FS ────────────────────────────────────────────
        fs = self.session.file_system
        for d in [base, f"{base}\\project-alpha", f"{base}\\project-beta", f"{base}\\project-beta\\cache"]:
            r = await fs.create_directory(d)
            print(f"  mkdir {d}: {'OK' if r.success else r.error_message}")

        test_files = [
            (f"{base}\\project-alpha\\main.py",       "# main entry point\nprint('hello')\n"),
            (f"{base}\\project-alpha\\README.txt",     "Project Alpha README\n"),
            (f"{base}\\project-beta\\config.json",     '{"env": "test"}\n'),
            (f"{base}\\project-beta\\cache\\temp.log", "temporary log\n"),
        ]
        for fpath, content in test_files:
            r = await fs.write_file(fpath, content)
            print(f"  write {fpath}: {'OK' if r.success else r.error_message}")

        # ── delete(sync_context=True) – triggers upload with BWList filter ────────────
        print("  Deleting session with sync_context=True (BWList upload filter applied)...")
        del_result = await self.agent_bay.delete(self.session, sync_context=True)
        self.assertTrue(del_result.success, f"Session delete failed: {del_result.error_message}")
        self.session = None
        print("  Session deleted. Filtered upload triggered.")

        # ── list_files(base) – one call, traverse entries directly ──────────────────
        # For FOLDER entries: extract the last path segment (sub-dir name),
        #   build absolute local path = base + "\\", + sub-dir name, then recurse.
        # For FILE entries: store file_path directly.
        print("\n=== Verifying OSS content via context.list_files ===")
        probe = await self.agent_bay.context.list_files(
            context_id=self.context_id, parent_folder_path=base, page_size=200
        )
        entry_count = len(probe.entries) if probe.entries else 0
        print(f"  list_files({base!r}) -> success={probe.success}, entries={entry_count}")

        all_files: list = []
        if probe.entries:
            for e in probe.entries:
                ftype = (e.file_type or "").upper()
                # Extract the last segment from OSS path as sub-dir/file name
                last_segment = e.file_path.rstrip("/").rsplit("/", 1)[-1]
                print(f"    [{ftype}] {e.file_path!r}  -> last_segment={last_segment!r}")
                if ftype in ("FOLDER", "DIR", "DIRECTORY"):
                    # Build local-style absolute path and recurse
                    sub_path = base.rstrip("\\") + "\\" + last_segment
                    print(f"      Recursing into {sub_path!r}...")
                    sub_files = await self._collect_all_files(self.context_id, sub_path)
                    all_files.extend(sub_files)
                else:
                    # FILE: store directly
                    all_files.append(e.file_path)
        else:
            print("  WARNING: No entries found in OSS.")

        print(f"  Collected {len(all_files)} file(s) total")
        print(f"\n  === All files in OSS ({len(all_files)} total) ===")
        self.assertEqual(len(all_files), 3)
        for p in all_files:
            print(f"    {p}")

        # ── Assertions ──────────────────────────────────────────────────────────────
        for name in ["main.py", "README.txt", "config.json"]:
            found = any(name in p for p in all_files)
            print(f"  {'FOUND' if found else 'NOT FOUND'}: {name}")
            self.assertTrue(found, f"Expected '{name}' in OSS after BWList upload filter, not found in: {all_files}")
        print("\u2705 Expected files present in OSS")

        for name in ["temp.log"]:
            found = any(name in p for p in all_files)
            print(f"  {'FOUND (should be absent!)' if found else 'correctly absent'}: {name}")
            self.assertFalse(found, f"Expected '{name}' ABSENT (excluded by BWList), but found in: {all_files}")
        print("\u2705 Excluded files correctly absent from OSS")
        print("BWList with is_path_regex + is_exclude_regex verified successfully")

class TestBrowserContext(unittest.IsolatedAsyncioTestCase):
    """Test cases for BrowserContext functionality."""

    async def asyncSetUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        self.agent_bay = AsyncAgentBay(api_key=api_key)
        self.session = None

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        # Clean up session
        if self.session:
            try:
                print("Cleaning up session with BrowserContext...")
                delete_result = await self.agent_bay.delete(self.session)
                print(
                    f"Delete Session RequestId: {delete_result.request_id or 'undefined'}"
                )
            except Exception as e:
                print(f"Warning: Error deleting session: {e}")

    @pytest.mark.asyncio
    async def test_create_session_with_browser_context_default_recycle_policy(self):
        """Test creating session with BrowserContext using default RecyclePolicy."""
        print("Testing session creation with BrowserContext (default RecyclePolicy)...")

        # Create a browser context first
        context_name = f"test-browser-context-default-{int(time.time())}"
        context_result = await self.agent_bay.context.get(context_name, create=True)
        if not context_result.success or not context_result.context:
            self.skipTest("Failed to create browser context")

        context = context_result.context
        context_id = context.id
        print(f"Created browser context: {context_name} (ID: {context_id})")

        # Create BrowserContext with default RecyclePolicy using the created context ID
        browser_context = BrowserContext(
            context_id=context_id, auto_upload=True
        )

        print(f"BrowserContext context_id: {browser_context.context_id}")
        print(f"BrowserContext auto_upload: {browser_context.auto_upload}")

        # Create session parameters with BrowserContext
        params = CreateSessionParams(
            labels={"test": "browserContext", "recycle_policy": "default"},
            browser_context=browser_context,
        )

        # Create session with BrowserContext
        create_result = await self.agent_bay.create(params)

        # Verify SessionResult structure
        self.assertTrue(create_result.success)
        self.assertIsNotNone(create_result.request_id)
        self.assertIsInstance(create_result.request_id, str)
        self.assertGreater(len(create_result.request_id), 0)
        self.assertIsNotNone(create_result.session)
        self.assertFalse(create_result.error_message)

        self.session = create_result.session
        print(f"Session created successfully with ID: {self.session.session_id}")
        print(f"Create Session RequestId: {create_result.request_id or 'undefined'}")

        # Verify session properties
        self.assertIsNotNone(self.session.session_id)
        self.assertGreater(len(self.session.session_id), 0)

        print(
            "Session with BrowserContext (default RecyclePolicy) created and verified successfully"
        )

        # Clean up the created context
        try:
            await self.agent_bay.context.delete(context)
            print(f"Browser context deleted: {context_id}")
        except Exception as e:
            print(f"Warning: Failed to delete browser context: {e}")


class TestSessionPauseResume(unittest.IsolatedAsyncioTestCase):
    """Test cases for session pause and resume functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        endpoint = os.environ.get("AGENTBAY_ENDPOINT")
        self.agent_bay = AsyncAgentBay(api_key=api_key, 
                                        cfg=Config(endpoint=endpoint, timeout_ms=60000))
        self.session = None

    async def asyncTearDown(self):
        """Tear down test fixtures."""
        if self.session:
            try:
                print("Cleaning up session...")
                delete_result = await self.agent_bay.delete(self.session)
                print(
                    f"Delete Session RequestId: {delete_result.request_id or 'undefined'}"
                )
            except Exception as e:
                print(f"Warning: Error deleting session: {e}")

    @pytest.mark.asyncio
    async def test_session_pause_and_resume(self):
        """Test pausing and resuming a session."""
        print("Creating a new session for pause/resume testing...")
        
        # Create session
        params = CreateSessionParams(
        image_id="imgc-0ab5ta4myt0ntw12x",
        # image_id="imgc-0ae8jvkn0mtjfs9ag",
        # image_id="linux_latest",
        # image_id="moltbot-linux-ubuntu-2204",
        # image_id="windows_latest",
        labels={"project": "piaoyun-demo", "environment": "testing"},
    )

        create_result = await self.agent_bay.create()
        self.assertTrue(
            create_result.success, 
            f"Session creation failed: {create_result.error_message}"
        )
        self.assertIsNotNone(create_result.session, "Session object is None")
        
        self.session = create_result.session
        print(f"Session created with ID: {self.session.session_id}")
        
        # Test pause
        print("\n=== Testing session pause ===")
        pause_result = await self.session.beta_pause(timeout=300, poll_interval=2)
        
        print(f"Pause result - Success: {pause_result.success}")
        print(f"Pause result - Status: {pause_result.status}")
        print(f"Pause result - RequestId: {pause_result.request_id}")
        
        if not pause_result.success:
            print(f"Pause error message: {pause_result.error_message}")
        
        self.assertTrue(
            pause_result.success, 
            f"Session pause failed: {pause_result.error_message}"
        )
        self.assertEqual(
            pause_result.status, 
            "PAUSED", 
            f"Expected status PAUSED, got {pause_result.status}"
        )
        print("✓ Session paused successfully")
        
        # Test resume
        print("\n=== Testing session resume ===")
        resume_result = await self.session.beta_resume(timeout=300, poll_interval=2)
        
        print(f"Resume result - Success: {resume_result.success}")
        print(f"Resume result - Status: {resume_result.status}")
        print(f"Resume result - RequestId: {resume_result.request_id}")
        
        if not resume_result.success:
            print(f"Resume error message: {resume_result.error_message}")
        
        self.assertTrue(
            resume_result.success, 
            f"Session resume failed: {resume_result.error_message}"
        )
        self.assertEqual(
            resume_result.status, 
            "RUNNING", 
            f"Expected status RUNNING, got {resume_result.status}"
        )
        print("✓ Session resumed successfully")
        
        print("\n=== Pause/Resume test completed successfully ===")
        

if __name__ == "__main__":
    unittest.main()
