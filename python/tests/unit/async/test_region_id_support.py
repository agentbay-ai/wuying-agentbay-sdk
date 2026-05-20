import os
import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agentbay import AsyncAgentBay, CreateSessionParams, Context, ContextResult, AsyncContextService, Config
from agentbay.api.models import (
    CreateMcpSessionRequest,
    CreateNetworkRequest,
    GetContextRequest,
)


class TestRegionIdSupport(unittest.IsolatedAsyncioTestCase):
    """Test region_id support in AgentBay client"""

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_agentbay_initialization_with_region_id(
        self, mock_mcp_client
    ):
        """Test initializing AgentBay with region_id parameter"""
        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AsyncAgentBay instance with region_id in config
        config = Config(timeout_ms=60000, region_id="cn-hangzhou")
        agent_bay = AsyncAgentBay(cfg=config)

        # Verify region_id is stored
        self.assertEqual(agent_bay.region_id, "cn-hangzhou")
        self.assertEqual(agent_bay.api_key, "test-api-key")

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio
    async def test_agentbay_initialization_with_partial_config_fills_defaults(
        self, mock_mcp_client
    ):
        """Test initializing AsyncAgentBay with partial config fills default endpoint/timeout"""
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        config = Config(timeout_ms=0, region_id="cn-hangzhou")
        agent_bay = AsyncAgentBay(cfg=config)

        self.assertEqual(agent_bay.region_id, "cn-hangzhou")

        called_openapi_cfg = mock_mcp_client.call_args[0][0]
        self.assertEqual(called_openapi_cfg.endpoint, "agentbay.cn-hangzhou.aliyuncs.com")
        self.assertEqual(called_openapi_cfg.read_timeout, 60000)
        self.assertEqual(called_openapi_cfg.connect_timeout, 60000)

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay._load_config")
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_agentbay_initialization_without_region_id(
        self, mock_mcp_client, mock_load_config
    ):
        """Test initializing AgentBay without region_id parameter (should default to None)"""
        # Mock configuration
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AsyncAgentBay instance without region_id
        agent_bay = AsyncAgentBay()

        # Verify region_id defaults to None
        self.assertIsNone(agent_bay.region_id)

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_session_create_with_region_id(
        self, mock_mcp_client
    ):
        """Test session creation passes LoginRegionId when region_id is set"""

        # Mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "Success": True,
                "Data": {
                    "Success": True,
                    "SessionId": "test-session-id",
                    "ResourceUrl": "test-resource-url",
                },
            }
        }
        mock_client.create_mcp_session_async = AsyncMock(return_value=mock_response)
        mock_mcp_client.return_value = mock_client

        # Mock context service and session methods
        with patch.object(AsyncContextService, "get") as mock_context_get:
            with patch(
                "agentbay._async.agentbay.AsyncAgentBay._wait_for_context_synchronization"
            ) as mock_wait:
                mock_context_result = ContextResult(
                    success=True,
                    context=Context(id="test-context-id", name="test-context"),
                )
                mock_context_get.return_value = mock_context_result
                mock_wait.return_value = None

                # Create AsyncAgentBay instance with region_id in config
                config = Config(timeout_ms=60000, region_id="cn-hangzhou")
                agent_bay = AsyncAgentBay(cfg=config)

                # Create session
                params = CreateSessionParams()
                result = await agent_bay.create(params)

                # Verify the API call was made with LoginRegionId
                mock_client.create_mcp_session_async.assert_called_once()
                call_args = mock_client.create_mcp_session_async.call_args[0][0]
                self.assertIsInstance(call_args, CreateMcpSessionRequest)
                self.assertEqual(call_args.login_region_id, "cn-hangzhou")

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay._load_config")
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_session_create_without_region_id(
        self, mock_mcp_client, mock_load_config
    ):
        """Test session creation doesn't pass LoginRegionId when region_id is not set"""
        # Mock configuration
        mock_load_config.return_value = {
            "endpoint": "test.endpoint.com",
            "timeout_ms": 30000,
            "region_id": None,
        }

        # Mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "Success": True,
                "Data": {
                    "Success": True,
                    "SessionId": "test-session-id",
                    "ResourceUrl": "test-resource-url",
                },
            }
        }
        mock_client.create_mcp_session_async = AsyncMock(return_value=mock_response)
        mock_mcp_client.return_value = mock_client

        # Mock context service and session methods
        with patch.object(AsyncContextService, "get") as mock_context_get:
            with patch(
                "agentbay._async.agentbay.AsyncAgentBay._wait_for_context_synchronization"
            ) as mock_wait:
                mock_context_result = ContextResult(
                    success=True,
                    context=Context(id="test-context-id", name="test-context"),
                )
                mock_context_get.return_value = mock_context_result
                mock_wait.return_value = None

                # Create AsyncAgentBay instance without region_id
                agent_bay = AsyncAgentBay()

                # Create session
                params = CreateSessionParams()
                result = await agent_bay.create(params)

            # Verify the API call was made without LoginRegionId
            mock_client.create_mcp_session_async.assert_called_once()
            call_args = mock_client.create_mcp_session_async.call_args[0][0]
            self.assertIsInstance(call_args, CreateMcpSessionRequest)
            # LoginRegionId should be None or not set when region_id is not provided
            self.assertIsNone(getattr(call_args, "login_region_id", None))

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_context_create_with_region_id(
        self, mock_mcp_client
    ):
        """Test context.get with create=True passes LoginRegionId when region_id is set"""

        # Mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "Success": True,
                "Data": {"ContextId": "test-context-id", "Name": "test-context-name"},
            }
        }
        mock_client.get_context_async = AsyncMock(return_value=mock_response)
        mock_mcp_client.return_value = mock_client

        # Create AsyncAgentBay instance with region_id in config
        config = Config(timeout_ms=60000, region_id="cn-hangzhou")
        agent_bay = AsyncAgentBay(cfg=config)

        # Create context (get with create=True)
        result = await agent_bay.context.get("test-context-name", create=True)

        # Verify the API call was made with LoginRegionId
        mock_client.get_context_async.assert_called_once()
        call_args = mock_client.get_context_async.call_args[0][0]
        self.assertIsInstance(call_args, GetContextRequest)
        self.assertEqual(call_args.login_region_id, "cn-hangzhou")

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio

    async def test_context_get_without_create_no_region_id(
        self, mock_mcp_client
    ):
        """Test context.get without create=True doesn't pass LoginRegionId even when region_id is set"""

        # Mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_map.return_value = {
            "body": {
                "Success": True,
                "Data": {"ContextId": "test-context-id", "Name": "test-context-name"},
            }
        }
        mock_client.get_context_async = AsyncMock(return_value=mock_response)
        mock_mcp_client.return_value = mock_client

        # Create AsyncAgentBay instance with region_id in config
        config = Config(timeout_ms=60000, region_id="cn-hangzhou")
        agent_bay = AsyncAgentBay(cfg=config)

        # Get existing context (create=False, which is default)
        result = await agent_bay.context.get("test-context-name")

        # Verify the API call was made without LoginRegionId
        mock_client.get_context_async.assert_called_once()
        call_args = mock_client.get_context_async.call_args[0][0]
        self.assertIsInstance(call_args, GetContextRequest)
        # LoginRegionId should be None when create=False
        self.assertIsNone(call_args.login_region_id)

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio
    async def test_network_bind_token_with_region_id(
        self, mock_mcp_client
    ):
        """Test get_network_bind_token passes LoginRegionId when region_id is set"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_map.return_value = {"body": {"RequestId": "req-id"}}
        mock_body = MagicMock()
        mock_body.success = True
        mock_body.data = MagicMock(
            network_id="test-network-id",
            network_token="test-network-token",
        )
        mock_response.body = mock_body
        mock_client.create_network_async = AsyncMock(return_value=mock_response)
        mock_mcp_client.return_value = mock_client

        config = Config(
            timeout_ms=60000,
            region_id="cn-hangzhou",
        )
        agent_bay = AsyncAgentBay(cfg=config)

        result = await agent_bay.beta_network.get_network_bind_token()

        mock_client.create_network_async.assert_called_once()
        call_args = mock_client.create_network_async.call_args[0][0]
        self.assertIsInstance(call_args, CreateNetworkRequest)
        self.assertEqual(call_args.login_region_id, "cn-hangzhou")
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
