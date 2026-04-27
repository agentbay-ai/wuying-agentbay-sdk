# ci-stable
# -*- coding: utf-8 -*-

import pytest

from agentbay import CreateSessionParams


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetSessionWsUrlIntegration:
    async def test_get_restored_session_should_include_ws_url(self, agent_bay_client):
        create_result = await agent_bay_client.create(CreateSessionParams())
        assert create_result.success is True, create_result.error_message
        assert create_result.session is not None

        created_session = create_result.session
        try:
            get_result = await agent_bay_client.get(created_session.session_id)
            assert get_result.success is True, get_result.error_message
            assert get_result.session is not None

            restored_session = get_result.session
            assert restored_session.ws_url, "ws_url should not be empty on restored session"
            assert restored_session.ws_url.startswith(("ws://", "wss://")), (
                f"ws_url should be a ws/wss URL, got: {restored_session.ws_url!r}"
            )
        finally:
            await agent_bay_client.delete(created_session)

