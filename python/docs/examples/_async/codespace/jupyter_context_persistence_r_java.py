#!/usr/bin/env python3
"""
ci-stable

AgentBay SDK - Jupyter Context Persistence (R & Java) Example

This example demonstrates that consecutive `session.code.run_code()` calls within the same
session can share an execution context (Jupyter-like behavior) for R and Java, so variables
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
        print("\n===== R: Jupyter-like context persistence =====")
        r_setup_code = """
x <- 41
cat("R_CONTEXT_SETUP_DONE\\n")
""".strip()
        r_setup_result = await session.code.run_code(r_setup_code, "R")
        if not r_setup_result.success:
            raise RuntimeError(f"R setup failed: {r_setup_result.error_message}")
        print(r_setup_result.result)

        r_use_code = """
cat(paste0("R_CONTEXT_VALUE:", x + 1, "\\n"))
""".strip()
        r_use_result = await session.code.run_code(r_use_code, "r")
        if not r_use_result.success:
            raise RuntimeError(f"R context use failed: {r_use_result.error_message}")
        print(r_use_result.result)

        if "R_CONTEXT_VALUE:42" not in r_use_result.result:
            raise RuntimeError("R context persistence verification failed")

        print("\n===== Java: Jupyter-like context persistence =====")
        java_setup_code = """
int x = 41;
System.out.println("JAVA_CONTEXT_SETUP_DONE");
""".strip()
        java_setup_result = await session.code.run_code(java_setup_code, "JAVA")
        if not java_setup_result.success:
            raise RuntimeError(f"Java setup failed: {java_setup_result.error_message}")
        print(java_setup_result.result)

        java_use_code = """
System.out.println("JAVA_CONTEXT_VALUE:" + (x + 1));
""".strip()
        java_use_result = await session.code.run_code(java_use_code, "java")
        if not java_use_result.success:
            raise RuntimeError(f"Java context use failed: {java_use_result.error_message}")
        print(java_use_result.result)

        if "JAVA_CONTEXT_VALUE:42" not in java_use_result.result:
            raise RuntimeError("Java context persistence verification failed")
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())


