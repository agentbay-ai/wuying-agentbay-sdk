# ci-stable
"""Integration tests for network bind token API."""

import pytest

from agentbay import AsyncAgentBay


@pytest.mark.asyncio
async def test_network_create_describe_and_bind_session(agent_bay_client: AsyncAgentBay):
    net_result = await agent_bay_client.beta_network.get_network_bind_token()
    assert net_result.success, net_result.error_message
    assert net_result.network_id != ""
    assert net_result.network_token != ""
