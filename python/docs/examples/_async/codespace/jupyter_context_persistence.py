#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - Jupyter Context Persistence Example

This example demonstrates that consecutive `session.code.run_code()` calls within the same
session can share an execution context (Jupyter-like behavior), so variables and functions
defined in one call can be reused in subsequent calls.
"""

import asyncio
import os

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)
    session_result = await agent_bay.create(CreateSessionParams(image_id="code_latest"))
    if not session_result.success:
        raise RuntimeError(f"Failed to create session: {session_result.error_message}")

    session = session_result.session
    print(f"Session created: {session.session_id}")

    try:
        setup_code = """
x = 41

def add(a, b):
    return a + b

print("CONTEXT_SETUP_DONE")
""".strip()

        setup_result = await session.code.run_code(setup_code, "python")
        if not setup_result.success:
            raise RuntimeError(f"Setup failed: {setup_result.error_message}")
        print(setup_result.result)

        use_code = """
print(f"CONTEXT_VALUE:{x + 1}")
print(f"CONTEXT_FUNC:{add(1, 2)}")
""".strip()

        use_result = await session.code.run_code(use_code, "python")
        if not use_result.success:
            raise RuntimeError(f"Context use failed: {use_result.error_message}")
        print(use_result.result)
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())


