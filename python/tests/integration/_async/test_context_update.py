"""Integration tests for context updates.
ci-stable
"""

import pytest


@pytest.mark.asyncio
async def test_context_file_update(agent_bay_client):
    """Test updating file in context using upload URLs."""
    import httpx

    ctx_result = await agent_bay_client.context.get("update_ctx", create=True)
    assert ctx_result.success

    try:
        upload_url_result = await agent_bay_client.context.get_file_upload_url(
            ctx_result.context_id, "/update_file.txt"
        )
        assert upload_url_result.success

        original_content = b"original content"
        async with httpx.AsyncClient() as client:
            response = await client.put(upload_url_result.url, content=original_content)
            assert response.status_code == 200

        upload_url_result2 = await agent_bay_client.context.get_file_upload_url(
            ctx_result.context_id, "/update_file.txt"
        )
        assert upload_url_result2.success

        updated_content = b"updated content"
        async with httpx.AsyncClient() as client:
            response = await client.put(upload_url_result2.url, content=updated_content)
            assert response.status_code == 200

        download_url_result = await agent_bay_client.context.get_file_download_url(
            ctx_result.context_id, "/update_file.txt"
        )
        assert download_url_result.success

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url_result.url)
            assert response.status_code == 200
            assert response.content == updated_content

        print("Context file updated successfully")
    finally:
        await agent_bay_client.context.delete(ctx_result.context)
