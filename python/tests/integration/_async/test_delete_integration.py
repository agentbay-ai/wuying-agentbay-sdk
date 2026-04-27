# ci-stable
import asyncio
from uuid import uuid4

import pytest

from agentbay import ContextSync
from agentbay import CreateSessionParams


class TestDeleteIntegration:
    """Integration test for session deletion functionality"""

    @pytest.mark.asyncio
    async def test_delete_without_params(self, agent_bay_client):
        """Test session deletion functionality without parameters"""
        # Create a session
        print("Creating session for parameter-less deletion test...")
        result = await agent_bay_client.create()
        assert result.success
        assert result.session is not None
        session = result.session
        print(f"Session created successfully, ID: {session.session_id}")

        # Delete session using default parameters
        print("Deleting session using parameter-less delete method...")
        delete_result = await session.delete()
        assert delete_result.success
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        # Verify session has been deleted
        # Wait for a while to ensure deletion operation is completed
        await asyncio.sleep(2)

        # Use list to get latest session list from server
        list_result = await agent_bay_client.list()
        assert list_result.success

        # Check if session has been deleted
        assert session.session_id not in list_result.session_ids, f"Session ID {session.session_id} still exists after deletion"

    @pytest.mark.asyncio
    async def test_delete_with_sync_context(self, agent_bay_client):
        """Test session deletion functionality with sync_context parameter"""
        # Create context
        context_name = f"test-context-{uuid4().hex[:8]}"
        print(f"Creating context: {context_name}...")
        context_result = await agent_bay_client.context.get(context_name, create=True)
        assert context_result.success
        assert context_result.context is not None
        context = context_result.context
        print(f"Context created successfully, ID: {context.id}")

        # Create persistence configuration
        persistence_data = [
            ContextSync(context_id=context.id, path="/home/wuying/test")
        ]

        # Create session with context
        params = CreateSessionParams(
            image_id="linux_latest", context_syncs=persistence_data
        )

        print("Creating session with context...")
        result = await agent_bay_client.create(params)
        assert result.success
        assert result.session
        session = result.session
        print(f"Session created successfully, ID: {session.session_id}")

        # Delete session using sync_context=True
        print("Deleting session using sync_context=True...")
        delete_result = await session.delete(sync_context=True)
        assert delete_result.success
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        # Verify session has been deleted
        await asyncio.sleep(2)
        list_result = await agent_bay_client.list()
        assert list_result.success
        assert session.session_id not in list_result.session_ids

        # Clean up context
        try:
            context_delete_result = await agent_bay_client.context.delete(context)
            if context_delete_result.success:
                print(f"Context {context.id} deleted successfully")
        except Exception as e:
            print(f"Warning: Failed to delete context {context.id}: {e}")

    @pytest.mark.asyncio
    async def test_agentbay_delete_with_sync_context(self, agent_bay_client):
        """Test agentbay-level deletion with sync context"""
        # Create a simple session
        print("Creating session for agentbay-level deletion test...")
        result = await agent_bay_client.create()
        assert result.success
        assert result.session is not None
        session = result.session
        print(f"Session created successfully, ID: {session.session_id}")

        # Delete using agentbay.delete method
        print("Deleting session using agentbay.delete method...")
        delete_result = await agent_bay_client.delete(session, sync_context=True)
        assert delete_result.success
        print(f"Session deleted successfully (RequestID: {delete_result.request_id})")

        # Verify session has been deleted
        await asyncio.sleep(2)
        list_result = await agent_bay_client.list()
        assert list_result.success
        assert session.session_id not in list_result.session_ids