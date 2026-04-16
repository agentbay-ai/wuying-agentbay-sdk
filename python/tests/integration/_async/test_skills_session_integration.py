"""Integration tests for skills functionality.
ci-stable

This test calls the real backend without mocks.
"""

import pytest

from agentbay import AsyncAgentBay
from agentbay._common.params.session_params import CreateSessionParams


@pytest.mark.asyncio
async def test_get_metadata_returns_skills_root_path(agent_bay_client: AsyncAgentBay):
    """get_metadata() should return SkillsMetadataResult with skills_root_path."""
    result = await agent_bay_client.beta_skills.get_metadata()

    assert result is not None
    assert isinstance(result.skills_root_path, str)
    assert len(result.skills_root_path) > 0, "skills_root_path should not be empty"
    assert isinstance(result.skills, list)


@pytest.mark.asyncio
async def test_get_metadata_with_skill_names(agent_bay_client: AsyncAgentBay):
    """get_metadata(skill_names=[...]) should not raise errors."""
    result = await agent_bay_client.beta_skills.get_metadata(skill_names=["non-existent-skill"])
    assert result is not None
    assert isinstance(result.skills, list)
    assert isinstance(result.skills_root_path, str)


@pytest.mark.asyncio
async def test_get_metadata_with_image_id(agent_bay_client: AsyncAgentBay):
    """get_metadata(image_id=...) should return skills_root_path for that image."""
    result = await agent_bay_client.beta_skills.get_metadata(image_id="linux_latest")
    assert result is not None
    assert isinstance(result.skills_root_path, str)
    assert len(result.skills_root_path) > 0


@pytest.mark.asyncio
async def test_create_session_with_load_skills(agent_bay_client: AsyncAgentBay):
    """Creating session with load_skills=True should succeed (backend accepts the param)."""
    params = CreateSessionParams(load_skills=True)
    result = await agent_bay_client.create(params)
    assert result.success, f"Session creation failed: {result.error_message}"
    assert result.session is not None
    await result.session.delete()

