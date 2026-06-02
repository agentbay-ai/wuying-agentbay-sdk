"""E2E test: create a session via the deprecated AGENTBAY_ENDPOINT fallback
pointing at the pre-release cn-hangzhou environment.

Run with:
    AGENTBAY_API_KEY=<key> \
    AGENTBAY_ENDPOINT=agentbay-pre.cn-hangzhou.aliyuncs.com \
    pytest tests/integration/_async/test_deprecated_endpoint_pre.py -s
"""

import os

import pytest

from agentbay import AsyncAgentBay, CreateSessionParams


@pytest.fixture(scope="module")
def agent_bay_client() -> AsyncAgentBay:
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable is not set")

    endpoint = os.environ.get("AGENTBAY_ENDPOINT")
    if not endpoint:
        pytest.skip("AGENTBAY_ENDPOINT environment variable is not set")

    client = AsyncAgentBay(api_key=api_key)
    print(f"Endpoint resolved to: {client.client._endpoint}")
    return client


@pytest.mark.asyncio
async def test_create_and_delete_session_via_deprecated_endpoint(agent_bay_client: AsyncAgentBay):
    """Create a session on the pre-release env using AGENTBAY_ENDPOINT, then delete it."""
    print("\nCreating session on pre-release endpoint...")
    params = CreateSessionParams(
        labels={"test": "deprecated-endpoint-pre"},
    )
    result = await agent_bay_client.create(params)
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None

    session = result.session
    print(f"Session created: {session.session_id}")

    status_result = await session.get_status()
    assert status_result.success, f"Failed to get status: {status_result.error_message}"
    print(f"Session status: {status_result.status}")
    assert status_result.status in ["RUNNING", "CREATING"]

    print("Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
    print("Session deleted successfully.")