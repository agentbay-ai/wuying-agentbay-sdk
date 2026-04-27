"""Integration tests for context file operations.
ci-stable
"""

import pytest


@pytest.mark.asyncio
async def test_context_file_operations(agent_bay_client):
    """Test context file operations using upload/download URLs."""
    import httpx

    # Create a context
    ctx_result = await agent_bay_client.context.get("test_ctx", create=True)
    assert ctx_result.success

    try:
        # Get upload URL for a file
        upload_url_result = await agent_bay_client.context.get_file_upload_url(
            ctx_result.context_id, "/test_file.txt"
        )
        assert upload_url_result.success
        assert upload_url_result.url != ""

        # Upload file content
        file_content = b"test content for context file"
        async with httpx.AsyncClient() as client:
            response = await client.put(upload_url_result.url, content=file_content)
            assert response.status_code == 200

        # List files in context
        files_result = await agent_bay_client.context.list_files(
            ctx_result.context_id, "/"
        )
        assert files_result.success

        # Get download URL
        download_url_result = await agent_bay_client.context.get_file_download_url(
            ctx_result.context_id, "/test_file.txt"
        )
        assert download_url_result.success
        assert download_url_result.url != ""

        # Download and verify content
        async with httpx.AsyncClient() as client:
            response = await client.get(download_url_result.url)
            assert response.status_code == 200
            assert response.content == file_content

        # Delete the file
        delete_result = await agent_bay_client.context.delete_file(
            ctx_result.context_id, "/test_file.txt"
        )
        assert delete_result.success

    finally:
        # Clean up context
        await agent_bay_client.context.delete(ctx_result.context)

    print("Context file operations test completed successfully")
