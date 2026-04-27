"""Integration tests for ListSkillMetaData POP action.

Tests call the real backend without mocks, covering:
  - Basic metadata structure validation (async)
  - Async / sync SDK response parity
"""
# ci-stable

import os

import pytest

from agentbay import AgentBay, AsyncAgentBay

# agent_bay_client fixture (AsyncAgentBay, scope="module") is provided by conftest.py


@pytest.fixture(scope="module")
def agent_bay_sync():
    """Sync AgentBay client for parity tests."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AgentBay(api_key=api_key)


def _to_name_desc_map(items):
    """Validate item list structure and return a name→description mapping."""
    assert isinstance(items, list)
    assert len(items) > 0
    seen = set()
    m = {}
    for it in items:
        assert isinstance(it, dict)
        assert set(it.keys()) == {"name", "description"}
        name = it["name"]
        desc = it["description"]
        assert isinstance(name, str) and name.strip()
        assert isinstance(desc, str)
        assert name not in seen, f"Duplicate skill name: {name}"
        seen.add(name)
        m[name] = desc
    return m


@pytest.mark.asyncio
async def test_beta_skills_list_metadata(agent_bay_client: AsyncAgentBay):
    """Verify async list_metadata returns a valid, non-empty list with expected fields."""
    items = await agent_bay_client.beta.skills.list_metadata()
    assert isinstance(items, list)
    assert len(items) > 0
    first = items[0]
    assert isinstance(first.get("name"), str) and first["name"].strip()
    assert isinstance(first.get("description"), str)
    assert "dir" not in first


@pytest.mark.asyncio
async def test_beta_skills_list_metadata_sync_async_parity(
    agent_bay_client: AsyncAgentBay, agent_bay_sync: AgentBay
):
    """Verify that async and sync SDKs return identical skill metadata."""
    async_items = await agent_bay_client.beta.skills.list_metadata()
    sync_items = agent_bay_sync.beta.skills.list_metadata()

    async_map = _to_name_desc_map(async_items)
    sync_map = _to_name_desc_map(sync_items)

    assert async_map == sync_map
