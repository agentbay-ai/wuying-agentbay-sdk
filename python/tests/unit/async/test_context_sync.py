#!/usr/bin/env python3
"""
Unit tests for context_sync module.
"""

import unittest
import pytest

import copy

from agentbay import (
    BWList,
    ContextSync,
    DeletePolicy,
    DownloadPolicy,
    DownloadStrategy,
    MappingPolicy,
    SyncPolicy,
    UploadMode,
    UploadPolicy,
    UploadStrategy,
    WhiteList,
)


class TestAsyncSyncPolicy(unittest.IsolatedAsyncioTestCase):
    """Test SyncPolicy class functionality."""

    @pytest.mark.asyncio


    async def test_sync_policy_with_partial_parameters(self):
        """Test that SyncPolicy automatically fills missing parameters with defaults."""
        # Create SyncPolicy with only upload_policy
        upload_policy = UploadPolicy(auto_upload=False)
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        # Verify upload_policy is set correctly
        self.assertEqual(sync_policy.upload_policy.auto_upload, False)

        # Verify other policies are filled with defaults
        self.assertIsNotNone(sync_policy.download_policy)
        self.assertIsNotNone(sync_policy.delete_policy)
        self.assertIsNotNone(sync_policy.bw_list)

        # Verify default values
        self.assertTrue(sync_policy.download_policy.auto_download)
        self.assertEqual(
            sync_policy.download_policy.download_strategy,
            DownloadStrategy.DOWNLOAD_ASYNC,
        )
        self.assertTrue(sync_policy.delete_policy.sync_local_file)
        self.assertEqual(len(sync_policy.bw_list.white_lists), 1)

    @pytest.mark.asyncio


    async def test_sync_policy_with_no_parameters(self):
        """Test that SyncPolicy with no parameters uses all defaults."""
        sync_policy = SyncPolicy()

        # Verify all policies are set with defaults
        self.assertIsNotNone(sync_policy.upload_policy)
        self.assertIsNotNone(sync_policy.download_policy)
        self.assertIsNotNone(sync_policy.delete_policy)
        self.assertIsNotNone(sync_policy.bw_list)

        # Verify default values
        self.assertTrue(sync_policy.upload_policy.auto_upload)
        self.assertEqual(
            sync_policy.upload_policy.upload_strategy,
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        )

        self.assertTrue(sync_policy.download_policy.auto_download)
        self.assertEqual(
            sync_policy.download_policy.download_strategy,
            DownloadStrategy.DOWNLOAD_ASYNC,
        )

        self.assertTrue(sync_policy.delete_policy.sync_local_file)

        self.assertEqual(len(sync_policy.bw_list.white_lists), 1)
        self.assertEqual(sync_policy.bw_list.white_lists[0].path, "")
        self.assertEqual(sync_policy.bw_list.white_lists[0].exclude_paths, [])

    @pytest.mark.asyncio


    async def test_sync_policy_with_all_parameters(self):
        """Test that SyncPolicy with all parameters works correctly."""
        upload_policy = UploadPolicy(auto_upload=False)
        download_policy = DownloadPolicy(auto_download=False)
        delete_policy = DeletePolicy(sync_local_file=False)
        bw_list = BWList(
            white_lists=[WhiteList(path="/test", exclude_paths=["/exclude"])]
        )

        sync_policy = SyncPolicy(
            upload_policy=upload_policy,
            download_policy=download_policy,
            delete_policy=delete_policy,
            bw_list=bw_list,
        )

        # Verify all policies are set correctly
        self.assertEqual(sync_policy.upload_policy.auto_upload, False)

        self.assertEqual(sync_policy.download_policy.auto_download, False)
        self.assertEqual(sync_policy.delete_policy.sync_local_file, False)

        self.assertEqual(len(sync_policy.bw_list.white_lists), 1)
        self.assertEqual(sync_policy.bw_list.white_lists[0].path, "/test")
        self.assertEqual(sync_policy.bw_list.white_lists[0].exclude_paths, ["/exclude"])

    @pytest.mark.asyncio


    async def test_sync_policy_serialization(self):
        """Test that SyncPolicy serializes correctly with all policies present."""
        sync_policy = SyncPolicy(upload_policy=UploadPolicy(auto_upload=False))

        # Serialize to dict
        result = sync_policy.__dict__()

        # Verify all policies are present in serialization
        self.assertIn("uploadPolicy", result)
        self.assertIn("downloadPolicy", result)
        self.assertIn("deletePolicy", result)
        self.assertIn("bwList", result)

        # Verify upload policy values
        self.assertEqual(result["uploadPolicy"]["autoUpload"], False)
        self.assertEqual(
            result["uploadPolicy"]["uploadStrategy"],
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE.value,
        )

        # Verify download policy values
        self.assertEqual(result["downloadPolicy"]["autoDownload"], True)
        self.assertEqual(
            result["downloadPolicy"]["downloadStrategy"],
            DownloadStrategy.DOWNLOAD_ASYNC.value,
        )

        # Verify delete policy values
        self.assertEqual(result["deletePolicy"]["syncLocalFile"], True)

        # Verify bw list values
        self.assertEqual(len(result["bwList"]["whiteLists"]), 1)
        self.assertEqual(result["bwList"]["whiteLists"][0]["path"], "")
        self.assertEqual(result["bwList"]["whiteLists"][0]["excludePaths"], [])


class TestAsyncMappingPolicy(unittest.IsolatedAsyncioTestCase):
    """Test MappingPolicy class functionality."""

    @pytest.mark.asyncio


    async def test_mapping_policy_default(self):
        """Test that MappingPolicy can be created with default values."""
        mapping_policy = MappingPolicy()
        self.assertEqual(mapping_policy.path, "")

    @pytest.mark.asyncio


    async def test_mapping_policy_with_path(self):
        """Test that MappingPolicy can be created with a Windows path."""
        windows_path = "c:\\Users\\Administrator\\Downloads"
        mapping_policy = MappingPolicy(path=windows_path)
        self.assertEqual(mapping_policy.path, windows_path)

    @pytest.mark.asyncio


    async def test_mapping_policy_serialization(self):
        """Test that MappingPolicy serializes correctly."""
        windows_path = "c:\\Users\\Administrator\\Downloads"
        mapping_policy = MappingPolicy(path=windows_path)

        result = mapping_policy.__dict__()
        self.assertIn("path", result)
        self.assertEqual(result["path"], windows_path)


class TestAsyncSyncPolicyWithMappingPolicy(unittest.IsolatedAsyncioTestCase):
    """Test SyncPolicy with MappingPolicy functionality."""

    @pytest.mark.asyncio


    async def test_sync_policy_with_mapping_policy(self):
        """Test that SyncPolicy can include MappingPolicy."""
        windows_path = "c:\\Users\\Administrator\\Downloads"
        mapping_policy = MappingPolicy(path=windows_path)

        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(),
            download_policy=DownloadPolicy(),
            delete_policy=DeletePolicy(),
            mapping_policy=mapping_policy,
        )

        self.assertIsNotNone(sync_policy.mapping_policy)
        self.assertEqual(sync_policy.mapping_policy.path, windows_path)

    @pytest.mark.asyncio


    async def test_sync_policy_serialization_with_mapping_policy(self):
        """Test that SyncPolicy with MappingPolicy serializes correctly."""
        windows_path = "c:\\Users\\Administrator\\Downloads"
        mapping_policy = MappingPolicy(path=windows_path)

        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(), mapping_policy=mapping_policy
        )

        result = sync_policy.__dict__()
        self.assertIn("mappingPolicy", result)
        self.assertEqual(result["mappingPolicy"]["path"], windows_path)


class TestAsyncContextSyncWithMappingPolicy(unittest.IsolatedAsyncioTestCase):
    """Test ContextSync with MappingPolicy functionality."""

    @pytest.mark.asyncio


    async def test_context_sync_with_mapping_policy(self):
        """Test that ContextSync can be created with MappingPolicy."""
        context_id = "ctx-12345"
        linux_path = "/home/wuying/下载"
        windows_path = "c:\\Users\\Administrator\\Downloads"

        mapping_policy = MappingPolicy(path=windows_path)
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(),
            download_policy=DownloadPolicy(),
            delete_policy=DeletePolicy(),
            mapping_policy=mapping_policy,
        )

        context_sync = ContextSync.new(context_id, linux_path, sync_policy)

        self.assertEqual(context_sync.context_id, context_id)
        self.assertEqual(context_sync.path, linux_path)
        self.assertIsNotNone(context_sync.policy)
        self.assertIsNotNone(context_sync.policy.mapping_policy)
        self.assertEqual(context_sync.policy.mapping_policy.path, windows_path)


class TestAsyncUploadPolicyArchiveExcludePaths(unittest.IsolatedAsyncioTestCase):
    """Test UploadPolicy.archive_exclude_paths functionality."""

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_serialization(self):
        """Test that archive_exclude_paths serializes to camelCase archiveExcludePaths."""
        policy = UploadPolicy(
            upload_mode=UploadMode.ARCHIVE,
            archive_exclude_paths=["AGENTS.md", "chats.json", "sessions"],
        )
        result = policy.__dict__()
        self.assertIn("archiveExcludePaths", result)
        self.assertEqual(
            result["archiveExcludePaths"],
            ["AGENTS.md", "chats.json", "sessions"],
        )
        self.assertEqual(result["uploadMode"], "Archive")

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_empty_omitted(self):
        """Test that empty archive_exclude_paths is not included in serialization."""
        policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        result = policy.__dict__()
        self.assertNotIn("archiveExcludePaths", result)

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_not_in_file_mode(self):
        """Test that archive_exclude_paths is omitted when upload_mode is FILE."""
        policy = UploadPolicy(
            upload_mode=UploadMode.FILE,
            archive_exclude_paths=["AGENTS.md"],
        )
        result = policy.__dict__()
        self.assertNotIn("archiveExcludePaths", result)

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_default(self):
        """Test that archive_exclude_paths defaults to empty list."""
        policy = UploadPolicy()
        self.assertEqual(policy.archive_exclude_paths, [])

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_in_sync_policy(self):
        """Test that archive_exclude_paths survives full SyncPolicy serialization."""
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(
                upload_mode=UploadMode.ARCHIVE,
                archive_exclude_paths=["config.json", "env.json"],
            )
        )
        result = sync_policy.__dict__()
        upload = result["uploadPolicy"]
        self.assertIn("archiveExcludePaths", upload)
        self.assertEqual(upload["archiveExcludePaths"], ["config.json", "env.json"])

    @pytest.mark.asyncio
    async def test_archive_exclude_paths_deepcopy(self):
        """Test that archive_exclude_paths is preserved through deepcopy."""
        original = UploadPolicy(
            upload_mode=UploadMode.ARCHIVE,
            archive_exclude_paths=["a.txt", "b.txt"],
        )
        copied = copy.deepcopy(original)
        self.assertEqual(copied.archive_exclude_paths, ["a.txt", "b.txt"])
        copied.archive_exclude_paths.append("c.txt")
        self.assertEqual(original.archive_exclude_paths, ["a.txt", "b.txt"])
        self.assertEqual(copied.archive_exclude_paths, ["a.txt", "b.txt", "c.txt"])


if __name__ == "__main__":
    unittest.main()
