"""E2E test: verify dynamically bound context supports real data persistence.
"""

from uuid import uuid4

import pytest

from agentbay import CreateSessionParams, ContextSync


@pytest.mark.asyncio
async def test_bind_context_data_persistence(agent_bay_client):
    """
    Full E2E test: dynamically bind a context, write data, sync upload,
    then bind the same context in a new session and verify data persists.
    """
    context_name = f"test-e2e-bind-{uuid4().hex[:8]}"
    bind_path = "/tmp/e2e-bind-test"
    test_filename = "hello.txt"
    test_content = f"bind-e2e-{uuid4().hex[:8]}"

    # Step 1: Create a fresh context
    ctx_result = await agent_bay_client.context.get(name=context_name, create=True)
    assert ctx_result.success, f"Failed to create context: {ctx_result.error_message}"
    ctx = ctx_result.context
    print(f"[Step 1] Created context: {ctx.id} ({ctx.name})")

    try:
        # Step 2: Session A - dynamically bind and write data
        session_a_result = await agent_bay_client.create(CreateSessionParams())
        assert session_a_result.success, f"Failed to create session A: {session_a_result.error_message}"
        session_a = session_a_result.session
        print(f"[Step 2] Created session A: {session_a.session_id}")

        try:
            bind_result = await session_a.context.bind(
                ContextSync(context_id=ctx.id, path=bind_path),
            )
            assert bind_result.success, f"bind() failed: {bind_result.error_message}"
            print(f"[Step 2] Bound context {ctx.id} to {bind_path}")

            # Write a file to the bound path
            write_cmd = f'echo -n "{test_content}" > {bind_path}/{test_filename}'
            write_result = await session_a.command.execute_command(write_cmd)
            print(f"[Step 2] Write command: exit_code={write_result.exit_code}")
            assert write_result.exit_code == 0, f"Write failed: {write_result.stderr}"

            # Verify the file is there
            read_result = await session_a.command.execute_command(f"cat {bind_path}/{test_filename}")
            assert read_result.exit_code == 0
            assert read_result.stdout.strip() == test_content, (
                f"Expected '{test_content}', got '{read_result.stdout.strip()}'"
            )
            print(f"[Step 2] Verified file content in session A: '{read_result.stdout.strip()}'")

            # Step 3: Trigger upload sync
            sync_result = await session_a.context.sync(
                context_id=ctx.id,
                path=bind_path,
                mode="upload",
            )
            assert sync_result.success, f"Upload sync failed: {sync_result.error_message}"
            print(f"[Step 3] Upload sync completed successfully")

        finally:
            await session_a.delete()
            print(f"[Step 3] Deleted session A")

        # Step 4: Session B - bind same context and verify data persists
        session_b_result = await agent_bay_client.create(CreateSessionParams())
        assert session_b_result.success, f"Failed to create session B: {session_b_result.error_message}"
        session_b = session_b_result.session
        print(f"[Step 4] Created session B: {session_b.session_id}")

        try:
            bind_result_b = await session_b.context.bind(
                ContextSync(context_id=ctx.id, path=bind_path),
                wait_for_completion=True,
            )
            assert bind_result_b.success, f"bind() in session B failed: {bind_result_b.error_message}"
            print(f"[Step 4] Bound context {ctx.id} to {bind_path} in session B")

            # Verify data persists from session A
            read_result_b = await session_b.command.execute_command(f"cat {bind_path}/{test_filename}")
            print(f"[Step 4] Read in session B: exit_code={read_result_b.exit_code}, stdout='{read_result_b.stdout.strip()}'")
            assert read_result_b.exit_code == 0, f"Read failed in session B: {read_result_b.stderr}"
            assert read_result_b.stdout.strip() == test_content, (
                f"Data persistence failed! Expected '{test_content}', "
                f"got '{read_result_b.stdout.strip()}'"
            )
            print(f"[Step 4] Data persistence verified! Content matches: '{test_content}'")

        finally:
            await session_b.delete()
            print(f"[Step 4] Deleted session B")

    finally:
        await agent_bay_client.context.delete(ctx)
        print(f"[Cleanup] Deleted context {ctx.id}")
