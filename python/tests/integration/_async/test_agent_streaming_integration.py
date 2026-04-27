"""Integration tests for Agent streaming output feature.

Tests the WS-based streaming execution path with real backend services.
Uses debug image imgc-0ab5takhnmlvhx9gp for Mobile Agent.
"""
import asyncio

import pytest

from agentbay import AgentEvent, get_logger

# make_session factory fixture is provided by conftest.py (auto-loaded by pytest)

logger = get_logger("agent-streaming-integration-test")


@pytest.mark.asyncio
async def test_mobile_streaming_with_typed_callbacks(make_session):
    """Test mobile agent streaming with typed callbacks (on_reasoning, on_tool_call, etc.)."""
    lc = await make_session("mobile_latest")
    agent = lc._result.session.agent
    reasoning_events = []
    content_events = []
    tool_calls = []
    tool_results = []

    def on_reasoning(event: AgentEvent):
        reasoning_events.append(event)
        print(f"  [Reasoning] round={event.round}: {event.content[:100]}...")

    def on_content(event: AgentEvent):
        content_events.append(event)
        print(f"  [Content] round={event.round}: {event.content[:100]}...")

    def on_tool_call(event: AgentEvent):
        tool_calls.append(event)
        print(f"  [ToolCall] round={event.round}: {event.tool_name}({event.args})")

    def on_tool_result(event: AgentEvent):
        tool_results.append(event)
        result_preview = str(event.result)[:100]
        print(f"  [ToolResult] round={event.round}: {event.tool_name} -> {result_preview}...")

    print(f"\n{'='*60}")
    print("Testing mobile agent streaming with typed callbacks")
    print(f"{'='*60}")

    result = await agent.mobile.execute_task_and_wait(
        task="Open Settings app",
        timeout=180,
        max_steps=10,
        on_reasoning=on_reasoning,
        on_content=on_content,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
    )

    print(f"\n{'='*60}")
    print(f"Result:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.task_status}")
    print(f"  Reasoning events: {len(reasoning_events)}")
    print(f"  Content events: {len(content_events)}")
    print(f"  Tool Calls: {len(tool_calls)}")
    print(f"  Tool Results: {len(tool_results)}")
    print(f"{'='*60}\n")

    assert isinstance(result.task_status, str), "task_status should be a string"


@pytest.mark.asyncio
async def test_mobile_streaming_token_level(make_session):
    """Test mobile agent streaming with typed callbacks for real-time output."""
    await asyncio.sleep(3)
    lc = await make_session("imgc-0ab5takhnmlvhx9gp")
    agent = lc._result.session.agent
    reasoning_chunks = []
    content_chunks = []

    def on_reasoning(event: AgentEvent):
        reasoning_chunks.append(event.content)
        print(event.content, end="", flush=True)

    def on_content(event: AgentEvent):
        content_chunks.append(event.content)
        print(event.content, end="", flush=True)

    def on_tool_call(event: AgentEvent):
        print(f"\n  [ToolCall] {event.tool_name}({event.args})")

    print(f"\n{'='*60}")
    print("Testing mobile agent streaming with real-time output")
    print(f"{'='*60}")
    print("\nStreaming output:")

    result = await agent.mobile.execute_task_and_wait(
        task="Open Settings app",
        timeout=180,
        max_steps=10,
        on_reasoning=on_reasoning,
        on_content=on_content,
        on_tool_call=on_tool_call,
    )

    print(f"\n\n{'='*60}")
    print(f"Result:")
    print(f"  Success: {result.success}")
    print(f"  Status: {result.task_status}")
    print(f"  Reasoning chunks: {len(reasoning_chunks)}")
    print(f"  Content chunks: {len(content_chunks)}")
    if result.task_result:
        print(f"  Task Result: {result.task_result[:200]}")
    print(f"{'='*60}\n")

    assert isinstance(result.task_status, str), "task_status should be a string"
    assert len(reasoning_chunks) > 0 or len(content_chunks) > 0, "Should have received at least one event"

    if reasoning_chunks:
        full_reasoning = "".join(reasoning_chunks)
        print(f"Reconstructed reasoning: {full_reasoning[:200]}...")
    if content_chunks:
        full_content = "".join(content_chunks)
        print(f"Reconstructed content: {full_content[:200]}...")
