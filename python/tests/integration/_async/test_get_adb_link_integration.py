# -*- coding: utf-8 -*-
"""
Integration tests for GetAdbLink API
"""
import json

import pytest

from agentbay import CreateSessionParams


class TestGetAdbLinkIntegration:
    """Integration tests for GetAdbLink API"""

    @pytest.mark.asyncio
    async def test_get_adb_link_with_mobile_session(self, agent_bay_client):
        """Test get_adb_link with a real mobile session"""
        # Create a mobile session
        params = CreateSessionParams(image_id="mobile_latest")
        session_result = await agent_bay_client.create(params)
        if "no authorized app" in session_result.error_message:
            pytest.skip("No authorization")
        assert session_result is not None
        assert session_result.success is True, f"Failed to create session: {session_result.error_message}"
        assert session_result.session is not None

        session = session_result.session

        try:
            # Call get_adb_link API
            from alibabacloud_tea_openapi.exceptions._client import ClientException

            from agentbay.api.models import GetAdbLinkRequest

            # Prepare options with adbkey_pub
            options = json.dumps({"adbkey_pub": "test-adb-public-key"})

            request = GetAdbLinkRequest(
                authorization=f"Bearer {agent_bay_client.api_key}",
                session_id=session.session_id,
                option=options,
            )

            try:
                response = agent_bay_client.client.get_adb_link(request)
            except ClientException as e:
                if "InvalidAction.NotFound" in str(e):
                    pytest.skip("GetAdbLink API not yet available in production")
                raise

            # Verify response
            assert response is not None
            assert response.body is not None
            assert response.body.success is True
            assert response.body.data is not None
            assert response.body.data.url is not None

            # Verify URL format (should be an ADB connection string)
            url = response.body.data.url
            assert "adb" in url.lower() or ":" in url
            print(f"ADB URL: {url}")

        finally:
            # Clean up
            await agent_bay_client.delete(session)

    def test_get_adb_link_with_invalid_session(self, agent_bay_client):
        """Test get_adb_link with invalid session ID"""
        from alibabacloud_tea_openapi.exceptions._client import ClientException

        from agentbay.api.models import GetAdbLinkRequest

        options = json.dumps({"adbkey_pub": "test-key"})
        request = GetAdbLinkRequest(
            authorization=f"Bearer {agent_bay_client.api_key}",
            session_id="invalid-session-id-12345",
            option=options,
        )

        # Should raise exception for invalid session
        with pytest.raises(ClientException) as exc_info:
            response = agent_bay_client.client.get_adb_link(request)

        # Verify it's the expected error
        assert "InvalidMcpSession.NotFound" in str(
            exc_info.value
        ) or "InvalidAction.NotFound" in str(exc_info.value)
