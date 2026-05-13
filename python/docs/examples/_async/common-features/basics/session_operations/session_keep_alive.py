"""
ci-stable
Session Keep-Alive Example
"""

import asyncio
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
        )
    )
)

from agentbay import AsyncAgentBay, CreateSessionParams


async def main():
    print("=== Session Keep-Alive ===\n")

    client = AsyncAgentBay()
    session = None

    try:
        params = CreateSessionParams(
            image_id="linux_latest",
            idle_release_timeout=30,
            labels={"example": "session-keep-alive", "sdk": "python-async"},
        )
        session_result = await client.create(params)
        session = session_result.session
        print(f"Session ID: {session.session_id}")

        print("Sleeping for 15 seconds...")
        await asyncio.sleep(15)

        print("Calling keep_alive() to refresh idle timer...")
        keep_alive_result = await session.keep_alive()
        print(f"keep_alive success: {keep_alive_result.success}")
        print(f"request_id: {keep_alive_result.request_id}")
        if not keep_alive_result.success:
            print(f"error: {keep_alive_result.error_message}")

        print("\n=== Completed ===")
    finally:
        if session:
            await client.delete(session)


if __name__ == "__main__":
    asyncio.run(main())

