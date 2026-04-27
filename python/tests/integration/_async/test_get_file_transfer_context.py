# ci-stable
import asyncio
import time

import pytest
import pytest_asyncio


class TestGetFileTransferContext:
    """Integration tests for get method file transfer context fix"""

    @pytest_asyncio.fixture
    async def test_session(self, make_session):
        """Create a test session and rely on make_session for cleanup."""
        lc = await make_session("code_latest")
        return lc._result.session


    @pytest.mark.asyncio
    async def test_recovered_session_can_perform_file_operations(
        self, agent_bay_client, test_session
    ):
        """
        Test that recovered session can perform actual file operations.

        This is an end-to-end test that verifies the recovered session
        can actually upload and download files.
        """
        # Get the session_id from the test_session
        session_id = test_session.session_id

        # Wait a bit for session to be fully ready
        await asyncio.sleep(5)

        # Use get method to recover the session
        get_result = await agent_bay_client.get(session_id)
        assert get_result.success, f"Get failed: {get_result.error_message}"

        recovered_session = get_result.session

        # Create a test file to upload
        test_content = f"Test content at {time.time()}"
        test_filename = f"test_file_{int(time.time())}.txt"

        # Try to write the file using file_system operations
        # This should work if file transfer context is properly set up
        try:
            # Write file to the session
            write_result = await recovered_session.file_system.write_file(
                f"/tmp/{test_filename}", test_content
            )

            # Verify the write was successful
            assert (
                write_result.success
            ), f"File write failed: {write_result.error_message}"

            # Read back the file to verify
            read_result = await recovered_session.file_system.read_file(
                f"/tmp/{test_filename}"
            )
            assert read_result.success, f"File read failed: {read_result.error_message}"
            assert (
                read_result.content == test_content
            ), "Read content doesn't match written content"

        except Exception as e:
            pytest.fail(f"File operations failed on recovered session: {e}")

    @pytest.mark.asyncio
    async def test_original_and_recovered_session_both_work(self, agent_bay_client, test_session):
        """
        Test that both original session and recovered session can perform file operations.

        This test verifies that:
        1. Original session created with create() works
        2. Recovered session obtained with get() works
        3. Both can perform file operations independently
        """
        session_id = test_session.session_id

        # Wait a bit for session to be fully ready
        await asyncio.sleep(5)

        # Test 1: Original session can write files
        test_content_1 = f"Original session test at {time.time()}"
        test_filename_1 = f"original_test_{int(time.time())}.txt"

        write_result_1 = await test_session.file_system.write_file(
            f"/tmp/{test_filename_1}", test_content_1
        )
        assert (
            write_result_1.success
        ), f"Original session file write failed: {write_result_1.error_message}"

        # Test 2: Recover the session
        get_result = await agent_bay_client.get(session_id)
        assert get_result.success, f"Get failed: {get_result.error_message}"
        recovered_session = get_result.session

        # Test 3: Recovered session can write files
        test_content_2 = f"Recovered session test at {time.time()}"
        test_filename_2 = f"recovered_test_{int(time.time())}.txt"

        write_result_2 = await recovered_session.file_system.write_file(
            f"/tmp/{test_filename_2}", test_content_2
        )
        assert (
            write_result_2.success
        ), f"Recovered session file write failed: {write_result_2.error_message}"

        # Test 4: Verify both files exist and have correct content
        read_result_1 = await recovered_session.file_system.read_file(
            f"/tmp/{test_filename_1}"
        )
        assert read_result_1.success and read_result_1.content == test_content_1

        read_result_2 = await recovered_session.file_system.read_file(
            f"/tmp/{test_filename_2}"
        )
        assert read_result_2.success and read_result_2.content == test_content_2
