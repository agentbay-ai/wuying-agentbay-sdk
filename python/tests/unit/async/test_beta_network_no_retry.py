import os
import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agentbay import AsyncAgentBay, Config


class TestAsyncBetaNetworkNoRetry(unittest.IsolatedAsyncioTestCase):
    """Test beta network bind token without retry."""

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._async.agentbay.mcp_client")
    @pytest.mark.asyncio
    async def test_get_network_bind_token_no_retry(self, mock_mcp_client):
        mock_client = MagicMock()
        mock_client.create_network_async = AsyncMock(
            side_effect=Exception("ServiceUnavailable")
        )
        mock_mcp_client.return_value = mock_client

        config = Config(
            timeout_ms=60000,
            region_id="cn-hangzhou",
        )
        agent_bay = AsyncAgentBay(cfg=config)

        result = await agent_bay.beta_network.get_network_bind_token()

        self.assertFalse(result.success)
        self.assertIn("ServiceUnavailable", result.error_message)
        self.assertEqual(mock_client.create_network_async.call_count, 1)


if __name__ == "__main__":
    unittest.main()
