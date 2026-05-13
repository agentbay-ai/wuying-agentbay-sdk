"""
ci-stable
Process Management Example
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    print("=== Process Management ===\n")
    client = AsyncAgentBay()
    session = None

    try:
        session_result = await client.create(CreateSessionParams(image_id="linux_latest"))
        session = session_result.session

        # List processes
        result = await session.command.execute_command("ps aux | head -5")
        print(f"1. Processes:\n{result.output}")

        # Check specific process
        result = await session.command.execute_command("ps aux | grep bash | head -1")
        print(f"2. Bash process: {result.output}")

        # Process count
        result = await session.command.execute_command("ps aux | wc -l")
        print(f"3. Process count: {result.output}")

        print("\n=== Completed ===")

    finally:
        if session:
            await client.delete(session)


if __name__ == "__main__":
    asyncio.run(main())

