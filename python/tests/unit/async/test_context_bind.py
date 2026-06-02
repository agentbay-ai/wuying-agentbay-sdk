import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentbay import (
    AsyncContextManager,
    ContextBinding,
    ContextBindingsResult,
    ContextBindResult,
)
from agentbay._common.models.context import ContextInfoResult, ContextStatusData
from agentbay._common.params.context_sync import ContextSync


def _mock_info_download_success(context_id="ctx-123", path="/tmp/test"):
    """Return an AsyncMock for info() that immediately returns download Success."""
    async def _info(context_id=None, path=None, task_type=None):
        return ContextInfoResult(
            success=True,
            context_status_data=[
                ContextStatusData(
                    context_id=context_id or "ctx-123",
                    path=path or "/tmp/test",
                    status="Success",
                    task_type="download",
                )
            ],
        )
    return _info


class TestAsyncContextManagerBind(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session._get_api_key.return_value = "test-api-key"
        self.mock_session._get_session_id.return_value = "test-session-id"
        self.mock_client = MagicMock()
        self.mock_session._get_client.return_value = self.mock_client
        self.context_manager = AsyncContextManager(self.mock_session)

    @pytest.mark.asyncio
    async def test_bind_no_contexts_returns_error(self):
        """bind() with no arguments should return an error."""
        result = await self.context_manager.bind()
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "No contexts provided")

    @pytest.mark.asyncio
    async def test_bind_single_context_success(self):
        """bind() with a single ContextSync should call BindContexts API."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-001",
                "Success": True,
                "Code": None,
                "Message": None,
            }
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        with patch.object(self.context_manager, "list_bindings") as mock_list, \
             patch.object(self.context_manager, "info", side_effect=_mock_info_download_success()):
            mock_list.return_value = ContextBindingsResult(
                success=True,
                bindings=[ContextBinding(context_id="ctx-123", path="/tmp/test")],
            )
            result = await self.context_manager.bind(
                ContextSync(context_id="ctx-123", path="/tmp/test"),
            )

        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-001")
        self.mock_client.bind_contexts_async.assert_called_once()

        call_args = self.mock_client.bind_contexts_async.call_args[0][0]
        self.assertEqual(call_args.session_id, "test-session-id")
        self.assertEqual(call_args.authorization, "Bearer test-api-key")
        self.assertEqual(len(call_args.persistence_data_list), 1)
        self.assertEqual(call_args.persistence_data_list[0].context_id, "ctx-123")
        self.assertEqual(call_args.persistence_data_list[0].path, "/tmp/test")

    @pytest.mark.asyncio
    async def test_bind_multiple_contexts(self):
        """bind() with multiple ContextSync should send all in one request."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-002", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        with patch.object(self.context_manager, "list_bindings") as mock_list, \
             patch.object(self.context_manager, "info", side_effect=_mock_info_download_success()):
            mock_list.return_value = ContextBindingsResult(
                success=True,
                bindings=[
                    ContextBinding(context_id="ctx-a", path="/tmp/a"),
                    ContextBinding(context_id="ctx-b", path="/tmp/b"),
                ],
            )
            result = await self.context_manager.bind(
                ContextSync(context_id="ctx-a", path="/tmp/a"),
                ContextSync(context_id="ctx-b", path="/tmp/b"),
            )

        self.assertTrue(result.success)
        call_args = self.mock_client.bind_contexts_async.call_args[0][0]
        self.assertEqual(len(call_args.persistence_data_list), 2)
        self.assertEqual(call_args.persistence_data_list[0].context_id, "ctx-a")
        self.assertEqual(call_args.persistence_data_list[1].context_id, "ctx-b")

    @pytest.mark.asyncio
    async def test_bind_api_failure(self):
        """bind() should return failure when API returns error."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-003",
                "Success": False,
                "Code": "PathAlreadyBound",
                "Message": "Path /tmp/test is already bound",
            }
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        result = await self.context_manager.bind(
            ContextSync(context_id="ctx-123", path="/tmp/test"),
        )

        self.assertFalse(result.success)
        self.assertIn("PathAlreadyBound", result.error_message)
        self.assertIn("already bound", result.error_message)

    @pytest.mark.asyncio
    async def test_bind_without_wait(self):
        """bind(wait_for_completion=False) should not poll list_bindings."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-004", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        with patch.object(self.context_manager, "list_bindings") as mock_list:
            result = await self.context_manager.bind(
                ContextSync(context_id="ctx-123", path="/tmp/test"),
                wait_for_completion=False,
            )
            mock_list.assert_not_called()

        self.assertTrue(result.success)

    @pytest.mark.asyncio
    async def test_list_bindings_success(self):
        """list_bindings() should parse DescribeSessionContexts response."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-010",
                "Success": True,
                "Data": [
                    {
                        "ContextId": "ctx-a",
                        "ContextName": "project-data",
                        "Path": "/tmp/project",
                        "Policy": "{}",
                        "BindTime": "2026-03-06T10:00:00Z",
                    },
                    {
                        "ContextId": "ctx-b",
                        "ContextName": "shared-libs",
                        "Path": "/opt/libs",
                        "Policy": "{}",
                        "BindTime": "2026-03-06T10:05:00Z",
                    },
                ],
            }
        }
        self.mock_client.describe_session_contexts_async = AsyncMock(
            return_value=mock_response
        )

        result = await self.context_manager.list_bindings()

        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-010")
        self.assertEqual(len(result.bindings), 2)

        self.assertEqual(result.bindings[0].context_id, "ctx-a")
        self.assertEqual(result.bindings[0].context_name, "project-data")
        self.assertEqual(result.bindings[0].path, "/tmp/project")
        self.assertEqual(result.bindings[0].bind_time, "2026-03-06T10:00:00Z")

        self.assertEqual(result.bindings[1].context_id, "ctx-b")
        self.assertEqual(result.bindings[1].context_name, "shared-libs")
        self.assertEqual(result.bindings[1].path, "/opt/libs")

    @pytest.mark.asyncio
    async def test_list_bindings_empty(self):
        """list_bindings() should return empty list when no bindings exist."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-011",
                "Success": True,
                "Data": [],
            }
        }
        self.mock_client.describe_session_contexts_async = AsyncMock(
            return_value=mock_response
        )

        result = await self.context_manager.list_bindings()

        self.assertTrue(result.success)
        self.assertEqual(len(result.bindings), 0)

    @pytest.mark.asyncio
    async def test_list_bindings_api_failure(self):
        """list_bindings() should return failure when API returns error."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-012",
                "Success": False,
                "Code": "InvalidMcpSession.NotFound",
                "Message": "Session not found",
            }
        }
        self.mock_client.describe_session_contexts_async = AsyncMock(
            return_value=mock_response
        )

        result = await self.context_manager.list_bindings()

        self.assertFalse(result.success)
        self.assertIn("InvalidMcpSession.NotFound", result.error_message)

    @pytest.mark.asyncio
    async def test_list_bindings_null_data(self):
        """list_bindings() should handle null Data field gracefully."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "RequestId": "req-013",
                "Success": True,
                "Data": None,
            }
        }
        self.mock_client.describe_session_contexts_async = AsyncMock(
            return_value=mock_response
        )

        result = await self.context_manager.list_bindings()

        self.assertTrue(result.success)
        self.assertEqual(len(result.bindings), 0)


class TestAsyncContextManagerBindDownloadPolling(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session._get_api_key.return_value = "test-api-key"
        self.mock_session._get_session_id.return_value = "test-session-id"
        self.mock_client = MagicMock()
        self.mock_session._get_client.return_value = self.mock_client
        self.context_manager = AsyncContextManager(self.mock_session)

    @pytest.mark.asyncio
    async def test_bind_waits_for_download_completion(self):
        """bind(wait_for_completion=True) should poll info() until download completes."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-005", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        info_call_count = 0

        async def mock_list_bindings():
            return ContextBindingsResult(
                success=True,
                bindings=[ContextBinding(context_id="ctx-123", path="/tmp/test")],
            )

        async def mock_info(context_id=None, path=None, task_type=None):
            nonlocal info_call_count
            info_call_count += 1
            if info_call_count <= 2:
                return ContextInfoResult(
                    success=True,
                    context_status_data=[
                        ContextStatusData(
                            context_id="ctx-123",
                            path="/tmp/test",
                            status="InProgress",
                            task_type="download",
                        )
                    ],
                )
            return ContextInfoResult(
                success=True,
                context_status_data=[
                    ContextStatusData(
                        context_id="ctx-123",
                        path="/tmp/test",
                        status="Success",
                        task_type="download",
                    )
                ],
            )

        with patch.object(self.context_manager, "list_bindings", side_effect=mock_list_bindings):
            with patch.object(self.context_manager, "info", side_effect=mock_info):
                result = await self.context_manager.bind(
                    ContextSync(context_id="ctx-123", path="/tmp/test"),
                    wait_for_completion=True,
                )

        self.assertTrue(result.success)
        self.assertGreaterEqual(info_call_count, 3)

    @pytest.mark.asyncio
    async def test_bind_no_download_polling_for_beta_context_mount(self):
        """bind() with BetaContextMount should NOT poll info() for download."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-006", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        info_call_count = 0

        async def mock_info(context_id=None, path=None, task_type=None):
            nonlocal info_call_count
            info_call_count += 1
            return ContextInfoResult(success=True, context_status_data=[])

        from agentbay._common.params.beta_context_mount import BetaContextMount

        with patch.object(self.context_manager, "info", side_effect=mock_info):
            result = await self.context_manager.bind(
                BetaContextMount(context_id="ctx-456", path="/mnt/data"),
                wait_for_completion=True,
            )

        self.assertTrue(result.success)
        self.assertEqual(info_call_count, 0)

    @pytest.mark.asyncio
    async def test_bind_download_failure_returns_success(self):
        """bind() returns success even if download fails (bind API itself succeeded)."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-007", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        async def mock_list_bindings():
            return ContextBindingsResult(
                success=True,
                bindings=[ContextBinding(context_id="ctx-123", path="/tmp/test")],
            )

        async def mock_info(context_id=None, path=None, task_type=None):
            return ContextInfoResult(
                success=True,
                context_status_data=[
                    ContextStatusData(
                        context_id="ctx-123",
                        path="/tmp/test",
                        status="Failed",
                        task_type="download",
                        error_message="Download timeout",
                    )
                ],
            )

        with patch.object(self.context_manager, "list_bindings", side_effect=mock_list_bindings):
            with patch.object(self.context_manager, "info", side_effect=mock_info):
                result = await self.context_manager.bind(
                    ContextSync(context_id="ctx-123", path="/tmp/test"),
                    wait_for_completion=True,
                )

        self.assertTrue(result.success)

    @pytest.mark.asyncio
    async def test_bind_without_wait_skips_download_polling(self):
        """bind(wait_for_completion=False) should not poll info() at all."""
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {"RequestId": "req-008", "Success": True}
        }
        self.mock_client.bind_contexts_async = AsyncMock(return_value=mock_response)

        with patch.object(self.context_manager, "list_bindings") as mock_list:
            with patch.object(self.context_manager, "info") as mock_info:
                result = await self.context_manager.bind(
                    ContextSync(context_id="ctx-123", path="/tmp/test"),
                    wait_for_completion=False,
                )
                mock_list.assert_not_called()
                mock_info.assert_not_called()

        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
