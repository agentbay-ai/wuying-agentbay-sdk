#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - Dynamic Context Binding Example

This example demonstrates how to dynamically bind contexts to a running session:
- Create a session without any initial context
- Dynamically bind a context using session.context.bind()
- List current bindings using session.context.list_bindings()
- Verify the bound context is usable
"""

import asyncio
import time
from agentbay import AsyncAgentBay, ContextSync, SyncPolicy


async def main():
    """Main function"""
    print("🔗 AgentBay Dynamic Context Binding Example")

    agent_bay = AsyncAgentBay()

    try:
        await dynamic_binding_demo(agent_bay)
    except Exception as e:
        print(f"❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()

    print("✅ Dynamic context binding example completed")


async def dynamic_binding_demo(agent_bay):
    """Demonstrate dynamic context binding"""
    print("\n🔄 === Dynamic Context Binding Demonstration ===")

    # Step 1: Create a context
    print("\n📦 Step 1: Creating a context...")
    context_name = f"dynamic-bind-{int(time.time())}"
    context_result = await agent_bay.context.get(context_name, create=True)
    if not context_result.success:
        print(f"❌ Context creation failed: {context_result.error_message}")
        return

    context = context_result.context
    print(f"✅ Context ready: {context.id} ({context.name})")

    # Step 2: Create a session WITHOUT any initial context
    print("\n🔧 Step 2: Creating a session (no initial context)...")
    session_result = await agent_bay.create()
    if not session_result.success:
        print(f"❌ Session creation failed: {session_result.error_message}")
        return

    session = session_result.session
    print(f"✅ Session created: {session.session_id}")

    try:
        # Step 3: List bindings - should be empty
        print("\n📋 Step 3: Listing bindings (should be empty)...")
        bindings_result = await session.context.list_bindings()
        if bindings_result.success:
            print(f"   Current bindings: {len(bindings_result.bindings)}")

        # Step 4: Dynamically bind the context
        print("\n🔗 Step 4: Dynamically binding context to session...")
        sync_policy = SyncPolicy.default()
        context_sync = ContextSync.new(
            context_id=context.id,
            path="/tmp/ctx-dynamic",
            policy=sync_policy,
        )

        bind_result = await session.context.bind(context_sync)
        if bind_result.success:
            print(f"✅ Context bound successfully (RequestId: {bind_result.request_id})")
        else:
            print(f"❌ Bind failed: {bind_result.error_message}")
            return

        # Step 5: List bindings again - should show the bound context
        print("\n📋 Step 5: Listing bindings (should show 1 binding)...")
        bindings_result = await session.context.list_bindings()
        if bindings_result.success:
            print(f"   Current bindings: {len(bindings_result.bindings)}")
            for b in bindings_result.bindings:
                print(f"   - Context: {b.context_id}, Path: {b.path}, Name: {b.context_name}")

        # Step 6: Verify the bound context is usable
        print("\n✍️ Step 6: Writing data to the bound context path...")
        cmd_result = await session.command.execute_command(
            "echo 'Hello from dynamic binding!' > /tmp/ctx-dynamic/test.txt"
        )
        if cmd_result.exit_code == 0:
            print("✅ Data written successfully")

        read_result = await session.file_system.read_file("/tmp/ctx-dynamic/test.txt")
        if read_result.success:
            print(f"✅ Data read back: {read_result.content.strip()}")
        else:
            print(f"❌ Failed to read data: {read_result.error_message}")

        # Step 7: Bind multiple contexts at once
        print("\n🔗 Step 7: Demonstrating multiple context binding...")
        ctx_res_a = await agent_bay.context.get(f"{context_name}-a", create=True)
        ctx_res_b = await agent_bay.context.get(f"{context_name}-b", create=True)
        if ctx_res_a.success and ctx_res_b.success:
            cs_a = ContextSync.new(
                context_id=ctx_res_a.context.id,
                path="/tmp/ctx-multi-a",
                policy=sync_policy,
            )
            cs_b = ContextSync.new(
                context_id=ctx_res_b.context.id,
                path="/tmp/ctx-multi-b",
                policy=sync_policy,
            )
            bind_result2 = await session.context.bind(cs_a, cs_b)
            if bind_result2.success:
                print("✅ Multiple contexts bound successfully")

            bindings_result = await session.context.list_bindings()
            if bindings_result.success:
                print(f"   Total bindings: {len(bindings_result.bindings)}")
                for b in bindings_result.bindings:
                    print(f"   - {b.context_name} -> {b.path}")

    finally:
        print("\n🧹 Cleaning up...")
        await agent_bay.delete(session, sync_context=True)
        print("✅ Session deleted")


if __name__ == "__main__":
    asyncio.run(main())
