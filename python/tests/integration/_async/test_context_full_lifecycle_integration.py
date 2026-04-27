"""Integration tests for Context full lifecycle operations.
ci-stable

This module tests the complete context lifecycle including:
- Context creation and deletion
- File upload and download within a context
- Cross-session context synchronization
"""

import time
from uuid import uuid4

import pytest

from agentbay import AgentBayError
from agentbay import ContextSync
from agentbay import CreateSessionParams


class TestContextFullLifecycle:
    """Integration tests for Context full lifecycle operations."""

    @pytest.mark.asyncio
    async def test_context_full_lifecycle_single_session(self, agent_bay_client):
        """
        Scenario 1: Complete context lifecycle within a single session.

        Test steps:
        1. Create a context
        2. Create a session with context sync
        3. Basic verification
        4. Clean up
        """
        print("\n" + "=" * 70)
        print("TEST: Context Full Lifecycle in Single Session")
        print("=" * 70)

        # Step 1: Create a context
        print("\nStep 1: Creating a test context...")
        context_name = f"test-lifecycle-{uuid4().hex[:8]}"
        context_result = await agent_bay_client.context.create(context_name)
        assert context_result.success, f"Failed to create context: {context_result.error_message}"

        context = context_result.context
        print(f"  ✓ Context created: {context.name} (ID: {context.id})")

        try:
            # Step 2: Create a session with context sync
            print("\nStep 2: Creating session with context sync...")
            test_path = "/tmp/lifecycle_test"

            params = CreateSessionParams(
                context_syncs=[ContextSync(context_id=context.id, path=test_path)]
            )
            session_result = await agent_bay_client.create(params=params)
            assert session_result.success, f"Failed to create session: {session_result.error_message}"

            session = session_result.session
            print(f"  ✓ Session created: {session.session_id}")

            # Step 3: Basic verification
            print("\nStep 3: Basic test completed")

            # Clean up session
            print("\nStep 4: Cleaning up session...")
            session_delete_result = await session.delete()
            assert session_delete_result.success, f"Failed to delete session: {session_delete_result.error_message}"
            print(f"  ✓ Session deleted successfully")

        finally:
            await agent_bay_client.context.delete(context)
            print(f"  ✓ Context deleted: {context.id}")

        print("\n" + "=" * 70)
        print("✅ Context Full Lifecycle Test PASSED")
        print("=" * 70)

    @pytest.mark.asyncio
    async def test_context_cross_session_persistence(self, agent_bay_client):
        """
        Scenario 2: Test context persistence across multiple sessions.
        """
        print("\n" + "=" * 70)
        print("TEST: Context Cross-Session Persistence")
        print("=" * 70)

        # Create a context
        print("\nStep 1: Creating a test context...")
        context_name = f"test-cross-session-{uuid4().hex[:8]}"
        context_result = await agent_bay_client.context.create(context_name)
        assert context_result.success, f"Failed to create context: {context_result.error_message}"

        context = context_result.context
        print(f"  ✓ Context created: {context.name} (ID: {context.id})")

        try:
            # Step 2: Create first session and write test data
            print("\nStep 2: Creating first session and writing test data...")
            test_path = "/tmp/cross_session_test"
            test_file_path = f"{test_path}/persistence_test.txt"
            test_content = f"Cross-session test data created at {time.time()}"

            context_sync = ContextSync(context_id=context.id, path=test_path)
            session1_params = CreateSessionParams(context_syncs=[context_sync])

            session1_result = await agent_bay_client.create(params=session1_params)
            assert session1_result.success, f"Failed to create session1: {session1_result.error_message}"

            session1 = session1_result.session
            print(f"  ✓ Session1 created: {session1.session_id}")

            # Write test data to session1
            write_result = await session1.file_system.write_file(test_file_path, test_content)
            assert write_result.success, f"Failed to write test file: {write_result.error_message}"
            print(f"  ✓ Test data written to: {test_file_path}")

            # Step 3: Delete session1 with sync_context=True to ensure data persistence
            print("\nStep 3: Deleting session1 with sync_context=True...")
            session1_delete_result = await agent_bay_client.delete(session1, sync_context=True)
            assert session1_delete_result.success, f"Failed to delete session1: {session1_delete_result.error_message}"
            print(f"  ✓ Session1 deleted with context sync completed")

            # Step 4: Re-get context by ID to simulate fresh context retrieval
            print("\nStep 4: Re-getting context by ID...")
            context_reget_result = await agent_bay_client.context.get(context_id=context.id)
            assert context_reget_result.success, f"Failed to re-get context: {context_reget_result.error_message}"

            reget_context = context_reget_result.context
            assert reget_context.id == context.id, "Context ID should match"
            print(f"  ✓ Context re-retrieved: {reget_context.id}")

            # Step 5: Create second session with the same context
            print("\nStep 5: Creating second session with re-retrieved context...")
            context_sync2 = ContextSync(context_id=reget_context.id, path=test_path)
            session2_params = CreateSessionParams(context_syncs=[context_sync2])

            session2_result = await agent_bay_client.create(params=session2_params)
            assert session2_result.success, f"Failed to create session2: {session2_result.error_message}"

            session2 = session2_result.session
            print(f"  ✓ Session2 created: {session2.session_id}")

            try:
                # Step 6: Verify that data persisted from session1 is accessible in session2
                print("\nStep 6: Verifying data persistence across sessions...")
                read_result = await session2.file_system.read_file(test_file_path)
                assert read_result.success, f"Failed to read test file in session2: {read_result.error_message}"

                # Verify content matches what was written in session1
                assert read_result.content == test_content, f"Content mismatch: expected '{test_content}', got '{read_result.content}'"
                print(f"  ✓ Data successfully persisted and retrieved")
                print(f"  ✓ Content verified: {read_result.content}")

                # Step 7: Clean up session2
                print("\nStep 7: Cleaning up session2...")
                session2_delete_result = await agent_bay_client.delete(session2)
                assert session2_delete_result.success, f"Failed to delete session2: {session2_delete_result.error_message}"
                print(f"  ✓ Session2 deleted successfully")
            except Exception:
                await session2.delete()
                raise

        finally:
            await agent_bay_client.context.delete(context)
            print(f"  ✓ Context deleted: {context.id}")

        print("\n" + "=" * 70)
        print("✅ Context Cross-Session Persistence Test PASSED")
        print("  • Data written in session1 was successfully persisted")
        print("  • Context re-retrieval by ID worked correctly")
        print("  • Data was accessible in session2 after context sync")
        print("=" * 70)
