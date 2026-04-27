# -*- coding: utf-8 -*-
"""
Integration tests for GetCdpLink API
"""
# ci-stable

import pytest



class TestGetCdpLinkIntegration:
    """Integration tests for GetCdpLink API"""

    @pytest.mark.asyncio
    async def test_get_cdp_link_with_browser_session(self, agent_bay_client):
        """Test get_cdp_link with a real browser session"""
        from agentbay import CreateSessionParams

        # Create a browser session
        params = CreateSessionParams(image_id="browser_latest")
        session_result = await agent_bay_client.create(params)
        assert session_result is not None
        assert session_result.success is True
        assert session_result.session is not None

        session = session_result.session

        try:
            # Call get_cdp_link API
            from alibabacloud_tea_openapi.exceptions._client import ClientException

            from agentbay.api.models import GetCdpLinkRequest

            request = GetCdpLinkRequest(
                authorization=f"Bearer {agent_bay_client.api_key}",
                session_id=session.session_id,
            )

            try:
                response = agent_bay_client.client.get_cdp_link(request)
            except ClientException as e:
                if "InvalidAction.NotFound" in str(e):
                    pytest.skip("GetCdpLink API not yet available in production")
                raise

            # Verify response
            assert response is not None
            assert response.body is not None
            assert response.body.success is True
            assert response.body.data is not None
            assert response.body.data.url is not None

            # Verify URL format (should be a WebSocket URL)
            url = response.body.data.url
            assert url.startswith("ws://") or url.startswith("wss://")
            print(f"CDP URL: {url}")

        finally:
            # Clean up
            await agent_bay_client.delete(session)

    def test_get_cdp_link_with_invalid_session(self, agent_bay_client):
        """Test get_cdp_link with invalid session ID"""
        from alibabacloud_tea_openapi.exceptions._client import ClientException

        from agentbay.api.models import GetCdpLinkRequest

        request = GetCdpLinkRequest(
            authorization=f"Bearer {agent_bay_client.api_key}",
            session_id="invalid-session-id-12345",
        )

        # Should raise exception for invalid session
        with pytest.raises(ClientException) as exc_info:
            response = agent_bay_client.client.get_cdp_link(request)

        # Verify it's the expected error
        assert "InvalidMcpSession.NotFound" in str(
            exc_info.value
        ) or "InvalidAction.NotFound" in str(exc_info.value)
