import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentbay import AsyncAgentBay
from agentbay._common.models.skill_info import SkillsMetadataResult


class TestBetaSkillsMetadata(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_agentbay_has_beta_skills(self):
        with patch("agentbay._async.agentbay._load_config") as mock_load_config, patch(
            "agentbay._async.agentbay.mcp_client"
        ) as mock_mcp_client:
            mock_load_config.return_value = {
                "endpoint": "test.endpoint.com",
                "timeout_ms": 30000,
                "region_id": None,
            }
            mock_mcp_client.return_value = MagicMock()
            agent_bay = AsyncAgentBay(api_key="test-key")
            assert hasattr(agent_bay, "beta")
            assert hasattr(agent_bay.beta, "skills")

    @pytest.mark.asyncio
    async def test_get_metadata_parses_response(self):
        with patch("agentbay._async.agentbay._load_config") as mock_load_config, patch(
            "agentbay._async.agentbay.mcp_client"
        ) as mock_mcp_client:
            mock_load_config.return_value = {
                "endpoint": "test.endpoint.com",
                "timeout_ms": 30000,
                "region_id": None,
            }
            mock_mcp_client.return_value = MagicMock()
            agent_bay = AsyncAgentBay(api_key="test-key")

            agent_bay.client = MagicMock()
            captured = {}

            async def _fake_get_skill_meta_data(req):
                captured["authorization"] = getattr(req, "authorization", None)

                item1 = MagicMock()
                item1.name = "sandbox-env-audit"
                item1.description = "Generate a sandbox report"
                item1.skill_id = "sk_001"
                item2 = MagicMock()
                item2.name = "empty-desc"
                item2.description = ""
                item2.skill_id = ""

                data = MagicMock()
                data.skill_path = "/home/wuying/skills"
                data.meta_data_list = [item1, item2]

                body = MagicMock()
                body.success = True
                body.code = ""
                body.message = ""
                body.data = data

                resp = MagicMock()
                resp.body = body
                return resp

            agent_bay.client.get_skill_meta_data_async = AsyncMock(side_effect=_fake_get_skill_meta_data)

            result = await agent_bay.beta.skills.get_metadata()
            assert captured["authorization"] == "Bearer test-key"

            assert isinstance(result, SkillsMetadataResult)
            assert result.skills_root_path == "/home/wuying/skills"
            assert len(result.skills) == 2
            assert result.skills[0].name == "sandbox-env-audit"
            assert result.skills[0].description == "Generate a sandbox report"
            assert result.skills[0].skill_id == "sk_001"
            assert result.skills[1].name == "empty-desc"
            assert result.skills[1].description == ""
