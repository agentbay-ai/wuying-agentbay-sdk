"""
ci-stable
Mobile Agent Streaming Example

This example demonstrates:
1. Mobile Agent task execution with real-time streaming output
2. Using typed callbacks (on_reasoning, on_content, on_tool_call, on_tool_result)
"""

import asyncio
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
)

from agentbay import AsyncAgentBay, AgentEvent, CreateSessionParams, get_logger

logger = get_logger("mobile_agent_streaming")


async def example_typed_callbacks():
    """Demonstrate Mobile Agent streaming with typed callbacks."""
    print("=" * 60)
    print("Example 1: Mobile Agent Streaming with Typed Callbacks")
    print("=" * 60)

    client = AsyncAgentBay()
    session = None

    try:
        session_result = await client.create(
            CreateSessionParams(image_id="mobile_latest")
        )
        session = session_result.session
        logger.info(f"Session created: {session.session_id}")

        agent = session.agent

        def on_reasoning(event: AgentEvent):
            print(f"[Reasoning] {event.content}", end="", flush=True)

        def on_content(event: AgentEvent):
            print(f"[Content] {event.content}", end="", flush=True)

        def on_tool_call(event: AgentEvent):
            print(f"\n[ToolCall] {event.tool_name}({event.args})")

        def on_tool_result(event: AgentEvent):
            result_preview = str(event.result)[:200]
            print(f"[ToolResult] {event.tool_name} -> {result_preview}")

        result = await agent.mobile.execute_task_and_wait(
            task="Open Settings app",
            timeout=180,
            max_steps=10,
            on_reasoning=on_reasoning,
            on_content=on_content,
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
        )

        print(f"\n\nTask completed:")
        print(f"  Success: {result.success}")
        print(f"  Status: {result.task_status}")
        if result.task_result:
            print(f"  Result: {result.task_result[:200]}")

    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if session:
            await client.delete(session)
            print("Session cleaned up")


async def main():
    print("Mobile Agent Streaming Output Examples\n")

    await example_typed_callbacks()

    print("\nAll examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
