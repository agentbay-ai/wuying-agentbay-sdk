import os
import pytest
import unittest
from unittest.mock import MagicMock, patch

from agentbay import AgentBay, Config


class TestSyncBetaNetworkNoRetry(unittest.TestCase):
    """Test beta network bind token without retry."""

    @patch.dict(os.environ, {"AGENTBAY_API_KEY": "test-api-key"})
    @patch("agentbay._sync.agentbay.mcp_client")
    @pytest.mark.sync
    def test_get_network_bind_token_no_retry(self, mock_mcp_client):
        mock_client = MagicMock()
        mock_client.create_network = MagicMock(
            side_effect=Exception("ServiceUnavailable")
        )
        mock_mcp_client.return_value = mock_client

        config = Config(
            timeout_ms=60000,
            region_id="cn-hangzhou",
        )
        agent_bay = AgentBay(cfg=config)

        result = agent_bay.beta_network.get_network_bind_token()

        self.assertFalse(result.success)
        self.assertIn("ServiceUnavailable", result.error_message)
        self.assertEqual(mock_client.create_network.call_count, 1)


if __name__ == "__main__":
    unittest.main()
