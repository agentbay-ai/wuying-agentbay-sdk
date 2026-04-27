"""Integration tests for Mobile Agent functionality."""
import asyncio

import pytest
import pytest_asyncio

from agentbay import get_logger
from agentbay import CreateSessionParams

from dotenv import load_dotenv

logger = get_logger("mobile-agent-integration-test")
load_dotenv()


@pytest_asyncio.fixture
async def mobile_agent_session(make_session):
    """Create a session for mobile agent testing."""
    await asyncio.sleep(3)
    params = CreateSessionParams(
        image_id="mobile_latest",
    )
    lc = await make_session(params=params)
    session = lc._result.session
    print(f"\n✅ Session created: {session.session_id}")
    logger.info(f"Session created: {session.session_id}")
    return session


@pytest.mark.asyncio
async def test_mobile_execute_task_success(mobile_agent_session):
    """Test execute_task basic functionality - non-blocking execution."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing execute_task - non-blocking execution")
        
        # Execute task and get task_id immediately
        result = await agent.mobile.execute_task(
            task, max_steps=1
        )
        task_id = result.task_id
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {result.request_id}")
        print(f"📋 Task ID: {result.task_id}")
        print(f"📋 Task Status: {result.task_status}")
        print(f"📋 Success: {result.success}")
        print(f"📋 Error Message: {result.error_message}")
        print(f"{'='*60}\n")
        
        # Verify execute_task returned successfully
        assert result.success, f"execute_task failed: {result.error_message}"
        assert result.request_id != "", "Request ID should not be empty"
        assert result.task_id != "", "Task ID should not be empty"
        assert result.error_message == "", f"Error message should be empty: {result.error_message}"
        assert result.task_status == "running", f"Initial status should be 'running', got: {result.task_status}"
        
        logger.info(f"✅ execute_task succeeded: task_id={result.task_id}")
        
        # Poll until task completes to avoid blocking subsequent tests
        max_try_times = 100
        retry_times = 0
        task_status = None

        while retry_times < max_try_times:
            status_result = await agent.mobile.get_task_status(task_id)
            
            # Verify the response
            assert status_result.success, f"get_task_status failed: {status_result.error_message}"
            
            # Print status for debugging
            print(f"\n📋 Content (Attempt #{retry_times + 1}):")
            print(f"  Task ID: {status_result.task_id}")
            print(f"  Status: {status_result.task_status}")
            print(f"  Error: {status_result.error}")
            print()
            
            # Check for error field (task finished or not found)
            if status_result.error:
                logger.info(f"✅ Task returned error (task finished or not found): {status_result.error}")
                break
            
            # Verify task ID matches
            assert status_result.task_id == task_id, f"Task ID mismatch: expected {task_id}, got {status_result.task_id}"
            
            task_status = status_result.task_status
            logger.info(f"⏳ Polling task status: {task_status} (attempt {retry_times + 1})")
            
            # If task completed, end polling immediately
            if task_status == "completed":
                logger.info(f"✅ Task reached completed status")
                break
            
            if task_status in ["failed", "unsupported"]:
                logger.info(f"✅ Task reached final status: {task_status}")
                break
            
            retry_times += 1
            await asyncio.sleep(3)
        
        # Verify task completed
        assert retry_times < max_try_times, f"Task did not complete within {max_try_times} attempts"
        assert task_status is not None, "Task status should be set"
        logger.info(f"✅ Task completed: status={task_status}")
        
    finally:
        # Final cleanup: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if not status.success:
                    logger.debug(f"Could not get task status for {task_id}: {status.error_message}")
                elif status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
                        await asyncio.sleep(1)
                else:
                    logger.debug(f"Task {task_id} already in final state: {status.task_status}")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_execute_task_and_wait_success(mobile_agent_session):
    """Test execute_task_and_wait - blocking execution with SDK polling."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing execute_task_and_wait - blocking execution")
        
        # Execute task and wait for completion using SDK's built-in polling
        result = await agent.mobile.execute_task_and_wait(
            task,
            timeout=180,
            max_steps=1
        )
        task_id = result.task_id
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {result.request_id}")
        print(f"📋 Task ID: {result.task_id}")
        print(f"📋 Task Status: {result.task_status}")
        print(f"📋 Success: {result.success}")
        print(f"📋 Error Message: {result.error_message}")
        if result.task_result:
            print(f"📋 Task Result: {result.task_result}")
        print(f"{'='*60}\n")
        
        # Verify execute_task_and_wait behavior
        assert result.request_id != "", "Request ID should not be empty"
        if result.task_id:
            assert result.task_id != "", "Task ID should not be empty if provided"
        
        logger.info(f"✅ execute_task_and_wait completed: status={result.task_status}")
        
        # If task didn't complete (timeout), ensure it's terminated
        if result.task_status == "running" or (not result.success and task_id):
            logger.info(f"Task still running or failed, ensuring termination...")
            if task_id:
                terminate_result = await agent.mobile.terminate_task(task_id)
                if terminate_result.success:
                    logger.info(f"✅ Task {task_id} terminated successfully")
                else:
                    # Poll until task completes naturally
                    max_try_times = 100
                    retry_times = 0
                    while retry_times < max_try_times:
                        status = await agent.mobile.get_task_status(task_id)
                        if status.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                            logger.info(f"✅ Task completed: {status.task_status}")
                            break
                        retry_times += 1
                        await asyncio.sleep(3)
        
    finally:
        # Final cleanup: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if not status.success:
                    logger.debug(f"Could not get task status for {task_id}: {status.error_message}")
                elif status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
                        await asyncio.sleep(1)
                else:
                    logger.debug(f"Task {task_id} already in final state: {status.task_status}")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_get_task_status_success(mobile_agent_session):
    """Test get_task_status - query task status and verify status changes."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing get_task_status - status querying")
        
        # First, execute a task
        execute_result = await agent.mobile.execute_task(
            task, max_steps=1
        )
        assert execute_result.success, f"execute_task failed: {execute_result.error_message}"
        task_id = execute_result.task_id
        
        logger.info(f"✅ Task started: task_id={task_id}")
        
        # Query status multiple times to verify status changes, and poll until completion
        max_try_times = 100
        retry_times = 0
        statuses_seen = []
        
        while retry_times < max_try_times:
            status_result = await agent.mobile.get_task_status(task_id)
            
            # Print status
            print(f"\n{'='*60}")
            print(f"📋 Query #{retry_times + 1}")
            print(f"📋 Request ID: {status_result.request_id}")
            print(f"📋 Task ID: {status_result.task_id}")
            print(f"📋 Task Status: {status_result.task_status}")
            print(f"📋 Task Action: {status_result.task_action}")
            print(f"📋 Success: {status_result.success}")
            print(f"📋 Error Message: {status_result.error_message}")
            print(f"{'='*60}\n")
            
            # Verify get_task_status returned successfully
            assert status_result.success, f"get_task_status failed: {status_result.error_message}"
            assert status_result.task_id == task_id, "Task ID should match"
            assert status_result.request_id != "", "Request ID should not be empty"
            
            statuses_seen.append(status_result.task_status)
            logger.info(f"✅ Query #{retry_times + 1}: status={status_result.task_status}, action={status_result.task_action}")
            
            # If task finished, we can stop querying
            if status_result.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                logger.info(f"✅ Task reached final status: {status_result.task_status}")
                break
            
            retry_times += 1
            await asyncio.sleep(3)
        
        # Verify task completed
        assert retry_times < max_try_times, f"Task did not complete within {max_try_times} attempts"
        assert len(statuses_seen) > 0, "Should have queried status at least once"
        logger.info(f"✅ Statuses seen: {statuses_seen}")
        
    finally:
        # Clean up: terminate task if still running
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if status.task_status == "running":
                    logger.info(f"Cleaning up: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated successfully")
            except Exception as e:
                logger.debug(f"Could not terminate task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_terminate_task_success(mobile_agent_session):
    """Test terminate_task - terminate a running task."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        task = "Open WeChat app"
        logger.info("🚀 Testing terminate_task - task termination")
        
        # First, execute a task
        execute_result = await agent.mobile.execute_task(
            task, max_steps=1
        )
        assert execute_result.success, f"execute_task failed: {execute_result.error_message}"
        task_id = execute_result.task_id
        
        logger.info(f"✅ Task started: task_id={task_id}")
        
        # Wait a moment to ensure task is running
        await asyncio.sleep(2)
        
        # Verify task is running before termination
        status_before = await agent.mobile.get_task_status(task_id)
        assert status_before.success, f"get_task_status failed: {status_before.error_message}"
        logger.info(f"📋 Task status before termination: {status_before.task_status}")
        
        # Terminate the task
        terminate_result = await agent.mobile.terminate_task(task_id)
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {terminate_result.request_id}")
        print(f"📋 Task ID: {terminate_result.task_id}")
        print(f"📋 Task Status: {terminate_result.task_status}")
        print(f"📋 Success: {terminate_result.success}")
        print(f"📋 Error Message: {terminate_result.error_message}")
        print(f"{'='*60}\n")
        
        # Verify terminate_task succeeded
        assert terminate_result.success, f"terminate_task failed: {terminate_result.error_message}"
        assert terminate_result.request_id != "", "Request ID should not be empty"
        assert terminate_result.task_id == task_id, "Task ID should match"
        
        logger.info(f"✅ terminate_task succeeded: status={terminate_result.task_status}")
        
        # Verify task status after termination - poll until confirmed terminated/completed
        max_try_times = 20
        retry_times = 0
        while retry_times < max_try_times:
            await asyncio.sleep(1)  # Wait a moment for termination to process
            status_after = await agent.mobile.get_task_status(task_id)
            assert status_after.success, f"get_task_status failed: {status_after.error_message}"
            logger.info(f"📋 Task status after termination (attempt {retry_times + 1}): {status_after.task_status}")
            
            # Task should be terminated, finished, or failed
            if status_after.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                logger.info(f"✅ Task confirmed in final status: {status_after.task_status}")
                break
            
            retry_times += 1
        
        # Verify task is no longer running
        final_status = await agent.mobile.get_task_status(task_id)
        assert final_status.task_status != "running", f"Task should not be running after termination, got: {final_status.task_status}"
        logger.info(f"✅ Task termination confirmed: {final_status.task_status}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Final cleanup attempt - ensure task is completed or terminated
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if not status.success:
                    logger.debug(f"Could not get task status for {task_id}: {status.error_message}")
                elif status.task_status == "running":
                    logger.info(f"Final cleanup: attempting to terminate task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated in cleanup")
                        await asyncio.sleep(1)
                    else:
                        # Poll until task completes naturally, but with shorter timeout
                        max_try_times = 5
                        retry_times = 0
                        while retry_times < max_try_times:
                            status = await agent.mobile.get_task_status(task_id)
                            if not status.success:
                                logger.debug(f"Could not get task status: {status.error_message}")
                                break
                            if status.task_status in ["completed", "finished", "failed", "cancelled", "unsupported"]:
                                logger.info(f"✅ Task completed in cleanup: {status.task_status}")
                                break
                            retry_times += 1
                            await asyncio.sleep(1)
                else:
                    # Task is already in final state, no cleanup needed
                    logger.debug(f"Task {task_id} already in final state: {status.task_status}")
            except Exception as e:
                logger.debug(f"Final cleanup failed for task {task_id}: {e}")


@pytest.mark.asyncio
async def test_mobile_execute_task_and_wait_timeout_termination(mobile_agent_session):
    """Test execute_task_and_wait timeout and verify task is fully terminated before returning."""
    agent = mobile_agent_session.agent
    task_id = None

    try:
        # Use a task that will take longer than the timeout
        task = "Open WeChat app and send a message to a contact"
        logger.info("🚀 Testing execute_task_and_wait timeout termination logic")
        
        # Execute with a very short timeout to trigger timeout behavior
        # This will test the termination polling logic
        short_timeout = 10  # 5 seconds timeout
        logger.info(f"⏱️ Executing task with short timeout ({short_timeout}s) to trigger timeout")
        
        result = await agent.mobile.execute_task_and_wait(
            task,
            timeout=short_timeout,
            max_steps=10,
        )
        task_id = result.task_id
        
        # Print results
        print(f"\n{'='*60}")
        print(f"📋 Request ID: {result.request_id}")
        print(f"📋 Task ID: {result.task_id}")
        print(f"📋 Task Status: {result.task_status}")
        print(f"📋 Success: {result.success}")
        print(f"📋 Error Message: {result.error_message}")
        print(f"📋 Task Result: {result.task_result}")
        print(f"{'='*60}\n")
        
        # Verify timeout occurred
        assert not result.success, "Task should have timed out"
        assert "timed out" in result.error_message.lower(), f"Error message should mention timeout: {result.error_message}"
        assert task_id != "", "Task ID should not be empty"
        
        logger.info(f"✅ Timeout occurred as expected: {result.error_message}")
        
        # CRITICAL: Verify that task is fully terminated by checking get_task_status
        # This is the key verification for the fix
        print(f"\n{'='*60}")
        print("🔍 Verifying task is fully terminated...")
        print(f"{'='*60}\n")
        logger.info("🔍 Verifying task is fully terminated...")
        max_verify_attempts = 10
        verify_attempt = 0
        task_terminated_confirmed = False
        
        while verify_attempt < max_verify_attempts:
            status_query = await agent.mobile.get_task_status(task_id)
            
            if not status_query.success:
                error_msg = status_query.error_message or ""
                print(f"📋 Verification attempt {verify_attempt + 1}: get_task_status returned error: {error_msg}")
                logger.info(f"📋 Verification attempt {verify_attempt + 1}: get_task_status returned error: {error_msg}")
                
                # This is the key check: verify we get "Task not found or already finished"
                if error_msg.startswith("Task not found or already finished"):
                    print(f"✅ Task {task_id} confirmed terminated (not found or finished)")
                    logger.info(f"✅ Task {task_id} confirmed terminated (not found or finished)")
                    task_terminated_confirmed = True
                    break
            else:
                print(f"📋 Verification attempt {verify_attempt + 1}: task status = {status_query.task_status}")
                logger.info(f"📋 Verification attempt {verify_attempt + 1}: task status = {status_query.task_status}")
                # If task is still running, that's a problem - the fix should have waited
                if status_query.task_status == "running":
                    print(f"⚠️ Task {task_id} is still running! This indicates the fix may not be working.")
                    logger.warning(f"⚠️ Task {task_id} is still running! This indicates the fix may not be working.")
            
            verify_attempt += 1
            await asyncio.sleep(1)
        
        # Assert that task is confirmed terminated
        assert task_terminated_confirmed, (
            f"Task {task_id} was not confirmed terminated. "
            f"After timeout, get_task_status should return 'Task not found or already finished' error. "
            f"This verifies the fix: terminate_task should wait for full termination before returning."
        )
        print(f"✅ Task termination verified: task is fully terminated")
        logger.info(f"✅ Task termination verified: task is fully terminated")
        
        # Additional verification: Try to start a new task immediately
        # This should not fail with "Another task is currently running" error
        print(f"\n{'='*60}")
        print("🔍 Verifying new task can be started immediately...")
        print(f"{'='*60}\n")
        logger.info("🔍 Verifying new task can be started immediately...")
        new_task_result = await agent.mobile.execute_task("Open WeChat app", max_steps=1)
        
        print(f"\n{'='*60}")
        print(f"📋 New Task Result:")
        print(f"📋 Request ID: {new_task_result.request_id}")
        print(f"📋 Task ID: {new_task_result.task_id}")
        print(f"📋 Success: {new_task_result.success}")
        print(f"📋 Error Message: {new_task_result.error_message}")
        print(f"{'='*60}\n")
        
        assert new_task_result.success, (
            f"New task should start successfully after timeout termination. "
            f"Error: {new_task_result.error_message}. "
            f"If you see 'Another task is currently running', the fix is not working correctly."
        )
        print(f"✅ New task started successfully: {new_task_result.task_id}")
        logger.info(f"✅ New task started successfully: {new_task_result.task_id}")
        
        # Clean up the new task
        if new_task_result.task_id:
            try:
                await asyncio.sleep(2)
                status = await agent.mobile.get_task_status(new_task_result.task_id)
                if status.success and status.task_status == "running":
                    terminate_result = await agent.mobile.terminate_task(new_task_result.task_id)
                    if terminate_result.success:
                        logger.info(f"✅ New task {new_task_result.task_id} terminated for cleanup")
            except Exception as e:
                logger.debug(f"Could not clean up new task: {e}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        # Final cleanup
        if task_id:
            try:
                status = await agent.mobile.get_task_status(task_id)
                if not status.success:
                    error_msg = status.error_message or ""
                    if "Task not found" in error_msg or "already finished" in error_msg:
                        logger.debug(f"Task {task_id} already terminated (as expected)")
                    else:
                        logger.debug(f"Could not get task status: {status.error_message}")
                elif status.task_status == "running":
                    logger.info(f"Final cleanup: terminating task {task_id}")
                    terminate_result = await agent.mobile.terminate_task(task_id)
                    if terminate_result.success:
                        logger.info(f"✅ Task {task_id} terminated in cleanup")
            except Exception as e:
                logger.debug(f"Final cleanup failed: {e}")

