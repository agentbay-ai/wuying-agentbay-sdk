"""
AgentBay SDK - Context Mount Example

This example demonstrates the Context Mount (direct-mount persistence) feature:
- Mounting a context at session creation time
- Write-through persistence (no manual sync needed)
- Cross-session data persistence via mount
- Dynamic mounting using bind()
"""

import asyncio
import os
import time

from agentbay import AsyncAgentBay, BetaContextMount, CreateSessionParams


async def main():
    print("📌 AgentBay Context Mount Example")

    api_key = os.environ.get("AGENTBAY_API_KEY", "")
    if not api_key:
        print("❌ Please set AGENTBAY_API_KEY environment variable")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)

    try:
        await context_mount_demo(agent_bay)
        await partial_mount_demo(agent_bay)
    except Exception as e:
        print(f"❌ Example execution failed: {e}")
        raise

    print("✅ Context mount example completed")


async def context_mount_demo(agent_bay: AsyncAgentBay):
    print("\n🔄 === Context Mount Demonstration ===")

    # Context Mount requires image_id=aio-ubuntu-2404.
    # Other images do not provide a real OSS-backed mount.
    image_id = "aio-ubuntu-2404"

    # Step 1: Create a context for persistent storage
    print("\n📦 Step 1: Creating context for persistent storage...")
    context_name = f"mount-demo-{int(time.time())}"
    context_result = await agent_bay.context.get(context_name, create=True)

    if not context_result.success:
        print(f"❌ Context creation failed: {context_result.error_message}")
        return

    context = context_result.context
    print(f"✅ Context created: {context.id} (name: {context.name})")

    # Step 2: Create first session with context mount
    print("\n🔧 Step 2: Creating first session with context mount...")
    context_mount = BetaContextMount.new(context.id, "/tmp/mounted_data")

    params = CreateSessionParams(image_id=image_id, beta_context_mounts=[context_mount])
    session1_result = await agent_bay.create(params)

    if not session1_result.success:
        print(f"❌ First session creation failed: {session1_result.error_message}")
        return

    session1 = session1_result.session
    print(f"✅ First session created: {session1.session_id}")

    session1_id = session1.session_id
    try:
        # Step 3: Write data — persisted immediately via write-through
        print("\n💾 Step 3: Writing data (write-through persistence)...")

        await session1.command.execute_command("mkdir -p /tmp/mounted_data/config")

        config_content = '{"app": "mount-demo", "version": "1.0", "session": "%s"}' % session1.session_id
        config_result = await session1.file_system.write_file(
            "/tmp/mounted_data/config/app.json", config_content
        )
        if config_result.success:
            print("✅ Config file written (persisted immediately)")
        else:
            print(f"❌ Failed to write config: {config_result.error_message}")

        data_content = "This data is persisted via Context Mount.\nNo manual sync() call needed!"
        data_result = await session1.file_system.write_file(
            "/tmp/mounted_data/notes.txt", data_content
        )
        if data_result.success:
            print("✅ Data file written (persisted immediately)")
        else:
            print(f"❌ Failed to write data: {data_result.error_message}")

        # List files
        print("\n📋 Files in mounted path:")
        list_result = await session1.command.execute_command(
            "find -L /tmp/mounted_data -type f"
        )
        if list_result.success:
            print(list_result.output)

    finally:
        # No sync_context needed — data is already persisted
        print("\n🧹 Deleting first session (no sync needed for mount)...")
        delete_result = await agent_bay.delete(session1)
        if delete_result.success:
            print("✅ First session deleted")
        else:
            print(f"❌ First session deletion failed: {delete_result.error_message}")

    # Step 4: Create second session to verify cross-session persistence
    print("\n🔧 Step 4: Creating second session to verify persistence...")

    params2 = CreateSessionParams(image_id=image_id, beta_context_mounts=[context_mount])
    session2_result = await agent_bay.create(params2)

    if not session2_result.success:
        print(f"❌ Second session creation failed: {session2_result.error_message}")
        return

    session2 = session2_result.session
    print(f"✅ Second session created: {session2.session_id}")

    try:
        print("\n🔍 Step 5: Verifying persisted data in second session...")

        files_to_check = [
            "/tmp/mounted_data/config/app.json",
            "/tmp/mounted_data/notes.txt",
        ]

        files_found = 0
        for file_path in files_to_check:
            print(f"\n🔍 Checking: {file_path}")
            read_result = await session2.file_system.read_file(file_path)

            if read_result.success:
                print(f"✅ File found!")
                preview = read_result.content[:120]
                print(f"   📄 Content: {preview}")
                files_found += 1
            else:
                print(f"❌ Not found: {read_result.error_message}")

        # Step 6: Dynamic mount demo (bind)
        print("\n🔧 Step 6: Dynamic mount using bind()...")
        dynamic_ctx_result = await agent_bay.context.get(
            f"dynamic-mount-{int(time.time())}", create=True
        )
        if dynamic_ctx_result.success:
            dynamic_mount = BetaContextMount.new(
                dynamic_ctx_result.context.id, "/tmp/dynamic_mount"
            )
            bind_result = await session2.context.bind(dynamic_mount)
            if bind_result.success:
                print("✅ Dynamic mount bound successfully")
                write_result = await session2.file_system.write_file(
                    "/tmp/dynamic_mount/dynamic.txt", "Dynamically mounted data!"
                )
                if write_result.success:
                    print("✅ Wrote to dynamically mounted path")
            else:
                print(f"❌ Dynamic bind failed: {bind_result.error_message}")

            # Clean up dynamic context
            await agent_bay.context.delete(dynamic_ctx_result.context)

        # Summary
        print(f"\n📊 === Persistence Summary ===")
        print(f"✅ Context ID: {context.id}")
        print(f"✅ Session 1: {session1_id} (deleted)")
        print(f"✅ Session 2: {session2.session_id} (active)")
        print(f"✅ Files found: {files_found}/{len(files_to_check)}")

        if files_found == len(files_to_check):
            print("🎉 Context Mount persistence verification SUCCESSFUL!")
        else:
            print("⚠️  Some files not found — mount may still be initializing")

    finally:
        print("\n🧹 Cleaning up second session...")
        delete_result = await agent_bay.delete(session2)
        if delete_result.success:
            print("✅ Second session deleted")

    # Clean up context
    print("\n🧹 Cleaning up context...")
    delete_ctx_result = await agent_bay.context.delete(context)
    if delete_ctx_result.success:
        print(f"✅ Context deleted: {delete_ctx_result.request_id}")


async def partial_mount_demo(agent_bay: AsyncAgentBay):
    """Demonstrate sourcePath: mount only a subdirectory of a context.

    Requires image_id=aio-ubuntu-2404 (CSI-based mount supports partial mounting).
    """
    print("\n🔄 === Partial Mount (sourcePath) Demonstration ===")

    image_id = "aio-ubuntu-2404"

    # Step 1: Create context and seed it with subdirectories
    print("\n📦 Step 1: Creating context and seeding subdirectories...")
    context_name = f"partial-mount-{int(time.time())}"
    context_result = await agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        print(f"❌ Context creation failed: {context_result.error_message}")
        return
    context = context_result.context
    print(f"✅ Context created: {context.id}")

    # Seed via a session that mounts the entire context root
    seed_mount = BetaContextMount.new(context.id, "/tmp/seed_data")
    seed_session_result = await agent_bay.create(
        CreateSessionParams(image_id=image_id, beta_context_mounts=[seed_mount])
    )
    if not seed_session_result.success:
        print(f"❌ Seed session creation failed: {seed_session_result.error_message}")
        return
    seed_session = seed_session_result.session
    print(f"✅ Seed session created: {seed_session.session_id}")

    seed_files = {
        "/tmp/seed_data/sub1/file_a.txt": "content of file_a",
        "/tmp/seed_data/sub1/file_b.txt": "content of file_b",
        "/tmp/seed_data/sub2/file_c.txt": "content of file_c",
    }

    await seed_session.command.execute_command(
        "mkdir -p /tmp/seed_data/sub1 /tmp/seed_data/sub2"
    )
    for path, content in seed_files.items():
        write_result = await seed_session.file_system.write_file(path, content)
        if write_result.success:
            print(f"✅ Wrote: {path}")
        else:
            print(f"❌ Failed to write {path}: {write_result.error_message}")

    # Delete seed session — data is already persisted via mount
    print("\n🧹 Deleting seed session...")
    await agent_bay.delete(seed_session)

    # Step 2: Mount only the /sub1 subdirectory to a fresh path
    print("\n🔧 Step 2: Mounting only /sub1 subdirectory to /tmp/sub1_only...")
    sub_mount = BetaContextMount.new(
        context_id=context.id,
        path="/tmp/sub1_only",
        source_path="/sub1",
    )
    sub_session_result = await agent_bay.create(
        CreateSessionParams(image_id=image_id, beta_context_mounts=[sub_mount])
    )
    if not sub_session_result.success:
        print(f"❌ Subdirectory session creation failed: {sub_session_result.error_message}")
    else:
        sub_session = sub_session_result.session
        print(f"✅ Session created with source_path=/sub1: {sub_session.session_id}")

        # sub1's contents are projected to the mount root (not nested under /sub1)
        for filename in ["file_a.txt", "file_b.txt"]:
            read_result = await sub_session.file_system.read_file(
                f"/tmp/sub1_only/{filename}"
            )
            if read_result.success:
                print(f"✅ /tmp/sub1_only/{filename} readable: {read_result.content}")
            else:
                print(f"❌ /tmp/sub1_only/{filename} NOT readable: {read_result.error_message}")

        # sub2 should NOT be visible (partial mount filters it out)
        list_sub2 = await sub_session.command.execute_command(
            "ls /tmp/sub1_only/sub2 2>&1 || echo NOT_FOUND"
        )
        if "NOT_FOUND" in list_sub2.output or "No such file" in list_sub2.output:
            print("✅ /tmp/sub1_only/sub2 correctly NOT visible (sourcePath filter working)")
        else:
            print(f"⚠️  /tmp/sub1_only/sub2 unexpectedly visible: {list_sub2.output}")

        await agent_bay.delete(sub_session)

    # Step 3: Cleanup
    print("\n🧹 Cleaning up partial-mount context...")
    delete_ctx_result = await agent_bay.context.delete(context)
    if delete_ctx_result.success:
        print(f"✅ Context deleted: {delete_ctx_result.request_id}")


if __name__ == "__main__":
    asyncio.run(main())
