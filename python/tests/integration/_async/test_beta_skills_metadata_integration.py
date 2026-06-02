"""Integration tests for GetSkillMetaData POP action.

Tests call the real backend without mocks, covering:
  - Basic metadata structure validation (async)
  - Async / sync SDK response parity
"""
# ci-stable

import os

import pytest

from agentbay import AgentBay, AsyncAgentBay
from agentbay._common.models.skill_info import SkillsMetadataResult

# agent_bay_client fixture (AsyncAgentBay, scope="module") is provided by conftest.py


@pytest.fixture(scope="module")
def agent_bay_sync():
    """Sync AgentBay client for parity tests."""
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")
    return AgentBay(api_key=api_key)


def _to_name_desc_map(result: SkillsMetadataResult):
    """Validate result structure and return a name->description mapping."""
    assert isinstance(result, SkillsMetadataResult)
    assert len(result.skills) > 0
    seen = set()
    m = {}
    for skill in result.skills:
        name = skill.name
        desc = skill.description
        assert isinstance(name, str) and name.strip()
        assert isinstance(desc, str)
        assert name not in seen, f"Duplicate skill name: {name}"
        seen.add(name)
        m[name] = desc
    return m


@pytest.mark.asyncio
async def test_beta_skills_get_metadata(agent_bay_client: AsyncAgentBay):
    """Verify async get_metadata returns a valid SkillsMetadataResult with expected fields."""
    result = await agent_bay_client.beta.skills.get_metadata()
    assert isinstance(result, SkillsMetadataResult)
    assert len(result.skills) > 0
    first = result.skills[0]
    assert isinstance(first.name, str) and first.name.strip()
    assert isinstance(first.description, str)


@pytest.mark.asyncio
async def test_beta_skills_get_metadata_sync_async_parity(
    agent_bay_client: AsyncAgentBay, agent_bay_sync: AgentBay
):
    """Verify that async and sync SDKs return identical skill metadata."""
    async_result = await agent_bay_client.beta.skills.get_metadata()
    sync_result = agent_bay_sync.beta.skills.get_metadata()

    async_map = _to_name_desc_map(async_result)
    sync_map = _to_name_desc_map(sync_result)

    assert async_map == sync_map
